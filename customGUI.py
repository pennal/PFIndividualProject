from tkinter import *   #All for the GUI
import colorGenerator
import colorGenerator   #Importing the file to generate color transitions
import datetime




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

#Hardwired for now, should be fixed in a later version
heightOfScreen = 1050
widthOfScreen = 1680

#Constants used to display the elements on the gui
heightOfSingleEntryBox = 230
paddingAroundBoxes = 20
widthOfOutlineOfEntryBox = 5
#Holds all the IDs for the GUI elements
boundingBoxes = []

window = 0
canvas = 0

def initWindow():
    global window
    global canvas
    #Create the main window
    window = Tk()
    window.title("Bus Schedule")
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

        shouldFetchData = False

        if len(entries) < 10:
            print("fetching new data")
            shouldFetchData = True

        isIdle = True


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