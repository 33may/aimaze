from scraper.content_processor import get_content, html_to_md, get_all_links, ParsingError

url = "https://openrouter.ai/docs/quickstart"

try:
    content = get_content(url)
    internal_links = get_all_links(content, url)
    print("Internal Links found:", internal_links)
except ParsingError as pe:
    print("An error occurred while parsing the content:", pe)
