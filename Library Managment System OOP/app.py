from flask import Flask, jsonify, session, redirect, url_for, render_template, request, flash
from database import init_db
from models import Book
from services import AuthService, BookService, FileService, RecommendationService
import os

app = Flask(__name__)
app.secret_key = "library_secret_key"

# Upload configuration
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads", "books")
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize database on startup
try:
    init_db()
except Exception as e:
    print(f"Warning: Database initialization failed: {e}")

@app.route('/test-db', methods=['GET'])
def test_db():
    try:
        from database_manager import db_manager
        db_manager.fetch_one("SELECT 1")
        return jsonify({"status": "success", "message": "Database connection successful"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/books/add', methods=('GET', 'POST'))
def add_book():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    categories = BookService.get_categories()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        genre = request.form.get('genre', '').strip()
        description = request.form.get('description', '').strip()
        try:
            quantity = int(request.form.get('quantity', 0) or 0)
        except (ValueError, TypeError):
            quantity = 0

        error = None
        if not all([title, author, genre, description]):
            error = "All fields are required."
        elif quantity <= 0:
            error = "Quantity must be a positive number."

        image_url = ""
        uploaded = request.files.get("image_file")
        if uploaded and uploaded.filename:
            image_url = FileService.save_book_cover(uploaded, app.config["UPLOAD_FOLDER"])
            if not image_url:
                error = "Invalid image type. Use jpeg/jpg/png/webp."

        if error:
            return render_template('add_book.html', categories=categories, error=error)

        new_book = Book(title=title, author=author, genre=genre, quantity=quantity, description=description, image_url=image_url)
        BookService.add_book(new_book)
        flash('Book added successfully!', 'success')
        return redirect(url_for('dashboard') + '?section=books')

    return render_template('add_book.html', categories=categories)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        user = AuthService.login_user(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['fullname'] = user.fullname
            return redirect(url_for('dashboard'))
        else:
            return render_template('index.html', error="Invalid username or password")
            
    return render_template('index.html')

@app.route('/login')
def login():
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm-password', '')
        
        if not all([fullname, email, username, password, confirm_password]):
            return render_template('register.html', error="All fields are required")
        if password != confirm_password:
            return render_template('register.html', error="Passwords do not match")
        
        user_id, error = AuthService.register_user(fullname, email, username, password)
        if error:
            return render_template('register.html', error=error)
        
        session['user_id'] = user_id
        session['username'] = username
        session['fullname'] = fullname
        flash('Registration successful! Welcome.', 'success')
        return redirect(url_for('dashboard'))
            
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    books = BookService.get_all_books()
    return render_template('dashboard.html', username=session.get('username'), books=books)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# ============ MEMBER PORTAL ============

@app.route('/member/login', methods=('GET', 'POST'))
def member_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        member = AuthService.login_member(username, password)
        if member:
            session['member_id'] = member.id
            session['member_username'] = member.username
            session['member_fullname'] = member.fullname
            return redirect(url_for('member_dashboard'))
        return render_template('member_login.html', error="Invalid username or password")
    return render_template('member_login.html')

@app.route('/member/register', methods=('GET', 'POST'))
def member_register():
    if request.method == 'POST':
        fullname = request.form.get('fullname', '').strip()
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm-password', '')
        
        if not all([fullname, email, username, password, confirm_password]):
            return render_template('member_register.html', error="All fields are required")
        
        member_id, error = AuthService.register_member(fullname, email, username, password)
        if error:
            return render_template('member_register.html', error=error)
            
        session['member_id'] = member_id
        session['member_username'] = username
        session['member_fullname'] = fullname
        flash('Registration successful!', 'success')
        return redirect(url_for('member_dashboard'))
    return render_template('member_register.html')

@app.route('/member/dashboard')
def member_dashboard():
    if 'member_id' not in session:
        return redirect(url_for('member_login'))
    
    member_id = session.get('member_id')
    books = BookService.get_all_books()
    recommendations = RecommendationService.get_recommendations(member_id)
    
    return render_template('member_dashboard.html', 
                         username=session.get('member_username'), 
                         books=books, 
                         recommendations=recommendations)

@app.route('/member/logout')
def member_logout():
    session.pop('member_id', None)
    return redirect(url_for('member_login'))

@app.route('/member/books/preview/<int:id>')
def member_book_preview(id):
    if 'member_id' not in session:
        return redirect(url_for('member_login'))
    book = BookService.get_book_by_id(id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('member_dashboard'))
    return render_template('member_book_preview.html', book=book)

@app.route('/books')
def books():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    per_page = 10
    all_books = BookService.get_all_books()
    total_books = len(all_books)
    start = (page - 1) * per_page
    end = start + per_page
    books = all_books[start:end]
    total_pages = (total_books + per_page - 1) // per_page if total_books > 0 else 1
    return render_template('book_menu.html', books=books, page=page, total_pages=total_pages, total_books=total_books)

@app.route('/books/preview/<int:id>')
def book_preview(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    book = BookService.get_book_by_id(id)
    if not book:
        flash('Book not found', 'error')
        return redirect(url_for('books'))
    return render_template('book_preview.html', book=book)

@app.route('/books/edit/<int:id>', methods=('GET', 'POST'))
def edit_book(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    book = BookService.get_book_by_id(id)
    if not book:
        return redirect(url_for('books'))

    categories = BookService.get_categories()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        genre = request.form.get('genre', '').strip()
        description = request.form.get('description', '').strip()
        try:
            quantity = int(request.form.get('quantity', 0) or 0)
        except (ValueError, TypeError):
            quantity = 0

        error = None
        if not all([title, author, genre, description]) or quantity <= 0:
            error = "Valid details required."

        image_url = book.image_url
        uploaded = request.files.get("image_file")
        if uploaded and uploaded.filename:
            new_img = FileService.save_book_cover(uploaded, app.config["UPLOAD_FOLDER"])
            if new_img: image_url = new_img

        if error:
            return render_template('edit_book.html', book=book, categories=categories, error=error)

        book.title, book.author, book.genre, book.quantity, book.description, book.image_url = \
            title, author, genre, quantity, description, image_url
        BookService.update_book(id, book)
        return redirect(url_for('books'))

    return render_template('edit_book.html', book=book, categories=categories)

@app.route('/books/delete/<int:id>', methods=('POST',))
def delete_book(id):
    if 'user_id' not in session:
        return redirect(url_for('index'))
    BookService.delete_book(id)
    return redirect(url_for('books'))

@app.route('/books/issue', methods=('GET', 'POST'))
def issue_book():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        book_id = request.form.get('book_id')
        student_id = request.form.get('student_id')
        if book_id and student_id:
            # Note: in this system, student_id refers to the member's ID
            success, message = BookService.issue_book(book_id, student_id)
            flash(message, 'success' if success else 'error')
        return redirect(url_for('books'))
    return render_template('issue.html')

if __name__ == "__main__":
    app.run(debug=True)

