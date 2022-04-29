#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: lukefronheiser
"""
from errno import errorcode
from sportsipy.nfl.teams import Teams
import pandas as pd
import mysql.connector
from bs4 import BeautifulSoup
import requests
import re
import urllib.request
from urllib.request import urlopen
import os
from plotly.subplots import make_subplots
import plotly.graph_objects as plot
import plotly.express as px



# Connect to local server
# TASK: CREATE DATABASE





# add_nfl_team= ('INSERT INTO nfl_data(name, team_abbreviation, team_wins, team_losses, team_fumbles, team_interceptions, team_penalties)'
#     'VALUES (%s,%s,%s,%s,%s,%s,%s)')

def search(target, text, context=7):
    # It's easier to use re.findall to split the string,
    # as we get rid of the punctuation
    words = re.findall(r'\w+', text)

    matches = (i for (i, w) in enumerate(words) if w.lower() == target)
    for index in matches:
        if index < context // 2:
            yield words[0:context + 1]
        elif index > len(words) - context // 2 - 1:
            yield words[-(context + 1):]
        else:
            yield words[index - context // 2:index + context // 2 + 1]


def getPlayers(team_abbreviation):
    page = requests.get(
        "https://www.pro-football-reference.com/teams/" + team_abbreviation.lower() + "/2021_roster.htm")

    soup = BeautifulSoup(page.content, 'html.parser')

    body = str(soup)

    scrapeObj = list(search('player', body))

    players = []
    for dataPoint in scrapeObj:
        if dataPoint[1] == "data":
            if dataPoint[4] == "csk":
                try:
                    thisdict = {
                        "first_name": dataPoint[6],
                        "last_name": dataPoint[5],
                        "playerIDString": dataPoint[0],
                        "playerLink": "https://www.pro-football-reference.com/players/" + dataPoint[0][0] + "/" +
                                      dataPoint[0] + ".htm"
                    }
                except:
                    print("New line exception")

                players.append(thisdict)
                print("yes")

    return players

def startupScript():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    # Method creates database if it doesn't exist with the given name
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))

    #Sets the connection object's database to my DB
    cnx.database = DB_NAME
    #Commits to save changes
    cnx.commit()
    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    # Commits to save changes
    cnx.commit()
    # Creating collection of tables needed for data- here only one needed for Iris
    TABLES = {}
    TABLES['nfl_data'] = (
        "CREATE TABLE `nfl_data` ("
        "  `team_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `name` VARCHAR(45) NOT NULL,"
        "  `team_abbreviation` VARCHAR(45) NOT NULL,"
        "  `team_wins` int(11) NOT NULL,"
        "  `team_losses` int(11) NOT NULL,"
        "  `team_fumbles` int(11) NOT NULL,"
        "  `team_interceptions` int(11) NOT NULL,"
        "  `team_penalties` int(11) NOT NULL,"
        "  PRIMARY KEY (`team_id`)"
        ") ENGINE=InnoDB")
    TABLES['user'] = (
        "CREATE TABLE `user` ("
        "  `user_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `first_name` VARCHAR(45) NOT NULL,"
        "  `last_name` VARCHAR(45) NOT NULL,"
        "  `email` VARCHAR(45) NOT NULL,"
        "  `password` VARCHAR(45) NOT NULL,"
        "  PRIMARY KEY (`user_id`)"
        ") ENGINE=InnoDB")
    TABLES['players'] = (
        "CREATE TABLE `players` ("
        "  `player_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `team_id` int(11) NOT NULL,"
        "  `first_name` VARCHAR(45) NOT NULL,"
        "  `last_name` VARCHAR(45) NOT NULL,"
        "  `playerIDString` VARCHAR(45) NOT NULL,"
        "  `playerLink` VARCHAR(255) NOT NULL,"
        "  PRIMARY KEY (`player_id`),"
        "  FOREIGN KEY (`team_id`) REFERENCES nfl_data(team_id)"
        ") ENGINE=InnoDB")
    TABLES['users_favorite_players'] = (
        "CREATE TABLE `users_favorite_players` ("
        "  `user_id` int(11) NOT NULL,"
        "  `player_id` int(11) NOT NULL,"
        "  PRIMARY KEY (`user_id`, `player_id`),"
        "  FOREIGN KEY (`user_id`) REFERENCES user(user_id),"
        "  FOREIGN KEY (`player_id`) REFERENCES players(player_id)"
        ") ENGINE=InnoDB")
    TABLES['users_favorite_teams'] = (
        "CREATE TABLE `users_favorite_teams` ("
        "  `user_id` int(11) NOT NULL,"
        "  `team_id` int(11) NOT NULL,"
        "  PRIMARY KEY (`user_id`, `team_id`),"
        "  FOREIGN KEY (`user_id`) REFERENCES user(user_id),"
        "  FOREIGN KEY (`team_id`) REFERENCES nfl_data(team_id)"
        ") ENGINE=InnoDB")
    TABLES['searched_teams'] = (
        "CREATE TABLE `searched_teams` ("
        "  `searched_teams_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `user_id` int(11) NOT NULL,"
        "  `team_id` int(11) NOT NULL,"
        "  PRIMARY KEY (`searched_teams_id`),"
        "  FOREIGN KEY (`user_id`) REFERENCES user(user_id),"
        "  FOREIGN KEY (`team_id`) REFERENCES nfl_data(team_id)"
        ") ENGINE=InnoDB")
    TABLES['searched_players'] = (
        "CREATE TABLE `searched_players` ("
        "  `searched_player_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `user_id` int(11) NOT NULL,"
        "  `player_id` int(11) NOT NULL,"
        "  PRIMARY KEY (`searched_player_id`),"
        "  FOREIGN KEY (`user_id`) REFERENCES user(user_id),"
        "  FOREIGN KEY (`player_id`) REFERENCES players(player_id)"
        ") ENGINE=InnoDB")
    TABLES['news'] = (
        "CREATE TABLE `news` ("
        "  `news_id` int(11) NOT NULL AUTO_INCREMENT,"
        "  `headline` VARCHAR(255) NOT NULL,"
        "  `link` VARCHAR(255) NOT NULL,"
        "  PRIMARY KEY (`news_id`)"
        ") ENGINE=InnoDB")

    ##Inserting tables into database
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno:
                print("already exists.")
            else:
                print(err.msg)

        else:
            print("OK")

    nfl_data = Teams()
    add_nfl_team = (
        'INSERT INTO nfl_data(name, team_abbreviation, team_wins, team_losses, team_fumbles, team_interceptions, team_penalties)'
        'VALUES (%s,%s,%s,%s,%s,%s,%s)')
    add_root_user = (
        'INSERT INTO user(first_name, last_name, email, password) VALUES (%s,%s,%s,%s)'
        )
    get_first_team = ('SELECT* FROM nfl_data LIMIT 1')
    add_root_user_fav_players = ('INSERT INTO users_favorite_players(user_id, player_id) VALUES (%s, %s)')
    add_root_user_fav_teams = ('INSERT INTO users_favorite_teams(user_id, team_id) VALUES (%s, %s)')
    add_root_user_searched_teams = ('INSERT INTO searched_teams(user_id, team_id) VALUES (%s, %s)')
    add_root_user_searched_players = ('INSERT INTO searched_players(user_id, player_id) VALUES (%s, %s)')

    cursor.execute(get_first_team)
    output = cursor.fetchone()
    if output == None:
        for team in nfl_data:
            # Inserts into database. Tuple is a python collection method to contain our fields in an object
            #     values = [(team.name, team.abbreviation, team.wins, team.losses, team.fumbles, team.interceptions, team.penalties)]
            cursor.execute(add_nfl_team, (
            team.name, team.abbreviation, team.wins, team.losses, team.fumbles, team.interceptions, team.penalties))
            #     cursor.execute(add_players_by_team, ())
            print("success")
        for team in nfl_data:
            cursor.execute('SELECT nfl.team_id FROM nfl_data AS nfl WHERE nfl.team_abbreviation=%s', (team.abbreviation,))
            myresult = cursor.fetchall()
            val = myresult
            num = val[0][0]
            allPlayers = getPlayers(team.abbreviation)
            for player in allPlayers:
                updateDict = {"team_id": num}
                updateDict.update(player)
                placeholders = ', '.join(['%s'] * len(updateDict))
                columns = ', '.join(updateDict.keys())
                sql = "INSERT INTO %s ( %s ) VALUES ( %s )" % ('players', columns, placeholders)
                cursor.execute(sql, list(updateDict.values()))
                print("added")
        
        cursor.execute(add_root_user, ("luke", "fron", "lukefron@ou.edu", "password"))
        cursor.execute(add_root_user_fav_players, ("1", "1"))
        cursor.execute(add_root_user_fav_players, ("1", "2"))
        cursor.execute(add_root_user_fav_players, ("1", "3"))
        
        cursor.execute(add_root_user_fav_teams, ("1", "1"))
        cursor.execute(add_root_user_fav_teams, ("1", "2"))
        cursor.execute(add_root_user_fav_teams, ("1", "3"))
        
        cursor.execute(add_root_user_searched_teams, ("1", "5"))
        cursor.execute(add_root_user_searched_teams, ("1", "6"))
        cursor.execute(add_root_user_searched_teams, ("1", "7"))
        
        cursor.execute(add_root_user_searched_players, ("1", "69"))
        cursor.execute(add_root_user_searched_players, ("1", "66"))
        cursor.execute(add_root_user_searched_players, ("1", "71"))

        print("root added")
        preloadGraphs()

    else: 
        print("data is loaded. App ready")
    




    cursor.close()
    cnx.commit()
    
def loginUser(email, password):
    
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
    output = cursor.fetchone()
    # Fetch one record and return result
    return output;



def getAllTables():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    # Commits to save changes
    cnx.commit() 
    
    cursor.execute("Show tables;")
    myresult = cursor.fetchall()
    return myresult

#CRUD Operations for USER
#CREATE
def createUser(email, password, first_name, last_name):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('INSERT INTO user(first_name, last_name, email, password) VALUES (%s,%s,%s,%s)', (first_name, last_name, email, password))
    cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password))
    output = cursor.fetchone()
    cnx.commit()
    # Fetch one record and return result
    return output

def getTeams():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM nfl_data')
    output = cursor.fetchmany(32)
    return output
def getTeamById(teamid):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)
    DB_NAME = 'fronheiser_CS_3203'
    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    
    cursor.execute('SELECT * FROM nfl_data WHERE team_id = %s' , (teamid,))
    output = cursor.fetchone()
    return output

def getAllPlayers():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)
    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM players')
    output = cursor.fetchall()
    return output
def getPlayerDataById(playerid):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)
    DB_NAME = 'fronheiser_CS_3203'
    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    #cursor.execute('SELECT playerLink FROM players WHERE player_id = %s' , (playerid,))
    #output = cursor.fetchall()
    #url = str(output)
    #page = requests.get('url')

    #soup = BeautifulSoup(page.content, 'html.parser')
    
    #body = str(soup)
    #print(body)

    #scrapeObj = list(search('player', body))

    #players = []
    #for dataPoint in scrapeObj:
    #    print(dataPoint)
    #return body
    cursor.execute('SELECT * FROM players WHERE player_id = %s' , (playerid,))
    output = cursor.fetchone()
    return output

    
def getTeamRosterById(teamid):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM players WHERE team_id = %s', (teamid,))
    output = cursor.fetchall()
    return output

def getTeamByString(teamString):
    nfl_data = Teams()
    outputTeams = []
    for team in nfl_data:
        if teamString.lower() in team.name.lower():
            outputTeams.append(team)
        elif teamString.lower() in team.abbreviation.lower():
            outputTeams.append(team)
    return outputTeams

def getPlayerByString(playerString):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    
    allPlayers = getAllPlayers()
    i = 0
    returnPlayers = []
    for player in allPlayers:
        if playerString.lower() in player[i][2].lower():
            returnPlayers.append(player)
        elif playerString.lower() in player[i][3].lower():
            returnPlayers.append(player)
        i = i+1

    return returnPlayers
def GetPlayerById(playerid):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM players WHERE player_id = %s',(playerid,))
    output = cursor.fetchall()
    return output

def addUserFavoriteTeam(team_id,user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('INSERT INTO users_favorite_teams(user_id, team_id) VALUES (%s, %s)', (user_id, team_id))
    cnx.commit()
    
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM users_favorite_teams WHERE user_id = %s AND team_id = %s', (user_id, team_id))
    output = cursor.fetchall()
    return output

def addUserFavoritePlayer(player_id, user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('INSERT INTO users_favorite_players(user_id, player_id) VALUES (%s, %s)', (user_id, player_id))
    cnx.commit()
    
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM users_favorite_players WHERE user_id = %s AND player_id = %s', (user_id, player_id))
    output = cursor.fetchall()
    return output
def getUserFavoritePlayers(user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('SELECT* FROM users_favorite_players WHERE user_id = %s', (user_id,))
    output = cursor.fetchall()
    return output
def getUserFavoriteTeams(user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('SELECT* FROM users_favorite_teams WHERE user_id = %s', (user_id,))
    output = cursor.fetchall()
    return output
def getUserSearchedTeams(user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('SELECT* FROM searched_teams WHERE user_id = %s', (user_id,))
    output = cursor.fetchall()
    return output
def addUserSearchedTeams(team_id,user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    
    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('INSERT INTO searched_teams(user_id, team_id) VALUES (%s, %s)', (user_id, team_id))
    output = cursor.execute('SELECT * FROM searched_teams WHERE user_id = %s AND team_id = %s', (user_id, team_id))
    output = cursor.fetchall()
    cnx.commit()
    
    return output

#READ
def getUserByEmail(email):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
    output = cursor.fetchone()
    cnx.commit()
    return output

def deleteSearches(user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    
    cursor.execute('DELETE FROM searched_teams WHERE user_id = %s', (user_id,))
    cnx.commit()
    
    return "deleted"

def deletePlayerSearches(user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    
    cursor.execute('DELETE FROM searched_players WHERE user_id = %s', (user_id,))
    cnx.commit()
    
def getUserSearchedPlayers(user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('SELECT* FROM searched_players WHERE user_id = %s', (user_id,))
    output = cursor.fetchall()
    return output
def addUserSearchedPlayers(player_id,user_id):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME

    cursor.execute('INSERT INTO searched_players(user_id, player_id) VALUES (%s, %s)', (user_id, player_id))
    output = cursor.execute('SELECT * FROM searched_players WHERE user_id = %s AND player_id = %s', (user_id, player_id))
    output = cursor.fetchall()
    cnx.commit()
    
    return output
def getNews():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor(buffered=True)
    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    
    url = 'https://www.nfl.com/news/'
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    htmlstring = str(soup)

    htmlstring = htmlstring[htmlstring.find("d3-o-media"):htmlstring.find("displays:none")]
    linkstring = ""
    storylist = []
    found = 1
    headlinestring = ""
    while(found > 0):
        # First generates the headline
        found = htmlstring.find("data-link_name")
        if(found < 0):
            break
        linkend = htmlstring.find("data-link_url", found)
        headlinestring = htmlstring[(found+16):(linkend-1)]
        # Now generate the url
        linkstart = htmlstring.find("href", 0)
        linkend = htmlstring.find(" ", linkstart)
        linkstring = url + htmlstring[(linkstart+12):(linkend-1)]
        htmlstring = htmlstring[linkend:len(htmlstring)]
        location = headlinestring.index('"')
        headlinestring = headlinestring[0:location]
        #Pair the url and headline, then save to the list
        story = [headlinestring,linkstring]
        storylist.append(story)

    # Filtering off other links
    storylistfinal = []
    for i in range(0,6):
        storylistfinal.append(storylist[i])
        print(storylistfinal)
        cursor.execute('INSERT INTO news(headline, link) VALUES (%s, %s)', (storylistfinal[i][0], storylistfinal[i][1]))

    cursor.execute('SELECT * FROM news')
    output = cursor.fetchall()
    return output
def preloadGraphs():

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
    team_data = pd.DataFrame(index = range(0,32), columns=['abbr','name','wins','losses','win%','passyds','rushyds','passTD','rushTD','totTD','fumbles','interceptions','penalties',])
# Inserting previous
    team_data['abbr'] = team_abbrev
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

    print(team_data)

    ''' GRAPH 1: TEAM W-L < WIN% '''

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #Plot the major yaxis
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['wins'], name = "Team Wins"), secondary_y = False)
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['losses'], name = "Team Losses"), secondary_y = False)
    #Plot the secondary yaxis
    #fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['win%'], name = "Win Percentage (%)",), secondary_y = True)
    fig.update_layout(title = "Team records 2021", xaxis_title = "Team")
    fig.update_yaxes(title_text = "Games won/lost", range = list([0,17]), secondary_y = False)
    fig.update_yaxes(title_text = "Win Percentage (%)", range = list([0,100]), secondary_y = True)
    #fig.show()
    name = "Graph1"
    location = "images/" + name + ".png"
    fig.write_image(location)

    ''' GRAPH 2: PASSING VS RUSHING YDS & TDS '''

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    #Plot the major yaxis
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['passyds'], name = "Passing Yards"), secondary_y = False)
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['rushyds'], name = "Rushing Yards"), secondary_y = False)
    fig.update_yaxes(title_text = "Yards", secondary_y = False)
    #Plot the secondary yaxis
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['passTD'], name = "Passing TDs", line = dict(width = 7)), secondary_y = True)
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['rushTD'], name = "Rushing TDs", line = dict(color = 'yellow', width = 7)), secondary_y = True)
    maxTD = 0
    if(team_data['passTD'].max() > team_data['rushTD'].max()):
        maxTD = team_data['passTD'] + 1
    else:
        maxTD = team_data['rushTD'] + 1
        fig.update_yaxes(title_text = "Touchdowns by type", range = list([0,maxTD]))
            
        fig.update_layout(title = "Passing vs Rushing by Team", xaxis_title = "Teams")
        #fig.show()
        name = 'Graph2'
        location = 'images/' + name + '.png'
        fig.write_image(location)
            
        ''' GRAPHS 3&4 , breaking down the previous graph '''

    fig = plot.Figure()
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['passyds'], name = "Passing Yards"))
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['rushyds'], name = "Rushing Yards"))
    fig.update_layout(title = "Passing vs Rushing yards", xaxis_title = "Teams", yaxis_title = "Yards")
    #fig.show()
    name = 'Graph3'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    
    fig = plot.Figure()
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['passTD'], name = "Passing TD"))
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['rushTD'], name = "Rushing TD"))
    fig.update_layout(title = "Passing vs Rushing Touchdowns", xaxis_title = "Teams", yaxis_title = "Touchdowns")
    #fig.show()
    name = 'Graph4'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    
    ''' GRAPH 5: EFFICIENCY '''

    #Efficiency in this case is described by yards/TD, less would be more efficient
    passeff = []
    rusheff = []
    eff = []
    Totyds = []
    i=0
    for teams in range(0,32):
        passeff.append((team_data['passyds'][teams])/(team_data['passTD'][teams]))
        rusheff.append((team_data['rushyds'][teams])/(team_data['rushTD'][teams]))
        eff.append((team_data['passyds'][teams]+team_data['rushyds'][teams])/(team_data['passTD'][teams]+team_data['rushTD'][teams]))
        Totyds.append(team_data['passyds'][teams]+team_data['rushyds'][teams])
        team_data = team_data.assign(Passeff = passeff[i])
        team_data = team_data.assign(Rusheff = rusheff[i])
        team_data = team_data.assign(Eff = eff[i])
        team_data = team_data.assign(totyds = Totyds[i])
        i = i+1
        print(team_data)

#Making The efficiency graph

#Plot Major y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['passyds'], name = "Passing Yards"), secondary_y = False)
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['rushyds'], name = "Rushing Yards"), secondary_y = False)
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['totyds'], name = "Total Yards"), secondary_y = False)
    fig.update_layout(barmode = 'group')
    fig.update_yaxes(title_text = "Yards", secondary_y = False)
    #Plot minor y
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Passeff'], name = "Passing Efficiency", line = dict(width = 7)), secondary_y = True)
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Rusheff'], name = "Rushing Efficiency", line = dict(width = 7)), secondary_y = True)
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Eff'], name = "Total Efficiency", line = dict(width = 7)), secondary_y = True)
    fig.update_yaxes(title_text = "Efficiency (yd/TD)", secondary_y = True)
    fig.update_layout(title = "Team Yards to Efficiency by type")
    #fig.show()
    name = 'Graph5'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    
    ''' GRAPHS 6&7: Breaking down the previous graph '''
    fig = plot.Figure()
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['passyds'], name = "Passing Yards"))
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['rushyds'], name = "Rushing Yards"))
    fig.add_trace(plot.Bar(x = team_data['abbr'], y = team_data['totyds'], name = "Total Yards"))
    fig.update_layout(barmode = 'group')
    fig.update_yaxes(title_text = "Yards")
    fig.update_layout(title = "Yards per team by type", xaxis_title = "Team", yaxis_title = "Yards")
    #fig.show()
    name = 'Graph6'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    
    fig = plot.Figure()
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Passeff'], name = "Passing Efficiency"))
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Rusheff'], name = "Rushing Efficiency"))
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Eff'], name = "Total Efficiency"))
    fig.update_layout(title = "Team Efficiency by type", xaxis_title = "Team", yaxis_title = "Efficiency (yd/TD)")
    #fig.show()
    name = 'Graph7'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    
    ''' GRAPH 8: Penalties, fumbles and Interceptions '''
    fig = plot.Figure()
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['fumbles'], name = "Fumbles"))
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['interceptions'], name = "Interceptions"))
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['penalties'], name = "Total Penalties"))
    fig.update_layout(title = "How Each Team Hurts Itself", xaxis_title = "Team", yaxis_title = "Misfortunes")
    #fig.show()
    name = 'Graph8'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    
    ''' GRAPH 9: Efficiency vs win% '''
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['Eff'], name = "Efficiency (yd/TD)"), secondary_y = False)
    fig.add_trace(plot.Line(x = team_data['abbr'], y = team_data['win%'], name = "Win %"), secondary_y = True)
    fig.update_yaxes(title_text = "Win Percentage (%)", range = list([0,100]), secondary_y = True)
    fig.update_yaxes(title_text = "Efficiency (yd/TD")
    fig.update_layout(title = "Teams Win% vs Efficiency", xaxis_title = "Teams")
    #fig.show()
    name = 'Graph9'
    location = 'images/' + name + '.png'
    fig.write_image(location)
    return("Done")

    
            
        
    





