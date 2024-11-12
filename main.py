import sys, os

from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox

import mysql.connector

from PIL import Image, ImageTk
initialWindow = Tk()
initialWindow.title("EasySQL")



'''
Root Variables
'''

screenHeight = initialWindow.winfo_screenheight()
screenWidth = initialWindow.winfo_screenwidth()



def startFunction(initialWindow, startButton: Button):
    '''
    First Function Ran.
    Changes the main menu to the login menu
    delWidgets: Widgets in previous menu to be deleted
    '''
    startButton.destroy()

    subHeading=Label(initialWindow, text="Enter SQL connection details", font=('Terminal', round(screenHeight*screenWidth*0.000018113)))
    subHeading.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.2)

    hostLabel = Label(initialWindow, text="Localhost:", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD))
    hostLabel.place(anchor=E, relx=0.5, rely=0.3)
    hostEntry = Entry(initialWindow, width = round((screenWidth/4) * 0.0625), font=('Arial', round(screenHeight*screenWidth*0.0000113), font.BOLD), highlightcolor='black', highlightthickness=1, highlightbackground='black')
    hostEntry.insert(0, 'localhost')
    hostEntry.place(anchor=W, relx=0.5, rely = 0.3)

    portLabel = Label(initialWindow, text="Port:", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD))
    portLabel.place(anchor=E, relx=0.5, rely=0.4)
    portEntry = Entry(initialWindow, width = round((screenWidth/4) * 0.0625), font=('Arial', round(screenHeight*screenWidth*0.0000113), font.BOLD), highlightcolor='black', highlightthickness=1, highlightbackground='black')
    portEntry.insert(0, '3306')
    portEntry.place(anchor=W, relx=0.5, rely = 0.4)

    usernameLabel = Label(initialWindow, text="Username:", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD))
    usernameLabel.place(anchor=E, relx=0.5, rely=0.5)
    usernameEntry = Entry(initialWindow, width = round((screenWidth/4) * 0.0625), font=('Arial', round(screenHeight*screenWidth*0.0000113), font.BOLD), highlightcolor='black', highlightthickness=1, highlightbackground='black')
    usernameEntry.insert(0, 'root')
    usernameEntry.place(anchor=W, relx=0.5, rely = 0.5)

    passwordLabel = Label(initialWindow, text="Password:", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD))
    passwordLabel.place(anchor=E, relx=0.5, rely=0.6)
    passwordEntry = Entry(initialWindow, width = round((screenWidth/4) * 0.0625), font=('Arial', round(screenHeight*screenWidth*0.0000113), font.BOLD), highlightcolor='black', highlightthickness=1, highlightbackground='black', show='*')
    passwordEntry.insert(0, '')
    passwordEntry.place(anchor=W, relx=0.5, rely = 0.6)    

    errorLabel = Label(initialWindow, text="Invalid Connection Details", fg='red', font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD))

    def resetDetails():
        hostEntry.delete(0,END)
        portEntry.delete(0,END)
        usernameEntry.delete(0,END)
        passwordEntry.delete(0,END)

        hostEntry.insert(0,'localhost')
        portEntry.insert(0,'3306')
        usernameEntry.insert(0,'root')
        passwordEntry.insert(0,'')

    def submitDetails():

        host = hostEntry.get()
        port = portEntry.get()
        username = usernameEntry.get()
        password = passwordEntry.get()

        try:
            connection = mysql.connector.connect(host=host, port=int(port), user=username, password=password)
        except:
            errorLabel.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.8)
            initialWindow.bell()
            return 0


        #Destroy all widgets of the current window before moving onto the next. SubHeading is not destroyed as it is used in the next window
        hostLabel.destroy()
        hostEntry.destroy()
        portLabel.destroy()
        portEntry.destroy()
        usernameLabel.destroy()
        usernameEntry.destroy()
        passwordLabel.destroy()
        passwordEntry.destroy()
        submitButton.destroy()
        resetButton.destroy()
        errorLabel.destroy()
        
        
        
        dbConnectionMenu(initialWindow, subHeading, connection, host, port, username, password)
                     

    submitButton = Button(initialWindow, text="Submit", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = submitDetails)
    submitButton.place(anchor = E, relx=0.49, rely= 0.7)
    resetButton = Button(initialWindow, text="Reset Details", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = resetDetails)
    resetButton.place(anchor = W, relx=0.51, rely= 0.7)


