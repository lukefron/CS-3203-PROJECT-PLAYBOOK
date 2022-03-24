#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:11:40 2022

@author: lukefronheiser
"""

from startupScript import startupScript, loginUser
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from errno import errorcode
import mysql.connector
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
startupScript = startupScript()


# Route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #if request.form['email'] != 'admin' or request.form['password'] != 'admin':
        if 'email' in request.form and 'password' in request.form:
            userReturn = loginUser(request.form['email'], request.form['password'])
            if userReturn:
                return jsonify(userReturn)
            else: 
                error = "Invalid Credentials"
    return render_template('index.html', error=error)

    
@app.route('/login/createNewUser', methods = ['POST'])
def createNewUser():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form:
        # Create variables for easy access
        email = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        # Check if account exists using MySQL
        user = startupScript.createUser(email, password, first_name, last_name)
        return user

if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000


