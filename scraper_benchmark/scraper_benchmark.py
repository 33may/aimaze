import json
from time import sleep
from typing import Callable, Dict, Union
from loguru import logger

from src.scraper.eval_db.db_utils import store_page
from src.scraper.scraper import bfs_site


def add_api_to_db(url: str, domain_url: str) -> None:

    with open('../benchmark_data.json', 'r') as file:
        data = json.load(file)
        for obj in data:
            if obj.get("base_url") == url:
                endpoint_pages = obj.get("endpoint_pages")


    data = bfs_site(url, lambda content: True, domain_url)

    all_scraped_pages = data.get("endpoint_pages", {})

    for key, value in all_scraped_pages.items():
        is_endpoint = key in endpoint_pages
        store_page(key, value, is_endpoint)


def benchmark_scraper(
        filter_fn: Callable[[str], bool],
        use_db = True,
        log=True,
        num_apis: Union[str, int] = "all",
) -> None:
    """
    Benchmarks the scraping function across multiple APIs from the benchmark dataset.

    Parameters:
      filter_fn: A filter function maps the page content (str) to the answer "is this page endpoint" .
                  Each filter function should accept a page's content (str) and return a bool.
      use_db: Flag to use db over the web scraping.
      num_apis: How many APIs to benchmark. Use "all" for every API in the dataset. If an integer,
                it must not exceed the number of APIs in the dataset.

    The final results are saved to "benchmark_summary.json".
    """

    # Load benchmark data from JSON file
    with open("benchmark_data.json", "r", encoding="utf-8") as f:
        benchmark_data = json.load(f)

    # which APIs to process
    if num_apis == "all":
        apis_to_process = benchmark_data
    else:
        num = int(num_apis)
        if num > len(benchmark_data):
            raise ValueError(
                f"num_apis ({num}) exceeds the available APIs ({len(benchmark_data)}) in the dataset."
            )
        apis_to_process = benchmark_data[:num]

    api_stats = {}
    total_expected = 0
    total_scraped = 0
    total_matched = 0

    # Process each API
    for api in apis_to_process:
        api_name = api.get("name", "Unnamed API")
        base_url = api.get("base_url")
        domain_url = api.get("domain_url")
        expected_pages = set(api.get("endpoint_pages", []))
        total_expected += len(expected_pages)

        logger.info(f"Benchmarking API: {api_name} ({base_url})")

        scraped_result = bfs_site(base_url, filter_fn, domain_url, use_db=use_db, log=log)

        scraped_pages = set(scraped_result.get("endpoint_pages", {}).keys())
        total_scraped += len(scraped_pages)

        # Calculate intersection (matched endpoints)
        matched_pages = expected_pages.intersection(scraped_pages)
        total_matched += len(matched_pages)

        # Compute coverage
        coverage = (len(matched_pages) / len(expected_pages)) if expected_pages else 1.0

        api_stats[api_name] = {
            "expected": len(expected_pages),
            "scraped": len(scraped_pages),
            "matched": len(matched_pages),
            "coverage": coverage,
            "missing": list(expected_pages - matched_pages),
            "extra": list(scraped_pages - expected_pages),
        }

        logger.info(
            f"API {api_name}: Expected {len(expected_pages)}, "
            f"Scraped {len(scraped_pages)}, Matched {len(matched_pages)}, "
            f"Coverage {coverage * 100:.2f}%"
        )

    overall_coverage = (total_matched / total_expected)

    benchmark_results = {
        "overall": {
            "total_expected": total_expected,
            "total_scraped": total_scraped,
            "total_matched": total_matched,
            "overall_coverage": overall_coverage,
        },
        "apis": api_stats,
    }

    with open("benchmark_summary.json", "w", encoding="utf-8") as out_file:
        json.dump(benchmark_results, out_file, indent=4)

    logger.info("Benchmark completed. Summary written to benchmark_summary.json")