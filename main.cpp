#include <iostream>
#include <fstream>
#include <string>
#include <sstream>

using namespace std;

int board[8][8], depth=2;
string moves=""; //A list of rooks and kings to detect if they where moved or not

//1 - Pawn
//2 - Rook
//3 - Bishop
//4 - Knite
//5 - Queen
//6 - King
//Special
//0 - None
//1 - Castle
//2 - Pawn got to the end

int toNumber(string str) //Converts a string to a number
{
    bool neg=false;
    int res=0, i=0;
    string scan;
    scan = str+'E'; //End charicter
    while (scan[i]!='E')
    {
        res*=10;
        if (scan[i]=='1') {res+=1;}
        else if (scan[i]=='2') {res+=2;}
        else if (scan[i]=='3') {res+=3;}
        else if (scan[i]=='4') {res+=4;}
        else if (scan[i]=='5') {res+=5;}
        else if (scan[i]=='6') {res+=6;}
        else if (scan[i]=='7') {res+=7;}
        else if (scan[i]=='8') {res+=8;}
        else if (scan[i]=='9') {res+=9;}
        else if (scan[i]=='-') {neg=true;}
        i+=1;
    }
    if (neg) {res*=-1;}
    return res;
}
int displayBoard() //Used for debugging
{
    int x,y;
    for (x=1;x<=8;x++)
    {
        for (y=1;y<=8;y++)
        {
            cout << board[y][x] << "\t";
        }
        cout << endl;
    }
    return 0;
}
string toString(char c) //Converts a char to a string
{
    stringstream s;
    string ret;
    s << c;
    s >> ret;
    return ret;
}
string toString2(int c) //Converts a number to a string
{
    stringstream s;
    string ret;
    s << c;
    s >> ret;
    return ret;
}
int pieceValue(int piece) //Returns the value for a piece, changing this will change the behaviour of the AI
{
    if (piece==1) {return 5;} //Pawn
    else if (piece==2) {return 25;} //Rook
    else if (piece==3) {return 20;} //Bishop
    else if (piece==4) {return 30;} //Knite
    else if (piece==5) {return 80;} //Queen
    return 0;
}
int getValue(int side) //Returns the score for the board
{
    int val=0,x,y;
    for (y=1; y<=8; y++)
    {
        for (x=1; x<=8; x++)
        {
            if (board[x][y]<0 && side==-1)
            {
                val+=pieceValue(board[x][y]*-1);
            } else if (board[x][y]>0 && side==1)
            {
                val+=pieceValue(board[x][y]);
            }
        }
    }
    return val;
}
int getLength(string trn) //Returns the length of a turn
{
    int i;
    for (i=0; i<240; i++)
    {
        if (trn[i]!='0' && trn[i]!='1' && trn[i]!='2' && trn[i]!='3' && trn[i]!='4' && trn[i]!='5' && trn[i]!='6' && trn[i]!='7' && trn[i]!='8' && trn[i]!='9' && trn[i]!='-' && trn[i]!='c' && trn[i]!='p')
        {
            return ((i-5)/3)+1;
        }
    }
    return 0;
}
int doMove(int fromX, int fromY, string mov) //Executes a move to the board and returns the piece taken over
{
    int tx,ty,bef=0;
    tx = toNumber(toString(mov[0]));
    ty = toNumber(toString(mov[1]));
    if (mov[2]=='c') { //Castle
        if (tx==0) {
            board[3][fromY+1] = board[fromX+1][fromY+1];
            board[4][fromY+1] = board[tx+1][ty+1];
            board[tx+1][ty+1] = 0;
            board[fromX+0][fromY+1] = 0;
        } else {
            board[7][fromY+1] = board[fromX+1][fromY+1];
            board[6][fromY+1] = board[tx+1][ty+1];
            board[tx+1][ty+1] = 0;
            board[fromX+0][fromY+1] = 0;
        }
    } else {
        bef = board[tx+1][ty+1];
        board[tx+1][ty+1] = board[fromX+1][fromY+1];
        board[fromX+1][fromY+1]=0;
    }
    return bef;
}
int undoMove(int fromX, int fromY, string mov, int piece) //Undoes a move
{
    int tx,ty;
    tx = toNumber(toString(mov[0]));
    ty = toNumber(toString(mov[1]));
    if (mov[2]=='c') { //Castle
        if (fromX==2) {
            board[1][fromY] = board[4][fromY];
            board[5][fromY] = board[3][fromY];
            board[4][fromY] = 0;
            board[3][fromY] = 0;
        } else {
            board[8][fromY] = board[6][fromY];
            board[5][fromY] = board[7][fromY];
            board[6][fromY] = 0;
            board[7][fromY] = 0;
        }
    } else {
        board[fromX+1][fromY+1]=board[tx+1][ty+1];
        board[tx+1][ty+1]=piece;
    }
    return 0;
}
bool isAttack(int px, int py) //Returns true if a piece is under attack
{
    int side,x,y,xy;
    if (board[px][py]<0) {side=-1;} else {side=1;}
    //Pawn
    if (side==1 && py+1<8) {
        if (px-1>=0) {if (board[px-1][py+1]==-1) {return true;}}
        if (px+1<8) {if (board[px+1][py+1]==-1) {return true;}}
    } else if (side==-1 && py-1>=0) {
        if (px-1>=0) {if (board[px-1][py-1]==1) {return true;}}
        if (px+1<8) {if (board[px+1][py-1]==1) {return true;}}
    }
    //Rook or queen
    for (x=px+1;x<8;x++) { //Left
        if (board[x][py]!=0)
        {
            if (((board[x][py]==-2 || board[x][py]==-5) && side==1) || ((board[x][py]==2 || board[x][py]==5) && side==-1)) {return true;}
            break;
        }}
    for (x=1;x<8;x++) { //Right
        if (px-x<0) {break;}
        if (board[px-x][py]!=0)
        {
            if (((board[px-x][py]==-2 || board[px-x][py]==-5) && side==1) || ((board[px-x][py]==2 || board[px-x][py]==5) && side==-1)) {return true;}
            break;
        }}
    for (y=py+1;y<8;y++) { //Down
        if (board[px][y]!=0)
        {
            if (((board[px][y]==-2 || board[px][y]==-5) && side==1) || ((board[px][y]==2 || board[px][y]==5) && side==-1)) {return true;}
            break;
        }}
    for (y=1;y<8;y++) { //Up
        if (py-y<0) {break;}
        if (board[px][py-y]!=0)
        {
            if (((board[px][py-y]==-2 || board[px][py-y]==-5) && side==1) || ((board[px][py-y]==2 || board[px][py-y]==5) && side==-1)) {return true;}
            break;
        }}
    //Bishop or queen
    for (xy=1;xy<8;xy++) { //Down, left
        if (px+xy>7 || py+xy>7) {break;}
        if (board[px+xy][py+xy]!=0) {
        if (((board[px+xy][py+xy]==-3 || board[px+xy][py+xy]==-5) && side==1) || ((board[px+xy][py+xy]==3 || board[px+xy][py+xy]==5) && side==-1)) {return true;}
        break;}
    }
    for (xy=1;xy<8;xy++) { //Down, right
        if (px-xy<0 || py+xy>7) {break;}
        if (board[px-xy][py+xy]!=0) {
        if (((board[px-xy][py+xy]==-3 || board[px-xy][py+xy]==-5) && side==1) || ((board[px-xy][py+xy]==3 || board[px-xy][py+xy]==5) && side==-1)) {return true;}
        break;}
    }
    for (xy=1;xy<8;xy++) { //Up, left
        if (px+xy>7 || py-xy<0) {break;}
        if (board[px+xy][py-xy]!=0) {
        if (((board[px+xy][py-xy]==-3 || board[px+xy][py-xy]==-5) && side==1) || ((board[px+xy][py-xy]==3 || board[px+xy][py-xy]==5) && side==-1)) {return true;}
        break;}
    }
    for (xy=1;xy<8;xy++) { //Up, right
        if (px-xy<0 || py-xy<0) {break;}
        if (board[px-xy][py-xy]!=0) {
        if (((board[px-xy][py-xy]==-3 || board[px-xy][py-xy]==-5) && side==1) || ((board[px-xy][py-xy]==3 || board[px-xy][py-xy]==5) && side==-1)) {return true;}
        break;}
    }
    //Knite
    if (px-2>=0) { //Left
        if (py-1>=0) {if ((board[px-2][py-1]==-4 && side==1) || (board[px-2][py-1]==4 && side==-1)) {return true;}}
        if (py+1<8) {if ((board[px-2][py+1]==-4 && side==1) || (board[px-2][py+1]==4 && side==-1)) {return true;}}}
    if (px+2<8) { //Right
        if (py-1>=0) {if ((board[px+2][py-1]==-4 && side==1) || (board[px+2][py-1]==4 && side==-1)) {return true;}}
        if (py+1<8) {if ((board[px+2][py+1]==-4 && side==1) || (board[px+2][py+1]==4 && side==-1)) {return true;}}}
    if (py-2>=0) { //Up
        if (px-1>=0) {if ((board[px-1][py-2]==-4 && side==1) || (board[px-1][py-2]==4 && side==-1)) {return true;}}
        if (px+1<8) {if ((board[px+1][py-2]==-4 && side==1) || (board[px+1][py-2]==4 && side==-1)) {return true;}}}
    if (py+2<8) { //Down
        if (px-1>=0) {if ((board[px-1][py+2]==-4 && side==1) || (board[px-1][py+2]==4 && side==-1)) {return true;}}
        if (px+1<8) {if ((board[px+1][py+2]==-4 && side==1) || (board[px+1][py+2]==4 && side==-1)) {return true;}}}
    //King
    for (x=-1;x<=1;x++) {
        if (px+x>=0 && px+x<8) {
            for (y=-1;y<=1;y++) {
                if (py+y>=0 && py+y<8) {
                    if ((board[px+x][py+y]==-6 && side==1) || (board[px+x][py+y]==6 && side==-1)) {return true;}
                }
            }
        }
    }
    return false;
}
string getMoves(int px, int py) //Returns all the possible moves the piece can do
{
    int side,piece,x,y,xy,kposx=-1,kposy,nMove;
    string moves=toString2(px)+toString2(py);
    if (board[px][py]<0) {side = -1;
        piece = board[px][py]*-1;
    } else {piece = board[px][py];
        side = 1;}
    if (piece==1) { //Pawn
        if (side==1) {
            if (board[px][py+1]==0) {moves=moves+toString2(px)+toString2(py+1)+"0";}
            if (px>0) {if (board[px-1][py+1]<0) {moves=moves+toString2(px-1)+toString2(py+1)+"0";}}
            if (px<8) {if (board[px+1][py+1]<0) {moves=moves+toString2(px+1)+toString2(py+1)+"0";}}
            if (py==1) {moves=moves+toString2(px)+toString2(py+2)+"0";}
        } else {
            if (board[px][py-1]==0) {moves=moves+toString2(px)+toString2(py-1)+"0";}
            if (px>0) {if (board[px-1][py-1]>0) {moves=moves+toString2(px-1)+toString2(py-1)+"0";}}
            if (px<8) {if (board[px+1][py-1]>0) {moves=moves+toString2(px+1)+toString2(py-1)+"0";}}
            if (py==6) {moves=moves+toString2(px)+toString2(py-2)+"0";}
        }
    }
    if (piece==2 || piece==5) { //Rook or queen
        for (x=px+1;x<8;x++) //Right
        {
            if (board[x][py]!=0)
            {
                if ((board[x][py]>0 && side==-1) || (board[x][py]<0 && side==1)) {moves = moves+toString2(x)+toString2(py)+"0";}
                break;
            }
            moves = moves+toString2(x)+toString2(py)+"0";}
        for (x=1;x<8;x++) //Left
        {
            if (px-x<0) {break;}
            if (board[px-x][py]!=0)
            {
                if ((board[px-x][py]>0 && side==-1) || (board[px-x][py]<0 && side==1)) {moves = moves+toString2(px-x)+toString2(py)+"0";}
                break;
            }
            moves = moves+toString2(px-x)+toString2(py)+"0";}
        for (y=py+1;y<8;y++) //Down
        {
            if (board[px][y]!=0)
            {
                if ((board[px][y]>0 && side==-1) || (board[px][y]<0 && side==1)) {moves = moves+toString2(px)+toString2(y)+"0";}
                break;
            }
            moves = moves+toString2(px)+toString2(y)+"0";}
        for (y=1;y<8;y++) //Up
        {
            if (py-y<0) {break;}
            if (board[px][py-y]!=0)
            {
                if ((board[px][py-y]>0 && side==-1) || (board[px][py-y]<0 && side==1)) {moves = moves+toString2(px)+toString2(py-y)+"0";}
                break;
            }
            moves = moves+toString2(px)+toString2(py-y)+"0";}
    }
    if (piece==3 || piece==5) { //Bishop or queen
        for (xy=1;xy<8;xy++) //Down, right
        {
            if (px+xy>7 || py+xy>7) {break;}
            if (board[px+xy][py+xy]!=0)
            {
                if ((board[px+xy][py+xy]>0 && side==-1) || (board[px+xy][py+xy]<0 && side==1)) {moves = moves+toString2(px+xy)+toString2(py+xy)+"0";}
                break;
            }
            moves = moves+toString2(px+xy)+toString2(py+xy)+"0";}
        for (xy=1;xy<8;xy++) //Down, left
        {
            if (px-xy<0 || py+xy>7) {break;}
            if (board[px-xy][py+xy]!=0)
            {
                if ((board[px-xy][py+xy]>0 && side==-1) || (board[px-xy][py+xy]<0 && side==1)) {moves = moves+toString2(px-xy)+toString2(py+xy)+"0";}
                break;
            }
            moves = moves+toString2(px-xy)+toString2(py+xy)+"0";}
        for (xy=1;xy<8;xy++) //Up, right
        {
            if (px+xy>7 || py-xy<0) {break;}
            if (board[px+xy][py-xy]!=0)
            {
                if ((board[px+xy][py-xy]>0 && side==-1) || (board[px+xy][py-xy]<0 && side==1)) {moves = moves+toString2(px+xy)+toString2(py-xy)+"0";}
                break;
            }
            moves = moves+toString2(px+xy)+toString2(py-xy)+"0";}
        for (xy=1;xy<8;xy++) //Up, left
        {
            if (px-xy<0 || py-xy<0) {break;}
            if (board[px-xy][py-xy]!=0)
            {
                if ((board[px-xy][py-xy]>0 && side==-1) || (board[px-xy][py-xy]<0 && side==1)) {moves = moves+toString2(px-xy)+toString2(py-xy)+"0";}
                break;
            }
            moves = moves+toString2(px-xy)+toString2(py-xy)+"0";}
    }
    if (piece==4) { //Knite
        if (px-2>=0) { //Left
            if (py-1>=0) {if (board[px-2][py-1]==0 || (board[px-2][py-1]<0 && side==1) || (board[px-2][py-1]>0 && side==-1)) {
                moves=moves+toString2(px-2)+toString2(py-1)+"0";}}
            if (py+1<8) {if (board[px-2][py+1]==0 || (board[px-2][py+1]<0 && side==1) || (board[px-2][py+1]>0 && side==-1)) {
                moves=moves+toString2(px-2)+toString2(py+1)+"0";}}}
        if (px+2<8) { //Right
            if (py-1>=0) {if (board[px+2][py-1]==0 || (board[px+2][py-1]<0 && side==1) || (board[px+2][py-1]>0 && side==-1)) {
                moves=moves+toString2(px+2)+toString2(py-1)+"0";}}
            if (py+1<8) {if (board[px+2][py+1]==0 || (board[px+2][py+1]<0 && side==1) || (board[px+2][py+1]>0 && side==-1)) {
                moves=moves+toString2(px+2)+toString2(py+1)+"0";}}}
        if (py-2>=0) { //Up
            if (px-1>=0) {if (board[px-1][py-2]==0 || (board[px-1][py-2]<0 && side==1) || (board[px-1][py-2]>0 && side==-1)) {
                moves=moves+toString2(px-1)+toString2(py-2)+"0";}}
            if (px+1<8) {if (board[px+1][py-2]==0 || (board[px+1][py-2]<0 && side==1) || (board[px+1][py-2]>0 && side==-1)) {
                moves=moves+toString2(px+1)+toString2(py-2)+"0";}}}
        if (py+2<8) { //Down
            if (px-1>=0) {if (board[px-1][py+2]==0 || (board[px-1][py+2]<0 && side==1) || (board[px-1][py+2]>0 && side==-1)) {
                moves=moves+toString2(px-1)+toString2(py+2)+"0";}}
            if (px+1<8) {if (board[px+1][py+2]==0 || (board[px+1][py+2]<0 && side==1) || (board[px+1][py+2]>0 && side==-1)) {
                moves=moves+toString2(px+1)+toString2(py+2)+"0";}}}
    }
    if (piece==6) { //King
        for (x=-1;x<=1;x++)
        {
            if (px+x>=0 && px+x<8) {
            for (y=-1;y<=1;y++)
            {
                if (py+y>=0 && py+y<8)
                {
                    if (board[px+x][py+y]==0 || (board[px+x][py+y]<0 && side==1) || (board[px+x][py+y]>0 && side==-1))
                    {
                        moves=moves+toString2(px+x)+toString2(py+y)+"0";
                    }
                }
            }}
        }
        if (false) {

        }
    }
    //Find the king
    for (x=1;x<=8;x++) {
        for (y=1;y<=8;y++) {
            if (board[x][y]==6*side) {kposx = x; kposy = y; break;}
        }
        if (kposx==-1) {break;}
    }
    if (kposx==-1) {cout << "Error, king was not found on the board\n"; return "";}
    nMove = getLength(moves);
}


