class User:
    def __init__(self, id=None, fullname=None, email=None, username=None, password=None):
        self.id = id
        self.fullname = fullname
        self.email = email
        self.username = username
        self.password = password

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return User(
            id=data.get('id'),
            fullname=data.get('fullname'),
            email=data.get('email'),
            username=data.get('username'),
            password=data.get('password')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'username': self.username,
            'password': self.password
        }

class Member:
    def __init__(self, id=None, fullname=None, email=None, username=None, password=None):
        self.id = id
        self.fullname = fullname
        self.email = email
        self.username = username
        self.password = password

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return Member(
            id=data.get('id'),
            fullname=data.get('fullname'),
            email=data.get('email'),
            username=data.get('username'),
            password=data.get('password')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'fullname': self.fullname,
            'email': self.email,
            'username': self.username,
            'password': self.password
        }

class Book:
    def __init__(self, id=None, title=None, author=None, genre=None, quantity=0, description=None, image_url=None):
        self.id = id
        self.title = title
        self.author = author
        self.genre = genre
        self.quantity = quantity
        self.description = description
        self.image_url = image_url

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return Book(
            id=data.get('id'),
            title=data.get('title'),
            author=data.get('author'),
            genre=data.get('genre'),
            quantity=data.get('quantity', 0),
            description=data.get('description'),
            image_url=data.get('image_url')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'quantity': self.quantity,
            'description': self.description,
            'image_url': self.image_url
        }

class Category:
    def __init__(self, id=None, category_name=None):
        self.id = id
        self.category_name = category_name

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        # Handle both 'id' and 'categories_id' (legacy schema naming)
        id_val = data.get('id') or data.get('categories_id')
        return Category(
            id=id_val,
            category_name=data.get('category_name')
        )

    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category_name
        }

class IssuedBook:
    def __init__(self, id=None, book_id=None, member_id=None, issue_date=None, return_date=None, status='issued'):
        self.id = id
        self.book_id = book_id
        self.member_id = member_id
        self.issue_date = issue_date
        self.return_date = return_date
        self.status = status

    @staticmethod
    def from_dict(data):
        if not data:
            return None
        return IssuedBook(
            id=data.get('id'),
            book_id=data.get('book_id'),
            member_id=data.get('member_id'),
            issue_date=data.get('issue_date'),
            return_date=data.get('return_date'),
            status=data.get('status')
        )
