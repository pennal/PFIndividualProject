# -*- coding: utf-8 -*-
import requests         #Used to request the data from the APIs
import json             #Pretty print the incoming data
import datetime         #Used to calculate the time left for a certain bus
import time             #Used for some delays
from tkinter import *   #All for the GUI
import sys              #Used to abort the script

import colorGenerator   #Importing the file to generate color transitions


########################################################################################################################
############################################## PLEASE READ BEFORE RUNNING ##############################################
########################################################################################################################
# In order for the program to scale correctly, it has to run on a screen that is at least 1680 x 1050, without the     #
# dock or any other element that might shrink the screen space. This limitation might be removed in a later version.   #
# If not used on a screen with such dimensions, some interface elements might get truncated, and the whole GUI will    #
# fall apart. Also:                                                                                                    #
#   - Comments are still missing in many parts of this document                                                        #
#   - As of now, everything is in one file. Once the program works in the desired way, it will be split into multiple  #
#     files                                                                                                            #
#   - Code cleanliness in general will be improved once the mechanics of it are working properly                       #
#   - Exception handling is still poor. This is on my list                                                             #
#                                                                                                                      #
# In order to see the animation without having to wait, the right arrow key can be pressed. This will trigger the pop  #
########################################################################################################################



#GENERAL SETTINGS
#base URL for the api
apiURL = 'http://transport.opendata.ch/v1/stationboard'
#number of connections requested. This is the minimum value to be known to work correctly
numberOfRequests = 15
#Stations for which the buses are displayed. If only one is needed, still use a list!
forStation = ["Ponte Madonnetta"]#['Ponte Madonnetta','Universita']



#GLOBAL VARIABLES
#Is the main APP idle? Used to avoid overlapping events
isIdle = True
#Watch colon blink "counter", used to actually make the symbol blink
isBlinkTrue = True
#Trigger to fetch new data
shouldFetchData = False
#Variable to hold all entries
entries = []
#Hardwired for now, should be fixed in a later version
heightOfScreen = 1050
widthOfScreen = 1680
#Constants used to display the elements on the gui
heightOfSingleEntryBox = 230
paddingAroundBoxes = 20
widthOfOutlineOfEntryBox = 5
#Holds all the IDs for the GUI elements
boundingBoxes = []

#Defining colors for each of the companies. If you wish to add your own, use HEX notation
#TPL color Dict
colorLinesTPL = {
    '1': '#D53B81',
    '2':'#7D156A',
    '3':'#DF6422',
    '4':'#845946',
    '5':'#1B498A',
    '6':'#5B528E',
    '7':'#059239',
    '8':'#B7D14D',
    '9':'#B7D14D',
    '10':'#B7D14D',
    '11':'#006AAC',
    '12':'#5CAC35',
    '16':'#CD0927',
    'F':'#009E8D',
    'S':'#F5BC1C'
}
#For the Autopostale we only need one color
colorLinePosta = '#FEC213'
#Same for the Societa nautica Lugano
colorLineSNL = '#0B255A'
#ARL color Dict
colorLinesARL = {
    '461':'#FFE400',
    '441':'#3FB454',
    '60':'#9600F6'
}


#List to hold all of the bottom bar's element IDs
fullBottomBar = ['','','']
#Define colors for the three different time states
statusRed = '#CC0605'
statusYellow = '#FFBE00'
statusGreen = '#46BF00'
#Lists containing all transition colors
yellowToRed = colorGenerator.linear_gradient(statusYellow,statusRed,40)['hex']
greenToYellow = colorGenerator.linear_gradient(statusGreen,statusYellow,40)['hex']

#Global variables for window and canvas. Initialized as zero, kind of a placeholder
window = 0
canvas = 0

def initWindow():
    """
    Creates the main view. Called in main when the data has been fetched.
    :return: VOID
    """
    global window
    global canvas
    #Create the main window
    window = Tk()
    window.title("Bus Schedule")
    #Create the canvas where items are added
    canvas = Canvas(window, width = widthOfScreen, height = heightOfScreen, bg = "#1A1C19")
    canvas.pack()
def getCorrectLineColor(lineNumber,company):
    """
    :param lineNumber:Line number of the bus in question
    :param company: Company it belongs to
    :return: (String) Hex of the color taken from the dict. If it fails (key not found) a default color is returned
    """
    try:
        if company == 'PAG':
            return colorLinePosta
        elif company == 'TPL':
            return colorLinesTPL[lineNumber]
        elif company == 'ARL':
            return colorLinesARL[lineNumber]
        elif company == 'SNL Auto':
            return colorLineSNL
        else:
            return "red"
    except:
        return 'red'

