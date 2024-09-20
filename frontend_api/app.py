from flask import Flask 
from flask_migrate import Migrate
from models import db
from frontend_routes import frontend
from config import Config

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

migration = Migrate(app, db)

app.register_blueprint(frontend)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
