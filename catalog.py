from flask import Flask, render_template, request, redirect, url_for, flash, make_response
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

# Boot up and conenct to database
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Retrieve client information from client_secrets.json
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App"

#########################################
# ANTI-FORGERY TOKEN

# Google+ login page
@app.route('/login')
def showLogin():
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	return render_template('login.html', STATE=state)

#########################################
# GCONNECT / DISCONNECT

# Gconnect route
@app.route('/gconnect', methods=['POST'])
def gconnect():
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
	stored_gplus_id = login_session.get('gplus_id')
	if stored_access_token is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected', 200))
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use
	login_session['access_token'] = access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['username'] = data['name']
	login_session['email'] = data['email']
	login_session['picture'] = data['picture']

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output

# Route for disconnect (logout)
@app.route('/gdisconnect')
def gdisconnect():
	access_token = login_session.get('access_token')
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
		return response

	# If other response, return error statement
	else:
		response = make_response(json.dumps('Failed to revoke token for given user.'), 400)
		response.headers['Content-Type'] = 'application/json'
		return response

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
