from flask import Flask, flash, make_response, render_template, request, session, redirect, url_for
from datetime import timedelta
from api_util import api_call
import re
import requests
import util

app = Flask(__name__)
app.config['SECRET_KEY'] = util.generate_randomstring(16).encode('utf-8')
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route('/')
def index():
    print("SESSION 0: ", session)
    if 'user' in session:
        return redirect(url_for("track_id"))
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

    access_token, refresh_token = util.get_token_pkce(auth_code, code_verifier)
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    # get user's name and store in a session
    user = api_call(access_token, "https://api.spotify.com/v1/me")["display_name"]
    user_img = api_call(access_token, "https://api.spotify.com/v1/me")['images'][0]["url"]
    user_id = api_call(access_token, "https://api.spotify.com/v1/me")["id"]

    session.permanent = True
    session['user'] = user
    session['user_img'] = user_img
    session['user_id'] = user_id

    return redirect(url_for("track_id"))

@app.route('/track_id', methods=['POST', 'GET'])
def track_id():
    if request.method == 'POST':
        if 'user' in session:
            user = session.get('user')
            user_img = session.get('user_img')
            access_token = session.get('access_token')
            track_id = request.form['track_id_input']

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

@app.route('/playlists', methods=['POST', 'GET'])
def playlists():

    # check if user is logged in
    if 'user' in session:
        user = session.get('user')
        user_img = session.get('user_img')
        user_id = session.get('user_id')
    else:
        return redirect(url_for("login"))

    if request.method == 'POST':
        ### TO DO create the playlist ###
        return render_template("playlists.html", user=user, user_img=user_img)
    else:
        return render_template('playlists.html', user=user, user_img=user_img)


@app.route('/logout', methods=["POST","GET"])
def logout():
    if request.method == "POST":
        session.clear()
        return redirect(url_for("index"))
    else:
        return redirect(url_for("track_id"))

if __name__ == "__main__":
    app.run(debug=True)