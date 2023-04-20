"""
File Name: RecipientUI.py
Program Name: Food for You
File purpose: This file is a subsystem of the Food for You program that streamlines a food resource
                database between three different user categories——Food Recipient, Food Donor, and
                Food Bank Staff. This File implements the Food Recipient use case.
                This file is the user interface that the food recipient uses to see food availability
                at different neighborhood foodbanks. The user can either select a specific food
                category and/or neighborhood. If no food category or neighborhood is selected,
                the program defaults to pulling all data for food categories and/or neighborhoods
Creation date: Feb 27th, 2023
Initial Authors: Lauren Van Horn
References used:
    tkinter creation learned from:https://www.youtube.com/watch?v=YXPyB4XeYLA
    tkinter view learned from:: https://blog.csdn.net/u013278255?type=blog
    tkinter function calls by button learned from: https://www.tutorialspoint.com/call-a-function-with-a-button-or-a-key-in-tkinter
    mysql display learned from:https://www.plus2net.com/python/tkinter-mysql.php
Modification Date: February 27rd, 2023 - created document and built user interface, LVH
    February 28th, 2023 - added search_database() function, LVH
    March 1st, 2023 - updated search_database() to be more robust, LVH
    March 3rd, 2023 - added writetofile(filename, results, open_stat) function, LVH
    March 6th, 2023 - added opennow(neighborhood) function, LVH
    March 7th, 2023 - added more formal connection to database function, LVH
    March 9th, 2023 - added comments, LVH
    March 11th, 2023 - added checkboxes, LVH
    March 12th, 2023 - cleaned up code and added more commentary, LVH
"""
import tkinter as tk
import datetime
from utilffy import *

# Connect to database
connection = connectToDatabase()
# Store connection as c
c = connection.cursor()

# get the food options from the database, store it in food_options
c.execute("SELECT DISTINCT Item_name FROM food_item")
food_options = [row[0] for row in c.fetchall()]

#get neighborhood options from database, store it in neighborhood_options
c.execute("SELECT DISTINCT Neighborhood FROM food_bank")
neighborhood_options = [row[0] for row in c.fetchall()]

# create the GUI window
root = tk.Tk()
root.title("Food-For-You Recipient")
# window size
root.geometry("430x540")
root.resizable(False, False)
# Apply style to gui
use_theme(root, "12")

# Check to see if we can include the photo images
try:
    # This is setting the background/Title image
    root.bg = tk.PhotoImage(file="img/backgroundimg.png")
    tk.Label(image=root.bg, borderwidth=0, highlightthickness=0).place(relx=-.15, rely=0)

    # This is setting the little people across the bottom of the UI
    root.trailing_img = tk.PhotoImage(file="img/trailingIMG.png")
    # Repeat image to fill entire space across the bottom
    for i in range(0, 480, root.trailing_img.width()):
        tk.Label(root, image=root.trailing_img, bg='white').place(x=i, y=480)
# If something goes wrong, print the message
except Exception as e:
    print(e)

# create the food category dropdown
food_label = ttk.Label(root, text="Select a food category:")
food_label.pack()
food_label.place(relx=0.5, rely=0.26, anchor=tk.CENTER)
# add a blank option to the list of food options
food_options.insert(0, "All Food")
# create the variable for the food dropdown and set it to the first option
food_var = tk.StringVar(root)
food_var.set(food_options[0])
# create the food dropdown with the blank option
food_dropdown = tk.OptionMenu(root, food_var, *food_options)
food_dropdown.pack()
food_dropdown.place(relx=0.5, rely=0.33, anchor=tk.CENTER)

