from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    """Table for users"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


class Category(Base):
    """Table for categories"""
    __tablename__ = 'category'

    name = Column(String(250), primary_key=True, nullable=False)

    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            'name': self.name
        }


class Item(Base):
    """Table for items"""
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)
    category_name = Column(String(250), ForeignKey('category.name'))
    category = relationship(Category)
    name = Column(String(250), nullable=False)
    description = Column(String, nullable=False)

    @property
    def serialize(self):
        '''Return object data in easily serializeable format'''
        return {
            'name': self.name,
            'id': self.id,
            'category_name': self.category_name,
            'description': self.description
        }

if __name__ == '__main__':
    db_string = "postgres://catalog:catalog@localhost/catalog_app"
    engine = create_engine(db_string)
    Base.metadata.create_all(engine)