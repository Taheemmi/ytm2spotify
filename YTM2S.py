import os
import json
import csv
import requests
import time
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# YouTube API setup
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def youtube_authenticate():
    creds = None
    token_file = 'token.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES) # Insert your google youtube api json here and make sure it is in the same folder as this script.
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return build('youtube', 'v3', credentials=creds)

def get_youtube_playlists(youtube):
    request = youtube.playlists().list(
        part="snippet,contentDetails",
        mine=True
    )
    response = request.execute()
    return response.get('items', [])

def get_playlist_items(youtube, playlist_id):
    playlist_items = []
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=50,  # Fetch 50 items per request
        playlistId=playlist_id
    )
    
    while request:
        response = request.execute()
        playlist_items.extend(response.get('items', []))
        request = youtube.playlistItems().list_next(request, response)
    return playlist_items


def clean_artist_name(artist_name):
    if " - Topic" in artist_name:
        return artist_name.replace(" - Topic", "").strip()
    return artist_name


# Spotify API setup
SPOTIPY_CLIENT_ID = 'INSERT_CLIENT_ID'
SPOTIPY_CLIENT_SECRET = 'INSERT_CLIENT_SECRET'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback' # This is a default redirect

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="playlist-modify-public"))

def search_spotify_track(sp, track_name, artist_name):
    query = f'track:{track_name} artist:{artist_name}'
    results = sp.search(q=query, type='track', limit=1)
    tracks = results.get('tracks', {}).get('items', [])
    if tracks:
        return tracks[0]['id']
    return None

def add_tracks_to_spotify_playlist(sp, playlist_id, track_ids, batch_size=100):
    for i in range(0, len(track_ids), batch_size):
        # Process a batch of track IDs
        batch = track_ids[i:i + batch_size]
        try:
            sp.playlist_add_items(playlist_id, batch)
            print(f"Added batch {i//batch_size + 1} of {len(track_ids)//batch_size + 1}")
            time.sleep(1)  # Short delay to avoid hitting rate limits
        except spotipy.exceptions.SpotifyException as e:
            print(f"Spotify API error: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

def create_spotify_playlist(sp, playlist_name):
    playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name)
    return playlist['id']

def add_tracks_to_spotify_playlist(sp, playlist_id, track_ids):
    sp.playlist_add_items(playlist_id, track_ids)

def export_to_csv(data, filename='youtube_to_spotify.csv'):
    # Define the headers based on the keys in the dictionary
    headers = ["Playlist", "Track Name", "Artist", "Spotify Track ID"]

    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        # Write the headers
        writer.writeheader()
        
        # Write the data rows
        writer.writerows(data)

def main():
    # Authenticate with YouTube
    youtube = youtube_authenticate()

    # Authenticate with Spotify
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id="your_spotify_client_id",
        client_secret="your_spotify_client_secret",
        redirect_uri="your_redirect_uri",
        scope="playlist-modify-public"
    ))

    # Get all YouTube playlists
    playlists = get_youtube_playlists(youtube)
    all_tracks_data = []

    # Only process the "Spotify" playlist
    target_playlist_name = "spotify"
    target_playlist = None

    # Find the "Spotify" playlist in the YouTube playlists
    for playlist in playlists:
        if playlist['snippet']['title'].lower() == target_playlist_name.lower():
            target_playlist = playlist
            break

    if not target_playlist:
        print(f"Playlist '{target_playlist_name}' not found.")
        return

    playlist_name = target_playlist['snippet']['title']
    print(f"Processing playlist: {playlist_name}")

    # Create or find the corresponding Spotify playlist
    playlist_id = create_spotify_playlist(sp, playlist_name)

    # Get items from the target YouTube playlist
    playlist_items = get_playlist_items(youtube, target_playlist['id'])
    print(f"Total tracks in playlist '{playlist_name}': {len(playlist_items)}")

    # Process tracks
    track_ids = []
    for item in playlist_items:
        track_title = item['snippet']['title']
        raw_artist_name = item['snippet']['videoOwnerChannelTitle']
        artist_name = clean_artist_name(raw_artist_name)
        print(f"Searching for track: {track_title} by {artist_name}")

        # Search for the track on Spotify
        spotify_track_id = search_spotify_track(sp, track_title, artist_name)
        if spotify_track_id:
            print(f"Found track on Spotify: {spotify_track_id}")
            track_ids.append(spotify_track_id)
            all_tracks_data.append({
                'Playlist': playlist_name,
                'Track Name': track_title,
                'Artist': artist_name,
                'Spotify Track ID': spotify_track_id
            })
        else:
            print(f"Track not found on Spotify: {track_title} by {artist_name}")

    print(f"Tracks found for playlist '{playlist_name}': {len(track_ids)}")

    # Add tracks in batches to the Spotify playlist
    if track_ids:
        try:
            add_tracks_to_spotify_playlist(sp, playlist_id, track_ids)
            print(f"Added {len(track_ids)} tracks to playlist '{playlist_name}' on Spotify.")
        except Exception as e:
            print(f"Error adding tracks to Spotify playlist: {e}")
    else:
        print(f"No valid tracks found to add to playlist: {playlist_name}")

    # Export the track data to a CSV file
    export_to_csv(all_tracks_data)
    print("Transfer complete! Playlist data saved to youtube_to_spotify.csv")

if __name__ == "__main__":
    main()
