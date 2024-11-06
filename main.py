import pyperclip
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from tkinter.font import BOLD
import re
from PIL import Image, ImageTk
import os
import mysql.connector

window = Tk()

'''
ROOT VARIABLES
'''

screenHeight = window.winfo_screenheight()
screenWidth = window.winfo_screenwidth()
filePath = os.path.dirname(__file__) + "\\"
details = ['localhost', 'root','',None]


logOpened = False #Where login window is opened or not
activeWin = None #keeps track of current active window


'''
MAIN FUNCTIONS
'''
def is_number_regex(s):
    """ Returns True is string is a number[including floats]. """
    if re.fullmatch(r"\d+") and re.fullmatch(r"\d+\.\d+", s) is None:
        return False
    return True

'''
LOGIN WINDOW
'''
def start():
    global logOpened
    global mLogWindow

    if logOpened == True: 
        mLogWindow.bell()
        return 0

    loginWindow = Tk()

    mLogWindow = loginWindow
    logOpened = True

    loginWindow.protocol("WM_DELETE_WINDOW", lambda: closeAll([window, loginWindow]) if messagebox.askokcancel("Quit", "Do you want to quit?") else None)
    loginWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

    mainText = Label(loginWindow, text = "Enter SQL details")
    mainText.place(anchor=S, relx=0.5, rely=0.2)


    lHostLabel = Label(loginWindow, text="Localhost: ")
    lHostLabel.place(anchor=W, relx=0.1, rely=0.3)
    lHost = Entry(loginWindow, borderwidth=5, width = round((screenWidth/4) * 0.0625))
    lHost.insert(0, 'localhost')
    lHost.place(anchor=W, relx=0.3, rely = 0.3)

    usernameLabel = Label(loginWindow, text="Username: ")
    usernameLabel.place(anchor=W, relx = 0.1, rely=0.4)
    username = Entry(loginWindow, borderwidth=5, width = round((screenWidth/4) * 0.0625))
    username.insert(0,'root')
    username.place(anchor=W, relx = 0.3, rely=0.4)

    pwdLabel = Label(loginWindow, text="Password: ")
    pwdLabel.place(anchor=W, relx = 0.1, rely=0.5)
    pwd = Entry(loginWindow, borderwidth=5, width = round((screenWidth/4) * 0.0625))
    pwd.insert(0, '')
    pwd.place(anchor=W, relx = 0.3, rely=0.5)

    def resetDef():
        lHost.delete(0,END)
        username.delete(0,END)
        pwd.delete(0,END)

        
        lHost.insert(0,'localhost')
        username.insert(0,'root')
        pwd.insert(0,'')

    def loginSubmit():
        host = lHost.get()
        name = username.get()
        password = pwd.get()


        try:
            db = mysql.connector.connect(
                host = host,
                username = name,
                password = password
            )


        except Exception as e: 
            print(e)
            messagebox.showerror("INVALID DATA", "THE DATA ENTERED IS NOT WORKING. PLEASE MAKE SURE THE SQL SERVER IS INSTALLED PROPERLY AND ALL THE INPUTS ARE CORRECT")
            return False

        else:
            global details
            details = [host, name, password, None]
            startDBCon(db, host, name, password)
            return db

    submitButton = Button(loginWindow, text = "Submit", command = loginSubmit)
    defButton = Button(loginWindow, text="Reset to default", command = resetDef)
    submitButton.place(anchor=E, relx = 0.5, rely = 0.7)
    defButton.place(anchor=W, relx=0.5, rely = 0.7)

    loginWindow.mainloop()
    
    
def closeAll(i):
    for j in i: j.destroy()

'''
DATABASE SELECTION
'''

def startDBCon(db, host, username, password):

    def newDB():
        closeAll([dbWindow])
        createNewDB(db, host, username, password)

    def conDB(db, name):
        try:
            db.close()
            db = mysql.connector.connect(
                username = username,
                host = host,
                password = password,
                database = name
            )
            global details
            details[3] = name
        except Exception as e:
            print(e)
            messagebox.showerror("ERROR!", f"UNKOWN ERROR OCCURED! ERR CODE: DBC08\n{e}")
            return False
        
        else:
            closeAll([dbWindow])
            startQuery(db, username, host, password, name)
            return db

    def delModeToggle():
        nonlocal delMode
        if delMode:
            for i in allButtons: i['bg'] = "white"
        else: 
            for i in allButtons: i['bg'] = "red"
        delMode = not delMode

    def delDB(bton):
        print(f"DELETED: {bton['text']}")
        a = db.cursor(buffered=True)
        query = f"DROP DATABASE {bton['text']};"
        a.execute(query)
        a.close()
        try: pyperclip.copy(f"DELETED: {bton['text']}")
        except: pass
        allButtons.remove(bton)
        bton.pack_forget()
        bton.destroy()

    try:
        closeAll([mLogWindow, window])
    except: pass

    delMode = False
    dbWindow = Tk()
    dbWindow.title('EasySQL')
    dbWindow.geometry(f'{screenWidth}x{screenHeight}+0+0')
    lbl = Label(dbWindow, text="EasySQL", fg='green', font=('Helvetica', round(screenHeight*screenWidth*0.000024113), BOLD))
    lbl.place(anchor = CENTER, relx = 0.5, rely=0.0463)

    lbl2 = Label(dbWindow, text="SELECT A DATABASE", fg = 'green', font = ('Helvetica', round(screenHeight*screenWidth*0.00000803766), UNDERLINE),borderwidth=1)
    lbl2.place(anchor = CENTER, relx = 0.5, rely= 0.15)

    dbParentFrame = LabelFrame(dbWindow)
    dbParentFrame.place(anchor=N, relx = 0.5, rely= 0.2, relheight = 0.5, relwidth= 0.5)

    frameCanvas = Canvas(dbParentFrame, background="white")
    frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

    frameScrollbar = ttk.Scrollbar(dbParentFrame, orient="vertical", command=frameCanvas.yview)
    frameScrollbar.place(anchor = E, rely=0.5, relx=1, relheight = 1)

    frameCanvas.configure(yscrollcommand=frameScrollbar.set)
    frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))

    dbFrame = Frame(frameCanvas, background="white")
    frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)
    
    cursor = db.cursor(buffered=True)
    cursor.execute("SHOW DATABASES;")

    allButtons = []
    for i in cursor:
        t = Button(dbFrame, text=i[0], borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W)
        t.configure(command= lambda n=i[0], b=t: conDB(db, n) if delMode == False else delDB(b))
        t.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
        t.pack(fill="both", expand = YES)
        allButtons.append(t)
    
    cursor.close()
     
    delButton = Button(dbWindow, text="Delete DB", font = ("Helvetica",30,NORMAL), command = delModeToggle)
    delButton.place(anchor=CENTER, relx=0.5, rely=0.9, relheight=0.08, relwidth=0.15)

    createButton = Button(dbWindow, text="Create New", font = ("Helvetica", 30, NORMAL), command = newDB)
    createButton.place(anchor=CENTER, relx=0.5, rely = 0.8, relheight=0.08, relwidth = 0.15)    

    dbWindow.mainloop()

