#COURSEWORK
#Modules
import os, json, time, tkinter, turtle, threading, copy
from tkinter import messagebox
from num2words import num2words

#NOTE: Any use of the copy module is to solve the issue I was having with variables referencing other variables instead of taking on the value stored within the variable.

#Classes
#---Tree-related---
#Holds all information for a member
class Member():

    #Utilise the database that holds the information for all members and trees
    #Members are usually stored as objects, but will be dictionaries if just extracted from the json file
    #Also holds 'family trees' - arrays of member ids referencing all the members of that tree
    global treedb

    #Used to create new members and convert the dictionaries stored in the json database into usable objects
    def __init__(self,famtree,given_names,surname,gender,dob,dod,notes, ID = None, children = [], spouses = [], father = None, mother = None):
        #If this is being used to convert a dictionary, 
        if ID != None:
            #Give the member object the id stored in the dictionary
            self.ID = ID
        #If this is being used to create a new member,
        else:
            #Assign a new, unique id to the member that will reference its position in the "Members" array
            self.ID = len(treedb['Members'])
        #Assign values to basic attributes using the information provided
        self.given_names = given_names
        self.surname = surname
        self.gender = gender
        self.dob = dob
        self.dod = dod
        #Assign arrays to the 'children' and 'spouses' attributes without accidentally making all members share said arrays
        #These will hold the ids of the children and spouses of the member
        #Children are held as ids
        self.children = list(children)
        #Spouses are held as an array of an id and two dates
        self.spouses = list(spouses)
        self.notes = notes
        #These attributes will hold the ids of the parents of the member
        self.father = father
        self.mother = mother
        #If a new member has been created,
        if ID == None:
            #Add to the 'Members' array and record its id in its main family tree
            treedb['Members'].append(self)
            treedb[famtree].append(self.ID)

    #Shortcut for retrieving a member's full name
    def full_name_get(self):
        return self.given_names + ' ' + self.surname

    #Shortcut for retrieving a member's birth year
    def birth_year_get(self):
        year = self.dob.split(" ")[2]
        if year == "[Unknown]":
            return None
        else:
            return year

    #Define the shortcuts as properties for ease of use        
    full_name = property(full_name_get)
    birth_year = property(birth_year_get)

    #Function for updating all the member's attributes at once
    #Takes in an array of the updated details as its main parameter
    def update_member(self, details):
        order = ['given_names','surname','gender','dob','dod','notes']
        #For every attribute to be updated,
        for i in range(0,len(order)):
            #Update the attribute with the new value
            setattr(self,order[i],details[i])
        #Updates record
        treedb['Members'][self.ID] = self

    #Methods for establishing relationships between members
    #Adds (or removes) a parent and configures the children of that parent
    def add_parent(self, member, parent = None):
        #If there is a parent to assign, (not 'None')
        if member != None:
            #If the parent is male, configure the member's father
            if member.gender == "Male":
                #If the member already had a father,
                if self.father != None:
                    #Remove the member from the old father's children
                    treedb['Members'][self.father].children.remove(self.ID)
                #Add the member to the new father's children
                member.children.append(self.ID)
                #Make the new father the father of the member
                self.father = member.ID
            #If the parent is female, configure the member's mother (same as with the father)
            else:
                if self.mother != None:
                    treedb['Members'][self.mother].children.remove(self.ID)
                member.children.append(self.ID)
                self.mother = member.ID
            #Updates record for parent
            treedb['Members'][member.ID] = member
        #If there is not a parent to assign,
        else:
            self.__dict__[parent] = None
            return
        #Updates record for member and parent
        #It is not necessary to update the record for the old parents - as they are edited directly
        treedb['Members'][self.ID] = self
        treedb['Members'][member.ID] = member

    #Checks if a given id belongs to a spouse of the member and, if so, the index of that id in the member's 'spouses' array
    def locate_spouse(self, ID):
        #Checks all the ids in self.spouses
        for spouse in self.spouses:
            #If the given id has been located,
            if ID == spouse[0]:
                #Return that the id has been found and where it has been found
                pos = self.spouses.index(spouse)
                return True, pos
        #If the given id has not been located, return that the id has not been found (along with some filler)
        return False, 0

    #Configures the spouses of a member
    #Takes in a member to serve as the main member's spouse, a date of marriage and a date of divorce
    def configure_spouse(self, member, dom, dodiv):
        #Checks if the spouse is already recorded as a spouse of the member
        present, pos = self.locate_spouse(member.ID)
        #Assemble the array of necessary data about the spouse
        data = [member.ID, dom, dodiv]
        #If the spouse is not already recorded,
        if present == False:
            #Add the data to self.spouses
            self.spouses.append(list(data))
            #Change the data to reference the main member
            data[0] = self.ID
            #Add the data to the spouse's 'spouses' array
            member.spouses.append(list(data))
        #If the spouse has already been recorded and is in need of updating,
        else:
            #Update the record for said spouse
            self.spouses[pos] = list(data)
            #Change the data to reference the main member
            data[0] = self.ID
            #Locate the main member in the 'spouses' array of the spouse
            present, pos = member.locate_spouse(self.ID)
            #Update the record for the member
            member.spouses[pos] = list(data)
        data = []
        #Updates the records for the member and the spouse
        treedb['Members'][self.ID] = self
        treedb['Members'][member.ID] = member

    #Removes a spouse if recorded accidentally
    def remove_spouse(self, member):
        #Locates the spouse in self.spouses
        present, pos = self.locate_spouse(member.ID)
        #If the spouse is found,
        if present == True:
            #Delete the record for the spouse
            del self.spouses[copy.deepcopy(pos)]
            present, pos = member.locate_spouse(self.ID)
            #Delete the record for the member in the spouse's 'spouses' array
            del member.spouses[copy.deepcopy(pos)]
        #If the spouse is not found,
        else:
            #Raise an error
            raise ValueError
        #Updates the records for the member and the spouse
        treedb['Members'][self.ID] = self
        treedb['Members'][member.ID] = member

#Used to cast member objects as "displays"
#(These are members that are currently being displayed in a tree view.)
#Holds the x,y coordinates of the box that references the member
class Display(Member):
    
    def __init__(self,member,x,y):
        global treedb
        self.__dict__ = copy.deepcopy(member.__dict__)
        self.as_member = member
        self.x = x
        self.y = y

#Class for the pen used to draw the family tree timeline
#Derivative of the RawTurtle class of the turtle module
class Pen(turtle.RawTurtle):

    def __init__(self, screen):
        #Creates a RawTurtle
        super().__init__(screen)
        #Hides the turtle and greatly speeds it up
        self.hideturtle()
        self.speed(1000000)
        #Sets its default position to (0,0)
        self.x = 0
        self.y = 0

    #Moves the turtle to a position based on its coordinates
    def move_to(self,x,y):
        #Records the x,y values of the position it will be moved to
        self.x = x
        self.y = y
        #Moves the turtle to that position
        self.goto(x,y)

    #Makes the turtle draw a rectangle (square) of a given colour based on global sizing choices
    #(There is currently no way to change the global sizing choices, but that could be added as a feature in the future.)
    def draw_rectangle(self, colour):
        #Draws four lines, fills in the space between
        global d
        self.fillcolor(colour)
        self.begin_fill()
        for i in range(4):
            self.forward(d)
            self.left(90)
        self.end_fill()

    #Draws a family tree timeline
    #Ideally, there would be one turtle for each timeline that would allow both timelines to be drawn at once
    #This would greatly speed up the drawing process
    #However, one cannot use threading with anything tkinter-related - as it raises an error - so this cannot be done
    def draw_line(self, start = 0, end = None):
        #Collects global variables
        global to_load, shown, shown_coords, d
        #If there is no set end,
        if end == None:
            #Set the end to the last member to be loaded
            end = len(to_load)
        #Allows the turtle to start drawing
        self.down()
        #For each member to be drawn,
        for i in range(start, end):
            #Draw a (blue) box on the canvas, representing said member
            self.draw_rectangle('blue')
            #Then cast the member as a displayed member ('display'), along with the x,y coordinates of its box
            showob = Display(to_load[i],self.x,self.y)
            #Store all displayed members in the 'shown' array
            shown.append(showob)
            #Store all the coordinates for the displayed members in the 'shown' array
            shown_coords.append([self.x,self.y])
            #If not the penultimate member to be drawn,
            if i != (end - 1):
                #Moves d*2 spaces to the right so that it doesn't draw over another box.
                self.move_to(self.x + d*2, self.y)
        #Stops drawing
        self.up()

#Thread for searching through a family tree
#Used when finding the relationship between two members
class SearchThread(threading.Thread):

    #Collects necessary global variables
    global treedb, focus_tree, loaded_frames

    #Parameters :
    #'origin' = Member of origin (that it searches the relatives of)
    #'to_find' = the member to find
    #'ups' = amount of times previous search threads have gone up to a member's parents
    #'downs' = amount of times previous search threads have gone down to a member's children
    #'sides' = amount of times previous search threads have gone to a member's spouses
    def __init__(self, origin, to_find, ups = 0, downs = 0, sides = 0):
        super().__init__()
        self.origin = origin
        self.to_find = to_find
        self.ups = ups
        self.downs = downs
        self.sides = sides

    def run(self):
        #Because there is no way to halt a thread directly, this must be dictated by the 'halt_all' variable
        global halt_all
        #Array for all the threads to be run off of this one
        threads = []
        #Retrieves the array of all the members that have already been searched (so that they aren't searched twice)
        #(Also prevents endless searching when two members are not related.)
        checked = loaded_frames[-1].checked
        #If the current member has not be searched,
        if self.origin.ID not in checked:
            #Add to checked
            checked.append(self.origin.ID)
            loaded_frames[-1].checked.append(self.origin.ID)
        #Gets parents of current member
        parents = [self.origin.father, self.origin.mother]
        #For each parent,
        for ID in parents:
            #If a parent has been recorded,
            if ID != None:
                #If the parent is the member that needed to be found,
                if ID == self.to_find:
                    #If the program has not already been told to stop searching,
                    if halt_all == False:
                        #Increments ups
                        self.ups += 1
                        #Returns ups, downs and sides. Tells the program to stop searching.
                        loaded_frames[-1].ups = self.ups
                        loaded_frames[-1].downs = self.downs
                        loaded_frames[-1].sides = self.sides
                        halt_all = True
                        #Halts processing of current function
                        return True
                #If the parent has not yet been checked,
                elif ID not in checked:
                    #Add parent to checked
                    loaded_frames[-1].checked.append(ID)
                    #Create a search thread that will search through the parent's relatives and add it to the 'threads' array
                    threads.append(SearchThread(treedb['Members'][ID], self.to_find, ups = self.ups + 1, downs = self.downs, sides = self.sides))
        #For each spouse,
        for spouse in self.origin.spouses:
            #Get the spouse's id
            spouse_ID = spouse[0]
            #If the spouse is the member we are looking to find,
            if spouse_ID == self.to_find:
                #If the program has not already been told to stop searching,
                if halt_all == False:
                    #Increment sides
                    self.sides += 1
                    #Returns ups, downs and sides. Tells the program to stop searching.
                    loaded_frames[-1].ups = self.ups
                    loaded_frames[-1].downs = self.downs
                    loaded_frames[-1].sides = self.sides
                    halt_all = True
                    #Halts processing of current function
                    return True
            #If the spouse has not already been checked,
            elif spouse_ID not in checked:
                #Add spouse to checked
                loaded_frames[-1].checked.append(spouse_ID)
                #Create a search thread that will search through the spouse's relatives and add it to the 'threads' array
                threads.append(SearchThread(treedb['Members'][spouse_ID], self.to_find, ups = self.ups, downs = self.downs, sides = self.sides + 1))
        #For each child,
        for child in self.origin.children:
            #If the child is the member we are looking to find,
            if child == self.to_find:
                #Same as above, but downs is incremented
                if halt_all == False:
                    self.downs += 1
                    loaded_frames[-1].ups = self.ups
                    loaded_frames[-1].downs = self.downs
                    loaded_frames[-1].sides = self.sides
                    halt_all = True
                    return True
            elif child not in checked:
                loaded_frames[-1].checked.append(child)
                threads.append(SearchThread(treedb['Members'][child], self.to_find, ups = self.ups, downs = self.downs + 1, sides = self.sides))
        #For every new thread in the 'threads' array,
        for thread in threads:
            #If the program has not already been told to stop searching,
            if halt_all == False:
                #Set off all the new threads
                thread.start()
                thread.join()

