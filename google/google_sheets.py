from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def create_service():
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=credentials)
        return service
    except HttpError as err:
        print(f"Error: {err}")
        return None

def create_spreadsheet(title):
    service = create_service()
    if not service:
        return None

    try:
        spreadsheet = {
            'properties': {
                'title': title
            }
        }

        spreadsheet = service.spreadsheets().create(
            body=spreadsheet,
            fields='spreadsheetId'
        ).execute()

        spreadsheet_id = spreadsheet.get('spreadsheetId')
        print(f'Spreadsheet created with ID: {spreadsheet_id}')
        return spreadsheet_id

    except HttpError as err:
        print(f"Error: {err}")
        return None

def save_to_sheets(spreadsheet_id, data):
    service = create_service()
    if not service:
        return None

    try:
        headers = ['Name', 'Email', 'Age', 'Phone', 'Address']
        values = [headers] + [data]  # Note: data should be a list of lists

        body = {
            'values': values
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range='Sheet1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"{result.get('updatedCells')} cells updated.")
        return spreadsheet_id
    except HttpError as err:
        print(f"Error: {err}")
        return None

