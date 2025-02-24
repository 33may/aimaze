from scraper.content_processor import ContentProcessor, ParsingError

url = "https://openrouter.ai/docs/quickstart"

try:
    processor = ContentProcessor(url)
    internal_links, external_links = processor.get_all_links()
    print("Internal Links found:", internal_links)
    print("External Links found:", external_links)
except ParsingError as pe:
    print("An error occurred while parsing the content:", pe)