def addNewItemWithData(lineNumber,destination,origin,colorOfLine,position = 3):
    """
    :param lineNumber:Number of the line to which the bus belongs to
    :param destination: Destination to which the bus is headed
    :param origin: Which stop it will leave from
    :param colorOfLine: Color of the line in question
    :param position: Position at which the entry has to be drawn. For new items, usually 4
    :return: VOID
    """
    offset = position*heightOfSingleEntryBox
    #changes the character size if too big
    if len(lineNumber) == 3:
        sizeOfChars = 100
    else:
        sizeOfChars = 150
    #Box holding the line number, gets colored with the correct line number
    boundingBoxes.append(canvas.create_rectangle(paddingAroundBoxes+10, paddingAroundBoxes+offset+10, 220, 220+offset, fill=colorOfLine))
    #Line number
    boundingBoxes.append(canvas.create_text(125,120+offset,text=lineNumber, font=('Helvetica Neue UltraLight',sizeOfChars),fill="white",anchor='center', tag='busNumber'))
    #Destination String
    boundingBoxes.append(canvas.create_text(250,12+offset,text=destination, font=('Helvetica Neue UltraLight',90),fill="white",anchor='nw', tag='destination'))
    #Station of origin
    boundingBoxes.append(canvas.create_text(250,230+offset,text=origin, font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='leavingStation'))
    #Circle with the status
    boundingBoxes.append(canvas.create_oval(widthOfScreen-paddingAroundBoxes-210, paddingAroundBoxes+offset+10, widthOfScreen-paddingAroundBoxes-10, 220+offset, fill=statusGreen))
    #Time left
    correctTime = deltaTime(datetime.datetime.strptime(entries[position]['departureTime'] + " " + entries[position]['departureDate'],"%H:%M:%S %Y-%m-%d"))
    #Add the time left inside the circle
    boundingBoxes.append(canvas.create_text(widthOfScreen-paddingAroundBoxes-110, paddingAroundBoxes+offset+100,text=correctTime, font=('Helvetica Neue UltraLight',100),fill="white",anchor='center', tag='timeLeft'))


def eliminateTopWithKey(event):
    """
    ===== DEBUG =====
    Invoked when the right arrow key is pressed. Used for debug purposes.
    :param event: A Key (in this case right arrow) being pressed
    :return: VOID
    """
    eliminateTop()

