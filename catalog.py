from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests

# Instantiate Flask app
app = Flask(__name__)

# Boot up and connect to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Retrieve client information from client_secrets.json
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"


#########################################
# ANTI-FORGERY TOKEN

# Google+ login page
@app.route('/login')
def showLogin():
	global login_session
	# If user is already logged in redirect to main page
	if 'username' in login_session:
		redirect('/')
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

#########################################
# GCONNECT / DISCONNECT

# Gconnect route
@app.route('/gconnect', methods=['POST'])
def gconnect():
	global login_session
	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	# Obtain authorization code
	code = request.data

	try:
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)

	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)

	# Submit request, parse response
	h = httplib2.Http()
	response = h.request(url, 'GET')[1]
	str_response = response.decode('utf-8')
	result = json.loads(str_response)

	# If there was an error in the access token info, abort
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_access_token = login_session.get('access_token')
	print "========================"
	print "This is my stored access token: %s" % stored_access_token
	print "========================"
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected', 200))
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use
	login_session['access_token'] = access_token
	print "========================"
	print "This is my NEW access token: %s" % login_session.get('access_token')
	print "========================"
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['email'] = data['email']
	login_session['picture'] = data['picture']

	# See if user exists, if it doesnt make a new one
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	# Debug
	print "################################"
	print "This is the current user:\nId: %s\nName: %s\nEmail: %s\nToken: %s" % (str(user_id), login_session['username'], login_session['email'], login_session['access_token'])
	print "################################"
	# users = session.query(User).all()
	# for u in users:
	# 	print (u.id, u.name)

	# Format and return loading page
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px; border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output

# Route for disconnect (logout)
@app.route('/logout')
@app.route('/gdisconnect')
def gdisconnect():
	# If user is not already logged in, just redirect to main page
	if 'username' not in login_session:
		return redirect('/')
	access_token = login_session.get('access_token')
	print "=========LOGOUT========="
	print "My access token is: %s" % access_token
	print "=========LOGOUT========="
	# If user is not logged in
	if access_token is None:
		print 'Access token is none'
		response = make_response(json.dumps('Current user is not connected.', 401))
		response.headers['Content-Type'] = 'application/json'
		return response

	# Contact Google server
	url = ('https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token'])
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]

	# If response is 200, proceed with logging out
	if result['status'] == '200':
		# Delete session user information
		del login_session['access_token']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
		del login_session['picture']
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		output = '<meta http-equiv="refresh" content="3; url=%s" />Sucessfully disconnected. Redirecting...' % url_for('showCategories')
		return output

	# If other response, return error statement
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response

#########################################
# User helper functions

