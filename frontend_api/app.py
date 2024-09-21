import os
import threading
import signal
import sys
from flask import Flask
from flask_migrate import Migrate
from models import db
from frontend_routes import frontend
from config import Config
from dotenv import load_dotenv
from rabbitmq_listener import start_rabbitmq_listener

load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)
migration = Migrate(app, db)
app.register_blueprint(frontend)

with app.app_context():
    db.create_all()

def signal_handler(signal, frame):
    print("Shutting down RabbitMQ connection...")
    # Ensure your RabbitMQ connection is stored globally for cleanup if needed
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Thread(target=start_rabbitmq_listener, args=(app,)).start()
    app.run(host='0.0.0.0', port=9000, debug=True)
