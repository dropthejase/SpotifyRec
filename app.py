from flask import Flask, flash, make_response, render_template, request, session, redirect, url_for
import util

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        # store user name in session
        user = request.form['user']
        session['user'] = user

        # redirect to Spotify login
        get_auth_code = util.get_auth_code()
        app.config['CODE_VERIFIER'] = get_auth_code[1]
        response = make_response(redirect(get_auth_code[0]))
        return response
    else:
        return render_template("index.html")

@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    code_verifier = app.config.get('CODE_VERIFIER')

    print("SESSION: ", session)
    user = session.get('user')

    access_token, refresh_token = util.get_token_pkce(auth_code, code_verifier)
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    return render_template('track_id.html', user=user)

@app.route('/track_id', methods=['POST', 'GET'])
def track_id():
    if request.method == 'POST':
        if 'user' in session:
            user = session.get('user')
            access_token = session.get('access_token')
            track_id = request.form['track_id_input']

            if track_id == "":
                flash("Please enter a track ID into the box above")
                return render_template("track_id.html", user=user)
            
            else:
                prediction = util.predict_vibe(access_token, track_id)
                flash("Result: " + prediction)
                return render_template("track_id.html", user=user, track_id=track_id, prediction=prediction)
        
        else:
            return redirect(url_for("login"))
    else:
        if 'user' in session:
            user = session.get('user')
            return render_template('track_id.html', user=user)
        else:
            return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)