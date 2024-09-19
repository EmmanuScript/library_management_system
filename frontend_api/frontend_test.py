from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from unittest import TestCase as Base
import json
from models import db
from frontend_routes import frontend

class MyConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:olamizzy66@localhost:5432/library_test_db"
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
        from models import Book, User

        test_books = [
            Book(id=1, title="Test Book 1", author="Author 1", publisher="Wiley", category="fiction", book_available = True),
            Book(id=2, title="Test Book 2", author="Author 2", publisher="J&P", category="fiction", book_available = True),User(id =3, email='testt@example.com', firstname="adebayo", lastname='lukman')
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
        response = self.client.post("/api/users/register", 
                                    data=json.dumps({
                                        "email": "test@example.com",
                                        "firstname": "John",
                                        "lastname": "Doe"
                                    }),
                                    content_type='application/json')
        print(response.data, "uer")
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
        response = self.client.post("/api/books/borrow_books", 
                                    data=json.dumps({"user_id": 3, "days": 7, "book_id": 2}),
                                    content_type='application/json')
        print("h56", response.data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data["message"], "Borrowed Successfully")

    def test_filter_books_by_category(self):
        response = self.client.get("/api/books?category=fiction")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(any(book['category'] == 'fiction' for book in data))

    


if __name__ == "__main__":
    import unittest
    unittest.main()
