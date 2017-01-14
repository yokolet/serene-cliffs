from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Book, Category, User
import json

engine = create_engine('postgresql:///catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Load seed data from JSON file
with open('seed_data.json') as data_file:
    seed_data = json.load(data_file)

# Create dummy user
user_data = seed_data['user'][0]
user = User(name=user_data['name'], email=user_data['email'])
session.add(user)
session.commit()

# Create ctegories
categories = {}
for cat_data in seed_data['category']:
    name = cat_data['name']
    c = Category(name=name, user=user)
    categories[name]=c
    session.add(c)

session.commit()

# Create books
for book_data in seed_data['book']:
    description = ' '.join(book_data['description'])
    b = Book(user=user,
             title=book_data['title'],
             author=book_data['author'] if 'author' in book_data else None,
             description=description,
             price=book_data['price'] if 'price' in book_data else '$0.00',
             category=categories[book_data['category']])
    session.add(b)

session.commit()
