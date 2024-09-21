from models import db, Book, User, Borrow
from marshmallow import ValidationError
from datetime import datetime, timedelta
from flask import jsonify, request
import pika
import json

class BackendController:
    
    @staticmethod
    def add_book():
        try:
            data = request.json
            
            # Check if the book already exists
            check_book = Book.query.filter_by(title=data['title'], author=data['author']).first()
            if check_book:
                return jsonify({'message': 'Book already exists'}), 409

            # Create a new book
            new_book = Book(
                title=data['title'],
                author=data['author'],
                publisher=data['publisher'],
                category=data['category'],
                book_available=True
            )
            db.session.add(new_book)
            db.session.commit()

            # Publish message to RabbitMQ
            BackendController.publish_message('add_book', new_book)

            return jsonify({'message': 'Book added'}), 201
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 400
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @staticmethod
    def publish_event(event_type, data):
        print('running event for rabbit mq')
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        
        channel.exchange_declare(exchange='library_exchange', exchange_type='topic')

        message = json.dumps(data)
        routing_key = f"library.{event_type}"

        channel.basic_publish(exchange='library_exchange', routing_key=routing_key, body=message)
        connection.close()

    @staticmethod
    def publish_message(action, book):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='library')

        message = {
            'action': action,
            'book': {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'publisher': book.publisher,
                'category': book.category,
                'book_available': book.book_available
            }
        }

        channel.basic_publish(exchange='', routing_key='library', body=json.dumps(message))
        connection.close()

    @staticmethod
    def remove_book(id):
        try:
            book = Book.query.get_or_404(id)
            db.session.delete(book)
            db.session.commit()

            BackendController.publish_message('remove_book', book)

            return jsonify({'message': 'Book removed'}), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @staticmethod
    def list_users():
        try:
            users = User.query.all()
            user_list = [{'id': user.id, 'email': user.email, 'firstname': user.firstname, 'lastname': user.lastname} for user in users]
            return jsonify(user_list), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

    @staticmethod
    def list_books_user_borrowed():
        try:
            # Query all borrowed books
            borrows = Borrow.query.all()

            # Check if any borrow records exist
            if not borrows:
                return jsonify({'message': 'No borrowed books found'}), 404

            # Create a list of borrowed books
            borrowed_list = [
                {
                    'user_id': borrow.user_id, 
                    'book_id': borrow.book_id, 
                    'borrow_date': borrow.date_borrowed, 
                    'return_date': borrow.date_returned
                } 
                for borrow in borrows
            ]
            return jsonify(borrowed_list), 200
        
        except Exception as e:
            # Log any other unexpected errors
            return jsonify({'message': 'An unexpected error occurred. Please try again later.', 'error': e}), 500


    @staticmethod
    def unavailable_books():
        try:
            books = Book.query.filter_by(book_available=False).all()
            book_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'publisher': book.publisher, 'category': book.category} for book in books]
            return jsonify(book_list), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    