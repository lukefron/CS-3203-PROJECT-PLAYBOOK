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
        "https://www.pro-football-reference.com/teams/" + team_abbreviation.lower() + "/2018_roster.htm")

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

def start():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor()

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

    cursor.close()
    cnx.commit()
    
def login(email, password):
    
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor()

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    # Commits to save changes
    cnx.commit()

    cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
    cnx.commit()
    # Fetch one record and return result
    return cursor.fetchone()
def createUser(email, password, first_name, last_name):
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor()

    DB_NAME = 'fronheiser_CS_3203'
    

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    # Commits to save changes
    cnx.commit()

    add_new_user = (
        'INSERT INTO user(first_name, last_name, email, password)'
        'VALUES (%s,%s,%s,%s)')
    cursor.execute(add_new_user, (first_name, last_name, email, password))
    cnx.commit()

    # Fetch one record and return result
    return cursor.fetchone()

def getAllTables():
    cnx = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="boomersooner7")

    # Get a cursor
    cursor = cnx.cursor()

    DB_NAME = 'fronheiser_CS_3203'

    # Sets the connection object's database to my DB
    cnx.database = DB_NAME
    # Commits to save changes
    cnx.commit() 
    
    cursor.execute("Show tables;")
    myresult = cursor.fetchall()
    return myresult













