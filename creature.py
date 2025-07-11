# The future goal is to make creatures learn to walk in 2d
# most of the parameters are below
# Currently only the "physic engine" is made the brains still need to be implemented
# /!\ do not make circular creatures


import numpy as np
import pygame
import time
import copy
import keyboard

WIDTH, HEIGHT = 800, 600
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GROUND = 400
GRAVITY = 0.8
AIR_RES = 0.05
GROUND_RES = 0.4
MUTATION_RATE = 0.3
BATCH = 10
DURATION = 500

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

class Creature:
    def __init__(self,startNode, parent = None, nodeList = [],  muscleList = [], lineList = []):
        self.startNode = startNode
        self.nodeList = nodeList
        self.muscleList = muscleList
        self.lineList = lineList
        hidden_size = len(lineList)*3
        if parent is None:
            #adding a hidden layer to make it possible for them to truly learn
            self.model_w1 = np.random.randn(hidden_size, len(lineList)*4)
            self.model_b1 = np.zeros(hidden_size)
            self.model_w2 = np.random.randn(len(muscleList), hidden_size)
            self.model_b2 = np.zeros(len(muscleList))
        else:
            self.model_w1 = parent.model_w1 + np.random.randn(hidden_size, len(lineList)*4) * MUTATION_RATE
            self.model_b1 = parent.model_b1 + np.zeros(hidden_size) * MUTATION_RATE
            self.model_w2 = parent.model_w2 + np.random.randn(len(muscleList), hidden_size) * MUTATION_RATE
            self.model_b2 = parent.model_b2 + np.zeros(len(muscleList)) * MUTATION_RATE
    
    def update(self, dt=1):
        for node in self.nodeList:
            node.update(dt = dt) 
        screen.fill(WHITE)
        pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
        for node in self.nodeList:
            pygame.draw.circle(screen, RED, node.pos, 5)
        for line in self.lineList:
            pygame.draw.line(screen, GREEN, line.startNode.pos, line.endNode.pos)    
        pygame.display.flip()
        
    def forward(self):
        state = []
        for line in self.lineList:
            state.append(line.startNode.pos[0])
            state.append(line.startNode.pos[1])
            state.append(line.endNode.pos[0])
            state.append(line.endNode.pos[1])
        x = np.dot(self.model_w1,state) + self.model_b1
        # adapted relu to make it possible to have negative value 
        x = x * (x > -0.5)
        output = np.dot(self.model_w2, x) + self.model_b2
        for i in range(len(output)):
            self.muscleList[i].contract(output[i])
            
    def randoModel(self, parent = None, score = 0):
        hidden_size = len(self.lineList)*3
        if parent is None:
            #adding a hidden layer to make it possible for them to truly learn
            self.model_w1 = np.random.randn(hidden_size, len(self.lineList)*4)
            self.model_b1 = np.zeros(hidden_size)
            self.model_w2 = np.random.randn(len(self.muscleList), hidden_size)
            self.model_b2 = np.zeros(len(self.muscleList))
        else:
            self.model_w1 = parent.model_w1 + np.random.randn(hidden_size, len(self.lineList)*4) * MUTATION_RATE * (700-score)/500
            self.model_b1 = parent.model_b1 + np.zeros(hidden_size) * MUTATION_RATE * (700-score)/500
            self.model_w2 = parent.model_w2 + np.random.randn(len(self.muscleList), hidden_size) * MUTATION_RATE * (700-score)/500
            self.model_b2 = parent.model_b2 + np.zeros(len(self.muscleList)) * MUTATION_RATE * (700-score)/500

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

        if self.pos[1] > GROUND:
            self.pos += velocity * (1-GROUND_RES) + self.force * dt * dt
            self.pos[1] = GROUND
            self.prev_pos[1] = self.pos[1] + velocity[1] * -0.5
        else:
            self.pos += velocity * (1-AIR_RES) + self.force * dt * dt
            
        if self.pos[0] < 0:
            self.pos[0] = 0
            self.prev_pos[0] = self.pos[0] + velocity[0] * -0.5

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
            #if launcher!=other:
            #    other.update(launcher=self)

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
        strength = max(-1, min(1, strength))

        delta = self.endLine.endNode.pos - self.startLine.endNode.pos
        dist = np.linalg.norm(delta)
        # protection
        if dist == 0:
            return

        direction = delta / dist
        force_vector = direction * strength * 5

        self.startLine.endNode.force += force_vector
        self.endLine.endNode.force -= force_vector
            

nodes = [Node(250,250),Node(300,310),Node(200,300)]
lines = [Line(startNode=nodes[0],endNode=nodes[1]),Line(startNode=nodes[0],endNode=nodes[2])]
nodes[0].addLine(lines[0])
nodes[1].addLine(lines[0])
nodes[0].addLine(lines[1])
nodes[2].addLine(lines[1])
muscles = [Muscle(lines[0], lines[1])]

modelCreature = Creature(nodes[0], nodeList=nodes, muscleList=muscles, lineList=lines)
creatures = [(copy.deepcopy(modelCreature))for _ in range(BATCH)]
for creature in creatures:
    creature.randoModel()

gen = 0
running = True
while running:
    scores = []    
    for creature in creatures:
        for i in range(DURATION):
            creature.forward()
            creature.update(0.5)
            #time.sleep(0.05)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
        scores.append(creature.startNode.pos[0] - modelCreature.startNode.pos[0] + (400-creature.startNode.pos[1])/2)
        print(scores[-1])
    
    best = creatures[scores.index(max(scores))]    
    creatures = [(copy.deepcopy(modelCreature))for _ in range(BATCH)]
    for creature in creatures:
        creature.randoModel(parent=best, score=max(scores))
    creatures.append(copy.deepcopy(best))
    gen +=1
    print("--" + str(max(scores)) + "--")
    print("---------------" + str(gen) + "---------------")

np.savez("creature", w1 = best.model_w1, b1 = best.model_b1, w2 = best.model_w2, b2 = best.model_b2)