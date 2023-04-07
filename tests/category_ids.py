### haven't figured out importing yet so have to move this out of test folder to work

from dotenv import load_dotenv
import os
from api_util import api_call, get_token


# Load .env variables
load_dotenv()
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# get access token
token = get_token(client_id, client_secret)

# get categories list (globally relevant)
categories_list = []


next = "https://api.spotify.com/v1/browse/categories?country=US&offset=0&limit=50"
while next:
    result = api_call(token, next)['categories']
    N = len(result['items'])
    for i in range(N):
        categories_list.append(result['items'][i]['name'])
    next = result['next']

print(sorted(categories_list))

