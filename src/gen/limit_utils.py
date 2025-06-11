import threading
import time
from collections import deque


class SlidingWindowRateLimiter:
    """
    Enforces the model-level tokens-per-minute (TPM) quota issued by OpenAI.

    The limiter keeps a rolling 60-second window of token “charges”.
    A thread that wants to send a request:
        1.  estimates how many tokens it will cost
        2.  blocks until that many tokens fit in the window
        3.  inserts a record (timestamp, tokens) to reserve the budget
        4.  waits until the request could be done
    """

    def __init__(self, tpm_limit: int, window_seconds: int = 60) -> None:
        self.tpm_limit = tpm_limit
        self.window_seconds = window_seconds
        self._token_events: deque[tuple[float, int]] = deque()
        self._lock = threading.Lock()

    def _drop_expired_events(self, now: float) -> None:
        """Remove events older than the sliding-window horizon."""
        while self._token_events and now - self._token_events[0][0] >= self.window_seconds:
            self._token_events.popleft()

    def _tokens_in_window(self, now: float) -> int:
        """Return the total tokens currently counted against the window."""
        self._drop_expired_events(now)
        return sum(tokens for _, tokens in self._token_events)

    def wait_until_budget_allows(self, tokens_needed: int) -> None:
        """
        Block the caller until `tokens_needed` can be spent without
        exceeding the TPM limit.
        """
        while True:
            with self._lock:
                now = time.time()
                used = self._tokens_in_window(now)
                free_budget = self.tpm_limit - used

                if tokens_needed <= free_budget:
                    # adds the events queue
                    self._token_events.append((now, tokens_needed))
                    return

                # Oldest event dictates when budget frees up
                sleep_for = self.window_seconds - (now - self._token_events[0][0]) + 0.05

            print(f"Waiting {sleep_for} seconds until budget is reached.")
            time.sleep(sleep_for)