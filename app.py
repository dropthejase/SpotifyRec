from flask import Flask, render_template, request, flash
import time
import util

app = Flask(__name__)
app.secret_key = 'ajweffas'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/track_id', methods=['POST'])
def predict():
    track_id = request.form['track_id_input']
    prediction = util.predict_vibe(track_id)
    flash("Result: " + prediction)
    return render_template("index.html", track_id=track_id, prediction=prediction)

if __name__ == "__main__":
    app.run(debug=True)