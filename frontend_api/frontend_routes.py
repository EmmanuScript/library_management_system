from flask import Blueprint
from frontend_controller import register_user_controller, list_books_controller, get_book_controller, borrow_book_controller, return_book_controller

frontend = Blueprint('frontend', __name__)

@frontend.route('/api/users/register', methods=['POST'])
def register_user():
    return register_user_controller()

@frontend.route('/api/books', methods=['GET'])
def list_books():
    return list_books_controller()

@frontend.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    return get_book_controller(id)

@frontend.route('/api/books/borrow_books', methods=['POST'])
def borrow_book():
    return borrow_book_controller()

@frontend.route('/api/books/return_books/<int:id>', methods=['POST'])
def return_book(id):
    return return_book_controller(id)
