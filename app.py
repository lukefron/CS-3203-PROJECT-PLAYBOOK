#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 14:11:40 2022

@author: lukefronheiser
"""

from startupScript import addUserSearchedPlayers, GetPlayerById, getNews, getUserSearchedPlayers,addUserFavoriteTeam, deletePlayerSearches, deleteSearches, addUserFavoritePlayer, addUserSearchedTeams,startupScript,getUserSearchedTeams,getPlayerByString,getTeamById,getTeamByString, loginUser, createUser, getTeams, getAllPlayers,getTeamRosterById, getUserByEmail, getPlayerDataById, getUserFavoritePlayers, getUserFavoriteTeams 
from flask import Flask, render_template, request, redirect, url_for, session, jsonify,Response
from errno import errorcode
import mysql.connector
from bs4 import BeautifulSoup
import requests
from sportsipy.nfl.teams import Teams
import re
import json
from flask_bootstrap import Bootstrap
import os
import plotly.graph_objects as plot
import plotly.express as px
import plotly as plotly
import json
import pandas as pd
from random import randrange
import time
from plotly.subplots import make_subplots
import pandas as pd
import plotly.graph_objects as plot


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

# Route for charts
@app.route('/charts', methods=['GET', 'POST'])
def viewcharts():
    error = None
    return render_template('viewCharts.html', error=error)

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

@app.route('/dashboard')
def dashboard():
    error = None
    return render_template('dashboard.html', error=error)

# Route for handling the login page logic
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    error = None
    session['email'] = ""
    return redirect(url_for('home'))
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
                if inputStr.lower() in team.name.lower():
                    print("found")
                    print(currentUser[0])
                    addUserSearchedTeams(i, currentUser[0])
                i = i+1            
            return jsonify(searchTeamsFound)
    
        
    else: 
        lists = []
        lists = getUserSearchedTeams(currentUser[0])
        teamList = []
        for each in lists:
            print(each[2])
            team = getTeamById(each[2])
            print(team)
            teamList.append(team)
        print(jsonify(teamList))
        return jsonify(teamList)


    
# Route for handling the login page logic
@app.route('/playerSearch', methods=['GET', 'POST'])
def playersearch():
    searchPlayersFound = []
    currentUser = getUserByEmail(session['email'])
    error = None
    if request.method == 'POST':
        output = request.get_json()
        inputStr = str(output['playerName'])
        players = getAllPlayers()
        i = 1
        for player in players:
            name = player[2]+ " " + player[3]
            if inputStr.lower() in name.lower():
                addUserSearchedPlayers(i, currentUser[0])
            i = i+1   
        return jsonify(searchPlayersFound)

    else: 
        lists = []
        lists = getUserSearchedPlayers(currentUser[0])
        output = []
        for each in lists:
            player = getPlayerDataById(each[2])
            output.append(player)
        return jsonify(output)
    
@app.route('/createNewUser', methods = ['GET','POST'])
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

@app.route('/teams/roster/<teamid>')
def getRosterByTeamId(teamid=0):
    error = None
    if request.method == 'GET':
        return render_template('rosterview.html', error = error)
@app.route('/teams/getRosterPlayers/<teamid>')
def getRosterPlayers(teamid=0):
    error = None
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
        return redirect(url_for('search'))
    else:
        return "hshd"
@app.route('/addFavoritePlayer/<playerid>')
def addFavoritePlayerById(playerid=0):
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        output = addUserFavoritePlayer(playerid, currentUser[0])
        return redirect(url_for('search'))
    else:
        return "hshd"
@app.route('/clearSearches')
def clearAllSearch():
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        output = deleteSearches(currentUser[0])
        print(output)
        return jsonify([])
    else:
        return "hshd"
@app.route('/clearPlayerSearches')
def clearAllPlayerSearch():
    if request.method == 'GET':
        currentUser = getUserByEmail(session['email'])
        output = deletePlayerSearches(currentUser[0])
        print(output)
        return jsonify([])
    else:
        return "hshd"
@app.route('/news')
def GetNewsHeadlines():
    if request.method == 'GET':
        headlines = getNews()
        return jsonify(headlines)
    else:
        return "hshd"
@app.route('/getPlayerByID/<playerid>')
def getPlayerById(playerid=0):
    if request.method == 'GET':
        player = GetPlayerById(playerid)
        return jsonify(player)
    else:
        return "hshd"
@app.route('/players/<playerid>')
def getPlayerDetailView(playerid=0):
    error = None
    if request.method == 'GET':
        return render_template('playerdetailview.html', error = error)
@app.route('/getGraphs')
def GetFavGraphs():
    if request.method =='GET':
        currentUser = getUserByEmail(session['email'])
        favTeams = getUserFavoriteTeams(currentUser[0])
        nfl_data = Teams()
        teamsToGraph = []
        i = 0
        for each in favTeams:
            print(each)
            teamsToGraph.append((each[1]-1))

        
        team_wins = []
        team_loss = []
        team_abbrev = []
        for each in nfl_data:
            team_abbrev.append(each.abbreviation)
            team_wins.append(each.wins)
            team_loss.append(each.losses)
   
        team_data = pd.DataFrame(index = range(0,32), columns=['abbrev','wins','losses','win%'])

        team_data['abbrev'] = team_abbrev
        team_data['wins'] = team_wins
        team_data['losses'] = team_loss

        for teams in range(0,32):
            team_data['win%'][teams] = (team_data['wins'][teams]/(team_data['wins'][teams]+team_data['losses'][teams]))*100
            #print(team_data)

        favorite_teams = teamsToGraph
        favorite_team_data = pd.DataFrame(index = range(0,len(favorite_teams)), columns = ['id','abbrev','wins','losses','win%'])
        for teams in range(0,len(favorite_teams)):
            favorite_team_data['id'][teams] = favorite_teams[teams]
            favorite_team_data['abbrev'][teams] = team_data['abbrev'][favorite_teams[teams]]
            favorite_team_data['wins'][teams] = team_data['wins'][favorite_teams[teams]]
            favorite_team_data['losses'][teams] = team_data['losses'][favorite_teams[teams]]
            favorite_team_data['win%'][teams] = team_data['win%'][favorite_teams[teams]]
            print(favorite_team_data)


        fig = px.line(x = favorite_team_data['abbrev'], y = favorite_team_data['win%'])
        fig.update_layout(title = 'Team win percentage', xaxis_title = 'Teams', yaxis_title = 'Win Percentage (%)')
        fig.update_yaxes(range = list([0,100]))
        
        
        
             
        if not os.path.exists("images"):
            os.mkdir("images")
        
        location = "static/images/test"
        random = str(randrange(10)) + str(randrange(10)) + str(randrange(10)) + str(randrange(10))
        location = location+random + ".png"
        fig.write_image(location)
        
        return "test" + random + ".png"
    else:
        return "Not a get request"
@app.route('/getSpecialGraphs')
def GetSpecialGraphs():
    if request.method =='GET':
        
        currentUser = getUserByEmail(session['email'])
        favTeams = getUserFavoriteTeams(currentUser[0])
        nfl_data = Teams()
        teamsToGraph = []
        i = 0
        for each in favTeams:
            print(each)
            teamsToGraph.append((each[1]-1))
            
        if not os.path.exists("images"):
            os.mkdir("images")

        nfl_data = Teams()
        #df = nfl_data.dataframe
        #print(df)
        print(nfl_data)

        # GRABBING DATA
        team_abbrev = []
        team_names = []
        team_wins = []
        team_loss = []
        team_totpassing = []
        team_totrushing = []
        team_TD = []
        team_passTD = []
        team_rushTD = []
        team_fumble = []
        team_intercept = []
        team_penalties = []
        for each in nfl_data:
            team_abbrev.append(str(each.abbreviation))
            team_names.append(str(each.name))
            team_wins.append(each.wins)
            team_loss.append(each.losses)
            team_totpassing.append(each.pass_yards)
            team_totrushing.append(each.rush_yards)
            team_passTD.append(each.pass_touchdowns)
            team_rushTD.append(each.rush_touchdowns)
            team_TD.append((each.pass_touchdowns + each.rush_touchdowns))
            team_fumble.append(each.fumbles)
            team_intercept.append(each.interceptions)
            team_penalties.append(each.penalties)
#print(team_names)
#print(team_names)
#print(team_wins)
#print(team_loss)
#print(team_totpassing)
#print(team_passTD)

    # Initializing the dataframe
        team_data = pd.DataFrame(index = range(0,32), columns=['abbrev','name','wins','losses','win%','passyds','rushyds','passTD','rushTD','totTD','fumbles','interceptions','penalties',])
        # Inserting previous
        team_data['abbrev'] = team_abbrev
        team_data['name'] = team_names
        team_data['wins'] = team_wins
        team_data['losses'] = team_loss
        team_data['passyds'] = team_totpassing
        team_data['rushyds'] = team_totrushing
        team_data['passTD'] = team_passTD
        team_data['rushTD'] = team_rushTD
        team_data['totTD'] = team_TD
        team_data['fumbles'] = team_fumble
        team_data['interceptions'] = team_intercept
        team_data['penalties'] = team_penalties
        
        for teams in range(0,32):
            team_data['win%'][teams] = (team_data['wins'][teams]/(team_data['wins'][teams]+team_data['losses'][teams]))*100

        favorite_teams = teamsToGraph
        favorite_team_data = pd.DataFrame(index = range(0,len(favorite_teams)), columns = ['abbrev','rushTD','passTD'])
        for teams in range(0,len(favorite_teams)):
            favorite_team_data['abbrev'][teams] = team_data['abbrev'][favorite_teams[teams]]
            favorite_team_data['rushTD'][teams] = team_data['rushTD'][favorite_teams[teams]]
            favorite_team_data['passTD'][teams] = team_data['passTD'][favorite_teams[teams]]
            print(favorite_team_data)
        print(team_data)
        
        team_data = favorite_team_data
        fig= plot.Figure()
        fig.add_trace(plot.Line(x = team_data['abbrev'], y = team_data['passTD'], name = "Passing TD"))
        fig.add_trace(plot.Line(x = team_data['abbrev'], y = team_data['rushTD'], name = "Rushing TD"))
        fig.update_layout(title = "Passing vs Rushing Touchdowns", xaxis_title = "Teams", yaxis_title = "Touchdowns")
        #fig.show()
        name = 'Graph4'
        location = 'images/' + name + '.png'
        fig.write_image(location)
        
             
        if not os.path.exists("images"):
            os.mkdir("images")
            
        location = "static/images/test"
        random = str(randrange(10)) + str(randrange(10)) + str(randrange(10)) + str(randrange(10))
        location = location+random + ".png"
        fig.write_image(location)
        
        return "test" + random + ".png"

    else:
        return "Not a get request"
    

if __name__ == '__main__':
    Bootstrap(app)
    app.run(debug=True, port=5000) #run app in debug mode on port 5000


