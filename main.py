from tkinter import *
from tkinter import ttk
import socket,select

#ID's
#0: Empty
#1: Pawn
#2: Rook
#3: Bishop
#4: Knite
#5: Queen
#6: King

#Players
#+: White
#-: Black

#Classes
class Bot:
    def __init__(self):
        pass
class ChessIcon: #Used for the visual element for the chess pieces
    def draw(self,can):
        if self.getSide()!=0:
            self.drawObj = can.create_image((self.pos[0]*45)+22.5,(self.pos[1]*45)+22.5,image=phot[self.getType()*self.getSide()])

class ChessPiece(ChessIcon): #Used to reference each chess piece on the board
    def __init__(self,typ):
        self.__typ = typ
        self.pos = [-1,-1]
        self.__side = 0 #Unset
    def setType(self,typ): #Change the type of the Chess piece
        if typ in range(0,7):
            self.__typ = typ
    def setSide(self,side): #Change who the chess piece belongs to
        if side==-1 or side==0 or side==1:
            self.__side = side
    def getType(self): #Returns the type of piece this is
        return self.__typ
    def getSide(self): #Returns what side the piece is on
        return self.__side
class ChessBoard: #A chess board to interact with
    def __init__(self):
        self.__board = []
        for x in range(8):
            self.__board.append([])
            for y in range(8):
                self.__board[x].append(ChessPiece(0))
        self.resetBoard()
    def resetBoard(self): #Resets the board back to starting positions
        for i in range(8):
            self.__board[i][1].setType(1)
            self.__board[i][6].setType(1)
        self.__board[0][0].setType(2)
        self.__board[7][0].setType(2)
        self.__board[0][7].setType(2)
        self.__board[7][7].setType(2)
        self.__board[1][0].setType(4)
        self.__board[6][0].setType(4)
        self.__board[1][7].setType(4)
        self.__board[6][7].setType(4)
        self.__board[2][0].setType(3)
        self.__board[5][0].setType(3)
        self.__board[2][7].setType(3)
        self.__board[5][7].setType(3)
        self.__board[3][0].setType(5)
        self.__board[4][0].setType(6)
        self.__board[3][7].setType(5)
        self.__board[4][7].setType(6)
        for x in range(8):
            for y in range(8):
                self.__board[x][y].pos = [x,y]
                if y<2:
                    self.__board[x][y].setSide(1)
                elif y>5:
                    self.__board[x][y].setSide(-1)
                else:
                    self.__board[x][y].setSide(0)
                    self.__board[x][y].setType(0)
    def callAll(self,func,*params): #Calls 'func' on every piece on the board
        for x in self.__board:
            for y in x:
                callObj = getattr(y,func)
                callObj(*params)

def drawAll(): #Draws everything to the canvas
    draw.delete(ALL)
    for xy in range(1,8):
        draw.create_line(xy*45,0,xy*45,360)
        draw.create_line(0,xy*45,360,xy*45)
    board.callAll("draw",draw)


#Variables
botList = [] #A list that contains all the bots online
phot = {}
board = ChessBoard()

#Tkinter stuff
main = Tk()
main.title("Distributed chess AI")

phot[1]=PhotoImage(file="Pieces/1.png")
phot[2]=PhotoImage(file="Pieces/2.png")
phot[3]=PhotoImage(file="Pieces/3.png")
phot[4]=PhotoImage(file="Pieces/4.png")
phot[5]=PhotoImage(file="Pieces/5.png")
phot[6]=PhotoImage(file="Pieces/6.png")
phot[-1]=PhotoImage(file="Pieces/-1.png")
phot[-2]=PhotoImage(file="Pieces/-2.png")
phot[-3]=PhotoImage(file="Pieces/-3.png")
phot[-4]=PhotoImage(file="Pieces/-4.png")
phot[-5]=PhotoImage(file="Pieces/-5.png")
phot[-6]=PhotoImage(file="Pieces/-6.png")
for a in phot:
    phot[a] = phot[a].subsample(7,7)

gside = Frame(main)
gBotL = Label(gside,text="Bots online")
gBotL.pack(side=TOP)
gBotScroll = ttk.Scrollbar(gside)
gBotList = Listbox(gside,yscrollcommand=gBotScroll.set)
gBotList.pack(side=LEFT,fill=Y,expand=True)
gBotScroll.config(command=gBotList.yview)
gBotScroll.pack(side=RIGHT,fill=Y)
gside.pack(side=RIGHT,fill=Y)

draw = Canvas(main,width=360,height=360,bg="white")
draw.pack(side=LEFT)
draw.phot = phot
drawAll()

main.mainloop()