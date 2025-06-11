from requests import get, post
import json

METHODS = {"GET": get,
           "POST": post}

class APIWrapper():
    def __init__(self, config: APIClientConfig, base_url: str, name: str):
        self.config = config
        self.base_url = base_url
        self.name = name

    def request(method: str, url: str, args_in_url: bool, data: dict) -> dict[str, any]:
        if args_in_url:
            url = url.format(**data)  # TODO: Take in-url args out of payload.

        response = METHODS[method](url, data)
        
        if response.status_code != 200:
            raise Exception(":(")

        return json.loads(response.text)