def createNewDB(db, host, username, password):
    createWindow = Tk()
    def end(db):
        closeAll([createWindow])
        db.close()
        db = mysql.connector.connect(
            username = username,
            host = host,
            password = password
        )
        startDBCon(db, host, username, password)
        
    def create_new(name):
        a = db.cursor(buffered=True)
        a.execute(f"CREATE DATABASE {name}")
        try: pyperclip.copy(f"CREATE DATABASE {name}")
        except: pass
        a.close()
        end(db)

    createWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

    nameLabel = Label(createWindow, text="DB Name: ")
    nameLabel.place(anchor=W, relx = 0.1, rely=0.4)
    nameLabel = Entry(createWindow, borderwidth=5, width = round((screenWidth/4) * 0.0625))
    nameLabel.place(anchor=W, relx = 0.3, rely=0.4)

    submitButton = Button(createWindow, text = "Submit", command = lambda: create_new(nameLabel.get()) if nameLabel.get().isalnum() else messagebox.showerror("INVALID DATA", "DATABASE NAME MUST BE ALPHA-NUMERIC ONLY."))
    submitButton.place(anchor=E, relx = 0.5, rely = 0.7)


    createWindow.protocol("WM_DELETE_WINDOW", lambda: end(db))
    createWindow.mainloop()

'''
    MAIN QUERY WINDOW
'''

