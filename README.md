# SimpleDistributedChessAI
A program that uses a script running on other computers to play chess againsed someone

Python is used for the GUI and the networking, C++ is used for the Chess AI. 
The program will get all the possible goes for the player selected and split them up to send sepretly to multiple computers. 
These computers will then put the board and the turns in a .txt file and execute an exe file. Ones complete the exe will feed back in a file and the python scripts will send the best turn back for the server to decide on
