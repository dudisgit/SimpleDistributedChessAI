from tkinter import *
from tkinter import ttk
import tkinter.messagebox as box
import socket,select,math,pickle,time
from random import randint

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

def listHash(lis): #Returns the sum of the hash for a list
    res = 0
    for a in lis:
        if type(a)==list:
            res+=listHash(a)
        elif type(a)==int:
            res+=abs(a)
    return res

#Classes
class Bot:
    def __init__(self,socc):
        self.sock = socc
        self.name = "No-name"
    def send(self,lis): #Sends a message to the client, keeps sending until the client sends its hash back
        has = listHash(lis)
        pic = pickle.dumps(lis)
        while True:
            self.sock.send(pic)
            tWait = time.time()+0.04
            while time.time()<tWait:
                serverLoop(1)
            if lastMessage[0]=="r":
                if lastMessage[1]==has:
                    break

class ChessIcon: #Used for the visual element for the chess pieces
    def __init__(self):
        self.drawObj = -1
        self.__movefrom = [0,0] #Place to move from
        self.__moveto = [0,0] #Place to move to
        self.__movePercent = 0 #For smooth animation
        self.__canSave = None #Pointer to the canvas it is drawn to
    def draw(self,can):
        if self.getSide()!=0:
            self.__canSave = can
            self.drawObj = can.create_image((self.pos[0]*45)+22.5,(self.pos[1]*45)+22.5,image=phot[self.getType()*self.getSide()],
                                                tags=str(int(self.pos[0]))+","+str(int(self.pos[1])))
    def moveTo(self,pos): #Moves a piece to a coordinate in a smooth way
        self.__movePercent = 0
        self.__movefrom = [self.pos[0]+0,self.pos[1]+0] #Makes sure it isn't a pointer
        self.__moveto = pos
        board.inAnimation = True
        self.hasMoved = True
        self.__canSave.after(25,self.moveLoop)
    def moveLoop(self): #Animation loop
        self.__movePercent += 4.5
        self.pos = [ self.__movefrom[0] + ((self.__moveto[0]-self.__movefrom[0])*math.sin(self.__movePercent/180*math.pi)),
                     self.__movefrom[1] + ((self.__moveto[1]-self.__movefrom[1])*math.sin(self.__movePercent/180*math.pi))]
        self.move(self.__canSave)
        if self.__movePercent<90:
            self.__canSave.after(25,self.moveLoop)
        else:
            board.inAnimation = False
            self.pos = [self.__moveto[0]+0,self.__moveto[1]+0]
    def move(self,can):
        if self.getSide()!=0:
            self.__canSave = can
            can.itemconfig(self.drawObj,tags=str(int(self.pos[0]))+","+str(int(self.pos[1])))
            can.coords(self.drawObj,(self.pos[0]*45)+22.5,(self.pos[1]*45)+22.5)
    def delete(self):
        if self.drawObj!=-1:
            self.__canSave.delete(self.drawObj)
            self.drawObj = -1
    def reDraw(self): #Re-draws the piece
        self.__canSave.itemconfig(self.drawObj,image=phot[self.getType()*self.getSide()])
class PieceSelect:
    def __init__(self):
        self.tmp = Toplevel(main)
        self.tmp.grab_set()
        self.tmp.protocol("WM_DELETE_WINDOW",self.nothing)
        self.sel = 0
        self.lab = Label(self.tmp,text="Please select a piece")
        self.lab.pack(side=TOP)
        self.but1 = Button(self.tmp,image=phot[4],command=self.b1)
        self.but1.pack(side=LEFT)
        self.but2 = Button(self.tmp,image=phot[5],command=self.b2)
        self.but2.pack(side=LEFT)
        while self.sel==0:
            self.tmp.update()
        self.tmp.destroy()
    def nothing(self):
        pass
    def b1(self):
        self.sel = 4
    def b2(self):
        self.sel = 5

