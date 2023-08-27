# Import necessary libraries
import json
import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv('API_KEY')

# Create a dictionary to store playlist information
playlist_dict = dict()

# List of unwanted keywords in video titles
unwanted_list = ['(Official Music Video)', 'official music video', 'OFFICIAL MUSIC VIDEO', 
                '(Official Video)', '(Music Video)', '(Lyric Video)', 'With Lyrics', 'with lyrics',
                'official', 'OFFICIAL', ' ( video)', '( VIDEO)', 'VIDEO', '(  VIDEO)', '( acoustic)',
                'Official', '(Live)', 'Lyrics', 'LYRICS', 'lyrics', 'Live', 'live', 'LIVE', '()']

# Build the YouTube API client using the provided API key
youtube = build('youtube', 'v3', developerKey=api_key)

# Specify the YouTube username
username = 'your_username'

# Retrieve channel information including content details, statistics, and snippet
channel_request = youtube.channels().list(part='contentDetails, statistics, snippet',
                                  forUsername=username)
channel_response = channel_request.execute()
channel_id = channel_response['items'][0]['id']

# Retrieve playlists associated with the specified channel
playlist_request = youtube.playlists().list(part='contentDetails, snippet',
                                  channelId=channel_id)
playlist_response = playlist_request.execute()

# Extract playlist IDs and names
playlist_ids = []
for item in playlist_response['items']:
    playlist_name = item['snippet']['title']
    playlist_ids.append((item['id'], playlist_name))
    playlist_dict[playlist_name] = []

# Function to retrieve video IDs from a playlist
def vid_ids(playlist_id):
    request = youtube.playlistItems().list(part='contentDetails',
                                  playlistId=playlist_id, maxResults=50)
    response = request.execute()
    id_list = [video['contentDetails']['videoId'] for video in response['items']]
    id_str = ','.join(id_list)
    return id_str

# Function to retrieve video titles from video IDs
def get_vid_titles(vid_str):
    request = youtube.videos().list(part='snippet',
                                    id=vid_str)
    response = request.execute()
    titles = [video['snippet']['title'] for video in response['items']]
    return titles

# Function to format video title and separate artist from song title
def format_title(title: str, bad_list: list):
    work_string = title
    for string in bad_list:
        if string in work_string:
            work_string = work_string.replace(string, '')
    work_list = work_string.split('-')
    output_dict = dict()
    try:
        output_dict['song_title'] = work_list[1]
        output_dict['song_artist'] = work_list[0]
    except IndexError:
        output_dict = {'None': 0}
    return output_dict

# Populate the playlist dictionary with formatted video titles
for playlist in playlist_ids:
    id_str, playlist_name = playlist
    vids = vid_ids(id_str)
    titles = get_vid_titles(vids)
    formatted_titles = [format_title(title, unwanted_list) for title in titles]
    playlist_dict[playlist_name] = formatted_titles

# Convert the playlist dictionary to a JSON object with proper indentation
json_object = json.dumps(playlist_dict, indent=2)

# Specify the output file name
file_name = 'your_file_name.json'

# Write the JSON object to the specified output file
with open(file_name, "w") as outfile:
    outfile.write(json_object)

