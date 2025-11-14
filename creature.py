# The future goal is to make creatures learn to walk in 2d
# most of the parameters are below
# Currently only the "physic engine" is made the brains still need to be implemented
# /!\ do not make circular creatures


import numpy as np
import pygame
import time
import copy
import keyboard
import threading

WIDTH, HEIGHT = 800, 600
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GROUND = 400
GRAVITY = 0.8
AIR_RES = 0.05
GROUND_RES = 0.4
MUTATION_RATE = 0.7
BATCH = 100
DURATION = 500
FORCE = 2

# comment to not see result
# pygame.init()
# screen = pygame.display.set_mode((WIDTH, HEIGHT))
# clock = pygame.time.Clock()

# todo : add velocity to input 

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
    
    def updateImg(self, dt=1):
        for node in self.nodeList:
            node.update(dt = dt) 
        screen.fill(WHITE)
        pygame.draw.rect(screen,BLACK,(0, GROUND, WIDTH, HEIGHT-GROUND))
        for node in self.nodeList:
            pygame.draw.circle(screen, RED, node.pos, 5)
        for line in self.lineList:
            pygame.draw.line(screen, GREEN, line.startNode.pos, line.endNode.pos)    
        #pygame.display.flip()
    
    def update(self, dt=1):
        for node in self.nodeList:
            node.update(dt = dt) 
        
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
            self.model_b1 = parent.model_b1 + np.random.randn(hidden_size) * MUTATION_RATE * (700-score)/500
            self.model_w2 = parent.model_w2 + np.random.randn(len(self.muscleList), hidden_size) * MUTATION_RATE * (700-score)/500
            self.model_b2 = parent.model_b2 + np.random.randn(len(self.muscleList)) * MUTATION_RATE * (700-score)/500
    
    def copyModel(self, parent):
        self.model_w1 = parent.model_w1
        self.model_b1 = parent.model_b1
        self.model_w2 = parent.model_w2
        self.model_b2 = parent.model_b2
    
    def setModel(self, w1, b1, w2, b2):
        self.model_w1 = w1
        self.model_b1 = b1
        self.model_w2 = w2
        self.model_b2 = b2

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
        strength = max(-FORCE, min(FORCE, strength))

        delta = self.endLine.endNode.pos - self.startLine.endNode.pos
        dist = np.linalg.norm(delta)
        # protection
        if dist == 0:
            return

        direction = delta / dist
        force_vector = direction * strength * 5

        self.startLine.endNode.force += force_vector
        self.endLine.endNode.force -= force_vector

def crawl(creature:Creature):
    global running
    global scores
    for i in range(DURATION):
        creature.forward()
        creature.update(0.5)
        #time.sleep(0.05)
    scores.append(creature.startNode.pos[0] - modelCreature.startNode.pos[0] + (creature.startNode.pos[1]-400)/2)
    print(creature.startNode.pos[0] - modelCreature.startNode.pos[0] + (creature.startNode.pos[1]-400)/2)

def show():
    global running
    pygame.display.flip()    
    pygame.display.flip()    
    demo = copy.deepcopy(modelCreature)
    demo.copyModel(best[0][0])
    for i in range(DURATION):
        demo.forward()
        demo.updateImg(0.5)
        pygame.display.flip()    
        time.sleep(0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

nodes = [Node(250,250),Node(300,310),Node(200,300)]
lines = [Line(startNode=nodes[0],endNode=nodes[1]),Line(startNode=nodes[0],endNode=nodes[2])]
nodes[0].addLine(lines[0])
nodes[1].addLine(lines[0])
nodes[0].addLine(lines[1])
nodes[2].addLine(lines[1])
muscles = [Muscle(lines[0], lines[1])]

modelCreature = Creature(nodes[0], nodeList=nodes, muscleList=muscles, lineList=lines)
creatures = [(copy.deepcopy(modelCreature))for _ in range(BATCH)]
modelBrain = None

if (bool(input("Do you want to start where you left ? jus type if yes"))):
    print("ok")
    bestModel = np.load("./creature_130.npz")
    modelBrain = copy.deepcopy(modelCreature)
    modelBrain.setModel(bestModel['w1'], bestModel['b1'], bestModel['w2'], bestModel['b2'])

for creature in creatures:
    creature.randoModel(modelBrain)

if modelBrain is not None:
    creatures.insert(0,modelBrain)

gen = 0
running = True
while running:
    scores = [] 
    threads = []  
    for creature in creatures:
        t = threading.Thread(target=crawl, args=(creature,))
        threads.append(t)
    # Start each thread
    for t in threads:
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()
    
    best = []
    for i in range(3):
        ind = scores.index(max(scores))
        best.append([creatures[ind],max(scores)])
        scores.pop(ind)
        creatures.pop(ind)
        
    # comment the following line to not the results
    #show() 
    
    creatures = [(copy.deepcopy(modelCreature))for _ in range(BATCH)]
    for i in range(int(BATCH/3)):
        creature.randoModel(parent=best[0][0], score=best[0][1])
    for i in range(int(BATCH/3)):
        creature.randoModel(parent=best[1][0], score=best[1][1])
    for i in range(int(BATCH/3)):
        creature.randoModel(parent=best[2][0], score=best[2][1])    
    
    bestModel = copy.deepcopy(modelCreature)
    bestModel.copyModel(best)
    creatures.append(copy.deepcopy(bestModel))
    
    gen +=1
    
    print("--" + str(max(scores)) + "--")
    print("---------------" + str(gen) + "---------------")
    
    if (keyboard.is_pressed('space')):
        running = False

np.savez("creature", w1 = best.model_w1, b1 = best.model_b1, w2 = best.model_w2, b2 = best.model_b2)