# create the neighborhood dropdown
neighborhood_label = ttk.Label(root, text="Select a neighborhood:")
neighborhood_label.pack()
neighborhood_label.place(relx=0.5, rely=0.43, anchor=tk.CENTER)
# add a blank option to the list of neighborhoods
neighborhood_options.insert(0, "All Neighborhoods")
# create the variable for the neighborhood dropdown and set it to the first option
neighborhood_var = tk.StringVar(root)
neighborhood_var.set(neighborhood_options[0])
# create the neighborhood dropdown with the blank option
neighborhood_dropdown = tk.OptionMenu(root, neighborhood_var, *neighborhood_options)
neighborhood_dropdown.pack()
neighborhood_dropdown.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# create phone number checkbox
phone_var = tk.BooleanVar(root)
phone_checkbox = ttk.Checkbutton(root, text="Show Phone Number", variable=phone_var)
phone_checkbox.pack()
phone_checkbox.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

# create street address checkbox
address_var = tk.BooleanVar(root)
address_checkbox = ttk.Checkbutton(root, text="Show Street Address", variable=address_var)
address_checkbox.pack()
address_checkbox.place(relx=0.5, rely=0.65, anchor=tk.CENTER)

# create hours checkbox
hours_var = tk.BooleanVar(root)
hours_checkbox = ttk.Checkbutton(root, text="Show Today's Hours", variable=hours_var)
hours_checkbox.pack()
hours_checkbox.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

# create hours checkbox
opennow_var = tk.BooleanVar(root)
opennow_checkbox = ttk.Checkbutton(root, text="Only Show Open Now", variable=opennow_var)
opennow_checkbox.pack()
opennow_checkbox.place(relx=0.5, rely=0.75, anchor=tk.CENTER)

def opennow(neighborhood) -> list:
    """ opennow(neighborhood: str):
        Takes in neighborhood name, neighborhood and pulls from database to check if the foodbanks in
        that neighborhood are currently open
        - Parameters
            neighborhood is the name of the neighborhood the user selected in the dropdown menu
        - Output
            Returns list, open_stat of all foodbanks that are currently open. If no food banks are currently open,
            it returns an empty list
        Note: If the user selected "All Neighborhoods" the function pulls the open now stat for every food bank
            Hours are stored as Military time
    """
    # List of days of the week
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    # Get the current date and time
    today = datetime.datetime.now()
    # Translate the time to military
    time_str = today.strftime("%H:%M")
    # Gets the current day index
    dayofweek = today.weekday()
    # Translate the day index into day name
    day = days[dayofweek]
    # Empty list of currently open food banks
    open_stat = []
    # Base query, using day of the week
    # Selects the open and close time of a specific location from the hours table
    # Also selects the location from food_bank table
    # The open and close times are not null
    query = (f"SELECT h.{day}, h.{day}_close, fb.Location "
             f"FROM hours h "
             f"JOIN food_bank fb USING(fb_id) "
             f"WHERE h.{day} <> '' AND h.{day}_close <> '' ")

    # If a specific neighborhood is chosen, filter results by neighborhood
    if neighborhood != "All Neighborhoods":
        # update query string
        query += f"AND fb.Neighborhood = '{neighborhood}'"

    # Execute the query
    c.execute(query)

    # Store the results of the query is variable hours
    hours = c.fetchall()
    # Check if nothing was pulled
    if len(hours) == 0:
        # If nothing is pulled, return an empty list
        return open_stat, hours
    # Step through each food bank that has hours during this weekday
    for entry in hours:
        # Check if current time is greater than the Open Time and less than the Close Time of food bank
        if entry[0] <= time_str <= entry[1]:
            # Check food bank isn't already in the list
            if entry[2] not in open_stat:
                # Add the food bank to the list
                open_stat.append(entry[2])
    # Return a list of Open food banks and results from query
    return open_stat, hours

