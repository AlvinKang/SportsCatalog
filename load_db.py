from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine("sqllite:///catalog.db")

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create user
user1 = User(name="Heather Weber", email="heatherweber1983@gmail.com")
session.add(user1)
session.commit()

# Create baseball category
category1 = Category(name="Baseball")
session.add(category1)
session.commit()

# Create item for baseball
item1 = Item(user_id=1, category_name="Baseball", name="Youth Bat",
	description="Youth Bat a good option for players who value the traditional feel of a one-piece bat and the classic ping off a durable aluminum barrel.")
session.add(item1)
session.commit()