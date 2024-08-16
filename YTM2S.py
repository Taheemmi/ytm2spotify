import os 
import pickle 
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def youtube_authenticate():
    creds = None
    # check if token.pickle file exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # if no credentials available, prompt user to log in
    if not creds or not creds.valid:
        if creds and creds