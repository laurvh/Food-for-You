"""
Name: staffUI.py
Created: 3/5/2023
Authors: Katherine Smirnov, Krishna Patel
Provides a table view of food items in the databases, allows user to modify food items by updating quantity,
moving or deletion, and allows insertion of new food items. The table may be sorted by quanity, and filtered by food item,
food item ID, and location.
Modifications:
    3/5/2023: Rough sketch of GUI -KS
              Added SQL queries, and connected to table widget -KP
              Added update screen - KS
    3/7/2023: Modified update screen to allow for "move", "update", "deletion" options -KS
              Rough implementation of moving items -KP
    3/8/2023: Added ID search, cleaned up GUI -KS
    3/9/2023: Full implementation of insert of deletion -KP
    3/10/2023: Integrated with util.py -KS
References:
    EasyA, admin.py from Jerry Pi
        -Recycled code to display database into table and update items from data to database
"""

from utilffy import *

connection = None #initialize connection to none
cursor = None #initialize cursor to none

class NewItem:
    """ class NewItem(parent)
        Creates a new window which prompts user to input food item, category, quantity, units, location. Populates
            database with new item.
        Input: Parent is the Tkinter screen which the newItem screen is a child of
    """
    def __init__(self, parent:Tk):
        #----------------------setting up screen for "New item"---------
        self.screen = Toplevel(parent)      #creates a child window of main screen
        self.screen.title("New Item")
        self.swidth = 300
        self.screen.geometry(f'{self.swidth}x300')
        self.screen.configure(background='white')
        self.locations = fetchLocations(cursor)     #holds list of locations in database
        self.categories = fetchCategory(cursor)     #holds list of categories in databse
        #--------------------------------------------------------------

        #============== holds user input of the new item ==========
        self.quantity_to_update = IntVar()      #quantity
        self.units_to_update = StringVar()
        #===========================================================


        #================== user widgets =============================================================
        ttk.Label(self.screen, text="New Item", font=(font, 13)).place(x=(self.swidth)/2 - 30, y=10)

        ttk.Label(self.screen, text="item").place(x=50, y=50)
        iteminput = ttk.Entry(self.screen, width=20, font=(font, searchInputSize)) # user input for food item
        iteminput.place(x=(self.swidth) / 2 - 30, y=50)

        ttk.Label(self.screen, text="category:").place(x=50, y=80)
        categoryinput = ttk.Combobox(self.screen, values=self.categories, font=(font, 8), state="readonly") #user dropdown for category
        categoryinput.place(x=(self.swidth) / 2 - 30, y=80)

        ttk.Label(self.screen, text="quantity:").place(x=50, y=110)
        quantityinput = ttk.Entry(self.screen, width=10,                        #user input for quantity
                                  textvariable=self.quantity_to_update, font=(font, searchInputSize))
        quantityinput.place(x=(self.swidth) / 2 - 30, y=110)

        ttk.Label(self.screen, text="units: ").place(x=50, y=140)
        unitsInput = ttk.Entry(self.screen, width=10,                           #user input for units
                               textvariable=self.units_to_update, font=(font, searchInputSize))
        unitsInput.place(x=(self.swidth) / 2 - 30, y=140)

        ttk.Label(self.screen, text="location:").place(x=50, y=170)
        locationinput = ttk.Combobox(self.screen, values=self.locations, font=(font, 8), state="readonly")    #user dropdown for location
        locationinput.place(x=(self.swidth) / 2 - 30, y=170)
        #======================================================================

        def saveChanges():
            """
            This function saves all of the user's input to the SQL database. All input is retrieved and then 
            verified to make sure it meets the system requirements. If any of the input is incorrect the SQL queries
            will not be executed, and a window will be shown to display what the error is to the food bank staff.
            """
            # pulls user input and removes trailing new_lines/spaces
            item_name = iteminput.get().strip()         #Assign item name to variable
            quantity = (quantityinput.get().strip())    #Assign quantity to variable
            location = locationinput.get().strip()      #Assign location to variable
            units = unitsInput.get().strip()            #Assign units to variable
            category = categoryinput.get().strip()      #Assign category to variable

            # search for the Food Bank ID for a certain location and store it in the cursor
            cursor.execute(f"select fb.fb_ID from food_bank fb where fb.Location='{location}'")
            temp = cursor.fetchall()        #Store the cursor data in a temporary variable

            if (category != "" and item_name != "" and units != "" and quantity != "" and location != ""): #Checks if all input fields from the tkinter window are non empty
                if(quantity.isdigit()):
                    quantity = int(quantity)            #convert the quantity to an int
                    if (quantity >= 0):                 #if the quantity is greater than 0, we can continue processing the item addtion
                        if (temp != []):                #If the foodBank ID list is not empty, we can continue since the food bank exists
                            fb_id = int(temp[0][0])     #assign the food bank ID from the temp variable to a new variable
                            cursor.execute(
                                f"select * from food_item fi where fi.Item_name = '{item_name}' and fi.units = '{units}' and fi.location = '{location}' and fi.fb_ID = {fb_id}") #retrieve all entries from the databse where the current item may exist
                            result = cursor.fetchall()              #store SQL data in a variable
                            if (result == []): #if the result is empty, this item does not exist so we can continue insertion
                                cursor.execute(f"select MAX(fi.fd_ID) from food_item fi") #select the max food item ID so a brand new unique item ID can be generated
                                temp = cursor.fetchall()            #fetch data into a temp variable
                                key = 1                             #initialize food item ID to 1
                                if (temp != []):                    #if the temp var is not empty convert into an int and increment by 1 to get a new unique ID
                                    key = int(temp[0][0]) + 1       #if the list is empty there is nothing in the data base and the food ID will start at 1
                                cursor.execute(
                                    f"insert into foodforyou.food_item values ('{item_name}', '{category}', {quantity}, '{units}', '{location}', {int(fb_id)}, {key})") #insert the data into the database cursor
                                connection.commit()                 #commit the data to the database so it can be written to disk.

                                self.screen.destroy()               # Upon sucessful completion destroy the window
                                messagebox.showinfo("Success", "Item added")  # indicate that the operation was successfully completed.

                            else:        #show an error indicating the item is already in the database.
                                messagebox.showerror("ERROR",
                                                    "This item appears to exist in the database, please find entry and modify.")
                                return     # error checking -> doesn't allow user to change, still views FB screen
                        else:           #show that the location is not valid
                            messagebox.showerror("ERROR", "Location is not valid, please pick valid location.")
                            return
                    else:               #tell user to use a positive quantity
                        messagebox.showerror("ERROR", "Enter a non-negative quantity.")
                        return
                else:
                    messagebox.showerror("ERROR", "Quantity must be an integer.")
                    return
            else:                       #if any fields are empty, we will prompt the food bank staff to re-enter the information.
                messagebox.showerror("ERROR", "Please enter all fields to insert an item.")
                return

        submitButton = ttk.Button(self.screen, text="Save changes", width=15, command=saveChanges) #set attributes of submit button
        submitButton.place(x=(self.swidth) / 2 - 60, y=250) #place the submit button
        self.screen.resizable(0, 0)                   #make the window size not adjustable


