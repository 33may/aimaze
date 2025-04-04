import psycopg2

from src.scraper.scraper import bfs_site

DB_NAME = "pages_cache"
DB_USER = "postgres"
DB_PASSWORD = "storage"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_connection():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        create table if not exists pages (
            url TEXT primary key,
            html TEXT,
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def get_page_by_url(url:str) -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT html FROM pages WHERE url = %s", (url,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row[0] if row else None

def store_page(url: str, html: str) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO pages (url, html)
        VALUES (%s, %s)
        on conflict do nothing
    ''', (url, html))
    conn.commit()
    cur.close()
    conn.close()

def add_api_to_db(url: str, domain_url: str) -> None:
    data = bfs_site(url, lambda content: True, domain_url)

    scraped_pages = data.get("endpoint_pages", {})

    for key, value in scraped_pages.items():
        store_page(key, value)


if __name__ == "__main__":
    # add_api_to_db("https://developers.hubspot.com", "/docs/")
    add_api_to_db("https://support.anewspring.com", "/en/")