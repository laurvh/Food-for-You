"""
Name: AdminView.py
Created: 3/5/2023
Authors: Katherine Smirnov, Krishna Patel

Provides a view of the Outgoing database with searching/filtering functionality,
and allows for a new food bank insertion to the Food Bank database.


Modifications:
    3/5/2023: Created validateFile() to check for headers and quantity -KS
              Added timepicker function for inputting times for newFB -KS
    3/8/2023: Added tabs to view FB and data log -KS
    3/9/2023: Added export buttons -KS
    3/10/2023: Cleaned up UI -KS
               Add export function -KP
               Added error checking for times -KP
    3/11/2023: Add neighborhood and phone number input to newFB -KS
               Added validate phone number function -KS

Table used:
    Outgoing
    Food Banks
    Food Items

References:
    EasyA, admin.py from Jerry Pi
        -Recycled code to display database in a table and update items in database

Notes:
    Abbreviations:
        - FB: Food Bank
"""
from utilffy import *
from tkinter import filedialog
import timepicker as time           #necessary for time widget in addFB screen
import csv
import os
import datetime


FBconnection = connectToDatabase()
#FBconnection = connectToDatabase("kp", "pass", "127.0.0.1", 3306, "foodforyou")
FBcursor = FBconnection.cursor()

Dconnection = connectToDatabase()
#Dconnection = connectToDatabase("kp", "pass", "127.0.0.1", 3306, "foodforyou")
Dcursor = Dconnection.cursor()

