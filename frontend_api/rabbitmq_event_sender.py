# /frontend_api/rabbitmq_event_sender.py
import pika
import json
from flask import current_app

def send_borrow_event(book_id, user_id, days, queue_name='book_updates', rabbitmq_host='localhost'):
    message = {
        'action': 'borrow',
        'book_id': book_id,
        'user_id': user_id,
        'days': days
    }

    with current_app.app_context():  # Automatically use the current app context
        connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue=queue_name)
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=json.dumps(message)
        )
        connection.close()

    print(f" [x] Sent 'borrow' event for Book ID: {book_id}, User ID: {user_id}, Days: {days}")
