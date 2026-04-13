"""
Add new columns to books table: genre, description, image_url
Run this script to update the database schema.
"""

import mysql.connector
from mysql.connector import Error

def add_book_columns():
    """Add genre, description, and image_url columns to books table"""
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='MySQL_2026!',
            port=3307,
            database='library_db'
        )
        cursor = conn.cursor()
        
        # Check current columns
        cursor.execute("DESCRIBE books")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        print(f"Current columns: {', '.join(column_names)}")
        
        # Add genre column if it doesn't exist
        if 'genre' not in column_names:
            cursor.execute("ALTER TABLE books ADD COLUMN genre VARCHAR(100) AFTER author")
            print("✓ Added 'genre' column")
        else:
            print("✓ 'genre' column already exists")
        
        # Add description column if it doesn't exist
        if 'description' not in column_names:
            cursor.execute("ALTER TABLE books ADD COLUMN description TEXT AFTER quantity")
            print("✓ Added 'description' column")
        else:
            print("✓ 'description' column already exists")
        
        # Add image_url column if it doesn't exist
        if 'image_url' not in column_names:
            cursor.execute("ALTER TABLE books ADD COLUMN image_url VARCHAR(500) AFTER description")
            print("✓ Added 'image_url' column")
        else:
            print("✓ 'image_url' column already exists")
        
        # Verify final structure
        cursor.execute("DESCRIBE books")
        final_columns = cursor.fetchall()
        print("\nFinal table structure:")
        for col in final_columns:
            print(f"  - {col[0]} ({col[1]})")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n✓ Books table updated successfully!")
        return True
        
    except Error as e:
        print(f"\n✗ Error: {e}")
        print(f"Error Code: {e.errno}")
        return False

if __name__ == "__main__":
    print("Adding new columns to books table...")
    print("=" * 50)
    success = add_book_columns()
    if success:
        print("\nDatabase schema updated! You can now use genre, description, and image features.")
    else:
        print("\nPlease fix the errors above and try again.")
