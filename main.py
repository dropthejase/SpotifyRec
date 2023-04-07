from dotenv import load_dotenv
import os

from api_util import get_audio_features, get_category_playlists, get_token, get_track_popularity
import util


if __name__ == "__main__":

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = get_token(client_id, client_secret)

    # get track_id
    track_id = input("Enter track ID: \n")

    # get prediction
    X = util.prepare_prediction(token, track_id)
    prediction = util.predict(X)
    print(prediction)