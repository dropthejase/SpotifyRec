from datetime import datetime, timedelta
import os
import time

from dotenv import load_dotenv
from flask import Flask, flash, render_template, request, session, redirect, url_for

from api_util import api_call, api_call_post, expired, get_refresh_token, get_token
import util

load_dotenv()

app = Flask(__name__)
app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
app.config['SECRET_KEY'] = util.generate_randomstring(16).encode('utf-8')
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for("playlists"))
    return render_template("index.html")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        # redirect to Spotify login
        get_auth_code = util.get_auth_code()
        app.config['CODE_VERIFIER'] = get_auth_code[1]
        return redirect(get_auth_code[0])
    else:
        return redirect(url_for("index"))


@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    code_verifier = app.config.get('CODE_VERIFIER')

    start_time = time.time()

    access_token, refresh_token, expires_in = util.get_token_pkce(auth_code, code_verifier)

    session['access_token'] = access_token
    session['refresh_token'] = refresh_token
    session['expires_in'] = start_time + expires_in

    # get user's name and store in a session
    user = api_call(access_token, "https://api.spotify.com/v1/me")["display_name"]
    user_img = api_call(access_token, "https://api.spotify.com/v1/me")['images'][0]["url"]
    user_id = api_call(access_token, "https://api.spotify.com/v1/me")["id"]

    session.permanent = True
    session['user'] = user
    session['user_img'] = user_img
    session['user_id'] = user_id

    return redirect(url_for("playlists"))


@app.route('/track_id', methods=['POST', 'GET'])
def track_id():
    if request.method == 'POST':
        if 'user' in session:
            user = session.get('user')
            user_img = session.get('user_img')
            access_token = session.get('access_token')
            track_id = request.form['track_id_input']

            # Time check
            expires_in = session.get('expires_in')
            if expired(time.time(), expires_in):
                access_token, expires_in = get_refresh_token(session['refresh_token'], app.config['CLIENT_ID'])
                session['access_token'] = access_token
                session['expires_in'] = time.time() + expires_in

            if track_id == "":
                flash("Please enter a track ID into the box above")
                return render_template("track_id.html", user=user, user_img=user_img)
            
            else:
                prediction = util.predict_vibe(access_token, track_id)
                flash("Result: " + prediction)
                return render_template("track_id.html", user=user, user_img=user_img, track_id=track_id, prediction=prediction)
        
        else:
            return redirect(url_for("login"))
    else:
        if 'user' in session:
            user = session.get('user')
            user_img = session.get('user_img')
            return render_template('track_id.html', user=user, user_img=user_img)
        else:
            return redirect(url_for("login"))


# Create playlists
party = util.song_recs(vibe="party", limit=50)
chill = util.song_recs(vibe="chill", limit=50)
sad = util.song_recs(vibe="sad", limit=50)


@app.route('/playlists', methods=['POST', 'GET'])
def playlists():

    # check if user is logged in
    if 'user' in session:
        user = session.get('user')
        user_img = session.get('user_img')
        access_token = session.get('access_token')

    else:
        return redirect(url_for("login"))

    # Get current user ID
    user_id = session.get('user_id')

    # Initialise playlist_id variable
    playlist_id = None

    # Create playlists
    playlists = {
        "party": party,
        "chill": chill,
        "sad": sad
    }
    if request.method == 'POST':

        # Time check
        expires_in = session.get('expires_in')
        if expired(time.time(), expires_in):
            access_token, expires_in = get_refresh_token(session['refresh_token'], app.config['CLIENT_ID'])
            session['access_token'] = access_token
            session['expires_in'] = time.time() + expires_in

        # Query DB
        selected_vibe = request.form['playlist_vibe']
        playlist = playlists[selected_vibe]

        # Create playlist
        createplaylist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
        playlist_name = selected_vibe.capitalize() + " " + datetime.now().strftime('%d.%m.%y %H:%M:%S')

        createplaylist_body = {"name": playlist_name,
                "public": "false"
        }
        playlist_id = api_call_post(access_token,createplaylist_url,createplaylist_body)['id']
        
        # Add songs to playlist
        addsongs_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        addsongs_body = {"uris": [],
                         "position": 0}
        for song in playlist:
            track_id = song[2]
            addsongs_body['uris'].append(f"spotify:track:{track_id}")

        api_call_post(access_token, addsongs_url, addsongs_body)

        return render_template("playlists.html", user=user, user_img=user_img, playlist_id=playlist_id, playlists=playlists)
    
    else:

        if playlist_id:
            return render_template("playlists.html", user=user, user_img=user_img, playlist_id=playlist_id, playlists=playlists)
        else:
            return render_template("playlists.html", user=user, user_img=user_img, playlists=playlists)


@app.route('/logout', methods=["POST","GET"])
def logout():
    if request.method == "POST":
        session.clear()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("playlists"))


if __name__ == "__main__":

    # refresh songs
    #token = get_token(os.getenv('CLIENT_ID'), os.getenv('CLIENT_SECRET'))
    #util.refresh_predictions_csv(token)
    #util.refresh_table()
    
    app.run(debug=True)