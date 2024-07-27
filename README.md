CONTEXT : I made this program for my mother as part of my programming project coursework for my Computer Science A-Level course. I have uploaded it here for archival purposes, however, it was the second major program I had ever made and was much more ambitious than my first, so it has a lot of issues. There is no admin password, so just click "Submit" to sign in. If a normal user signs in before an admin user has created any trees/members, the program will break. If the UI disappears, resize the window. If the program refuses to save, which it will at times, there is no solution; you just have to restart the program and lose all your changes.

Instead of trying to untangle this mess, I am remaking this program from the ground up as an excuse to study industry-standard Python GUI modules. Old databases will not be compatible with this new version, but it should be considerably less broken.

Below is the original, unedited user guide.

-----
Family Tree Management Application User Guide
-----

Contents: 

	- Introduction £
	- How to Install ¢
	- How to Use $
	- Distribution and Updates €

(Use Ctrl + F and search for the character next to the section in order to skip to it.)

-----
£
-----

Hello and thank you for using the Family Tree Management Application! This program was developed as part of my A-level computer science coursework for my mother, but its purpose is to be shared around families to bring us closer together and help us to understand how we are all connected. It provides two main features for the average user: The ability to view all the members of a family tree in timeline form and the ability to decipher the (blood) relation between two members. For admin users, it allows you to do all of this, but also to create family trees, create members for family trees, import members form other family trees, and to edit the details of any member or family tree that has already been created. The reason why normal users do not have access to these features is to reduce the amount of individuals with the ability to modify the family tree so that, when changes are made, everyone associated with the change will be notified of it and no changes will be overwritten when trying to update the database. These features will work in harmony to digitalise the creation, editing and sharing of a family tree, as well as providing other useful features that sheets of paper would not.

This program was created in response to the issues that physical family trees create: They take up excessive amounts of paper, (which is bad for the environment,) they're quite immobile and hard to picture in their entirety, (thus making them hard to share), and they can get very messy, congested and confusing with all the new additions. A digital family tree has none of these problems, especially not the version in this program. You see, instead of using the traditional layout for a family tree - as it becomes more and more illegible and confusing as more members are added to it, so it is only really suitable for a few people. Instead, I decided to display family trees in the form of timelines. Initially, one might imagine that a timeline might be harder to navigate than the normal layout, and one would be correct, but I have taken this account and included several search and navigation features that allow you to find people and jump to their relatives with great ease.

-----
¢
-----

	FOR ALL OPERATING SYSTEMS:

1. Create a folder on your computer of any name.
2. Download the attachments of the email and move them into that folder. (Including this guide.)
3. (OPTIONAL) Create a shortcut for opening the file titled "Family Tree Program.py" and put it somewhere convenient (for ease of access).

	FOR WINDOWS:

4. Go to the Microsoft Store and download the Python app. (Should look like a blue snake and a yellow snake.)
5. Follow this guide to download "pip": https://pip.pypa.io/en/stable/installation/
6. Wait for pip to download. (This will not harm your computer.)
7. Once pip has downloaded, search for a program on your computer called "cmd", also known as the "Command Prompt".
8. Type in the following command: "pip install num2words" , and then press the "Enter" key.
9. Wait for "num2words" to finish downloading.

Now, all you have to do is double click the file "Family Tree Program.py" (or the shortcut you created) to run the program.

	FOR MAC:

4. Go to https://www.python.org/downloads/ and download the latest version of Python for Mac.
	Your Mac should have Python 2.7 already downloaded, but this version is out-of-date.
7. Follow this guide to download "pip": https://pip.pypa.io/en/stable/installation/
8. Wait for pip to download. (This will not harm your computer.) You only need to download this once, so, if you have already downloaded pip, you do not need to do this again.
6. Find the program called "Terminal" on your computer and open it.
7. Type in the following command: "python3 -m pip install num2words --user" , and then press the "Enter" key. (You must enter the exact text between the speech marks.)
9. Wait for "num2words" to finish downloading.

Now, you should have everything in place to actually run the program, but I have found no alternate way to do this other than by double clicking on the program and running it like you ran the "get-pip.py" file. Apologies for the inconvenience.

-----
$
-----

!!! IMPORTANT !!! : Before I can tell you how to use this program, I must first ask you to have patience. Some parts of this program can take a while to load, especially with larger/more family trees, but please trust that they will load eventually. If you are ever left with a white screen with just the menubar at the top, then it is still loading.

Run the specific application for your operating system (the .exe file for Windows or the .app file for Mac) [or something].

