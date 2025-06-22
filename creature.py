import numpy as np
import pygame
import time

WIDTH, HEIGHT = 800, 600
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GROUND = 400

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lines = []
        
    def addLine(self, line):
        self.lines.append(line)

class Line:
    def __init__(self, startPos, endPos, startNode=0, endNode = 0):
        self.startPos = startPos
        self.endPos = endPos
        self.middle = (np.average((startPos[0],endPos[0])),np.average((startPos[1],endPos[1])))
        self.startNode = startNode
        self.endNode = endNode
        self.muscles = []
        
    def addMuscle(self, muscle):
        self.muscles.append(muscle)
    

class Muscle:
    def __init__(self, startLine:Line, endLine:Line):
        self.startLine = startLine
        self.endLine = endLine
    
    def contract(self, force):
        force = min(0.5, force)
        force = max(-0.5, force)
        startAng = np.arctan2((self.startLine.endPos[0] - self.startLine.startPos[0]),(self.startLine.endPos[1] - self.startLine.startPos[1]))
        startLength = np.sqrt(np.square(self.startLine.startPos[0] - self.startLine.endPos[0]) +
                      np.square(self.startLine.startPos[1] - self.startLine.endPos[1]))

        endAng = np.arctan2((self.endLine.endPos[0] - self.endLine.startPos[0]),(self.endLine.endPos[1] - self.endLine.startPos[1]))
        endLength = np.sqrt(np.square(self.endLine.startPos[0] - self.endLine.endPos[0]) +
                      np.square(self.endLine.startPos[1] - self.endLine.endPos[1]))

        angle = startAng + (endAng - startAng) * force
        
        if (self.startLine.startNode == self.endLine.startNode):
            # dif = getMaxAngle(self.startLine.endPos[1], startLength, self.endLine.endPos[1], endLength, angle)
            # startAng += dif
            # endAng += dif
            self.startLine.endPos = (int(self.startLine.startPos[0] + np.sin(startAng + (endAng - startAng) * force) * startLength),
                       int(self.startLine.startPos[1] + np.cos(startAng + (endAng - startAng) * force) * startLength))
            self.endLine.endPos = (int(self.endLine.startPos[0] + np.sin(endAng + (startAng - endAng) * force) * endLength),
                       int(self.endLine.startPos[1] + np.cos(endAng + (startAng - endAng) * force) * endLength))
        elif (self.startLine.startNode == self.endLine.endNode):
            # dif = getMaxAngle(self.startLine.endPos[1], startLength, self.endLine.startPos[1], endLength, angle)
            # startAng += dif
            # endAng += dif
            self.startLine.endPos = (int(self.startLine.startPos[0] + np.sin(startAng + (endAng - startAng) * force) * startLength),
                       int(self.startLine.startPos[1] + np.cos(startAng + (endAng - startAng) * force) * startLength))
            self.endLine.startPos = (int(self.endLine.startPos[0] + np.sin(endAng + (startAng - endAng) * force) * endLength),
                       int(self.endLine.startPos[1] + np.cos(endAng + (startAng - endAng) * force) * endLength))
        elif (self.startLine.endNode == self.endLine.startNode):
            # dif = getMaxAngle(self.startLine.startPos[1], startLength, self.endLine.endPos[1], endLength, angle)
            # startAng += dif
            # endAng += dif
            self.startLine.startPos = (int(self.startLine.startPos[0] + np.sin(startAng + (endAng - startAng) * force) * startLength),
                       int(self.startLine.startPos[1] + np.cos(startAng + (endAng - startAng) * force) * startLength))
            self.endLine.endPos = (int(self.endLine.startPos[0] + np.sin(endAng + (startAng - endAng) * force) * endLength),
                       int(self.endLine.startPos[1] + np.cos(endAng + (startAng - endAng) * force) * endLength))
        elif (self.startLine.endNode == self.endLine.endNode):
            # dif = getMaxAngle(self.startLine.startPos[1], startLength, self.endLine.startPos[1], endLength, angle)
            # startAng += dif
            # endAng += dif
            self.startLine.startPos = (int(self.startLine.startPos[0] + np.sin(startAng + (endAng - startAng) * force) * startLength),
                       int(self.startLine.startPos[1] + np.cos(startAng + (endAng - startAng) * force) * startLength))
            self.endLine.startPos = (int(self.endLine.startPos[0] + np.sin(endAng + (startAng - endAng) * force) * endLength),
                       int(self.endLine.startPos[1] + np.cos(endAng + (startAng - endAng) * force) * endLength))

def getMaxAngle(startLinePos, startLineLength, endLinePos, endLineLength, angle):
    startDif = startLinePos - GROUND
    startAngleMax = np.arcsin(startDif/startLineLength)
    endDif = endLinePos - GROUND
    endAngleMax = np.arcsin(endDif/endLineLength)
    dif = 0 
    if (angle>=startAngleMax):
        dif = angle - startAngleMax
        
    if (angle>=endAngleMax):
        dif = angle - endAngleMax
    
    return dif


node = Node(125,200)
line1 = Line((125,200), (200,390), startNode=node)
line2 = Line((125,200), (125,25), startNode=node)
muscle = Muscle(line1, line2)

screen.fill(WHITE)
pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
pygame.draw.line(screen, GREEN, line1.startPos, line1.endPos)
pygame.draw.line(screen, RED, line2.startPos, line2.endPos)
pygame.display.flip()
time.sleep(1)
muscle.contract(0.1)
screen.fill(WHITE)
pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
pygame.draw.line(screen, GREEN, line1.startPos, line1.endPos)
pygame.draw.line(screen, RED, line2.startPos, line2.endPos)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False    
        