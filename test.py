from scraper.content_processor import ContentProcessor, ParsingError

url = "https://openrouter.ai/docs/quickstart"

try:
    processor = ContentProcessor(url)
    links = processor.get_all_links()
    print("Links found:", links)
except ParsingError as pe:
    print("An error occurred while parsing the content:", pe)
