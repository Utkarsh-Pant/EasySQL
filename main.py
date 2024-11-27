import sys, os, re, datetime, threading
import customtkinter
from customtkinter import *
import mysql.connector
import pyperclip
import time



initialWindow = CTk()
initialWindow.title("EasySQL")


screenWidth = initialWindow.winfo_screenwidth()
screenHeight = initialWindow.winfo_screenheight()

bgColor = "#0d1117"
orangeColor = "#faa356"
grayColor = "#89929b"
blueColor = "#77bdfb"
purpleColor = "#cea5fb"
redColor = "#fa7970"
whiteColor = "#ecf2f8"
greenColor = "#7ce38b"
textFont = CTkFont(family="Helvetica", size=(screenWidth*screenHeight)//60000, weight="bold")

def notValidIdentifier(text):
    return len(text) == 0 or text[-1] == " " or re.fullmatch(r"[0-9a-zA-Z$_\s.]+", text) == None

def messageBox(type, title, message):
        
        messageBoxFont = CTkFont(family="Helvetica", size=(screenWidth*screenHeight)//100000, weight="bold")

        if type != "error":
            textColor = greenColor
        else: textColor = redColor
        messageBoxWindow = CTk()
        messageBoxWindow.title(title)
        messageBoxWindow.geometry(f"{screenWidth//5}x{screenHeight//5}")
        messageBoxWindow.config(bg=bgColor)
        
        messageContent = CTkTextbox(messageBoxWindow, font=messageBoxFont, fg_color=bgColor, text_color=textColor, wrap="word", scrollbar_button_color=orangeColor)
        messageContent.insert(1.0, message+"asjdflsdfsdlfksdlfksd"*100)
        messageContent.place(relx=0.5, rely=0.4, anchor=CENTER, relwidth=0.9, relheight=0.6)

        exitButton = CTkButton(
            messageBoxWindow, 
            text="OK", 
            font=messageBoxFont, 
            command = messageBoxWindow.destroy, 
            border_color= textColor, 
            border_width=2, 
            fg_color=bgColor, 
            hover=False
            )
        exitButton.place(relx=0.5, rely=0.8, anchor=CENTER, relwidth=0.2, relheight=0.15)

        messageBoxWindow.bell()
        messageBoxWindow.grab_set()
        messageBoxWindow.mainloop()
        messageBoxWindow.grab_release()


def typeAnimation(parentObj, textLabel, newText, timeTotal):
    if hasattr(parentObj, "callID"):
        parentObj.after_cancel(parentObj.callID)

    textLabel.configure(text="")
    timeTotal = timeTotal * 1000

    def animationLoop(i=0):
        try: #Fails if window is closed before animation is complete
            if i < len(newText):
                textLabel.configure(text=textLabel.cget("text") + newText[i])
                parentObj.callID = parentObj.after(int(timeTotal / len(newText)), animationLoop, i + 1)
        except: pass
    animationLoop()

     

def loginPage(initialWindow, appSubheading, appUnderline, startButton: CTkButton):
    '''
    First Function Ran.
    Changes the main menu to the login menu
    delWidgets: Widgets in previous menu to be deleted
    '''
    startButton.destroy()

    appSubheading.place_forget()
    appSubheading.place(relx=0.01, rely=0.04, anchor=NW)
    appSubheading.configure(text_color=orangeColor)
    appUnderline.place_forget()
    appUnderline.place(relx=0.01, rely=0.08, anchor=NW, relwidth=0.2, relheight=0.007)

    typeAnimation(initialWindow, appSubheading, "Enter SQL Connection Details...", 1)

    dataWidgets = ["Host: ", "Port: ", "Username: ", "Password: "]
    defaultValues = ['localhost', '3306', 'root', '']

    for i in range(len(dataWidgets)):
        # Create labels and input entries with default values like , Host: [localhost]

        dataLabel = CTkLabel(initialWindow, text=dataWidgets[i], font=textFont, fg_color=bgColor, text_color=purpleColor)
        dataLabel.place(relx=0.4, rely=0.3 + i*0.1, anchor=E)

        dataEntry = CTkEntry(initialWindow, font=textFont, fg_color=bgColor, border_color=whiteColor, border_width=2)
        dataEntry.insert(0,defaultValues[i])
        dataEntry.place(relx=0.4, rely = 0.3 + i*0.1, anchor=W, relwidth = 0.3)
        
        # Overwrite the label and entry to dataWidgets
        dataWidgets[i] = [dataLabel, dataEntry]

    dataWidgets[-1][-1].configure(show='*')  #Change password entry display to show stars
    
    errorLabel = CTkLabel(initialWindow, text="Invalid Connection Details", text_color=redColor, font=textFont, fg_color=bgColor)

    def resetDetails(): #self-explanatory :/
        for i in dataWidgets:
            i[1].delete(0, END)
            i[1].insert(0, defaultValues[dataWidgets.index(i)])

    def submitDetails():

        try:
            connection = mysql.connector.connect(host=dataWidgets[0][1].get(), port=int(dataWidgets[1][1].get()), user=dataWidgets[2][1].get(), password=dataWidgets[3][1].get())
        except:
            errorLabel.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.8)
            initialWindow.bell()
            return 0


        #Destroy all widgets of the current window before moving onto the next. SubHeading is not destroyed as it is used in the next window
        for i in dataWidgets:
            i[0].destroy()
            i[1].destroy()

        submitButton.destroy()
        resetButton.destroy()
        errorLabel.destroy()                
        
        dbConnectionMenu(initialWindow, appSubheading, connection)
                     

    submitButton = CTkButton(
        initialWindow, 
        text="Submit", 
        font=textFont, 
        command = submitDetails, 
        border_color= orangeColor, 
        border_width=2, 
        fg_color=bgColor, 
        hover=False
    )
    submitButton.place(anchor = E, relx=0.49, rely= 0.7)

    resetButton = CTkButton(
        initialWindow, 
        text="Reset Details", 
        font=textFont, 
        command = resetDetails, 
        border_color= orangeColor, 
        border_width=2, 
        fg_color=bgColor, 
        hover=False
    )
    resetButton.place(anchor = W, relx=0.51, rely= 0.7)
    
def dbConnectionMenu(initialWindow, subHeading, connection):
    '''
    Database connection menu
    '''

    delMode = False
    typeAnimation(initialWindow, subHeading, "Select A Database to work with...", 1)

    def createDb():

        '''
        Function called when create new database button is clicked
        Temporarily changes menu to a create database menu
        Then creates the database and changes back to the database connection menu
        '''

        def createDbSubmit(name):
            '''
            Actually creates the database after submit button is pressed
            Validates the input and creates the database
            Destroys the new elements, and recalls the dbConnectionMenu function
            '''

            
            if notValidIdentifier(name):
                messageBox("error", "Invalid Database Name", "Database name can only contain letters and numbers")
                return 0

            cursor = connection.cursor(buffered=True)
            query = f"CREATE DATABASE `{name}`;"
            cursor.execute(query)
            cursor.close()
            connection.commit()
            pyperclip.copy(query)

            nameEntry.destroy()
            submitButton.destroy()
            dbConnectionMenu(initialWindow, subHeading, connection)

        nonlocal buttonFrame, createDbButton, deleteDbButton, allButtons

        buttonFrame.destroy()
        createDbButton.destroy()
        deleteDbButton.destroy()

        for buttons in allButtons: buttons.destroy()

        typeAnimation(initialWindow, subHeading, "Enter New Database Name...", 1)

        nameEntry = CTkEntry(initialWindow, width = round((screenWidth/4) * 0.0625), font=textFont)
        nameEntry.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.5)

        submitButton = CTkButton(initialWindow, text="Submit", font=textFont, command = lambda: createDbSubmit(nameEntry.get()))
        submitButton.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.6)

    def deleteDb(db):
        '''
        Function called when a database button is clicked in delete mode
        Drops the database and deletes the button from the menu
        '''


        nonlocal allButtons

        cursor = connection.cursor(buffered=True)
        query = f"DROP DATABASE `{db['text']}`;"
        cursor.execute(query)
        cursor.close()
        connection.commit()
        pyperclip.copy(query)

        allButtons.remove(db)
        db.pack_forget()
        db.destroy()

        pass

    def delModeToggle(allButtons):
        '''
        Method called when swithcing between delete mode and normal mode
        Changes color of buttons and swaps value of delMode
        '''
        nonlocal delMode #Without nonlocal creates a local scope delMode ;0
        delMode = not delMode
        if delMode == True: 
            for dbButton in allButtons: dbButton.configure(text_color=redColor)               
        else:
            for dbButton in allButtons: dbButton.configure(text_color=whiteColor)

    def connectDB(db):

        '''
        Function called when a database button is clicked.
        Makes the connection to the database and changes the menu to the query menu; deleting current elements
        '''

        nonlocal connection, buttonFrame, createDbButton, deleteDbButton, allButtons
        connection.close()
        connection._database = db['text']
        buttonFrame.destroy()
        createDbButton.destroy()
        deleteDbButton.destroy()
        for buttons in allButtons: buttons.destroy()

        queryMenu(initialWindow, subHeading, connection)

    buttonFrame = CTkScrollableFrame(
        initialWindow,
        fg_color=bgColor, 
        border_color=orangeColor, 
        border_width=2, 
        corner_radius=10, 
        scrollbar_fg_color=orangeColor, 
        scrollbar_button_color=bgColor, 
        scrollbar_button_hover_color=bgColor
    )

    
    cursor = connection.cursor(buffered=True)
    query = "SHOW DATABASES;"
    cursor.execute(query)
    pyperclip.copy(query)

    allButtons = []
    for db in cursor:
        #Adding the buttons to the frame
        dbButton = CTkButton(
            buttonFrame, 
            text=db[0], 
            fg_color=bgColor,
            anchor=CENTER, 
            height=round(screenHeight*0.5*0.075),
            width=round(screenWidth*0.48),
            corner_radius=0,
            border_color=purpleColor,
            border_width=2,
            font=textFont,
            text_color=whiteColor,
            hover_color=bgColor
            )
        dbButton.configure(command= lambda dbButton = dbButton: connectDB(dbButton) if delMode == False else deleteDb(dbButton))
        dbButton.grid(row=len(allButtons), column=0, pady=10)
        allButtons.append(dbButton)
    
    buttonFrame.place(anchor=CENTER, x=round(screenWidth/2), y=round(screenHeight/2), relwidth=0.5, relheight=0.5)
    
    cursor.close()

    createDbButton = CTkButton(
        initialWindow, 
        text="Create New Database", 
        font=textFont, 
        command = createDb, 
        border_color= orangeColor, 
        border_width=2, 
        fg_color=bgColor, 
        hover=False
    )
    createDbButton.place(anchor = E, relx=0.49, rely= 0.8)

    deleteDbButton = CTkButton(
        initialWindow, 
        text="Delete Database", 
        font=textFont, 
        command = lambda: delModeToggle(allButtons), 
        border_color= orangeColor, 
        border_width=2, 
        fg_color=bgColor, 
        hover=False
    )
    deleteDbButton.place(anchor = W, relx=0.51, rely= 0.8)

def queryMenu(a,b,c): pass



appName = CTkButton(
    initialWindow, 
    text="EasySQL", 
    font=CTkFont(family="Impact", size=(screenWidth*screenHeight)//10000), 
    bg_color=bgColor, 
    text_color=orangeColor, 
    fg_color="transparent", 
    hover=False
)

appUnderline = CTkLabel(initialWindow, fg_color=grayColor, text="")
appSubheading = CTkLabel(initialWindow, text="Easy Execution. Easy life.", fg_color=bgColor, text_color=blueColor, font=textFont)

appName.place(relx=0.5, rely=0.4, anchor=CENTER, relheight = 0.6)
appUnderline.place(relx=0.5, rely=0.5, anchor=N, relwidth=0.4, relheight=0.01)
appSubheading.place(relx=0.5, rely=0.55, anchor=CENTER)

appName.configure(command = lambda: loginPage(initialWindow, appSubheading, appUnderline, appName))

initialWindow.config(bg=bgColor)
initialWindow.geometry(f"{screenWidth}x{screenHeight}+0+0")
initialWindow.mainloop()




