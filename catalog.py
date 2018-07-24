from flask import (Flask, render_template,
                   request, redirect, url_for, flash, make_response, jsonify)
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
from datetime import timedelta
import random
import string
import httplib2
import json
import requests

# Instantiate Flask app
app = Flask(__name__)
app.secret_key = 'ed67095a42efbb9c86ead967e1d4cf0d'

# Boot up and connect to database
db_string = "postgres://catalog:catalog@localhost/catalog_app"
engine = create_engine(db_string)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Retrieve client information from client_secrets.json
f = open('/var/www/CatalogApp/CatalogApp/client_secrets.json', 'r').read()
CLIENT_ID = json.loads(f)['web']['client_id']
APPLICATION_NAME = "Catalog App"

#########################################
# ANTI-FORGERY TOKEN


@app.route('/login')
def showLogin():
    global login_session
    # If user is already logged in redirect to main page
    if 'username' in login_session:
        redirect('/')
    state_string = string.ascii_uppercase + string.digits
    state = ''.join(random.choice(state_string) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

#########################################
# SET SESSION TIMEOUT


@app.before_request
def set_session_timeout():
    global login_session
    login_session.permanent = True
    # User's session gets deleted after 5 minutes of inactivity
    app.permanent_session_lifetime = timedelta(minutes=5)


#########################################
# GCONNECT / DISCONNECT


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
        oauth_flow = flow_from_clientsecrets('/var/www/CatalogApp/CatalogApp/client_secrets.json', scope='')

        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)

    except FlowExchangeError:
        error_msg = json.dumps('Failed to upgrade the authorization code.')
        response = make_response(error_msg, 401)
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
        error_msg = json.dumps("Token's user ID doesn't match given user ID.")
        response = make_response(error_msg, 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app
    if result['issued_to'] != CLIENT_ID:
        error_msg = json.dumps("Token's client ID does not match app's.")
        response = make_response(error_msg, 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    print "========================"
    print "This is my stored access token: %s" % stored_access_token
    print "========================"
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        error_msg = json.dumps('Current user is already connected')
        response = make_response(error_msg, 200)
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
    print ("This is the current user:\nId: %s\nName: %s\nEmail: %s\nToken: %s"
           %
           (str(user_id), login_session['username'], login_session['email'],
            login_session['access_token']))
    print "################################"

    # Format and return loading page
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' "style = "width: 300px; height: 300px; border-radius:
              150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;">
              '''
    flash("You are now logged in as %s" % login_session['username'])
    return output


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
        error_msg = json.dumps('Current user is not connected.')
        response = make_response(error_msg, 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Contact Google server
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
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
        output = ('''<meta http-equiv="refresh" content="3; url=%s" />
                  <h1 style="text-align: center; margin-top: 30%%;">
                  Sucessfully disconnected. Redirecting...</h1>'''
                  % url_for('showCategories'))
        return output

    # If other response, return error statement and provide link
    else:
        error_msg = json.dumps('Failed to revoke token for given user.')
        response = make_response(error_msg, 400)
        response.headers['Content-Type'] = 'application/json'
        return ('''<h3>Failed to revoke token for given user. Your token is expired.
                To log out, click <a href="%s">here</a>.</h3>
                '''
                % url_for('forceDisconnect'))

#########################################
# User helper functions


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
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


@app.route('/catalog/JSON/')
def catalogJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/catalog/<category_name>/JSON/')
def itemsJSON(category_name):
    items = session.query(Item).filter_by(category_name=category_name).all()
    return jsonify(CategoryItems=[i.serialize for i in items])


@app.route('/catalog/<category_name>/<item_name>/JSON/')
def itemInfoJSON(category_name, item_name):
    item = session.query(Item).filter_by(
                                         category_name=category_name,
                                         name=item_name).one()
    return jsonify(Item=item.serialize)

#########################################
# HOME PAGE


@app.route('/')
@app.route('/catalog/')
def showCategories():
    categories = session.query(Category).all()
    # If user not logged in, remove option to create new items
    if 'username' not in login_session:
        return render_template('publicCategories.html', categories=categories)
    else:
        print "Username is: %s" % login_session['username']
        return render_template('categories.html', categories=categories,
                               user_name=login_session['username'])

#########################################
# CATEGORY ITEMS PAGE


@app.route('/catalog/<category_name>/')
def showItems(category_name):
    # If the user tries to manually access a nonexisting page of a non-existing category
    # redirect back to the home page
    does_category_exist = session.query(Category).filter_by(name=category_name).scalar() is not None
    # print "DOES THIS CATEGORY EXIST? \t" + str(exists_check)

    if not does_category_exist:
        return redirect(url_for('showCategories'))

    items = session.query(Item).filter_by(category_name=category_name).all()
    users = [session.query(User).filter_by(id=i.user_id).one() for i in items]
    # If user not logged in, remove creator name and option to create new items
    if 'username' not in login_session:
        return render_template('publicItems.html',
                               category_name=category_name, items=items)
    else:
        return render_template('items.html', category_name=category_name,
                               items=items, users=users,
                               user_name=login_session['username'])


@app.route('/catalog/new/', methods=['GET', 'POST'])
def newItem():
    # Restrict access for logged in user only
    if 'username' not in login_session:
        return redirect('/')
    if request.method == 'POST':
        newItem = Item(user_id=login_session['user_id'],
                       category_name=request.form['category'],
                       name=request.form['itemName'],
                       description=request.form['itemDescription'])
        entries = session.query(Item).filter_by(name=newItem.name,
                                                category_name=newItem
                                                .category_name).all()
        # If the new item is a duplicate entry (same name and category)
        # send alert and redirect
        if len(entries) > 0:
            return ('''<script> function myFunction() {
                    alert('This is a duplicate item.');}
                    </script><body onload='myFunction()'>
                    <meta http-equiv='refresh' content='1;url=/catalog/%s/'/>
                    ''' % (newItem.category_name))
        session.add(newItem)
        flash("Your item has been successfully created")
        session.commit()
        return redirect(url_for('showCategories'))
    else:
        return render_template('newItem.html',
                               user_name=login_session['username'])


#########################################
# ITEM PAGE


@app.route('/catalog/<category_name>/<item_name>/')
def showItemInfo(category_name, item_name):
    try:
        item = session.query(Item).filter_by(category_name=category_name,
                                             name=item_name).one()
    except:
        print "item doesn't exist!"
        # If the item doesn't exist return back to category
        return redirect(showItems(category_name))

    # Edit/Delete options only shown to item's creator
    creator = getUserInfo(item.user_id)
    logged_in = 'username' in login_session
    if not logged_in:
        return render_template('publicItemInfo.html', item=item)
    else:
        is_creator = creator.id == login_session['user_id']
        return render_template('itemInfo.html', item=item,
                               user_name=login_session['username'],
                               is_creator=is_creator)


@app.route('/catalog/<category_name>/<item_name>/edit/',
           methods=['GET', 'POST'])
def editItemInfo(category_name, item_name):
    # Restrict access to logged in user
    if 'username' not in login_session:
        return redirect('/')

    editedItem = session.query(Item).filter_by(category_name=category_name,
                                               name=item_name).one()

    # Restrict access to creator, show alert if user tries to manually access
    if editedItem.user_id != login_session['user_id']:
        return ('''<script>function myFunction() {
                alert('You are not authorized to edit this item.');}</script>
                <body onload='myFunction()'>
                <meta http-equiv='refresh'
                content='1;url=/catalog/%s/%s/' />'''
                % (category_name, item_name))

    if request.method == 'POST':
        if request.form['itemName']:
            # If the name of the item is changed, check database for duplicate
            if editedItem.name != request.form['itemName']:
                entries = session.query(Item) \
                          .filter_by(name=request.form['itemName'],
                                     category_name=editedItem.category_name) \
                          .all()

                # If duplicate (same name and category name, flash error and
                # redirect
                if len(entries) > 0:
                    return ('''<script> function myFunction() {
                            alert('This is a duplicate item.');}
                            </script><body onload='myFunction()'>
                            <meta http-equiv='refresh'
                            content='1;url=/catalog/%s/'/>'''
                            % (editedItem.category_name))

            editedItem.name = request.form['itemName']

        if request.form['itemDescription']:
            editedItem.description = request.form['itemDescription']

        session.add(editedItem)
        flash("Your item has been successfully edited")
        session.commit()
        return redirect(url_for('showItems', category_name=category_name))
    else:
        return render_template('editItem.html', category_name=category_name,
                               item=editedItem,
                               user_name=login_session['username'])


@app.route('/catalog/<category_name>/<item_name>/delete/',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_name):
    # Restrict access to logged in user
    if 'username' not in login_session:
        return redirect('/')

    deletedItem = session.query(Item).filter_by(category_name=category_name,
                                                name=item_name).one()

    # Restrict access to creator, show alert if user tries to manually access
    if deletedItem.user_id != login_session['user_id']:
        return ('''<script>function myFunction() {
                alert('You are not authorized to delete this item.');}</script>
                <body onload='myFunction()'>
                <meta http-equiv='refresh'
                content='1;url=/catalog/%s/%s/' />'''
                % (category_name, item_name))

    if request.method == 'POST':
        session.delete(deletedItem)
        flash("Your item has been successfully deleted")
        session.commit()
        return redirect(url_for('showItems', category_name=category_name))
    else:
        return render_template('deleteItem.html', item=deletedItem,
                               user_name=login_session['username'])

#########################################
# Debug: force logout when gdisconnect fails to revoke


@app.route('/forcedc/')
def forceDisconnect():
    # If user is not already logged in, just redirect to main page
    if 'username' not in login_session:
        return redirect('/')
    access_token = login_session.get('access_token')

    # If user is not logged in
    if access_token is None:
        print 'Access token is none'
        error_msg = json.dumps('Current user is not connected.')
        response = make_response(error_msg, 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Delete session user information
    del login_session['access_token']
    del login_session['gplus_id']
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    error_msg = json.dumps('Successfully disconnected.')
    response = make_response(error_msg, 200)
    response.headers['Content-Type'] = 'application/json'
    output = ('''<meta http-equiv="refresh" content="3; url=%s" /><h1
              style="text-align: center; margin-top: 30%%;">Sucessfully
              disconnected. Redirecting...</h1>'''
              % url_for('showCategories'))

    return output


if __name__ == '__main__':
    app.debug = True
    # app.secret_key = 'ed67095a42efbb9c86ead967e1d4cf0d'
    # app.run(host='0.0.0.0', port=5000)
    app.run()