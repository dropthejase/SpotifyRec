from requests import get, post

def get_token(client_id, client_secret):
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
    headers = {"Authorization" : "Bearer " + token}
    result = get(url, headers=headers)
    json_result = result.json()
    
    return json_result

def get_category_playlists(token, category_id, country="GB", limit=1, offset=0):
    '''
    Gets category playlists
    Arguments:
        category_id: category - e.g. "dinner"
        country: country in ISO 3166-1 alpha-2 country code
        limit: how many results to return
        offset: index of first item to return
    Returns: A dict comprising:
        name: name of playlist
        api: spotify call to get tracks in playlist
    '''
    url = f"https://api.spotify.com/v1/browse/categories/{category_id}/playlists?country={country}&offset={offset}&limit={limit}"
    items = api_call(token, url)["playlists"]["items"]

    result = {}
    for item in range(len(items)):
        name = items[item]["name"]
        playlist_api = items[item]["href"]
        result[name] = playlist_api

    return result