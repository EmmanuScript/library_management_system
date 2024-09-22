# /frontend_api/app.py
from flask import Flask 
from flask_migrate import Migrate
from models import db
from frontend_routes import frontend
from config import Config
from dotenv import load_dotenv
import os
import threading

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)
migration = Migrate(app, db)
app.register_blueprint(frontend)

# Initialize database schema if not already created
with app.app_context():
    db.create_all()

# Start the RabbitMQ listener in a separate thread
if __name__ == '__main__':
    from rabbitmq_listener import start_rabbitmq_listener  # Move import here
    threading.Thread(target=start_rabbitmq_listener, args=(app,), daemon=True).start()  # Pass the app
    app.run(host='0.0.0.0', port=9000, debug=True)
