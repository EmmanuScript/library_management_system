from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validates, ValidationError
from datetime import datetime, timedelta

db = SQLAlchemy()

# User Model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    
    # One-to-many relationship with Borrow
    books_borrowed = db.relationship('Borrow', backref='user', lazy='dynamic')
    
    def __repr__(self):
        return f"<User {self.email}>"


# User Schema with Validation
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True, error_messages={'required': 'Email is required.'})
    firstname = fields.Str(required=True, error_messages={'required': 'First name is required.'})
    lastname = fields.Str(required=True, error_messages={'required': 'Last name is required.'})
    
    @validates('firstname')
    def validate_firstname(self, value):
        if len(value) < 2:
            raise ValidationError("First name must be at least 2 characters long.")
    
    @validates('lastname')
    def validate_lastname(self, value):
        if len(value) < 2:
            raise ValidationError("Last name must be at least 2 characters long.")


# Book Model
class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    # Indicates availability of the book
    book_available = db.Column(db.Boolean, default=True, index=True)
    
    # One-to-many relationship with Borrow
    borrow_records = db.relationship('Borrow', backref='book', lazy='dynamic')

    def __repr__(self):
        return f"<Book {self.title} by {self.author}>"


# Book Schema with Validation
class BookSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, error_messages={'required': 'Title is required.'})
    author = fields.Str(required=True, error_messages={'required': 'Author is required.'})
    publisher = fields.Str(required=True, error_messages={'required': 'Publisher is required.'})
    category = fields.Str(required=True, error_messages={'required': 'Category is required.'})
    book_available = fields.Boolean(default=True, dump_only=True)

    @validates('title')
    def validate_title(self, value):
        if len(value) < 2:
            raise ValidationError("Title must be at least 2 characters long.")


# Borrow Model 
class Borrow(db.Model):
    __tablename__ = 'borrows'
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    # Duration of borrow in days
    days = db.Column(db.Integer, nullable=False)
    
    # Timestamps
    date_borrowed = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_returned = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<Borrow User {self.user_id} -> Book {self.book_id}>"

    # Checks to see if overdue
    @property
    def is_overdue(self):
        return datetime.utcnow() > self.return_date


# Borrow Schema with Validation
class BorrowSchema(Schema):
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True, error_messages={'required': 'User ID is required.'})
    book_id = fields.Int(required=True, error_messages={'required': 'Book ID is required.'})
    days = fields.Int(required=True, error_messages={'required': 'Number of days is required.'})
    date_borrowed = fields.DateTime(dump_only=True)
    date_returned = fields.DateTime(dump_only=True)

    @validates('days')
    def validate_days(self, value):
        if value <= 0:
            raise ValidationError("Number of days must be a positive integer.")

borrow_schema = BorrowSchema()

class ReturnBookSchema(Schema):
    user_id = fields.Int(required=True, error_messages={'required': 'User ID is required.'})