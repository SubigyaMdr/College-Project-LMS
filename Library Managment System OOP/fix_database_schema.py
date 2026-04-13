"""
Database Schema Fix Script
This script will check and fix the users table structure to match the expected schema.
"""

import mysql.connector
from mysql.connector import Error

def fix_users_table():
    """Fix the users table structure"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='MySQL_2026!',
            port=3307,
            database='library_db'
        )
        cursor = conn.cursor()
        
        # Check if users table exists and get its structure
        cursor.execute("SHOW TABLES LIKE 'users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Users table doesn't exist. Creating it...")
            cursor.execute('''
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fullname VARCHAR(255) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL
                )
            ''')
            print("✓ Users table created with correct schema")
        else:
            print("Users table exists. Checking structure...")
            
            # Get current columns
            cursor.execute("DESCRIBE users")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            print(f"Current columns: {', '.join(column_names)}")
            
            # Check and add missing columns
            needs_fix = False
            
            if 'username' not in column_names:
                print("⚠ Missing 'username' column - this is required!")
                needs_fix = True
                # Check if there's data in the table
                cursor.execute("SELECT COUNT(*) FROM users")
                row_count = cursor.fetchone()[0]
                
                if row_count > 0:
                    print(f"⚠ Warning: Table has {row_count} existing rows.")
                    print("  Adding username column with default values...")
                    try:
                        cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR(255) AFTER email")
                        # Set default username based on email or id
                        cursor.execute("""
                            UPDATE users 
                            SET username = CONCAT('user_', id) 
                            WHERE username IS NULL OR username = ''
                        """)
                        # Now add unique constraint
                        cursor.execute("ALTER TABLE users ADD UNIQUE KEY unique_username (username)")
                        print("✓ Added 'username' column with default values")
                    except Error as e:
                        print(f"Error adding username column: {e}")
                        raise
                else:
                    try:
                        cursor.execute("ALTER TABLE users ADD COLUMN username VARCHAR(255) UNIQUE AFTER email")
                        print("✓ Added 'username' column")
                    except Error as e:
                        if e.errno == 1060:  # Duplicate column name
                            print("Username column already exists (different case?)")
                        else:
                            raise
            
            if 'fullname' not in column_names:
                print("Adding missing 'fullname' column...")
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN fullname VARCHAR(255) AFTER id")
                    print("✓ Added 'fullname' column")
                except Error as e:
                    if e.errno == 1060:
                        print("Fullname column already exists")
                    else:
                        raise
            
            if 'email' not in column_names:
                print("Adding missing 'email' column...")
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) UNIQUE AFTER fullname")
                    print("✓ Added 'email' column")
                except Error as e:
                    if e.errno == 1060:
                        print("Email column already exists")
                    else:
                        raise
            
            if 'password' not in column_names:
                print("Adding missing 'password' column...")
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN password VARCHAR(255) AFTER username")
                    print("✓ Added 'password' column")
                except Error as e:
                    if e.errno == 1060:
                        print("Password column already exists")
                    else:
                        raise
            
            # Verify final structure
            cursor.execute("DESCRIBE users")
            final_columns = cursor.fetchall()
            print("\nFinal table structure:")
            for col in final_columns:
                print(f"  - {col[0]} ({col[1]})")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Database schema fix completed successfully!")
        return True
        
    except Error as e:
        print(f"\n✗ Error: {e}")
        print(f"Error Code: {e.errno}")
        
        if e.errno == 1049:
            print("\nDatabase 'library_db' does not exist!")
            print("Please run setup_database.py first")
        elif e.errno == 1045:
            print("\nAccess denied. Please check your MySQL credentials in the script")
        elif e.errno == 2003:
            print("\nCannot connect to MySQL server on port 3307")
            print("Please ensure MySQL is running")
        else:
            print(f"\nUnexpected error: {e}")
        
        return False

if __name__ == "__main__":
    print("Fixing database schema...")
    print("=" * 50)
    success = fix_users_table()
    if success:
        print("\nYou can now try registering again!")
    else:
        print("\nPlease fix the errors above and try again.")
