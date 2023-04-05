import csv
from dotenv import load_dotenv
import json
import os
import re
import sys

from api_util import get_audio_features, get_token
from Playlist import Playlist

'''
def make_playlists(token, category_id, limit=5):
    """
    Makes Playlist Objects based on category id
    Arguments:
        token: access token
        category_id: category ID e.g. "dinner"
        limit: how many results to return
    Returns: A list of Playlist objects
    """
    playlists = []
    result = get_category_playlists(token=token, category_id=category_id, limit=limit)
    for name, url in result.items():
        x = Playlist(token, name, url)
        playlists.append(x)
    return playlists
'''

def get_filepath(path, low):
    prefix = "mpd.slice."
    filepath_low = low // 1000 * 1000
    filepath_high = filepath_low + 999

    filepath = f"{path}{prefix}{filepath_low}-{filepath_high}.json"
    return filepath, filepath_low, filepath_high

def get_playlists(filepath, low, high, regex=".*"):
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

# create csv
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

        fieldnames = ['name','artist','id','acousticness','danceability','duration_ms','energy','instrumentalness','liveness','loudness','speechiness','tempo','valence','playlist_name', 'playlist_category']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if write_header:
            writer.writeheader()

        for playlist in playlists:
            for n in range(len(playlist.tracklist)):
                name = playlist.tracklist[n][0]
                artist = playlist.tracklist[n][1]
                id = playlist.tracklist[n][2]
                audio_features = get_audio_features(token, id)
                try:
                    writer.writerow({'name': name,
                                    'artist': artist,
                                    'id': id,
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

    morning = []
    afternoon = []
    evening = []
    sleep = []

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
        
        # morning
        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*morning.*")
        for playlist in playlists:
            morning.append(playlist)
        
        # afternoon
        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(afternoon)|(study)|(lunch)|(work(?!.*out)).*")
        for playlist in playlists:
            afternoon.append(playlist)
        
        # evening
        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(dinner)|(evening)|(night)|(late)|(sunset).*")
        for playlist in playlists:
            evening.append(playlist)
        
        # sleep
        playlists = get_playlists(filepath, filepath_low, filepath_high, ".*(sleep)|(bed).*")
        for playlist in playlists:
            sleep.append(playlist)
        
        range_low += 1000
    
    # create csv dataset
    # 0 - morning, 1 - afternoon, 2 - evening, 3 - sleep
    create_csv(token, 'data.csv', morning, 0, write_header=True)
    create_csv(token, 'data.csv', afternoon, 1)
    create_csv(token, 'data.csv', evening, 2)
    create_csv(token, 'data.csv', sleep, 3)