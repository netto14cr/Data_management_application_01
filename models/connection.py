import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Cargar variables de entorno del archivo .env
load_dotenv()

class MySQLDatabase:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST')
        self.database = os.getenv('MYSQL_DATABASE')
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
    
    def connect(self):
        try:
            connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if connection.is_connected():
                return connection
            else:
                raise Exception("Connection to database failed.")
        except Error as e:
            print(f"Error: {e}")
            return None

    def insert_data(self, name, email, age, phone, address):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    'INSERT INTO personal_data (name, email, age, phone, address) VALUES (%s, %s, %s, %s, %s)',
                    (name, email, age, phone, address)
                )
                connection.commit()
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
                
    def get_data_by_id(self, record_id):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    'SELECT * FROM personal_data WHERE id = %s',
                    (record_id,)
                )
                result = cursor.fetchone()
                return result
            except Error as e:
                print(f"Error: {e}")
                return None
            finally:
                cursor.close()
                connection.close()
    
    def get_all_data(self):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    'SELECT * FROM personal_data'
                )
                result = cursor.fetchall()
                return result
            except Error as e:
                print(f"Error: {e}")
                return []
            finally:
                cursor.close()
                connection.close()
                
    def delete_data(self, record_id):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute('DELETE FROM personal_data WHERE id = %s', (record_id,))
                connection.commit()
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
                
    def update_data(self, record_id, name, email, age, phone, address):
        connection = self.connect()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute(
                    '''
                    UPDATE personal_data 
                    SET name = %s, email = %s, age = %s, phone = %s, address = %s
                    WHERE id = %s
                    ''',
                    (name, email, age, phone, address, record_id)
                )
                connection.commit()
            except Error as e:
                print(f"Error: {e}")
            finally:
                cursor.close()
                connection.close()