int stepGo(int curDepth, int side) //Steps a go
{

}

int main()
{
    string turns[120];
    int turnLength=0,turn,Side;
    cout << "Loading from file...";
    ifstream file("comFile.txt", ios::in);
    if (file.is_open()) {
        int i=1, ch, piece;
        string line;
        while ( getline (file,line) ) {
            if (i<=8) {
            for (ch=1; ch<=8; ch++) {
                if (line[(ch*2)-1]=='0') {piece=0;} //Nothing
                else if (line[(ch*2)-1]=='1') {piece=1;} //Pawn
                else if (line[(ch*2)-1]=='2') {piece=2;} //Rook
                else if (line[(ch*2)-1]=='3') {piece=3;} //Bishop
                else if (line[(ch*2)-1]=='4') {piece=4;} //Knite
                else if (line[(ch*2)-1]=='5') {piece=5;} //Queen
                else if (line[(ch*2)-1]=='6') {piece=6;} //King
                if (line[(ch*2)-2]=='-') {piece*=-1;}
                board[i][ch]=piece;
            }} else if (i==9) {depth = toNumber(line);}
            else if (i==10) {Side = toNumber(line);}
            else if (i==11) {moves = line;}
            else {
                turns[turnLength] = line;
                turnLength++;
            }
            i++;
        }
        file.close();
        cout << "done\nCalculating moves...\n";
        int numMoves,iner,be;
        for (turn=0;turn<turnLength;turn++)
        {
            numMoves = getLength(turns[turn]);
            cout << "Doing " << turns[turn] << ", " << numMoves << endl;
            int froX,froY;
            froX = toNumber(toString(turns[turn][0]));
            froY = toNumber(toString(turns[turn][1]));
            for (iner=2; iner<=numMoves; iner++)
            {
                be = doMove(froX,froY,toString(turns[turn][(iner*3)-4])+toString(turns[turn][(iner*3)-3])+toString(turns[turn][(iner*3)-2]));
                stepGo(depth,Side);
                undoMove(froX,froY,toString(turns[turn][(iner*3)-4])+toString(turns[turn][(iner*3)-3])+toString(turns[turn][(iner*3)-2]),be);
            }
            break;
        }
    } else {cout << "fail\nError loading file, does it exist??\n";}
    return 0;
}

