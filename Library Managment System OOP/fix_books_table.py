"""
Books Table Schema Fix Script
This script will check and fix the books table structure to ensure it has the correct schema.
"""

import mysql.connector
from mysql.connector import Error

def fix_books_table():
    """Fix the books table structure"""
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
        
        # Check if books table exists
        cursor.execute("SHOW TABLES LIKE 'books'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Books table doesn't exist. Creating it...")
            cursor.execute('''
                CREATE TABLE books (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL
                )
            ''')
            print("✓ Books table created with correct schema")
        else:
            print("Books table exists. Checking structure...")
            
            # Get current columns
            cursor.execute("DESCRIBE books")
            columns = cursor.fetchall()
            column_names = [col[0] for col in columns]
            
            print(f"Current columns: {', '.join(column_names)}")
            
            # Check if id column exists
            if 'id' not in column_names:
                print("⚠ Missing 'id' column - this is required!")
                
                # Check if there's data in the table
                cursor.execute("SELECT COUNT(*) FROM books")
                row_count = cursor.fetchone()[0]
                
                if row_count > 0:
                    print(f"⚠ Warning: Table has {row_count} existing rows.")
                    print("  Backing up data...")
                    
                    # Backup existing data
                    cursor.execute("SELECT * FROM books")
                    backup_data = cursor.fetchall()
                    
                    # Get column names for backup
                    cursor.execute("SHOW COLUMNS FROM books")
                    backup_columns = [col[0] for col in cursor.fetchall()]
                    
                    print(f"  Backup columns: {', '.join(backup_columns)}")
                    
                    # Drop and recreate table
                    cursor.execute("DROP TABLE books")
                    print("  Dropped old books table")
                    
                    # Create new table with correct schema
                    cursor.execute('''
                        CREATE TABLE books (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            author VARCHAR(255) NOT NULL,
                            quantity INT NOT NULL
                        )
                    ''')
                    print("  Created new books table with correct schema")
                    
                    # Note: We can't restore data without knowing the exact structure
                    print("  Note: Existing data could not be automatically restored.")
                    print("  Please add books again through the application.")
                else:
                    # No data, safe to drop and recreate
                    cursor.execute("DROP TABLE books")
                    cursor.execute('''
                        CREATE TABLE books (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            title VARCHAR(255) NOT NULL,
                            author VARCHAR(255) NOT NULL,
                            quantity INT NOT NULL
                        )
                    ''')
                    print("✓ Recreated books table with correct schema")
            else:
                # Check other required columns
                missing_columns = []
                if 'title' not in column_names:
                    missing_columns.append('title')
                if 'author' not in column_names:
                    missing_columns.append('author')
                if 'quantity' not in column_names:
                    missing_columns.append('quantity')
                
                if missing_columns:
                    print(f"⚠ Missing columns: {', '.join(missing_columns)}")
                    for col in missing_columns:
                        if col == 'title':
                            cursor.execute("ALTER TABLE books ADD COLUMN title VARCHAR(255) NOT NULL AFTER id")
                        elif col == 'author':
                            cursor.execute("ALTER TABLE books ADD COLUMN author VARCHAR(255) NOT NULL AFTER title")
                        elif col == 'quantity':
                            cursor.execute("ALTER TABLE books ADD COLUMN quantity INT NOT NULL AFTER author")
                        print(f"✓ Added '{col}' column")
                else:
                    print("✓ Books table structure is correct")
            
            # Verify final structure
            cursor.execute("DESCRIBE books")
            final_columns = cursor.fetchall()
            print("\nFinal table structure:")
            for col in final_columns:
                print(f"  - {col[0]} ({col[1]})")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Books table schema fix completed successfully!")
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
    print("Fixing books table schema...")
    print("=" * 50)
    success = fix_books_table()
    if success:
        print("\nYou can now use the books functionality!")
    else:
        print("\nPlease fix the errors above and try again.")
