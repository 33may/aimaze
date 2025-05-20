from src.scraper.scraper import bfs_site
from src.scraper.scraper_benchmark import benchmark_scraper

# link="https://developers.hubspot.com/docs"
#
# a = bfs_site(link, lambda content: True, slowdown_s=0.01)
#
# print(len(a))
# print(a.keys())


# benchmark_scraper(lambda content: True)








from openai import OpenAI
client = OpenAI()                     # api_key можно оставить в переменной окружения

response = client.chat.completions.create(
    model="gpt-4o-2024-08-06",          # убедитесь, что используете свежий снапшот
    messages=[{"role": "user", "content": "ping"}],
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "PingResponse",
            "schema": JSON_SCHEMA,
            "strict": True              # опционально: запретит любые отклонения
        }
    },
    temperature=0,
)
print(response.choices[0].message.content)
# → {"msg":"pong"}