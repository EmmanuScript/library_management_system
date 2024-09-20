from flask import Flask 
from flask_migrate import Migrate
from models import db
from backend_routes import backend
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

migration = Migrate(app, db)

app.register_blueprint(backend)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080, debug=True)
