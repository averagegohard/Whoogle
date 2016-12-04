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
app.config['MYSQL_DATABASE_PASSWORD'] = 'mynewpass'
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

@app.route("/search", methods=['GET'])
def search():
	return render_template('search.html')
	#search=request.form.get('searchterm')
	
@app.route("/profile", methods=['GET'])
def profile():
	return render_template('profile.html')
	
@app.route("/results/<string:name>", methods=['GET','POST'])
def results():
	name = request.form.get('name')
	return render_template('results.html')

#def login():
#	return render_template('login.html')
