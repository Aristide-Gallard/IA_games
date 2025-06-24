# The future goal is to make creatures learn to walk in 2d
# most of the parameters are below
# Currently only the "physic engine" is made the brains still need to be implemented
# /!\ do not make circular creatures




import numpy as np
import pygame
import time
import time


WIDTH, HEIGHT = 800, 600
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GROUND = 400
GRAVITY = 0.9
AIR_RES = 0.05

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Node:
    def __init__(self, x, y):
        self.pos = np.array((x,y),float)
        self.prev_pos = self.pos.copy()
        self.lines = []
        self.force = np.array((0,0),float)
        
    def addLine(self, line):
        self.lines.append(line)
    
    def update(self, dt=1.0, launcher = 0):
        # apply gravity
        self.force += np.array((0, GRAVITY))

        # velocity + new pos
        velocity = self.pos - self.prev_pos
        self.prev_pos = self.pos.copy()
        self.pos += velocity * 1-AIR_RES + self.force * dt * dt

        if self.pos[1] > GROUND:
            self.pos[1] = GROUND
            self.prev_pos[1] = self.pos[1] + velocity[1] * -0.5

        # keep lentgh + transfer force
        for line in self.lines:
            if line.startNode == self:
                other = line.endNode
            else:
                other = line.startNode

            delta = self.pos - other.pos
            dist = np.linalg.norm(delta)
            # in case of a bug
            if dist == 0:
                continue
            
            diff = (dist - line.length) / dist
            correction = delta * 0.5 * diff
            self.pos -= correction
            other.pos += correction
            if launcher!=other:
                other.update(launcher=self)

        # Reset force
        self.force[:] = 0

class Line:
    def __init__(self, startNode, endNode):
        self.startNode = startNode
        self.endNode = endNode
        self.muscles = []
        self.length = np.linalg.norm(self.endNode.pos - self.startNode.pos)
        
    def addMuscle(self, muscle):
        self.muscles.append(muscle)
    
    def getMiddle(self):
        return(np.average(self.startNode.pos,self.endNode.pos))

class Muscle:
    def __init__(self, startLine:Line, endLine:Line):
        self.startLine = startLine
        self.endLine = endLine
    
    def contract(self, strength):
        # caped strength when I was based on circular motion to not do multiple laps
        # strength = max(-0.5, min(0.5, strength))

        delta = self.endLine.endNode.pos - self.startLine.endNode.pos
        dist = np.linalg.norm(delta)
        # protection
        if dist == 0:
            return

        direction = delta / dist
        force_vector = direction * strength * 5

        self.startLine.endNode.force += force_vector
        self.endLine.endNode.force -= force_vector
            

line1 = Line(startNode=Node(125,250),endNode=Node(300,100))
line1.startNode.addLine(line1)
line1.endNode.addLine(line1)
line2 = Line(startNode=line1.startNode,endNode=Node(100,250))
line2.startNode.addLine(line2)
line2.endNode.addLine(line2)
muscle = Muscle(line1, line2)

screen.fill(WHITE)
pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
pygame.draw.line(screen, GREEN, line1.startNode.pos, line1.endNode.pos)
pygame.draw.line(screen, RED, line2.startNode.pos, line2.endNode.pos)
pygame.display.flip()
time.sleep(1)
muscle.contract(0.5)
screen.fill(WHITE)
pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
pygame.draw.line(screen, GREEN, line1.startNode.pos, line1.endNode.pos)
pygame.draw.line(screen, RED, line2.startNode.pos, line2.endNode.pos)
pygame.display.flip()

running = True
while running:
    #muscle.contract(0.5)
    line1.endNode.update()
    screen.fill(WHITE)
    pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
    pygame.draw.line(screen, GREEN, line1.startNode.pos, line1.endNode.pos)
    pygame.draw.line(screen, RED, line2.startNode.pos, line2.endNode.pos)
    pygame.display.flip()
    time.sleep(0.1)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False    
        