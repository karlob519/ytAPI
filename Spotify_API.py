# Import necessary libraries
import base64
import requests
import json
import os
from dotenv import load_dotenv
from openpyxl import Workbook

# Load environment variables from .env file
load_dotenv()
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')

# Function to get authentication token from Spotify API
def get_token():
    auth_string = client_id + ':' + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'ContentType': 'application/x-www-form-urlencoded' 
    }
    data = {'grant_type': 'client_credentials'}
    result = requests.post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result['access_token']

    return token

# Get the authentication token
access_token = get_token()

# Specify your Spotify username and API endpoint URL
spotify_username = 'your_spotify_username'
spotify_url = f'https://api.spotify.com/v1/users/{spotify_username}/playlists'

# Function to create the authorization header
def get_auth_header(token):
    return {'Authorization': f'Bearer {token}'}

# Function to search for a track on Spotify
def search_for_track(track_name, token=access_token):
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={track_name}&type=track&limit=3'
    query_url = url + query

    result = requests.get(query_url, headers=headers)
    json_result = json.loads(result.content)
    
    return json_result

# Function to get the Spotify URI link of a track
def get_uri_link(track_name):
    json_track = search_for_track(track_name)
    return json_track['tracks']['items'][0]['uri']

# Load playlist data from a JSON file
file_name = 'your_file_name.json'
with open(file_name) as f:
    playlists = json.load(f)

# Extract playlist names
playlist_names = list(playlists.keys())

# Create an Excel workbook
wb = Workbook()

# Iterate through each playlist and its songs
for name in playlist_names:
    ws = wb.create_sheet(name)
    ws.title = name
    ws.append(['Name', 'Artist', 'Link'])
    tracks = []
    songs = playlists[name]
    
    # For each song in the playlist, retrieve its title, artist, and Spotify URI
    for song in songs:
        title = song.get('song_title')
        artist = song.get('song_artist')
        search_str = f'{title} {artist}'
        uri = get_uri_link(search_str)
        track = [title, artist, uri]
        if title is not None:
            tracks.append(track)

    # Write the track details to the Excel sheet
    for track in tracks:
        ws.append(track)

# Specify the Excel file name and save the workbook
excel_file_name = 'your_excel_file_name.xlsx'
wb.save(excel_file_name)

# Print a completion message
print('Done!!')