def dbConnectionMenu(initialWindow, subHeading, connection, host, port, username, password):
    '''
    Database connection menu
    '''

    delMode = False

    def createDb():

        def createDbSubmit(name):
            cursor = connection.cursor(buffered=True)
            cursor.execute(f"CREATE DATABASE {name};")
            cursor.close()
            connection.commit()

            nameEntry.destroy()
            submitButton.destroy()
            dbConnectionMenu(initialWindow, subHeading, connection, host, port, username, password)

        nonlocal selectorCanvas, selectorScrollbar, buttonFrame, createDbButton, deleteDbButton, allButtons

        selectorCanvas.destroy()
        selectorScrollbar.destroy()
        buttonFrame.destroy()
        createDbButton.destroy()
        deleteDbButton.destroy()
        for buttons in allButtons: buttons.destroy()

        subHeading.config(text="Enter new database name")
        nameEntry = Entry(initialWindow, width = round((screenWidth/4) * 0.0625), font=('Arial', round(screenHeight*screenWidth*0.0000113), font.BOLD), highlightcolor='black', highlightthickness=1, highlightbackground='black')
        nameEntry.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.5)

        submitButton = Button(initialWindow, text="Submit", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = lambda: createDbSubmit(nameEntry.get()))
        submitButton.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.6)
        pass

    def deleteDb(db):

        nonlocal allButtons

        cursor = connection.cursor(buffered=True)
        cursor.execute(f"DROP DATABASE {db['text']};")
        cursor.close()
        connection.commit()

        allButtons.remove(db)
        db.pack_forget()
        db.destroy()

        pass

    def delModeToggle(allButtons):
        nonlocal delMode
        delMode = not delMode
        if delMode == True: 
            for dbButton in allButtons: dbButton['fg']="red"                
        else:
            for dbButton in allButtons: dbButton['fg'] = "black"
                

    def connectDB(db):
        nonlocal connection, selectorCanvas, selectorScrollbar, buttonFrame, createDbButton, deleteDbButton, allButtons
        connection.close()
        connection = mysql.connector.connect(host=host, port=int(port), user=username, password=password, database=db['text'])
        
        selectorCanvas.destroy()
        selectorScrollbar.destroy()
        buttonFrame.destroy()
        createDbButton.destroy()
        deleteDbButton.destroy()
        for buttons in allButtons: buttons.destroy()

        queryMenu(initialWindow, subHeading, connection, host, port, username, password, db)

        


    subHeading.config(text="Choose Database")

    selectorCanvas = Canvas(initialWindow)
    selectorCanvas.place(anchor=N, relx=0.5, rely=0.3, relwidth=0.5, relheight=0.5)
    selectorScrollbar = Scrollbar(initialWindow, orient="vertical", command=selectorCanvas.yview)
    selectorScrollbar.place(anchor=W, relx=0.75, rely=0.55, relheight=0.5)
    selectorCanvas.configure(yscrollcommand=selectorScrollbar.set)
    

    buttonFrame = Frame(selectorCanvas)
    selectorCanvas.create_window((0,0), window=buttonFrame, anchor="nw")

    
    cursor = connection.cursor(buffered=True)
    cursor.execute("SHOW DATABASES;")

    allButtons = []
    for db in cursor:
        dbButton = Button(buttonFrame, text=db[0], borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W)
        dbButton.configure(command= lambda dbButton = dbButton: connectDB(dbButton) if delMode == False else deleteDb(dbButton))
        dbButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
        dbButton.grid(row=len(allButtons), column=0, pady=0.1)
        allButtons.append(dbButton)
    
    
    buttonFrame.update_idletasks()
    selectorCanvas.config(scrollregion=selectorCanvas.bbox("all"))
    cursor.close()

    createDbButton = Button(initialWindow, text="Create New Database", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = createDb)
    createDbButton.place(anchor = W, relx=0.25, rely= 0.85)
    deleteDbButton = Button(initialWindow, text="Delete Database", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command= lambda: delModeToggle(allButtons))
    deleteDbButton.place(anchor = E, relx=0.75, rely= 0.85)


def queryMenu(initialWindow, subHeading, connection, host, port, username, password, db):
    subHeading.config(text="Select SQL Query")


'''
Start Window
'''
titleHeading=Label(initialWindow, text="EasySQL", fg='green', font=('Terminal', round(screenHeight*screenWidth*0.000044113), font.BOLD))
titleHeading.place(anchor = CENTER, x=round(screenWidth/2), y=screenHeight*0.0663)

# Get Image Path [Changes depending on whether running py file or as compiled executable]
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    imagePath = sys._MEIPASS
else: imagePath = os.path.dirname(__file__)

startImg = ImageTk.PhotoImage(file = os.path.join(imagePath, 'start.png'))
startButton = Button(initialWindow, image= startImg, borderwidth=0, command = lambda: startFunction(initialWindow, startButton))
startButton.place(relx = 0.5, rely = 0.5, anchor = CENTER)

initialWindow.geometry(f"{screenWidth}x{screenHeight}")
initialWindow.mainloop()