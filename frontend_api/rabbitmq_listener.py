# rabbitmq_service.py
import pika
import json
from models import db, Book, Borrow
from flask import app

# Callback to handle book actions based on the message
def callback(ch, method, properties, body):
    message = json.loads(body)
    action = message.get('action')
    book_data = message.get('book')

    if action and book_data:
        with app.app_context():  # Automatically reference the current app context
            handle_message(action, book_data)

def handle_message(action, book_data):
    if action == 'add_book':
        new_book = Book(
            id=book_data['id'],
            title=book_data['title'],
            author=book_data['author'],
            publisher=book_data['publisher'],
            category=book_data['category'],
            book_available=book_data['book_available']
        )
        db.session.add(new_book)
        db.session.commit()

    elif action == 'remove_book':
        book = Book.query.get(book_data['id'])
        if book:
            db.session.delete(book)
            db.session.commit()


# Function to set up the RabbitMQ listener
def start_rabbitmq_listener(app, queue_name='library', rabbitmq_host='localhost'):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    # Use lambda to inject the app into the callback
    channel.basic_consume(queue=queue_name,
                          on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, app), 
                          auto_ack=True)

    print(f" [*] Waiting for messages in queue '{queue_name}'. To exit, press CTRL+C")
    channel.start_consuming()
