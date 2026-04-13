import mysql.connector
from mysql.connector import Error
from flask import current_app

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.config = {
                'host': '127.0.0.1',
                'user': 'root',
                'password': 'MySQL_2026!',
                'port': 3307,
                'database': 'library_db',
                'autocommit': True
            }
        return cls._instance

    def get_connection(self):
        try:
            return mysql.connector.connect(**self.config)
        except Error as e:
            print(f"Database connection error: {e}")
            raise

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor
        except Error as e:
            print(f"Query execution error: {e}")
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None, dictionary=True):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query, params=None, dictionary=True):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=dictionary)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def execute_lastrowid(self, query, params=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

db_manager = DatabaseManager()
