from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Bookstore, Book, Category, Seller

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


# Create dummy seller
seller = Seller(name="Yoko", email="yoko@servletgarden.com")
                 
session.add(seller)
session.commit()

# Create ctegories
computer = Category(name="Computer")
session.add(computer)
session.commit()
children = Category(name="Children")
session.add(children)
session.commit()
nonfiction = Category(name="Nonfiction")
session.add(nonfiction)
session.commit()
fiction = Category(name="Fiction")
session.add(fiction)
session.commit()

# Books for Unlikely Story Books
bookstore1 = Bookstore(seller=seller, name="Unlikely Story Books")

session.add(bookstore1)
session.commit()

book1 = Book(seller=seller,
             title="Python for More Than Dummies",
             description="Everyone can get started fairly easily.",
             price="$14.99",
             category=computer,
             bookstore=bookstore1)

session.add(book1)
session.commit()

book2 = Book(seller=seller,
             title="Statistics Explained in Kid's Terms",
             description="Fundamentals of statics are explained with examples.",
             price="$20.00",
             category=computer,
             bookstore=bookstore1)

session.add(book2)
session.commit()

book3 = Book(seller=seller,
             title="Spelling Bee Ninja",
             description="How to beat them at spelling bees like a ninja.",
             price="$7.50",
             category=children,
             bookstore=bookstore1)

session.add(book3)
session.commit()

book4 = Book(seller=seller,
             title="Cooking for Eat Outers",
             description="Extremely easy cooking for normally eat outers.",
             price="$23.49",
             category=nonfiction,
             bookstore=bookstore1)

session.add(book4)
session.commit()

book5 = Book(seller=seller,
             title="The Diary of a Web Developer",
             description="A diary of a man who mistakenly became a web developer.",
             price="$15.99",
             category=nonfiction,
             bookstore=bookstore1)

session.add(book5)
session.commit()


# Books for Fantastic World Press
bookstore2 = Bookstore(seller=seller, name="Fantastic World Press")

session.add(bookstore2)
session.commit()

book1 = Book(seller=seller,
             title="Trotting Zombies",
             description="""The night before a new moon, watch your behind.
             Zombies are...""",
             price="$5.99",
             category=fiction,
             bookstore=bookstore2)

session.add(book1)
session.commit()

book2 = Book(seller=seller,
             title="James Smith and the Woods of Secrets",
             description="""James found himself in a strange woods filled with
             dense fog. His body was aching all over...""",
             price="$5.99",
             category=fiction,
             bookstore=bookstore2)

session.add(book2)
session.commit()

book3 = Book(seller=seller,
             title="A Bug Lived in Emily's Laptop",
             description="""A little Emily loved to play with a bug living in
             her laptop. One day, the bug the Goo told her...""",
             price="$5.99",
             category=children,
             bookstore=bookstore2)

session.add(book3)
session.commit()

book4 = Book(seller=seller,
             title="Master Whoknows",
             description="""Kung Fu master, Whoknows, decided to travel space
             and time using Anywhere Door, which was a dusty family treasure
             saved in a half broken shed...""",
             price="$5.99",
             category=fiction,
             bookstore=bookstore2)

session.add(book4)
session.commit()
