from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Book, Category, User

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


# Create dummy user
user = User(name='Yoko', email='yoko@servletgarden.com')
                 
session.add(user)
session.commit()

# Create ctegories
computer = Category(name='Computer', user=user)
session.add(computer)
session.commit()
children = Category(name='Children', user=user)
session.add(children)
session.commit()
nonfiction = Category(name='Nonfiction', user=user)
session.add(nonfiction)
session.commit()
fiction = Category(name='Fiction', user=user)
session.add(fiction)
session.commit()

book1 = Book(user=user,
             title='Python for More Than Dummies',
             author='African Great Pythonians',
             description='Everyone can get started fairly easily.',
             price='$14.99',
             category=computer)

session.add(book1)
session.commit()

book2 = Book(user=user,
             title="Statistics Explained in Kid's Terms",
             author='World Statistics Education Team',
             description="""Fundamentals of statics are explained by the words
             even kids can understand.""",
             price='$20.00',
             category=computer)

session.add(book2)
session.commit()

book3 = Book(user=user,
             title='Spelling Bee Ninja',
             description='How to beat them at spelling bees like a ninja.',
             price='$7.50',
             category=children)

session.add(book3)
session.commit()

book4 = Book(user=user,
             title='Cooking for Eat Outers',
             author='Julia Doe',
             description='Extremely easy cooking for normally eat outers.',
             price='$23.49',
             category=nonfiction)

session.add(book4)
session.commit()

book5 = Book(user=user,
             title='The Diary of a Web Developer',
             author='anonymous',
             description='A diary of a man who mistakenly became a web developer.',
             price='$15.99',
             category=nonfiction)

session.add(book5)
session.commit()

book1 = Book(user=user,
             title='Trotting Zombies',
             author='Holy Johnson',
             description="""The night before a new moon, watch your behind.
             Zombies are...""",
             price='$5.99',
             category=fiction)

session.add(book1)
session.commit()

book2 = Book(user=user,
             title='James Smith and the Woods of Secrets',
             author='K. L., Rounding',
             description="""James found himself in strange woods filled with
             dense fog lying on his back. His body was aching all over...""",
             price='$5.99',
             category=fiction)

session.add(book2)
session.commit()

book3 = Book(user=user,
             title="A Bug Lived in Emily's Laptop",
             author='Star Skyler',
             description="""A little Emily loved to play with a bug living in
             her laptop. One day, the bug the Goo told her...""",
             price='$5.99',
             category=children)

session.add(book3)
session.commit()

book4 = Book(user=user,
             title='Master Whoknows',
             description="""Kung Fu master, Whoknows, decided to travel space
             and time using Anywhere Door, which was a dusty family treasure
             saved in a half broken shed...""",
             price='$5.99',
             category=fiction)

session.add(book4)
session.commit()