class UpdateItem:
    """ class UpdateItem(parent, item, quantity, units, location, food_id)
    Creates a new window which allows the user to choose to "update", "move", "delete"
        - Update:
            - Change the quantity/units of an item at a food bank (cannot change item, category, or location)
        - Move item from one food bank to another
            - User selects a desired quantity to move (must be less than the current quantity)
            - User selects the location to move to
            - Food item at the moving location is incremented, and current item is decremented.
            - Combines with items of the same item name at moving location, else creates a new
                item at such food bank
        - Delete item from food bank

    Input: Parent is the Tkinter screen which the UpdateItem screen is a child of
           Item: food item name
           Quantity: Existing quantity of item
           Unit: Existing units of item
           location: Existing locaiton of item
           food_id: ID of food item
    """
    def __init__(self, parent:Tk, item:str, quantity:int, units:str, location:str, food_id:str):
        #----------------------setting up screen for "Update item"---------
        self.screen = Toplevel(parent) #creates a child window of main screen
        screen = self.screen
        self.screen.title("Updating")
        screen.configure(background='white')
        self.swidth = 300
        self.screen.geometry(f'{self.swidth}x300')
        self.locations = fetchLocations(cursor)

        #============== holds what the user inputs =================
        self.quantity_to_update = IntVar()      #quantity
        self.units_to_update = StringVar()      #units
        self.screenopt = StringVar() #holds if the user is updating, moving or deleting
        #============== holds what the user inputs =================

        #-------------------------------------------------- input widgets -----------------------------------------
        # user input for food item
        ttk.Label(screen, text="item").place(x=50, y=50)
        iteminput = ttk.Entry(screen, width=20, font=(font, searchInputSize))
        iteminput.insert(0, item)   #inserts the existing food item
        iteminput.configure(state=DISABLED)     #makes the text field read-only
        iteminput.place(x=(self.swidth) / 2 - 30, y=50)

        # user input for quantity
        ttk.Label(screen, text="quantity:").place(x=50, y=80)
        quantityinput = ttk.Entry(screen, width=10, textvariable=self.quantity_to_update, font=(font, searchInputSize))
        self.quantity_to_update.set(quantity)   # inserts the existing quantity
        quantityinput.place(x=(self.swidth) / 2 - 30, y=80)

        # user input for units
        ttk.Label(screen, text="units: ").place(x=50, y=110)
        unitsInput = ttk.Entry(screen, width=10, textvariable=self.units_to_update, font=(font, searchInputSize))
        self.units_to_update.set(units)     # inserts the existing units
        unitsInput.place(x=(self.swidth) / 2 - 30, y=110)

        # user input for location
        ttk.Label(screen, text="location:").place(x=50, y=140)
        locationinput = ttk.Entry(screen, width=20, font=(font, searchInputSize))
        locationinput.insert(0, location)   # inserts the existing location
        locationinput.place(x=(self.swidth) / 2 - 30, y=140)
        locationinput.configure(state="disabled")       #makes the text field read-only

        # location input (only for moving item, so placement will be later)
        locationDD = ttk.Combobox(screen, values=self.locations, font=(font, 8),state="readonly")

        #allow users to save their changes
        fillerlbl = ttk.Label(screen)

        submitButton = ttk.Button(screen, text="Save changes", width=15)
        submitButton.place(x=(self.swidth) / 2 - 60, y=250)


        movelbl = ttk.Label(screen, text="location to move items to")


        # ------------------------------ modification functions -----------------------------------------------
        def compareItems(item1:tuple, item2:tuple)->bool:
            """
            This function compares two items in the database and ensures they are the same so they can be merged 
            upon moving an item that already exists in another database.
            """
            name = (item1[0] == item2[0])       #create bool for if the item names are equal
            category = (item1[1] == item2[1])   #create a bool for if the categories are the samee
            units = (item1[3] == item2[3])      #create a bool for if the units are the same
            return (name and category and units) #use boolean algebra to determine if the items are the same

        def saveChanges():
            """
            This function saves all of the user's input to the SQL database. All input is retrieved and then 
            verified to make sure it meets the system requirements. If any of the input is incorrect the SQL queries
            will not be executed, and a window will be shown to display what the error is to the food bank staff.
            """
            # If one or more required field is empty, show error
            operation = self.screenopt.get()        #obtain the operation so the correct code can be executed.
            cursor.execute(f"select fb.fb_id from food_bank fb where fb.Location = '{location}'") #obtain the food bank id of the location from the database.
            fb_id = [int(i[0]) for i in cursor.fetchall()][0] #store the food bank ID in a variable
            if (operation == 'update'):              #if the update operation is specified execute code below
                if(quantityinput.get().isdigit()):
                    if (int(quantityinput.get()) < 0): #verify quantity to be updated is non-negative
                        messagebox.showerror("ERROR", "Quantity must be non-negative") #show message if quantity is negative
                    else:                           #continue if quantity is correct
                        currentfb_id = fb_id        #set new var for fb_id
                        cursor.execute(
                            f"select * from food_item fi where fi.Item_name='{item}' and fi.fb_id={currentfb_id} and fi.units = '{units}'") #select all columns for food item matching input from database
                        origEntry = cursor.fetchall()[0] #set database result to variable
                        origQuantity = origEntry[2] #set variable for original quantity

                        cursor.execute(
                            f"update foodforyou.food_item set Item_name='{iteminput.get().strip()}', Quantity={int(quantityinput.get())}, Units='{unitsInput.get().strip()}', Location='{location}', fb_id='{currentfb_id}' where fd_ID='{int(food_id)}'")
                            #update entry in food_item table to set quantity of current food item to its new quantity
                        if (int(quantityinput.get()) < origQuantity): #if the quantity set in the database was less than original record it to the outgoing database for record keeping
                            cursor.execute(
                                f"select * from outgoing o where o.Item_name='{item}' and o.fb_ID={fb_id} and o.fd_ID={food_id}") #select item if it exists in the outgoing database
                            outgoingEntry = cursor.fetchall() #store in variable
                            if (outgoingEntry != []): #if the entry is not empty we will update it 
                                cursor.execute(
                                    f"update foodforyou.outgoing set Quantity={int(outgoingEntry[0][2]) + origQuantity - int(quantityinput.get())} where fd_ID='{int(food_id)}'") #increment quantity in outgoing table
                            else:
                                cursor.execute(
                                    f"insert into foodforyou.outgoing (Item_name, Category, Quantity, Units, Location, fb_ID, fd_ID) values ('{item}', '{origEntry[1]}', {origQuantity - int(quantityinput.get())}, '{origEntry[3]}', '{origEntry[4]}', {int(origEntry[5])}, {int(origEntry[6])})")
                                #if the entry is not in the table, insert it 
                        connection.commit() #commit the connection, so the insertions are written to disk inthe database
                        messagebox.showinfo("Success", "Quantity successfully updated.") #show a message showing success
                else:
                    messagebox.showerror("ERROR", "Quantity must be an integer.")

            elif (operation == 'move'): #if the move operation is specified execute code below
                cursor.execute(f"select fi.Quantity from food_item fi where fi.fd_id = '{food_id}'") #select quantity for food_item
                origQuantity = [int(i[0]) for i in cursor.fetchall()][0] #store quantity in variable
                moveQuantity = (quantityinput.get()) #get the quantity to move and store in variable
                if(moveQuantity.isdigit()):
                    moveQuantity = int(moveQuantity)
                    if (moveQuantity > origQuantity): # check if move quantity is greater than available
                        messagebox.showerror("ERROR", "The move quantity cannot be greater than the current quantity") #show error if it is
                    elif (moveQuantity < 0): #move quantity cannot be less than 0
                        messagebox.showerror("ERROR", "The move quantity cannot be negative") #show error if less than 0
                    elif (locationDD.get() == "None" or locationDD.get() == ""): #Location cannot be None or empty
                        messagebox.showerror("Operation Cancelled", "Move location was none.") #show error
                    elif (locationDD.get() == location): #Cannot move to the same location
                        messagebox.showerror("Location cannot be the same.", "Select a different location.")
                    else:
                        cursor.execute(f"select fb.fb_id from food_bank fb where fb.Location = '{locationDD.get()}'") #get food bank ID for move location
                        movefb_id = [int(i[0]) for i in cursor.fetchall()][0] #store food bank ID in varaible
                        cursor.execute(
                            f"select * from food_item fi where fi.Item_name='{item}' and fi.units = '{units}' and fi.fb_id={movefb_id}") #select all columns for current item in move location
                        itemCheck = cursor.fetchall() #store in variable
                        # print(a)
                        if (itemCheck != []): #if the item exists in the move location itemCheck will not be empty
                            item2 = itemCheck[0] #set item to variable
                            cursor.execute(f"select * from food_item fi where fi.Item_name='{item}' and fi.fb_id={fb_id}") #select all columns for current item in current location 
                            item1 = cursor.fetchall()[0] #set current location item to variable
                            if (compareItems(item1, item2)): #verify that both items are the same
                                cursor.execute(
                                    f"select fi.fd_id from food_item fi join food_bank fb using (fb_id) where fb_id = '{movefb_id}' and fi.Item_name = '{iteminput.get().strip()}'") #select food item ID if item exists
                                newFoodID = [int(i[0]) for i in cursor.fetchall()][0] #store food_item id
                                cursor.execute(f"select fi.Quantity from food_item fi where fi.fd_id = '{newFoodID}'") #select quantity for moved food item
                                existingNewQuantity = [int(i[0]) for i in cursor.fetchall()][0] #store existing move quantity to variable
                                updateQuantity = moveQuantity + existingNewQuantity #add to location being moved to, so set to variable
                                currentItemUpdateQuantity = origQuantity - moveQuantity #set variable for update to current location
                                cursor.execute(
                                    f"update foodforyou.food_item set Quantity='{currentItemUpdateQuantity}' where fd_ID='{int(food_id)}'") #write new quantity to database for current location
                                cursor.execute(
                                    f"update foodforyou.food_item set Quantity='{updateQuantity}' where fd_ID='{int(newFoodID)}'") #write new quantity for moved location

                                connection.commit() # write database updates to disk 
                                messagebox.showinfo("Success", "Quantity successfully moved.") #display message indicating success
                            else: #if both items are not the same, show an error
                                messagebox.showerror("ERROR", "The items are not the same. Check units and category.")
                        else:#if item does not exist in location being moved to, insert it
                            cursor.execute(f"select fb.fb_id from food_bank fb where fb.Location = '{locationDD.get()}'") #get food bank id for move location
                            movefb_id = [int(i[0]) for i in cursor.fetchall()][0] #store move location ID in variable
                            cursor.execute(f"select * from food_item fi where fi.Item_name='{item}' and fi.fb_id={fb_id}") #select all columns for item at current location
                            item1 = cursor.fetchall()[0] #store item in variable
                            cursor.execute(f"select MAX(fi.fd_ID) from food_item fi") #find max food_item ID to create unique ID
                            temp = cursor.fetchall() #store in temp var
                            key = 1 #initialize key to 1
                            if (temp != []): #if no IDs exist, 1 will be used to start table
                                key = int(temp[0][0]) + 1 #covert maxID to int and increment by 1 to get new unique ID
                            newQuantity = origQuantity - moveQuantity #store new quantity for current location in variable
                            cursor.execute(
                                    f"update foodforyou.food_item set Quantity='{newQuantity}' where fd_ID='{int(food_id)}'") #update quantity for current location 
                            cursor.execute(
                                f"insert into foodforyou.food_item values ('{item}', '{item1[1]}', {moveQuantity}, '{units}', '{locationDD.get()}', {int(movefb_id)}, {key})"
                            ) #insert quantity for move location

                            messagebox.showinfo("Item does not exist", "The item did not exist in the food bank it was being moved to an entry was created automatically") #indicate success, and addition of new item
                else:
                    messagebox.showerror("ERROR", "Quantity must be an integer.")
            elif (operation == 'delete'): #if operation is delete do code below
                cursor.execute(f"delete from food_item where fd_id = {food_id}") #delete all rows matching current food id
                connection.commit() #commit changes to disk
                messagebox.showinfo("Success", "Item successfully removed.") #show message indicating success
            else:
                messagebox.showerror("ERROR", "Select a valid option from the dropdown.")
            fetchData() #refresh screen
            screen.destroy() #destroy child window

        def showScreen(a, b, c):
            """ ShowScreen
            Displays the update, move, or delete screen based on what is selected in tabControl
            Note: Inputs are not used, but required by tkinter command option for dropdowns
            """
            s = self.screenopt.get()
            #reset to normal state for "update" screen
            quantityinput.configure(state="active")     #reset from "delete"
            unitsInput.configure(state="active")
            submitButton.configure(text="Save changes")
            unitsInput.configure(state="active")
            movelbl.pack_forget()       #clears the widgets from the "move" screen
            locationDD.pack_forget()
            fillerlbl.pack_forget()
            if s == "update":
                pass
            elif s == "delete":
                # disable users from editing the items to be deletion
                quantityinput.configure(state="disabled")
                unitsInput.configure(state="disabled")
                #change the action button text
                submitButton.configure(text="Confirm deletion")
            else:
                # only want to "edit" quantity -> disable everything but quantity
                unitsInput.configure(state="disabled")
                #show moving location dropdown
                fillerlbl.pack(side=BOTTOM, pady=25)
                locationDD.pack(side=BOTTOM, pady=5)
                movelbl.pack(side=BOTTOM)

        #set default screen option as update
        self.screenopt.set("update")
        options = ["update", "move", "delete"]
        # when screenopt is changed, calls showscreen to change the screen
        self.screenopt.trace('w', showScreen)
        #holds the screen options
        tabControl = ttk.Combobox(screen, textvariable=self.screenopt, values=options, font=(font, 12), width=7, state="readonly")
        tabControl.pack(pady=10)
        #add action/function to submit button
        submitButton.configure(command=saveChanges)
        self.screen.resizable(0, 0)       #make the window size not adjustable


