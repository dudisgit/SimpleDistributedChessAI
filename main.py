from tkinter import *
from tkinter import ttk
import socket,select

#Classes
class Bot:
    def __init__(self):
        pass


#Variables
botList = [] #A list that contains all the bots online


#Tkinter stuff
main = Tk()
main.title("Distributed chess AI")
gside = Frame(main)
gBotL = Label(gside,text="Bots online")
gBotL.pack(side=TOP)
gBotScroll = ttk.Scrollbar(gside)
gBotList = Listbox(gside,yscrollcommand=gBotScroll.set)
gBotList.pack(side=LEFT,fill=Y,expand=True)
gBotScroll.config(command=gBotList.yview)
gBotScroll.pack(side=RIGHT,fill=Y)
gside.pack(side=RIGHT,fill=Y)



main.mainloop()