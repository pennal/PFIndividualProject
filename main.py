# -*- coding: utf-8 -*-
import requests#Used to request the data from the APIs
import json #Pretty print the incoming data
import datetime
from tkinter import *
import sys


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
apiURL = 'http://transport.opendata.ch/v1/stationboard' #base URL for the api
numberOfRequests = 30 #number of connections requested
forStation = ['Ponte Madonnetta','Universita']



#GLOBAL VARIABLES
isIdle = True
isBlinkTrue = True
entries = [] #Variable to hold all entries
heightOfScreen = 1050
widthOfScreen = 1680
heightOfSingleEntryBox = 230
paddingAroundBoxes = 20
widthOfOutlineOfEntryBox = 5

boundingBoxes = []

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

colorLinePosta = '#FEC213'
colorLineSNL = '#0B255A'
colorLinesARL = {
    '461':'#FFEB04',
    '441':'#3FB454',
    '60':'#9600F6'
}

entryBeingDisplayed = 0

fullBottomBar = ['','','']
clock = 'hello'

statusRed = '#CC0605'
statusYellow = '#FFBE00'
statusGreen = '#27E833'
window = Tk()
canvas = Canvas(window, width = widthOfScreen, height = heightOfScreen, bg = "black")
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


    #global fullBottomBar
    #canvas.tag_raise(fullBottomBar)

#TODO:Remove this, only for debugging purposes
def eliminateTopWithKey(event):
    eliminateTop()

def eliminateTop():
    """
    Used when the first item has to be deleted off the top. It takes care of sliding the entry out of the way, as well
    as generating a new entry. The list containing all the indexes is also updated and truncated.
    :return: VOID
    """
    if isIdle == True:
        global isIdle
        isIdle = False
        global boundingBoxes
        global entries
        global canvas
        addNewItemWithData(entries[4]['lineNumber'],entries[4]['destination'],entries[4]['originStation'],getCorrectLineColor(entries[4]['lineNumber'],entries[4]['operator']),4)
        #Bring the bottom bar to the top of the view
        canvas.tag_raise(fullBottomBar[0])
        canvas.tag_raise(fullBottomBar[1])
        canvas.tag_raise(fullBottomBar[2])
        x = 0.5
        for i in range(40):
            for item in range(0,6):
                canvas.move(boundingBoxes[item],x,0)
                x +=0.5
            canvas.after(10)
            canvas.update()
        #Remove the top entry from the list of active elements
        boundingBoxes = boundingBoxes[6:]

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
        isIdle = True

def fetchNewDataForStation():
    global entries
    #Create a temp dict to hold the data
    temporaryEntries = []
    for station in range(0,len(forStation)):
        #remove all spaces from the name of the starting station
        forStationURL = forStation[station].replace(" ","%20")
        try:
            #Get the data from the URL
            response = requests.get(apiURL + '?station=' + forStationURL + '&limit=' + str(numberOfRequests))
        except:
            print("COULD NOT CONNECT TO THE NETWORK")
            sys.exit()
        #DEBUG: Pretty print the incoming data
        #print(response.text)
        data = json.loads(response.text)
        try:
            amountOfData = len(data["stationboard"])
        except KeyError:
            print("Error: Could not find key. Might be a timeout issue, reopen the program")
            sys.exit()
        except:
            print("Unknown error occured")
            sys.exit()

        #Clean up the data, and extract all we need
        for entry in range(0,amountOfData):
            originStation = data["station"]["name"]
            destination = data["stationboard"][entry]["to"]
            lineNumber = data["stationboard"][entry]["number"]
            #Split the time and date
            departureTimeTemp = data["stationboard"][entry]["stop"]["departure"].split("T")
            departureDate = departureTimeTemp[0]
            departureTime = departureTimeTemp[1].split("+")[0]#Remove the greenwich delta

            #TODO: Find the difference in time (timeDelta)
            timeDelta = 60

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
                'operator':operator,
                'timeDelta':timeDelta
            })

    #Sort the dictionary by keys
    temporaryEntries = quickSortTime(temporaryEntries)



    entries = temporaryEntries





def sortByTime():
    global entries
    entries = quickSortTime(entries)

def quickSortTime(theEntries):
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
        if res[1] > 45:
            return str(res[0]+1) +'\''
        else:
            return str(res[0]) +'\''

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
            canvas.itemconfig(boundingBoxes[4+(itemDisplayed*6)],fill=statusRed)
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeftAsString))
        elif newTimeLeft <= 2:
            canvas.itemconfig(boundingBoxes[4+(itemDisplayed*6)],fill=statusYellow)
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeftAsString))
        else:
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeftAsString))

    #Pop the item(s) to be deleted. We do it here to handle multiple ones at once
    for i in range(0,numberOfItemsToPopOffTop):
        eliminateTop()


    #Schedule the update after 10 seconds
    window.after(10000,updateTimeLeft)

def addBottomBarWithClock():
    global fullBottomBar
    global clock
    #Add the overlay box to hide the redrawing
    fullBottomBar[0] = canvas.create_rectangle(0,heightOfScreen-115, widthOfScreen+10, heightOfScreen+10, fill="black")
    #Add the clock
    fullBottomBar[1] = canvas.create_text(widthOfScreen-paddingAroundBoxes-10,heightOfScreen-paddingAroundBoxes,text='hh:mm', font=('Helvetica Neue UltraLight',70),fill="white",anchor='se', tag='time')
    #Add the date
    fullBottomBar[2] = canvas.create_text(paddingAroundBoxes+10,heightOfScreen-paddingAroundBoxes,text='dd/mm/yyyy', font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='date')
    canvas.tag_raise(fullBottomBar)

def update_clock():
    global fullBottomBar
    global isBlinkTrue
    #Get current time
    currentDate = datetime.datetime.now()
    stringOfTime = datetime.datetime.strftime(currentDate,"%H:%M %d/%m/%Y")

    currentTime = stringOfTime.split(" ")[0]
    currentDate = stringOfTime.split(" ")[1]

    if isBlinkTrue == False:
        currentTime = currentTime.replace(":"," ")
    isBlinkTrue = not isBlinkTrue

    canvas.itemconfig(fullBottomBar[1],text=currentTime)
    canvas.itemconfig(fullBottomBar[2],text=currentDate)
    window.after(1000,update_clock)

def main():
    fetchNewDataForStation()

    addBottomBarWithClock()
    update_clock()
    for i in range(0,4):
        addNewItemWithData(entries[i]['lineNumber'],entries[i]['destination'],entries[i]['originStation'],getCorrectLineColor(entries[i]['lineNumber'],entries[i]['operator']),i)


    global entryBeingDisplayed
    entryBeingDisplayed = 0

    updateTimeLeft()

if __name__ == "__main__":
    main()

#TODO:Remove this, only for debugging purposes
window.bind("<Right>", eliminateTopWithKey)

window.mainloop()