class ChessPiece(ChessIcon): #Used to reference each chess piece on the board
    def __init__(self,typ):
        super().__init__()
        self.__typ = typ
        self.pos = [-1,-1]
        self.__side = 0 #Unset
        self.hasMoved = False
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
        self.inAnimation = False #Is true when the board is currently animating a movement (to stop moving pieces while it is animating)
        self.undoList = []
        self.resetBoard()
    def resetBoard(self): #Resets the board back to starting positions
        for i in range(8):
            self.__board[i][1].setType(1)
            self.__board[i][6].setType(1)
        self.undoList = []
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
    def movePiece(self,x,y,tx,ty,dob): #Move a piece from (x,y) to (tx,ty)
        if x in range(8) and y in range(8) and tx in range(8) and ty in range(8):
            itm = self.__board[x].pop(y)
            self.__board[x].insert(y,ChessPiece(0))
            self.__board[tx][ty].delete()
            beft = self.__board[tx][ty].getType()
            self.__board[tx][ty] = itm
            if itm.getType()==1 and (ty==0 or ty==7):
                swi = PieceSelect()
                self.__board[tx][ty].setType(swi.sel)
                self.__board[tx][ty].reDraw()
                self.undoList.append([x,y,tx,ty,beft,"p"])
            elif dob:
                self.undoList.append([x,y,tx,ty,beft,"c"])
            else:
                self.undoList.append([x,y,tx,ty,beft])
            itm.moveTo([tx,ty])
    def isAttack(self,px,py): #Returns true if the piece is being attacked!
        #Rook or queen
        for y in range(py+1,8): #Down
            if self.__board[px][y].getType()!=0:
                if (self.__board[px][y].getType()==2 or self.__board[px][y].getType()==5) and self.__board[px][py].getSide()!=self.__board[px][y].getSide():
                    return True
                break
        for y in range(1,py+1): #Up
            if py-y<0:
                break
            if self.__board[px][py-y].getType()!=0:
                if (self.__board[px][py-y].getType()==2 or self.__board[px][py-y].getType()==5) and self.__board[px][py].getSide()!=self.__board[px][py-y].getSide():
                    return True
                break
        for x in range(px+1,8): #Right
            if self.__board[x][py].getType()!=0:
                if (self.__board[x][py].getType()==2 or self.__board[x][py].getType()==5) and self.__board[px][py].getSide()!=self.__board[x][py].getSide():
                    return True
                break
        for x in range(1,px+1): #Left
            if px-x<0:
                break
            if self.__board[px-x][py].getType()!=0:
                if (self.__board[px-x][py].getType()==2 or self.__board[px-x][py].getType()==5) and self.__board[px][py].getSide()!=self.__board[px-x][py].getSide():
                    return True
                break
        #Pawn
        if self.__board[px][py].getSide()==1 and py<7:
            if px>0:
                if self.__board[px-1][py+1].getType()==1 and self.__board[px-1][py+1].getSide()==-1:
                    return True
            if px<7:
                if self.__board[px+1][py+1].getType()==1 and self.__board[px+1][py+1].getSide()==-1:
                    return True
        elif self.__board[px][py].getSide()==-1 and py>0:
            if px>0:
                if self.__board[px-1][py-1].getType()==1 and self.__board[px-1][py-1].getSide()==1:
                    return True
            if px<7:
                if self.__board[px+1][py-1].getType()==1 and self.__board[px+1][py-1].getSide()==1:
                    return True
        #Bishop or queen
        for xy in range(1,8): #Down, Right
            if px+xy>7 or py+xy>7:
                break
            if self.__board[px+xy][py+xy].getType()!=0:
                if (self.__board[px+xy][py+xy].getType()==3 or self.__board[px+xy][py+xy].getType()==5) and self.__board[px+xy][py+xy].getSide()!=self.__board[px][py].getSide():
                    return True
                break
        for xy in range(1,8): #Up, Left
            if px-xy<0 or py-xy<0:
                break
            if self.__board[px-xy][py-xy].getType()!=0:
                if (self.__board[px-xy][py-xy].getType()==3 or self.__board[px-xy][py-xy].getType()==5) and self.__board[px-xy][py-xy].getSide()!=self.__board[px][py].getSide():
                    return True
                break
        for xy in range(1,8): #Down Left
            if px-xy<0 or py+xy>7:
                break
            if self.__board[px-xy][py+xy].getType()!=0:
                if (self.__board[px-xy][py+xy].getType()==3 or self.__board[px-xy][py+xy].getType()==5) and self.__board[px-xy][py+xy].getSide()!=self.__board[px][py].getSide():
                    return True
                break
        for xy in range(1,8): #Up, right
            if px+xy>7 or py-xy<0:
                break
            if self.__board[px+xy][py-xy].getType()!=0:
                if (self.__board[px+xy][py-xy].getType()==3 or self.__board[px+xy][py-xy].getType()==5) and self.__board[px+xy][py-xy].getSide()!=self.__board[px][py].getSide():
                    return True
                break
        #Knite
        if px-2>=0: #Left
            if py-1>=0:
                if self.__board[px-2][py-1].getType()==4 and self.__board[px-2][py-1].getSide()!=self.__board[px][py].getSide():
                    return True
            if py+1<=7:
                if self.__board[px-2][py+1].getType()==4 and self.__board[px-2][py+1].getSide()!=self.__board[px][py].getSide():
                    return True
        if px+2<=7: #Right
            if py-1>=0:
                if self.__board[px+2][py-1].getType()==4 and self.__board[px+2][py-1].getSide()!=self.__board[px][py].getSide():
                    return True
            if py+1<=7:
                if self.__board[px+2][py+1].getType()==4 and self.__board[px+2][py+1].getSide()!=self.__board[px][py].getSide():
                    return True
        if py-2>=0: #Up
            if px-1>=0:
                if self.__board[px-1][py-2].getType()==4 and self.__board[px-1][py-2].getSide()!=self.__board[px][py].getSide():
                    return True
            if px+1<=7:
                if self.__board[px+1][py-2].getType()==4 and self.__board[px+1][py-2].getSide()!=self.__board[px][py].getSide():
                    return True
        if py+2<=7: #Down
            if px-1>=0:
                if self.__board[px-1][py+2].getType()==4 and self.__board[px-1][py+2].getSide()!=self.__board[px][py].getSide():
                    return True
            if px+1<=7:
                if self.__board[px+1][py+2].getType()==4 and self.__board[px+1][py+2].getSide()!=self.__board[px][py].getSide():
                    return True
        #King
        for x in range(3):
            if px+(x-1)>=0 and px+(x-1)<=7:
                for y in range(3):
                    if py+(y-1)>=0 and py+(y-1)<=7:
                        if self.__board[px+(x-1)][py+(y-1)].getType()==6 and self.__board[px+(x-1)][py+(y-1)].getSide()!=self.__board[px][py].getSide():
                            return True
        return False #If no piece was found then it is not being attacked
    def getAllMoves(self,x,y): #Returns a list for all the possible moves for a piece
        moves = []
        pc = self.__board[x][y]
        typ = pc.getType()
        side = pc.getSide()
        if typ==1: #Pawn
            if pc.getSide()==1:
                if self.__board[x][y+1].getType()==0:
                    moves.append([x,y+1])
                if x>0:
                    if self.__board[x-1][y+1].getSide()==-1:
                        moves.append([x-1,y+1])
                if x<7:
                    if self.__board[x+1][y+1].getSide()==-1:
                        moves.append([x+1,y+1])
                if y==1:
                    if self.__board[x][2].getType()==0 and self.__board[x][3].getType()==0:
                        moves.append([x,3])
            else:
                if self.__board[x][y-1].getType()==0:
                    moves.append([x,y-1])
                if x>0:
                    if self.__board[x-1][y-1].getSide()==1:
                        moves.append([x-1,y-1])
                if x<7:
                    if self.__board[x+1][y-1].getSide()==1:
                        moves.append([x+1,y-1])
                if y==6:
                    if self.__board[x][5].getType()==0 and self.__board[x][4].getType()==0:
                        moves.append([x,4])
        if typ==2 or typ==5: #Rook or queen
            for px in range(x+1,8): #Left
                if self.__board[px][y].getType()==0:
                    moves.append([px+0,y+0])
                else:
                    if self.__board[px][y].getSide()!=side:
                        moves.append([px+0,y+0])
                    break
            for px in range(1,x+1): #Right
                if self.__board[x-px][y].getType()==0:
                    moves.append([x-px,y+0])
                else:
                    if self.__board[x-px][y].getSide()!=side:
                        moves.append([x-px,y+0])
                    break
            for py in range(1,y+1): #Up
                if self.__board[x][y-py].getType()==0:
                    moves.append([x+0,y-py])
                else:
                    if self.__board[x][y-py].getSide()!=side:
                        moves.append([x+0,y-py])
                    break
            for py in range(y+1,8): #Down
                if self.__board[x][py].getType()==0:
                    moves.append([x+0,py+0])
                else:
                    if self.__board[x][py].getSide()!=side:
                        moves.append([x+0,py+0])
                    break
        if typ==3 or typ==5: #Bishop or queen
            for xy in range(1,8): #Down, right
                if x+xy>7 or y+xy>7:
                    break
                if self.__board[x+xy][y+xy].getType()!=0:
                    if self.__board[x+xy][y+xy].getSide()!=side:
                        moves.append([x+xy,y+xy])
                    break
                else:
                    moves.append([x+xy,y+xy])
            for xy in range(1,8): #Down, left
                if x-xy<0 or y+xy>7:
                    break
                if self.__board[x-xy][y+xy].getType()!=0:
                    if self.__board[x-xy][y+xy].getSide()!=side:
                        moves.append([x-xy,y+xy])
                    break
                else:
                    moves.append([x-xy,y+xy])
            for xy in range(1,8): #Up, right
                if x+xy>7 or y-xy<0:
                    break
                if self.__board[x+xy][y-xy].getType()!=0:
                    if self.__board[x+xy][y-xy].getSide()!=self.__board[x][y].getSide():
                        moves.append([x+xy,y-xy])
                    break
                else:
                    moves.append([x+xy,y-xy])
            for xy in range(1,8): #Up, left
                if x-xy<0 or y-xy<0:
                    break
                if self.__board[x-xy][y-xy].getType()!=0:
                    if self.__board[x-xy][y-xy].getSide()!=side:
                        moves.append([x-xy,y-xy])
                    break
                else:
                    moves.append([x-xy,y-xy])
        if typ==4: #Knite
            if x-2>=0: #Left
                if y-1>=0:
                    if self.__board[x-2][y-1].getSide()!=side:
                        moves.append([x-2,y-1])
                if y+1<=7:
                    if self.__board[x-2][y+1].getSide()!=side:
                        moves.append([x-2,y+1])
            if x+2<=7: #Right
                if y-1>=0:
                    if self.__board[x+2][y-1].getSide()!=side:
                        moves.append([x+2,y-1])
                if y+1<=7:
                    if self.__board[x+2][y+1].getSide()!=side:
                        moves.append([x+2,y+1])
            if y-2>=0: #Up
                if x-1>=0:
                    if self.__board[x-1][y-2].getSide()!=side:
                        moves.append([x-1,y-2])
                if x+1<=7:
                    if self.__board[x+1][y-2].getSide()!=side:
                        moves.append([x+1,y-2])
            if y+2<=7: #Down
                if x-1>=0:
                    if self.__board[x-1][y+2].getSide()!=side:
                        moves.append([x-1,y+2])
                if x+1<=7:
                    if self.__board[x+1][y+2].getSide()!=side:
                        moves.append([x+1,y+2])
        if typ==6: #King
            for px in range(3):
                if x+(px-1)>=0 and x+(px-1)<=7:
                    for py in range(3):
                        if y+(py-1)>=0 and y+(py-1)<=7:
                            if self.__board[x+(px-1)][y+(py-1)].getSide()!=side:
                                moves.append([x+(px-1),y+(py-1)])
            if not pc.hasMoved: #Castling
                for px in range(x+1,8): #Right
                    if self.__board[px][y].getType()!=0:
                        if self.__board[px][y].getType()==2 and self.__board[px][y].getSide()==side and not self.__board[px][y].hasMoved:
                            moves.append([px+0,y+0,"c"])
                        break
                for px in range(1,x+1): #Left
                    if self.__board[x-px][y].getType()!=0:
                        if self.__board[x-px][y].getType()==2 and self.__board[x-px][y].getSide()==side and not self.__board[x-px][y].hasMoved:
                            moves.append([x-px,y+0,"c"])
                        break
        #Loop through each move and test to see if one will get the player in check, if yes then remove them
        kingPos = [-1,-1]
        for px,a in enumerate(self.__board): #Find the kind on the board
            for py,b in enumerate(a):
                if b.getType()==6 and b.getSide()==side:
                    kingPos = [px+0,py+0]
                    break
            if kingPos[0]!=-1:
                break
        if kingPos[0]==-1:
            print("Error, king was not found on the board!")
            return 0
        rem = []
        for a in moves:
            if typ==6:
                kingPos = [a[0],a[1]]
            if len(a)==3:
                if a[2]=="c": #Castle
                    to = self.__board[a[0]].pop(a[1])
                    self.__board[a[0]].insert(a[1],ChessPiece(0))
                    hold = self.__board[x].pop(y)
                    self.__board[x].insert(y,ChessPiece(0))
                    if a[0]==0: #Right
                        self.__board[2][y] = hold
                        kingPos = [2,y+0]
                        self.__board[3][y] = to
                    else:
                        self.__board[6][y] = hold
                        kingPos = [6,y+0]
                        self.__board[5][y] = to
                    if self.isAttack(kingPos[0],kingPos[1]):
                        rem.append(a)
                    if a[0]==0:
                        hold = self.__board[2].pop(y)
                        self.__board[2].insert(y,ChessPiece(0))
                        to = self.__board[3].pop(y)
                        self.__board[3].insert(y,ChessPiece(0))
                        self.__board[4][y] = hold
                        self.__board[0][y] = to
                    else:
                        hold = self.__board[6].pop(y)
                        self.__board[6].insert(y,ChessPiece(0))
                        to = self.__board[5].pop(y)
                        self.__board[5].insert(y,ChessPiece(0))
                        self.__board[4][y] = hold
                        self.__board[7][y] = to
            else:
                to = self.__board[a[0]].pop(a[1]) #Pop out the piece at the location it is moving to
                self.__board[a[0]].insert(a[1],ChessPiece(0))
                hold = self.__board[x].pop(y) #Pop out the piece at the location it is moving from
                self.__board[x].insert(y,ChessPiece(0)) #Insert an empty piece into the location from
                self.__board[a[0]][a[1]] = hold
                if self.isAttack(kingPos[0],kingPos[1]): #Is the kind in check??
                    rem.append(a)
                hold = self.__board[a[0]].pop(a[1])
                self.__board[a[0]].insert(a[1],to)
                self.__board[x][y] = hold
        for a in rem:
            moves.remove(a)
        return moves
    def inCheck(self,side): #Returns true if a side is in check
        for x,a in enumerate(self.__board):
            for y,b in enumerate(a):
                if b.getType()==6 and b.getSide()==side:
                    return self.isAttack(x,y)
    def undoMove(self,*res): #Undus a move
        if len(self.undoList)==0:
            return 0
        l = self.undoList.pop()
        if len(l)==5:
            hold = self.__board[l[2]].pop(l[3])
            self.__board[l[2]].insert(l[3],ChessPiece(l[4]))
            if l[4]!=0:
                self.__board[l[2]][l[3]].setSide(hold.getSide()*-1)
                self.__board[l[2]][l[3]].pos = [l[2],l[3]]
                self.__board[l[2]][l[3]].draw(draw)
            self.__board[l[0]][l[1]] = hold
            hold.moveTo([l[0],l[1]])
            if len(res)!=0:
                hold.hasMoved = False
        else:
            if l[5]=="p": #Was ones a pawn
                hold = self.__board[l[2]].pop(l[3])
                hold.delete()
                self.__board[l[2]].insert(l[3],ChessPiece(0))
                self.__board[l[0]][l[1]] = ChessPiece(1)
                self.__board[l[0]][l[1]].pos = [l[2],l[3]]
                self.__board[l[0]][l[1]].setSide(hold.getSide())
                self.__board[l[0]][l[1]].draw(draw)
                self.__board[l[0]][l[1]].moveTo([l[0],l[1]])
            elif l[5]=="c": #A castle was taken place
                self.undoList.append(l[:5])
                self.undoMove(1)
                self.undoMove(1)
        deSelectAll()
    def totalMove(self,side): #Returns ALL the possible moves for the player
        res = []
        for x,a in enumerate(self.__board):
            for y,b in enumerate(a):
                if b.getSide()==side:
                    res.append([x+0,y+0,self.getAllMoves(x,y)])
        return res
    def givePickle(self): #Returns the whole board ready to be converted to pickle
        lis = []
        mvs = []
        for x,a in enumerate(self.__board):
            lis.append([])
            for y,b in enumerate(a):
                lis[x].append(b.getType()*b.getSide())
                if b.getType()==2 or b.getType()==6:
                    mvs.append([x+0,y+0,b.hasMoved])
        return ["b",lis,mvs]