class StaffGUI:
    """ class StaffGUI
        Displays the food item table, and allows the user to:
            - Search/Filter: search by item ID, search by item name, filter by location, sort by ascending quantity
            - Update Item: update quantity, move item to another location, or delete an item
            - Add Item: Creates a new food item (user must input food item, category, quantity, units, location)

            Note: Each row displays the distinct items by item ID. Each food item at each food bank has a unique food
                item ID; Similar food items between different food banks have different food item IDs.
    """
    def __init__(self):
        #----------------------setting up screen for "New item"---------
        self.root = Tk()
        root = self.root
        self.root.title("Staff")
        self.screenWidth = 900
        self.root.geometry(f'{self.screenWidth}x540')
        self.ascSort = BooleanVar()
        self.locations = fetchLocations(cursor)         #grab exisiting locations
        use_theme(root, "10")

        #-----------------------------setting up background---------------------------------------
        global fetchData #set fetchData functiont o be global so screen can be refreshed by any class
        #structured to catch errors if user does not have background images,
            # allows the user to run the program without bg images
        try:
            self.bg = PhotoImage(file="img/backgroundimg.png")
            Label(master=root, image=self.bg, borderwidth=0, highlightthickness=0).place(x=0, y=0)

            self.trailing_img = PhotoImage(file="img/trailingIMG.png")
            for i in range(0, self.screenWidth, self.trailing_img.width()):
                Label(master=root, image=self.trailing_img, bg='white').place(x=i, y=480)
        except Exception as e:
            print(e)

        root.configure(background='white') #set background to white

        def onClose(): #override built in close function in Tkinter so connection is terminated to prevent memory leaks on SQL database side.
            connection.close() #close the connection
            root.destroy() #destory the main window

        #-------------------------- item modification functions ---------------------------------------------
        def fetchData():
            search() #call search function to store all entries in cursor
            rows = cursor.fetchall() #set rows from cursor

            # Delete the old table and insert each row in the current database to accomplish refresh
            if rows != 0:
                table.delete(*table.get_children())

                for row in rows: #populate table with new entries
                    table.insert('', END, values=row)

        def search():
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
                cursor.execute(
                    f"SELECT fi.Item_name, fi.Quantity, fi.Units, fi.fd_id, fb.Location from food_item fi join food_bank fb using(fb_id) where fi.Item_name like '{item}' and fb.location like '{location}' and fi.fd_id like '{fd_id}' order by fi.Quantity ASC")
            else: #if ascending not specified use this query
                cursor.execute(
                    f"SELECT fi.Item_name, fi.Quantity, fi.Units, fi.fd_id, fb.Location from food_item fi join food_bank fb using(fb_id) where fi.Item_name like '{item}' and fb.location like '{location}' and fi.fd_id like '{fd_id}'")

        def update(e):
            # taken from focus(e) by jerry
            cursor = table.focus()
            content = table.item(cursor)
            row = content['values']
            item = row[0]
            quantity = row[1]
            units = row[2]
            food_id = row[3]
            location = row[4]
            UpdateItem(root, item, quantity, units, location, food_id)

        def addItem():
            """ addItem()
            Creates a NewItem() class
            """
            NewItem(root)


        #--------------------------------------- search widgets -------------------------------------
        # widgets to search by item
        ttk.Label(root, text="Search by item").place(x=675, y=110)
        ItemSearch = ttk.Entry(root, width=25)
        ItemSearch.place(x=675, y=130)

        # widgets to search by item ID
        ttk.Label(root, text="Search by item ID").place(x=675, y=170)
        IDSearch = ttk.Entry(root, width=25)
        IDSearch.place(x=675, y=190)

        # widgets to filter by location
        ttk.Label(root, text="Sort by location").place(x=675, y=230)
        LocationFilter = ttk.Combobox(root, values=self.locations, state="readonly")
        LocationFilter.place(x=675, y=250)

        # widgets to sort by quantity
        QuantitySortButton = ttk.Checkbutton(root, text="Sort ascending quantity", command=fetchData, onvalue=True,
                                             offvalue=False, variable=self.ascSort)
        QuantitySortButton.place(x=675, y=300)

        # widgets to do the search action
        SearchButton = ttk.Button(root, text="Search", width=15, command=fetchData)
        SearchButton.place(x=675, y=350)

        # widgets to do the "add item" action
        addButton = ttk.Button(text="New Item +", command=addItem, width=15)
        addButton.place(x=675, y=410)


        #------------------------------------ table ---------------------------------------------------
        viewFrame = Frame(root, bd=5, relief='ridge', bg='wheat')
        viewFrame.place(x=30, y=110, width=600, height=350)
        xScroll = Scrollbar(viewFrame, orient=HORIZONTAL)   #allows the user to scroll
        yScroll = Scrollbar(viewFrame, orient=VERTICAL)
        table = ttk.Treeview(viewFrame, columns=(
            'item_to_filter', 'quantity_to_filter', 'units', 'fid_to_filter', 'location_to_filter'),
                             xscrollcommand=xScroll.set,
                             yscrollcommand=yScroll.set)

        table.heading("item_to_filter", text="item")
        table.heading("quantity_to_filter", text="quantity")
        table.heading("units", text="units")
        table.heading("fid_to_filter", text="food id")
        table.heading("location_to_filter", text="locations")

        table.column("item_to_filter", width=100)
        table.column("quantity_to_filter", width=25)
        table.column("units", width=25)
        table.column("fid_to_filter", width=10);
        table.column("location_to_filter", width=100)
        table['show'] = 'headings'

        # get all values and pack the table on to the screen
        table.bind('<ButtonRelease-1>', update)
        fetchData()
        table.pack(fill=BOTH, expand=1)
        root.protocol("WM_DELETE_WINDOW", onClose)

        self.root.resizable(0, 0)                   #make the window size not adjustable
        root.mainloop()


connection = connectToDatabase() #create connection to database using function from utilffy.py
#connection = connectToDatabase("kp", "pass", "127.0.0.1", 3306, "foodforyou")
cursor = connection.cursor() #initialize cursor to database


StaffGUI() #start tkinter interface