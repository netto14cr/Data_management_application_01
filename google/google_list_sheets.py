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
        
    def get_record_data(self, spreadsheet_id, record_id, range_name='Sheet1'):
        """
        Obtiene los datos de una fila específica (registro) en una hoja de Google Sheets.

        :param spreadsheet_id: El ID de la hoja de cálculo.
        :param record_id: El nombre o índice del registro que deseas obtener.
        :param range_name: El nombre del rango, por defecto 'Sheet1'.
        :return: Los datos de la fila especificada como una lista.
        """
        try:
            # Obtener todos los datos de la hoja
            result = self.sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])

            # Buscar la fila cuyo primer valor coincida con record_id
            for row in values:
                if row[0] == record_id:
                    return row

            print(f"Error: El registro con ID '{record_id}' no fue encontrado.")
            return []
        except HttpError as err:
            print(f"Error: {err}")
            return []
        
    def update_record(self, spreadsheet_id, record_id, updated_data, range_name='Sheet1'):
        try:
            # Obtener todos los datos de la hoja
            result = self.sheets_service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
    
            # Buscar la fila cuyo primer valor coincida con record_id
            for i, row in enumerate(values):
                if row[0] == record_id:
                    # Define el rango de celdas para actualizar (asumiendo que se actualizan todas las columnas)
                    num_columns = len(updated_data)
                    range_to_update = f"{range_name}!A{i+1}:{chr(65 + num_columns - 1)}{i+1}"
                    body = {
                        'values': [updated_data]
                    }
                    self.sheets_service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=range_to_update,
                        valueInputOption='RAW',
                        body=body
                    ).execute()
                    return True
    
            print(f"Error: El registro con ID '{record_id}' no fue encontrado.")
            return False
        except HttpError as err:
            print(f"Error: {err}")
            return False
    
    



