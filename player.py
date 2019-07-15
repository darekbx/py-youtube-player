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

class YoutubeTerminal:

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    authorization_url = "https://www.googleapis.com/oauth2/v4/token"
    client_secrets_file = "yt_python_client.json"
    refresh_token_file = "refresh_token.bin"

    def refresh_token(self, client_id, client_secret, refresh_token):
        params = {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token
        }
        response = requests.post(self.authorization_url, data=params)
        if response.ok:
            return response.json()['access_token']
        else:
            return None

    def save_refresh_token(self, refresh_token):
        with open(self.refresh_token_file, "w+") as handle:
            handle.write(refresh_token)

    def read_refresh_token(self):
        with open(self.refresh_token_file) as handle:
            return handle.read()

    def read_auth_configuration(self):
        with open(self.client_secrets_file) as handle:  
            return json.load(handle)

    def request_credentials(self):
        if not os.path.isfile(self.refresh_token_file):
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, self.scopes)
            credentials = flow.run_console()
            self.save_refresh_token(credentials._refresh_token)
            return credentials
        else:
            refresh_token = self.read_refresh_token() 
            auth_configuration = self.read_auth_configuration()
            clientId = auth_configuration['installed']['client_id']
            clientSecret = auth_configuration['installed']['client_secret']
            access_token = self.refresh_token(clientId, clientSecret, refresh_token)
            return google.oauth2.credentials.Credentials(access_token)

    def search(self, keyword, limit=25):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        credentials = self.request_credentials()
        youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)
            
        request = youtube.search().list(
            part="snippet",
            maxResults=limit,
            q=keyword
        )
        response = request.execute()

        print(response)


terminal = YoutubeTerminal()
terminal.search("chopin", 5)