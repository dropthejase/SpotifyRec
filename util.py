from dotenv import load_dotenv
import pandas as pd
import numpy as np
import pickle
import os
import time

from api_util import get_audio_features, get_token

def prepare_prediction(token, track_id):

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

def predict_vibe(track_id):

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = get_token(client_id, client_secret)

    # prepare data
    while True:
        try:
            print("Analysing...")
            time.sleep(3)
            X = prepare_prediction(token, track_id)
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
        
    return {'prediction': response}

