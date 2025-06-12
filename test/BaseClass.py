from requests import get, post
import base64
import json

METHODS = {"GET": get,
           "POST": post}

class APIWrapper():
    def __init__(self, config, base_url: str, name: str):
        self.config = config
        self.base_url = base_url
        self.name = name

    def request(self, method: str, url: str, args_in_url: bool, data: dict) -> dict[str, any]:
        if args_in_url:
            url = url.format(**data)  # TODO: Take in-url args out of payload.

        data["scope"] = ['user-library-read',
                         'user-library-modify',
                         'playlist-read-private',
                         'playlist-read-collaborative',
                         'playlist-modify-private',
                         'playlist-modify-public']

        response = METHODS[method](
            url, data=data,
            headers={"Authorization": f"Basic {base64.b64encode("a766651ba4b744ed82f1e520a75b2455:767732da0b064b838ebe5d0e3f6ce4eb".encode("ascii")).decode("ascii")}"}
        )
        
        if response.status_code != 200:
            raise Exception(response.text)

        return json.loads(response.text)

