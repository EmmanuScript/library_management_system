import pika
import json
from app import app
from models import db, Book, Borrow
from datetime import datetime, timedelta


def callback(ch, method, properties, body):
    message = json.loads(body)
    action = message['action']

    if action == 'add':
        book_data = message['book']
        new_book = Book(
            id=book_data['id'],
            title=book_data['title'],
            author=book_data['author'],
            book_available=True
        )
        db.session.add(new_book)
        db.session.commit()
    elif action == 'borrow':
        book_id = message['book_id']
        user_id = message['user_id']
        days = message['days']
        book = Book.query.get(book_id)
        if book:
            # Update book availability
            book.book_available = False
            
            # Add the borrow record
            borrow = Borrow(
                user_id=user_id,
                book_id=book_id,
                days=days,
                date_borrowed=datetime.utcnow(),
                date_returned=datetime.utcnow() + timedelta(days=days)
            )
            db.session.add(borrow)
            db.session.commit()

def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='book_updates')
    channel.basic_consume(queue='book_updates', on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    with app.app_context():
        start_consumer()
