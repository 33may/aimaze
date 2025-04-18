import psycopg2

DB_NAME = "pages_cache"
DB_USER = "may"
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
            is_endpoint BOOLEAN)
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

def get_api_pages_by_url(url: str) -> list:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT html FROM pages WHERE url LIKE %s and is_endpoint = True", (f"%{url}%",))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def is_site_in_db(url: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pages WHERE url LIKE %s LIMIT 1", (f"%{url}%",))
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

def store_page(url: str, html: str, is_endpoint: bool) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO pages (url, html, is_endpoint)
        VALUES (%s, %s, %s)
        on conflict do nothing
    ''', (url, html, is_endpoint))
    conn.commit()
    cur.close()
    conn.close()