def createUser(login_session):
	newUser = User(name=login_session['username'], email=login_session['email'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email=login_session['email']).first()
	return user.id

def getUserInfo(user_id):
	user = session.query(User).filter_by(id=user_id).one()
	return user

def getUserID(email):
	try:
		user = session.query(User).filter_by(email=email).one()
		return user.id
	except:
		return None

#########################################
# API-JSON endpoints

# Categories
@app.route('/catalog/JSON/')
def catalogJSON():
	categories = session.query(Category).all()
	return jsonify(Categories=[i.serialize for i in categories])

# Items of Category
@app.route('/catalog/<category_name>/JSON/')
def itemsJSON(category_name):
	items = session.query(Item).filter_by(category_name=category_name).all()
	return jsonify(CategoryItems=[i.serialize for i in items])

# Item
@app.route('/catalog/<category_name>/<item_name>/JSON/')
def itemInfoJSON(category_name, item_name):
	item = session.query(Item).filter_by(category_name=category_name, name=item_name).one()
	return jsonify(Item=item.serialize)

#########################################
# HOME PAGE

# Show all categories (main page)
@app.route('/')
@app.route('/catalog/')
def showCategories():
	categories = session.query(Category).all()
	# If user not logged in, remove option to create new items
	if 'username' not in login_session:
		return render_template('publicCategories.html', categories=categories)
	else:
		print "Username is: %s" % login_session['username']
		return render_template('categories.html', categories=categories,user_name=login_session['username'])

#########################################
# CATEGORY ITEMS PAGE

# Show items of category
@app.route('/catalog/<category_name>/')
def showItems(category_name):
	items = session.query(Item).filter_by(category_name=category_name).all()
	users = [session.query(User).filter_by(id=i.user_id).one() for i in items]
	# If user not logged in, remove creator name and option to create new items
	if 'username' not in login_session:
		return render_template('publicItems.html', category_name=category_name, items=items)
	else:
		return render_template('items.html', category_name=category_name, items=items, users=users, user_name=login_session['username'])

# Create a new item
@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
	# Restrict access for logged in user only
	if 'username' not in login_session:
		return redirect('/')
	if request.method == 'POST':
		newItem = Item(user_id=login_session['user_id'], category_name=request.form['category'], name=request.form['itemName'], description=request.form['itemDescription'])
		entries = session.query(Item).filter_by(name=newItem.name, category_name=newItem.category_name).all()
		# If the new item is a duplicate entry (same name and category) send alert and redirect
		if len(entries) > 0:
			return "<script>function myFunction() {alert('This is a duplicate item. Please enter a different name or category name.');}</script><body onload='myFunction()'><meta http-equiv='refresh' content='1;url=/catalog/%s/' />" % (newItem.category_name)
		session.add(newItem)
		session.commit()
		return redirect(url_for('showCategories'))
	else:
		return render_template('newItem.html', user_name=login_session['username'])


#########################################
# ITEM PAGE

# Show item info
@app.route('/catalog/<category_name>/<item_name>/')
def showItemInfo(category_name, item_name):
	item = session.query(Item).filter_by(category_name=category_name, name=item_name).one()
	# Edit/Delete options only shown to item's creator
	creator = getUserInfo(item.user_id)
	if 'username' not in login_session or creator.id != login_session['user_id']:
		return render_template('publicItemInfo.html', item=item)
	else:
		return render_template('itemInfo.html', item=item, user_name=login_session['username'])

# Edit item info
@app.route('/catalog/<category_name>/<item_name>/edit/', methods=['GET', 'POST'])
def editItemInfo(category_name, item_name):
	# Restrict access to logged in user
	if 'username' not in login_session:
		return redirect('/')

	editedItem = session.query(Item).filter_by(category_name=category_name, name=item_name).one()

	# Restrict access to creator, show alert if user tries to manually access
	if editedItem.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to edit this item. Please create your own item in order to edit.');}</script><body onload='myFunction()'><meta http-equiv='refresh' content='1;url=/catalog/%s/%s/' />" % (category_name, item_name)

	if request.method == 'POST':
		if request.form['itemName']:
			entries = session.query(Item).filter_by(name=request.form['itemName'], category_name=editedItem.category_name).all()

			# If duplicate (same name and category name, show alert and redirect
			if len(entries) > 0:
				return "<script>function myFunction() {alert('This is a duplicate item. Please enter a different name or category name.');}</script><body onload='myFunction()'><meta http-equiv='refresh' content='1;url=/catalog/%s/' />" % (editedItem.category_name)

			editedItem.name = request.form['itemName']

		if request.form['itemDescription']:
			editedItem.description = request.form['itemDescription']

		session.add(editedItem)
		session.commit()
		return redirect(url_for('showItems', category_name=category_name))
	else:
		return render_template('editItem.html', category_name=category_name, item=editedItem, user_name=login_session['username'])

# Delete item
@app.route('/catalog/<category_name>/<item_name>/delete/', methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
	# Restrict access to logged in user
	if 'username' not in login_session:
		return redirect('/')

	deletedItem = session.query(Item).filter_by(category_name=category_name, name=item_name).one()

	# Restrict access to creator, show alert if user tries to manually access
	if deletedItem.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authorized to delete this item. Please create your own item in order to delete.');}</script><body onload='myFunction()'><meta http-equiv='refresh' content='1;url=/catalog/%s/%s/' />" % (category_name, item_name)

	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		return redirect(url_for('showItems', category_name=category_name))
	else:
		return render_template('deleteItem.html', item=deletedItem, user_name=login_session['username'])

#########################################
# Debug

# Force logout / disconnect user when gdisconnect fails to revoke
@app.route('/forcedc/')
def forceDisconnect():
	# If user is not already logged in, just redirect to main page
	if 'username' not in login_session:
		return redirect('/')
	access_token = login_session.get('access_token')

	# If user is not logged in
	if access_token is None:
		print 'Access token is none'
		response = make_response(json.dumps('Current user is not connected.', 401))
		response.headers['Content-Type'] = 'application/json'
		return response

	# Delete session user information
	del login_session['access_token']
	del login_session['gplus_id']
	del login_session['username']
	del login_session['email']
	del login_session['picture']
	response = make_response(json.dumps('Successfully disconnected.'), 200)
	response.headers['Content-Type'] = 'application/json'
	output = '<meta http-equiv="refresh" content="3; url=%s" />Sucessfully disconnected. Redirecting...' % url_for('showCategories')
	return output

if __name__ == '__main__':
	app.debug = True
	app.secret_key = 'ed67095a42efbb9c86ead967e1d4cf0d'
	app.run(host='0.0.0.0', port=5000)
