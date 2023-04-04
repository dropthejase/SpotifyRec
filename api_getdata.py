from dotenv import load_dotenv
import os
from api_util import api_call, get_audio_features, get_category_playlists, get_token
from Playlist import Playlist
import csv

def make_playlists(token, category_id, limit=5):
    '''
    Makes Playlist Objects based on category id
    Arguments:
        token: access token
        category_id: category ID e.g. "dinner"
        limit: how many results to return
    Returns: A list of Playlist objects
    '''
    playlists = []
    result = get_category_playlists(token=token, category_id=category_id, limit=limit)
    for name, url in result.items():
        x = Playlist(token, name, url)
        playlists.append(x)
    return playlists

# create csv
def create_csv(token, csv_filename, playlists, category_id):
    """
    Creates csv file with audio features based on list of Playlist Objects
    Arguments:
        token: access token
        csv_filename: filename for csv
        playlists: a list of Playlist Objects
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
def main():

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = get_token(client_id, client_secret)

    # get category's playlist - creates 5 playlist objects
    morningplaylists = make_playlists(token, 'workout', 5)
    afternoonplaylists = make_playlists(token, 'focus', 5)
    dinnerplaylists = make_playlists(token, 'dinner', 5)
    bedtimeplaylists = make_playlists(token, 'sleep', 5)

    # write to csv file
    # 0 - workout, 1 - focus, 2 - dinner, 3 - sleep
    create_csv(token, 'data.csv', morningplaylists, 0)
    create_csv(token, 'data.csv', afternoonplaylists, 1)
    create_csv(token, 'data.csv', dinnerplaylists, 2)
    create_csv(token, 'data.csv', bedtimeplaylists, 3)
    

if __name__ == "__main__":
    main()