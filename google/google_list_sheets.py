from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

def create_services():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    drive_service = build('drive', 'v3', credentials=creds)
    sheets_service = build('sheets', 'v4', credentials=creds)
    return drive_service, sheets_service

class GoogleSheetsManager:
    def __init__(self):
        self.drive_service, self.sheets_service = create_services()
        
    def list_sheets(self):
        try:
            results = self.drive_service.files().list(
                q="mimeType='application/vnd.google-apps.spreadsheet'",
                fields="nextPageToken, files(id, name)"
            ).execute()
            return results.get('files', [])
        except HttpError as err:
            print(f"Error: {err}")
            return []

    def get_sheet_url(self, file_id):
        return f"https://docs.google.com/spreadsheets/d/{file_id}/edit"

    def delete_sheet(self, file_id):
        try:
            self.drive_service.files().delete(fileId=file_id).execute()
            return True
        except HttpError as err:
            print(f"Error: {err}")
            return False
        
    def get_sheet_data(self, file_id, range_name='Sheet1'):
        try:
            result = self.sheets_service.spreadsheets().values().get(spreadsheetId=file_id, range=range_name).execute()
            values = result.get('values', [])
            return values
        except HttpError as err:
            print(f"Error: {err}")
            return []
        
    def get_sheet_name(self, file_id):
        try:
            file = self.drive_service.files().get(fileId=file_id, fields='name').execute()
            return file.get('name', 'Unknown')
        except HttpError as err:
            print(f"Error: {err}")
            return 'Unknown'
