
import base64
import csv
import hashlib
import os
import pickle
import string
import secrets
import sqlite3

from dotenv import load_dotenv
import numpy as np
from requests import post, Request

from api_util import get_audio_features, get_category_playlists, get_single_playlist, get_token

########################### PKCE AUTHENTICATION ###########################

def generate_randomstring(n):
    """
    Generates random string
    Arguments:
        n: length of string
    Returns:
        A randomly generated string
    """
    alphabet = string.ascii_letters + string.digits
    code_verifier = ''.join(secrets.choice(alphabet) for i in range(n))
    return code_verifier


def generate_code_challenge(code_verifier):
    """
    Transforms code verifier using SHA256 algorithm, creating digest
    Then the digest is encoded into base64
    Arguments:
        code_verifier: the code verifier
    Returns:
        Base64 encoding of digest - serves as the code challenge
    """
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    return code_challenge


def get_auth_code():
    """
    Creates an authorisation code to send for an access token.
    Returns:
        Authorisation code
    """

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")

    url = "https://accounts.spotify.com/authorize?"
    scope = "user-read-private user-read-email playlist-modify-public playlist-modify-private"
    redirect_uri = "http://localhost:5000/callback"
    state = generate_randomstring(16)
    code_verifier = generate_randomstring(128)
    code_challenge = generate_code_challenge(code_verifier)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge
    }

    request = Request('GET', url, params=params)
    request = request.prepare()
    
    return request.url, code_verifier


def get_token_pkce(auth_code, code_verifier):

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")

    url = "https://accounts.spotify.com/api/token"
    redirect_uri = "http://localhost:5000/callback"

    headers = {
        "Content_Type" : "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type" : "authorization_code",
        "code" : auth_code,
        "client_id" : client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier
    }
    
    request = Request('POST', url, headers=headers, data=data)
    request = request.prepare()

    result = post(url, headers=headers, data=data)
    json_result = result.json()
    access_token = json_result["access_token"]
    refresh_token = json_result["refresh_token"]
    expires_in = json_result["expires_in"]

    return access_token, refresh_token, expires_in

########################### MAKING VIBE PREDICTIONS ###########################

def prepare_prediction(token, track_id):
    """
    Gets audio features, given an access token and track ID
    and returns and prepared Numpy array
    Arguments:
        token: access token
        track_id: Track ID
    Returns:
        Prepared Numpy array of shape (1, 10) to pass into model
    """

    audio_features = get_audio_features(token, track_id)
    X = np.zeros((1,10))

    try:
        X[:,0] = audio_features['acousticness']
        X[:,1] = audio_features['danceability']
        X[:,2] = audio_features['duration_ms']
        X[:,3] = audio_features['energy']
        X[:,4] = audio_features['instrumentalness']
        X[:,5] = audio_features['liveness']
        X[:,6] = audio_features['loudness']
        X[:,7] = audio_features['speechiness']
        X[:,8] = audio_features['tempo']
        X[:,9] = audio_features['valence']

        return X
    
    except:
        raise Exception
    

def predict_vibe(access_token, track_id):

    # prepare data
    while True:
        try:
            X = prepare_prediction(access_token, track_id)
            break
        except:
            return "Something went wrong - please check your track ID and try again."

    # make prediction
    PREDICTION_LIST = ['party', 'chill', 'sad']
    MODEL = pickle.load(open('pipe_rf.pkl','rb'))
    
    pY = MODEL.predict(X)

    if pY == 1:
        response = PREDICTION_LIST[0]
    elif pY == 2:
        response = PREDICTION_LIST[1]
    else:
        response = PREDICTION_LIST[2]
        
    return response


