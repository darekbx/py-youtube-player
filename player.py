# Prerequisites:
# pip install --upgrade google-api-python-client
# pip install --upgrade google-auth-oauthlib google-auth-httplib2

import os
import os.path
import requests
import json

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "yt_python_client.json"
    refresh_token_file = "refresh_token.bin"

    credentials = None

    if not os.path.isfile(refresh_token_file):
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        with open(refresh_token_file, "w+") as handle:
            handle.write(credentials._refresh_token)
    else:
        with open(refresh_token_file) as handle:
            refresh_token = handle.read()

        with open(client_secrets_file) as handle:  
            data = json.load(handle)
        
        clientId = data['installed']['client_id']
        clientSecret = data['installed']['client_secret']
        access_token = refreshToken(clientId, clientSecret, refresh_token)
        credentials = google.oauth2.credentials.Credentials(access_token)

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
        
    request = youtube.search().list(
        part="snippet",
        maxResults=25,
        q="chopin"
    )
    response = request.execute()

    print(response)

def refreshToken(client_id, client_secret, refresh_token):
    params = {
        "grant_type": "refresh_token",
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token
    }
    authorization_url = "https://www.googleapis.com/oauth2/v4/token"
    r = requests.post(authorization_url, data=params)
    if r.ok:
        return r.json()['access_token']
    else:
        return None
            
if __name__ == "__main__":
    main()