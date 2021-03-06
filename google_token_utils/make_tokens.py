import base64
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json

Message = dict

drive_scopes = ["https://www.googleapis.com/auth/drive.metadata.readonly", "https://www.googleapis.com/auth/drive"]
gmail_scopes = ['https://www.googleapis.com/auth/gmail.send']

# If modifying these scopes, delete the file token.pickle.
SCOPES = drive_scopes
FILENAME = 'credentials.json'


# using the default file credentials.json it will provide a refresh_token

def main():
    flow = InstalledAppFlow.from_client_secrets_file(
                FILENAME, SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    print('client id :', creds.client_id)
    print('client secret :', creds.client_secret)
    print('refresh token :', creds.refresh_token)
    with open('auth.json', 'w') as f:
        f.write(creds.to_json())

if __name__ == '__main__':
    main()
