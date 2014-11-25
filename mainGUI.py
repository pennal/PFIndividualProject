from tkinter import *
import time








#OLD COLOR: SteelBlue2



# for i in range(0,4):
#     offset = i*heightOfSingleEntryBox
#     #boundingBoxes[i] = canvas.create_rectangle(paddingAroundBoxes, paddingAroundBoxes+offset, widthOfScreen-paddingAroundBoxes, heightOfSingleEntryBox+offset, outline="white",width=5)
#     #fillerRectangle =
#     boundingBoxes.append(canvas.create_rectangle(paddingAroundBoxes+10, paddingAroundBoxes+offset+10, 220, 220+offset, fill="red"))
#     #numberOfBus =
#     boundingBoxes.append(canvas.create_text(125,120+offset,text='n', font=('Helvetica Neue UltraLight',150),fill="white",anchor='center', tag='busNumber'))
#     #destination =
#     boundingBoxes.append(canvas.create_text(250,12+offset,text='Destination', font=('Helvetica Neue UltraLight',90),fill="white",anchor='nw', tag='destination'))
#     #leavingStation = \
#     boundingBoxes.append(canvas.create_text(250,230+offset,text='Origin', font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='leavingStation'))
#     #timeLeft = \
#     boundingBoxes.append(canvas.create_oval(widthOfScreen-paddingAroundBoxes-210, paddingAroundBoxes+offset+10, widthOfScreen-paddingAroundBoxes-10, 220+offset, fill="green"))




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

#
# def addItemAtBottom(event):
#     offset = 3*heightOfSingleEntryBox
#     #boundingBoxes[i] = canvas.create_rectangle(paddingAroundBoxes, paddingAroundBoxes+offset, widthOfScreen-paddingAroundBoxes, heightOfSingleEntryBox+offset, outline="white",width=5)
#     #fillerRectangle =
#     boundingBoxes.append(canvas.create_rectangle(paddingAroundBoxes+10, paddingAroundBoxes+offset+10, 220, 220+offset, fill="red"))
#     #numberOfBus =
#     boundingBoxes.append(canvas.create_text(125,120+offset,text='n', font=('Helvetica Neue UltraLight',150),fill="white",anchor='center', tag='busNumber'))
#     #destination =
#     boundingBoxes.append(canvas.create_text(250,12+offset,text='Destination', font=('Helvetica Neue UltraLight',90),fill="white",anchor='nw', tag='destination'))
#     #leavingStation = \
#     boundingBoxes.append(canvas.create_text(250,230+offset,text='Origin', font=('Helvetica Neue UltraLight',70),fill="white",anchor='sw', tag='leavingStation'))
#     #timeLeft = \
#     boundingBoxes.append(canvas.create_oval(widthOfScreen-paddingAroundBoxes-210, paddingAroundBoxes+offset+10, widthOfScreen-paddingAroundBoxes-10, 220+offset, fill="green"))

def changeStatus(event):
    canvas.itemconfig(boundingBoxes[4], fill="red") # change color





#
# topStackIsNum = boundingBoxes[0]
# # window.bind("<Left>", moveleft )
# window.bind("<Right>", eliminateTop)
# window.bind("<Up>", changeStatus)
# # window.bind("<Up>", moveup)
# # window.bind("<Down>", movedown)
#
#
#
# window.mainloop()