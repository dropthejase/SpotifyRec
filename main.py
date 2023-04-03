from dotenv import load_dotenv
import os
from api_util import get_category_playlists, get_token
from Playlist import Playlist

def make_playlists(token, genre, limit):
    '''
    Arguments:
        token: access token
        genre: category ID e.g. "dinner"
        limit: how many results to return
    Returns: A list of Playlist objects
    '''
    playlists = []
    result = get_category_playlists(token=token, category_id=genre, limit=limit)
    for name, url in result.items():
        x = Playlist(token, name, url)
        playlists.append(x)
    return playlists

def main():

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = get_token(client_id, client_secret)

    # get category's playlist {name: api_url}
    dinnerplaylists = make_playlists(token, 'dinner', 5)
    print(dinnerplaylists)


if __name__ == "__main__":
    main()