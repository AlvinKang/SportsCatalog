from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
	"""Table for users"""
	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)


class Category(Base):
	"""Table for categories"""
	__tablename__ = 'category'

	name = Column(String(250), primary_key=True, nullable=False)


class Item(Base):
	"""Table for items"""
	__tablename__ = 'item'

	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('user.id'))
	category_name = Column(String(250), ForeignKey('category.name'))
	name = Column(String(250), nullable=False)
	description = Column(String(250), nullable=False)


engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)
