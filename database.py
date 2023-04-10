### MOVE THIS ALL TO UTIL ###

import sqlite3
from api_util import get_audio_features, get_category_playlists, get_single_playlist, get_token
from dotenv import load_dotenv
from util import create_csv_from_model
import os
import csv

def refresh_predictions_csv(token, category_id="toplists", limit=25):

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

    # delete all entries
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute(f"DELETE FROM {table_name}")
    c.commit()

    # add new data
    with open(csvfilename) as csvfile:
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


    
    