YouTube Music to Spotify Transfer
This method works better than Tune My Music and runs locally.

How to Use:
**1. Create a Playlist on YouTube Music:**

 * Create a playlist named "spotify" on YouTube Music and add up to 100 songs.

**2. Set Up Google Cloud Project:**

 * Go to [Google Cloud Console](https://console.cloud.google.com// "Google Cloud Console") and create a new project (you can name it anything).
 * Navigate to APIs & Services -> Library -> search for YouTube Data API v3 -> enable it.
 * Go to Credentials -> Create Credentials -> select OAuth Client ID (set the application type to Desktop Application) -> name it.
 * Download the JSON file and keep it safe.

**3. Set Up Spotify Developer Account:**

 * Go to [Spotify Developer Console](https://developer.spotify.com/dashboard// "Spotify Developer Console")
 * Create an App and name it (ensure the redirect URI matches the one in your script, e.g., 'http://localhost:8888/callback').
 * In the app's Settings, obtain the Client ID and Client Secret.

**4. Prepare the Script:**

 * Place the secret.json file (from Google) in the same directory as the script.
 * Enter the Client ID and Client Secret from Spotify into the script.

**5. Run the Script:**

 * Execute the script to transfer the playlist from YouTube Music to Spotify.

Note: The Spotify API has a limit of 100 songs per playlist. To transfer more than 100 songs, you would need to apply for an extension or modify the script to handle multiple playlists.
