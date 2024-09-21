from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase as Base
import json
from models import db
from frontend_routes import frontend
import os
from dotenv import load_dotenv

load_dotenv()

class MyConfig(object):
    SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_TEST_URL', 'postgresql://<username>:<password>@<db>:5432/<test_db>')
    TESTING = True

def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)  # Make sure this is called correctly
    # Register blueprint here
    app.register_blueprint(frontend)
    return app

class TestCase(Base):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(MyConfig())
        cls.client = cls.app.test_client()
        cls._ctx = cls.app.app_context()  # Use app_context
        cls._ctx.push()
        with cls.app.app_context():
            db.create_all()

        # Insert test data into the database
        cls._insert_test_data()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
        cls._ctx.pop()

    @classmethod
    def _insert_test_data(cls):
        # Insert test data here
        # For example:
        from models import Book, User, Borrow

        test_books = [
            Book(id=1, title="Test Book 1", author="Author 1", publisher="Wiley", category="fiction", book_available = True),
            Book(id=2, title="Test Book 2", author="Author 2", publisher="Wiley", category="fiction", book_available = True),User(id =3, email='testt@example.com', firstname="adebayo", lastname='lukman'), 
            Book(id=3, title = 'Test Book 3', author='Author 3', publisher='Smith and sons',category='thriller',book_available=False), Borrow(id=2, user_id=3, book_id=2, days=7, date_borrowed='2024-09-17 23:55:53.561092', date_returned = '2024-09-24 23:55:53.561092')
        ]

        db.session.add_all(test_books)
        db.session.commit()

    def setUp(self):
        db.session.begin()

    def tearDown(self):
        db.session.rollback()
        db.session.close()


class TestModel(TestCase):

    def test_enroll_user(self):
        response = self.client.post("/api/users/register", data=json.dumps({
        "email": "test@example.com",
        "firstname": "John",
        "lastname": "Doe"}),
        content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["email"], "test@example.com")

    def test_list_books(self):
        response = self.client.get("/api/books")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_get_book_by_id(self):
        response = self.client.get("/api/books/1")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["id"], 1)

    def test_filter_books_by_publisher(self):
        response = self.client.get("/api/books?publisher=Wiley")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(any(book['publisher'] == 'Wiley' for book in data))

    def test_borrow_book(self):
        response = self.client.post("/api/books/borrow_books", data=json.dumps({"user_id": 3, "days": 7, "book_id": 1}),content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Borrowed Successfully")
    
    def test_return_book(self):
        response = self.client.post("/api/books/return_books/2", data=json.dumps({"user_id": 3}),content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Book returned successfully")

    def test_filter_books_by_category(self):
        response = self.client.get("/api/books?category=fiction")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(any(book['category'] == 'fiction' for book in data))

    


if __name__ == "__main__":
    import unittest
    unittest.main()
