from flask import Flask, redirect, jsonify, request, session
from datetime import datetime

import dotenv
import os

import pandas as pd
import urllib.parse
import requests

app = Flask(__name__)

FILE_PATH = os.path.dirname(os.path.abspath(__file__))

dotenv.load_dotenv()

app.secret_key = os.getenv('SECRET_KEY')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

REDIRECT_URI = "http://localhost:5000/callback"

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
API_BASE_URL = "https://api.spotify.com/v1"


if not os.path.exists(f'{FILE_PATH}/csv/'):
    os.makedirs(f'{FILE_PATH}/csv/')

CSV_PATH = f'{FILE_PATH}/csv'

@app.route('/')
def index():
    return "Welcome to Spotify playlist extractor, plz login first! <a href='/login'>login with spotify</a>"


@app.route('/login')
def login():
    scope = 'user-library-read playlist-read-private user-read-private user-read-email'

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error":request.args['error']})
    
    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info['access_token']
        session['refresh_token'] = token_info['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + token_info['expires_in']

        return redirect('/playlists')


@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    params = {
        'limit': 20,
        'offset': 0
    }

    response = requests.get(API_BASE_URL + '/me/playlists', headers=headers, params=params)
    playlists = response.json()

    playlist_items = []

    playlist_info_extract(playlist_items, playlist_items=playlists['items'])

    if playlists['next'] is not None:
        get_nextplaylists(next_playlists=playlists['next'], playlist_items=playlist_items)
    
    grabbed_playlists_to_csv(playlist_items)

    get_favorite_songs()

    extract_songs_from_playlists(playlists=playlist_items)

    return "all Done!"


def get_nextplaylists(next_playlists, playlist_items):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(next_playlists, headers=headers)
    playlists = response.json()

    playlist_info_extract(playlist_items, playlist_items=playlists['items'])

    if playlists['next'] is not None:
        get_nextplaylists(next_playlists=playlists['next'], playlist_items=playlist_items)

    return playlist_items

def playlist_info_extract(lists, playlist_items):
    for item in playlist_items:
        playlist_info = {
            'id': item['id'],
            'name': item['name'],
            'tracks_number': item['tracks']['total'],
            'type': item['type']
        }
        lists.append(playlist_info)

def grabbed_playlists_to_csv(playlists):
    playlist_df = pd.DataFrame(playlists)
    file_name = '/spotify_playlists.csv'
    playlist_df.to_csv(f'{CSV_PATH}{file_name}')


def get_favorite_songs():
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    params = {
        'market': 'TW',
        'limit': 50,
        'offset': 0
    }

    response = requests.get(API_BASE_URL + '/me/tracks', headers=headers, params=params)
    favorite_tracks_partial = response.json()

    favorite_tracks = []

    song_info_extract(lists=favorite_tracks, tracks_items=favorite_tracks_partial['items'])

    if favorite_tracks_partial['next'] is not None:
        get_next_favortie_songs(next_songs_uri=favorite_tracks_partial['next'], favorite_tracks=favorite_tracks)

    tracks_to_csv(tracks=favorite_tracks, name='Favorite_Tracks')

    return "favorite_tracks extracted"


def get_next_favortie_songs(next_songs_uri, favorite_tracks):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(next_songs_uri, headers=headers)
    favorite_tracks_partial = response.json()

    song_info_extract(favorite_tracks, favorite_tracks_partial['items'])

    if favorite_tracks_partial['next'] is not None:
        get_next_favortie_songs(next_songs_uri=favorite_tracks_partial['next'], favorite_tracks=favorite_tracks)

def song_info_extract(lists, tracks_items):
    for song_info in tracks_items:
        track_dict = {
            'album_type': song_info['track']['album']['album_type'],
            'album_name': song_info['track']['album']['name'],
            'artists_name': song_info['track']['artists'][0]['name'],
            'artists_type': song_info['track']['artists'][0]['type'],
            'disc_number': song_info['track']['disc_number'],
            'durations_ms': song_info['track']['duration_ms'],
            'track_name': song_info['track']['name'],
            'track_number': song_info['track']['track_number'],
            'uri': song_info['track']['uri']
        }
        lists.append(track_dict)

def tracks_to_csv(tracks, name):
    tracks = pd.DataFrame(tracks)
    try:
        file_name = f'/{name}.csv'
        tracks.to_csv(f'{CSV_PATH}{file_name}')
    except OSError:
        file_name = f"/{''.join(e for e in name if e.isalnum())}.csv"
        tracks.to_csv(f'{CSV_PATH}{file_name}')
        


def extract_songs_from_playlists(playlists):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    for playlist in playlists:
        ID = playlist['id']
        LIST_NAME = playlist['name']
        params = {
            'market': 'TW',
            'feilds': 'next, items(track(name,album(name,album_type),artists(name,type),disc_number,track_number,duration_ms,type))',
            'limit': 50
        }
        response = requests.get(API_BASE_URL + f'/playlists/{ID}/tracks', headers=headers, params=params)
        songs = response.json()

        lists = []

        song_info_extract(lists, songs['items'])

        if songs['next'] is not None:
            get_next_songs(next_songs_uri=songs['next'], lists=lists)
        
        tracks_to_csv(tracks=lists, name=LIST_NAME)

    return "songs_extracted_from_playlists"
        

def get_next_songs(next_songs_uri, lists):
    if 'access_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')
    
    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }

    response = requests.get(next_songs_uri, headers=headers)
    songs = response.json()

    song_info_extract(lists, songs['items'])

    if songs['next'] is not None:
        get_next_songs(next_songs_uri=songs['next'], lists=lists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    
    if datetime.now().timestamp() > session['expire_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info['access_token']
        session['expires_at'] = datetime.now().timestamp() + new_token_info['expires_in']

        return redirect('/playlists')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)