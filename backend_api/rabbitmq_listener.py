import pika
import json
from models import db, Borrow
from flask import Flask

def callback(ch, method, properties, body, app):
    message = json.loads(body)
    action = message.get('action')
    
    if action == 'borrow':
        book_id = message.get('book_id')
        user_id = message.get('user_id')
        days = message.get('days')
        
        # Use the passed app context
        with app.app_context():
            new_borrow = Borrow(book_id=book_id, user_id=user_id, days=days)
            db.session.add(new_borrow)
            try:
                db.session.commit()
                print(f"Borrow event processed for Book ID: {book_id}, User ID: {user_id}, Days: {days}")
            except Exception as e:
                print(f"Error processing borrow event: {e}")
                db.session.rollback()

def start_rabbitmq_listener(app):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='book_updates')
    
    # Pass the app to the callback using a lambda
    channel.basic_consume(queue='book_updates', 
                          on_message_callback=lambda ch, method, properties, body: callback(ch, method, properties, body, app), 
                          auto_ack=True)
    
    print(" [*] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()