When you open up the program, you will be met by a screen asking you to select which kind of user you are. If you are a normal user or don't want to make any changes, click the button labelled "Normal User". If you are an admin user, click the button labelled "Admin". If you select "Admin", you will have to enter the admin password. There will also be a two buttons on either top corner of the screen. The button on the left will say "<- Previous Page" and it will allow you to navigate to the previous page. The button on the right will say "Exit" which will allow you to exit the program. You can also exit the program the normal way by pressing the red cross.

This program will communicate with you through pop-up windows and error messages lower down on the screen. Often, after performing an action, you will receive a pop-up window informing you that an action has been completed successfully. If you wish to then do something else, you will have to navigate backwards manually using the "<- Previous Page" button in the top left corner of the screen.

If you try to perform any actions whilst no trees have been created, you will be asked to create a tree on selecting a user. This tree will be empty after you create it, as will all other trees. You will need to create members to put in these trees in order for them to be useful.

After selecting a user, you will be brought to a page with the heading "Select an Action". Use the drop-down menu located underneath the "Configure Members" button to select a family tree to work with. The only action that can be performed without selecting a tree is "Configure Family Trees".

"Display a Family Tree" will display the family tree you have selected via the drop-down menu. (If there are no members in the tree you have selected, then it will show you an error - as it has nothing to display.) There will be three parts of this new screen:
	1. The search widget, located on the left. By default, this will allow you to search for members in the tree by certain attributes. Members that fit you search criteria will be highlighted in red. If you press the "Change Navigation Type" button, it will allow you to navigate the tree based on the relatives of the selected member. Press it again to return to searching by criteria.
	2. The timeline, located in the centre. This will show you the family tree in timeline form. Click on a box to get the information about the member it represents. Most of the time, it will be shown as two lines: One for members with known DOBs and another for members without known DOBs. If the tree you are viewing does not contain members in one of those categories, then only one line will be shown.
	3. Member Info, located on the right. This will show you all the information about the selected member, including all of their spouses and the dates associated with each spouse. (I.e. date of marriage and date of divorce.)

"Find a Relationship" will allow you to select two members from the tree using the "Change" buttons for Person A and Person B. In order to select a member from the tree, you will be shown a screen similar to that in "Display a Family Tree", except it will have an additional "Select" button lower down. All you have to do is click on a member in the timeline and press "Select" to select a member. After you have selected a Person A and a Person B, you can press the "Find Relationship" button to retrieve their (blood) relationship. In cases of incest, the program will only return one relationship.

"Configure Members" will allow you to create, import, edit and remove members.
	- "Create a Member" will allow you to fill in the details of a new member. You can fill in as little or as many details as you like. After pressing "Create", you will either be met with an error message or a pop-up saying that the creation was successful. If you get an error message, please read it and correct the error accordingly. If you don't, you will be asked about the members parents. You can either select these from the tree or leave them blank.
	- "Import a Member" will allow you to import a member from one tree to another. This is useful if there is overlap between trees. Simply select a tree from the drop-down menu (located underneath "Import from:") to import a member from, then select a member from that tree to import. To import the member, press the "Import" button. If all goes well, you will be met with a pop-up. If not, you will see an error message.
	- "Edit a Member" will allow you to select a member from the tree and edit all of their details. Here, you can also add spouses or configure parents. Press "Confirm Changes" to finalise any changes in basic details (e.g. Given Names), "Configure Spouses" to add spouses, remove spouses and edit the date of marriage and date of divorce for known spouses, and "Configure Parents" to configure parents.
	- "Remove a Member" will allow you to remove a member from a tree. Simply select a member and press the "Remove Member" button. You will be asked to confirm your decision - as this action is mostly irreversible. You could, of course, just import the member back into the tree, but if you have removed the member from all trees, then you will not be able to retrieve them using normal methods. If this occurs, you can contact me - as the member is not lost forever - but please try not to let this happen if you don't want it to happen.

"Configure Family Trees" will allow you to create, rename and delete family trees. Renaming a family tree will not affect any of its members, nor will deleting a family tree. However, if those members could only be found in that family tree, then you will need to contact me in order to retrieve them. (Again, please try to prevent this from happening if you don't want this to happen.)

That is the full extent of the functionality of this program. If you are still unsure about anything, contact me.

-----
€
-----

The purpose of this program is to be shared, so feel free to share it with anyone and everyone you know - just make sure to include all relevant files when sharing, such as this user guide. Apart from that, normal copyright law applies. 

You are not to edit, sell or take ownership of any part of this program. If you would like to change something, then please contact me.

As for updating the program and its databases, if a new version is released, just simply download the new version and delete the old one. This should not affect your trees. If you would like to update the database with a new one, simply just download the new database and delete the old one, but make sure that it is in the same folder as the program. If the old database contained content not found in the new database, then this will be lost. You cannot have more than one database at once.
