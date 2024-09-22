import pika
import json
from flask import current_app
from models import db, Borrow, Book
from datetime import datetime, timedelta

def callback(ch, method, properties, body, app):
    message = json.loads(body)
    action = message.get('action')
    
    if action == 'borrow':
        book_id = message.get('book_id')
        user_id = message.get('user_id')
        days = message.get('days')
        date_borrowed = datetime.fromisoformat(message['date_borrowed'])
        date_returned = datetime.fromisoformat(message['date_returned'])

        print("this is getting called")

        with app.app_context():  # Use the passed app context
            new_borrow = Borrow(book_id=book_id, user_id=user_id, days=days,  date_borrowed=date_borrowed,
            date_returned=date_returned)
            db.session.add(new_borrow)
            try:
                # Update the book's availability
                book = Book.query.get(book_id)
                if book:
                    book.book_available = False  # Set book as unavailable
                    db.session.commit()  # Commit changes to the book
                db.session.commit()
                print(f"Borrow event processed for Book ID: {book_id}, User ID: {user_id}, Days: {days}")
            except Exception as e:
                print(f"Error processing borrow event: {e}")
                db.session.rollback()

def start_rabbitmq_listener(app, rabbitmq_host='localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='book_updates')
    
    # Wrap the callback to include the app
    def wrapped_callback(ch, method, properties, body):
        callback(ch, method, properties, body, app)

    channel.basic_consume(queue='book_updates', on_message_callback=wrapped_callback, auto_ack=True)
    
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
