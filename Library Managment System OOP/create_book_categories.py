"""
Create book_categories table and insert default categories
Run this script to set up the book categories table.
"""

import mysql.connector
from mysql.connector import Error

def create_book_categories():
    """Create book_categories table (no default data)."""
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='MySQL_2026!',
            port=3307,
            database='library_db'
        )
        cursor = conn.cursor()
        
        # Create book_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL UNIQUE
            )
        ''')
        print("✓ Table 'book_categories' created or already exists")
        
        # Do NOT insert default categories here.
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Book categories setup completed successfully!")
        return True
        
    except Error as e:
        print(f"\n✗ Error: {e}")
        print(f"Error Code: {e.errno}")
        return False

if __name__ == "__main__":
    print("Setting up book categories...")
    print("=" * 50)
    success = create_book_categories()
    if success:
        print("\nYou can now use category dropdowns in book forms!")
    else:
        print("\nPlease fix the errors above and try again.")
