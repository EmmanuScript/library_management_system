from flask import jsonify, request
from models import BorrowSchema, ReturnBookSchema, UserSchema, db, Book, User, Borrow
from datetime import datetime, timedelta
from marshmallow import ValidationError

def register_user_controller():  
    schema = UserSchema()  
    try:    
        data = schema.load(request.json)

        check_user = User.query.filter_by(email=data['email']).first()

        print(check_user)
        if check_user:
            return jsonify({'message': 'User already Registered', "email": check_user.email}), 409

        user = User(
            email=data['email'],
            firstname=data['firstname'],
            lastname=data['lastname']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User Registered Successfully', "email": user.email}), 201
     
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400  
    except Exception as e:
        return jsonify({'message': str(e)}), 500

def list_books_controller():
    books = Book.query.filter_by(book_available=True).all()
    book_list = [{'id': book.id, 'title': book.title, 'author': book.author, 'publisher': book.publisher, 'category': book.category} for book in books]
    return jsonify(book_list), 200


def get_book_controller(id):
    try:
        # Attempt to retrieve the book by its ID
        book = Book.query.get(id)
        
        # Handle case where the book is not found
        if not book:
            return jsonify({
                'error': 'Book not found',
                'message': f'No book found with id: {id}'
            }), 404

        # If found, return the book details
        return jsonify({
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'publisher': book.publisher,
            'category': book.category
        }), 200

    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


def borrow_book_controller():
    try:
        data = request.json
        user_id = data.get('user_id')
        days = data.get('days')
        book_id = data.get('book_id')

        print(book_id)
        
        if not user_id or not days:
            return jsonify({"error": "User ID and days are required."}), 400
        
        # Find the book by ID
        book = Book.query.get(book_id)
        if not book:
            return jsonify({"error": "Book not found."}), 404
        
        if not book.book_available:
            return jsonify({"error": "Book is not available for borrowing."}), 400

        # Create a new borrow record
        return_date = datetime.utcnow() + timedelta(days=days)
        borrow = Borrow(
            user_id=user_id,
            book_id=book_id,
            days=days,
            date_borrowed=datetime.utcnow(),
            date_returned=return_date
        )
        
        # Save the borrow record and update book availability
        try:
            db.session.add(borrow)
            book.book_available = False
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

        # Serialize the response
        borrow_schema = BorrowSchema()
        result = borrow_schema.dump(borrow)
        
        return jsonify({"Borrow ": result, "message": "Borrowed Successfully"}), 201

    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500


def return_book_controller(id):
    schema = ReturnBookSchema()
    try:
        data = schema.load(request.json)
        book = Book.query.get_or_404(id)

        borrow = Borrow.query.filter_by(book_id=book.id, user_id=data['user_id']).first()
        if not borrow:
            return jsonify({'message': 'User did not borrow book'}), 400

        book.book_available = True
        db.session.delete(borrow)
        db.session.commit()

        return jsonify({'message': 'Book returned successfully'}), 200
    
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@staticmethod
# Controller for getting books by category
def get_books_by_category(category):
    try:
        category = category.lower()
        books = Book.query.filter_by(category=category).all()
        if not books:
            return jsonify({'message': 'No books found for this category'}), 404
        books_list = [{'title': book.title, 'author': book.author, 'publisher': book.publisher, 'category': book.category} for book in books]
        return jsonify(books_list), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@staticmethod
# Controller for getting books by publisher
def get_books_by_publisher(publisher):
    try:
        publisher = publisher.lower()
        books = Book.query.filter_by(publisher=publisher).all()
        if not books:
            return jsonify({'message': 'No books found for this publisher'}), 404
        books_list = [{'title': book.title, 'author': book.author, 'publisher': book.publisher, 'category': book.category} for book in books]
        return jsonify(books_list), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500