def simulateTurn(side):
    if len(botList)==0:
        return 0
    gStatus.config(text="Getting moves...")
    main.update()
    goes = board.totalMove(side)
    gStatus.config(text="Splitting...")
    main.update()
    split = [[]]*len(botList)
    end = 0
    cur = 0
    for a in goes:
        split[cur].append(a)
        end+=1
        if end>len(goes)/len(botList):
            end=0
            cur+=1
    gStatus.config(text="Sending...")
    main.update()
    brd = board.givePickle()
    for i,a in enumerate(split):
        botList[i].send(brd) #Send the board
        time.sleep(0.1) #Wait an amount of time for the message to send fully
        for i2,b in enumerate(a):
            botList[i].send(["t",b])
            gProg["value"] = ((i+(i2/len(a)))/len(split))*100
            main.update()
            time.sleep(0.03)
        botList[i].send(["s",3,side]) #3 is the search depth
        gProg["value"] = (i/len(split))*100
        gStatus.config(text="Sending... ("+str(i)+"/"+str(len(split))+")")
        main.update()
    gProg["value"] = 0
    gStatus.config(text="Nothings happening")



def undoMove(): #Undus a move
    board.undoMove()
    pMove = [board.totalMove(-1),board.totalMove(1)]
    ln1 = 0
    ln2 = 0
    for a in pMove[0]:
        ln1+=len(a[2])
    for a in pMove[1]:
        ln2+=len(a[2])
    gStatus.config(text="Nothings happening")
    if board.inCheck(1):
        gStatus.config(text="White is in check")
    elif board.inCheck(-1):
        gStatus.config(text="Black is in check")
    if ln1==0:
        gStatus.config(text="White wins!")
    elif ln2==0:
        gStatus.config(text="Black wins!")
