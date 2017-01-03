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

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'email'        : self.email,
           'picture'      : self.picture,
       }


class Category(Base):
    """Category model definition
    A category has an id and name.
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer,ForeignKey('book_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
           'user'         : self.user.email
       }
 

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    author = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer,ForeignKey('book_user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'title'        : self.title,
           'author'       : self.author if self.author else '',
           'description'  : self.description if self.description else '',
           'price'        : self.price if self.price else '$ 0.00',
           'category'     : self.category.name if self.category else '',
           'user'         : self.user.email
       }


engine = create_engine('postgresql:///catalog')
 

Base.metadata.create_all(engine)
