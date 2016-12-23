from flask import Flask, jsonify, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Seller, Bookstore, Category, Book

#  Creates flask app
app = Flask(__name__)

#  Connects to PostgreSQL and creates a database session
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/bookstores/JSON')
def bookstoresJSON():
    bookstores = session.query(Bookstore).all()
    return jsonify(booksotre=[b.serialize for b in bookstores])


@app.route('/bookstores/<int:bookstore_id>/books/JSON')
def bookstoreBookJSON(bookstore_id):
    bookstore= session.query(Bookstore).filter_by(id=bookstore_id).one()
    books = session.query(Book).filter_by(bookstore_id=bookstore_id).all()
    return jsonify(books=[b.serialize for b in books])


@app.route('/bookstores/<int:bookstore_id>/books/<int:book_id>/JSON')
def booksJSON(bookstore_id, book_id):
    book = session.query(Book).filter_by(id=book_id).one()
    return jsonify(book=book.serialize)


@app.route('/')
@app.route('/bookstores')
def showBookstores():
    bookstores = session.query(Bookstore).all()
    categories = session.query(Category).all()
    books = session.query(Book).all()
    return render_template('bookstores.html',
                           bookstores=bookstores,
                           categories=categories,
                           books=books)

@app.route('/bookstores/categories/<int:category_id>')
def showCategory(category_id):
    categories = session.query(Category).all()
    books = session.query(Book).filter_by(category_id=category_id)
    bookstores = {b.bookstore: 1 for b in books}.keys()
    return render_template('bookstores.html',
                           bookstores=bookstores,
                           categories=categories,
                           books=books)

@app.route('/bookstores/categories/<int:category_id>/books/<int:book_id>')
def showDescription(category_id, book_id):
    categories = session.query(Category).all()
    if category_id:
        books = session.query(Book).filter_by(category_id=category_id)
    else:
        books = session.query(Book).all()
    bookstores = {b.bookstore: 1 for b in books}.keys()
    book = filter(lambda b: b.id == book_id, books)[0]
    return render_template('bookstores.html',
                           bookstores=bookstores,
                           categories=categories,
                           books=books,
                           book=book)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
