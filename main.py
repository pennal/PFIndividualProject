import requests#Used to request the data from the APIs
import json #Pretty print the incoming data
import time
import datetime
from tkinter import *
from threading import Timer

#GENERAL SETTINGS
apiURL = 'http://transport.opendata.ch/v1/stationboard' #base URL for the api
numberOfRequests = 100 #number of connections requested
forStation = ['Cornaredo']#['Ponte Madonnetta','Universita','Corso Elvezia']



#GLOBAL VARIABLES
isIdle = True

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

aBottomBar = 0
clock = 'hello'

window = Tk()
canvas = Canvas(window, width = widthOfScreen, height = heightOfScreen, bg = "black")
canvas.pack()

def getCorrectLineColor(lineNumber,company):
    try:
        if company == 'PAG':
            return colorLinePosta
        elif company == 'TPL':
            return colorLinesTPL[lineNumber]
        elif company == 'ARL':
            return colorLinesARL[lineNumber]
        elif company == 'SNL Auto':
            return colorLineSNL
    except:
        return 'red'

def addNewItemWithData(lineNumber,destination,origin,colorOfLine,position = 3):
    offset = position*heightOfSingleEntryBox

    if len(lineNumber) == 3:
        sizeOfChars = 100
    else:
        sizeOfChars = 150

    boundingBoxes.append(canvas.create_rectangle(paddingAroundBoxes+10, paddingAroundBoxes+offset+10, 220, 220+offset, fill=colorOfLine))
    boundingBoxes.append(canvas.create_text(125,120+offset,text=lineNumber, font=('Helvetica Neue UltraLight',sizeOfChars),fill="white",anchor='center', tag='busNumber'))
    boundingBoxes.append(canvas.create_text(250,12+offset,text=destination, font=('Helvetica Neue UltraLight',90),fill="white",anchor='nw', tag='destination'))
    boundingBoxes.append(canvas.create_text(250,230+offset,text=origin, font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='leavingStation'))
    boundingBoxes.append(canvas.create_oval(widthOfScreen-paddingAroundBoxes-210, paddingAroundBoxes+offset+10, widthOfScreen-paddingAroundBoxes-10, 220+offset, fill="green"))
    boundingBoxes.append(canvas.create_text(widthOfScreen-paddingAroundBoxes-110, paddingAroundBoxes+offset+100,text='1', font=('Helvetica Neue UltraLight',100),fill="white",anchor='center', tag='timeLeft'))

    global entryBeingDisplayed
    entryBeingDisplayed += 1
    #global aBottomBar
    #canvas.tag_raise(aBottomBar)

def eliminateTopWithKey(event):
    eliminateTop()

def eliminateTop():
    if isIdle == True:
        global isIdle
        isIdle = False
        global boundingBoxes
        global entries
        addNewItemWithData(entries[4]['lineNumber'],entries[4]['destination'],entries[4]['originStation'],getCorrectLineColor(entries[4]['lineNumber'],entries[4]['operator']),4)

        x = 0.5
        for i in range(40):
            for item in range(0,6):
                canvas.move(boundingBoxes[item],x,0)
                x +=0.5
            canvas.after(10)
            canvas.update()
        #Remove the top entry from the list of active elements
        print("Hi1")
        boundingBoxes = boundingBoxes[6:]
        print("Hi2")
        print(boundingBoxes)

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
            for item in range(0,5):
                    canvas.move(boundingBoxes[item+(6*group)],0,+3)

            canvas.after(10)
            canvas.update()
        #Remove from list of buses
        entries = entries[1:]
        isIdle = True
def fetchNewDataForStation():
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

def deltaTime(timeOfDeparture):
    a = datetime.datetime.now()
    c = timeOfDeparture - a
    res = divmod(c.days * 86400 + c.seconds, 60)
    if res[1] > 45:
        return res[0]+1
    else:
        return res[0]

# def addBottomBarWithClock():
#     global aBottomBar
#     global clock
#     #aBottomBar = canvas.create_rectangle(0,heightOfScreen-115, widthOfScreen, heightOfScreen, fill="#4F4F4F")
#     clock = Label(padx=widthOfScreen//2,pady=heightOfScreen//2,text='hello', font=('Helvetica Neue UltraLight',70),anchor='se')
#     clock.pack()
#     #canvas.tag_raise(aBottomBar)
#     canvas.tag_raise(clock)

# def update_clock():
#     global clock
#     now = time.strftime("%H:%M:%S")
#     clock.configure(text=now)
#     window.after(1000,update_clock)


def updateTimeLeft():
    print("IN")
    for itemDisplayed in range(0,4):
        newTimeLeft = deltaTime(datetime.datetime.strptime(entries[itemDisplayed]['departureTime'] + " " + entries[itemDisplayed]['departureDate'],"%H:%M:%S %Y-%m-%d"))
        if newTimeLeft <= 0:
            eliminateTop()
            itemDisplayed -= 1
        else:
            canvas.itemconfig(boundingBoxes[5+(itemDisplayed*6)],text=str(newTimeLeft))
    timerForTimeLeft = Timer(10.0,updateTimeLeft)
    timerForTimeLeft.start()


def main():
    fetchNewDataForStation()

    # addBottomBarWithClock()
    # update_clock()

    addNewItemWithData(entries[0]['lineNumber'],entries[0]['destination'],entries[0]['originStation'],getCorrectLineColor(entries[0]['lineNumber'],entries[0]['operator']),0)
    addNewItemWithData(entries[1]['lineNumber'],entries[1]['destination'],entries[1]['originStation'],getCorrectLineColor(entries[1]['lineNumber'],entries[1]['operator']),1)
    addNewItemWithData(entries[2]['lineNumber'],entries[2]['destination'],entries[2]['originStation'],getCorrectLineColor(entries[2]['lineNumber'],entries[2]['operator']),2)
    addNewItemWithData(entries[3]['lineNumber'],entries[3]['destination'],entries[3]['originStation'],getCorrectLineColor(entries[3]['lineNumber'],entries[3]['operator']),3)

    global entryBeingDisplayed
    entryBeingDisplayed = 0

    updateTimeLeft()




if __name__ == "__main__":


    main()


window.bind("<Right>", eliminateTopWithKey)

window.mainloop()