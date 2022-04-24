#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:11:40 2022

@author: lukefronheiser
"""

from startupScript import startupScript, loginUser, createUser, getTeams, getAllPlayers,getTeamRosterById, getUserByEmail, getPlayerDataById
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from errno import errorcode
import mysql.connector
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = "Secret"
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
                session['email'] = request.form['email']
                return jsonify(userReturn)
            else: 
                error = "Invalid Credentials"
    return render_template('index.html', error=error)

    
@app.route('/login/createNewUser', methods = ['GET','POST'])
def createNewUser():
    error = None
    if request.method == 'POST':
        if 'email' in request.form and 'password' in request.form and 'first_name' in request.form and 'last_name' in request.form:
            # Check if account exists using MySQL
            user = createUser(request.form['email'], request.form['password'], request.form['first_name'], request.form['last_name'])
            if user:
                return redirect("http://localhost:5000/login", code=302)
            else:
                error = "Failure"
    return render_template('newuser.html', error = error)

@app.route('/teams', methods = ['GET'])
def getAllTeams():
    if request.method == 'GET':
        teams = getTeams()
        return jsonify(teams)
    return "Error"


@app.route('/players', methods = ['GET'])
def getAllPlayer():
    if request.method == 'GET':
        players = getAllPlayers()
        return jsonify(players)
    return "Error"
@app.route('/players/<playerid>', methods = ['GET'])
def getPlayerData(playerid=0):
    if request.method == 'GET':
        player = getPlayerDataById(int(playerid))
        return jsonify(player)
    return "Error"

@app.route('/teams/roster/<teamid>')
def getRosterByTeamId(teamid=0):
    if request.method == 'GET':
        team = getTeamRosterById(int(teamid))
        return jsonify(team)
@app.route('/testContext')
def getUserInContext():
    if request.method == 'GET':
        user = getUserByEmail(session['email'])
        return jsonify(user)
    else:
        return "hshd"
if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000


