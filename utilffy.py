"""
Name: utilffy.py
Created: 3/9/2023
Authors: Katherine Smirnov, Krishna Patel

Provides a common functions used by all modules, such as the database connection.

Modifications:
    3/09/2023 Added connection function to database, fetch location, and fetch category.
    3/12/2023 Changed input parameters to connection function to all be contained in this file 
              for easy modification.
"""
from tkinter import *
from tkinter import ttk
import mysql.connector
from tkinter import messagebox

font = "Helvetica"
searchInputSize = "9"

port = 3157     #holds the database port number
user = "jerryp" #set username for database to variable
password = "111" #set password for database to variable
host = "ix-dev.cs.uoregon.edu" #set hostname to variable
database = "foodforyou" #set database name for variable

def use_theme(window:Tk, regFontSize):
    """ use_theme(window)
    Applies the theme to the inputted 'window'
    Note: can change the font (font) and size (regFontSize) from the global variables
    """
    style = ttk.Style(window)
    style.theme_create("Custom")    #creates a blank theme
    # creates a theme for such widgets
    style.configure("TLabel", font=(f'{font}, {regFontSize}'), background="#fff")
    style.configure("TButton", font=(f'{font}, {regFontSize}'), background="#fff")
    style.configure("TCheckbutton", font=(f'{font}, {regFontSize}'), background="#fff")
    style.configure("TEntry", font=(f'{font}, {regFontSize}'))
    style.configure("TSpinbox", font=(f'{font} {regFontSize}'))

def fetchLocations(cursor):
    """ fetchLocations(cursor)
    Pulls the existing locations from the database from the cursor.
    """
    cursor.execute("SELECT fb.Location from food_bank fb order by fb.Location ASC") #selects all foodbank locations from food bank database
    locations = []
    locations.append(None)
    #for each row in the databsae
    for row in cursor:
        #grab the location and appends to return value
        for col in row:
            locations.append(col)
    return locations

def fetchCategory(cursor):
    """ fetchLocations(cursor)
        Pulls the existing categories from the database from the cursor.
    """
    cursor.execute("SELECT DISTINCT fi.Category from food_item fi order by fi.Category ASC") #selects all distinct categories from food bank database
    categories = []
    #for each row in the databsae
    for row in cursor:
        #grab the category and appends to return value
        for col in row:
            categories.append(col)
    return categories

def connectToDatabase():
    """ connectToDatabase(user, password, host, port, database)
    user: username
    password: user's password
    host: server name
    port: port number
    database: database name
    This function creates a connection to the MySQL database.
    """
    dbconnect = None #Initialize variable to connection
    counter = 0 #initialize counter for connection tries
    while dbconnect is None: #while the connection is not initialized we will keep trying to connect
        if (counter >= 4): #once 4 connection attempts have been failed, exit the program.
            print("Check connection to internet")
            exit()
        try:
            dbconnect = mysql.connector.connect(
                host=host,
                user=user,
                passwd=password,
                port=port,
                database=database) #use mysql connector with the database parameters for a connection
            # print("Connected")
        except:
            print("Connection failed") #when connection fails, catch exception 
            dbconnect = None
            counter += 1 #increment counter by 1
    return dbconnect #return connection to file calling function.