from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string

# Instantiate Flask app
app = Flask(__name__)

# Boot up and conenct to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#########################################
# ANTI-FORGERY TOKEN
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return state

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
	# for item in items:
	# 	print item.name
	# 	print category_name
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
@app.route('/catalog/<category_name>/<item_name>/')
def showItemInfo(category_name, item_name):
	item = session.query(Item).filter_by(category_name=category_name, name=item_name).one()
	return render_template('itemInfo.html', item=item)

# Edit item info
@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def editItemInfo(category_name, item_name):
	editedItem = session.query(Item).filter_by(category_name=category_name, name=item_name).one()
	if request.method == 'POST':
		if request.form['itemName']:
			editedItem.name = request.form['itemName']
		if request.form['itemDescription']:
			editedItem.description = request.form['itemDescription']
		session.add(editedItem)
		session.commit()
		return redirect(url_for('showItems', category_name=category_name))
	else:
		return render_template('editItem.html', category_name=category_name, item=editedItem)

# Delete item
@app.route('/catalog/<category_name>/<item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
	deletedItem = session.query(Item).filter_by(category_name=category_name, name=item_name).one()
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		return redirect(url_for('showItems', category_name=category_name))
	else:
		return render_template('deleteItem.html', item=deletedItem)

if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'ed67095a42efbb9c86ead967e1d4cf0d'
	app.run(host='0.0.0.0', port=5000)
