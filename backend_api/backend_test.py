from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase as Base
import json
from models import db
from backend_routes import backend
import os
from dotenv import load_dotenv

load_dotenv()


class MyConfig(object):
    SQLALCHEMY_DATABASE_URI =  os.getenv('DATABASE_TEST_URL', 'postgresql://<username>:<password>@<db>:5432/<test_db>')
    TESTING = True

def create_app(config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    # Register blueprint here
    app.register_blueprint(backend)
    return app

class TestCase(Base):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(MyConfig())
        cls.client = cls.app.test_client()
        cls._ctx = cls.app.app_context()
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
        from models import Book, User, Borrow

        test_data = [
            User(id=1, email='test1@example.com', firstname="John", lastname="Doe"),
            User(id=2, email='test2@example.com', firstname="Jane", lastname="Smith"),
            Book(title="Test Book 1", author="Author 1", publisher="Wiley", category="fiction", book_available=True),
            Book(title="Test Book 2", author="Author 2", publisher="O'Reilly", category="non-fiction", book_available=False),
            Book(id = 7, title="Test Book 3", author="Author 3", publisher="O'Reilly", category="non-fiction", book_available=False),
            Borrow(id=1, user_id=1, book_id=7, days=7, date_borrowed='2024-09-17 23:55:53.561092', date_returned='2024-09-24 23:55:53.561092'),
        ]

        db.session.add_all(test_data)
        db.session.commit()

    def setUp(self):
        db.session.begin()

    def tearDown(self):
        db.session.rollback()
        db.session.close()


class TestBackendRoutes(TestCase):
    
    def test_add_book(self):
        response = self.client.post("/api/books", data=json.dumps({
            "title": "New Test Book",
            "author": "New Author",
            "publisher": "New Publisher",
            "category": "Sci-Fi"
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Book added")
    
    def test_list_users_borrowed_books(self):
        response = self.client.get("/api/users/books_borrowed")
        print("greta", response.data)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(any(borrow['user_id'] == 1 for borrow in data))

    def test_remove_book(self):
        response = self.client.delete("/api/books/2")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Book removed")

    def test_list_users(self):
        response = self.client.get("/api/users")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        self.assertTrue(any(user['email'] == 'test1@example.com' for user in data))

    def test_unavailable_books(self):
        response = self.client.get("/api/books/unavailable_books")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(len(data)>0)



if __name__ == "__main__":
    import unittest
    unittest.main()
