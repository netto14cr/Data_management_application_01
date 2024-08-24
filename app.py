import os
import time
import webbrowser
import threading
import webview
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io


import time
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import webbrowser
import threading
import webview
from threading import Timer
from google.google_sheets import save_to_sheets, create_spreadsheet
from models.excel_handler import ExcelHandler
from models.connection import MySQLDatabase
from models.data_entry import DataEntry
from datetime import datetime
from google.google_list_sheets import GoogleSheetsManager
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account

import os
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize the Google Sheets Manager
sheets_manager = GoogleSheetsManager()

@app.route('/')
def index():
    return render_template('main/index.html')

@app.route('/manage_sheets')
def manage_sheets():
    sheets = sheets_manager.list_sheets()
    return render_template('sheets/manage_sheets.html', sheets=sheets)

@app.route('/view_sheet_data/<file_id>')
def view_sheet_data(file_id):
    # Obtener los datos desde el sheet
    sheets_manager = GoogleSheetsManager()
    data = sheets_manager.get_sheet_data(file_id)
    
    # Obtener el nombre del sheet
    sheet_name = sheets_manager.get_sheet_name(file_id)
    
    # Renderizar el template con los datos y el ID de la hoja
    return render_template('sheets/view_sheet_data.html', 
                           data=data, 
                           sheet_name=sheet_name, 
                           spreadsheet_id=file_id, 
                           zip=zip)

@app.route('/download_sheet/<file_id>')
def download_sheet(file_id):
    # Load environment variables
    load_dotenv()
    SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Get the file from Google Drive
        request = service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            if status:
                print(f"Download {int(status.progress() * 100)}%.")

        fh.seek(0)
        return send_file(fh, as_attachment=True, download_name=f'{file_id}.xlsx')

    except Exception as err:
        print(f"Error: {err}")
        flash('Unable to download the sheet', 'danger')
        return redirect(url_for('manage_sheets'))

@app.route('/delete_sheet/<file_id>', methods=['POST'])
def delete_sheet(file_id):
    if sheets_manager.delete_sheet(file_id):
        flash('Sheet deleted successfully!', 'success')
    else:
        flash('Failed to delete sheet.', 'danger')
    return redirect(url_for('manage_sheets'))



@app.route('/edit_sheet_data/<spreadsheet_id>/<record_id>', methods=['GET', 'POST'])
def edit_sheet_data(spreadsheet_id, record_id):
    sheets_manager = GoogleSheetsManager()

    if request.method == 'POST':
        # Recibir datos del formulario
        updated_data = [
            request.form['Name'],
            request.form['Email'],
            request.form['Age'],
            request.form['Phone'],
            request.form['Address']
        ]
        success = sheets_manager.update_record(spreadsheet_id, record_id, updated_data)
        if success:
            return redirect(url_for('view_sheet_data', file_id=spreadsheet_id))
        else:
            return "Error updating record", 500

    # Para la solicitud GET, cargar los datos existentes
    data = sheets_manager.get_record_data(spreadsheet_id, record_id)
    if data:
        # Los datos deben ser un diccionario en lugar de una lista de tuplas
        headers = ['Name', 'Email', 'Age', 'Phone', 'Address']
        # Combina encabezados con datos en un diccionario para la plantilla
        data_dict = dict(zip(headers, data))
        return render_template('sheets/edit_sheet_data.html', data=data_dict, record_id=record_id, spreadsheet_id=spreadsheet_id)
    else:
        return "Record not found", 404





@app.route('/update_sheet_data/<record_id>', methods=['POST'])
def update_sheet_data(record_id):
    # Obtener los datos del formulario
    updated_data = {
        'name': request.form['name'],
        'email': request.form['email'],
        'age': request.form['age'],
        'phone': request.form['phone'],
        'address': request.form['address']
    }
    
    # Actualizar los datos en la hoja
    sheets_manager.update_record_data(record_id, updated_data)
    
    return redirect(url_for('view_sheet_data', file_id=record_id))



