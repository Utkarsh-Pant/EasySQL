import sys, os, re, datetime

from tkinter import *
from tkinter import font
from tkinter import ttk
from tkinter import messagebox

import mysql.connector
import pyperclip
from PIL import Image, ImageTk


initialWindow = Tk()
initialWindow.title("EasySQL")



'''
Root Variables
'''

screenHeight = initialWindow.winfo_screenheight()
screenWidth = initialWindow.winfo_screenwidth()


def notValidIdentifier(text):
    return text[-1] == " " or re.fullmatch(r"[0-9a-zA-Z$_\s.]+", text) == None

def notTypeValid(type, text):
    if type=="int":
        return re.fullmatch(r"[0-9]+", text) == None
    elif type=="float":
        return re.fullmatch(r"\d+", text) == None and re.fullmatch(r"\d+\.\d+", text) == None
    elif type=="date":
        try: datetime.date.fromisoformat(text)
        except ValueError: return True
        return False
    elif type=="char":
        return len(text) != 0
    elif type=="varchar(1024)":
        return False
    else: raise ValueError("Not supported type")
    
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
        try:
            connection = mysql.connector.connect(host=hostEntry.get(), port=int(portEntry.get()), user=usernameEntry.get(), password=passwordEntry.get())
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
        
        
        
        dbConnectionMenu(initialWindow, subHeading, connection)
                     

    submitButton = Button(initialWindow, text="Submit", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = submitDetails)
    submitButton.place(anchor = E, relx=0.49, rely= 0.7)
    resetButton = Button(initialWindow, text="Reset Details", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = resetDetails)
    resetButton.place(anchor = W, relx=0.51, rely= 0.7)


