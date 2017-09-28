from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item

# Instantiate Flask app
app = Flask(__name__)

# Boot up and conenct to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#########################################

# Show all categories (main page)
@app.route('/')
@app.route('/catalog/')
def showCategories():
	categories = session.query(Category)
	return render_template('categories.html', categories=categories)

#########################################

# Show items of category
@app.route('/catalog/<category_name>/')
@app.route('/catalog/<category_name>/items/')
def showItems(category_name):
	items = session.query(Item).filter_by(category_name=category_name).all()
	for item in items:
		print item.name
		print category_name
	return render_template('items.html', category_name=category_name, items=items)


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)