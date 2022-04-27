#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:11:40 2022

@author: lukefronheiser
"""

from startupScript import addUserSearchedPlayers, getUserSearchedPlayers,addUserFavoriteTeam, deletePlayerSearches, deleteSearches, addUserFavoritePlayer, addUserSearchedTeams,startupScript,getUserSearchedTeams,getPlayerByString,getTeamById,getTeamByString, loginUser, createUser, getTeams, getAllPlayers,getTeamRosterById, getUserByEmail, getPlayerDataById, getUserFavoritePlayers, getUserFavoriteTeams 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify,Response
from errno import errorcode
import mysql.connector
from bs4 import BeautifulSoup
import requests
from sportsipy.nfl.teams import Teams
import re
from flask_bootstrap import Bootstrap


app = Flask(__name__)
app.config['SECRET_KEY'] = "Secret"
startupScript = startupScript()



# Route for homepage
@app.route('/', methods=['GET', 'POST'])
def home():
    error = None
    if request.method == 'POST':
        return redirect(url_for('login', email=request.form['email'], password=request.form['password']))
    return render_template('home.html', error=error)

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
                #return jsonify(userReturn)
                return render_template('dashboard.html', error=error)
            else: 
                error = "Invalid Credentials"
    return render_template('index.html', error=error)

@app.route('/search', methods=['GET', 'POST'])
def search():
    error = None
    if request.method == 'POST':
        #if request.form['email'] != 'admin' or request.form['password'] != 'admin':
        return jsonify("hello") 
    return render_template('search.html', error=error)

# Route for handling the login page logic
@app.route('/teamSearch', methods=['POST', 'GET'])
def teamSearch():
    searchTeamsFound = []
    currentUser = getUserByEmail(session['email'])
    error = None
    if request.method == 'POST':
        output = request.get_json()
        inputStr = str(output['teamName'])
        teams = Teams()
        if output:
            i = 1
            for team in teams:
                print(team)
                print(team.name)
                if inputStr.lower() in team.name.lower():
                    print("found")
                    print(i)
                    print(currentUser[0])
                    addUserSearchedTeams(i, currentUser[0])
                i = i+1            
        return jsonify(searchTeamsFound)
    
        
    else: 
        lists = []
        lists = getUserSearchedTeams(currentUser[0])
        output = []
        for each in lists:
            team = getTeamById(each[1])
            output.append(team)
        return jsonify(output)


    
# Route for handling the login page logic
@app.route('/playerSearch', methods=['GET', 'POST'])
def playersearch():
    searchPlayersFound = []
    currentUser = getUserByEmail(session['email'])
    error = None
    if request.method == 'POST':
        output = request.get_json()
        inputStr = str(output['playerName'])
        players = list(getAllPlayers())
        i = 0
        for player in players:
            print(player)
            name = player[2]+ " " + player[3]
            if inputStr.lower() in name.lower():
                print(i)
                print(currentUser[0])
                addUserSearchedPlayers(i, currentUser[0])
                searchPlayersFound.append(player)
            i = i+1            
        return jsonify(searchPlayersFound)

    
        
    else: 
        lists = []
        lists = getUserSearchedPlayers(currentUser[0])
        output = []
        for each in lists:
            player = getPlayerDataById(each[1])
            output.append(player)
        return jsonify(output)
    
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
@app.route('/getUserFavoritePlayers')
def GetUserFavoritePlayers():
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        playerList = getUserFavoritePlayers(currentUser[0])
        output = []
        for player in playerList:
            target = getPlayerDataById(player[1])
            output.append(target)
        return jsonify(output)
    else:
        return "hshd"
@app.route('/getUserFavoriteTeams')
def GetUserFavoriteTeams():
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        teamList = getUserFavoriteTeams(currentUser[0])
        output = []
        for team in teamList:
            target = getTeamById(team[1])
            output.append(target)
        return jsonify(output)
    else:
        return "hshd"
@app.route('/getTeamById/<teamid>')
def GetTeamById(teamid=0):
    if request.method == 'GET':
        team = getTeamById(int(teamid))
        return jsonify(team)
    else:
        return "hshd"
@app.route('/addFavoriteTeam/<teamid>')
def addFavoriteTeamById(teamid=0):
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        output = addUserFavoriteTeam(teamid, currentUser[0])
        return jsonify(output)
    else:
        return "hshd"
@app.route('/clearSearches')
def clearAllSearch():
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        output = deleteSearches(currentUser[0])
        print(output)
        if (output is None):
            return jsonify([])
        else: return jsonify(output)
    else:
        return "hshd"
@app.route('/clearPlayerSearches')
def clearAllPlayerSearch():
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        output = deletePlayerSearches(currentUser[0])
        if (output is None):
            return jsonify([])
        else: return jsonify(output)
    else:
        return "hshd"

if __name__ == '__main__':
    Bootstrap(app)
    app.run(debug=True, port=5000) #run app in debug mode on port 5000


