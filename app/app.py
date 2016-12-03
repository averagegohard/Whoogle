# this is where we will put the code for the app
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import datetime

# this import statement means:
# from keys.py import the variables API_KEY and API_SECRET
from keys import API_KEY, API_SECRET

#for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

#These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'wtfidget7120'
app.config['MYSQL_DATABASE_DB'] = 'whoogle'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()

#default page  
@app.route("/", methods=['GET'])
def login():
	return render_template('login.html')
