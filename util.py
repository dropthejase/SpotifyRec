import hashlib, string, secrets
from requests import get, post, Request
import base64
from api_util import get_audio_features
import numpy as np
import pickle

def generate_randomstring(n):
    """
    Generates random string
    Arguments:
        n: length of string
    Returns:
        A randomly generated string
    """
    alphabet = string.ascii_letters + string.digits
    code_verifier = ''.join(secrets.choice(alphabet) for i in range(n))
    return code_verifier

def generate_code_challenge(code_verifier):
    """
    Transforms code verifier using SHA256 algorithm, creating digest
    Then the digest is encoded into base64
    Arguments:
        code_verifier: the code verifier
    Returns:
        Base64 encoding of digest - serves as the code challenge
    """
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.replace('=', '')

    return code_challenge

def get_auth_code():
    """
    Creates an authorisation code to send for an access token.
    Returns:
        Authorisation code
    """
    url = "https://accounts.spotify.com/authorize?"
    scope = "playlist-modify-public"
    redirect_uri = "http://localhost:5000/callback"
    state = generate_randomstring(16)
    code_verifier = generate_randomstring(128)
    code_challenge = generate_code_challenge(code_verifier)

    params = {
        "response_type": "code",
        "client_id": "af2795e2f63545f3883b5ab47e29187a",
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge
        }

    request = Request('GET', url, params=params)
    request = request.prepare()
    
    return request.url, code_verifier

def get_token_pkce(auth_code, code_verifier):

    url = "https://accounts.spotify.com/api/token"
    redirect_uri = "http://localhost:5000/callback"

    headers = {
        "Content_Type" : "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type" : "authorization_code",
        "code" : auth_code,
        "client_id" : "af2795e2f63545f3883b5ab47e29187a",
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier}
    
    request = Request('POST', url, headers=headers, data=data)
    request = request.prepare()

    result = post(url, headers=headers, data=data)
    print("Result: ", result.content)
    json_result = result.json()
    access_token = json_result["access_token"]
    refresh_token = json_result["refresh_token"]

    return access_token, refresh_token

def prepare_prediction(token, track_id):
    """
    Gets audio features, given an access token and track ID
    and returns and prepared Numpy array
    Arguments:
        token: access token
        track_id: Track ID
    Returns:
        Prepared Numpy array of shape (1, 10) to pass into model
    """

    audio_features = get_audio_features(token, track_id)
    X = np.zeros((1,10))

    try:
        X[:,0] = audio_features['acousticness']
        X[:,1] = audio_features['danceability']
        X[:,2] = audio_features['duration_ms']
        X[:,3] = audio_features['energy']
        X[:,4] = audio_features['instrumentalness']
        X[:,5] = audio_features['liveness']
        X[:,6] = audio_features['loudness']
        X[:,7] = audio_features['speechiness']
        X[:,8] = audio_features['tempo']
        X[:,9] = audio_features['valence']

        return X
    
    except:
        raise Exception
    
def predict_vibe(access_token, track_id):

    # prepare data
    while True:
        try:
            X = prepare_prediction(access_token, track_id)
            break
        except:
            return "Something went wrong - please check your track ID and try again."

    # make prediction
    PREDICTION_LIST = ['party', 'chill', 'sad']
    MODEL = pickle.load(open('pipe_rf.pkl','rb'))
    
    pY = MODEL.predict(X)

    if pY == 1:
        response = PREDICTION_LIST[0]
    elif pY == 2:
        response = PREDICTION_LIST[1]
    else:
        response = PREDICTION_LIST[2]
        
    return response