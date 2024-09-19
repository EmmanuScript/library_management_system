import os
from dotenv import load_dotenv



class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'mydefaultsecretkey')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/library_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False