def eliminateTop():
    """
    Used when the first item has to be deleted off the top. It takes care of sliding the entry out of the way, as well
    as generating a new entry. The list containing all the indexes is also updated and truncated.
    :return: VOID
    """
    global isIdle
    if isIdle == True:
        isIdle = False
        global boundingBoxes
        global entries
        global canvas
        global shouldFetchData
        #Add a new item out of the view
        addNewItemWithData(entries[4]['lineNumber'],entries[4]['destination'],entries[4]['originStation'],getCorrectLineColor(entries[4]['lineNumber'],entries[4]['operator']),4)

        #Bring the bottom bar to the top of the view. Done to give the effect of a slide in for the new entry
        canvas.tag_raise(fullBottomBar[0])
        canvas.tag_raise(fullBottomBar[1])
        canvas.tag_raise(fullBottomBar[2])

        # Animation: Slide Out
        x = 0.5
        for i in range(40):
            for item in range(0,6):
                canvas.move(boundingBoxes[item],x,0)
                x +=0.5
            canvas.after(10)
            canvas.update()
        #Remove the top entry from the list of active elements
        boundingBoxes = boundingBoxes[6:]

        # Animation: Move up all remaining items as well as the new one
        for group in range(0,len(boundingBoxes)//6):
            i = 0
            x=0
            for i in range(31):
                for item in range(0,6):
                    canvas.move(boundingBoxes[item+(6*group)],0,x)
                x-=1/2
                canvas.after(10)
                canvas.update()
            #compensate a bit, TODO: remove
            for item in range(0,6):
                    canvas.move(boundingBoxes[item+(6*group)],0,+3)

            canvas.after(10)
            canvas.update()
        #Remove from list of buses
        entries = entries[1:]


        #Check if an update is needed
        if len(entries) < 10:
            print("fetching new data")
            shouldFetchData = True
        #We set the idle switch to true so the GUI resumes updating
        isIdle = True

def fetchNewDataForStation():
    global entries
    #Create a temp list to hold the data
    temporaryEntries = []
    #Repeat for all input stations
    for station in range(0,len(forStation)):
        #remove all spaces from the name of the starting station
        forStationURL = forStation[station].replace(" ","%20")


        hasTimedOut = True
        #While the text returned is a timeout, continue trying
        while hasTimedOut:
            try:
                #Get the data from the URL
                if len(entries) > 0: #If this is an update to the previously existing data
                    response = requests.get(apiURL + '?station=' + forStationURL + '&limit=' + str(numberOfRequests) + "&datetime=" + str(entries[-1]["departureDate"]) + "%20" + str(entries[-1]["departureTime"][:-3]))
                else: #New data, program just started
                    response = requests.get(apiURL + '?station=' + forStationURL + '&limit=' + str(numberOfRequests))
                #Formath the incoming data as plaintext

                data = json.loads(response.text)
                #Check if what was returned is actually a timeout issue
                if "errors" in data:
                    if "Connection timed out" in data["errors"][0]["message"]:
                        hasTimedOut = True
                        print("Connection timed out. Retrying...")
                else:
                    hasTimedOut = False
            except ConnectionError:
                print("ConnectionError: Check your internet connection, and retry")
                sys.exit()
            except:
                print("UnknownError: An unknown error has occured")
                sys.exit()


        #Clean up the data, and extract all we need
        for entry in range(0,len(data["stationboard"])):
            originStation = data["station"]["name"]
            destination = data["stationboard"][entry]["to"]
            lineNumber = data["stationboard"][entry]["number"]
            #Split the time and date
            departureTimeTemp = data["stationboard"][entry]["stop"]["departure"].split("T")
            departureDate = departureTimeTemp[0]
            departureTime = departureTimeTemp[1].split("+")[0]#Remove the greenwich delta

            datetime.datetime.strptime(departureTime, "%H:%M:%S")


            possibleDelays = data["stationboard"][entry]["stop"]["delay"]
            typeOfTransport = data["stationboard"][entry]["category"]
            operator = data["stationboard"][entry]["operator"]




            temporaryEntries.append({
                'originStation':originStation,
                'destination':destination,
                'lineNumber':lineNumber,
                'departureTime':departureTime,
                'departureDate':departureDate,
                'possibleDelays':possibleDelays,
                'typeOfTransport':typeOfTransport,
                'operator':operator
            })

    #Sort the dictionary by keys
    temporaryEntries = quickSortTime(temporaryEntries)

    #Find the entries that have to be added to the preexisting ones
    if len(entries) > 0:
        for i in range(len(temporaryEntries)-1,-1,-1):
            if temporaryEntries[i] == entries[-1]:
                #print("Found it, entry: " + str(i))
                #print("the following should be equal: " + str(temporaryEntries[i]) + " and " + str(entries[-1]))
                actualEntry = i
                break


        for n in range(actualEntry+1,len(temporaryEntries)):
            #print("Current index: " + str(n))
            try:
                entries.append(temporaryEntries[n])
            except:
                print("Error while adding entry number " + str(n) + " to the entries list.")

    else:
        entries = temporaryEntries

    print("Number of entries stored: " + str(len(entries)))

def quickSortTime(theEntries):
    """
    Simple quick sort algorithm to sort the incoming data when more than 1 stop is requested. Sorted by leaving time
    :param theEntries: list to be sorted, usually the bus entries
    :return: sorted list by departure time.
    """
    if len(theEntries) <= 1:
        return theEntries
    pivotVal = theEntries.pop()
    left = []
    right = []
    for i in range(0,len(theEntries)):
        if datetime.datetime.strptime(theEntries[i]['departureTime'] + " " + theEntries[i]['departureDate'],"%H:%M:%S %Y-%m-%d") <= datetime.datetime.strptime(pivotVal['departureTime'] + " " + pivotVal['departureDate'],"%H:%M:%S %Y-%m-%d"): #TODO: DO THE CONVERSION FOR BOTH!!
            left.append(theEntries[i])
        else:
            right.append(theEntries[i])
    return quickSortTime(left) + [pivotVal] + quickSortTime(right)

def deltaTime(timeOfDeparture):
    """
    :param timeOfDeparture: Time at which the bus is supposed to depart
    :return:(int)time left until departure
    """
    a = datetime.datetime.now()
    c = timeOfDeparture - a

    res = divmod(c.days * 86400 + c.seconds, 60)
    if res[0] > 59: #More than an hour
            return str(res[0]//60) + 'h'
    else: #If time left is less than an hour
        return str(res[0]+1) +'\''

def changeColorFromYellowToRed(id):
    """
    Animation for color transition
    :param id: Id of the element for which the color has to be changed, and animated
    :return: VOID
    """
    for i in range(0,len(yellowToRed),1):
        canvas.itemconfig(boundingBoxes[4+(id*6)],fill=yellowToRed[i])
        canvas.update()
        time.sleep(0.0050)

def changeColorFromGreenToYellow(id):
    """
    Animation for color transition
    :param id: Id of the element for which the color has to be changed, and animated
    :return: VOID
    """
    for i in range(0,len(greenToYellow),1):
        canvas.itemconfig(boundingBoxes[4+(id*6)],fill=greenToYellow[i])
        canvas.update()
        time.sleep(0.0050)


def updateTimeLeft():
    numberOfItemsToPopOffTop = 0
    #Loop through the items currently displayed, and update the time for all of them
    for itemDisplayed in range(0,4):
        newTimeLeftAsString = deltaTime(datetime.datetime.strptime(entries[itemDisplayed]['departureTime'] + " " + entries[itemDisplayed]['departureDate'],"%H:%M:%S %Y-%m-%d"))
        if '\'' in newTimeLeftAsString:
            newTimeLeft = int(newTimeLeftAsString[:-1])
        elif 'h' in newTimeLeftAsString:
            newTimeLeft = 60 #Dummy value


        if newTimeLeft <= 0:
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text='0')
            numberOfItemsToPopOffTop += 1
        elif newTimeLeft <= 1:
            if not (str(canvas.itemconfig(boundingBoxes[4+(itemDisplayed*6)])['fill'][4]).upper() == str(statusRed)):
                window.after(1,changeColorFromYellowToRed(itemDisplayed))
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeftAsString))
        elif newTimeLeft <= 2:
            if not (str(canvas.itemconfig(boundingBoxes[4+(itemDisplayed*6)])['fill'][4]).upper() == str(statusYellow)):
                window.after(1,changeColorFromGreenToYellow(itemDisplayed))
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeftAsString))
        else:
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeftAsString))

    #Pop the item(s) to be deleted. We do it here to handle multiple ones at once
    for i in range(0,numberOfItemsToPopOffTop):
        eliminateTop()
        #window.after(1,eliminateTop)

    global shouldFetchData
    if shouldFetchData == True:
        fetchNewDataForStation()
        shouldFetchData = False

    #Schedule the update after 10 seconds
    window.after(10000,updateTimeLeft)

