from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from threading import Timer
import webbrowser
from google.google_sheets import save_to_sheets, create_spreadsheet
from models.excel_handler import ExcelHandler
from models.connection import MySQLDatabase
from models.data_entry import DataEntry
from datetime import datetime
from google.google_list_sheets import GoogleSheetsManager
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

import os
from dotenv import load_dotenv


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Instancia del gestor de Google Sheets
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
    # Obtener datos de la hoja
    data = sheets_manager.get_sheet_data(file_id)
    
    # Obtener el nombre del archivo
    sheet_name = sheets_manager.get_sheet_name(file_id)
    
    return render_template('sheets/view_sheet_data.html', data=data, sheet_name=sheet_name)




@app.route('/download_sheet/<file_id>')
def download_sheet(file_id):
    # Load environment variables
    load_dotenv()
    SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Obtener la metadata del archivo y prepararse para la descarga
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
            excel_handler = ExcelHandler()  # Aquí se usa la clase con la dirección predeterminada
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
    return render_template('cloud/cloud_data.html', data=all_data)

@app.route('/cloud_data', endpoint='manage_data')
def manage_data():
    db = MySQLDatabase()
    all_data = db.get_all_data()
    return render_template('cloud/cloud_data.html', data=all_data)

# Endpoint para ver detalles de un dato específico
@app.route('/view_cloud_data/<int:record_id>')
def view_data(record_id):
    db = MySQLDatabase()
    data = db.get_data_by_id(record_id)
    return render_template('cloud/view_row.html', data=data)

# Endpoint para eliminar un dato específico
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


if __name__ == '__main__':
    app.run(debug=True)
    Timer(2, lambda: webbrowser.open('http://127.0.0.1:5000/')).start()
