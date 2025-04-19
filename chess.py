# The goal of this code is to try to code a cehss engine and make it compete against an AI.
# For simplification reasons (and fun) there will be no rules. It end when a player lose theiir king

import matplotlib.pyplot as plt
import numpy as np
import random
import chess_pst
import copy

LETTERS = ["a","b","c","d","e","f","g","h"]
NUMBERS = {
    "a":0,
    "b":1,
    "c":2,
    "d":3,
    "e":4,
    "f":5,
    "g":6,
    "h":7
}
P_VALUES = {
    "p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0
}
PST = {
    "p" : chess_pst.P_PST,
    "n" : chess_pst.N_PST,
    "b" : chess_pst.B_PST,
    "r" : chess_pst.R_PST,
    "q" : chess_pst.Q_PST,
    "k" : chess_pst.K_PST
}
O_PST = {
    "p" : chess_pst.PO_PST,
    "n" : chess_pst.NO_PST,
    "b" : chess_pst.BO_PST,
    "r" : chess_pst.RO_PST,
    "q" : chess_pst.QO_PST,
    "k" : chess_pst.KO_PST
}

turn=0

class piece:
    def __init__(self,type,color):
        self.type = type
        self.color = color
    
    def __str__(self):
        return self.type + self.color

    def checkmoves(self,x,y):
        pbMoves.clear()
        if self.color=="w":
            match self.type:
                case "p":
                    if (x+1<8 and moves[-1]=="p"+LETTERS[x+1]+str(6)+LETTERS[x+1]+str(4) and y==4 and board[x+1][y+1]==""):
                        pbMoves.append(self.type + LETTERS[x]+str(y)+LETTERS[x+1] + str(y+1) + "p")
                    if (x-1<8 and moves[-1]=="p"+LETTERS[x-1]+str(6)+LETTERS[x-1]+str(4) and y==4 and board[x-1][y+1]==""):
                        pbMoves.append(self.type + LETTERS[x]+str(y)+LETTERS[x-1] + str(y+1) + "p")
                    if (y==1 and board[x][y+2]=="" and board[x][y+1]==""):
                        pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+2))
                    if (board[x][y+1]=="" and y+1<8):
                        pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1))
                    if (x+1<8 and board[x+1][y+1]!="" and board[x+1][y+1].color!=self.color):
                        pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1]+str(y+1))
                    if (x-1>=0 and board[x-1][y+1]!="" and board[x-1][y+1].color!=self.color):
                        pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1]+str(y+1))
                case "n":
                    for i in range(2):
                        if (x+(2*((-1)**i))>=0 and x+(2*((-1)**i))<8 and y-1>=0 and y-1<8):
                            if (board[x+(2*((-1)**i))][y-1]=="" or board[x+(2*((-1)**i))][y-1].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+(2*((-1)**i))]+str(y-1))
                        if (x-1>=0 and x-1<8 and y+(2*((-1)**i))>=0 and y+(2*((-1)**i))<8):
                            if (board[x-1][y+(2*((-1)**i))]=="" or board[x-1][y+(2*((-1)**i))].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1]+str(y+(2*(-1)**i)))
                        if (x+(2*((-1)**i))>=0 and x+(2*((-1)**i))<8 and y+1>=0 and y+1<8):
                            if (board[x+(2*((-1)**i))][y+1]=="" or board[x+(2*((-1)**i))][y+1].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+(2*((-1)**i))]+str(y+1))
                        if (x+1>=0 and x+1<8 and y+(2*((-1)**i))>=0 and y+(2*((-1)**i))<8):
                            if (board[x+1][y+(2*((-1)**i))]=="" or board[x+1][y+(2*((-1)**i))].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1]+str(y+((2*(-1)**i))))
                case "r":
                    for i in range(7):
                        if x+1+i<8 and board[x+1+i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                        elif x+1+i<8 and board[x+1+i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):
                        if x-1-i>=0 and board[x-1-i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                        elif x-1-i>=0 and board[x-1-i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):
                        if y+1+i<8 and board[x][y+1+i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                        elif y+1+i<8 and board[x][y+1+i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                            break
                        else :
                            break
                    for i in range(7):
                        if y-1-i>=0 and board[x][y-1-i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                        elif y-1-i>=0 and board[x][y-1-i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                            break
                        else :
                            break
                case "k":
                    for i in range(2):
                        for j in range(2):
                            if x+((-1)**i)>=0 and x+((-1)**i)<8 and y+((-1)**j)>=0 and y+((-1)**j)<8 and board[x+((-1)**i)][y+((-1)**j)]=="":
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+((-1)**i)]+str(y+((-1)**j)))
                            elif x+((-1)**i)>=0 and x+((-1)**i)<8 and y+((-1)**j)>=0 and y+((-1)**j)<8 and board[x+((-1)**i)][y+((-1)**j)].color!=self.color:
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+((-1)**i)]+str(y+((-1)**j)))
                        
                        if x+1-2*i>=0 and x+1-2*i<8 and board[x+1-2*i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1-2*i]+str(y))
                        elif x+1-2*i>=0 and x+1-2*i<8 and board[x+1-2*i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1-2*i]+str(y))
                        if y+1-2*i>=0 and y+1-2*i<8 and board[x][y+1-2*i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1-2*i))
                        elif y+1-2*i>=0 and y+1-2*i<8 and board[x][y+1-2*i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1-2*i))
                case "b":
                    for i in range(1,8):
                        if x+i<8 and y+i<8 and board[x+i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                        elif x+i<8 and y+i<8 and board[x+i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x+i<8 and y-i>=0 and board[x+i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                        elif x+i<8 and y-i>=0 and board[x+i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y+i<8 and board[x-i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                        elif x-i>=0 and y+i<8 and board[x-i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y-i>=0 and board[x-i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                        elif x-i>=0 and y-i>=0 and board[x-i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                            break
                        else:
                            break
                case "q":
                    # rook movement
                    for i in range(7):
                        if x+1+i<8 and board[x+1+i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                        elif x+1+i<8 and board[x+1+i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):
                        if x-1-i>=0 and board[x-1-i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                        elif x-1-i>=0 and board[x-1-i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):
                        if y+1+i<8 and board[x][y+1+i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                        elif y+1+i<8 and board[x][y+1+i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                            break
                        else :
                            break
                    for i in range(7):
                        if y-1-i>=0 and board[x][y-1-i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                        elif y-1-i>=0 and board[x][y-1-i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                            break
                        else :
                            break
                    # bishop movement
                    for i in range(1,8):
                        if x+i<8 and y+i<8 and board[x+i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                        elif x+i<8 and y+i<8 and board[x+i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x+i<8 and y-i>=0 and board[x+i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                        elif x+i<8 and y-i>=0 and board[x+i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y+i<8 and board[x-i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                        elif x-i>=0 and y+i<8 and board[x-i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y-i>=0 and board[x-i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                        elif x-i>=0 and y-i>=0 and board[x-i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                            break
                        else:
                            break
                    

        if self.color=="b":
            match self.type:
                case "p":
                    # en passant
                    if (x+1<8 and moves[-1]=="p"+LETTERS[x+1]+str(1)+LETTERS[x+1]+str(3) and y==3 and board[x+1][y-1]==""):
                        pbMoves.append(self.type + LETTERS[x]+str(y)+LETTERS[x+1] + str(y-1) + "p")
                    if (x-1<8 and moves[-1]=="p"+LETTERS[x-1]+str(1)+LETTERS[x-1]+str(3) and y==3 and board[x-1][y-1]==""):
                        pbMoves.append(self.type + LETTERS[x]+str(y)+LETTERS[x-1] + str(y-1) + "p")
                    # forward
                    if (y==6 and board[x][y-2]=="" and board[x][y-1]=="" and y+1>=0):
                        pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-2))
                    if (board[x][y-1]==""):
                        pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1))
                    # eating
                    if (x+1<8 and board[x+1][y-1]!="" and board[x+1][y-1].color!=self.color):
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1]+str(y-1))
                    if (x-1>=0 and board[x-1][y-1]!="" and board[x-1][y-1].color!=self.color):
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1]+str(y-1))
                case "n":# knight
                    for i in range(2):
                        if (x+(2*((-1)**i))>=0 and x+(2*((-1)**i))<8 and y-1>=0 and y-1<8):
                            if (board[x+(2*((-1)**i))][y-1]=="" or board[x+(2*((-1)**i))][y-1].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+(2*((-1)**i))]+str(y-1))
                        if (x-1>=0 and x-1<8 and y+(2*((-1)**i))>=0 and y+(2*((-1)**i))<8):
                            if (board[x-1][y+(2*((-1)**i))]=="" or board[x-1][y+(2*((-1)**i))].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1]+str(y+(2*(-1)**i)))
                        if (x+(2*((-1)**i))>=0 and x+(2*((-1)**i))<8 and y+1>=0 and y+1<8):
                            if (board[x+(2*((-1)**i))][y+1]=="" or board[x+(2*((-1)**i))][y+1].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+(2*((-1)**i))]+str(y+1))
                        if (x+1>=0 and x+1<8 and y+(2*((-1)**i))>=0 and y+(2*((-1)**i))<8):
                            if (board[x+1][y+(2*((-1)**i))]=="" or board[x+1][y+(2*((-1)**i))].color!=self.color):
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1]+str(y+((2*(-1)**i))))
                case "r":
                    for i in range(7):# right
                        if x+1+i<8 and board[x+1+i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                        elif x+1+i<8 and board[x+1+i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):# left
                        if x-1-i>=0 and board[x-1-i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                        elif x-1-i>=0 and board[x-1-i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):# up
                        if y+1+i<8 and board[x][y+1+i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                        elif y+1+i<8 and board[x][y+1+i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                            break
                        else :
                            break
                    for i in range(7):# down
                        if y-1-i>=0 and board[x][y-1-i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                        elif y-1-i>=0 and board[x][y-1-i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                            break
                        else :
                            break
                case "k":
                    for i in range(2):
                        for j in range(2):#check for the diagonals
                            if x+((-1)**i)>=0 and x+((-1)**i)<8 and y+((-1)**j)>=0 and y+((-1)**j)<8 and board[x+((-1)**i)][y+((-1)**j)]=="":
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+((-1)**i)]+str(y+((-1)**j)))
                            elif x+((-1)**i)>=0 and x+((-1)**i)<8 and y+((-1)**j)>=0 and y+((-1)**j)<8 and board[x+((-1)**i)][y+((-1)**j)].color!=self.color:
                                pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+((-1)**i)]+str(y+((-1)**j)))
                        
                        #check for the horizontal and vertical
                        if x+1-2*i>=0 and x+1-2*i<8 and board[x+1-2*i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1-2*i]+str(y))
                        elif x+1-2*i>=0 and x+1-2*i<8 and board[x+1-2*i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1-2*i]+str(y))
                        if y+1-2*i>=0 and y+1-2*i<8 and board[x][y+1-2*i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1-2*i))
                        elif y+1-2*i>=0 and y+1-2*i<8 and board[x][y+1-2*i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1-2*i))
                case "b":
                    for i in range(1,8):
                        if x+i<8 and y+i<8 and board[x+i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                        elif x+i<8 and y+i<8 and board[x+i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x+i<8 and y-i>=0 and board[x+i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                        elif x+i<8 and y-i>=0 and board[x+i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y+i<8 and board[x-i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                        elif x-i>=0 and y+i<8 and board[x-i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y-i>=0 and board[x-i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                        elif x-i>=0 and y-i>=0 and board[x-i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                            break
                        else:
                            break
                case "q":
                    # rook movement
                    for i in range(7):
                        if x+1+i<8 and board[x+1+i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                        elif x+1+i<8 and board[x+1+i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x+1+i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):
                        if x-1-i>=0 and board[x-1-i][y]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                        elif x-1-i>=0 and board[x-1-i][y].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x-1-i]+str(y))
                            break
                        else :
                            break
                    for i in range(7):
                        if y+1+i<8 and board[x][y+1+i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                        elif y+1+i<8 and board[x][y+1+i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y+1+i))
                            break
                        else :
                            break
                    for i in range(7):
                        if y-1-i>=0 and board[x][y-1-i]=="":
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                        elif y-1-i>=0 and board[x][y-1-i].color!=self.color:
                            pbMoves.append(self.type+LETTERS[x]+str(y)+LETTERS[x]+str(y-1-i))
                            break
                        else :
                            break
                    # bishop movement
                    for i in range(1,8):
                        if x+i<8 and y+i<8 and board[x+i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                        elif x+i<8 and y+i<8 and board[x+i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y+i))
                            break
                        else:
                            print(str(x+i) + " : " + str(y+i))
                            break
                    for i in range(1,8):
                        if x+i<8 and y-i>=0 and board[x+i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                        elif x+i<8 and y-i>=0 and board[x+i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x+i] + str(y-i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y+i<8 and board[x-i][y+i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                        elif x-i>=0 and y+i<8 and board[x-i][y+i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y+i))
                            break
                        else:
                            break
                    for i in range(1,8):
                        if x-i>=0 and y-i>=0 and board[x-i][y-i]=="":
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                        elif x-i>=0 and y-i>=0 and board[x-i][y-i].color!=self.color:
                            pbMoves.append(self.type + LETTERS[x] + str(y) + LETTERS[x-i] + str(y-i))
                            break
                        else:
                            break

def draw_chessboard():
    aboard = np.zeros((8,8), dtype=float)
    for i in range(8):
        for j in range(8):
            if (i + j) % 2 == 1:
                aboard[i, j] = 0
            else :
                aboard[i, j] = 0.5
                
    
    plt.figure(figsize=(6, 6))
    plt.imshow(aboard, cmap='Greens', origin='upper',vmin=0, vmax=1)
    plt.xticks([])
    plt.yticks([])

def draw_chessboardm():
    ax = plt.gca() #prends existant
    ax.cla()

    aboard = np.zeros((8, 8), dtype=float)
    for i in range(8):
        for j in range(8):
            aboard[i, j] = 0.5 if (i + j) % 2 == 0 else 0

    for move in pbMoves:
        aboard[7 - int(move[2]), NUMBERS[move[1]]] += 0.1
        aboard[7 - int(move[4]), NUMBERS[move[3]]] = 0.15 if (aboard[7 - int(move[4]), NUMBERS[move[3]]]==0) else 0.35

    ax.imshow(aboard, cmap='Greens', origin='upper', vmin=0, vmax=1)
    ax.set_xticks([])
    ax.set_yticks([])

    display_pieces()
    plt.draw()


def display_pieces():
    white_symbols = {
        'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
        'k': '♔', 'q': '♕', 'r': '♖', 'b': '♗', 'n': '♘', 'p': '♙'
    }
    
    black_symbols = {
        'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟',
        'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
    }
    
    for x in range(8):
        for y in range(8):
            if board[x][y]!="":
                if board[x][y].color=="w":
                    plt.text(x, 7-y, white_symbols[board[x][y].type], fontsize=32, ha='center', va='center')
                if board[x][y].color=="b":
                    plt.text(x, 7-y, black_symbols[board[x][y].type], fontsize=32, ha='center', va='center')

def on_click(event):
    if event.xdata is not None and event.ydata is not None:
        global board
        global turn
        col = round(event.xdata)
        row = round(event.ydata)
        row = 7 - row # bc top to bottom and want inverse
        for move in pbMoves:
            if col == NUMBERS[move[3]] and str(row) == move[4]:
                res = toMove(move)
                if res!=0:
                    if res==1:
                        print("white won")
                    if res==-1:
                        print("black won")
                    setup_board()
                    display_pieces()
                draw_chessboardm()
                res = toMove(ce_pos("b"))
                if res!=0:
                    if res==1:
                        print("white won")
                    if res==-1:
                        print("black won")
                    board = []
                    turn=0
                    board = [([("")for _ in range(8)])for _ in range(8)]
                    setup_board()
                    display_pieces()
                draw_chessboardm()
                return
        if board[col][row]=="":
            print("you can't click here")
        elif ((board[col][row].color=="w" and turn%2==0) or (board[col][row].color=="b" and turn%2==1)):
            board[col][row].checkmoves(col,row)
        draw_chessboardm()
        
def toMove(move):
    global turn # to get turn and not create local variable 
    if board[NUMBERS[move[3]]][int(move[4])]!="" and board[NUMBERS[move[3]]][int(move[4])].type=="k":
        if board[NUMBERS[move[3]]][int(move[4])].color == "w":
            return -1
        if board[NUMBERS[move[3]]][int(move[4])].color == "b":
            return 1
    board[NUMBERS[move[3]]][int(move[4])] = board[NUMBERS[move[1]]][int(move[2])] # replace
    board[NUMBERS[move[1]]][int(move[2])] = "" # del
    if (move[-1]=="p"): # en passant
        board[NUMBERS[move[3]]][int(move[2])] = ""
    moves.append(move) # to store
    turn+=1
    pbMoves.clear()
    print(moves)
    return 0

def setup_board():
    for i in range(8):
        board[i][1] = piece("p","w")
    for i in range(8):
        board[i][6] = piece("p","b")
    for i in range(2):
        board[i*7][0] = piece("r","w")
    for i in range(2):
        board[i*7][7] = piece("r","b")
    for i in range(2):
        board[i*5+1][0] = piece("n","w")
    for i in range(2):
        board[i*5+1][7] = piece("n","b")
    for i in range(2):
        board[i*3+2][0] = piece("b","w")
    for i in range(2):
        board[i*3+2][7] = piece("b","b")
    
    board[3][0] = piece("q","w")
    board[4][0] = piece("k","w")
    board[3][7] = piece("q","b")
    board[4][7] = piece("k","b")

# first engine, wanted to make it in another file but causes problems
def ce_random(color):
    totalMoves = []
    for i in range(8):
        for j in range(8):
            if board[i][j]!="" and board[i][j].color==color:
                board[i][j].checkmoves(i,j)
                for move in pbMoves:
                    totalMoves.append(move) 
    return totalMoves[random.randint(0,len(totalMoves)-1)]

# An engine solely based on the position of each individual piece, later the depth parameter will be added
def ce_pos(color):
    bestMove = ["",0]
    for i in range(8):
        for j in range(8):
            if board[i][j]!="" and board[i][j].color==color:
                board[i][j].checkmoves(i,j)
                for move in pbMoves:
                    pbBoard = ce_pos_pbBoard(move)
                    value = ce_pos_eval(pbBoard)
                    if bestMove[0]=="":
                        bestMove = [move, value]
                    if color=="w" and value>bestMove[1]:
                        bestMove = [move, value]
                    elif color=="b" and value<bestMove[1]:
                        bestMove = [move, value]
    return bestMove[0]

# a function to evaluate the position of a given board
def ce_pos_eval(myboard):
    if myboard==1 or myboard==(-1):
        return (100000000000000*myboard)
    value = 0
    for i in range(8):
        for j in range(8):
            if myboard[i][j]!="":
                if myboard[i][j].color=="w":
                    value+=P_VALUES[myboard[i][j].type]
                    value+=PST[myboard[i][j].type][i][j]
                elif myboard[i][j].color=="b":
                    value-=P_VALUES[myboard[i][j].type]
                    value-=PST[myboard[i][j].type][i][j]
    return value

def ce_pos_pbBoard(move):
    pbBoard = []
    pbBoard = copy.deepcopy(board)
    if pbBoard[NUMBERS[move[3]]][int(move[4])]!="" and pbBoard[NUMBERS[move[3]]][int(move[4])].type=="k":
        if pbBoard[NUMBERS[move[3]]][int(move[4])].color == "w":
            return -1
        if pbBoard[NUMBERS[move[3]]][int(move[4])].color == "b":
            return 1
    pbBoard[NUMBERS[move[3]]][int(move[4])] = pbBoard[NUMBERS[move[1]]][int(move[2])] # replace
    pbBoard[NUMBERS[move[1]]][int(move[2])] = "" # del
    if (move[-1]=="p"): # en passant
        pbBoard[NUMBERS[move[3]]][int(move[2])] = ""
    return pbBoard

board = [([("")for _ in range(8)])for _ in range(8)] # to initialize, could be better to use numpy but it's like that
moves = ["start"] # to avoid creating errors when checking previous move (en passant)
pbMoves = [] # list of possibles moves

def main():
    draw_chessboard()
    setup_board()
    display_pieces()
    plt.gcf().canvas.mpl_connect('button_press_event', on_click)
    plt.ion()
    plt.show(block=True)

if __name__ == "__main__":
    main()