from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqllite:///catalog.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create dummy user
user1 = User(name="Heather Weber", email="heatherweber1983@gmail.com")
session.add(user1)
session.commit()

# Create category
category1 = Category(name="Baseball")
session.add(category1)
session.commit()