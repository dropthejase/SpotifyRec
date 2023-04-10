# Vibe-Based Spotify Recommender #

## Background ##
Data was sourced from:
Training files

## Quickstart ##
### Create a Client ID and Client Secret ###
You'll need, at the minimum, a client ID to use the web app.
Further API calls for the backend (e.g. in the api_util.py) will require a client secret as I use the 'client credientials' authorisation route for pulling data to train the model
1. Log into Spotify and head to the Dashboard: https://developer.spotify.com/dashboard
2. Click 'Create app' and complete the fields with anything you want (we just need to do this to create a Client ID and Client Secret)
3. Navigate to the root directory and create an .env file
            touch .env

4. Add your Client ID and Secret as follows:
            CLIENT_ID = "your_client_id"
            CLIENT_SECRET = "your_client_secret"

### Run the application ###
            python app.py

### Refreshing the database with new songs ###
Create a new python file and import util.py
            import util.py
Then use the following commands:
            util.refresh_predictions_csv() # to pull new playlists into a csv file
            util.refresh_table() # to fresh the SQLite DB

## Methodology ##
xxx

