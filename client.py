import socket,select,pickle


def listHash(lis): #Returns the sum of the hash for a list
    res = 0
    for a in lis:
        if type(a)==list:
            res+=listHash(a)
        elif type(a)==int:
            res+=abs(a)
    return res


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.settimeout(30)
sock.connect(("10.20.0.8",3764))
print("Connected")
board = []
turns = []
moves = []

def zAdd(n):
    if len(str(n))==1:
        return "0"+str(n)
    return str(n)

running = False

while True:
    read,write,err = select.select([sock],[],[],0)
    for soc in read:
        if soc==sock:
            data = sock.recv(4096)
            mes = pickle.loads(data)
            sock.sendall(pickle.dumps(["r",listHash(mes)]))
            if mes[0]=="b":
                board = mes[1]
                moves = mes[2]
                turns = []
            elif mes[0]=="t" and not mes[1] in turns:
                turns.append(mes[1])
            elif mes[0]=="s" and not running: #Start the thing
                running = True
                file = open("comFile.txt","w")
                for x,a in enumerate(board):
                    for y,b in enumerate(a):
                        file.write(zAdd(b))
                    file.write("\n")
                file.write(str(mes[1])+"\n")
                file.write(str(mes[2])+"\n")
                for a in moves:
                    file.write(str(a[0])+str(a[1])+str(int(a[2])))
                file.write("\n")
                for a in turns:
                    if len(a[2])!=0:
                        file.write(str(a[0])+str(a[1]))
                        for b in a[2]:
                            if len(b)==3:
                                file.write(str(b[0])+str(b[1])+b[2])
                            else:
                                file.write(str(b[0])+str(b[1])+"0")
                        file.write("\n")
                file.close()
