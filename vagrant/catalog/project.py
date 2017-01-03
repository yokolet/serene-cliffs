import httplib2
import json
import random
import requests
import string
from database_setup import Base, User, Category, Book
from flask import Flask, flash, jsonify, make_response
from flask import redirect, render_template, request, url_for
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


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


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state=state, on_login=True)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    print('username ' + login_session['username'])
    return "you have been logged out"


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['credentials']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategoriesBooks'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCtegoriesBooks'))


@app.route('/')
@app.route('/book_catalog')
def showCategoriesBooks():
    """Renders all categories and books"""
    categories = session.query(Category).all()
    books = session.query(Book).order_by(Book.id.desc()).limit(10)
    logged_in = True if 'username' in login_session else False
    return render_template('book_catalog.html',
                           logged_in=logged_in,
                           categories=categories,
                           category_name='New',
                           books=books)


@app.route('/book_catalog/categories/<int:category_id>/books')
def showBooksCategory(category_id):
    """Renders all books of a specified category id"""
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    books = session.query(Book).filter_by(category_id=category_id).order_by(Book.id.desc())
    logged_in = True if 'username' in login_session else False
    return render_template('book_catalog.html',
                           logged_in=logged_in,
                           categories=categories,
                           category_name=category.name,
                           number_of_books=books.count(),
                           books=books)


@app.route('/book_catalog/books/<int:book_id>')
def showBookDescription(book_id):
    """Renders a description of specified book id"""
    book = session.query(Book).filter_by(id=book_id).one()
    logged_in = login_session['username'] if 'username' in login_session else None
    return render_template('book_description.html',
                           logged_in=logged_in,
                           book=book)


def bookData(request):
    """Utilily function to get form data to create a dict.
    If title is not given, adds an error to the dict.
    """
    if request.form.get('category'):
        category = session.query(Category).filter_by(
            name=request.form.get('category')).one()
    else:
        categoty = None
    data = {
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'category': category,
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
    logged_in = True if 'username' in login_session else False
    if not logged_in:
        flash('Login to add a new book')
        return redirect(url_for('showCategoriesBooks'))

    if request.method == 'POST' and logged_in:
        data = bookData(request)
        if data.has_key('error'):
            categories = session.query(Category).all()
            data = bookDataCorrected(data)
            return render_template('book_edit.html',
                                   logged_in=logged_in,
                                   title='Add New Book',
                                   button='Create',
                                   categories=categories,
                                   data=data)
        else:
            book = getBookInstance(data)
            user = session.query(User).filter_by(id=login_session['user_id']).one()
            book.user_id = user.id
            session.add(book)
            session.commit()
            flash('New Book "%s" Successfully Created' % book.title)
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
                               logged_in=logged_in,
                               title='Add New Book',
                               button='Create',
                               categories=categories,
                               data=data)


@app.route('/book_catalog/books/<int:book_id>/edit', methods=['GET', 'POST'])
def editBook(book_id):
    """Renders a form and adds a new book"""
    logged_in = login_session['username'] if 'username' in login_session else None
    if not logged_in:
        flash('Login to edit a book you have created.')
        return redirect(url_for('showCategoriesBooks'))

    if request.method == 'POST':
        data = bookData(request)
        if data.has_key('error'):
            categories = session.query(Category).all()
            data = bookDataCorrected(data)
            return render_template('book_edit.html',
                                   logged_in=logged_in,
                                   title='Edit Book',
                                   button='Update',
                                   categories=categories,
                                   data=data)
        else:
            book = session.query(Book).filter_by(id=book_id).one()
            if book.user_id == login_session['user_id']:
                if 'title' in data: book.title = data['title']
                if 'author' in data: book.author = data['author']
                if 'description' in data: book.description = data['description']
                if 'price' in data: book.price = data['price']
                print(data['category'])
                if 'category' in data: book.category = data['category']
                session.add(book)
                session.commit()
                flash('Book "%s" Successfully Updated' % book.title)
            else:
                flash("%s doesn't have a permission to edit the book %s"
                      % (logged_in, book.title))
            return redirect(url_for('showCategoriesBooks'))
    else:
        book = session.query(Book).filter_by(id=book_id).one()
        categories = session.query(Category).all()
        data = {
            'title': book.title,
            'author': book.author if book.author else '',
            'category': book.category.name if book.category else '',
            'price': book.price if book.price else '$ 0.00',
            'description': book.description if book.description else ''
        }
        return render_template('book_edit.html',
                               logged_in=logged_in,
                               title='Edit Book',
                               button='Update',
                               categories=categories,
                               data=data)


@app.route('/book_catalog/books/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(book_id):
    """Poses a book deletion and deletes the book"""
    logged_in = login_session['username'] if 'username' in login_session else None
    if not logged_in:
        flash('Login to delete a book you have created.')
        return redirect(url_for('showCategoriesBooks'))

    book = session.query(Book).filter_by(id=book_id).one()
    if request.method == 'POST':
        if book.user_id == login_session['user_id']:
            session.delete(book)
            session.commit()
            flash('Book "%s" Successfully Deleted' % book.title)
        else:
            flash("%s doesn't have a permission to delete the book %s" % (logged_in, book.title))
        return redirect(url_for('showCategoriesBooks'))
    else:
        return render_template('book_delete.html',
                               logged_in=logged_in,
                               book=book)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
