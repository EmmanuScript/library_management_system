from flask import Flask 
from flask_migrate import Migrate
from models import db
from backend_routes import backend
from config import Config
from dotenv import load_dotenv
import os
import pika
import threading
from rabbitmq_listener import start_rabbitmq_listener  # Import the listener


# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

app.config.from_object(Config)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')

db.init_app(app)

migration = Migrate(app, db)

def create_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='book_updates')
    return channel

def get_rabbitmq_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='book_updates')
    return channel

rabbitmq_channel = get_rabbitmq_channel()



app.register_blueprint(backend)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    # Start RabbitMQ listener in a separate thread
    threading.Thread(target=start_rabbitmq_listener, args=(app,)).start()
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=9001, debug=True)