def writetofile(filename, results, open_stat, open_time, food, neighborhood):
    """ writetofile(filename: str, results: list, open_stat: list):
            Takes in filename, results list from database query, and a list of open food banks and formats
            the data to print to stdout as well as writes to filename. This way, the user can store the file
            and print it out if they won't have access to internet in the soon future
            - Parameters
                filename: name of file to write pulled data to
                results: list of data pulled from the search_database query
                open_stat: list of food banks that are currently open
                open_time: results of query
            - Output
                No set return, but does create a file named after filename input and prints data
                to stdout
        """
    # Check if the user only wants to see Open food banks
    if opennow_var.get():
        # Check if there are no open food banks
        if open_stat == []:
            # Alerts the user to the empty results
            print(f"No Food Banks are currently open.\n"
                  f"Please either select a different neighborhood or allow closed Food Banks. Thank you!\n")
            # Exit
            return
    # Open filename as f
    with open(filename, 'w') as f:
        # next chunk of code is used to calculate the max length of each field to help with formatting
        # Set Default values for open and close max
        maxopen = 5
        maxclose = 5
        # Ensure that open_time isn't empty
        if open_time != []:
            # max open time length
            maxopen = max(len(entry[0]) for entry in open_time)
            # max close time length
            maxclose = max(len(entry[1]) for entry in open_time)
        # max item length
        maxitem = max(len(entry[0]) for entry in results)
        # max location legnth
        maxlocation = max(len(entry[1]) for entry in results)
        # max status length
        maxstatus = max(len(entry[4]) for entry in results)
        # max address length
        maxaddress = max(len(entry[2]) for entry in results)

        # minstat checks if every item is listed as unavailable
        minstat = min(len(entry[4]) for entry in results)

        # check if every status is set to unavailable
        if minstat == 11:
            # Alerts the user to there was no food available
            print(f"{food} is not available at the food banks located in {neighborhood}. "
            f"Please either select a different food item or neighborhood. Thank you!")
            # Exit
            return

        # Prints an error informing statement for the User to understand the ordering of entries
        f.write(f"Entries are listed in Descending order by Quantity.\n"
                f"Entries at the top of the table have the greatest availabilty.\n"
                f"Entries marked as Low Stock have 20 units or less available.")
        print(f"Entries are listed in Descending order by Quantity.\n"
              f"Entries at the top of the table have the greatest availabilty.\n"
              f"Entries marked as Low Stock have 20 units or less available.\n")

        # Use the max length variables to create space buffers
        # Item space buffer
        ispace = (maxitem + 5 - 4) * " "
        #location space buffer
        lspace = (maxlocation + 5 - 8) * " "
        # status space buffer
        sspace = (maxstatus + 5 - 6) * " "
        # address space buffer
        aspace = (maxaddress + 5 - 8) * " "
        # phone space buffer
        pspace = (14 + 5 - 12) * " "
        # open time space buffer
        ospace = (maxopen + 5 - 4) * " "
        # close time space buffer
        cspace = maxclose * " "
        # Write the headers to filename
        if address_var.get() and phone_var.get() and hours_var.get():
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Address{aspace}Phone Number{pspace}Open{ospace}Close{cspace}Hours")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + maxaddress + 75) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Address{aspace}Phone Number{pspace}Open{ospace}Close{cspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-" * (maxitem + maxlocation + maxaddress + 75))
        elif address_var.get() and hours_var.get():
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Address{aspace}Open{ospace}Close{cspace}Hours\n")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + maxaddress + maxopen + maxclose + 48) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Address{aspace}Open{ospace}Close{cspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-" * (maxitem + maxlocation + maxaddress + maxopen + maxclose + 48))
        elif address_var.get():
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Address{aspace}Hours\n")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + maxaddress + 34) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Address{aspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-" * (maxitem + maxlocation + maxaddress + 34))
        elif phone_var.get() and hours_var.get():
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Phone Number{pspace}Open{ospace}Close{cspace}Hours\n")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + maxopen + maxclose + 60) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Phone Number{pspace}Open{ospace}Close{cspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-" * (maxitem + maxlocation + maxopen + maxclose + 60))
        elif phone_var.get():
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Phone Number{pspace}Hours\n")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + 50) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Phone Number{pspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-" * (maxitem + maxlocation + 50))
        elif hours_var.get():
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Open{ospace}Close{cspace}Hours\n")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + 65) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Open{ospace}Close{cspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-" * (maxitem + maxlocation + 65))
        else:
            f.write(f"Item{ispace}Location{lspace}Status{sspace}Hours\n")
            # Write a dashed line for Visual ease in filename
            f.write('-' * (maxitem + maxlocation + 34) + '\n')
            # Write headers to stdout
            print(f"Item{ispace}Location{lspace}Status{sspace}Hours")
            # Write a dashed line for visual ease in stdout
            print("-"*(maxitem + maxlocation + 34))

        # Step through each entry in results
        for entry in results:
            # Get the food name, location name, address name, phone number, and status
            fname, lname, aname, pname, stat = (entry[i].rstrip() for i in range(5))
            # Create dynamic space buffers for each field. First letter of variable denotes which
            # variable it is holding (i.e. fspace -> food space, lspace -> location space)
            # food space buffer
            fspace = (maxitem + 5 - len(fname)) * " "
            # location space buffer
            lspace = (maxlocation + 5 - len(lname)) * " "
            # address space buffer
            aspace = (maxaddress + 4 - len(aname)) * " "
            # phone space buffer
            pspace = (14 + 5 - len(pname)) * " "
            # stat space buffer
            sspace = (maxstatus + 5 - len(stat)) * " "

            # initialize open hour time to be blank, will fill in later
            openh = ""

            # If the food is unavailable, don't display it
            if stat == "Unavailable":
                # move on to next entry
                break

            # Check if there is an open food bank
            if open_stat != []:
                # If location is in open_stat, it's open now
                if lname in open_stat:
                    hours = "Open Now"
                    for entry in open_time:
                        # match up the location name in open_time to lname
                        if entry[2] == lname:
                            # Grab the open and close times and set it for openh and close h, strip and trailing \n
                            openh = entry[0].rstrip()
                            closeh = entry[1].rstrip()
                # Location isn't open now
                else:
                    # set everything (hours, openh, closeh) to be closed
                    hours = "Closed"
                    openh = "Closed"
                    closeh = "Closed"
            # Location isn't open now
            else:
                hours = "Closed"
                # Check if location is open at some point today
                for entry in open_time:
                    # match up the location name in open_time to lname
                    if entry[2] == lname:
                        # Grab the open and close times and set it for openh and close h, strip and trailing \n
                        openh = entry[0].rstrip()
                        closeh = entry[1].rstrip()
                # If we still haven't set open, it's closed
                if openh == "":
                    # Set to closed
                    openh = "Closed"
                    closeh = "Closed"

            # Create space buffers for open (ospace) and close (cspace)
            ospace = (maxopen + 5 - len(openh)) * " "
            cspace = (maxclose + 5 - len(closeh)) * " "


            # Now we print everything out, but must specify based on what was selected
            # If we only want to see open now
            if opennow_var.get():
                # Check if hours are set to Open Now
                if hours == "Open Now":
                    # Each of the following print statements prints selected info details first to filename and then to stdout
                    # Check if the FB is open now and if the user has selected all three checkboxes
                    if address_var.get() and phone_var.get() and hours_var.get():
                        # Write to file
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                        # Write to stdout
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}")
                    # Check if the FB is open now and the user has selected the address and hours checkboxes
                    elif address_var.get() and hours_var.get():
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{openh}{ospace}{closeh}{cspace}{hours}")
                    # Check if the FB is open now and the user has selected the address checkbox
                    elif address_var.get():
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{hours}\n")
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{hours}")
                    # Check if the FB is open now and the user has selected the phone and hours checkboxes
                    elif phone_var.get() and hours_var.get():
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}")
                    # Check if FB is open now and user has selected phone checkbox
                    elif phone_var.get():
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{hours}\n")
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{hours}")
                    # Check if FB is open now and user has selected hours checkbox
                    elif hours_var.get():
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{openh}{ospace}{closeh}{cspace}{hours}")
                    # Check if FB is open now, no checkboxes were selected
                    else:
                        f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{hours}\n")
                        print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{hours}")
            # User doesn't care if FB is open now
            else:
                # Check if user selected address, phone, and hours checkbox
                if address_var.get() and phone_var.get() and hours_var.get():
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}")
                # Check if user selected address and hours checkbox
                elif address_var.get() and hours_var.get():
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{openh}{ospace}{closeh}{cspace}{hours}")
                # User only selected address checkbox
                elif address_var.get():
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{aname}{aspace}{hours}")
                # User selected both phone and hours checkbox
                elif phone_var.get() and hours_var.get():
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{openh}{ospace}{closeh}{cspace}{hours}")
                # User selected only phone checkbox
                elif phone_var.get():
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{pname}{pspace}{hours}")
                # User only selected hours checkbox
                elif hours_var.get():
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{openh}{ospace}{closeh}{cspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{openh}{ospace}{closeh}{cspace}{hours}")
                # No checkboxes were selected
                else:
                    f.write(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{hours}\n")
                    print(f"{fname}{fspace}{lname}{lspace}{stat}{sspace}{hours}")
        # Print newlines so there is space between requests
        print("\n")


def search_database():
    """ search_database():
                performs queries based on what the user has selected from the UI
            - Parameters
                no parameters, but does pull information from the dropdowns on the UI
            - Output
                returns the results in a list variable, results
    """
    # Get the user selection of food category
    food = food_var.get()
    # Get the user neighborhood selection
    neighborhood = neighborhood_var.get()

    # This is our base select clause, everything the user might want to reference
    select_clause = "SELECT fi.Item_name, fi.Location, fb.Address, fb.Phone_number, "
    # Clause that labels quantities
    stock_status_clause = "CASE WHEN Quantity = 0 THEN 'Unavailable' " \
                          "WHEN Quantity < 21 THEN 'Low Stock' ELSE 'Available' END AS stock_status "
    # Where we are pulling data from
    from_clause = "FROM food_item fi " \
                  "LEFT JOIN food_bank fb USING(fb_ID) "
    # How we want to order the data
    order_by_clause = "ORDER BY fi.Quantity DESC"

    # Checks if any specifications were made
    if neighborhood == "All Neighborhoods" and food == "All Food":
        # None were made, so no need for a where_clause
        where_clause = ""
    # A food selection was made, but not a neighborhood selection
    elif neighborhood == "All Neighborhoods":
        # Add to query to specify the food category
        where_clause = f"WHERE fi.Item_name = '{food}' "
    # A neighborhood selection was made, but not a food selection
    elif food == "All Food":
        # Add to query to specify the neighborhood category
        where_clause = f"WHERE fb.Neighborhood = '{neighborhood}' "
    # Both a food and a neighborhood selection were made
    else:
        # Add to query to specify the food category and neighborhood
        where_clause = f"WHERE fi.Item_name = '{food}' AND fb.Neighborhood = '{neighborhood}' "

    # Format the query
    query = select_clause + stock_status_clause + from_clause + where_clause + order_by_clause
    # Execute the query
    c.execute(query)
    # Store the query return in results
    results = c.fetchall()

    # Return results, and the food and neighborhood user selections
    return results, food, neighborhood


def main():
    """ main():
                once the user presses the submit button, it calls search_database(), creates filename
                calls opennow(), and writetofile(filename, results, open_stat, open_time)
            - Parameters
                no parameters
            - Output
                no returns, but does print an error statement is we return an empty query
    """
    # Search the database
    results, food, neighborhood = search_database()
    # Check if there was an empty query result return
    if results == []:
        # Alerts the user to the empty results
        print(f"{food} is not available at the food banks located in {neighborhood}. "
            f"Please either select a different food item or neighborhood. Thank you!")
        # Exit
        return

    # Check hours of Food Banks with opennow()
    open_stat, open_time = opennow(neighborhood)
    # Create a file named after food and neighborhood selections
    filename = f"{food}AvailabilityAt{neighborhood}.txt"
    # Write everything to stdout and file named filename
    writetofile(filename, results, open_stat, open_time, food, neighborhood)


# create the search button
search_button = ttk.Button(root, text="Search", command=main)
search_button.pack()
search_button.place(relx=0.5, rely=.8, anchor=tk.CENTER)

# create the label to display the results
result_label = ttk.Label(root, text="")
result_label.pack()

# start the main loop
root.mainloop()

# close the database connection when finished
connection.close()