def addBottomBarWithClock():
    """
    Add a bar at the bottom with the current time and date. Usually called in the setting up phase
    :return: VOID
    """
    global fullBottomBar

    #Add the overlay box to hide the redrawing
    fullBottomBar[0] = canvas.create_rectangle(0,heightOfScreen-115, widthOfScreen+10, heightOfScreen+10, fill="black")
    #Add the clock
    fullBottomBar[1] = canvas.create_text(widthOfScreen-paddingAroundBoxes-10,heightOfScreen-paddingAroundBoxes+5,text='hh:mm', font=('Helvetica Neue UltraLight',70),fill="white",anchor='se', tag='time')
    #Add the date
    fullBottomBar[2] = canvas.create_text(paddingAroundBoxes+10,heightOfScreen-paddingAroundBoxes+5,text='dd/mm/yyyy', font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='date')
    canvas.tag_raise(fullBottomBar)

def update_clock():
    """
    Function to update the clock to always display the correct time. Done by asking the system for the actual time.
    :return: VOID
    """
    global fullBottomBar
    global isBlinkTrue
    #Get current time
    currentDate = datetime.datetime.now()
    stringOfTime = datetime.datetime.strftime(currentDate,"%H:%M %d/%m/%Y")
    #split and get useful data
    currentTime = stringOfTime.split(" ")[0]
    currentDate = stringOfTime.split(" ")[1]
    # Blinking colon
    if isBlinkTrue == False:
        currentTime = currentTime.replace(":"," ")
    isBlinkTrue = not isBlinkTrue

    # Update the time and date
    canvas.itemconfig(fullBottomBar[1],text=currentTime)
    canvas.itemconfig(fullBottomBar[2],text=currentDate)
    # Call with delay
    window.after(1000,update_clock)

def main():
    # First of all get the updated data
    fetchNewDataForStation()
    # Create a window and canvas to display it all
    initWindow()
    # Add the bottom bar with the clock
    addBottomBarWithClock()
    #Start the updating process for the clock
    update_clock()
    # Add 4 items to the main view
    for i in range(0,4):
        addNewItemWithData(entries[i]['lineNumber'],entries[i]['destination'],entries[i]['originStation'],getCorrectLineColor(entries[i]['lineNumber'],entries[i]['operator']),i)
    # Update the times left until departure
    updateTimeLeft()

if __name__ == "__main__":
    main()

#DEBUG: Used when trying the animations
window.bind("<Right>", eliminateTopWithKey)

# Enter the infinite loop
window.mainloop()