#---Custom Widgets---
#This widget is msotly used to display the information about a chosen member, but it has some other uses.
#It is a derivative of the tkinter.Frame object.
class ScrollBox(tkinter.Frame):

    def __init__(self, master, state='disabled', startingText='', height=5, width=35):
        #Initialise tkinter.Frame
        super().__init__(master)
        #Attribute to keep track of the state
        self.state = state
        #Creates a scroll bar for navigating the text
        scroll_bar = tkinter.Scrollbar(self)
        #Creates a tkinter.Text the same size as the frame
        self.text_box = tkinter.Text(self, height=height, width=width, state=state)

        #Configures the scroll bar so that it navigates the tkinter.Text widget
        scroll_bar.configure(command=self.text_box.yview)
        self.text_box.configure(yscrollcommand=scroll_bar.set)

        #Inserts any starting text into the tkinter.Text widget
        self.text_box.insert('1.0', startingText)

        #Packs the widgets inside the frame
        scroll_bar.pack(side='right', fill='y')
        self.text_box.pack(side='left', fill='y')

    #Changes the state of the text widget
    #('disabled' means that the text inside can't be edited, allowing it to be used for display purposes)
    def change_state(self, state):
        #Keeps track of the state
        self.state = state
        #Changes the state of the text widget
        self.text_box.configure(state=state)

    #Permits changing the state with an attribute for ease of use
    text_state = property(None, change_state)

    #Functions to get and edit the text widget, like one would be able to do normally
    #Retrieving text
    def get(self):
        return self.text_box.get('1.0', 'end')

    #Inserting text
    def insert(self, text):
        if self.state == 'normal':
            self.text_box.insert('1.0', text)
        else:
            #(Cannot insert text into disabled text widget, so must temporarily change its state)
            self.text_state = 'normal'
            self.text_box.insert('1.0', text)
            self.text_state = 'disabled'

    #Emptying text widget of text
    def clear(self):
        if self.state == 'normal':
            self.text_box.delete('1.0', 'end')
        else:
            self.text_state = 'normal'
            self.text_box.delete('1.0', 'end')
            self.text_state = 'disabled'

    #Displays the details about a member
    def show_member_info(self, member):
        #Clears the text widget of any pre-existing text
        self.clear()
        #If there is a member to extract data from,
        if member != None:
            #Extract the data from said member and combine it all into one strong
            member_info = ""
            member_info += "Given Names: " + member.given_names + "\n"
            member_info += "Surname: " + member.surname + "\n"
            member_info += "Gender: " + member.gender + "\n"
            member_info += "Date of Birth: " + member.dob + "\n"
            member_info += "Date of Death: " + member.dod + "\n"
            member_info += "Notes: \n" + member.notes
            #Insert that string into the text widget
            self.insert(member_info)

    #Displays the details of multiple members via their ids. Used to display relatives.
    #Works similarly to the previous function
    def show_multiple(self, IDs, is_spouse=False):
        global treedb
        #Clears the text widget
        self.clear()
        #Separates each member with a line
        member_info = "-------- \n"
        #If not displaying spouses, display the same basic info as you would in the previous function.
        if is_spouse == False:
            for ID in IDs:
                member = treedb['Members'][ID]
                member_info += "Index: " + str(member.ID) + "\n"
                member_info += "Given Names: " + member.given_names + "\n"
                member_info += "Surname: " + member.surname + "\n"
                member_info += "Gender: " + member.gender + "\n"
                member_info += "Date of Birth: " + member.dob + "\n"
                member_info += "Date of Death: " + member.dod + "\n"
                member_info += "Notes: \n" + member.notes + "\n -------- \n"
        #If displaying spouses, display dom and dodiv as well as basic info.
        else:
            for data in IDs:
                member = treedb['Members'][data[0]]
                member_info += "Name: " + member.full_name + "\n"
                member_info += "Date of Marriage: " + data[1] + "\n"
                member_info += "Date of Divorce: " + data[2] + "\n -------- \n"
        #Insert the data for each member into the text widget
        self.insert(member_info)

#---Saving Thread---
#This is a solution to the current saving issue
#It does not solve the problem, it only lessens its effect.
class SaveThread(threading.Thread):

    def __init__(self):
        super().__init__()

    def run(self):
        while True:
            time.sleep(10)
            save_db()

#---Views---
#View for selecting user type
#Two options: Normal or Admin
class UserSelect(tkinter.Frame):

    def __init__(self,master):
        global treedb, width, height
        super().__init__(master, height=height, width=width)
        greet = tkinter.Label(self,text="Welcome to the Family Tree Program! \n Please select which type of user you are.")
        #If normal user, produce Action Select view
        norm = tkinter.Button(self,text="Normal User", command = lambda : show_acts(normal = True))
        #If admin user, produce view that asks for admin password
        adm = tkinter.Button(self,text="Admin",command=get_pass)
        #Arranges everything
        greet.grid(row = 0, column = 1)
        norm.grid(row = 1, column = 0)
        adm.grid(row = 1, column = 2)

#View for entering admin password        
class EnterPassword(tkinter.Frame):

    def __init__(self,master):
        global width, height
        super().__init__(master, height=height, width=width)
        info1 = tkinter.Label(self,text="Confirmation")
        info2 = tkinter.Label(self,text="Enter the admin password:")
        self.enter_pass = tkinter.Entry(self)
        submit = tkinter.Button(self,text="Submit",command=self.butt_func)
        self.error = tkinter.Label(self)
        #Arranges everything
        info1.pack()
        info2.pack()
        self.enter_pass.pack()
        submit.pack()
        self.error.pack()

    #Function to check if entered password is correct
    def butt_func(self):
        global admin_pass, admin
        #Retrieves user input
        entered = self.enter_pass.get()
        #Compares user input with admin password
        #If password is correct,
        if entered == admin_pass:
            #Grant admin access to the program
            admin = True
            #Produce Action Select view
            show_acts()
        #If not,
        else:
            #Show an error message
            self.error.configure(text="Password is incorrect.")
        
#View for selecting an action
#Actions for normal user: View Tree, Find Relationship
#Actions for admin user: View Tree, Find Relationship, Configure Trees, Configure Members
#Also has drop-down menu for selecting a family tree to focus on
class ActionSelect(tkinter.Frame):

    def __init__(self, master):
        global admin, treedb, width, height, focus_tree
        infocol = 1
        super().__init__(master, height=height, width=width)
        info = tkinter.Label(self,text="Select an Action")
        view_tree = tkinter.Button(self,text="Display a Family Tree", command = self.show_tree)
        find_rels = tkinter.Button(self,text="Find a Relationship", command = self.find_relationship)
        tree_lab = tkinter.Label(self,text="Select a Family Tree:")
        self.tree = tkinter.StringVar(self, focus_tree)
        keys = list(treedb.keys())
        keys.remove("Members")
        keys.sort()
        tree_dd = tkinter.OptionMenu(self,self.tree, *keys, command = change_tree_focus)
        view_tree.grid(row = 1, column = 0)
        find_rels.grid(row = 1, column = 2)
        self.error = tkinter.Label(self)
        #If user has admin access,
        if admin == True:
            #Give access to admin content
            infocol = 3
            config_trees = tkinter.Button(self,text="Configure Family Trees", command = self.configure_trees)
            config_members = tkinter.Button(self,text="Configure Members", command = self.configure_members)
            config_trees.grid(row = 1, column = 6)
            config_members.grid(row = 1, column = 4)
        info.grid(row = 0, column = infocol)
        tree_lab.grid(row = 2, column = infocol-1)
        tree_dd.grid(row = 2, column = infocol+1)
        self.error.grid(row = 3, column = infocol)

    #Function to create a Tree View
    def show_tree(self):
        global focus_tree
        #If no tree has been selected,
        if focus_tree == '':
            #Return an error
            self.error.config(text = "Please select a tree.")
        #If there's nothing to show in the selected tree,
        elif treedb[focus_tree] == []:
            #Inform user
            self.error.config(text = "There are no members in this tree.")
        #If all is well,
        else:
            #Make a Tree View
            global loaded_frames, back
            back.config(state = 'disabled')
            loaded_frames[-1].pack_forget()
            frame = TreeView(window, focus_tree)
            loaded_frames.append(frame)
            frame.pack(fill='both',expand=1)
            back.config(state = 'normal')

    #Function to create a Find Relationship View
    def find_relationship(self):
        global focus_tree
        #If no tree has been selected,
        if focus_tree == '':
            #Return an error
            self.error.config(text = "Please select a tree.")
        #If there are no members in the tree,
        elif treedb[focus_tree] == []:
            #Return error
            self.error.config(text = "There are no members in this tree.")
        #If all is well,
        else:
            #Produces a Find Relationship view
            #(Doesn't use a global function as this is the only way of accessing it)
            global loaded_frames, back
            back.config(state = 'disabled')
            #Unload previous view
            loaded_frames[-1].pack_forget()
            #Create a Find Relationship view
            frame = GetRel(window)
            #Add view to loaded_frames
            loaded_frames.append(frame)
            #Display view on screen
            frame.pack(fill='both',expand=1)
            back.config(state = 'normal')

    #Function for creating a Configure Tree view
    def configure_trees(self):
        global loaded_frames, back
        back.config(state = 'disabled')
        loaded_frames[-1].pack_forget()
        frame = ConfigureTree(window)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
        back.config(state = 'normal')

    #Function for creating a Configure Members view
    def configure_members(self):
        global focus_tree
        #If no tree has been selected,
        if focus_tree == '':
            #Return an error
            self.error.config(text = "Please select a tree.")
        else:
            #Produce a Configure Members view
            global loaded_frames, do_save, loaded_tree, back
            back.config(state = 'disabled')
            do_save = False
            loaded_tree = None
            loaded_frames[-1].pack_forget()
            frame = ConfigureMembers(window)
            loaded_frames.append(frame)
            frame.pack(fill='both',expand=1)
            back.config(state = 'normal')

