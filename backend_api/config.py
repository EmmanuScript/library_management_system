import os



class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mydefaultsecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5433/backend_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False