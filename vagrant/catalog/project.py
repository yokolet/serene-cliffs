from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Book

#  Creates flask app
app = Flask(__name__)

#  Connects to PostgreSQL and creates a database session
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/book_catalog/books/JSON')
def bookCatalogJSON():
    """Returns all books in JSON format"""
    books = session.query(Book).all()
    return jsonify(books=[b.serialize for b in books])

@app.route('/book_catalog/categories/JSON')
def categoryJSON():
    """Returns all categories in JSON format"""
    categories = session.query(Category).all()
    return jsonify(categories=[b.serialize for b in categories])


@app.route('/book_catalog/categories/<int:category_id>/books/JSON')
def categoryBookJSON(category_id):
    """Returns all books of a specified category id in JSON format"""
    category= session.query(Category).filter_by(id=category_id).one()
    books = session.query(Book).filter_by(category_id=category_id).all()
    return jsonify(books=[b.serialize for b in books])


@app.route('/book_catalog/books/<int:book_id>/JSON')
def bookJSON(book_id):
    """Returns a book of a specified book id in JSON format"""
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=book.serialize)


@app.route('/')
@app.route('/book_catalog')
def showCategoriesBooks():
    """Renders all categories and books"""
    categories = session.query(Category).all()
    books = session.query(Book).all()
    return render_template('book_catalog.html',
                           categories=categories,
                           books=books)

@app.route('/book_catalog/categories/<int:category_id>/books')
def showBooksCategory(category_id):
    """Renders all books of a specified category id"""
    categories = session.query(Category).all()
    books = session.query(Book).filter_by(category_id=category_id)
    return render_template('book_catalog.html',
                           categories=categories,
                           books=books)

@app.route('/book_catalog/books/<int:book_id>')
def showBookDescription(book_id):
    """Renders a description of specified book id"""
    book = session.query(Book).filter_by(id=book_id).one()
    print(book.title)
    return render_template('book_description.html',
                           book=book)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
