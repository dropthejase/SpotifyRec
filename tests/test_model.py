### haven't figured out importing yet so have to move this out of test folder to work

from dotenv import load_dotenv
import os
import sys

import api_util, util

def accuracy(results, answer):
    correct = 0
    N = len(results)
    for i in results:
        if i == answer:
            correct += 1
    return correct / N

if __name__ == "__main__":

    # Load .env variables
    load_dotenv()
    client_id = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")

    # get access token
    token = api_util.get_token(client_id, client_secret)

    # get songs from 'summer songs' playlist
    if len(sys.argv) != 2:
        sys.exit("Enter a playlist ID")
    
    playlist = api_util.get_single_playlist(token, sys.argv[1])
 
    # get prediction
    predictions_name = []
    predictions = []

    for track in range(len(playlist)):
        track_name = playlist.tracklist[track][0]
        track_id = playlist.tracklist[track][2]
        X = util.prepare_prediction(token, track_id)
        X = util.predict(X)
        predictions_name.append([track_name, X['prediction']])
        predictions.append(X['prediction'])
    
    correct = 0

    for i in predictions_name:
        print(i)
    
    print("Accuracy: ", accuracy(predictions, "chill"))
