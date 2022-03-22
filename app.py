#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:11:40 2022

@author: lukefronheiser
"""

import startupScript
from flask import Flask, render_template, request, redirect, url_for, session
from errno import errorcode
import mysql.connector
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)

try: 
    startupScript.start()
except mysql.connector.Error as err:
    print("failed")
    output = startupScript.getAllTables()
    if(output):
        for table in output:
            print(table)
    

@app.route('/')
def root():
    return '<h1>hello there</h1>'

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
    user = startupScript.login(email, password)
    # If account exists in accounts table in out database
    if user:
        # Create session data, we can access this data in other routes
        session['loggedin'] = True
        session['id'] = user['user_id']
        session['username'] = user['email']
        # Redirect to home page
        return 'Logged in successfully!' 
    else:
        msg = 'Incorrect username/password!'
        return render_template('index.html', msg=msg)
    
@app.route('/createUser/', methods = ['POST'])
def createNewUser():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form:
        # Create variables for easy access
        email = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        # Check if account exists using MySQL
        user = startupScript.createUser(email, password, first_name, last_name)
        if user:
            return 'New Account created'
        else:
            return "failed"
if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000


