from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 

Base = declarative_base()


class User(Base):
    """User model definition.
    A user has an id, name, email and optional picture url.
    """
    __tablename__ = 'book_user'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    """Category model definition
    A category has an id and name.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('book_user.id', ondelete='CASCADE'))
    user = relationship(User, backref='category', passive_deletes=True)


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    author = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id', ondelete='CASCADE'))
    category = relationship(Category, backref='book', passive_deletes=True)
    user_id = Column(Integer, ForeignKey('book_user.id', ondelete='CASCADE'))
    user = relationship(User, backref='book', passive_deletes=True)


engine = create_engine('postgresql:///catalog')
 

Base.metadata.create_all(engine)
