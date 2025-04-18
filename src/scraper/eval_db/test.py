import requests
from pprint import pprint

payload={
    'source': 'universal',
    'url': 'https://developers.hubspot.com/docs/reference/api/cms/media-bridge',
}

# Get response.
response=requests.request(
    'POST',
    'https://realtime.oxylabs.io/v1/queries',
    auth=('antonnedf@gmail.com','Thecyclone2112+'),
    json=payload,)

# Instead of response with job status and results url,
# this will return the JSON response with results.
pprint(response.json())

print(33)