"""
File Name: DonorUI.py
Program Name: Food for You

Created: 3/1/2023
Last Modified: 3/12/2023

Author: Linnea Gilius

This file is a subsystem of Food for You which provides a graphical user interface and functions for a donor user to search for food banks matching their needs.

Modifications:
    March 1, 2023: created file and implemented get_locations(), get_category(), and get_hours(), LG
    March 3, 2023: created the DonorGUI class constructor
    March 4, 2023: implemented the query() method of the DonorGUI class
    March 7, 2023: implemented the get_food_bank_info, is_open(), and format_results() methods of the DonorGUI class
    March 10, 2023: implemented the write_file method of the DonorGUI class
    March 11, 2023: cleaned up code and added comments
    March 12, 2023: added more comments
"""

# libraries used
from tkinter import *
import mysql.connector as mysql
import datetime

# modules
from utilffy import *


def get_locations(cursor):
    """
    function which retrieves all neighborhoods which contain a food bank,
    formatted for a dropdown menu

    parameter: MySQL Connector Cursor (mysql.connector.cursor.MySQLCursor)
    """

    # executes SQL query
    cursor.execute("SELECT DISTINCT Neighborhood FROM foodforyou.food_bank ORDER BY Neighborhood")
    # retrieves a list of neighborhoods, sorted in alphabetical order
    neighborhoods = cursor.fetchall()

    # formats list of neighborhoods
    locations = [area[0] for area in neighborhoods]
    # inserts "All Locations" into the head of the list
    # formatting for a dropdown menu
    locations.insert(0, "All Locations")

    return locations


def get_category(cursor):
    """
    function which retrieves all food categories in the database,
    formatted for a dropdown menu

    parameter: MySQL Connector Cursor (mysql.connector.cursor.MySQLCursor)
    """

    # executes SQL query
    cursor.execute("SELECT DISTINCT Category FROM foodforyou.food_item ORDER BY Category")
    # retrieves a list of food categories, sorted in alphabetical order
    foods = cursor.fetchall()

    # formats list of food categories
    categories = [food[0] for food in foods]
    # inserts "All Categories" into the head of the list
    # formatting for a dropdown menu
    categories.insert(0, "All Categories")
    return categories


def get_hours(cursor, fb_id):
    """
    function which retrieves the hours of operation for the food bank specified by the fb_id

    parameters: MySQL Connector Cursor (mysql.connector.cursor.MySQLCursor)
                Food Bank ID (int)
    """

    # checks that fb_id is an integer
    if type(fb_id) is not int:
        print("ERROR: food bank ID must be an int")
        return [('', '')]

    # retrieves name of the current day of the week
    day = datetime.datetime.today().strftime('%A')

    # executes the SQL query
    query = f"SELECT {day}, {day}_close FROM hours WHERE fb_ID = {fb_id}"
    cursor.execute(query)

    # retrieves and returns a list of hours
    hours = cursor.fetchall()
    return hours


