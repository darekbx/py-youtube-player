#!usr/bin/env python

# Prerequisites:
# python3 -m pip install google-api-python-client
# python3 -m pip install google-auth-oauthlib google-auth-httplib2
# python3 -m pip install google-oauth
# python3 -m pip install colorama

import os
import os.path
import requests
import json
from colorama import init
from colorama import Fore, Back, Style

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

class YoutubeTerminal:

    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    authorization_url = "https://www.googleapis.com/oauth2/v4/token"
    client_secrets_file = "yt_python_client.json"
    refresh_token_file = "refresh_token.bin"
    youtube = None

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
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, self.scopes)
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

    def authorize(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"

        credentials = self.request_credentials()
        self.youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

    def search(self, keyword, limit=25):
        request = self.youtube.search().list(
            part="snippet",
            maxResults=limit,
            type="video",
            q=keyword
        )
        return request.execute()
    
    def displaySerachResults(self, result):
        for index, result in enumerate(result['items']):
            snippet = result['snippet']
            title = snippet['title']
            channelTitle = snippet['channelTitle']

            print(Fore.GREEN + "{0}. {1}".format(index + 1, title))
            print(Style.DIM + "   {0}".format(channelTitle))
            print(Style.RESET_ALL)

terminal = YoutubeTerminal()
terminal.authorize()
result = terminal.search("chopin", 5)
terminal.displaySerachResults(result)