#View for editing a family tree
#Enables three actions: Creating trees, renaming trees and deleting trees
class ConfigureTree(tkinter.Frame):

    global treedb, width, height

    def __init__(self,master):
        super().__init__(master, height=height, width=width)
        heading = tkinter.Label(self,text="Configure Family Trees")
        subheading = tkinter.Label(self,text="Please choose an action:")
        #For creating a tree, a global function is used - as multiple ways of accessing this view
        create_tree_butt = tkinter.Button(self,text="Create a Tree",command=make_tree)
        rename_tree_butt = tkinter.Button(self,text="Rename a Tree",command=self.rename_tree)
        delete_tree_butt = tkinter.Button(self,text="Delete a Tree",command=self.delete_tree_func)
        self.error = tkinter.Label(self)

        heading.pack()
        subheading.pack()
        create_tree_butt.pack()
        rename_tree_butt.pack()
        delete_tree_butt.pack()
        self.error.pack()

    #Creates a 'change tree name' view
    def rename_tree(self):
        global loaded_frames, back
        back.config(state = 'disabled')
        loaded_frames[-1].pack_forget()
        frame = ChangeTreeName(window)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
        back.config(state = 'normal')
        
    #Creates a 'delete tree' view
    def delete_tree_func(self):
        global loaded_frames, back
        back.config(state = 'disabled')
        loaded_frames[-1].pack_forget()
        frame = DeleteTree(window)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
        back.config(state = 'normal')

#View for creating new family trees
class CreateTree(tkinter.Frame):

    def __init__(self,master):
        global width, height
        super().__init__(master, height=height, width=width)
        heading = tkinter.Label(self,text="Create a Family Tree")
        subheading = tkinter.Label(self,text="Enter the name of the family tree you would like to create. \n (Perhaps use a prominent surname for this.)")
        self.tree_ent = tkinter.Entry(self)
        submit = tkinter.Button(self,text="Submit", command = self.add_tree)
        self.error = tkinter.Label(self,text="")
        heading.pack()
        subheading.pack()
        self.tree_ent.pack()
        submit.pack()
        self.error.pack()

    #Creates a new family tree, provided there are no other trees under that name
    def add_tree(self):
        global loaded_frames
        global treedb
        #Collects user input
        name = self.tree_ent.get()
        #Checks if a name has been entered and hasn't already been taken by another tree
        if name == '':
            self.error.configure(text = "You must enter a name for the tree.")
        elif name in treedb.keys():
            self.error.configure(text = "Sorry, but there is already a tree under that name.")
        else:
            #Creates a new family tree
            treedb[name] = []
            #Informs user of this
            messagebox.showinfo("Success","You have successfully created a new tree.")
            go_back(1)
    
#Renaming a tree
class ChangeTreeName(tkinter.Frame):

    global treedb, width, height

    def __init__(self,master):
        super().__init__(master, height=height, width=width)
        heading = tkinter.Label(self,text="Rename a Family Tree")
        subheading = tkinter.Label(self,text="Select the tree you would like to rename and enter the new name below.")
        tree_lab = tkinter.Label(self,text="Family Tree:")
        self.tree = tkinter.StringVar(self)
        keys = list(treedb.keys())
        keys.remove("Members")
        keys.sort()
        tree_dd = tkinter.OptionMenu(self, self.tree, *keys)
        change_lab = tkinter.Label(self,text="New Name:")
        self.tree_ent = tkinter.Entry(self)
        submit = tkinter.Button(self,text="Change",command=self.ask_confirmation)
        self.error = tkinter.Label(self,text="")
        heading.pack()
        subheading.pack()
        tree_lab.pack()
        tree_dd.pack()
        change_lab.pack()
        self.tree_ent.pack()
        submit.pack()
        self.error.pack()

    #Speedbump to ensure that user actually wants to rename tree
    def ask_confirmation(self):
        #If the user has not selected a tree to rename,
        if self.tree.get() == '':
            #Return an error and halt function
            self.error.config(text = "Please select a tree to rename.")
            return False
        response = messagebox.askquestion("Change Name","Are you sure you want to change this tree's name?")
        if response == "yes":
            self.confirmed()

    #Renames tree
    def confirmed(self):
        global loaded_frames
        #Collects user inputs
        old_name = self.tree.get()
        new_name = self.tree_ent.get()
        #Validates new name for tree
        if new_name == '':
            self.error.configure(text = "You must enter a name for the tree.")
        elif new_name in treedb.keys():
            self.error.configure(text = "Sorry, but there is already a tree under that name.")
        #If the new name is suitable,
        else:
            #Create a new tree by that name, copy contents of original tree to that tree
            treedb[new_name] = treedb[old_name]
            #Destroys the original tree
            del treedb[old_name]
            #Informs user of success
            messagebox.showinfo("Success","You have successfully renamed this tree.")
            go_back(1)

#Deleting a tree
class DeleteTree(tkinter.Frame):

    global treedb, width, height

    def __init__(self,master):
        super().__init__(master, height=height, width=width)
        heading = tkinter.Label(self,text="Delete a Family Tree")
        subheading = tkinter.Label(self,text="Select the tree you would like to delete.")
        tree_lab = tkinter.Label(self,text="Family Tree:")
        self.tree = tkinter.StringVar(self, '')
        keys = list(treedb.keys())
        keys.remove("Members")
        keys.sort()
        tree_dd = tkinter.OptionMenu(self,self.tree,*keys)
        submit = tkinter.Button(self,text="Delete Tree",command=self.ask_confirmation)
        warning = tkinter.Label(self,text="WARNING: This action cannot be reversed.")
        self.error = tkinter.Label(self,text="")
        heading.pack()
        subheading.pack()
        tree_lab.pack()
        tree_dd.pack()
        submit.pack()
        warning.pack()
        self.error.pack()

    #Speedbump to ensure that user actually wants to delete tree
    def ask_confirmation(self):
        #If the user has not selected a tree to delete,
        if self.tree.get() == '':
            #Return an error and halt function
            self.error.config(text = "Please select a tree to delete.")
            return False
        #Ask for confirmation from the user
        response = messagebox.askquestion("Delete Tree","Are you sure you want to delete '"+self.tree.get()+"'?")
        if response == "yes":
            self.confirmed()

    #Deletes the tree
    def confirmed(self):
        global loaded_frames
        #Collects user input
        name = self.tree.get()
        #Deletes tree
        del treedb[name]
        messagebox.showinfo("Success","You have successfully deleted this tree.")
        go_back(1)

#View for providing actions to configure the members of a tree
#Actions: Creating, Importing, Editing and Removing members
#Importing a member = Taking a member that exists in one family tree and making it a part of another.
class ConfigureMembers(tkinter.Frame):

    global height, width

    def __init__(self, master):
        super().__init__(master, height=height, width=width)
        heading = tkinter.Label(self, text = "Configure Members")
        subheading = tkinter.Label(self, text = "Please select an action.")
        #Uses global function to produce a Get Details View in create mode
        add_mem_butt = tkinter.Button(self,text="Create a Member",command= lambda : get_deets("Create"))
        import_mem_butt = tkinter.Button(self, text = "Import a Member", command = self.import_mem)
        edit_mem_butt = tkinter.Button(self, text = "Edit a Member",command = self.edit_mem)
        remove_mem_butt = tkinter.Button(self, text = "Remove a Member", command = self.remove_mem)
        self.error = tkinter.Label(self)

        heading.pack()
        subheading.pack()
        add_mem_butt.pack()
        import_mem_butt.pack()
        edit_mem_butt.pack()
        remove_mem_butt.pack()
        self.error.pack()

    #Produces an Import Member view
    #Allows user to take a member that exists in a family tree and make it a part of another one
    #(The selected member will then be a part of both trees simultaneously.)
    def import_mem(self):
        global loaded_frames, back
        back.config(state = 'disabled')
        loaded_frames[-1].pack_forget()
        frame = ImportMember(window)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
        back.config(state = 'normal')

    #Produces an Edit Member view
    def edit_mem(self):
        global focus_tree
        #Checks if there are members in the selected family tree to edit
        if treedb[focus_tree] == []:
            #If not, return error
            self.error.configure(text = "There are no members in this tree to edit.")
        else:
            #If so, produce an Edit Member view
            global loaded_frames, back
            back.config(state = 'disabled')
            loaded_frames[-1].pack_forget()
            frame = EditMember(window)
            loaded_frames.append(frame)
            frame.pack(fill='both',expand=1)
            back.config(state = 'normal')

    #Produces a Remove Member view (works like above function)
    def remove_mem(self):
        global focus_tree
        if treedb[focus_tree] == []:
            self.error.configure(text = "There are no members in this tree to remove.")
        else:
            global loaded_frames, back
            back.config(state = 'disabled')
            loaded_frames[-1].pack_forget()
            frame = RemoveMember(window)
            loaded_frames.append(frame)
            frame.pack(fill='both',expand=1)
            back.config(state = 'normal')

#View for importing members
#First use of the "get members from tree" feature
#How it works:
#   1. Object has an attribute, usually [name]_beneath, in which to store a member
#   2. Object has a method, usually set_[name], which changes the value of [name]_beneath and usually some other things
#   3. Object makes use of the global "find_from_tree" function in a method that usually also contains some input validation.
#      This function takes in the name of the method used to change the value of [name]_beneath as a parameter.
#   4. (See later on for how the "find_from_tree" functions works.) User is allowed to select a member from a family tree.
#   5. The selected member is stored in [name]_beneath and used as necessary.
class ImportMember(tkinter.Frame):

    global width, height

    def __init__(self, master):
        super().__init__(master, height=height, width=width)
        #Here, [name]_beneath is "importee_beneath"
        self.importee_beneath = None
        self.tree = tkinter.StringVar(self, '')
        heading = tkinter.Label(self, text = "Import a Member")
        #Drop-down menu that allows the user to select a family tree to import from
        tree_lab = tkinter.Label(self,text="Import from:")
        keys = list(treedb.keys())
        keys.remove("Members")
        keys.sort()
        tree_dd = tkinter.OptionMenu(self,self.tree,*keys)
        mem_lab = tkinter.Label(self, text = "Importee:")
        self.mem_box = ScrollBox(self)
        change_mem = tkinter.Button(self, text = "Select a Member", command = self.change)
        import_butt = tkinter.Button(self, text = "Import", command = self.import_mem)
        self.error = tkinter.Label(self)

        heading.pack()
        tree_lab.pack()
        tree_dd.pack()
        mem_lab.pack()
        self.mem_box.pack()
        change_mem.pack()
        import_butt.pack()
        self.error.pack()

    #Function for getting importee_beneath
    def get_mem(self):
        return self.importee_beneath

    #Function for setting importee_beneath
    def set_mem(self, value):
        #Changes value of importee_beneath
        self.importee_beneath = value
        #Shows information about the selected member in the Scroll Box.
        self.mem_box.show_member_info(value)

    #Makes importee_beneath and its associated functions into a property
    importee = property(get_mem, set_mem)

    #Function for selecting a member to import
    def change(self):
        global focus_tree
        #Checks if user has chosen a tree to import from
        if self.tree.get() == '':
            #If not, return an error and halt the function
            self.error.config(text = "Please choose a tree to import from.")
            return False
        #Checks that the tree the user has chosen to import from is not the tree the user is importing to.
        elif self.tree.get() == focus_tree:
            #If not, return an error and halt the function
            self.error.config(text = "You are already importing to that tree.")
            return False
        #If everything is ok,
        else:
            #Use the "find_from_tree" function to allow the user to select a member from their selected family tree
            find_from_tree("set_mem", tree = self.tree.get())

    #Function for importing the chosen member into the tree
    def import_mem(self):
        global treedb, focus_tree
        #If no member has been selected,
        if self.importee == None:
            #Inform user and don't import the member
            self.error.config(text = "Please select a member to import.")
        #If that member is already in the tree the user is importing to,
        #(Checks if the ID of the chosen member is already in the family tree)
        elif self.importee.ID in treedb[focus_tree]:
            #Inform user and don't import the member
            self.error.config(text = "That member is already in this tree.")
        #If all is well,
        else:
            #Add the (ID for the) member to the family tree
            treedb[focus_tree].append(self.importee.ID)
            #Inform the user of this success
            messagebox.showinfo("Success!", "You have successfully imported a member.")