def startQuery(db, username, host, password, dbName):

    tables = []
    activeWin = None

    # Different Queries
    def createTable():

        global activeWin
        columns = {}

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            nonlocal db
            db.close()
            db = mysql.connector.connect(
                username = username,
                host = host,
                password = password,
                db = dbName
            )
            cursor = db.cursor(buffered=True)
            cursor.execute('SHOW TABLES;')
            tables.clear()
            for i in cursor: tables.append(i[0])
            cursor.close()
            global activeWin
            activeWin = None
            # Code By Utkarsh Pant :) https://github.com/utkarsh-pant
            closeAll([sWindow])
        
        def addCol():

            def runQueryAddCol():

                def checkDate(input_text):
                    pattern = re.compile(r"([0-9]+(-[0-9]+)+)", re.IGNORECASE)
                    return pattern.match(input_text)
                colName = cName.get()
                if colName in columns:
                    messagebox.showerror("ERR!", "Column names must be unique!")
                    return 0
                
                if colName.isalnum() == False:
                    messagebox.showerror("ERR!", "Column names must be alpha-numeric")
                    return 0
                
                colQuery = ""
                attribute = ""
                colName = cName.get()
                if colName in columns.keys():
                    messagebox.showerror("Column name should be unique!")
                    return 0
                
                if colName.isalnum() != True:
                    k = colName
                    k.replace(" ", "")
                    if k.isalnum() == False: 
                        messagebox.showerror("Column name should be alpha numeric.")
                        return 0
                    else: k = "\""+k+"\""
                dataType = dType.get()
                colQuery = f"{colName} {dataType}"
                attribute = f"Datatype: {dataType},"
                if nAllow.get() == 0:
                    colQuery += " NOT NULL"
                    attribute += " No Null Values,"
                if dVal.get() == 1:
                    colQuery += " UNIQUE"
                    attribute += " Distinct Values Only,"

                if defEnabled.get() == 1:
                    if "char" in dataType: defVal = "\"" + defEntry.get() + "\""
                    elif dataType == "int":
                        defVal = defEntry.get()
                        if defVal.isnumeric() == False and defVal[1:].isnumeric() == False:
                            messagebox.showerror("ERR", "INVALID DEFAULT VALUE")
                            return 0
                    elif dataType == "decimal":
                        defVal = defEntry.get()
                        if is_number_regex(defVal) == False and is_number_regex(defVal[1:]) == False:
                            messagebox.showerror("ERR", "INVALID DEFAULT VALUE")
                            return 0
                    elif dataType == "date":
                        defVal = defEntry.get()
                        if checkDate(defVal) == False:
                            messagebox.showerror("ERR", "INVALID DEFAULT VALUE")
                            return 0         
                        defVal = "\"" + defVal + "\""
                    colQuery += f" DEFAULT {defVal}"
                    attribute += f" DEFAULT VALUE: {defVal},"   

                if pKey.get() == 1:
                    colQuery += f" PRIMARY KEY"
                    attribute += " PRIMARY KEY"

                if (pKey.get() == 1 or dVal.get() == 1) and defEnabled.get() == 1:
                    messagebox.showerror("ERR!", "DEFAULT AND UNIQUE CANNOT WORK TOGETHER!")
                    return 0

                columns[colName] = colQuery
                displayTable.insert(parent="", index='end', iid = len(columns), text=len(columns), values = (colName, attribute))

                

            miniWindow = Tk()
            miniWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

            lbl1 = Label(miniWindow, text="Column Name: ")
            lbl1.place(relx = 0.5, rely = 0.1, anchor = E)

            cName = Entry(miniWindow)
            cName.place(relx = 0.5, rely= 0.1, anchor = W)

            lbl2 = Label(miniWindow, text="Datatype: ")
            lbl2.place(relx = 0.5, rely = 0.2, anchor = E)

            dType = ttk.Combobox(miniWindow, values = ("int","decimal","date","varchar","char"), state="readonly")
            dType.place(relx = 0.5, rely= 0.2, anchor = W)
            dType.current(0)

            nAllow = IntVar(miniWindow)
            nCheck = ttk.Checkbutton(miniWindow, variable = nAllow)
            nCheck.place(relx = 0.2, rely= 0.4, anchor = E)

            lbl3 = Label(miniWindow, text=" Null Allowed")
            lbl3.place(relx=0.2, rely=0.4, anchor = W)

            dVal = IntVar(miniWindow)
            dCheck = ttk.Checkbutton(miniWindow, variable = dVal)
            dCheck.place(relx = 0.5, rely= 0.4, anchor = E)

            lbl4 = Label(miniWindow, text=" Unique Values")
            lbl4.place(relx=0.5, rely=0.4, anchor = W)

            defEnabled = IntVar(miniWindow)
            defCheck = ttk.Checkbutton(miniWindow, variable = defEnabled)
            defCheck.place(relx=0.2, rely=0.5, anchor=E)

            lbl5 = Label(miniWindow, text = "Default Value:")
            lbl5.place(relx=0.5, rely=0.5, anchor=E )

            defEntry = Entry(miniWindow)
            defEntry.place(relx=0.5, rely=0.5, anchor=W)

            pKey = IntVar(miniWindow)
            pCheck = ttk.Checkbutton(miniWindow, variable = pKey)
            pCheck.place(relx = 0.2, rely= 0.6, anchor = E)

            lbl6 = Label(miniWindow, text=" Primary Key")
            lbl6.place(relx=0.2, rely=0.6, anchor = W)


            submitButton = Button(miniWindow, text="ADD COLUMN", command = runQueryAddCol)
            submitButton.place(relx = 0.5, rely=0.9, anchor = S)

            miniWindow.mainloop()

        def runQuery():
            if len(columns) == 0:
                messagebox.showerror("ERR","Need atleast 1 column!")
                return 0

            if tName.get() in tables:
                messagebox.showerror("ERR","Table names must be unique!")
                return 0

            query = f"CREATE TABLE {tName.get()}({','.join([f'{columns[i]}' for i in columns])});"
            cursor = db.cursor()
            print(query)	
            cursor.execute(query)
            print(query)
            cursor.close()
            try: pyperclip.copy(query)
            except: pass
            messagebox.showinfo("SUCCESS","TABLE ADDED!")
            
        sWindow = Tk()
        sWindow.geometry(f'{round(screenWidth/3)}x{round(screenHeight/3)}+0+0')

        lbl1 = Label(sWindow, text="Table Name: ")
        lbl1.place(relx = 0.5, rely = 0.1, anchor = E)

        tName = Entry(sWindow)
        tName.insert(0, 'tableName')
        tName.place(relx = 0.5, rely = 0.1, anchor = W)

        addButton = Button(sWindow, text="Add Column", command = addCol)
        addButton.place(relx = 0.5, rely = 0.2, anchor = W)

        submitButton = Button(sWindow, text="Run Query", command = runQuery)
        submitButton.place(relx = 0.5, rely= 0.2, anchor = E)

        parentFrame = LabelFrame(sWindow)
        parentFrame.place(relx = 0.5, rely = 0.3, anchor = N, relwidth = 1, relheight = 0.6)

        frameCanvas = Canvas(parentFrame, background="white")
        frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

        frameScrollbarY = ttk.Scrollbar(parentFrame, orient="vertical", command=frameCanvas.yview)
        frameScrollbarY.place(anchor = E, rely=0.5, relx=1, relheight = 1)

        frameScrollbarX = ttk.Scrollbar(parentFrame, orient="horizontal", command=frameCanvas.xview)
        frameScrollbarX.place(anchor=S, rely=1, relx=0.5, relwidth=1)

        frameCanvas.configure(yscrollcommand=frameScrollbarY.set)
        frameCanvas.configure(xscrollcommand=frameScrollbarX.set)
        frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))
        dFrame = Frame(frameCanvas, background="white")
        frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)

        displayTable = ttk.Treeview(dFrame)
        displayTable['columns'] = ('Column', 'Attributes')
        displayTable.column("#0", minwidth=10)
        displayTable.column("Column", minwidth = 10)
        displayTable.column("Attributes", minwidth = 10)
        displayTable.heading("#0", text="S. No.", anchor = W)        
        displayTable.heading("Column", text="Column", anchor = W)
        displayTable.heading("Attributes", text="Attributes", anchor = W)        
        displayTable.pack(fill=BOTH, expand=YES)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()

    def dropTable():
        global activeWin
        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0

        if len(tables) == 0:
            messagebox.showerror("ERROR","No tables to delete!")
            return 0

        def killSelf():
            nonlocal db
            db.close()
            db = mysql.connector.connect(
                username = username,
                host = host,
                password = password,
                db = dbName
            )
            cursor = db.cursor(buffered=True)
            cursor.execute('SHOW TABLES;')
            tables.clear()
            for i in cursor: tables.append(i[0])
            cursor.close()
            global activeWin
            activeWin = None
            closeAll([dWindow])

        def runQuery():
            q = db.cursor(buffered=True)
            k = cBox.get()
            q.execute(f'DROP TABLE {k};')
            try: pyperclip.copy(f'DROP TABLE {k};')
            except: pass
            messagebox.showinfo(f"Successfully deleted {k}!")
            q.close()

            options = list(cBox['values'])
            options.remove(k)

            if len(options) == 0:
                killSelf

            cBox['values'] = options
            cBox.current(0)

        dWindow = Tk()
        dWindow.title('Query - Delete Table')
        dWindow.geometry(f'{round(screenWidth/3)}x{round(screenHeight/3)}+0+0')

        lbl = Label(dWindow, text="DESCRIBE  ")
        lbl.place(anchor=E, rely=0.2,relx=0.5)

        cBox = ttk.Combobox(dWindow, value=tables, width=10, state="readonly")
        cBox.place(anchor=W, rely=0.2, relx= 0.5)
        cBox.current(0)

        submitButton = Button(dWindow, text='DELETE TABLE', command= runQuery)
        submitButton.place(anchor=CENTER, rely=0.4, relx=0.5)

        activeWin = dWindow

        dWindow.protocol("WM_DELETE_WINDOW", killSelf)
        dWindow.mainloop()


    def descTable():
        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
            
        def killSelf():
            global activeWin
            activeWin = None
            closeAll([dWindow])

        def runQuery():
            print(tables)
            print(cBox.get())
            resultTable.delete(*resultTable.get_children())
            q = db.cursor(buffered=True)
            q.execute(f'DESCRIBE {cBox.get()};')
            try: pyperclip.copy(f'DESCRIBE {cBox.get()};')
            except: pass
            c = 0
            for i in q: 
                val = []
                for k in i:
                    if type(k) == bytes: val.append(k.decode('utf-8'))
                    else: val.append(k)

                resultTable.insert(parent='', index='end', iid = c, text="", values= tuple(val))
                c+= 1
            q.close()

        if len(tables) == 0:
            messagebox.showerror("NO TABLES IN THE DATABASE")
            return 0


        dWindow = Tk()
        dWindow.title('Query - Describe Table')
        dWindow.geometry(f'{round(screenWidth/3)}x{round(screenHeight/3)}+0+0')

        lbl = Label(dWindow, text="DESCRIBE  ")
        lbl.place(anchor=E, rely=0.2,relx=0.5)

        cBox = ttk.Combobox(dWindow, value=tables, width=10,state="readonly")
        cBox.place(anchor=W, rely=0.2, relx= 0.5)
        cBox.current(0)

        submitButton = Button(dWindow, text='RUN QUERY', command= runQuery)
        submitButton.place(anchor=CENTER, rely=0.4, relx=0.5)

        parentFrame = LabelFrame(dWindow)
        parentFrame.place(anchor=N, relx = 0.5, rely = 0.5, relheight = 0.4, relwidth = 0.8)

        frameCanvas = Canvas(parentFrame, background="white")
        frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

        frameScrollbarY = ttk.Scrollbar(parentFrame, orient="vertical", command=frameCanvas.yview)
        frameScrollbarY.place(anchor = E, rely=0.5, relx=1, relheight = 1)

        frameScrollbarX = ttk.Scrollbar(parentFrame, orient="horizontal", command=frameCanvas.xview)
        frameScrollbarX.place(anchor=S, rely=1, relx=0.5, relwidth=1)

        frameCanvas.configure(yscrollcommand=frameScrollbarY.set)
        frameCanvas.configure(xscrollcommand=frameScrollbarX.set)
        frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))
        dFrame = Frame(frameCanvas, background="white")
        frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)

        resultTable = ttk.Treeview(dFrame)
        resultTable['columns'] = ('col','dataType','null', 'key', 'def', 'ext')
        resultTable.column("#0", width=0)
        resultTable.column("col", minwidth=10)            
        resultTable.column("dataType", minwidth=10)    
        resultTable.column("null", minwidth=10)    
        resultTable.column("key", minwidth=10)
        resultTable.column("def", minwidth=10)
        resultTable.column("ext", minwidth=10)

        resultTable.heading("col", text="Col. Name", anchor=W)
        resultTable.heading("dataType", text="DataType", anchor=W)        
        resultTable.heading("null", text="Null Val. Allowed", anchor=W)        
        resultTable.heading("key", text="Key", anchor=W)        
        resultTable.heading("def", text="Default Value", anchor=W)        
        resultTable.heading("ext", text="Extra", anchor=W)                

        resultTable.pack(fill=BOTH,expand=YES)
        
        activeWin = dWindow
        dWindow.protocol("WM_DELETE_WINDOW", killSelf)
        dWindow.mainloop()
        
    def selectTable1():
        if len(tables) == 0:
            messagebox.showerror("ERR","ERROR! No Tables")

        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            global activeWin
            activeWin = None
            closeAll([sWindow])

        def runQuery():
            tName = cBox.get()
            killSelf()
            selectTable2(tName)
            

        sWindow = Tk()
        sWindow.geometry()
        sWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

        lbl = Label(sWindow, text="Select Table: ")
        lbl.place(anchor=E, relx=0.5, rely=0.5)

        cBox = ttk.Combobox(sWindow, values = tables,state="readonly")
        cBox.current(0)
        cBox.place(anchor=W, relx=0.5, rely=0.5)

        submitButton = Button(sWindow, text='Submit', command= runQuery)
        submitButton.place(anchor=CENTER, relx=0.5, rely = 0.7)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()

    def selectTable2(name):
        if len(tables) == 0:
            messagebox.showerror("ERR","ERROR! No Tables")

        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            nonlocal db
            db.close()
            db = mysql.connector.connect(
                username = username,
                host = host,
                password = password,
                db = dbName
            )
            global activeWin
            activeWin = None
            closeAll([sWindow])

        def runQuery():
            nonlocal wOp
            if len(selectedButtons) == 0:
                colQ = "*"
            else: colQ = ",".join(selectedButtons)
            query = "SELECT " + colQ + f" FROM {name}"

            if whereEnabled.get() == 1:
                query += " WHERE "
                operator = wOp.get()
                if wNot.get() == "IS NOT": query += "NOT "
                queryVal = wEntry.get()
                if is_number_regex(queryVal) == False and is_number_regex(queryVal[1:]) == False and queryVal[0]=="-" and queryVal != 'NULL': queryVal = "\"" + queryVal + "\""
                if queryVal == 'NULL':
                    if operator == '=': operator = 'IS'
                    elif operator == '!=': operator = 'IS NOT'
                    else:
                        messagebox.showerror("ERR!", "Null only works with = or != operators")
                        return 0

                query += f"{wCol1.get()} {operator} {queryVal}"

            if orderByEnabled.get() == 1:
                ord_by = 'ASC'
                if cOrderBoxOrd.get() == "Descending": ord_by = "DESC"
                query += f" ORDER BY {cOrderBoxCol.get()} {ord_by}"

            query += ";"
            print(query)

            dWindow = Tk()
            dWindow.geometry(f'{round(screenWidth/3)}x{round(screenHeight/3)}+0+0')

            parentFrame = LabelFrame(dWindow)
            parentFrame.place(anchor=NW, relx = 0, rely = 0, relheight = 1, relwidth = 1)

            frameCanvas = Canvas(parentFrame, background="white")
            frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

            frameScrollbarY = ttk.Scrollbar(parentFrame, orient="vertical", command=frameCanvas.yview)
            frameScrollbarY.place(anchor = E, rely=0.5, relx=1, relheight = 1)

            frameScrollbarX = ttk.Scrollbar(parentFrame, orient="horizontal", command=frameCanvas.xview)
            frameScrollbarX.place(anchor=S, rely=1, relx=0.5, relwidth=1)

            frameCanvas.configure(yscrollcommand=frameScrollbarY.set)
            frameCanvas.configure(xscrollcommand=frameScrollbarX.set)
            frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))
            dFrame = Frame(frameCanvas, background="white")
            frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)

            selectedButtons_ = selectedButtons.copy()
            if len(selectedButtons_) == 0: selectedButtons_ = columns.copy()
            resultTable = ttk.Treeview(dFrame)
            resultTable['columns'] = tuple(selectedButtons_)
            for i in selectedButtons_:
                resultTable.column(i, minwidth = 10)
                resultTable.heading(i, text=i, anchor = W)             

            cursor = db.cursor(buffered=True)
            cursor.execute(query)
            try: pyperclip.copy(query)
            except: pass
            c=0
            for i in cursor:
                resultTable.insert(parent='', index='end', iid = c, text="", values= tuple(i))
                c+= 1

            resultTable.pack(fill=BOTH,expand=YES)

            dWindow.mainloop()

        def buttonClick(button):
            buttonName = button['text']
            if buttonName in selectedButtons:
                selectedButtons.remove(buttonName)
                button['bg'] = 'white'
                button['activebackground']
            else:
                selectedButtons.append(buttonName)
                button['bg'] = 'green'
        # Code By Utkarsh Pant :) https://github.com/utkarsh-pant
        sWindow = Tk()
        sWindow.geometry(f'{round(screenWidth/3)}x{round(screenHeight/3)}+0+0')

        lbl1 = Label(sWindow, text="SELECT FROM TABLE COLUMNS: " )
        lbl1.place(rely = 0.2, relx = 0.5, anchor = E)

        lbl2 = Label(sWindow, text="(Leave empty for all)")
        lbl2.place(rely=0.3, relx = 0.5)


        cursor = db.cursor(buffered=True)
        cursor.execute(f"DESC {name};")
        columns = [i[0] for i in cursor]
        cursor.close()


        parentFrame = LabelFrame(sWindow)
        parentFrame.place(rely = 0.2, relx= 0.5, anchor = W, relheight = 0.2, relwidth = 0.4)

        frameCanvas = Canvas(parentFrame, background="white")
        frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

        frameScrollbarY = ttk.Scrollbar(parentFrame, orient="vertical", command=frameCanvas.yview)
        frameScrollbarY.place(anchor = E, rely=0.5, relx=1, relheight = 1)

        frameCanvas.configure(yscrollcommand=frameScrollbarY.set)
        frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))
        dFrame = Frame(frameCanvas, background="white")

        selectedButtons = []

        for i in columns:
            t = Button(dFrame, text=i, borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W)
            t.configure(command= lambda t=t: buttonClick(t))
            t.configure(height=round(screenHeight*0.1*0.0075), width=round(screenWidth*0.3*0.9))
            t.pack(fill="both", expand = YES)
    
        orderByEnabled = IntVar(sWindow)
        cOrderButton = Checkbutton(sWindow, variable=orderByEnabled)
        cOrderButton.place(anchor = W, rely = 0.4, relx = 0.1)

        lbl3 = Label(sWindow, text=" ORDER BY: " )
        lbl3.place(rely = 0.4, relx = 0.3, anchor = E)
        cOrderBoxOrd = ttk.Combobox(sWindow, values=("Ascending", "Descending"),state="readonly")
        cOrderBoxOrd.place(rely = 0.4, relx = 0.6, anchor = W,)
        cOrderBoxOrd.current(0)
        cOrderBoxCol = ttk.Combobox(sWindow, values=columns, state="readonly")
        cOrderBoxCol.place(rely = 0.4, relx = 0.3, anchor = W)
        cOrderBoxCol.current(0)

        whereEnabled = IntVar(sWindow)
        cWhereButton = Checkbutton(sWindow, variable = whereEnabled)
        cWhereButton.place(anchor = W, rely = 0.5, relx = 0.1)
        
        lbl4 = Label(sWindow, text="CONDITION: ")
        lbl4.place(rely = 0.5, relx = 0.3, anchor = E)

        wCol1 = ttk.Combobox(sWindow, values = columns,state="readonly")
        wCol1.place(rely = 0.5, relx = 0.3, anchor = W, relwidth = 0.15)
        wCol1.current(0)

        wNot = ttk.Combobox(sWindow, values = ('IS','IS NOT'),state="readonly")
        wNot.place(rely = 0.5, relx = 0.6,anchor = E, relwidth = 0.1)
        wNot.current(0)

        wOp = ttk.Combobox(sWindow, values = ("=","<",">","<=",">=", "!="),state="readonly")
        wOp.place(rely=0.5, relx= 0.6, anchor = W, relwidth = 0.1)
        wOp.current(0)

        wEntry = Entry(sWindow)
        wEntry.insert(0, '0')
        wEntry.place(rely=0.5, relx = 0.9, anchor = E, relwidth = 0.2)

        frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)
        submitButton = Button(sWindow, text='RUN QUERY', command= runQuery)
        submitButton.place(anchor=CENTER, relx=0.5, rely = 0.8)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()

    def insertData1():
        if len(tables) == 0:
            messagebox.showerror("ERR","ERROR! No Tables")

        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            global activeWin
            activeWin = None
            closeAll([sWindow])

        def runQuery():
            tName = cBox.get()
            killSelf()
            insertData2(tName)
            

        sWindow = Tk()
        sWindow.geometry()
        sWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

        lbl = Label(sWindow, text="Select Table: ")
        lbl.place(anchor=E, relx=0.5, rely=0.5)

        cBox = ttk.Combobox(sWindow, values = tables,state="readonly")
        cBox.current(0)
        cBox.place(anchor=W, relx=0.5, rely=0.5)

        submitButton = Button(sWindow, text='Submit', command= runQuery)
        submitButton.place(anchor=CENTER, relx=0.5, rely = 0.7)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()

    def insertData2(name):
        if len(tables) == 0:
            messagebox.showerror("ERR","ERROR! No Tables")

        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            nonlocal db
            db.close()
            db = mysql.connector.connect(
                username = username,
                host = host,
                password = password,
                db = dbName
            )
            global activeWin
            activeWin = None
            closeAll([sWindow])
        
        def checkDate(input_text):
            pattern = re.compile(r"([0-9]+(-[0-9]+)+)", re.IGNORECASE)
            return pattern.match(input_text)

        def runQuery():

            query = f"INSERT INTO {name}({','.join(list(columns.keys()))}) VALUES("
            for butt in allButtons:
                data = butt.get()
                colName = allButtons[butt]
                dataType =  columns[colName].lower()
                try:
                    dataType = dataType.decode('utf-8')
                except: pass
                if data == "": data = "NULL"
                if colName in notNullColumns and data == "NULL":
                    messagebox.showerror("ERR!", f"COLUMN - {colName} CANNOT HAVE NULL VALUES")
                    return 0
                if colName in uniqueColumns:
                    cursor = db.cursor()
                    cursor.execute(f"SELECT {colName} FROM {name}")
                    k = False
                    for i in cursor:
                        j = str(i[0]).lower()
                        if j== data.lower(): k = True
                    if k:
                        messagebox.showerror("ERR!", f"COLUMN - {colName} DATA MUST BE UNIQUE")
                    cursor.close()
                if "char" in dataType: data = "\"" + data + "\""
                elif dataType == "int":
                    if data.isnumeric() == False and data[1:].isnumeric() == False:
                        messagebox.showerror("ERR", "INVALID VALUE")
                        return 0
                elif dataType == "decimal":
                    if is_number_regex(data) == False and is_number_regex(data) == False:
                        messagebox.showerror("ERR", "INVALID VALUE")
                        return 0
                elif dataType == "date":
                    if checkDate(data) == False:
                        messagebox.showerror("ERR", "INVALID DEFAULT VALUE")
                        return 0         
                    data = "\"" + data + "\""
                print(data, colName, dataType)

                query += data + ","
            cursor = db.cursor(buffered=True)
            try:
                query = query[:-1]+");"
                cursor.execute(query)
                try: pyperclip.copy(query)
                except: pass
                db.commit()
            except Exception:
                messagebox.showerror("ERR", "UNEXPECTED ERROR. MAKE SURE ALL COLUMN CONTSRAINTS ARE FOLLOWED.")
                cursor.close()
                return 0
            else:
                messagebox.showinfo("SUCCESS!", "DATA ADDED!")
            cursor.close()
            killSelf()

        sWindow = Tk()
        sWindow.geometry()
        sWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

        parentFrame = LabelFrame(sWindow)
        parentFrame.place(relx = 0.5, rely = 0.1, anchor = N, relwidth = 1, relheight = 0.7)

        frameCanvas = Canvas(parentFrame, background="white")
        frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

        frameScrollbarY = ttk.Scrollbar(parentFrame, orient="vertical", command=frameCanvas.yview)
        frameScrollbarY.place(anchor = E, rely=0.5, relx=1, relheight = 1)

        frameScrollbarX = ttk.Scrollbar(parentFrame, orient="horizontal", command=frameCanvas.xview)
        frameScrollbarX.place(anchor=S, rely=1, relx=0.5, relwidth=1)

        frameCanvas.configure(yscrollcommand=frameScrollbarY.set)
        frameCanvas.configure(xscrollcommand=frameScrollbarX.set)
        frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))
        dFrame = Frame(frameCanvas, background="white")
        frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)

        cursor = db.cursor()
        cursor.execute(f"DESC {name};")
        columns = {}
        notNullColumns = []
        uniqueColumns = []
        allButtons = {}

        for i in cursor:
            columns[i[0]] = i[1]
            if i[2] == "NO": notNullColumns.append(i[0])
            if i[3] == 'UNI' or i[3] == 'PRI': uniqueColumns.append(i[0])

        for i in columns:
            t = Entry(dFrame, width=round(screenWidth/4), borderwidth=0, background="white", highlightcolor="white")
            allButtons[t] = i
            t.insert(0, f"Enter data for {i}")
            t.pack(fill=X)        

        submitButton = Button(sWindow, text = "Run Query", command = runQuery)
        submitButton.place(relx=0.5, rely= 0.9, anchor = N)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()

    def removeData():
        if len(tables) == 0:
            messagebox.showerror("ERR","ERROR! No Tables")

        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            global activeWin
            activeWin = None
            closeAll([sWindow])

        def runQuery():
            tName = cBox.get()
            killSelf()
            removeData2(tName)
            

        sWindow = Tk()
        sWindow.geometry()
        sWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

        lbl = Label(sWindow, text="Select Table: ")
        lbl.place(anchor=E, relx=0.5, rely=0.5)

        cBox = ttk.Combobox(sWindow, values = tables,state="readonly")
        cBox.current(0)
        cBox.place(anchor=W, relx=0.5, rely=0.5)

        submitButton = Button(sWindow, text='Submit', command= runQuery)
        submitButton.place(anchor=CENTER, relx=0.5, rely = 0.7)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()
    
    def removeData2(tName):
        if len(tables) == 0:
            messagebox.showerror("ERR","ERROR! No Tables")

        global activeWin

        if activeWin != None: 
            messagebox.showerror("ERROR","Another query window open!")
            return 0
        
        def killSelf():
            global activeWin
            activeWin = None
            closeAll([sWindow])

        def runQuery():
            query = f"DELETE FROM {tName}"
            if whereEnabled.get() == 1:
                query += " WHERE "
                operator = wOp.get()
                if wNot.get() == "IS NOT": query += "NOT "
                queryVal = wEntry.get()
                if is_number_regex(queryVal) == False and is_number_regex(queryVal[1:]) == False and queryVal[0]=="-" and queryVal != 'NULL': queryVal = "\"" + queryVal + "\""
                if queryVal == 'NULL':
                    if operator == '=': operator = 'IS'
                    elif operator == '!=': operator = 'IS NOT'
                    else:
                        messagebox.showerror("ERR!", "Null only works with = or != operators")
                        return 0

                query += f"{wCol1.get()} {operator} {queryVal}"
            
            cursor = db.cursor()
            cursor.execute(query+";")
            cursor.close()
            try: pyperclip.copy(query+";")
            except: pass
            messagebox.showinfo("SUCCESS!", "DATA REMOVED!")
            killSelf()
            
        cursor = db.cursor()
        cursor.execute(f"DESC {tName};")
        columns = []
        for i in cursor: columns.append(i[0])
        cursor.close()

        sWindow = Tk()
        sWindow.geometry()
        sWindow.geometry(f'{round(screenWidth/4)}x{round(screenHeight/4)}+0+0')

        whereEnabled = IntVar(sWindow)
        cWhereButton = Checkbutton(sWindow, variable = whereEnabled)
        cWhereButton.place(anchor = W, rely = 0.5, relx = 0.1)
        
        lbl4 = Label(sWindow, text="CONDITION: ")
        lbl4.place(rely = 0.5, relx = 0.3, anchor = E)

        wCol1 = ttk.Combobox(sWindow, values = tuple(columns), state="readonly")
        wCol1.place(rely = 0.5, relx = 0.3, anchor = W, relwidth = 0.15)
        wCol1.current(0)

        wNot = ttk.Combobox(sWindow, values = ('IS','IS NOT'),state="readonly")
        wNot.place(rely = 0.5, relx = 0.6,anchor = E, relwidth = 0.1)
        wNot.current(0)

        wOp = ttk.Combobox(sWindow, values = ("=","<",">","<=",">=", "!="),state="readonly")
        wOp.place(rely=0.5, relx= 0.6, anchor = W, relwidth = 0.1)
        wOp.current(0)

        wEntry = Entry(sWindow)
        wEntry.insert(0, '0')
        wEntry.place(rely=0.5, relx = 0.9, anchor = E, relwidth = 0.2)

        submitButton = Button(sWindow, text='Submit', command= runQuery)
        submitButton.place(anchor=CENTER, relx=0.5, rely = 0.7)

        activeWin = sWindow
        sWindow.protocol("WM_DELETE_WINDOW", killSelf)
        sWindow.mainloop()

    db.close()
    db = mysql.connector.connect(
        username = username,
        host = host,
        password = password,
        db = dbName
    )

    cursor = db.cursor(buffered=True)
    cursor.execute('SHOW TABLES;')
    for i in cursor: tables.append(i[0])
    cursor.close()


    mWindow = Tk()
    mWindow.title('EasySQL')
    mWindow.geometry(f'{screenWidth}x{screenHeight}+0+0')

    lbl = Label(mWindow, text="EasySQL", fg='green', font=('Helvetica', round(screenHeight*screenWidth*0.000024113), BOLD))
    lbl.place(anchor = CENTER, relx = 0.5, rely=0.0463)

    lbl2 = Label(mWindow, text="CHOOSE QUERIES TO PERFORM", fg = 'green', font = ('Helvetica', round(screenHeight*screenWidth*0.00000803766), UNDERLINE),borderwidth=1)
    lbl2.place(anchor = CENTER, relx = 0.5, rely= 0.15)

    dbParentFrame = LabelFrame(mWindow)
    dbParentFrame.place(anchor=N, relx = 0.5, rely= 0.2, relheight = 0.5, relwidth= 0.5)

    frameCanvas = Canvas(dbParentFrame, background="white")
    frameCanvas.place(anchor = CENTER, relx= 0.5, rely= 0.5, relheight = 1, relwidth = 1)

    frameScrollbar = ttk.Scrollbar(dbParentFrame, orient="vertical", command=frameCanvas.yview)
    frameScrollbar.place(anchor = E, rely=0.5, relx=1, relheight = 1)

    frameCanvas.configure(yscrollcommand=frameScrollbar.set)
    frameCanvas.bind("<Configure>", lambda e: frameCanvas.configure(scrollregion = frameCanvas.bbox('all')))

    dbFrame = Frame(frameCanvas, background="white")
    frameCanvas.create_window((0,0), window=dbFrame, anchor = NW)

    # LIST OF COMPATIBLE QUERIES:
    
    cButton = Button(dbFrame, text="CREATE TABLE", borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, command= createTable)
    cButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
    cButton.pack(fill="both", expand = YES)
    
    dButton = Button(dbFrame, text="DESCRIBE TABLE", borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, command= descTable)
    dButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
    dButton.pack(fill="both", expand = YES)
    
    deButton = Button(dbFrame, text="DELETE TABLE", borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, command= dropTable)
    deButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
    deButton.pack(fill="both", expand = YES)

    sButton = Button(dbFrame, text="SELECT DATA", borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, command= selectTable1)
    sButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
    sButton.pack(fill="both", expand = YES)    

    sButton = Button(dbFrame, text="INSERT DATA", borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, command= insertData1)
    sButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
    sButton.pack(fill="both", expand = YES)    

    rButton = Button(dbFrame, text="REMOVE DATA", borderwidth=0, background="white", highlightcolor="white", activeforeground="blue", anchor=W, command= removeData)
    rButton.configure(height=round(screenHeight*0.5*0.0075), width=round(screenWidth*0.5*0.9))
    rButton.pack(fill="both", expand = YES)  

    

    mWindow .mainloop()









'''
BASIC WINDOW SETUP
'''
lbl=Label(window, text="EasySQL", fg='green', font=('Helvetica', round(screenHeight*screenWidth*0.000024113), BOLD))
lbl.place(anchor = CENTER, x=round(screenWidth/2), y=screenHeight*0.0463)
window.title('EasySQL')
window.geometry(f'{screenWidth}x{screenHeight}+0+0')

sImg = Image.open(filePath + 'images/start.png')
sImg = ImageTk.PhotoImage(sImg)
sButton = Button(window, image= sImg, borderwidth=0, command = start)
sButton.place(relx = 0.5, rely = 0.5, anchor = CENTER)

window.protocol("WM_DELETE_WINDOW", lambda: closeAll([window, mLogWindow]) if logOpened else closeAll([window]))
window.mainloop()