def drawAll(): #Draws everything to the canvas
    draw.delete(ALL)
    for xy in range(1,8):
        draw.create_line(xy*45,0,xy*45,360)
        draw.create_line(0,xy*45,360,xy*45)
    board.callAll("draw",draw)
def deSelectAll(): #De-selects all pieces
    if sele[0]:
        sele[0] = False
        for a in sele[2]:
            draw.delete(a)
        sele[2] = []
def click(ev): #The mouse was clicked
    global pMove
    if board.inAnimation:
        return 0
    clos = draw.find_closest(ev.x,ev.y)
    tag = draw.gettags(clos)
    if len(tag)!=0:
        did = True
        if "," in tag[0]:
            deSelectAll()
            spl = tag[0].split(",")
            if len(spl)>=2:
                if spl[0].isnumeric() and spl[1].isnumeric():
                    sele[0] = True
                    sele[1] = [int(spl[0])+0,int(spl[1])+0]
                    mvs = board.getAllMoves(int(spl[0]),int(spl[1]))
                    for a in mvs:
                        if len(a)==3:
                            sele[2].append(draw.create_oval((a[0]*45)+10,(a[1]*45)+10,(a[0]*45)+35,(a[1]*45)+35,outline="",fill="green",
                                                                tags=str(a[0])+"x"+str(a[1])+"x"+a[2]))
                        else:
                            sele[2].append(draw.create_oval((a[0]*45)+10,(a[1]*45)+10,(a[0]*45)+35,(a[1]*45)+35,outline="",fill="green",
                                                                tags=str(a[0])+"x"+str(a[1])))
        elif "x" in tag[0] and sele[0]:
            spl = tag[0].split("x")
            if len(spl)>=2:
                if spl[0].isnumeric() and spl[1].isnumeric():
                    if len(spl)==3:
                        if spl[2]=="c": #Castle
                            if int(spl[0])==0:
                                board.movePiece(sele[1][0],sele[1][1],2,sele[1][1],False)
                                board.movePiece(int(spl[0]),int(spl[1]),3,int(spl[1]),True)
                            else:
                                board.movePiece(sele[1][0],sele[1][1],6,sele[1][1],False)
                                board.movePiece(int(spl[0]),int(spl[1]),5,int(spl[1]),True)
                    else:
                        board.movePiece(sele[1][0],sele[1][1],int(spl[0]),int(spl[1]),False)
            deSelectAll()
        else:
            did = False
            deSelectAll()
        if did:
            pMove = [board.totalMove(-1),board.totalMove(1)]
            ln1 = 0
            ln2 = 0
            for a in pMove[0]:
                ln1+=len(a[2])
            for a in pMove[1]:
                ln2+=len(a[2])
            gStatus.config(text="Nothings happening")
            if board.inCheck(1):
                gStatus.config(text="White is in check")
            elif board.inCheck(-1):
                gStatus.config(text="Black is in check")
            if ln1==0:
                gStatus.config(text="White wins!")
            elif ln2==0:
                gStatus.config(text="Black wins!")
    else:
        deSelectAll()