class FBView:
    """FBView: class
        GUI which allows the user to insert a new food bank, and view the newly inserted data.
    """
    def __init__(self, parent):
        #----------------------setting up screen for "New Food Bank"---------
        self.root = Frame(parent, bg="white")

        global fetchData

        def fetchData(newFBID:int):
            """
                Grabs data in database of the newly inserted food bank, and places in table
                Input: newFBID is the new food bank
            """
            FBcursor.execute(                   # selects all rows/columns from food item table with the food bank location which is known from the new FB ID
                f"SELECT fi.Item_name, fi.Quantity, fi.Units, fi.fd_id, fb.Location from food_item fi join food_bank fb using(fb_id) where fb.fb_id = {newFBID}")
            rows = FBcursor.fetchall()          # stores query as list

            # Delete the old table and insert each row in the current database to accomplish refresh
            if rows != 0:
                table.delete(*table.get_children())
                for row in rows:
                    table.insert('', END, values=row)

        #================== user widgets =============================================================
        AddFBButton = ttk.Button(self.root, text="New Food Bank +", width=20, command=self.addFB)
        AddFBButton.place(x=675, y=200)

        #================== view table from database ==================================================
            # (credit due to Jerry Pi)
        viewFrame = Frame(self.root, bd=5, relief='ridge', bg='wheat')   #frame to hold the table
        viewFrame.place(x=30, y=110, width=600, height=350)
        xScroll = Scrollbar(viewFrame, orient=HORIZONTAL)   #allows the user to scroll
        yScroll = Scrollbar(viewFrame, orient=VERTICAL)
        table = ttk.Treeview(viewFrame, columns=(           #sets up the table
            'item_to_filter', 'quantity_to_filter', 'units', 'fid_to_filter', 'location_to_filter'),
                             xscrollcommand=xScroll.set,
                             yscrollcommand=yScroll.set)
        #table column headers
        table.heading("item_to_filter", text="item")
        table.heading("quantity_to_filter", text="quantity")
        table.heading("units", text="units")
        table.heading("fid_to_filter", text="food_id")
        table.heading("location_to_filter", text="locations")

        table.column("item_to_filter", width=100)
        table.column("quantity_to_filter", width=25)
        table.column("units", width=25)
        table.column("fid_to_filter", width=10);
        table.column("location_to_filter", width=100)
        table['show'] = 'headings'

        # get all values and pack the table on to the screen
        table.pack(fill=BOTH, expand=1)
        #=============================================================================================


    def addFB(self):
        """ addFB()
        Displays a new screen which asks users for the new food bank information
            (hours, location, contact information, food item data), and updates the database.
        - Called when "New Food Bank +" button is selected.
        """
        filedata = []                        # holds data from file upload
        imported_filename = StringVar()  # holds name of file uploaded, used as a textvariable in a label
        def compareTimes(timeDict:dict)->list:
            """
                Validates open time is less than close time for a day. If the two times are equal,
                they are omitted
                Input: timeDict is the dictionary of times of format {"str": (datetime.time, datetime,time), ....}
                Returns: List of start end times, from increasing order of timeDict's keys
            """
            keys = timeDict.keys()  #holds days of timeDict
            formattedTime = []      #holds return value to be append to
            for key in keys:        #for each day
                time = timeDict[key]            #grab the times of such day
                if(time[0] == time[1]):         #if open and end times are equal
                    formattedTime.append('')    #omit, appends an empty string
                    formattedTime.append('')
                elif(time[0] < time[1]): # validates that the open time is before close time
                    formattedTime.append(str(time[0]))      #appends valid start
                    formattedTime.append(str(time[1]))              #and end time
                else:   #error catching: close time is before open time
                    formattedTime = None        #appends nothing -> will check in other functions if len(formattedTime) is correct
                    break
            return formattedTime

        def validateFile(filepath)->bool:
            """validateFile(filepath)
                Verifies the inserted file is of the correct format:
                    - columns: "item", "category", "quantity", "units"
                    - quantities are positive/zero digits
                    - all rows/columns have data
                Returns false if file was in incorrect format, else returns True.
            """
            try:
                # ---------- checking headers -------------
                file = open(filepath, 'r')       #read the file given
                expected = ["item", "category", "quantity", "units"] #columns of csv must match

                dict_from_csv = list(csv.DictReader(file))          #turns csv into dictionary
                if expected != [x for x in dict_from_csv[0].keys()]:    #compares csv column names to expected headers
                    messagebox.showerror("File error", "Incorrect headers: expected 'item', 'category', 'quantity', 'units'")
                    return False

                #through every row in the csv file
                for i, item in enumerate(dict_from_csv):
                    # ---------- validate quantity -------------
                    quant = item['quantity']

                    # checks if integer and non-negative
                        # isdigit() also returns false if digit is negative
                    if not (quant.isdigit()):
                        #shows which row was incorrect
                        messagebox.showerror("File error", "Invalid quantity (" + quant + ") on row " + str(i + 2))
                            #str(i+2): adds two since csv indices starts at 2 due to headers and difference in start index
                        return False

                    # -------- checking for empty rows -----------
                    if (not item['item']) or (not item['category']) or (not item['quantity']) or (not item['units']):
                        #shows which row is empty
                        messagebox.showerror("File error", "Empty values row " + str(i + 2))
                        return False

                #turns dict_from_csv into a 2D-list (more readable for inserting to database)
                dict_to_list= []
                for x in dict_from_csv:
                    i, c, q, u = x.values()     #unpack dict_from_csv values
                    # each row of dict_to_list is a row of the csv file
                    dict_to_list.append((i, c, q, u))
                nonlocal filedata
                #sets the uploaded data to the global variable
                filedata = dict_to_list
                return True

            except Exception as e:
                print("Error:", e)
                #if error errors that is not already checked for
                messagebox.showerror("File error",
                                     "Having trouble uploading file. Please ensure the file uploaded is a CSV with the columns 'item', 'category' and 'quantity'")

        def fileUpload():
            """fileUpload()
                Prompts user to input a file. Ensures the file is .csv and calls validateFile() to
                    verify if inputted data is valid.
            """

            filepath = filedialog.askopenfilename()             #prompts user for file
            filename, fextension = os.path.splitext(filepath)   #splits filepath by its extension

            if fextension != '.csv':        #verifies file is a .csv
                messagebox.showerror("File Error", "Incorrect File Type. Must be CSV")
                return

            if validateFile(filepath) == False:  # validateFile() found an error in validating data from file
                return

            imported_filename.set("File upload: " + filepath.split("/")[-1]) #show which file uploaded in label
            print("Succesfully imported file")

        def saveChanges():
            """
            This function saves all of the user's input to the SQL database. All input is retrieved and then
            verified to make sure all inputs are filled in, the phone number is of correct format, food bank name
            doesn't already exist, and that the open and closing times are valid. If such cases of where the input is
            incorrect the SQL queries will not be executed, and a window will be shown to display what the error is to
            the user.
            """

            newloc = locationInput.get()                                        #holds the location input
            times = {"Monday": (MtimeOpen.getTime(), MtimeClose.getTime()),     #holds the time inputs
                     "Tuesday": (TtimeOpen.getTime(), TtimeClose.getTime()),
                     "Wednesday": (WtimeOpen.getTime(), WtimeClose.getTime()),
                     "Thursday": (RtimeOpen.getTime(), RtimeClose.getTime()),
                     "Friday": (FtimeOpen.getTime(), FtimeClose.getTime()),
                     "Saturday": (StimeOpen.getTime(), StimeClose.getTime()),
                     "Sunday": (UtimeOpen.getTime(), UtimeClose.getTime())
                     }
            openTimes = compareTimes(times)        #keeps the days which are open (omits times with open == end)
            if(openTimes != [""]*14): #If we get back an empty list of 14 items, there are no open days. This is an error.
                phone_number = PhoneNumInput.get()                      #holds the user inputted phone number
                if not self.checkPhoneNum(phone_number):                #validates its of correct format
                    messagebox.showerror("ERROR", "Invalid phone number. Must be formatted as (XXX) XXX-XXXX")
                    return

                neighborhood = NeighborhoodInput.get()              #holds the user inputted neighborhood
                if neighborhood == None:            #validates they insert a neighborhood
                    messagebox.showerror("ERROR", "Please input a neighborhood")

                FBName = FBNameInput.get()                          #holds the user inputter food bank name
                if FBName == None:              #validates they insert a food bank name
                    messagebox.showerror("ERROR", "Please input a Food Bank name")

                if newloc == None:              #validates they insert a food bank location
                    messagebox.showerror("ERROR", "Please input a Food Bank location")

                FBcursor.execute(f"select MAX(fb.fb_ID) from food_bank fb")     #grabs max exisiting food bank id
                maxfb_ID = FBcursor.fetchall()                                  #holds such above
                FBcursor.execute(f"select MAX(fi.fd_ID) from food_item fi")     #grabs max exisiting food item id
                maxfd_ID = FBcursor.fetchall()                                  #holds such above
                if (maxfd_ID != []):   #creates a new id for the new food bank
                    maxfd_ID = int(maxfd_ID[0][0]) + 1
                else:                                       # if no existing food bank already
                    maxfd_ID = 1
                newfb_ID = None
                if (maxfb_ID != []):     #creates a new id for the new food item
                    newfb_ID = int(maxfb_ID[0][0]) + 1
                else:                   # if no existing food item already
                    newfb_ID = 1
                FBcursor.execute(f"select * from food_bank fb where fb.Location = '{FBName}'")
                locationCheck = FBcursor.fetchall()         #pulls existing food banks with such name
                FBcursor.execute(f"select * from food_bank fb where fb.Address = '{newloc}'")
                addressCheck = FBcursor.fetchall()          #pulls existing food banks with such address
                if(openTimes != None):                      #verifies not all days are closed
                    if (locationCheck == [] and addressCheck == []):        #verifies no similar food bank name or location already exists
                        # adds food bank to database
                        FBcursor.execute(f"insert into foodforyou.food_bank values('{FBName}', " + \
                                        f"'{newloc}', '{neighborhood}', '{phone_number}', '{newfb_ID}')")
                        FBcursor.execute(
                            f"insert into foodforyou.hours values ('{newfb_ID}', '{openTimes[0]}', '{openTimes[1]}'," + \
                            f"'{openTimes[2]}', '{openTimes[3]}','{openTimes[4]}', '{openTimes[5]}'," + \
                            f"'{openTimes[6]}', '{openTimes[7]}','{openTimes[8]}', '{openTimes[9]}'," + \
                            f"'{openTimes[10]}', '{openTimes[11]}','{openTimes[12]}', '{openTimes[13]}')")
                        nonlocal filedata
                        # imports data from file to Food Item database
                        for line in filedata:
                            # grabs row from data from csv -> will become a new entry in database
                            item_name = line[0]
                            category = line[1]
                            quantity = int(line[2])
                            units = line[3]

                            FBcursor.execute(f"select * from food_item fi where fi.Item_name='{item_name}' and fi.units = '{units}' and fi.category = '{category}' and fi.location = '{FBName}'")
                                    #checks by (union by item_name, units, category, FBName)
                            duplicateCheck = FBcursor.fetchall()
                            #comibines duplicate food items
                            if(duplicateCheck==[]):  #no duplicates
                                FBcursor.execute(
                                    f"insert into foodforyou.food_item values ('{item_name}', '{category}', {quantity}, '{units}', '{FBName}', {int(newfb_ID)}, {maxfd_ID})")
                                maxfd_ID += 1       #creates a new row in data base, -> creates new food item ID
                            else:
                                duplicateID = duplicateCheck[0][6]      #merge by item id
                                insertQuantity = quantity+int(duplicateCheck[0][2])     #merge quantities
                                FBcursor.execute(       #change quantity of item id
                                    f"update foodforyou.food_item set Quantity={insertQuantity} where fd_ID = {duplicateID}"
                                )

                        FBconnection.commit()       # modifies the database with such changes
                        fetchData(newfb_ID)         # resets the GUI table
                        newFBScreen.destroy()       # closes out window
                    else:       # error checking -> doesn't allow user to change, still views FB screen
                        messagebox.showerror("ERROR", "Food bank with this name or address appears to already exist.")
                        return
                else:
                    messagebox.showerror("ERROR", "One of the open times is after the close time.")
                    return
            else:
                messagebox.showerror("ERROR", "The food bank times are all closed, a food bank must have at least one open day to be added.")
                return
                #Error message for always closed food bank

            # closes screen


        #----------------------setting up screen for "New Food bank"---------
        newFBScreen = Toplevel(self.root)
        newFBScreen.geometry("800x315")
        newFBScreen.configure(background='white')

        #====================== user input widgets ======================
        # user input button to upload file
        fileUploadButton = ttk.Button(newFBScreen, text="Upload Data", width=15, command=fileUpload)
        fileUploadButton.place(x=600, y=175)
        # if a file is uploaded, displays the file name
        ttk.Label(newFBScreen, textvariable=imported_filename, font=(font,9)).place(x=600, y=210)

        # text labels to prompt user to insert times
        ttk.Label(newFBScreen, text="Insert times").place(x=75, y=25)
        ttk.Label(newFBScreen, text="To indicate 'Closed', set the open and close times of the desired day equal.",
                  font=(font, 9), foreground="gray").place(x=350, y=25)

        ttk.Label(newFBScreen, text="Open", font=(font, 9)).place(x=25, y=75)
        ttk.Label(newFBScreen, text="Close", font=(font, 9)).place(x=25, y=100)

        # text input to insert food bank street address
        ttk.Label(newFBScreen, text="Street Address: ").place(x=75, y=160)
        locationInput = ttk.Entry(newFBScreen, width=30)
        locationInput.place(x=75, y=185)

        # text input to insert food bank name
        ttk.Label(newFBScreen, text="Food Bank Name:").place(x=75, y=225)
        FBNameInput = ttk.Entry(newFBScreen, width=30)
        FBNameInput.place(x=75, y=250)

        # text input to insert neighborhood
        ttk.Label(newFBScreen, text="Neighborhood:").place(x=300, y=160)
        NeighborhoodInput = ttk.Entry(newFBScreen, width=30)
        NeighborhoodInput.place(x=300, y=185)

        # text input to insert phone neighborhood
        ttk.Label(newFBScreen, text="Phone Number:").place(x=300, y=225)
        PhoneNumInput = ttk.Entry(newFBScreen, width=30)
        PhoneNumInput.place(x=300, y=250)
        # text label describe phone number format
        ttk.Label(newFBScreen, text="Expected format: (XXX) XXX-XXXX", font=(font,9), foreground="gray").place(x=300, y=275)

        # time picker objects to insert open/closing times for each day of the week
            #for monday
        ttk.Label(newFBScreen, text="Monday", font=(font, 9)).place(x=75, y=50)
        MtimeOpen = time.App(newFBScreen)       #uses timepicker.py widget
        MtimeOpen.place(x=75, y=75)
        MtimeClose = time.App(newFBScreen)
        MtimeClose.place(x=75, y=100)

            #for tuesday
        ttk.Label(newFBScreen, text="Tuesday", font=(font, 9)).place(x=175, y=50)
        TtimeOpen = time.App(newFBScreen)
        TtimeOpen.place(x=175, y=75)
        TtimeClose = time.App(newFBScreen)
        TtimeClose.place(x=175, y=100)

            #for wednesday
        ttk.Label(newFBScreen, text="Wednesday", font=(font, 9)).place(x=275, y=50)
        WtimeOpen = time.App(newFBScreen)
        WtimeOpen.place(x=275, y=75)
        WtimeClose = time.App(newFBScreen)
        WtimeClose.place(x=275, y=100)

            #for thursday
        ttk.Label(newFBScreen, text="Thursday", font=(font, 9)).place(x=375, y=50)
        RtimeOpen = time.App(newFBScreen)
        RtimeOpen.place(x=375, y=75)
        RtimeClose = time.App(newFBScreen)
        RtimeClose.place(x=375, y=100)

            #for friday
        ttk.Label(newFBScreen, text="Friday", font=(font, 9)).place(x=475, y=50)
        FtimeOpen = time.App(newFBScreen)
        FtimeOpen.place(x=475, y=75)
        FtimeClose = time.App(newFBScreen)
        FtimeClose.place(x=475, y=100)

            #for saturday
        ttk.Label(newFBScreen, text="Saturday", font=(font, 9)).place(x=575, y=50)
        StimeOpen = time.App(newFBScreen)
        StimeOpen.place(x=575, y=75)
        StimeClose = time.App(newFBScreen)
        StimeClose.place(x=575, y=100)

            #for sunday
        ttk.Label(newFBScreen, text="Sunday", font=(font, 9)).place(x=675, y=50)
        UtimeOpen = time.App(newFBScreen)
        UtimeOpen.place(x=675, y=75)
        UtimeClose = time.App(newFBScreen)
        UtimeClose.place(x=675, y=100)

        # button to submit changes
        submitButton = ttk.Button(newFBScreen, text="Save changes", width=15, command=saveChanges)
        submitButton.place(x=600, y=250)

        newFBScreen.resizable(0, 0)       #make the window size not adjustable
        newFBScreen.mainloop()            #display widgets

    def checkPhoneNum(self, num:str)->bool:
        """ checkPhoneNum(str)
            Checks if input is of the correct format (XXX) XXX-XXXX
            Input: A string containing a phone number
            Output: Return true if of correct format, else returns False.
        """
        if len(num) != 14: return False     #is of correct length
        for i in range(14):
            if i == 0:
                if num[i] != "(": return False  #0th character is (
            elif i == 4:
                if num[i] != ")": return False  #4th character is )
            elif i == 5:
                if num[i] != " ": return False  #5th character is " "
            elif i == 9:
                if num[i] != "-": return False  #9th character is -
            elif not num[i].isdigit():          #rest are digits
                return False
        return True