def create_csv_from_model(token, csv_filename, playlists, write_header=False):
    """
    Creates csv file with audio features based on list of Playlist Objects
    Arguments:
        token: access token
        csv_filename: filename for csv
        playlists: a list of Playlist Objects
        category_id: label based on model
    """
    if csv_filename == None:
        csv_filename = 'data.csv'
    if csv_filename[-4:] != '.csv':
        raise Exception("Please enter a valid csv - please include .csv in filename")
    if len(playlists) == 0:
        raise Exception("No Playlist Objects found")

    with open(csv_filename, 'w', encoding='utf-8', newline='') as csvfile:

        fieldnames = ['name','artist','id','playlist_name', 'vibe']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_NONE)

        if write_header:
            writer.writeheader()

        for playlist in playlists:
            for n in range(len(playlist.tracklist)):
                name = playlist.tracklist[n][0]
                artist = playlist.tracklist[n][1]
                id = playlist.tracklist[n][2]

                # make prediction
                predicted_vibe = predict_vibe(token, id)

                # write to csv
                try:
                    writer.writerow({'name': name,
                                    'artist': artist,
                                    'id': id,
                                    'playlist_name': playlist.name,
                                    'vibe': predicted_vibe})
                except:
                    continue

########################### DATABASE / RECOMMENDING PLAYLISTS ###########################

def refresh_predictions_csv(token, category_id="toplists", limit=25):
    """
    Refreshes list of songs based on Spotify category ID (default = 'toplists' category)
    Then pulls songs from the playlists collected, runs them through model and creates 'predictions.csv'
    Arguments:
        token: access token
        category_id: playlist category_id
        limit: how many playlists to look at
    """
    # Get access token
    load_dotenv()
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    token = get_token(client_id, client_secret)

    # Get playlists
    toplist_playlists = get_category_playlists(token=token, category_id=category_id,limit=limit)

    # Create Playlist objects
    playlists = []
    for name, id in toplist_playlists.items():
        playlist = get_single_playlist(token, id)
        playlists.append(playlist)
    
    # Create csv with predictions
    create_csv_from_model(token, 'predictions.csv', playlists, True)


def refresh_table(db_name='topplaylist_songs.db', table_name='predictions', csvfilename='predictions.csv'):
    """
    Refreshes database from predictions.csv
    Arguments:
        db_name: name of DB
        table_name: name of table
        csvfilename: filename of csv file to pull data into table
    """
    # delete all entries
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name}")
    conn.commit()

    # add new data
    with open(csvfilename, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        id = 0
        for row in reader:
            if id == 0:
                id += 1
                continue

            c.execute(f"""INSERT INTO {table_name} (name, artist, track_id, playlist_name, vibe)
                        VALUES (?, ?, ?, ?, ?)""", (row[0], row[1], row[2], row[3], row[4]))

            id += 1

    conn.commit()
    conn.close()


def create_table(db_name='topplaylist_songs.db', table_name='predictions'):
    """
    Creates a table
    Arguments:
        db_name: name of DB
        table_name: name of table to create
    """
    # connect to db
    conn = sqlite3.connect(db_name)

    # create a cursor
    c = conn.cursor()

    # create table
    c.execute(f"""CREATE TABLE {table_name} (
            name TEXT,
            artist TEXT,
            track_id TEXT,
            playlist_name TEXT,
            vibe TEXT
        )""")
    
    # commit to db
    conn.commit()

    # close connection
    conn.close()


def song_recs(db_name='topplaylist_songs.db', table_name='predictions', vibe='party', limit=25):
    """
    Creates a list of recommended songs based on vibe selected using SQL query
    Arguments:
        db_name: name of DB
        table_name: name of table
        vibe: vibe chosen
        limit: how many songs to pull
    Returns:
        A list of songs
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    c.execute(f"""SELECT * FROM {table_name}
                    WHERE rowid IN (SELECT MAX(rowid) FROM {table_name} GROUP BY track_id)
                        AND vibe = '{vibe}'
                    ORDER BY RANDOM()
                    LIMIT({limit})""")

    recommended_playlist = c.fetchall()

    conn.commit()
    conn.close()

    return recommended_playlist