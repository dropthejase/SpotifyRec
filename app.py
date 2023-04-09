from flask import Flask, flash, make_response, render_template, request, session, redirect, url_for
import util

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
# immediate authentication
def index():
    request = util.get_auth_code()
    app.config['CODE_VERIFIER'] = request[1]
    print("STORED CODE VERIFIER: ", app.config.get('CODE_VERIFIER'))
    response = make_response(redirect(request[0]))
    return response

@app.route('/callback')
def callback():
    auth_code = request.args.get('code')
    code_verifier = app.config.get('CODE_VERIFIER')
    print("RETRIEVED CODE VERIFIER: ", app.config.get('CODE_VERIFIER'))

    access_token, refresh_token = util.get_token_pkce(auth_code, code_verifier)
    session['access_token'] = access_token
    session['refresh_token'] = refresh_token

    return render_template('index.html')

@app.route('/track_id', methods=['POST'])
def predict():
    access_token = session.get('access_token')
    track_id = request.form['track_id_input']
    prediction = util.predict_vibe(access_token, track_id)
    flash("Result: " + prediction)
    return render_template("index.html", track_id=track_id, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)