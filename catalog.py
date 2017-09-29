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
# HOME PAGE

# Show all categories (main page)
@app.route('/')
@app.route('/catalog/')
def showCategories():
	categories = session.query(Category).all()
	return render_template('categories.html', categories=categories)

#########################################
# CATEGORY ITEMS PAGE

# Show items of category
@app.route('/catalog/<category_name>/')
def showItems(category_name):
	items = session.query(Item).filter_by(category_name=category_name).all()
	for item in items:
		print item.name
		print category_name
	return render_template('items.html', category_name=category_name, items=items)

# Create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
	if request.method == 'POST':
		newItem = Item(user_id=1, category_name=request.form['category'], name=request.form['itemName'], description=request.form['itemDescription'])
		session.add(newItem)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('newItem.html')


#########################################
# ITEM PAGE

# Show item info
@app.route('/catalog/<category_name>/items/<item_name>/')
def showItemInfo(category_name, item_name):
	item = session.query(Item).filter_by(category_name=category_name, name=item_name).one()
	return render_template('itemInfo.html', item=item)


if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
