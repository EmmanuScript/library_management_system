from flask import Flask 
from flask_migrate import Migrate
from models import db
from backend_routes import backend
from config import Config
from dotenv import load_dotenv
import os
import threading
from rabbitmq_listener import start_rabbitmq_listener  # Import from the new module

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db.init_app(app)
migration = Migrate(app, db)

app.register_blueprint(backend)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    threading.Thread(target=start_rabbitmq_listener, args=(app,), daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=True)
