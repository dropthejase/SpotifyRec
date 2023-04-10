from requests import get, post
from Playlist import Playlist

def get_token(client_id, client_secret):
    """
    Creates an access token, given a client_id and client_secret.
    This is required every time we send a GET request towards the Spotify API
    Arguments:
        client_id: your client ID
        client_secret: your client secret
    Returns:
        A temporary access token
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content_Type" : "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type" : "client_credentials",
        "client_id" : client_id,
        "client_secret": client_secret}

    result = post(url, headers=headers, data=data)
    json_result = result.json()
    token = json_result["access_token"]
    
    return token

def api_call(token, url):
    """
    Calls the Spotify API
    Arguments:
        token: access token
        url: the url for the GET request - this will depend on what you wish to extract from the Spotify API
    Returns:
        The API's response in JSON format
    """
    headers = {"Authorization" : "Bearer " + token}
    result = get(url, headers=headers)
    json_result = result.json()
    return json_result

def get_audio_features(token, id):
    """
    Gets audio features analysis for a track from Spotify API
    Arguments:
        token: access token
        id: track ID
    Returns:
        A JSON of the audio features - same response from the Spotify API
    """
    url = f"https://api.spotify.com/v1/audio-features/{id}"
    return api_call(token, url)

def get_category_playlists(token, category_id, country="GB", limit=1, offset=0):
    """
    Gets category's playlists from Spotify API
    Arguments:
        category_id: category - e.g. "dinner"
        country: country in ISO 3166-1 alpha-2 country code
        limit: how many results to return
        offset: index of first item to return
    Returns:
        A dict comprising:
            name: name of playlist
            playlist_id: playlist ID
    """
    url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists?country={country}&offset={offset}&limit={limit}"
    items = api_call(token, url)["playlists"]["items"]

    result = {}
    for item in range(len(items)):
        name = items[item]["name"]
        playlist_id = items[item]["id"]
        result[name] = playlist_id

    return result

def get_single_playlist(token, playlist_id):
    """
    Creates a Playlist object from a single playlist ID
    Arguments:
        token: access token
        playlist_id: playlist ID
    Returns:
        A Playlist object
    """
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    result = api_call(token, url)
    playlist = Playlist(result['name'])

    # just add first 100 tracks if playlist exceeds it
    if result['tracks']['total'] <= 100:
        num_tracks = result['tracks']['total']
    else:
        num_tracks = 100
    
    for i in range(num_tracks):
        try:
            track_name = result['tracks']['items'][i]['track']['name']
            track_artist = result['tracks']['items'][i]['track']['artists'][0]['name']
            track_id = result['tracks']['items'][i]['track']['id']
            playlist.add_track(track_name, track_artist, track_id)
        except:
            continue
    
    return playlist

def get_track_popularity(token, id):
    """
    Gets popularity of a track from Spotify API
    Arguments:
        token: access token
        id: track ID
    Returns:
        A JSON of the audio features - same response from the Spotify API
    """
    url = f"https://api.spotify.com/v1/tracks/{id}"
    result = api_call(token, url)
    return result['popularity']