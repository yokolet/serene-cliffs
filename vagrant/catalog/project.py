from flask import Flask, jsonify, render_template, request, redirect, url_for
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
    books = session.query(Book).order_by(Book.id.desc()).limit(10)
    return render_template('book_catalog.html',
                           categories=categories,
                           category_name='New',
                           books=books)

@app.route('/book_catalog/categories/<int:category_id>/books')
def showBooksCategory(category_id):
    """Renders all books of a specified category id"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    books = session.query(Book).filter_by(category_id=category_id).order_by(Book.id.desc())
    return render_template('book_catalog.html',
                           categories=categories,
                           category_name=category.name,
                           number_of_books=books.count(),
                           books=books)

@app.route('/book_catalog/books/<int:book_id>')
def showBookDescription(book_id):
    """Renders a description of specified book id"""
    book = session.query(Book).filter_by(id=book_id).one()
    return render_template('book_description.html',
                           book=book)

def bookData(request):
    """Utilily function to get form data to create a dict.
    If title is not given, adds an error to the dict.
    """
    data = {
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'category': request.form.get('category'),
        'price': request.form.get('price'),
        'description': request.form.get('description')
    }
    if not data['title']:
        data['error'] = 'Title should not be empty.'
    return data

def bookDataCorrected(data):
    if not data['author']: data['author']=''
    if not data['price']: data['price']='$ 0.00'
    if not data['description']: data['description']=''
    return data

def getBookInstance(data):
    book = Book(title=data['title'])
    if data['author']: book.author = data['author']
    if data['category']: book.category = data['category']
    if data['price']: book.price = data['price']
    if data['description']: book.description = data['description']
    return book

@app.route('/book_catalog/books/new', methods=['GET', 'POST'])
def newBook():
    """Renders a form and adds a new book"""
    if request.method == 'POST':
        data = bookData(request)
        if data.has_key('error'):
            categories = session.query(Category).all()
            data = bookDataCorrected(data)
            return render_template('book_edit.html',
                                   title='Add New Book',
                                   button='Create',
                                   categories=categories,
                                   data=data)
        else:
            book = getBookInstance(data)
            session.add(book)
            session.commit()
            return redirect(url_for('showCategoriesBooks'))
    else:
        categories = session.query(Category).all()
        data = {
            'author': '',
            'category': '',
            'price': '$ 0.00',
            'description': ''
        }
        return render_template('book_edit.html',
                               title='Add New Book',
                               button='Create',
                               categories=categories,
                               data=data)

@app.route('/book_catalog/books/<int:book_id>/edit', methods=['GET', 'POST'])
def editBook(book_id):
    """Renders a form and adds a new book"""
    if request.method == 'POST':
        data = bookData(request)
        if data.has_key('error'):
            categories = session.query(Category).all()
            data = bookDataCorrected(data)
            return render_template('book_edit.html',
                                   title='Edit Book',
                                   button='Update',
                                   categories=categories,
                                   data=data)
        else:
            book = getBookInstance(data)
            session.add(book)
            session.commit()
            return redirect(url_for('showCategoriesBooks'))
    else:
        book = session.query(Book).filter_by(id=book_id).one()
        categories = session.query(Category).all()
        data = {
            'title': book.title,
            'author': book.author if book.author else '',
            'category': book.category,
            'price': book.price if book.price else '$ 0.00',
            'description': book.description if book.description else ''
        }
        return render_template('book_edit.html',
                               title='Edit Book',
                               button='Update',
                               categories=categories,
                               data=data)

@app.route('/book_catalog/books/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(book_id):
    """Poses a book deletion and deletes the book"""
    book = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        session.delete(book)
        session.commit()
        return redirect(url_for('showCategoriesBooks'))
    else:
        return render_template('book_delete.html',
                               book=book)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
