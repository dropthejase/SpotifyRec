from api_util import api_call

class Playlist:
    def __init__(self, token, name, api_url):
        self.name = name
        self.api_url = api_url
        self.tracklist = []
        
        tracks = api_call(token, api_url + "/tracks")['items']
        for i in range(len(tracks)):
             self.tracklist.append((tracks[i]['track']['name'], tracks[i]['track']['artists'][0]['name'], tracks[i]['track']['href']))

    def __iter__(self):
        for track in range(len(self.tracklist)):
            yield(self.tracklist[track])