def resetBoard():
    if box.askyesno(title="Reset board",message="Are you sure you want to reset the board?"):
        board.resetBoard()
        deSelectAll()
        drawAll()

def serverLoop(*can):
    global lastMessage
    read,write,err = select.select(sockList,[],[],0)
    for soc in read:
        if soc==sock: #New connection
            con,addr = sock.accept()
            sockList.append(con)
            botList.append(Bot(con))
            try:
                botList[-1].name = socket.gethostbyaddr(addr[0])
            except:
                botList[-1].name = addr[0]
            gBotList.insert(END,botList[-1].name)
        else:
            try:
                data = soc.recv(4096)
                if data:
                    d = pickle.loads(data)
                    lastMessage = d
                else:
                    print("Error reading infomation")
            except:
                raise
    if len(can)==0:
        main.after(1,serverLoop)




#Variables
botList = [] #A list that contains all the bots online
phot = {}
board = ChessBoard()
sele = [False,[-1,-1],[]]
pMove = [[],[]] #A list for all the possible moves for both players
lastMessage = [] #The last message that was received

#Tkinter stuff
main = Tk()
main.title("Distributed chess AI")
main.resizable(width=FALSE, height=FALSE)

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

gBotm = Frame(main)
gUndo = ttk.Button(gBotm,text="Undo move",command=undoMove)
gUndo.pack(side=LEFT)
gReset = ttk.Button(gBotm,text="Reset",command=resetBoard)
gReset.pack(side=LEFT)
gProg = ttk.Progressbar(gBotm,mode='determinate',orient=HORIZONTAL)
gProg.pack(side=RIGHT,fill=X,expand=True)

gBotM = Frame(main)
gSimB = ttk.Button(gBotM,text="Simulate black's turn",command=lambda: simulateTurn(-1))
gSimB.pack(side=LEFT)
gSimW = ttk.Button(gBotM,text="Simulate white's turn",command=lambda: simulateTurn(1))
gSimW.pack(side=LEFT)
gStatus = ttk.Label(gBotM,text="Nothings happening")
gStatus.pack(side=LEFT)
gBotM.pack(side=BOTTOM,fill=X)

gBotm.pack(side=BOTTOM,fill=X)

draw = Canvas(main,width=360,height=360,bg="white")
draw.bind("<Button-1>",click)
draw.pack(side=LEFT)
draw.phot = phot
drawAll()

ip = socket.gethostbyname(socket.gethostname())
port = 3764

sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
sock.bind((ip,port))
sock.listen(60)
sockList = [sock]
print("Binded to ip "+ip+" on port "+str(port))

main.after(10,serverLoop)
main.mainloop()