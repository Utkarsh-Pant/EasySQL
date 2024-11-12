import sys, os

from tkinter import *
from tkinter import font
import mysql.connector

from PIL import Image, ImageTk
initialWindow = Tk()
initialWindow.title("EasySQL")
print(type(initialWindow))



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
            errorLabel = Label(initialWindow, text="Invalid Connection Details", fg='red', font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD))
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
        
        dbConnectionMenu(initialWindow, subHeading, connection, host, port, username, password)
                     

    submitButton = Button(initialWindow, text="Submit", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = submitDetails)
    submitButton.place(anchor = E, relx=0.49, rely= 0.7)
    resetButton = Button(initialWindow, text="Reset Details", font=('Terminal', round(screenHeight*screenWidth*0.0000113), font.BOLD), command = resetDetails)
    resetButton.place(anchor = W, relx=0.51, rely= 0.7)


def dbConnectionMenu(initialWindow, subHeading, connection, host, port, username, password):
    '''
    Database connection menu
    '''
    subHeading.config(text="Choose Database")

    selectorParentFrame = LabelFrame(initialWindow)
    selectorParentFrame.place(anchor=CENTER, x=round(screenWidth/2), y=screenHeight*0.5)
    


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