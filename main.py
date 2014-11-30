# -*- coding: utf-8 -*-
import requests         #Used to request the data from the APIs
import json             #Pretty print the incoming data
import datetime         #Used to calculate the time left for a certain bus
import time             #Used for some delays
from customGUI import *
import sys              #Used to abort the script




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
forStation = ['Ponte Madonnetta','Universita']



#GLOBAL VARIABLES
#Is the main APP idle? Used to avoid overlapping events
isIdle = True
#Watch colon blink "counter", used to actually make the symbol blink
isBlinkTrue = True
#Trigger to fetch new data
shouldFetchData = False
#Variable to hold all entries
entries = []







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
    Simple quick sort algorithm to sort the incoming data when more than 1 stop is requested
    :param theEntries: list to be sorted, usually the bus entries
    :return: sorted list.
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



def changeColorFromYellowToRed(id):
    for i in range(0,len(yellowToRed),1):
        canvas.itemconfig(boundingBoxes[4+(id*6)],fill=yellowToRed[i])
        canvas.update()
        time.sleep(0.0050)

def changeColorFromGreenToYellow(id):
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

    initWindow()

    #addBottomBarWithClock()
    #update_clock()
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