#View for editing members
#Works like above, except the user selects members from the tree of focus and can edit them
class EditMember(tkinter.Frame):

    global height, width

    def __init__(self, master):
        super().__init__(master, height=height, width=width)
        self.member_beneath = None
        heading = tkinter.Label(self, text = "Edit a Member")
        subheading = tkinter.Label(self, text = "Select the member you would like to edit.")
        mem_lab = tkinter.Label(self, text = "Member:")
        self.mem_box = ScrollBox(self)
        change_mem = tkinter.Button(self, text = "Select Member", command = lambda : find_from_tree("set_mem"))
        edit = tkinter.Button(self, text = "Edit", command = self.edit)
        self.error = tkinter.Label(self)

        heading.pack()
        subheading.pack()
        mem_lab.pack()
        self.mem_box.pack()
        change_mem.pack()
        edit.pack()
        self.error.pack()

    def get_mem(self):
        return self.member_beneath

    def set_mem(self, value):
        self.member_beneath = value
        self.mem_box.show_member_info(value)

    member = property(get_mem, set_mem)

    #Function for editing the selected member
    def edit(self):
        #Checks if a member has been selected,
        if self.member == None:
            #If not, return an error
            self.error.config(text = "You must select a member to edit.")
        #If so,
        else:
            #Create a "Get Details" view in edit mode
            get_deets("Edit", member = self.member)

#View for removing members from a tree
#Works as above, but the user removes a member from a tree instead of editing them
#(By removing them from the tree, the user will no longer be able to access them through that tree.)
class RemoveMember(tkinter.Frame):

    global treedb, width, height

    def __init__(self,master):
        super().__init__(master, height=height, width=width)
        self.member_beneath = None
        heading = tkinter.Label(self,text="Remove a Member")
        subheading = tkinter.Label(self,text="Select the member you would like to remove.")
        mem_lab = tkinter.Label(self, text = "Member:")
        self.mem_box = ScrollBox(self)
        change_mem = tkinter.Button(self, text = "Select Member", command = lambda : find_from_tree("set_mem"))
        submit = tkinter.Button(self, text = "Remove Member", command = self.ask_confirmation)
        warning = tkinter.Label(self, text = "WARNING: This action cannot be reversed.")
        self.error = tkinter.Label(self,text="")
        
        heading.pack()
        subheading.pack()
        mem_lab.pack()
        self.mem_box.pack()
        change_mem.pack()
        submit.pack()
        warning.pack()
        self.error.pack()

    def get_mem(self):
        return self.member_beneath

    def set_mem(self, value):
        self.member_beneath = value
        self.mem_box.show_member_info(value)

    member = property(get_mem, set_mem)

    #Speedbump to ensure that user is making the right choice - as if a member is removed accidentally, it would be difficult to get them back.
    def ask_confirmation(self):
        if self.member == None:
            self.error.config(text = "Please select a member to remove.")
            return False
        self.error.config(text = "")
        response = messagebox.askquestion("Change Name","Are you sure you want to remove '"+self.member.full_name+"'?")
        if response == "yes":
            self.confirmed()

    #If the user is sure about his/her decision,
    def confirmed(self):
        global treedb, focus_tree
        #Removes the member('s ID) from the tree
        treedb[focus_tree].remove(self.member.ID)
        #Informs the user of the success
        messagebox.showinfo("Success!","You have successfully removed this member.")
        #Resets member to None.
        self.member = None
        
