"""
Database Setup Script
Run this script to create the database if it doesn't exist.
"""

import mysql.connector
from mysql.connector import Error

def create_database():
    """Create the library_db database if it doesn't exist"""
    try:
        # Connect without specifying database
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='MySQL_2026!',
            port=3307
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS library_db")
        print("✓ Database 'library_db' created or already exists")
        
        # Use the database
        cursor.execute("USE library_db")
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                quantity INT NOT NULL
            )
        ''')
        print("✓ Table 'books' created or already exists")
        
        # Drop users table if it exists (to ensure correct schema)
        cursor.execute("DROP TABLE IF EXISTS users")
        
        cursor.execute('''
            CREATE TABLE users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        ''')
        print("✓ Table 'users' created with correct schema")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database setup completed successfully!")
        return True
        
    except Error as e:
        print(f"\n✗ Error: {e}")
        print(f"Error Code: {e.errno}")
        
        if e.errno == 1045:
            print("\nPlease check your MySQL username and password in database.py")
        elif e.errno == 2003:
            print("\nCannot connect to MySQL server.")
            print("Please ensure MySQL is running on port 3307")
        else:
            print(f"\nUnexpected error occurred: {e}")
        
        return False

if __name__ == "__main__":
    print("Setting up database...")
    print("=" * 50)
    success = create_database()
    if success:
        print("\nYou can now run your Flask application!")
    else:
        print("\nPlease fix the errors above and try again.")