class DataView:
    """DataView: class
        GUI which allows the user to view and search/filter the data log.
    """
    def __init__(self, parent):
        self.root = Frame(parent, bg="white")

        self.locations = fetchLocations(Dcursor)    #all exisitng food bank locations
        # ========= holds user input of the search criteria =========
        self.foodItemSearchText = StringVar()   #food item
        self.ascSort = BooleanVar()             #ascending sort (true: asc, false: desc)
        self.loc_to_update = StringVar()        #food bank location


        def fetchData():
            search() #call search function to store all entries in cursor
            rows = Dcursor.fetchall() #set rows from cursor

            # Delete the old table and insert each row in the current database to accomplish refresh
            if rows != 0:
                table.delete(*table.get_children())

                for row in rows: #populate table with new entries
                    table.insert('', END, values=row)

        def search():
            """searches Outgoing Database for user input search criteria"""
            item = ItemSearch.get() #get item name from search box
            locationBool = True #initialize location bool to true
            itemBool = True #initialize item bool to true
            location = LocationFilter.get() #initialize location variable from dropdown
            ascending = self.ascSort.get() #set bool for ascending search
            fd_id = IDSearch.get()
            if (location == "None" or location == ""): #if location is None or empty set bool to false
                location = "%"
            if (item.strip() == ""): #if item is empty set bool to false
                item = "%"
            if (fd_id.strip() == ""):
                fd_id = "%"
            else:
                fd_id = int(fd_id.strip())
            if (ascending): #if ascending is specified, execute this query
                Dcursor.execute(
                    f"SELECT fi.Item_name, fi.Quantity, fi.Units, fi.fd_id, fb.Location from outgoing fi join food_bank fb using(fb_id) where fi.Item_name like '{item}' and fb.location like '{location}' and fi.fd_id like '{fd_id}' order by fi.Quantity ASC")
            else: #if ascending not specified use this query
                Dcursor.execute(
                    f"SELECT fi.Item_name, fi.Quantity, fi.Units, fi.fd_id, fb.Location from outgoing fi join food_bank fb using(fb_id) where fi.Item_name like '{item}' and fb.location like '{location}' and fi.fd_id like '{fd_id}'")


        def export():
            """Exports Outgoing data base as a csv"""
            Dcursor.execute("SELECT * from outgoing")       #selects everything from database
            result = Dcursor.fetchall()                     #calls such query
            toWrite = []                   #list to hold data from database, which will be used to import to csv

            now = datetime.datetime.now()           #take current time
            currentTime = now.strftime("%H%M%S")           #reformats to hours, minute, second
            filename = "FoodForYou_Export_" + currentTime + ".csv"      #creates new file name for export

            if (result):            #if query is not empty
                toWrite.append(["Item_name", "Category", "Quantity", "Units", "Location", "fb_ID", "fd_ID"]) #sets headers of csv
                for row in result:  #appends each row in database to toWrite
                    toWrite.append(row)
                with open(filename, 'w', newline='\n') as csvF:     # creates filename (will overwrite if file is already existing in directory, else creates new file in directory)
                    csvw = csv.writer(csvF, quotechar='"', delimiter=',')   #removes quotes and delimites by commas
                    for line in toWrite:
                        csvw.writerow(line)         #writes data as line
            else:
                messagebox.showerror("ERROR", "There are no entries in the database.")

        #====================== user input widgets ======================
        ttk.Label(self.root, text="Search by item").place(x=675, y=110)

        #prompts for user to search by item
        ItemSearch = ttk.Entry(self.root, width=25)
        ItemSearch.place(x=675, y=130)

        # prompts for user to search by item ID
        ttk.Label(self.root, text="Search by item ID").place(x=675, y=170)
        IDSearch = ttk.Entry(self.root, width=25)
        IDSearch.place(x=675, y=190)

        # prompts for user to search by location
        ttk.Label(self.root, text="Sort by location").place(x=675, y=230)
        LocationFilter = ttk.Combobox(self.root, values=self.locations)
        LocationFilter.place(x=675, y=250)

        # prompts for user to sort by quantity
        QuantitySortButton = ttk.Checkbutton(self.root, text="Sort ascending quantity", command=fetchData, onvalue=True,
                                             offvalue=False, variable=self.ascSort)
        QuantitySortButton.place(x=675, y=300)

        # Allows user to commit search
        SearchButton = ttk.Button(self.root, text="Search", width=15, command=fetchData)
        SearchButton.place(x=675, y=350)

        # Allows user to export data log
        exportButton = ttk.Button(self.root, text="Export data", width=15, command=export)
        exportButton.place(x=675, y=420)

        # ================== view table =============================================================
        # (credit due to Jerry Pi)
        viewFrame = Frame(self.root, bd=5, relief='ridge', bg='wheat')   #frame to hold data
        viewFrame.place(x=30, y=110, width=600, height=350)

        xScroll = Scrollbar(viewFrame, orient=HORIZONTAL)       #allows user to scroll through table
        yScroll = Scrollbar(viewFrame, orient=VERTICAL)
        table = ttk.Treeview(viewFrame, columns=(
            'item_to_filter', 'quantity_to_filter', 'units', 'fid_to_filter', 'location_to_filter'),
                             xscrollcommand=xScroll.set,
                             yscrollcommand=yScroll.set)      #table to display database

        # creates column headers
        table.heading("item_to_filter", text="item")
        table.heading("quantity_to_filter", text="quantity")
        table.heading("units", text="units")
        table.heading("fid_to_filter", text="food_id")
        table.heading("location_to_filter", text="locations")

        table.column("item_to_filter", width=100)
        table.column("quantity_to_filter", width=25)
        table.column("units", width=25)
        table.column("fid_to_filter", width=10);
        table.column("location_to_filter", width=100)
        table['show'] = 'headings'

        # get all values and pack the table on to the screen
        fetchData()
        table.pack(fill=BOTH, expand=1)

def onClose():
    """called when root window is closed to close out database connnections"""
    Dconnection.close()     #closes out Outgoing database
    FBconnection.close()    #closes out Food Bank database
    root.destroy()          #closes out root window

root = Tk()                 #creates Tkinter window
root.protocol("WM_DELETE_WINDOW", onClose)  #sets the window's closing function to onClose()
root.geometry('900x540')                    #set geometry of screen
tabControl = ttk.Notebook(root)             #creates "tabs" widget
use_theme(root, "10")                             #use theme for screen to applied to widgets

tab1 = FBView(root).root                    #sets food bank view frame as a tab
tabControl.add(tab1, text="Food Banks")

tab2 = DataView(root).root                  #sets data log view frame as tab
tabControl.add(tab2, text="Data Log")

tabControl.pack(expand=1, fill="both")      #places frame on screen
root.mainloop()
