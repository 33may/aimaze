from src.scraper.scraper import bfs_site
from src.scraper.scraper_benchmark import benchmark_scraper

# link="https://developers.hubspot.com/docs"
#
# a = bfs_site(link, lambda content: True, slowdown_s=0.01)
#
# print(len(a))
# print(a.keys())


benchmark_scraper(lambda content: True, num_apis=1)