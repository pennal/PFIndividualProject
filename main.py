import requests#Used to request the data from the APIs
import json #Pretty print the incoming data
import time
import datetime
from tkinter import *


print("After")
#GENERAL SETTINGS
apiURL = 'http://transport.opendata.ch/v1/stationboard' #base URL for the api
numberOfRequests = 10 #number of connections requested
forStation = ['Ponte Madonnetta','Universita','Corso Elvezia']

entries = []

#GLOBAL VARIABLES
heightOfScreen = 1050
widthOfScreen = 1680


heightOfSingleEntryBox = 230
paddingAroundBoxes = 20
widthOfOutlineOfEntryBox = 5

boundingBoxes = []


topStackIsNum = 0
colorLinesDict = {
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
    '461':'red'
}

window = Tk()
canvas = Canvas(window, width = widthOfScreen, height = heightOfScreen, bg = "black")
canvas.pack()

def addNewItemWithData(lineNumber,destination,origin,colorOfLine):
    offset = 3*heightOfSingleEntryBox
    #boundingBoxes[i] = canvas.create_rectangle(paddingAroundBoxes, paddingAroundBoxes+offset, widthOfScreen-paddingAroundBoxes, heightOfSingleEntryBox+offset, outline="white",width=5)
    #fillerRectangle =
    boundingBoxes.append(canvas.create_rectangle(paddingAroundBoxes+10, paddingAroundBoxes+offset+10, 220, 220+offset, fill=colorOfLine))
    #numberOfBus =
    boundingBoxes.append(canvas.create_text(125,120+offset,text=lineNumber, font=('Helvetica Neue UltraLight',150),fill="white",anchor='center', tag='busNumber'))
    #destination =
    boundingBoxes.append(canvas.create_text(250,12+offset,text=destination, font=('Helvetica Neue UltraLight',90),fill="white",anchor='nw', tag='destination'))
    #leavingStation = \
    boundingBoxes.append(canvas.create_text(250,230+offset,text=origin, font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='leavingStation'))
    #timeLeft = \
    boundingBoxes.append(canvas.create_oval(widthOfScreen-paddingAroundBoxes-210, paddingAroundBoxes+offset+10, widthOfScreen-paddingAroundBoxes-10, 220+offset, fill="green"))

def eliminateTop(event):
    global boundingBoxes

    #Add next item
    offset = 4*heightOfSingleEntryBox
    #boundingBoxes[i] = canvas.create_rectangle(paddingAroundBoxes, paddingAroundBoxes+offset, widthOfScreen-paddingAroundBoxes, heightOfSingleEntryBox+offset, outline="white",width=5)
    #fillerRectangle =
    boundingBoxes.append(canvas.create_rectangle(paddingAroundBoxes+10, paddingAroundBoxes+offset+10, 220, 220+offset, fill="red"))
    #numberOfBus =
    boundingBoxes.append(canvas.create_text(125,120+offset,text='n', font=('Helvetica Neue UltraLight',150),fill="white",anchor='center', tag='busNumber'))
    #destination =
    boundingBoxes.append(canvas.create_text(250,12+offset,text='Destination', font=('Helvetica Neue UltraLight',90),fill="white",anchor='nw', tag='destination'))
    #leavingStation = \
    boundingBoxes.append(canvas.create_text(250,230+offset,text='Origin', font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='leavingStation'))
    #timeLeft = \
    boundingBoxes.append(canvas.create_oval(widthOfScreen-paddingAroundBoxes-210, paddingAroundBoxes+offset+10, widthOfScreen-paddingAroundBoxes-10, 220+offset, fill="green"))







    x = 0.5
    for i in range(40):
        for item in range(0,5):
            canvas.move(boundingBoxes[item],x,0)
            x +=0.5
        canvas.after(10)
        canvas.update()
    #Remove the top entry from the list of active elements
    boundingBoxes = boundingBoxes[5:]
    print(boundingBoxes)

    for group in range(0,len(boundingBoxes)//5):
        i = 0
        x=0
        for i in range(31):
            for item in range(0,5):
                canvas.move(boundingBoxes[item+(5*group)],0,x)
            x-=1/2
            canvas.after(10)
            canvas.update()
        #compensate a bit, TODO: remove
        for item in range(0,5):
                canvas.move(boundingBoxes[item+(5*group)],0,+3)

        canvas.after(10)
        canvas.update()


def fetchNewDataForStation():
    print("in")
    global entries
    for station in range(0,len(forStation)):
        #remove all spaces from the name of the starting station
        forStationURL = forStation[station].replace(" ","%20")

        #Get the data from the URL
        response = requests.get(apiURL + '?station=' + forStationURL + '&limit=' + str(numberOfRequests))
        #DEBUG: Pretty print the incoming data
        #print(response.text)
        data = json.loads(response.text)
        #print(json.dumps(data,indent=4))
        #Clean up the data, and extract all we need
        for entry in range(0,len(data["stationboard"])):
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
            entries.append({
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

    print(json.dumps(entries,indent=4))


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
        if theEntries <= pivotVal: #TODO: DO THE CONVERSION FOR BOTH!!
            left.append(theEntries[i])
        else:
            right.append(theEntries[i])
    return quickSortTime(left) + [pivotVal] + quickSortTime(right)


def main():


    fetchNewDataForStation()



    addNewItemWithData(entries[2]['lineNumber'],entries[2]['destination'],entries[2]['originStation'],colorLinesDict[entries[2]['lineNumber']])

if __name__ == "__main__":


    main()


window.mainloop()