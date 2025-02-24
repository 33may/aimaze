from scraper.content_processor import PageProcessor, ParsingError
from scraper.scraper_agent import ScraperAgent

# url = "https://openrouter.ai/docs/quickstart"
# url = "https://developers.kvk.nl/documentation"
url = "https://woocommerce.github.io/woocommerce-rest-api-docs/#introduction"

try:
    agent = ScraperAgent(url)

    agent = agent.scrape()

    print(33)

except ParsingError as pe:
    print("An error occurred while parsing the content:", pe)
