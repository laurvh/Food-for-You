Description: The Food-For-You program is a tool meant for those who are facing food insecurity to have a 
reliable and easy to use way to find the resources they need. The recipient interface will allow these users
to obtain a list of foods at individual food banks and whether or not that food bank is open at the current 
time the data is pulled. This allows the user to both see what food is available and conveniently see what is 
currently open as the times for all the food pantries are scattered. This program will also allow donors 
to see what is in low stock at food pantries to see what items are in need of donations. This interface
will also show what locations are currently open. Lastly, this program is also meant to aid the staff at food 
banks and food pantries by allowing the easy manipulation of what data is stored in the system. The staff are 
able to search for items, add items, move items to different locations, and update what quantities are available. 
Whenever an item is updated to be a lower quantity it is also recorded so administrators can see trends that can 
help them improve the services they offer to the community. This can be accessed through an admin interface where
current items can be exported to a csv, and the administrators can add new food pantries with the option to bulk 
add food items via a file upload. The data populated in the system is fake data as the spreadsheet used to order 
items to food pantries could not be shared by the individuals we interviewed.

Authors: Linnea Gilius, Krishna Patel, Jerry Pi, Lauren Van Horn

Date Created: 2/19/2023

Why project was created: This project is created for CS 422 at University of Oregon and is taught by Anthony Hornof. 
The purpose of this project is to simplify the process of donating to and receiving from a food bank.

How to run the program files:
    1. Unzip the source file once it is downloaded into a folder called “Food-For-You”.
    2. Open the terminal on your computer. (Powershell on Windows, Terminal on Mac.)
    3. Navigate to the directory where the file is downloaded to. This is usually done by typing “cd Downloads/Food-For-You” 
    and pressing return. If the file is in a different directory type “cd  your_directory_path/Food-For-You” and press enter. 
    4. If you do not have Python 3.x installed, go to https://www.python.org/downloads/ to download and install the latest version.
    5. If you do not have mysql-connector, or tkinter installed, type “pip3 install mysql.connector-python” to and press return 
    to install mysql-connector, and type “pip3 install tk” to install tkinter.
    6. Once step 5 is finished, type “python3 <interface>” in your terminal where <interface> is replaced by the file you 
    want to execute from the options “staffUI.py,” “AdminView.py,” “RecipientUI.py,” “DonorUI.py”
    To see how to use these individual files, see Section 5, “Use Cases” in the User Documenation.
    If you need to reinitialize the database values, please see Section 4 “Database Installation.”


Software Dependencies: Python3, mysql.connector-python, tkinter

Directory Structure:
    1. "Food-For-You": Contains all python files needed to run the program (utilffy.py, AdminView.py, staffUI.py,
    timepicker.py, DonorUI.py, RecipientUI.py), a sample new food bank file (SampleNewFoodBankData.csv), a copy of the database exported in a sql file (422-finalv2.sql), and the README.txt.
    2. "Documenation": Contains all required documentation such as SRS, SDS, Project Plan, User Documenation, and 
    Programmer Documenation.
    3. "img": Contains all images used by tkinter for our interface themes.
