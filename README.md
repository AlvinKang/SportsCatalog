# CatalogApp
This is a project submission for Udacity's Full Stack Nanodegree program. The Python code uses [**Flask**](http://flask.pocoo.org/), a Python microframework, to deploy a Sports Catalog web application using HTML and CSS templates.

run SQL scripts and prints out a report answering the questions required for the Logs Analysis Project.

### Design
```analysis.py``` connects to the ```news``` database using psycopg2 Python module. First, the SQL queries for each of the three questions are defined as multi-line string variables. Then, a universal ```run_script()``` function executes each query, while three ```format_script()``` functions transform the query outputs into the desired format. Finally, those outputs are printed in order of the questions.

## Getting Started
**IMPORTANT:** It is expected that you have the setup stipulated by Udacity. The SQL database accessed in this project is provided by Udacity and is necessary to be able to execute the Python code.

This code runs **Python 2.7**.

### Installing and Running
Here are the steps to follow to use Python to print out the report:
1. Download the files in this repository as a ZIP.
2. Before you run the Python code, you will have to connect to the database and run the SQL scripts to create views that will be used. After starting ```psql```, copy and paste the scripts from ```SQL-scripts/createView.sql``` into your terminal.
3. Exit out of ```psql``` and ```cd``` to the directory that you downloaded this repo. Type ```python analysis.py```.
4. The command above will print out the report to your terminal.

Alternatively, if you'd like to see the content of the report without executing the code, you can view it in ```output.txt```. You can also see the raw SQL queries for each of the questions in ```/SQL-scripts```, where ```scriptN.sql``` contains the query executed for question N.