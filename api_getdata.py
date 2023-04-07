import csv
from dotenv import load_dotenv
import json
import os
import re
import sys

from api_util import get_audio_features, get_token, get_track_popularity
from Playlist import Playlist

def get_filepath(path, low):
    prefix = "mpd.slice."
    filepath_low = low // 1000 * 1000
    filepath_high = filepath_low + 999

    filepath = f"{path}{prefix}{filepath_low}-{filepath_high}.json"
    return filepath, filepath_low, filepath_high

def get_playlists(filepath, low, high, regex=".*"):
    """
    Makes Playlist Objects objects based on a search string
    Arguments:
        filepath: path of the Spotify dataset files
        low: bottom end of the range of playlist IDs to search
        high: top range of the range of playlist IDs to search
        regex: search string to be used to select playlists
    """
    playlists = []
    pattern = re.compile(regex)

    with open(filepath) as file:
        parsed_json = json.loads(file.read())
        for i in range(low, high + 1):
            if re.match(pattern, parsed_json["playlists"][i]["name"].lower()):
                playlist = Playlist(parsed_json["playlists"][i]["name"])
                tracklist = parsed_json["playlists"][i]["tracks"]
                
                # add tracks to Playlist object
                for track in range(len(tracklist)):
                    playlist.add_track(tracklist[track]['track_name'], tracklist[track]['artist_name'], tracklist[track]['track_uri'][14:])
            
                playlists.append(playlist)
    return playlists

def total_songs(playlists):
    count = 0
    for playlist in playlists:
        count += len(playlist)
    return count

def create_csv(token, csv_filename, playlists, category_id, write_header=False):
    """
    Creates csv file with audio features based on list of Playlist Objects
    Arguments:
        token: access token
        csv_filename: filename for csv
        playlists: a list of Playlist Objects
        category_id: target label
    """
    if csv_filename == None:
        csv_filename = 'data.csv'
    if csv_filename[-4:] != '.csv':
        raise Exception("Please enter a valid csv - please include .csv in filename")
    if len(playlists) == 0:
        raise Exception("No Playlist Objects found")

    with open(csv_filename, 'a', encoding='utf-8', newline='') as csvfile:

        fieldnames = ['name','artist','id','popularity','acousticness','danceability','duration_ms','energy','instrumentalness','liveness','loudness','speechiness','tempo','valence','playlist_name', 'playlist_category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()

        for playlist in playlists:
            for n in range(len(playlist.tracklist)):
                name = playlist.tracklist[n][0]
                artist = playlist.tracklist[n][1]
                id = playlist.tracklist[n][2]

                # if key error for popularity, skip track
                try:
                    popularity = get_track_popularity(token, id)['popularity']
                except:
                    popularity = None
                # get audio features
                audio_features = get_audio_features(token, id)
                try:
                    writer.writerow({'name': name,
                                    'artist': artist,
                                    'id': id,
                                    'popularity': popularity,
                                    'acousticness': audio_features['acousticness'],
                                    'danceability': audio_features['danceability'],
                                    'duration_ms': audio_features['duration_ms'],
                                    'energy': audio_features['energy'],
                                    'instrumentalness': audio_features['instrumentalness'],
                                    'liveness': audio_features['liveness'],
                                    'loudness': audio_features['loudness'],
                                    'speechiness': audio_features['speechiness'],
                                    'tempo': audio_features['tempo'],
                                    'valence': audio_features['valence'],
                                    'playlist_name': playlist.name,
                                    'playlist_category': category_id})
                except:
                    continue


if __name__ == "__main__":
    # check command line
    if (len(sys.argv) != 2):
        sys.exit("Please enter a range <intA>-<intB>")
    args = sys.argv[1:]

    if "-" in args[0]:
        args = args[0].split("-")

        try:
            low = int(args[0])
            high = int(args[1])
        except:
            sys.exit("Please enter a valid range")

        if high < low:
            high, low = low, high
    
    else:
        try:
            low = int(args[0])
            high = low
        except:
            sys.exit("Please enter a valid range")
    
    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = get_token(client_id, client_secret)

    # get playlists
    path = 'data/'

    happy = []
    party = []
    chill = []
    sad = []

    range_low = low // 1000 * 1000
    while range_low <= high:
        # gets json slice
        filepath, filepath_low, filepath_high = get_filepath(path, range_low)
        if low <= filepath_low:
            filepath_low = 0
        else:
            filepath_low = low % 1000
        if high > filepath_high:
            filepath_high = 999
        else:
            filepath_high = high % 1000
        
        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(happy)|(inspir)|(workout)|(energy)|(motivation)|(summer)|(road).*")
        for playlist in playlists:
            happy.append(playlist)

        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(party)|(fun)|(dance)|(groove)|(club).*")
        for playlist in playlists:
            party.append(playlist)

        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(chill)|(focus)|(ambien)|(study)|(concentra)|(mood)|(work(?!.*out)).*") #|(work(?!.*out))
        for playlist in playlists:
            chill.append(playlist)
        
        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(sad)|(breakup)|(heartbr)|(moody)|(vibe)|(depress)|(angr)|(slow)|(alternative).*")
        for playlist in playlists:
            sad.append(playlist)
        
        range_low += 1000
    
    print("Happy: ", total_songs(happy))
    print("Party: ", total_songs(party))
    print("Chill: ", total_songs(chill))
    print("Sad: ", total_songs(sad))

    # create csv dataset
    # 0 - happy; 1 - party; 2 - chill; 3 - sad
    create_csv(token, 'data.csv', happy, 0, write_header=True)
    create_csv(token, 'data.csv', party, 1)
    create_csv(token, 'data.csv', chill, 2)
    create_csv(token, 'data.csv', sad, 3)
