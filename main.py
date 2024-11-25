import sys, os, re, datetime, asyncio
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
textFont = CTkFont(family="Helvetica", size=(screenWidth*screenHeight)//60000, weight="bold")


def typeAnimation(parentObj, textLabel, newText, timeTotal):
    textLabel.configure(text="")
    timeTotal = timeTotal * 1000

    def animationLoop(i=0):
        if i < len(newText):
            textLabel.configure(text=textLabel.cget("text") + newText[i])
            parentObj.after(int(timeTotal / len(newText)), animationLoop, i + 1)

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
            print(i)
            i[1].delete(0, END)
            i[0].insert(0, defaultValues[dataWidgets.index(i)])

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
                     

    submitButton = CTkButton(initialWindow, text="Submit", font=textFont, command = submitDetails)
    submitButton.place(anchor = E, relx=0.49, rely= 0.7)
    resetButton = CTkButton(initialWindow, text="Reset Details", font=textFont, command = resetDetails)
    resetButton.place(anchor = W, relx=0.51, rely= 0.7)
    
def dbConnectionMenu(a,b,c): pass





appName = CTkButton(initialWindow, text="EasySQL", font=CTkFont(family="Impact", size=(screenWidth*screenHeight)//10000), bg_color=bgColor, text_color=orangeColor, fg_color="transparent", hover=False)
appUnderline = CTkLabel(initialWindow, fg_color=grayColor, text="")
appSubheading = CTkLabel(initialWindow, text="Easy Execution. Easy life.", fg_color=bgColor, text_color=blueColor, font=textFont)

appName.place(relx=0.5, rely=0.4, anchor=CENTER, relheight = 0.6)
appUnderline.place(relx=0.5, rely=0.5, anchor=N, relwidth=0.4, relheight=0.01)
appSubheading.place(relx=0.5, rely=0.55, anchor=CENTER)

appName.configure(command = lambda: loginPage(initialWindow, appSubheading, appUnderline, appName))

initialWindow.config(bg=bgColor)
initialWindow.geometry(f"{screenWidth}x{screenHeight}+0+0")
initialWindow.mainloop()




