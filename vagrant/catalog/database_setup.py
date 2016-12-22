from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
 

Base = declarative_base()


class Seller(Base):
    """Seller model definition.
    A seller has a bookstore and books.
    """
    __tablename__ = 'seller'
   
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


class Bookstore(Base):
    __tablename__ = 'bookstore'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    seller_id = Column(Integer,ForeignKey('seller.id'))
    seller = relationship(Seller)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'name'         : self.name,
       }
 

class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))
    price = Column(String(8))
    category = Column(String(250))
    bookstore_id = Column(Integer,ForeignKey('bookstore.id'))
    bookstore = relationship(Bookstore)
    seller_id = Column(Integer,ForeignKey('seller.id'))
    seller = relationship(Seller)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'           : self.id,
           'title'        : self.title,
           'description'  : self.description,
           'price'        : self.price,
           'category'     : self.category,
       }


engine = create_engine('postgresql:///catalog')
 

Base.metadata.create_all(engine)
