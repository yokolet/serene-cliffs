import httplib2
import json
import random
import requests
import string
from database_setup import Base, User, Category, Book
from flask import Flask, flash, jsonify, make_response
from flask import redirect, render_template, request, url_for
from flask import session as login_session
from flask_restless import APIManager
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


#  Creates flask app
app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
FB_APP_ID = json.loads(
    open('fb_client_secrets.json', 'r').read())['web']['app_id']

#  Connects to PostgreSQL and creates a database session
engine = create_engine('postgresql:///catalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

apimanager = APIManager(app, session=session)

apimanager.create_api(User,
                      methods=['GET'],
                      include_columns=['id', 'name', 'email', 'picture'])
apimanager.create_api(Category,
                      methods=['GET'],
                      include_columns=['id', 'name'])
apimanager.create_api(Book, methods=['GET'])


@app.route('/login')
def showLogin():
    """Renders login page"""
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',
                           state=state,
                           fb_app_id=FB_APP_ID,
                           client_id=CLIENT_ID,
                           on_login=True)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Connects to Facebook for login.
    After logging in, the catalog page will show up."""
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
    """Disconnect a user from Facebook"""
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    print('username ' + login_session['username'])
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
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
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Functions
def createUser(login_session):
    """Helper function to create a user"""
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Helper function to find a user by user_id"""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Helper function to get a user by email"""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    """Logout a user"""
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        elif login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategoriesBooks'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategoriesBooks'))


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
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    if not category:
        flash("No category found (id=%s)" % category_id)
        return redirect(url_for('showCategoriesBooks'))

    books = session.query(Book).filter_by(category_id=category_id).order_by(Book.id.desc())
    logged_in = True if 'username' in login_session else False
    return render_template('book_catalog.html',
                           logged_in=logged_in,
                           categories=categories,
                           category_name=category.name if category else None,
                           number_of_books=books.count(),
                           books=books)


@app.route('/book_catalog/books/<int:book_id>')
def showBookDescription(book_id):
    """Renders a description of specified book id"""
    book = session.query(Book).filter_by(id=book_id).one_or_none()
    if not book:
        flash("No book found (id=%s)" % book_id)
        return redirect(url_for('showCategoriesBooks'))

    logged_in = login_session['username'] if 'username' in login_session else None
    return render_template('book_description.html',
                           logged_in=logged_in,
                           book=book)


def bookData(request):
    """Helper function to get form data to create a dict.
    If title is not given, adds an error to the dict.
    """
    if request.form.get('category'):
        category = session.query(Category).filter_by(
            name=request.form.get('category')).one_or_none()
    else:
        category = None
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
    """Helper function to create a data to render."""
    if not data['author']: data['author']=''
    if not data['price']: data['price']='$ 0.00'
    if not data['description']: data['description']=''
    return data


def getBookInstance(data):
    """Helper function to create a book instance."""
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
            book = session.query(Book).filter_by(id=book_id).one_or_none()
            if book and (book.user_id == login_session['user_id']):
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
        book = session.query(Book).filter_by(id=book_id).one_or_none()
        categories = session.query(Category).all()
        if book:
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
                               data=data if data else {})


@app.route('/book_catalog/books/<int:book_id>/delete', methods=['GET', 'POST'])
def deleteBook(book_id):
    """Poses a book deletion and deletes the book"""
    logged_in = login_session['username'] if 'username' in login_session else None
    if not logged_in:
        flash('Login to delete a book you have created.')
        return redirect(url_for('showCategoriesBooks'))

    book = session.query(Book).filter_by(id=book_id).one_or_none()
    if book and (request.method == 'POST'):
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
    app.run(host='0.0.0.0', port=5000)