@app.route('/data_entry', methods=['GET', 'POST'])
def data_entry():
    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age']) if request.form['age'].isdigit() else None
        email = request.form['email']
        phone = request.form.get('phone')
        address = request.form.get('address')

        entry = DataEntry(name, age, email, phone, address)

        if entry.is_valid():
            # Save data to Excel
            excel_handler = ExcelHandler()  # Create an instance of the ExcelHandler class
            excel_handler.save_data([entry.name, entry.age, entry.email, entry.phone, entry.address])

            flash('Data submitted and saved to Excel successfully!', 'success')
        else:
            flash('Invalid data. Please check your inputs.', 'danger')

        return redirect(url_for('data_entry'))
    
    return render_template('form/data_entry.html')

@app.route('/data_entry_sheets', methods=['GET', 'POST'])
def data_entry_sheets():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        phone = request.form.get('phone')
        address = request.form.get('address')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        sheet_title = f'user_data_{timestamp}'

        # Create a new Google Sheets document
        spreadsheet_id = create_spreadsheet(sheet_title)

        if spreadsheet_id:
            # Save data to the created Google Sheets document
            save_to_sheets(spreadsheet_id, [name, email, age, phone, address])
            flash(f'Data submitted and saved to Google Sheets with ID: {spreadsheet_id}', 'success')
        else:
            flash('Failed to create Google Sheets document.', 'danger')

        return redirect(url_for('data_entry_sheets'))
    
    return render_template('form/data_entry_sheets.html')

@app.route('/data_entry_mysql', methods=['GET', 'POST'])
def data_entry_mysql():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        db = MySQLDatabase()
        db.insert_data(name, email, age, phone, address)
        
        flash('Data submitted and saved to MySQL successfully!', 'success')
        return redirect(url_for('data_entry_mysql'))
    
    return render_template('form/data_entry_mysql.html')


@app.route('/cloud_data', endpoint='cloud_data')
def cloud_data():
    db = MySQLDatabase()
    all_data = db.get_all_data()
    if not all_data:
        return render_template('main/error_500.html', message="No data available or database error.")
    return render_template('cloud/cloud_data.html', data=all_data)

@app.route('/manage_data', endpoint='manage_data')
def manage_data():
    db = MySQLDatabase()
    all_data = db.get_all_data()
    if not all_data:
        return render_template('main/error_500.html', message="No data available or database error.")
    return render_template('cloud/cloud_data.html', data=all_data)

@app.route('/view_cloud_data/<int:record_id>')
def view_data(record_id):
    db = MySQLDatabase()
    data = db.get_data_by_id(record_id)
    if not data:
        return render_template('main/error_500.html', message="Data not found or database error.")
    return render_template('cloud/view_row.html', data=data)

@app.route('/delete_cloud_data/<int:record_id>', methods=['POST'])
def delete_data(record_id):
    db = MySQLDatabase()
    db.delete_data(record_id)
    return redirect(url_for('manage_data'))

@app.route('/edit_cloud_data/<int:record_id>', methods=['GET'])
def edit_data(record_id):
    db = MySQLDatabase()
    data = db.get_data_by_id(record_id)
    if data:
        return render_template('cloud/edit_cloud_data.html', data=data)
    else:
        return redirect(url_for('manage_data'))
    
@app.route('/update_cloud_data/<int:record_id>', methods=['POST'])
def update_data(record_id):
    name = request.form.get('name')
    email = request.form.get('email')
    age = request.form.get('age')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    db = MySQLDatabase()
    db.update_data(record_id, name, email, age, phone, address)
    return redirect(url_for('view_data', record_id=record_id))

# Error handling route
@app.errorhandler(500)
def internal_error(error):
    return render_template('main/error_500.html', message="Internal server error."), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('main/error_404.html', message="Page not found."), 404


# Set the port for the Flask application
PORT = 5000

def run_flask():
    app.run(port=PORT, debug=True, use_reloader=False)

def open_browser():
    url = f"http://127.0.0.1:{PORT}/"
    webbrowser.open_new(url)

def open_webview():
    # Ensure webview is running in a separate thread
    webview.create_window('Flask App', f'http://127.0.0.1:{PORT}/', resizable=True, maximized=True)
    webview.start()

if __name__ == '__main__':
    # Check if the server is running in the main thread
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        # Open the webview in a separate thread
        threading.Timer(2, open_browser).start()  # Wait for 2 seconds before opening the browser
    
    # Run the Flask app in a separate thread
    app.run(port=PORT, debug=True)