def dbConnectionMenu(initialWindow, subHeading, connection):
    '''
    Database connection menu
    '''

    delMode = False

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
                messagebox.showerror("Invalid Database Name", "Database name can only contain letters and numbers")
                initialWindow.bell()
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
        nonlocal delMode
        delMode = not delMode
        if delMode == True: 
            for dbButton in allButtons: dbButton['fg']="red"                
        else:
            for dbButton in allButtons: dbButton['fg'] = "black"
                

    def connectDB(db):

        '''
        Function called when a database button is clicked.
        Makes the connection to the database and changes the menu to the query menu; deleting current elements
        '''

        nonlocal connection, selectorCanvas, selectorScrollbar, buttonFrame, createDbButton, deleteDbButton, allButtons
        connection.close()
        connection._database = db['text']
        selectorCanvas.destroy()
        selectorScrollbar.destroy()
        buttonFrame.destroy()
        createDbButton.destroy()
        deleteDbButton.destroy()
        for buttons in allButtons: buttons.destroy()

        queryMenu(initialWindow, subHeading, connection)

        


    subHeading.config(text="Choose Database")

    selectorCanvas = Canvas(initialWindow)
    selectorCanvas.place(anchor=N, relx=0.5, rely=0.3, relwidth=0.5, relheight=0.5)
    selectorScrollbar = Scrollbar(initialWindow, orient="vertical", command=selectorCanvas.yview)
    selectorScrollbar.place(anchor=W, relx=0.75, rely=0.55, relheight=0.5)
    selectorCanvas.configure(yscrollcommand=selectorScrollbar.set)
    

    buttonFrame = Frame(selectorCanvas)
    selectorCanvas.create_window((0,0), window=buttonFrame, anchor="nw")

    
    cursor = connection.cursor(buffered=True)
    query = "SHOW DATABASES;"
    cursor.execute(query)
    pyperclip.copy(query)

    allButtons = []
    for db in cursor:
        dbButton = Button(buttonFrame, text=db[0], borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
        dbButton.configure(command= lambda dbButton = dbButton: connectDB(dbButton) if delMode == False else deleteDb(dbButton))
        dbButton.grid(row=len(allButtons), column=0, pady=0.1)
        allButtons.append(dbButton)
    
    
    buttonFrame.update_idletasks()
    selectorCanvas.config(scrollregion=selectorCanvas.bbox("all"))
    cursor.close()

    createDbButton = Button(initialWindow, text="Create New Database", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = createDb)
    createDbButton.place(anchor = W, relx=0.25, rely= 0.85)
    deleteDbButton = Button(initialWindow, text="Delete Database", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command= lambda: delModeToggle(allButtons))
    deleteDbButton.place(anchor = E, relx=0.75, rely= 0.85)


def queryMenu(initialWindow, subHeading, connection):
    subHeading.config(text="Select SQL Query")

    selectorCanvas = Canvas(initialWindow)
    selectorCanvas.place(anchor=N, relx=0.5, rely=0.3, relwidth=0.5, relheight=0.5)
    selectorScrollbar = Scrollbar(initialWindow, orient="vertical", command=selectorCanvas.yview)
    selectorScrollbar.place(anchor=W, relx=0.75, rely=0.55, relheight=0.5)
    selectorCanvas.configure(yscrollcommand=selectorScrollbar.set)
    

    buttonFrame = Frame(selectorCanvas)
    selectorCanvas.create_window((0,0), window=buttonFrame, anchor="nw")

    supportedQueries = {"Create Table": lambda: createTableMenu(connection), "Insert Data": insertDataMenu, "Select Data": selectDataMenu, "Update Data": updateDataMenu, "Delete Data": deleteDataMenu, "Drop Table": dropTableMenu, "Show Tables": showTablesMenu}    
    i = 0
    for key,value in supportedQueries.items():
        qButton = Button(buttonFrame, text=key, borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
        qButton.configure(command= value)
        qButton.grid(row=i, column=0, pady=0.1)
        i+=1

    buttonFrame.update_idletasks()
    selectorCanvas.config(scrollregion=selectorCanvas.bbox("all"))


def createTableMenu(connection,tableMenu: Tk = None, columnData: list[list[str]] = []):

    connection = mysql.connector.connect(host=connection._host, port=connection._port, user=connection._user, password=connection._password, database=connection._database)

    def addTable():
        nonlocal tableNameEntry, columnData, connection
        if len(tableNameEntry.get()) == 0:
            messagebox.showerror("Error", "Table name is required")
            return 0
        if notValidIdentifier(tableNameEntry.get()):
            messagebox.showerror("Error", "Invalid Table Name")
            return 0
        if len(columnData) == 0:
            messagebox.showerror("Error", "Atleast 1 Column Needed")
            return 0
        
        query = f"CREATE TABLE {tableNameEntry.get()}("
        for column in columnData:
            if column[1][3][0] and column[1][0] == "varchar(1024)": column[1][3][1] = '`'+column[1][3][1]+'`'
            query+= f"{column[0]} {column[1][0]} "
            query += "NOT NULL " * (column[1][1])
            query += "UNIQUE " * (column[1][2])
            query += f"DEFAULT \'{column[1][3][1]}\'" * column[1][3][0]
            query += "PRIMARY KEY" * (column[1][4])
            query += ","
        
        query = query[:-1] + ");"
        print(query)
        cursor = connection.cursor(buffered=True)
        cursor.execute(query)
        cursor.close()
        connection.commit()
        pyperclip.copy(query)

        messagebox.showinfo("Table Created", "Table Created Successfully")
        return 0

    def addColumnMenu():
        def columnAdd():
            nonlocal tableMenu, columnData, temporaryElements, tableNameEntry, nullToggle, uniqueToggle, defToggle, defEntry, dataTypeComboBox, primaryToggle
            
            if uniqueToggle.get() == 1 and defToggle.get() == 1:
                messagebox.showerror("Error", "Column Cannot Be Unique and Have Default Value")
                return 0

            if len(tableNameEntry.get()) == 0:
                messagebox.showerror("Error", "Column Name is required")
                return 0
            for columns in columnData:
                if columns[0] == tableNameEntry.get():
                    messagebox.showerror("Error", "Column Name Should Be Unique")
                    return 0
            if notValidIdentifier(tableNameEntry.get()):
                messagebox.showerror("Error", "Column Name Invalid")
                return 0
            if defToggle.get() and notTypeValid(dataTypeComboBox.get(), defEntry.get()):
                messagebox.showerror("Error", "Default value invalid")
                return 0
            columnData.append([tableNameEntry.get(), [dataTypeComboBox.get(), nullToggle.get(), uniqueToggle.get(), [defToggle.get(), defEntry.get()], primaryToggle.get()]])
            
            for element in temporaryElements: element.destroy()
            createTableMenu(connection, tableMenu, columnData)
        

        nonlocal tableMenu, tableNameLabel, tableNameEntry, displayTable, submitButton, addColButton

        displayTable.destroy()
        submitButton.destroy()

        temporaryElements = [tableNameLabel, tableNameEntry]

        tableNameLabel.config(text="Column Name:")

        nullToggle = IntVar(tableMenu)
        nullCheck = ttk.Checkbutton(tableMenu, variable = nullToggle)
        nullCheck.place(relx = 0.1, rely= 0.3, anchor = E)
        nullLabel = Label(tableMenu, text="No Null Values", font = ('Terminal', round(screenHeight*screenWidth*0.000009113), font.BOLD))
        nullLabel.place(relx=0.1, rely=0.3, anchor=W)
        temporaryElements.extend([nullCheck, nullLabel])

        uniqueToggle = IntVar(tableMenu)
        uniqueCheck = ttk.Checkbutton(tableMenu, variable = uniqueToggle)
        uniqueCheck.place(relx = 0.1, rely= 0.4, anchor = E)
        uniqueLabel = Label(tableMenu, text="Unique Values Only", font = ('Terminal', round(screenHeight*screenWidth*0.000009113), font.BOLD))
        uniqueLabel.place(relx=0.1, rely=0.4, anchor=W)
        temporaryElements.extend([uniqueCheck, uniqueLabel])

        defToggle = IntVar(tableMenu)
        defCheck = ttk.Checkbutton(tableMenu, variable = defToggle)
        defCheck.place(relx = 0.1, rely= 0.5, anchor = E)
        defEntry = Entry(tableMenu, font = ('Arial', round(screenHeight*screenWidth*0.000009113)))
        defEntry.insert(0, "Default Value (Optional)")
        defEntry.place(relx=0.1, rely=0.5, anchor=W)
        temporaryElements.extend([defCheck, defEntry])

        primaryToggle = IntVar(tableMenu)
        primaryCheck = ttk.Checkbutton(tableMenu, variable = primaryToggle)
        primaryCheck.place(relx = 0.1, rely= 0.6, anchor = E)
        primaryLabel = Label(tableMenu, text="Is Primary Key", font = ('Terminal', round(screenHeight*screenWidth*0.000009113), font.BOLD))
        primaryLabel.place(relx=0.1, rely=0.6, anchor=W)
        temporaryElements.extend([primaryCheck, primaryLabel])

        dataTypeLabel = Label(tableMenu, text="Data Type:", font=('Terminal', round(screenHeight*screenWidth*0.000009113), font.BOLD))
        dataTypeLabel.place(anchor = E, relx=0.5, rely=0.7)
        dataTypeComboBox =  ttk.Combobox(tableMenu, values = ("int","decimal","date","varchar(1024)","char"), state="readonly")
        dataTypeComboBox.place(anchor= W, relx=0.5, rely= 0.7)
        dataTypeComboBox.current(0)
        temporaryElements.extend([dataTypeLabel, dataTypeComboBox])

        addColButton.place_forget()
        addColButton.place(anchor=CENTER, relx=0.5, rely= 0.85)
        addColButton.config(command=columnAdd)
        temporaryElements.append(addColButton)

    
    if tableMenu is None:
        tableMenu = Tk()
        tableMenu.title("Create Table")
        tableMenu.geometry(f"{int(screenWidth/2)}x{int(screenHeight/2)}")
        tableMenu.protocol("WM_DELETE_WINDOW", lambda: [connection.close(), tableMenu.destroy()])

    tableNameLabel = Label(tableMenu, text="Table Name:", font=('Terminal', round(screenHeight*screenWidth*0.000009113), font.BOLD))
    tableNameLabel.place(anchor = W, relx=0.1, rely=0.15)
    tableNameEntry = Entry(tableMenu, width = round((screenWidth/4) * 0.0675), font=('Arial', round(screenHeight*screenWidth*0.0000113), font.BOLD), highlightcolor='black', highlightthickness=1, highlightbackground='black')
    tableNameEntry.place(anchor= E, relx=0.9, rely= 0.15)            

    displayTable = ttk.Treeview(tableMenu)
    displayTable['columns'] = ('Column', 'Attributes')
    displayTable.column("#0", minwidth=10)
    displayTable.column("Column", minwidth = 10)
    displayTable.column("Attributes", minwidth = 10)
    displayTable.heading("#0", text="S. No.", anchor = W)        
    displayTable.heading("Column", text="Column", anchor = W)
    displayTable.heading("Attributes", text="Attributes", anchor = W)        
    displayTable.place(anchor=N, relx = 0.5, rely = 0.3, width = screenWidth/2.5)

    print(columnData)
    for i in range(len(columnData)):
        
        attributeList = columnData[i][1]
        attributeStr = f"DataType: {attributeList[0]}"
        if attributeList[1] == 1: attributeStr += ", No Null Values"
        if attributeList[2] == 1: attributeStr += ", Unique Values Only"
        if attributeList[3][0] == 1: attributeStr += f", Default Value {attributeList[3][1]}"
        if attributeList[4] == 1: attributeStr += ", Primary Key"
        displayTable.insert(parent="", index='end', iid = i, text=i, values = (columnData[i][0], attributeStr))

    submitButton = Button(tableMenu, text="Submit", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command=addTable)
    submitButton.place(anchor=E, relx=0.8, rely= 0.85)

    addColButton = Button(tableMenu, text="Add Column", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command=addColumnMenu)
    addColButton.place(anchor=W, relx=0.2, rely= 0.85)



insertDataMenu = lambda: print("Insert Data")
selectDataMenu = lambda: print("Select Data")
updateDataMenu = lambda: print("Update Data")
deleteDataMenu = lambda: print("Delete Data")
dropTableMenu = lambda: print("Drop Table")
showTablesMenu = lambda: print("Show Tables")



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