#View for collecting details
#View-types = "Create", "Edit", "Search"
class GetDetails(tkinter.Frame):
    
    global treedb, focus_tree, loaded_frames, width, height

    def __init__(self, master, view_type, member = None, height_local = None, width_local = None):
        #'Get Details' views will not always need to fit the screen, so checks for custom sizing choices
        #(If there are no custom sizing choices, set to full screen.)
        if height_local == None:
            height_local = height
        if width_local == None:
            width_local = width
        super().__init__(master, height=height_local, width=width_local)
        #The variable "view-type" changes the contents of the view
        self.view_type = view_type
        self.member = member
        #Array containing all the months for dates, including an option for where the month is unknown
        months = ['[Unknown]', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        #Attributes that are dictated using drop-down menus require 'StringVar's to store their current valu
        #These attributes are: birth month, death month and gender
        #Create StringVars for the birth month and the death month of the member in question
        self.def_b_month = tkinter.StringVar(self, '[Unknown]')
        self.def_d_month = tkinter.StringVar(self, '[Unknown]')
        #If the view has been created in 'Create' mode,
        if self.view_type == "Create":
            #Define title, subtitle and button text
            title = "Create a Member"
            subtitle = "(Enter all known details of this member into the boxes below.) \n (Separate given names with a space.) \n (You don't need to fill in all the boxes.)"
            buttontext = "Create"
        #If the view has been created in 'Edit' mode,
        elif self.view_type == "Edit":
            #Define title, subtitle and button text
            title = "Edit a Member"
            subtitle = "(You change or add any necessary details by adjusting the contents of the correct box.)"
            buttontext = "Confirm Changes"
        #If the view has been created in 'Search' mode,
        else:
            #Define title, subtitle and button text
            title = "Search for a Member"
            subtitle = "(Fill in the boxes with any necessary search criteria.)"
            buttontext = "Search"
            #Create an attribute for storing all found members
            self.found = []
        #Two halves of the view:
        top = tkinter.Frame(self)
        #and
        bottom = tkinter.Frame(self)
        #This is so that the view is not needlessly wide due to oddly-sized columns from other widgets
        heading = tkinter.Label(top, text=title)
        subheading = tkinter.Label(top, text=subtitle)
        gname_lab = tkinter.Label(bottom, text="Given Names:")
        #Allows user to enter member given names
        self.gname_ent = tkinter.Entry(bottom)
        sname_lab = tkinter.Label(bottom, text="Surname:")
        #Allows user to enter member surname
        self.sname_ent = tkinter.Entry(bottom)
        gen_lab = tkinter.Label(bottom, text="Gender")
        #If the view has not been created in 'Search' mode,
        if self.view_type != 'Search':
            #Create a StringVar for the gender of the member in question
            self.def_gen = tkinter.StringVar(bottom, 'Male')
            #Allows user to select member gender
            self.gen = tkinter.OptionMenu(bottom, self.def_gen, *['Male', 'Female'])
            #Allows user to enter date of birth
            #Birth day:
            self.bday = tkinter.Entry(bottom)
            #Birth month:
            bmonth = tkinter.OptionMenu(bottom, self.def_b_month, *months)
            #Birth year:
            self.byear = tkinter.Entry(bottom)
            #Allows user to enter date of death
            #Death day:
            self.dday = tkinter.Entry(bottom)
            #Death month:
            dmonth = tkinter.OptionMenu(bottom, self.def_d_month, *months)
            #Death year:
            self.dyear = tkinter.Entry(bottom)
            #Allows user to add notes about the member
            notes_lab = tkinter.Label(bottom, text="Notes:")
            self.notes_ent = ScrollBox(bottom, width=20, height=5, state = 'normal')
            #Arranges everything
            self.bday.grid(row=7, column=0)
            bmonth.grid(row=7, column=1)
            self.byear.grid(row=7, column=2)
            self.dday.grid(row=9, column=0)
            dmonth.grid(row=9, column=1)
            self.dyear.grid(row=9, column=2)
            notes_lab.grid(column=3, row=3)
            self.notes_ent.grid(column=3, row=4)
        #If the view has been created in 'Search' mode,
        else:
            #Create a StringVar for the gender of the member in question
            self.def_gen = tkinter.StringVar(bottom, 'Either')
            #Allows user to or to not select member gender
            self.gen = tkinter.OptionMenu(bottom, self.def_gen, *['Either','Male', 'Female'])
            #Create labels to show the range
            b_labs = [tkinter.Label(bottom, text="from"), tkinter.Label(bottom, text="to")]
            d_labs = [tkinter.Label(bottom, text="from"), tkinter.Label(bottom, text="to")]
            #Allows user to enter a starting birth year and an ending birth year to use as a range for members to search for
            self.start_b_year = tkinter.Entry(bottom)
            self.end_b_year = tkinter.Entry(bottom)
            #Same with the year of death
            self.start_d_year = tkinter.Entry(bottom)
            self.end_d_year = tkinter.Entry(bottom)
            #Arranges everything
            b_labs[0].grid(row=7, column=0)
            self.start_b_year.grid(row=7, column=1)
            b_labs[1].grid(row=7, column=2)
            self.end_b_year.grid(row=7, column=3)
            d_labs[0].grid(row=9, column=0)
            self.start_d_year.grid(row=9, column=1)
            d_labs[1].grid(row=9, column=2)
            self.end_d_year.grid(row=9, column=3)
        #If the view has been created in 'Edit' mode,
        if view_type == "Edit":
            #Fill in all known details about the member
            #Given names:
            self.gname_ent.insert(0, self.member.given_names)
            #Surname:
            self.sname_ent.insert(0, self.member.surname)
            #Gender:
            self.def_gen.set(self.member.gender)
            #Notes:
            self.notes_ent.insert(self.member.notes)
            #Date of birth:
            dob = self.member.dob.split(" ")
            if dob[0] != "[Unknown]":
                self.bday.insert(0,dob[0])
            self.def_b_month.set(dob[1])
            if dob[2] != "[Unknown]":
                self.byear.insert(0,dob[2])
            #Date of death:
            dod = self.member.dod.split(" ")
            if dod[0] != "[Unknown]":
                self.dday.insert(0,dod[0])
            self.def_d_month.set(dod[1])
            if dod[2] != "[Unknown]":
                self.dyear.insert(0,dod[2])
            #(Enter nothing if part of date is not known)
            #Add buttons to configure spouses and parents of member
            #This allows the user to draw relationships between members
            config_spouses_butt = tkinter.Button(self, text = "Configure Spouses", command = self.set_spouse)
            config_parents_butt = tkinter.Button(self, text = "Configure Parents", command = self.set_parent)
            config_spouses_butt.grid(row = 5, column = 0)
            config_parents_butt.grid(row = 6, column = 0)
        #Creates labels for dates
        dob_lab = tkinter.Label(bottom, text="Date Of Birth:")
        dod_lab = tkinter.Label(bottom, text="Date Of Death:")
        #Creates a submit button. The function of this button depends on the view-type.
        self.submit = tkinter.Button(self, text=buttontext, command=self.collect_details)
        #Label for showing errors
        self.error = tkinter.Label(self, text='')
        #Arranges everything
        gname_lab.grid(row=3, column=0)
        self.gname_ent.grid(row=3, column=1)
        sname_lab.grid(row=4, column=0)
        self.sname_ent.grid(row=4, column=1)
        dob_lab.grid(row=6, column=0)
        dod_lab.grid(row=8, column=0)
        gen_lab.grid(row=5, column=0)
        self.gen.grid(row=5, column=1)
        heading.grid(row = 0, column = 0)
        subheading.grid(row = 1, column = 0)
        top.grid(row = 2, column = 0)
        bottom.grid(row = 3, column = 0)
        self.submit.grid(row = 4, column = 0)
        self.error.grid(row = 7, column = 0)

    #Function for using the data entered by the user
    def collect_details(self):
        #There is an error that occurs if the user quickly clicks the submit button in 'Search' mode.
        #It causes the timeline to morph into a growing mass of blue and red.
        #This is prevented by preventing the user from pressing the button while the function is running.
        if self.view_type == 'Search':
            self.submit.config(state='disabled')
        # info = [gname,sname,gender,dob,dod,notes,dom,dodiv]
        info = []
        # Extracts and appends given names, surname and gender to info
        info.append(self.gname_ent.get())
        info.append(self.sname_ent.get())
        info.append(self.def_gen.get())
        #If not in 'Search' mode, validate DOB and fill in any gaps in the date with "[Unknown]"
        #(Ensures that everything entered is an integer)
        if self.view_type != "Search":
            # Assemble dob
            bday = self.bday.get()
            bmonth = self.def_b_month.get()
            byear = self.byear.get()
            dob = vali_date(bday,bmonth,byear)
            #Do the same for the DOD
            dday = self.dday.get()
            dmonth = self.def_d_month.get()
            dyear = self.dyear.get()
            dod = vali_date(dday,dmonth,dyear)
            #Checks that the dates are valids
            if dob == None or dod == None:
                # Returns an error if days and years are not numerical
                self.error.configure(text="Error: Days and Years must be numerical.")
                return False
            #Adds them both to info
            info.extend([dob,dod])
            # Extracts and appends notes to info
            notes = self.notes_ent.get()
            info.append(notes)
        #If the view is in 'Search' mode,
        else:
            #Validate the ranges for birth years and death years
            #(Ensure that all inputs are integers and that the start is less than the end
            start_b = self.start_b_year.get()
            end_b = self.end_b_year.get()
            if start_b != "" or end_b != "":
                if start_b.isdigit() == True and end_b.isdigit() == True:
                    start_b, end_b = int(start_b), int(end_b)
                    if start_b < end_b:
                        info.append([start_b, end_b])
                    else:
                        self.error.configure(text="'From' must be lesser than 'to'.")
                        return False
                else:
                    self.error.configure(text="Error: Days and Years must be numerical.")
                    return False
            else:
                info.append("")
            start_d = self.start_d_year.get()
            end_d = self.end_d_year.get()
            if start_d != "" or end_d != "":
                if start_d.isdigit() == True and end_d.isdigit() == True:
                    start_d, end_d = int(start_d), int(end_d)
                    if start_d < end_d:
                        info.append([start_d, end_d])
                    else:
                        self.error.configure(text="'From' must be lesser than 'to'.")
                        return False
                else:
                    self.error.configure(text="Error: Days and Years must be numerical.")
                    return False
            else:
                info.append("")
        #If in 'Create' mode,
        if self.view_type == "Create":
            # Creates a new member
            self.member = Member(focus_tree, *info)
            # Informs user of success
            messagebox.showinfo("Success!", "You have successfully created a member.")
            #Asks user about the parents of the member
            self.set_parent()
        #If in 'Edit' mode,
        elif self.view_type == "Edit":
            # Updates the info for the current member
            self.member.update_member(info)
            # Informs user of success
            messagebox.showinfo("Success!", "You have successfully updated this member's details.")
        #If in 'Search' mode,
        else:
            global shown
            found = []
            #Array of attributes to search for
            #(There was an issue with searching using keywords in the 'notes' section, so that has been omitted.)
            atts = ['given_names', 'surname', 'gender', 'dob', 'dod']
            #Goes through all the members in the timeline and sees if they match the entered criteria
            for display in shown:
                #Converts the display to a dictionary for ease of use
                member = display.__dict__
                #Variable to hold whether the member matches the search criteria or not (assumes that they do)
                valid = True
                #If the data was entered and data entered doesn't match the member's data,
                if info[0] not in member[atts[0]] and info[0] != '':
                    #State that member does not match the search criteria
                    valid = False
                #(Does this for all attributes)
                if info[1] != member[atts[1]] and info[1] != '':
                    valid = False
                if info[2] != member[atts[2]] and info[2] != 'Either':
                    valid = False
                if member[atts[3]] != '[Unknown]' and info[3] != '':
                    bYear = int((member[atts[3]].split(" "))[2])
                    if bYear < info[3][0] or bYear > info[3][1]:
                        valid = False
                if member[atts[4]] != '[Unknown]' and info[4] != '':
                    dYear = int((member[atts[4]].split(" "))[2])
                    if dYear < info[4][0] or dYear > info[4][1]:
                        valid = False
                #If the member matches the search criteria,
                if valid == True:
                    #Append display (not the dictionary) to 'found'
                    found.append(display)
            #Sets the timeline's array of found members to its own array of found members
            #(Essentially, it's returning what it's found)
            self.master.master.found = found
        #If in 'Search' mode,
        if self.view_type == 'Search':
            #Allows the user to press the button again
            self.submit.config(state='normal')

    #Produces a 'Set Parent' view
    def set_parent(self):
        global loaded_frames, back
        back.config(state = 'disabled')
        loaded_frames[-1].pack_forget()
        frame = SetParents(window, self.member)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
        back.config(state = 'normal')

    #Produces a 'Set Spouse' view
    def set_spouse(self):
        global loaded_frames, back
        back.config(state = 'disabled')
        loaded_frames[-1].pack_forget()
        frame = SetSpouse(window, self.member)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
        back.config(state = 'normal')

#Mini-mini-view for allowing the user to navigate through found members in a timeline
#(Is a part of the 'Search Navigation' view)
class Navigation(tkinter.Frame):

    global width, height

    def __init__(self, master):
        super().__init__(master, height=(height // 3), width=width //3)
        #Label for holding the amount of members that have been found
        self.number_label = tkinter.Label(self, text='')
        #Has options for going right and going left
        go_left = tkinter.Button(self, text="<-", command=lambda: self.scroll(right=False))
        go_right = tkinter.Button(self, text="->", command=self.scroll)
        text = tkinter.Label(self, text="results found.")
        #Arranges everything
        go_left.grid(column=0, row=1)
        go_right.grid(column=3, row=1)
        self.number_label.grid(column=1, row=0)
        text.grid(column=2, row=0)

    #Function for jumping to a selected member
    def scroll(self, right=True):
        #Shortcut for accessing the tree view
        root = self.master.master
        #tree view.at = the index of the current found member being viewed
        #If the user is going right,
        if right == True:
            #If it is possible to travel further right in the 'found' array,
            if root.at != (len(root.found) - 1):
                #Go right by one
                root.at += 1
            #If not,
            else:
                #Go back to the beginning
                root.at = 0
        #If the user is going left,
        else:
            #If it is impossible to go further left,
            if root.at == 0:
                #Go to the end
                root.at = len(root.found) - 1
            #If not,
            else:
                #Go left by one
                root.at -= 1
        #Uses the timeline's function for jumping to a member to jump to the member at that index
        #(It takes in a member as its parameter, so member is found via index and converted from a display to a member
        root.timeline.scroll_to((root.found[root.at]).as_member)

#Mini-view for navigating through a tree based on searching for members with certain characteristics
#(Part of the tree view.)
class SearchNavigation(tkinter.Frame):

    global width, height

    def __init__(self, master):
        super().__init__(master, height=height, width=width // 3)
        #Uses a 'Get Details' view in search mode for this
        self.search = GetDetails(self, 'Search', height_local=(height // 3 * 2))
        #Uses implements above view as a widget
        self.navigation = Navigation(self)
        #Button for switching between search navigation and relative navigation
        change_nav = tkinter.Button(self, text="Change Navigation Type", command=self.master.change_navigation)
        #Arranges everything
        change_nav.pack()
        self.search.pack()
        self.navigation.pack()

#Mini-view for navigating through a tree based on jumping from a member to their direct relatives (parents, spouses, children)
#(Part of the tree view.)
class RelativeNavigation(tkinter.Frame):

    global height, width

    def __init__(self, master):
        super().__init__(master, height=height, width=(width // 3))
        #Button for switching between search navigation and relative navigation
        change_nav = tkinter.Button(self, text="Change Navigation Type", command=self.master.change_navigation)
        #Stores 'source' of relatives. (The member that the relatives are related to.)
        self.source = self.master.focus_member
        #(Cosmetics)
        heading = tkinter.Label(self, text=(self.source.full_name + "' s Relatives"))
        subheading = tkinter.Label(self, text="Select the index of the member you wish to go to in the drop-down menu.")
        labs = [(tkinter.Label(self, text="Parents:")), (tkinter.Label(self, text="Spouses:")), (tkinter.Label(self, text="Children:"))]
        #For showing information about relatives, including their indexes
        parent_box = ScrollBox(self)
        spouse_box = ScrollBox(self)
        children_box = ScrollBox(self)
        #Button for jumping to a chosen member
        go_to_butt = tkinter.Button(self, text="Go To", command=self.go_to)
        #For showing errors
        self.error = tkinter.Label(self)
        #Holds parents and spouses together (as their indexes)
        parents = []
        spouses = []
        if self.source.father != None:
            parents.append(self.source.father)
        if self.source.mother != None:
            parents.append(self.source.mother)
        for data in self.source.spouses:
            spouses.append(data[0])
        #Display information about relatives
        parent_box.show_multiple(parents)
        spouse_box.show_multiple(spouses)
        children_box.show_multiple(self.source.children)
        #Collects IDs of all direct relatives
        all_ids = parents + spouses + self.source.children
        #Sorts them
        all_ids.sort()
        #Arranges widgets
        change_nav.pack()
        heading.pack()
        subheading.pack()
        labs[0].pack()
        parent_box.pack()
        labs[1].pack()
        spouse_box.pack()
        labs[2].pack()
        children_box.pack()
        #If there are relatives to choose from,
        if all_ids != []:
            #Create a drop-down menu with all the IDs
            #The user chooses which member to jump to based on their ID
            self.index = tkinter.StringVar(self, all_ids[0])
            index_dd = tkinter.OptionMenu(self, self.index, *all_ids)
            index_dd.pack()
            go_to_butt.pack()
        #If not,
        else:
            #Display an error
            self.error.config(text="This person has no relatives.")
        self.error.pack()

    #Function for jumping to a relative
    def go_to(self):
        global treedb, to_load, shown_ids
        #Gets the index of the member to jump to
        index = self.index.get()
        #If a relative has been chosen,
        if index != '':
            #Make the index an integer
            index = int(index)
            #Find the member in question
            member = to_load[shown_ids.index(index)]
            #Uses the timeline's function for jumping to a member to jump to the member
            self.master.timeline.scroll_to(member)
        #If not,
        else:
            #Return an error
            self.error.config(text="Please select an index to travel to.")

#Mini-view for displaying a family tree timeline
#(Part of the tree view.)
class Timeline(tkinter.Frame):

    global width, height

    def __init__(self, master):
        super().__init__(master, height=height // 2, width=width // 3)
        # Create a canvas to draw the timeline onto
        # Add a canvas to the canvas-frame (cframe)
        self.canvas = tkinter.Canvas(self, width=800 // 3, height=500, scrollregion=(0, 0, 800, 800))
        # Add a vertical scroll bar to the cframe
        y = tkinter.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        # Add a horizontal scroll bar to the cframe
        x = tkinter.Scrollbar(self, orient='horizontal', command=self.canvas.xview)
        # Configure the canvas so that it can be navigated using the two scroll bars
        self.canvas.config(yscrollcommand=y.set, xscrollcommand=x.set)
        # Create a Turtle Screen over the canvas
        self.screen = turtle.TurtleScreen(self.canvas)
        # Create a "Raw Turtle" to use as a pen on the Turtle Screen
        self.pen = Pen(self.screen)
        # When the Turtle Screen is right-clicked, run the function 'clickBox', which will receive values for x and y.
        self.screen.onclick(self.click_box, btn=1)
        # Arranges everything
        self.canvas.pack()
        x.pack(side='bottom', fill='x')
        y.pack(side='right', fill='y')

    # Generates the tree
    def draw_all(self):
        global treedb, to_load, shown, shown_ids, shown_coords, found_coords, d
        members = []
        ids_and_years = []
        just_ids = []
        to_load = []
        shown = []
        shown_ids = []
        shown_coords = []
        found_coords = []
        # Turn the IDs in the tree into members
        for ID in treedb[self.master.tree]:
            members.append(copy.deepcopy(treedb['Members'][ID]))
        # Collect the IDs and birth years (where possible) of the members in the tree
        for member in members:
            if member.birth_year != None:
                ids_and_years.append([member.ID, int(member.birth_year)])
            else:
                just_ids.append(member.ID)
        # Sort the IDs and birth years by birth years, oldest to youngest
        ids_and_years.sort(key=lambda x: x[1])
        # Load all the members to load into the timeline into to_load
        for couple in ids_and_years:
            to_load.append(copy.deepcopy(treedb['Members'][couple[0]]))
            shown_ids.append(couple[0])
        # Separate members with birth years and those without
        final = len(to_load)
        for ID in just_ids:
            to_load.append(copy.deepcopy(treedb['Members'][ID]))
            shown_ids.append(ID)
        # Draw first line
        self.pen.move_to(0, 0)
        self.pen.draw_line(end=final)
        # Put pens back, lower.
        self.pen.up()
        self.pen.move_to(0, -d * 2)
        self.pen.write("Unknown Birth Years:", font=("Arial", 12, "normal"))
        self.pen.move_to(0, -d * 4)
        self.pen.down()
        # Draws second line
        if len(shown) != len(to_load):
            self.pen.draw_line(start=final)
        try:
            # Get oldest year and youngest year
            oldest = ids_and_years[0][1]
            youngest = ids_and_years[-1][1]
            # Draw dates
            self.pen.up()
            self.pen.move_to(shown[0].x, d * 2)
            self.pen.write(oldest, font=("Arial", 12, "normal"))
            self.pen.move_to(shown[final - 1].x, d * 2)
            self.pen.write(youngest, font=("Arial", 12, "normal"))
            self.pen.up()
        except:
            # If there are not dates to get, do nothing
            pass
        # Set the scroll-region of the canvas to the size of the timeline so that it all may be navigated
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        # Determines the length of the timeline/the longest timeline based on the difference in x-coordinates of the starting and ending members
        if ids_and_years == [] or just_ids == []:
            self.length = shown[-1].x - shown[0].x + 5
        else:
            line_a_length = shown[final - 1].x - shown[0].x
            line_b_length = shown[-1].x - shown[final].x
            if line_a_length >= line_b_length:
                self.length = line_a_length + 5
            else:
                self.length = line_b_length + 5

    #Function for highlighting found members
    def find_all(self):
        global found_coords
        pen = self.pen
        #If some members have already been highlighted,
        if found_coords != []:
            #Go through each highlighted member and unhighlight them
            for pair in found_coords:
                pen.up()
                pen.goto(pair[0], pair[1])
                pen.down()
                pen.draw_rectangle('blue')
            #Clear array for the coordinates of found members
            found_coords = []
        #Highlights all the members that have been found in red
        for display in self.master.found:
            pen.up()
            pen.goto(display.x, display.y)
            pen.down()
            pen.draw_rectangle('red')
            found_coords.append([display.x, display.y])

    #Function that allows the user to click on a member box to select it
    #(Runs in response to the user clicking on the canvas)
    def click_box(self, x, y):
        global shown, show_coords, d
        #Converts x,y to the nearest top left corner of a square
        x -= (x % d)
        y -= (y % d)
        #If the x,y coordinates point to a member,
        if [x, y] in shown_coords:
            #Retrieve the member
            member = to_load[shown_coords.index([x, y])]
            #Set the member as the focus of the tree view
            self.master.focus_member = member

    #Jumps to a certain member in the timeline
    def scroll_to(self, member):
        global to_load, shown
        #If the ID of the member the user wishes to jump to is not in the current family tree,
        if member.ID not in treedb[self.master.tree]:
            #Return an error
            messagebox.showinfo("Failure!", "The member you are looking for is not in this tree.")
            #(This error can be caused by importing a member without importing its relatives and trying to do a relative search.)
        #Otherwise,
        else:
            #Locate the member in shown based on its position in to_load
            display = shown[to_load.index(member)]
            #Calculate a fraction with the x-coordinate of the display as the numerator and the length of the timeline as the denominator.
            fraction = display.x / self.length
            #Moves the horizontal scroll bar of the canvas to show the part of the canvas indicated to by that fraction
            #(tkinter.Canvas.xview_moveto takes in a fraction of the scroll-region as its parameter)
            self.canvas.xview_moveto(fraction)
            #Change the focus of the tree view to the member that has just been jumped to
            self.master.focus_member = member

#Mini-view for displaying information about the current member of focus
#(Part of the tree view.)
class MemberInfo(tkinter.Frame):

    global height, width

    def __init__(self, master):
        super().__init__(master, height=height, width=width // 3)
        title = tkinter.Label(self, text="Member Information")
        #Scroll Box for member information
        self.information = ScrollBox(self, state='disabled', height=(500 // 50), width=(800 // 30))
        #Scroll Box for basic information about the member's spouses (name, date of marriage/divorce)
        self.spouse_information = ScrollBox(self, state='disabled', height=(500 // 50), width=(800 // 30))
        spouse_lab = tkinter.Label(self, text="Spouses:")
        #Arranges everything
        title.pack()
        self.information.pack()
        spouse_lab.pack()
        self.spouse_information.pack()

    #Shows the information about the current member of focus
    def show_info(self):
        member = self.master.focus_member
        #Shows the info about the member
        self.information.show_member_info(member)
        #Shows the info about the member's spouses
        self.spouse_information.show_multiple(member.spouses, is_spouse=True)

#View for displaying and interacting with a family tree
class TreeView(tkinter.Frame):

    global height, width

    def __init__(self, master, tree):
        super().__init__(master, height=height, width=width)
        #Holds the name of the family tree that is being displayed
        self.tree = tree
        #Consists of: A timeline, a navigation widget and a member info widget
        self.timeline = Timeline(self)
        self.member_info = MemberInfo(self)
        self.search_navigation = SearchNavigation(self)
        #('[name]_beneath's are used whenever certain events must occur when the value of [name] is changed)
        #Holds array of found members
        self.found_beneath = []
        #Holds current member of focus
        self.focus_member_beneath = None
        #Holds current index of 'found' array
        self.at = 0
        #By default, the using navigates using search navigation
        self.navigation_type = 'search'
        #Draws all members onto the timeline
        self.timeline.draw_all()
        #Arranges everything
        self.search_navigation.grid(row=0, column=0)
        self.timeline.grid(row=0, column=1)
        self.member_info.grid(row=0, column=2)

    #Function for getting the focus member
    def get_mem(self):
        return self.focus_member_beneath

    #Function for setting the focus member
    def set_mem(self, value):
        #Changes value for focus member
        self.focus_member_beneath = value
        #Shows the information about the focus member
        self.member_info.show_info()

    #Function for getting the 'found' array
    def get_found(self):
        return self.found_beneath

    #Function for setting the 'found' array
    def set_found(self, value):
        #Changes the value for 'found'
        self.found_beneath = value
        #Makes the member of focus the first member in 'found'
        self.focus_member = self.found[0]
        #Highlights all found members
        self.timeline.find_all()
        #Resets the current index of 'found' array
        self.at = 0
        #Changes the label on the navigation mini-mini-view to show the number of found members
        self.search_navigation.navigation.number_label.configure(text=str(len(self.found_beneath)))

    #Converts them into properties
    found = property(get_found, set_found)
    focus_member = property(get_mem, set_mem)

    #Function for changing the navigation type
    def change_navigation(self):
        #If using search navigation,
        if self.navigation_type == 'search':
            #If there is a member currently in focus,
            if self.focus_member != None:
                #Switch to relative navigation
                #(Create and load a relative navigation mini-view and unload the search navigation mini-view)
                self.navigation_type = 'relative'
                self.search_navigation.grid_forget()
                self.relative_navigation = RelativeNavigation(self)
                self.relative_navigation.grid(column=0, row=0)
            #If not,
            else:
                #Display an error
                messagebox.showerror("Cannot Do That", "You must select a member in order to see its relatives.")
        #If not,
        else:
            #Switch to search navigation, like above
            self.navigation_type = 'search'
            self.relative_navigation.grid_forget()
            self.search_navigation.grid(column=0, row=0)

#View for selecting a member from a tree view
class SelectMember(tkinter.Frame):

    global width, height

    def __init__(self, master, set_func, tree):
        super().__init__(master, width = width, height = height)
        #Holds name of function for setting the variable that holds the member the user is selecting
        self.set_func = set_func
        #Creates a tree view
        self.tree_view = TreeView(self, tree)
        #(Widgets)
        heading = tkinter.Label(self, text="Select Member From Tree")
        select_butt = tkinter.Button(self, text="Select", command=self.select_member)
        self.error = tkinter.Label(self)
        #Arranges everything
        heading.pack()
        self.tree_view.pack()
        select_butt.pack()
        self.error.pack()

    #Function for 'returning' selected member
    def select_member(self):
        global loaded_frames
        #If no member has been selected,
        if self.tree_view.focus_member == None:
            #Return an error
            self.error.configure(text="Please select a member.")
        #Otherwise,
        else:
            #Generate the line of code that needs to be run
            #(Take the view before this one, runs the setting function on it with a parameter called 'member'
            code = "loaded_frames[-2]." + self.set_func + "(member)"
            #Creates an anonymous function that takes in a parameter 'member' and runs the above code
            #('eval(x)' converts string 'x' into runnable code)
            x = lambda member: eval(code)
            #Runs the anonymous function, using the current member of focus in place of 'member'
            x(self.tree_view.focus_member)
            #Goes back to the previous view where one can use the selected member
            go_back(1)

#View for finding a relationship between two members
class GetRel(tkinter.Frame):

    global treedb, focus_tree, height, width

    def __init__(self, master):
        super().__init__(master, height=height, width=width)
        #Stores first member
        self.person_a_beneath = None
        #Stores second member
        self.person_b_beneath = None
        #(Cosmetics)
        heading = tkinter.Label(self, text = "Find Relationship")
        subheading = tkinter.Label(self, text = "(Relationship will be given in terms of what B is to A.)")
        a_lab = tkinter.Label(self, text = "Person A")
        self.a_scrollbox = ScrollBox(self, state = "disabled")
        #Button for selecting first member
        a_change = tkinter.Button(self, text = "Change", command = lambda : find_from_tree("set_a"))
        b_lab = tkinter.Label(self, text = "Person B")
        self.b_scrollbox = ScrollBox(self, state = "disabled")
        #Button for selecting second member
        b_change = tkinter.Button(self, text = "Change", command = lambda : find_from_tree("set_b"))
        submit = tkinter.Button(self, text = "Find Relationship", command = self.find_rels)
        self.error = tkinter.Label(self, text = '')
        self.rel_string = tkinter.Label(self, text = '')
        #Arranges everything
        heading.grid(row = 0, column = 1)
        subheading.grid(row = 1, column = 1)
        a_lab.grid(row = 2, column = 0)
        self.a_scrollbox.grid(row = 3, column = 0)
        a_change.grid(row = 4, column = 0)
        b_lab.grid(row = 2, column = 2)
        self.b_scrollbox.grid(row = 3, column = 2)
        b_change.grid(row = 4, column = 2)
        submit.grid(row = 5, column = 1)
        self.error.grid(row = 6, column = 1)
        self.rel_string.grid(row = 8, column = 1)

    #Function for getting first member
    def get_a(self):
        return self.person_a_beneath

    #Function for setting first member
    def set_a(self, value):
        self.person_a_beneath = value
        self.a_scrollbox.show_member_info(value)

    #Function for getting second member
    def get_b(self):
        return self.person_b_beneath

    #Function for setting second member
    def set_b(self, value):
        self.person_b_beneath = value
        self.b_scrollbox.show_member_info(value)

    #Converts to properties
    person_a = property(get_a, set_a)
    person_b = property(get_b, set_b)

    #Function for finding the relationship between the two selected members
    def find_rels(self):
        global halt_all
        #Checks if two members have been selected
        if self.person_a == None or self.person_b == None:
            self.error.configure(text = "You must select two persons to find a relationship between.")
        #Checks if the same member has been selected twice
        elif self.person_a.ID == self.person_b.ID:
            self.error.configure(text = "That's the same person!")
        #If all is well,
        else:
            #Gets rid of any error message
            self.error.configure(text = '')
            #Sets ups, downs and sides to 0
            self.ups = 0
            self.downs = 0
            self.sides = 0
            #Holds all checked members
            self.checked = []
            #Allows search threads to run
            halt_all = False
            #Runs a search thread from the first member to find the second
            first_thread = SearchThread(self.person_a, self.person_b.ID)
            first_thread.start()
            first_thread.join()
            #Uses values of ups, downs and sides to define a relationship
            relationship = self.define_rels()
            #Displays that relationship to the user
            self.rel_string.configure(text = relationship)

    #Function for defining a relationship between members
    def define_rels(self):
        #Holds placeholder words and their gendered equivalents
        conversions = {"Parent" : ['Father', 'Mother'], "Child" : ['Son','Daughter'], "Nibling" : ['Nephew', 'Niece'], "Sibling" : ['Brother', 'Sister'], "P_sib" : ['Uncle', 'Aunt']}
        #If second member cannot be found or is related to the first via a spouse,
        if self.sides != 0 or self.ups == 0 and self.downs == 0:
            #There is no blood relation
            return "No blood relation."
        #(Quicker to write)
        ups = self.ups
        downs = self.downs
        #If there are no downs,
        if downs == 0:
            #If there is one up,
            if ups == 1:
                #Then B is A's parent
                relationship = "Parent"
            #If there is more than one,
            else:
                #Then B is A's grandparent to a degree of greatness
                relationship = ("Great " * (ups - 2)) + "GrandParent"
        #If there are no ups,
        elif ups == 0:
            #If there is one down,
            if downs == 1:
                #Then B is A's child
                relationship = "Child"
            #If there is more than one,
            else:
                #Then B is A's grandchild to a degree of greatness
                relationship = ("Great " * (downs - 2)) + "GrandChild"
        #If there is one up and at least two downs,
        elif ups == 1 and downs >= 2:
            #Then B is A's nibling to some degree of greatness
            relationship = ("Great " * (downs - 2)) + "Nibling"
        #If there is one down and at least two ups,
        elif downs == 1 and ups >= 2:
            #Then B is A's aunt/uncle to some degree of greatness
            #(Couldn't find a general term for uncles and aunts, so just used 'P_sib" (parent-sibling).)
            relationship = ("Great " * (ups - 2)) + "P_sib"
        #If there are at least two downs and ups,
        elif ups >= 2 and downs >= 2:
            #Then B is A's...
            if ups == downs:
                #[something] cousin
                relationship = num2words(ups - 1, ordinal = True) + " Cousin"
            elif downs > ups:
                #[something] cousin to a degree of removal
                relationship = num2words(ups - 1, ordinal = True) + " Cousin " + self.times(downs - ups) + " Removed"
            else:
                #[something] cousin to a degree of removal
                relationship = num2words(downs - 1, ordinal = True) + " Cousin Once Removed"
        #If none of the above is applicable,
        else:
            #Then B is A's sibling
            relationship = "Sibling"
        #Locates placeholder word in relationship and replaces it with the correct gendered version
        for key in list(conversions.keys()):
            if key in relationship:
                if self.person_b.gender == 'Male':
                    relationship = relationship.replace(key, conversions[key][0])
                else:
                    relationship = relationship.replace(key, conversions[key][1])
        #Returns a sentence explaining A and B's relationship
        return self.person_b.full_name + " is " + self.person_a.full_name + "'s " + relationship + "."

    #Converts numbers to these word things
    def times(self, removed):
        #Special words:
        words = ['Once','Twice','Thrice']
        #If there is a special word for this degree of removal,
        try:
            #Return special word
            return words[removed-1]
        #If not,
        except:
            #Return [number] + 'times', capitalises each word
            return num2words(removed - 1)[0].upper() + " Times"


#View for setting a member's parents
class SetParents(tkinter.Frame):

    global width, height

    def __init__(self, master, member):
        global treedb
        super().__init__(master, height=height, width=width)
        self.subject = member 
        #Shows information about parents
        self.father_box = ScrollBox(self)
        self.mother_box = ScrollBox(self)
        #If the member in question already has a father,
        if member.father != None:
            #Retrieve the member's current father and display his information
            self.father_beneath = treedb["Members"][member.father]
            self.father_box.show_member_info(self.father_beneath)
        #If not,
        else:
            self.father_beneath = None
        #If the member in question already has a mother,
        if member.mother != None:
            #Retrieve the member's current mother and display her information
            self.mother_beneath = treedb["Members"][member.mother]
            self.mother_box.show_member_info(self.mother_beneath)
        #If not,
        else:
            self.mother_beneath = None
        #(Cosmetics)
        heading = tkinter.Label(self, text = "Who are " + member.full_name + "'s parents?")
        father_lab = tkinter.Label(self, text = "Father:")
        change_father = tkinter.Button(self, text = "Change", command = lambda : find_from_tree("set_father"))
        clear_father = tkinter.Button(self, text = "Clear", command = self.clear_father)
        mother_lab = tkinter.Label(self, text = "Mother:")
        change_mother = tkinter.Button(self, text = "Change", command = lambda : find_from_tree("set_mother"))
        clear_mother = tkinter.Button(self, text = "Clear", command = self.clear_mother)
        configure_butt = tkinter.Button(self, text = "Configure", command = self.configure_parents)
        self.error = tkinter.Label(self)
        #Arranges everything
        heading.grid(row = 0, column = 1)
        father_lab.grid(row = 1, column = 0)
        self.father_box.grid(row = 2, column = 0)
        change_father.grid(row = 3, column = 0)
        clear_father.grid(row = 4, column = 0)
        mother_lab.grid(row = 1, column = 2)
        self.mother_box.grid(row = 2, column = 2)
        change_mother.grid(row = 3, column = 2)
        clear_mother.grid(row = 4, column = 2)
        configure_butt.grid(row = 5, column = 1)
        self.error.grid(row = 6, column = 1)

    #(Same as with all other _beneath attributes)
    def get_father(self):
        return self.father_beneath

    def set_father(self, value):
        self.father_beneath = value
        self.father_box.show_member_info(value)

    def get_mother(self):
        return self.mother_beneath

    def set_mother(self, value):
        self.mother_beneath = value
        self.mother_box.show_member_info(value)

    father = property(get_father, set_father)
    mother = property(get_mother, set_mother)

    #Resets value of father to None
    def clear_father(self):
        self.father = None

    #Resets value of mother to None
    def clear_mother(self):
        self.mother = None

    #Sets the selected members as the member's parents
    def configure_parents(self):
        #Checks if selected members are the correct genders before continuing
        if self.father != None:
            if self.father.gender != 'Male':
                self.error.configure(text = "The father cannot be female.")
                return False
        if self.mother != None:
            if self.mother.gender != 'Female':
                self.error.configure(text = "The mother cannot be male.")
                return False
        #Uses add_parent method of Member class to add parents
        self.subject.add_parent(self.father, parent = 'father')
        self.subject.add_parent(self.mother, parent = 'mother')
        #Informs user of success
        messagebox.showinfo("Success!","Parents successfully configured.")

#View for setting a member's spouse
class SetSpouse(tkinter.Frame):

    global width, height

    def __init__(self, master, member):
        super().__init__(master, height=height, width=width)
        self.subject = member
        self.spouse_beneath = None
        #Holds whether the member selected is already a spouse of the member one is configuring the spouses for
        self.present = False
        months = ['[Unknown]', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        heading = tkinter.Label(self, text = "Configure Spouse for " + member.full_name)
        spouse_lab = tkinter.Label(self)
        self.spouse_info = ScrollBox(self)
        change_spouse = tkinter.Button(self, text = "Change", command  = lambda : find_from_tree("set_spouse"))
        #Button for removing a pre-existing spouse. Starts off disabled, but is enabled when the user selects a pre-existing spouse.
        self.remove_butt = tkinter.Button(self, text = "Remove", command = self.remove, state = 'disabled')
        dom_lab = tkinter.Label(self, text = "Date of Marriage")
        self.mday = tkinter.Entry(self)
        self.mmonth = tkinter.StringVar(self, '[Unknown]')
        mmonths_dd = tkinter.OptionMenu(self, self.mmonth, *months)
        self.myear = tkinter.Entry(self)
        dodiv_lab = tkinter.Label(self, text = "Date of Divorce")
        self.divday = tkinter.Entry(self)
        self.divmonth = tkinter.StringVar(self, '[Unknown]')
        divmonths_dd = tkinter.OptionMenu(self, self.divmonth, *months)
        self.divyear = tkinter.Entry(self)
        self.confirm_butt = tkinter.Button(self, text = "Confirm", command = self.confirm, state = 'normal')
        self.error = tkinter.Label(self)
        #Arranges everything
        heading.grid(row = 0, column = 1)
        spouse_lab.grid(row = 1, column = 1)
        self.spouse_info.grid(row = 2, column = 1)
        change_spouse.grid(row = 3, column = 1)
        self.remove_butt.grid(row = 4, column = 1)
        dom_lab.grid(row = 5, column = 1)
        self.mday.grid(row = 6, column = 0)
        mmonths_dd.grid(row = 6, column = 1)
        self.myear.grid(row = 6, column = 2)
        dodiv_lab.grid(row = 7, column = 1)
        self.divday.grid(row = 8, column = 0)
        divmonths_dd.grid(row = 8, column = 1)
        self.divyear.grid(row = 8, column = 2)
        self.confirm_butt.grid(row = 9, column = 1)
        self.error.grid(row = 10, column = 1)

    #Same as with all _beneath attributes
    def get_spouse(self):
        return self.spouse_beneath

    def set_spouse(self, value):
        #Prevents spam-clicking the 'confirm' button
        self.confirm_butt.config(state = 'disabled')
        #Checks if the chosen member and the member in question are the same
        if value != None:
            if value.ID == self.subject.ID:
                #If so, return an error
                self.error.configure(text = "One cannot marry oneself.")
                return False
        #Retrieves chosen member
        self.spouse_beneath = value
        #Shows info about chosen member
        self.spouse_info.show_member_info(value)
        #If the value of spouse_beneath has been reset,
        if value == None:
            #Prevent the user from being able to remove the spouse
            self.remove_butt.config(state = 'disabled')
            #Clear all dates
            self.mday.delete(0, 'end')
            self.mmonth.set('[Unknown]')
            self.myear.delete(0, 'end')
            self.divday.delete(0, 'end')
            self.divmonth.set('[Unknown]')
            self.divyear.delete(0, 'end')
        else:
            #Checks if chosen member is a pre-existing spouse or not
            present, pos = self.subject.locate_spouse(value.ID)
            #If so,
            if present == True:
                #Collect the data about the spouse
                data = self.subject.spouses[pos]
                #If the previous chosen member was not a pre-existing spouse,
                if self.present != True:
                    #Enable the remove button
                    self.remove_butt.config(state = 'normal')
                #Fill in the dates for the spouse
                dom = data[1].split(" ")
                if dom[0] != "[Unknown]":
                    self.mday.insert(0,dom[0])
                self.mmonth.set(dom[1])
                if dom[2] != "[Unknown]":
                    self.myear.insert(0,dom[2])
                dodiv = data[2].split(" ")
                if dodiv[0] != "[Unknown]":
                    self.divday.insert(0,dodiv[0])
                self.divmonth.set(dodiv[1])
                if dodiv[2] != "[Unknown]":
                    self.divyear.insert(0,dodiv[2])
            #If not,
            else:
                #If the previous chosen member was a pre-existing spouse,
                if self.present == True:
                    #Disable the remove button
                    self.remove_butt.config(state = 'disabled')
            self.present = present
        #Allows 'confirm' button to be clicked again
        self.confirm_butt.config(state = 'normal')

    #Convert to a property
    spouse = property(get_spouse, set_spouse)

    def confirm(self):
        #If no member has been selected,
        if self.spouse == None:
            self.error.config(text = "Please select a member.")
            return False
        #Validates dates (as with DOB and DOD in 'Get Details' views)
        mday = self.mday.get()
        mmonth = self.mmonth.get()
        myear = self.myear.get()
        divday = self.divday.get()
        divmonth = self.divmonth.get()
        divyear = self.divyear.get()
        dom = vali_date(mday,mmonth,myear)
        dodiv = vali_date(divday,divmonth,divyear)
        if dom == None or dodiv == None:
            # Returns an error if days and years are not numerical
            self.error.configure(text="Error: Days and Years must be numerical.")
            return False
        #Uses the configure_spouse method of the Member class
        self.subject.configure_spouse(self.spouse, dom, dodiv)
        #Informs user of success
        messagebox.showinfo("Success!", "Spouse successfully configured.")

    #Removes a spouse
    def remove(self):
        #Uses the remove_spouse method of the Member class
        self.subject.remove_spouse(self.spouse)
        self.spouse = None
        #Informs user of success
        messagebox.showinfo("Success!", "Spouse removed successfully.")

#Functions
#---Non-Button Functions---
#Saves the database
def save_db():
    #Saves to JSON file
    global treedb, db_copy
    try:
        convert_members()
        datafile = open('family_tree.json','w+')
        json.dump(db_copy,datafile)
        datafile.close()
        time.sleep(0.5)
        datafile = open('back-up.json','w+')
        json.dump(db_copy,datafile)
        datafile.close()
    except:
        messagebox.showerror("Could not save","Sorry, but the program ran into an error whilst trying to save your program. A previous version of your save will be recovered.")
        os.remove('family_tree.json')
        os.rename('back-up.json','family_tree.json')
        datafile = open('family_tree.json')
        treedb = json.load(datafile)
        datafile.close()

#Exits the program
def stop():
    save_db()
    #Exits program
    os._exit(0)

#Validates dates
def vali_date(day,month,year):
    #Holds date as a string
    date = ''
    #If day of date is not known,
    if day == '':
        #Set it as unknown
        date += "[Unknown] "
    #If day is known,
    else:
        #If the day is not numerical,
        if day.isdigit() == False:
            #Then date is invalid
            return None
        #Otherwise,
        else:
            #Add day to date
            date += day + ' '
    #Add month to date, no validation needed here
    date += month
    #Do the same for the year
    if year == '':
        date += " [Unknown]"
    else:
        if year.isdigit() == False:
            return None
        else:
            date += ' ' + year
    #Return the full date
    return date

#Converts the members in and out of Member objects
#This is so that they can be loaded into the JSON database and used out of the JSON database
def convert_members():
    global treedb, db_copy
    to_convert = copy.deepcopy(treedb["Members"])
    converted = []
    #Checks if object is a dict
    if len(to_convert) == 0:
        return False
    if str(type(to_convert[0])) != "<class 'dict'>":
        #Takes a copy of the database
        db_copy = copy.deepcopy(treedb)
        #Converts into dictionaries
        for member in to_convert:
            converted.append(member.__dict__)
        db_copy["Members"] = converted
    else:
        #Converts into Members
        for dictionary in to_convert:
            m = dictionary
            converted.append(Member('none', m["given_names"], m['surname'], m['gender'], m['dob'],m['dod'],m['notes'], ID = m['ID'], children = m['children'], spouses = m['spouses'], father = m['father'], mother = m['mother']))
        treedb["Members"] = converted

#---Button Functions---
#+++Navigating Views+++
#Navigates backwards to previous views
def go_back(num):
    global loaded_frames, do_save
    #If the user is on a Configure Tree view,
    if str(type(loaded_frames[-1])) == "<class '__main__.ConfigureTree'>":
        #Go back by two
        for i in range(2):
            loaded_frames[-1].pack_forget()
            loaded_frames.pop()
        #And reload the Action Select view
        show_acts()
    #If not,
    else:
        #If there are frames to navigate backwards through,
        if str(type(loaded_frames[-1])) == "<class '__main__.ConfigureMembers'>":
            do_save = True
        if len(loaded_frames) != 1:
            #For the past [num] views, unload all views and remove them from loaded_frames
            #(Unless if the view is the 'User Select' view, A.K.A. the first view in loaded_frames)
            for i in range(num):
                if loaded_frames[-1] != loaded_frames[0]:
                    loaded_frames[-1].pack_forget()
                    loaded_frames.pop()
            loaded_frames[-1].pack(fill='both',expand=1)
        #If not,
        else:
            #Return an error
            messagebox.showinfo("Error","There are no pages before this.")

#Creates a 'user-select' view
def select_user():
    global loaded_frames
    frame = UserSelect(window)
    loaded_frames.append(frame)
    frame.pack(fill='both',expand=1)

#Produces a "Get Password" view
def get_pass():
    global loaded_frames, admin, back
    back.config(state = 'disabled')
    if admin == True:
        show_acts()
    else:
        loaded_frames[-1].pack_forget()
        frame = EnterPassword(window)
        loaded_frames.append(frame)
        frame.pack(fill='both',expand=1)
    back.config(state = 'normal')

#Creates an 'Action Select' view
def show_acts(normal = False):
    global loaded_frames, treedb, back
    back.config(state = 'disabled')
    if normal == True:
        global admin
        admin = False
    loaded_frames[-1].pack_forget()
    #If there are trees available to work on,
    if list(treedb.keys()) != ["Members"]:
        #Produce an 'Action Select' view
        frame = ActionSelect(window)
    #If not,
    else:
        #Produce a 'Create Tree' view
        frame = CreateTree(window)
    loaded_frames.append(frame)
    frame.pack(fill='both',expand=1)
    back.config(state = 'normal')

#Creates a 'Get Details' view
def get_deets(view_type, member = None):
    global loaded_frames, back
    back.config(state = 'disabled')
    loaded_frames[-1].pack_forget()
    frame = GetDetails(window, view_type, member = member)
    loaded_frames.append(frame)
    frame.pack(fill='both',expand=1)
    back.config(state = 'normal')

#Creates a 'Make Tree' view
def make_tree():
    global loaded_frames, back
    back.config(state = 'disabled')
    loaded_frames[-1].pack_forget()
    frame = CreateTree(window)
    loaded_frames.append(frame)
    frame.pack(fill='both',expand=1)
    back.config(state = 'normal')

#Produces a 'Find From Tree' view
def find_from_tree(set_func, tree = None):
    global loaded_frames, focus_tree, loaded_tree, back
    back.config(state = 'disabled')
    loaded_frames[-1].pack_forget()
    if loaded_tree != None:
        loaded_tree.set_func = set_func
        frame = loaded_tree
    else:
        #By default, allows the user to select a member from the current tree of focus
        if tree == None:
            frame = SelectMember(window, set_func, focus_tree)
        #Can be used to show other trees, though
        else:
            frame = SelectMember(window, set_func, tree)
        if do_save == True:
            loaded_tree = frame
    loaded_frames.append(frame)
    frame.pack(fill='both', expand=1)
    back.config(state = 'normal')

#+++Other Actions+++
#Changes tree of focus (the tree that actions will be performed on)
def change_tree_focus(event):
    global loaded_frames, focus_tree, loaded_tree
    focus_tree = loaded_frames[-1].tree.get()
    loaded_tree = None

#Variables
#Holds all loaded frames
loaded_frames = []
#Holds current tree
focus_tree = ''
#Tree variables
d = 10
shown = []
shown_ids = []
shown_coords = []
to_load = []
found_coords = []
#Variables for storing a loaded tree
loaded_tree = None
do_save = True
#Holds admin password
admin_pass = ""
#Holds admin status
admin = False
halt_all = False
#Checks if JSON file exists or not and loads necessary database into 'treedb'
if os.path.exists('family_tree.json') == False:
    treedb = {}
    treedb['Members'] = []
else:
    datafile = open('family_tree.json')
    treedb = json.load(datafile)
    datafile.close()
    datafile = open('back-up.json','w+')
    json.dump(treedb,datafile)
    datafile.close()
    convert_members()
#Variable for holding a copy of the database
db_copy = {}
#Creates tkinter window
window = tkinter.Tk()
#Make fullscreen
#(Get dimensions of user's screen)
width = window.winfo_screenwidth()
height = window.winfo_screenheight()
#(Set dimensions as the dimensions of the window)
window.geometry(str(width)+"x"+str(height))
window.title("Family Tree Program")
#If the user decides to press the red 'X' button on the top of the window, ensure that program is still exited correctly
window.protocol("WM_DELETE_WINDOW", stop)
#Adds a 'menu bar'
global_actions = tkinter.Frame(window)
#Adds back button to menu bar
back = tkinter.Button(global_actions,text="<- Previous Page", command=lambda:go_back(1))
#Adds exit button to menu bar
leave = tkinter.Button(global_actions,text="Exit", command=stop)
#Arranges everything
back.pack(side='left')
leave.pack(side='right')
global_actions.pack(fill='x',side='top')
security = SaveThread()
security.start()

#Sequence
#Opens with a 'user select' frame
select_user()
window.mainloop()

