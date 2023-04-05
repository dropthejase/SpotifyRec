class Playlist:
    def __init__(self, name):
        self.name = name
        self.tracklist = []

    def __iter__(self):
        for track in range(len(self.tracklist)):
            yield(self.tracklist[track])
    
    def __len__(self):
        return len(self.tracklist)
    
    def add_track(self, name, artist, id):
        self.tracklist.append([name, artist, id])