import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='MySQL_2026!',
            port=3307,
            database='library_db',
            autocommit=False
        )
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        raise

def init_db():
    """Initialize database tables with proper schema"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create books table - check and fix structure if needed
        cursor.execute("SHOW TABLES LIKE 'books'")
        books_table_exists = cursor.fetchone()
        
        if books_table_exists:
            # Check if id column exists
            cursor.execute("SHOW COLUMNS FROM books LIKE 'id'")
            id_exists = cursor.fetchone()
            
            if not id_exists:
                print("Books table exists but missing 'id' column. Fixing...")
                # Check what columns exist
                cursor.execute("DESCRIBE books")
                existing_columns = cursor.fetchall()
                column_names = [col[0] for col in existing_columns]
                
                # Drop and recreate with correct schema
                cursor.execute("DROP TABLE IF EXISTS books")
                print("Dropped old books table")
        
        # Create books table with correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                genre VARCHAR(100),
                quantity INT NOT NULL,
                description TEXT,
                image_url VARCHAR(500)
            )
        ''')
        
        # Add new columns to existing table if they don't exist
        cursor.execute("DESCRIBE books")
        existing_columns = [col[0] for col in cursor.fetchall()]
        
        if 'genre' not in existing_columns:
            try:
                cursor.execute("ALTER TABLE books ADD COLUMN genre VARCHAR(100) AFTER author")
            except:
                pass
        
        if 'description' not in existing_columns:
            try:
                cursor.execute("ALTER TABLE books ADD COLUMN description TEXT AFTER quantity")
            except:
                pass
        
        if 'image_url' not in existing_columns:
            try:
                cursor.execute("ALTER TABLE books ADD COLUMN image_url VARCHAR(500) AFTER description")
            except:
                pass
        
        # Create users table - drop and recreate to ensure correct schema
        # First check if table exists
        cursor.execute("SHOW TABLES LIKE 'users'")
        users_table_exists = cursor.fetchone()
        
        if users_table_exists:
            # Check if username column exists
            cursor.execute("SHOW COLUMNS FROM users LIKE 'username'")
            username_exists = cursor.fetchone()
            
            if not username_exists:
                print("Users table exists but missing 'username' column. Fixing...")
                # Drop and recreate with correct schema
                cursor.execute("DROP TABLE IF EXISTS users")
                print("Dropped old users table")
        
        # Create users table with correct schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        ''')
        
        # Create book_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_categories (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(100) NOT NULL UNIQUE
            )
        ''')
        
        # Create members table (for member portal)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                username VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        ''')

        # Create issued_books table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS issued_books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_id INT UNSIGNED NOT NULL,
                member_id INT NOT NULL,
                issue_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                return_date TIMESTAMP NULL,
                status VARCHAR(50) DEFAULT 'issued',
                FOREIGN KEY (book_id) REFERENCES books(id),
                FOREIGN KEY (member_id) REFERENCES members(id)
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database tables initialized successfully.")
    except Error as e:
        print(f"Error initializing database: {e}")
        print(f"Error Code: {e.errno}")
        if e.errno == 1049:  # Unknown database
            print("\n*** IMPORTANT: Database 'library_db' does not exist! ***")
            print("Please create the database first:")
            print("1. Connect to MySQL on port 3307")
            print("2. Run: CREATE DATABASE library_db;")
            print("Or run: python setup_database.py")
        raise

# Initialize the database when this module is imported (or called explicitly)
if __name__ == '__main__':
    init_db()
    print("Database initialized.")
