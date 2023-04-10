# Vibe-Based Spotify Recommender #

## Background ##
The Vibe-Based Spotify Recommender uses a Random Forest classifier trained on around 20,000 songs to be able to classify the 'vibe' of a track (either party, chill, or sad), based on audio features of each song according to the Spotify API.

This is then used to classify new songs from Spotify's featured playlists under the 'toplists' category, which is stored in a SQL database.

The recommender then queries the the database to provide song recommendations for each vibe. The user can then create a playlist with these songs.

The user can also enter a track ID to see what vibe the algorithm predicts.

I used this project as a way to:
* Practice using ML algorithms on my own sourced datasets
* Practice deploying an ML model
* Practice using APIs to pull data
* Practice creating web apps using Flask

I'm passionate about music production so thought this would be a cool project.

## Quickstart ##
### Create a Client ID and Client Secret ###
You'll need, at the minimum, a client ID to use the web app.
Further API calls for the backend (e.g. in the api_util.py) will require a client secret as I use the 'client credientials' authorisation route for pulling data to train the model
1. Log into Spotify and head to the Dashboard: https://developer.spotify.com/dashboard
2. Click 'Create app' and complete the fields with anything you want (we just need to do this to create a Client ID and Client Secret)
3. Navigate to the root directory and create an .env file
```
touch .env
```
4. Add your Client ID and Secret as follows:

```
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
```

### Run the application ###
Create a virtual environment and install the required packages:
```
pip install -r requirements.txt
```
Then run app.py:
```
python app.py
```

### Refreshing the database with new songs ###
Create a new python file and import util.py

```
import util.py
```
    
Then use the following commands:
```
util.refresh_predictions_csv() # to pull new playlists into a csv file
util.refresh_table() # to fresh the SQLite DB
```

## Methodology ##
The Vibe-Based Spotify Recommender uses a Random Forest classifier trained on roughly 20,000 songs.
Songs were gathered by looking through 5000 playlists from the Spotify Million Playlist Dataset (https://www.aicrowd.com/challenges/spotify-million-playlist-dataset-challenge) to see if any had the following words as their playlist name:
* **Party vibe:** "party", "fun", "dance", "groove", "club" - to capture upbeat songs. Use cases: parties
* **Chill vibe:** "chill", "focus", "ambien[ce/t]", "study", "concentra[te/tion]", "mood", "work" (but not "workout") - to capture less upbeat, but generally positive songs. Use cases: studying, background music
* **Sad vibe:** "sad", "breakup", "heartbr[eak]", "moody", "vibe", "depress", "angr", "slow", "alternative". Use cases: type of song you listen to when you're upset

I then removed playlists with (what I felt were) unrelated to the representation of the vibe I was going for. For example, I removed playlists to do with wedding parties and in one case, a funeral party, from the 'party' playlists that were captured.

I then cleaned the data and removed duplicate tracks.

I then used the lazypredict library to quickly check which ML algorithms performed well - the Random Forest was one of the higher ones. I then tested to see which max depth provided the highest validation accuracy (and found that accuracy generally levelled off after a max depth of 15).

I also used PyTorch to see if an ANN could beat the Random Forest, but it appears to not be able to (performing at around 55% validation accuracy).

The final model is then used to predict the vibe of new songs from the 'toplists' category from Spotify, as well as any track ID that the user wishes to feed into the algorithm.

### Limitations ###
* The model works out to be about 76% accurate when used on the test set
* My approach to creating 'true' labels to train the classifier relied on what Spotify users named their playlists. However, music is subjective: someone's 'party playlist' will sound different from another
* A 'party' vibe does not necessarily just mean upbeat, loud EDM songs. An 80s party for example, will have songs with different characteristics.
* My search keywords may not be expansive enough
* The scores of audio features provided by Spotify might also be subjective

