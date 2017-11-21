# CatalogApp
This is a project submission for Udacity's Full Stack Nanodegree program. The Python code uses [**Flask**](http://flask.pocoo.org/), a Python microframework, to deploy a RESTful Sports Catalog web application implementing Google's OAuth authentication. Upon successful authentication (Google login), the user will be able to create, update, and delete his own items on the catalog, which stores the information on a back-end database.

## Getting Started
**IMPORTANT:** It is expected that you have the setup stipulated by Udacity, such as the correct Vagrant configuration file for VirtualBox with all the dependencies needed to run the app.

### Running the CatalogApp
Here are the steps to follow to get the app up and running:
1. Download the contents in this repository as a ZIP and unzip into your Vagrant directory.
2. Open up the terminal, start up the Vagrant virtual machine, and change directory into where ```CatalogApp``` is located.
3. Before you run the application, you will have to initiate the database. In your terminal, type ```python database_setup.py```. This will create a file named ```catalog.db```.
4. Load the entries of the database by typing ```python load_db.py```.
5. Now that the databse is set up, you can run the wep app by typing ```python catalog.py```.
6. To access the app, head to **http://localhost:5000** in your browser.

## Navgating the CatalogApp
There you can navigate through any of the 6 different categories. To create, edit, or delete catalog items, you must log in. Note that you can only edit or delete items that you have created. Any time you'd like to log out, you may simply log out by clicking **log out** on the top bar.

## Error: "Failed to revoke token for given user."
Typically when logging out, the browser will communicate with Google to revoke the session token that you were assigned when you first logged in. However, if you halted or restarted the app without logging out, the token will not match the one that was previously kept by Google.

In such case, you can force the log out by heading to **http://localhost:5000/forcedc**, which will delete the session and log you out regardless of token mismatch.
