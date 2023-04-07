from dotenv import load_dotenv
import os
import sys

from api_util import api_call, get_audio_features, get_category_playlists, get_token, get_single_playlist, get_track_popularity
import util


if __name__ == "__main__":

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = get_token(client_id, client_secret)

    summer_songs = get_single_playlist(token, "37i9dQZF1DWSwyaV6GLT48")

    # get track_id
    track_id = input("Enter track ID: \n")

    # get prediction
    try:
        X = util.prepare_prediction(token, track_id)
    except:
        print("Something went wrong - please check your track ID and try again.")
        sys.exit()

    prediction = util.predict(X)
    print(prediction)

    