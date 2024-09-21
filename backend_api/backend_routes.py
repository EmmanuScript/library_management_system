# backend_routes.py
from flask import Blueprint
from backend_controller import BackendController

backend = Blueprint('backend', __name__)

# Add a book
@backend.route('/api/books', methods=['POST'])
def add_book():
    return BackendController.add_book()

# Remove a book by ID
@backend.route('/api/books/<int:id>', methods=['DELETE'])
def remove_book(id):
    return BackendController.remove_book(id)

# List all users
@backend.route('/api/users', methods=['GET'])
def list_users():
    return BackendController.list_users()

# List users and their borrowed books
@backend.route('/api/users/books_borrowed', methods=['GET'])
def list_users_borrowed_books():
    return BackendController.list_books_user_borrowed()

# List unavailable books
@backend.route('/api/books/unavailable_books', methods=['GET'])
def unavailable_books():
    return BackendController.unavailable_books()