class DonorGUI:
    """
    class DonorGUI
        creates the graphical user interface for the donor user
        allows the user to search by location and/or food category
        allows the user to only see the food banks which are open at the time the program is run
        allows the user to select to display the address, hours, and/or phone number of food banks
    """
    def __init__(self):
        """
        Donor GUI constructor
        """

        # creates a tkinter window
        self.interface = Tk()
        interface = self.interface
        # use the theme from utiliffy.py
        use_theme(interface, "12")

        # sets the window size and title
        self.interface.geometry('430x540')
        self.interface.title('Food4You Food Bank Finder')
        self.interface.resizable(False, False)

        # establishes connection to Food Resource Database
        self.connection = connectToDatabase()
        self.cursor = self.connection.cursor()
        assert self.connection
        assert self.cursor

        # retrieves the list of all neighborhoods
        self.all_locations = get_locations(self.cursor)
        # creates the variable for the location dropdown menu and sets it to the first option
        self.location = StringVar()
        self.location.set(self.all_locations[0])

        # retrieves the list of all food categories
        self.all_categories = get_category(self.cursor)
        # creates the variable for the food category dropdown menu and sets it to the first option
        self.category = StringVar()
        self.category.set(self.all_categories[0])

        # creates the display variables and sets them all to 0
        self.open_now = IntVar()
        self.open_now.set(0)
        self.address = IntVar()
        self.address.set(0)
        self.hours = IntVar()
        self.hours.set(0)
        self.phone = IntVar()
        self.phone.set(0)

        # creates dictionary to hold food bank information
        self.fb_info = {}

        # displays background images for the tkinter window
        try:
            self.background = PhotoImage(file="img/backgroundimg.png")
            Label(master=interface, image=self.background, borderwidth=0, highlightthickness=0).place(relx=-.15, rely=0)
        except Exception as background_e:
            print(f"ERROR in background image: {background_e}")

        try:
            self.trailing_img = PhotoImage(file="img/trailingIMG.png")
            for i in range(0, 480, self.trailing_img.width()):
                Label(master=interface, image=self.trailing_img, bg='white').place(x=i, y=480)
        except Exception as trailing_e:
            print(f"ERROR in trailing image: {trailing_e}")

        def window():
            """
            function which creates the tkinter window
            """
            # creates the location dropdown and displays it in the tkinter window
            neighborhood_label = ttk.Label(interface, text='search by neighborhood: ')
            neighborhood_menu = OptionMenu(interface, self.location, *self.all_locations)
            neighborhood_label.pack()
            neighborhood_label.place(relx=0.3, rely=0.3, anchor=CENTER)
            neighborhood_menu.pack()
            neighborhood_menu.place(relx=0.7, rely=0.3, anchor=CENTER)

            # creates the food category dropdown and displays it in the tkinter window
            category_label = ttk.Label(interface, text='search by food category: ')
            category_menu = OptionMenu(interface, self.category, *self.all_categories)
            category_label.pack()
            category_label.place(relx=0.3, rely=0.4, anchor=CENTER)
            category_menu.pack()
            category_menu.place(relx=0.7, rely=0.4, anchor=CENTER)

            # creates the checkboxes for the display variables and displays them in the tkinter window
            # open_now display variable
            open_label = ttk.Label(interface, text='show only open now')
            open_check = ttk.Checkbutton(interface, variable=self.open_now)
            open_label.pack()
            open_label.place(relx=0.35, rely=0.55, anchor=CENTER)
            open_check.pack()
            open_check.place(relx=0.65, rely=0.55, anchor=CENTER)

            # hours display variable
            hours_label = ttk.Label(interface, text='show hours for today')
            hours_check = ttk.Checkbutton(interface, variable=self.hours)
            hours_label.pack()
            hours_label.place(relx=0.35, rely=0.60, anchor=CENTER)
            hours_check.pack()
            hours_check.place(relx=0.65, rely=0.60, anchor=CENTER)

            # address display variable
            address_label = ttk.Label(interface, text='show address')
            address_check = ttk.Checkbutton(interface, variable=self.address)
            address_label.pack()
            address_label.place(relx=0.35, rely=0.65, anchor=CENTER)
            address_check.pack()
            address_check.place(relx=0.65, rely=0.65, anchor=CENTER)

            # phone number display variable
            phone_label = ttk.Label(interface, text='show phone number')
            phone_check = ttk.Checkbutton(interface, variable=self.phone)
            phone_label.pack()
            phone_label.place(relx=0.35, rely=0.70, anchor=CENTER)
            phone_check.pack()
            phone_check.place(relx=0.65, rely=0.70, anchor=CENTER)

        # creates the tkinter window
        window()

        def search():
            """
            function called upon clicking the "search" button
            retrieves user input from tkinter window
            """

            # retrieves user input
            self.location = self.location.get()
            self.category = self.category.get()
            self.open_now = self.open_now.get()
            self.hours = self.hours.get()
            self.address = self.address.get()
            self.phone = self.phone.get()

            interface.destroy()
            self.query()

        # creates the search button and displays it in the tkinter window
        search_button = ttk.Button(interface, text='search', command=search)
        search_button.pack()
        search_button.place(relx=0.5, rely=0.8, anchor=CENTER)
        interface.update()

        # starts the main loop
        self.interface.mainloop()

    def query(self):
        """
        function which retrieves all food banks which match the user's preferences
        """

        # sets neighborhood and category local variables to location and category instance variables
        neighborhood = self.location
        category = self.category

        # format neighborhood and category for the SQL query
        if neighborhood == "All Locations":
            neighborhood = "%"
        if category == "All Categories":
            category = "%"

        # creates the SQL query which retrieves all food banks which match the user's preferences
        query = f"SELECT temp.fb_ID, temp.Location, SUM(temp.total) AS final_total " \
                f"FROM food_bank fb JOIN " \
                f"(SELECT fi.fb_ID, fi.Location, fi.Category, SUM(fi.Quantity) AS total " \
                f"FROM food_item fi " \
                f"WHERE fi.Category LIKE '{category}' " \
                f"GROUP BY fi.fb_ID, fi.Location, fi.Category) AS temp USING(fb_ID, Location) " \
                f"WHERE fb.Neighborhood LIKE '{neighborhood}' " \
                f"GROUP BY temp.fb_ID, temp.Location " \
                f"ORDER BY final_total"

        # executes the SQL query and returns results
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        self.format_results(results)

    def get_food_bank_info(self, fb_id):
        """
        function which retrieves the address, phone number, and name for the food bank specified by the fb_id

        parameter: Food Bank ID (int)
        """

        # creates the SQL query which retrieves the address, phone number, and name
        # for the food bank specified by the food bank ID
        query = f"SELECT Address, Phone_number, Location FROM food_bank " \
                f"WHERE fb_ID = {fb_id}"

        # executes the SQL query and returns results
        self.cursor.execute(query)
        fb_info = self.cursor.fetchall()
        return fb_info

    def is_open(self, fb_id):
        """
        function which checks if the food bank specified by the fd_id is open at the time of DonorUI being run

        parameter: Food Bank ID (int)
        """

        # retrieves the "current" hour and minute, where current is the time at which DonorUI.py was run
        hour = datetime.datetime.now().hour
        minute = datetime.datetime.now().minute
        # formats the time
        now = f"{hour}:{minute:02}:00"

        # retrieves the hours of operation for the food bank specified by the given fb_id
        hours = get_hours(self.cursor, fb_id)
        opening = hours[0][0]
        closing = hours[0][1]

        invalid_hours = ['', "", ' ', " "]
        # food bank is closed today
        if (opening in invalid_hours) or (closing in invalid_hours):
            now_open = False
        # food bank is always open
        elif (opening == '00:00:00') and (closing == '00:00:00'):
            now_open = True
        else:
            # checks if the current time is within the hours of operation
            now_open = (now >= opening) and (now <= closing)
        return now_open

    def format_results(self, results):
        """
        function which formats the results of the SQL query

        parameter: results (list of lists)
        """

        fb_ids = []
        fb_info = {}
        # creates a dictionary to contain the length of the longest address, name, and phone number for formatting purposes
        max_lengths = {"address": 5, "location": 1, "phone": 1}

        # iterates over each item in results
        for item in results:
            fb_id, category, total = item
            fb_id = int(fb_id)

            # if the user opted to only show food banks currently open
            if self.open_now:
                if not self.is_open(fb_id):
                    continue

            # if the food bank has not been processed
            if fb_id not in fb_info:
                fb_ids.append(fb_id)
                info = self.get_food_bank_info(fb_id)
                address, phone, location = info[0][0], info[0][1], info[0][2]

                # strips address of newline character
                address.strip()
                if address[-1:] == "\n":
                    length = len(address)
                    address = address[:length - 1]
                max_lengths["address"] = max(max_lengths["address"], len(address))

                # strips phone number of newline character
                phone.strip()
                if phone[-1:] == "\n":
                    length = len(phone)
                    phone = phone[:length - 1]
                max_lengths["phone"] = max(max_lengths["phone"], len(phone))

                # strips name of newline character
                location.strip()
                if location[-1:] == "\n":
                    length = len(location)
                    location = location[:length - 1]
                max_lengths["location"] = max(max_lengths["location"], len(location))

                # append food bank information to food bank dictionary
                fb_info[fb_id] = [address, location, phone]

                if self.hours:
                    fb_info[fb_id].append(get_hours(self.cursor, fb_id))

        self.fb_info = fb_info
        self.write_file(fb_ids, max_lengths)

    def write_file(self, fb_ids, max_lengths):
        """
        function which writes results to file

        parameters: Food Bank ID's (list)
                    max_lengths (dictionary, for formatting purposes)
        """

        # strips location and category of all spaces
        location = "".join(str(self.location).split())
        category = "".join(str(self.category).split())

        # creates the name of the file which will be written to
        filename = f"FoodNeedsAt{location}For{category}.txt"

        # retrieves the length of the longest address, name, and phone number for formatting purposes
        max_address = max_lengths["address"]
        max_location = max_lengths["location"]
        max_phone = max_lengths["phone"]

        with open(filename, "w") as f:
            # writes the header
            f.write(f"Results for Food Banks in {self.location} in Need of {self.category}\n")

            if self.open_now:
                f.write("showing those open now\n")

            # if there is no data
            if len(fb_ids) == 0:
                f.write("No Results")
            else:
                # write the header
                f.write(f"Name{' ':{max_location}}")
                if self.address:
                    f.write(f"Address {' ':{max_address - 4}}")
                if self.hours:
                    f.write(f"Hours {' ':18}")
                if self.phone:
                    f.write(f"Phone # {' ':{max_phone}}")

            f.write("\n")

            # iterates over each food bank in fb_ids list
            for food_bank in fb_ids:
                location = self.fb_info[food_bank][1]
                f.write(f"{location:{max_location + 4}}")

                # if the user opted to show addresses
                if self.address:
                    f.write(f"{self.fb_info[food_bank][0]:{max_address + 4}}")

                # if the user opted to show hours
                if self.hours:
                    # retrieves the hours of operation for the food bank
                    hours = self.fb_info[food_bank][3]
                    opening = hours[0][0]
                    closing = hours[0][1]

                    invalid_hours = ['', "", ' ', " "]
                    # food bank is closed today
                    if (opening in invalid_hours) or (closing in invalid_hours):
                        hours = "Closed Today"
                    else:
                        hours = f"{opening} - {closing}"

                    f.write(f"{hours:24}")

                # if the user opted to show phone number
                if self.phone:
                    f.write(f"{self.fb_info[food_bank][2]:{max_phone}}")

                f.write("\n")
            f.write("\n")

        # displays results on standard output
        with open(filename, "r") as f:
            lines = f.readlines()
            for line in lines:
                print(line.strip())


# create a DonorGUI instance
donor = DonorGUI()
# closes database connection
donor.connection.close()
