# Automatic API Wrapper

## File/folder Setup

- **src/**;
    - **gen/** is the core of the codebase;
        - **gen.py** is the essentially the entrypoint with functions extract_schemas and generate_code;
        - **chunker.py** chunks pages too big for a single call;
        - **transpiler.py** takes the generated schemas and converts them to Python code;
        - **types.py** contains the predefined AIMaze types with some small tweaks;

    - **schemas.py** contains all the schema's used to structure imformation extracted by the LLM;
    - **scrape.py** contains a Selenium and requests.get scraper, along with a BFS search to scrape all linkes encountered;
    - **main.py** is the entrypoint of the entire project, also contains the simple CLI;
- **scraper_benchmark/** contains benchmarking tools and data for further iterations of the scraper;
- **test/** contains testing outputs, which can also function as generated examples;


## How to use
Simply run 'python src/main.py' (or better yet, assign an alias so you can run it in any directory). You will then be asked to enter some information about the API/project. All of this is quite self explanatory (especially with the examples at the top of main.py) except for the scraping domains. 
A scraping domain is simply a starting page for BFS scrape + a scope. For instance: '/rest/en/start.html' + 'rest/en'. In this case, without that domain/scope every translation of the API in 'rest/...' would be scraped as well. Setting the domain allows you to omit parts of the documentation that aren't necessary. In some documentation structures you might need multiple of these. For instance, the GitHub API is essentially 20+ API's bundled together, and you might not need all. 
