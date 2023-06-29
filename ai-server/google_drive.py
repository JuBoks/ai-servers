import os.path

from fastapi import UploadFile
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from datetime import datetime
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata', 
          'https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/drive']

def connect_to_google_drive():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = Credentials.from_service_account_file('service-account.json')

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')

async def upload_photo(service, path, googleFileName, folder_id):
    try:
        # Upload a file to google drive
        file_metadata = {'name': googleFileName, 'parents': [folder_id], 'uploadType': 'multipart'}
        media = MediaFileUpload(path, mimetype='image/png')
        file = service.files().create(body=file_metadata, media_body=media, fields='id,webViewLink').execute()
        # 구글드라이브 링크 얻기
        # webviewlink = file.get('webViewLink')
        return True
    except:
        return False