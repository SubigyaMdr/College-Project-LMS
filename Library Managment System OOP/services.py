from database_manager import db_manager
from models import User, Member, Book, Category
import os
import uuid
from werkzeug.utils import secure_filename

class AuthService:
    @staticmethod
    def login_user(username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        user_data = db_manager.fetch_one(query, (username, password))
        return User.from_dict(user_data)

    @staticmethod
    def register_user(fullname, email, username, password):
        # Check if exists
        check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
        if db_manager.fetch_one(check_query, (username, email)):
            return None, "Username or email already exists"
        
        insert_query = "INSERT INTO users (fullname, email, username, password) VALUES (%s, %s, %s, %s)"
        try:
            user_id = db_manager.execute_lastrowid(insert_query, (fullname, email, username, password))
            return user_id, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def login_member(username, password):
        query = "SELECT * FROM members WHERE username = %s AND password = %s"
        member_data = db_manager.fetch_one(query, (username, password))
        return Member.from_dict(member_data)

    @staticmethod
    def register_member(fullname, email, username, password):
        check_query = "SELECT * FROM members WHERE username = %s OR email = %s"
        if db_manager.fetch_one(check_query, (username, email)):
            return None, "Username or email already exists"

        insert_query = "INSERT INTO members (fullname, email, username, password) VALUES (%s, %s, %s, %s)"
        try:
            member_id = db_manager.execute_lastrowid(insert_query, (fullname, email, username, password))
            return member_id, None
        except Exception as e:
            return None, str(e)

class BookService:
    @staticmethod
    def get_all_books(limit=None, offset=None):
        query = "SELECT * FROM books ORDER BY id DESC"
        if limit is not None:
            query += f" LIMIT {limit}"
        if offset is not None:
            query += f" OFFSET {offset}"
        
        books_data = db_manager.fetch_all(query)
        return [Book.from_dict(b) for b in books_data]

    @staticmethod
    def get_book_by_id(book_id):
        query = "SELECT * FROM books WHERE id = %s"
        book_data = db_manager.fetch_one(query, (book_id,))
        return Book.from_dict(book_data)

    @staticmethod
    def add_book(book_obj):
        query = """
            INSERT INTO books (title, author, genre, quantity, description, image_url) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            book_obj.title, book_obj.author, book_obj.genre, 
            book_obj.quantity, book_obj.description, book_obj.image_url
        )
        return db_manager.execute_lastrowid(query, params)

    @staticmethod
    def update_book(book_id, book_obj):
        query = """
            UPDATE books SET title = %s, author = %s, genre = %s, 
            quantity = %s, description = %s, image_url = %s 
            WHERE id = %s
        """
        params = (
            book_obj.title, book_obj.author, book_obj.genre, 
            book_obj.quantity, book_obj.description, book_obj.image_url, book_id
        )
        db_manager.execute_query(query, params)

    @staticmethod
    def delete_book(book_id):
        query = "DELETE FROM books WHERE id = %s"
        db_manager.execute_query(query, (book_id,))

    @staticmethod
    def get_categories():
        query = "SELECT * FROM book_categories ORDER BY category_name"
        categories_data = db_manager.fetch_all(query)
        return [Category.from_dict(c) for c in categories_data]

    @staticmethod
    def issue_book(book_id, member_id):
        book = BookService.get_book_by_id(book_id)
        if book and book.quantity > 0:
            # Update book quantity
            query = "UPDATE books SET quantity = quantity - 1 WHERE id = %s"
            db_manager.execute_query(query, (book_id,))
            
            # Record in issued_books
            history_query = "INSERT INTO issued_books (book_id, member_id) VALUES (%s, %s)"
            db_manager.execute_query(history_query, (book_id, member_id))
            
            return True, f'Book "{book.title}" issued successfully!'
        return False, "Book not found or not available."

class RecommendationService:
    @staticmethod
    def get_recommendations(member_id, limit=5):
        """
        Genre-based recommendation algorithm:
        1. Find genres user has borrowed most
        2. Find books in those genres not yet borrowed by user
        """
        # Get favorite genres
        genre_query = """
            SELECT b.genre, COUNT(*) as count 
            FROM issued_books ib
            JOIN books b ON ib.book_id = b.id
            WHERE ib.member_id = %s
            GROUP BY b.genre
            ORDER BY count DESC
        """
        user_genres = db_manager.fetch_all(genre_query, (member_id,))
        
        if not user_genres:
            # If no history, return newest books as generic recommendation
            return BookService.get_all_books(limit=limit)

        fav_genres = [g['genre'] for g in user_genres]
        
        # Format for SQL IN clause
        placeholders = ', '.join(['%s'] * len(fav_genres))
        
        # Get recommended books
        recommend_query = f"""
            SELECT * FROM books 
            WHERE genre IN ({placeholders})
            AND id NOT IN (SELECT book_id FROM issued_books WHERE member_id = %s)
            AND quantity > 0
            ORDER BY RAND()
            LIMIT %s
        """
        params = fav_genres + [member_id, limit]
        books_data = db_manager.fetch_all(recommend_query, params)
        
        return [Book.from_dict(b) for b in books_data]

class FileService:
    ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png", "webp"}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_book_cover(file, upload_folder):
        if file and FileService.allowed_file(file.filename):
            original = secure_filename(file.filename)
            ext = original.rsplit(".", 1)[1].lower()
            new_name = f"{uuid.uuid4().hex}.{ext}"
            save_path = os.path.join(upload_folder, new_name)
            file.save(save_path)
            return f"/static/uploads/books/{new_name}"
        return None
