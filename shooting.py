import pygame
import numpy as np
import math
import random

WHITE=(255,255,255)
BLACK=(0,0,0)
RED=(255,0,0)
BLUE=(0,0,255)
GREEN=(0,255,0)

WIDTH,HEIGHT=800,600

INPUT_SIZE=9
HIDDEN_SIZE=16
OUTPUT_SIZE=3

BASE_HEALTH=200
PLAYER_SPEED=10
PLAYER_SIZE=5
TURN_SPEED=0.15

COOLDOWN=0.6
BULLET_RANGE=350
BULLET_SIZE=2
BULLET_DAMAGE=50

POPULATION_SIZE=60
ELITE_COUNT=4
MUTATION_RATE=0.01
GENERATION_TIME=800

ZONE_SHRINK_RATE=0.15
ZONE_DAMAGE=2

pygame.init()
screen=pygame.display.set_mode((WIDTH,HEIGHT))
clock=pygame.time.Clock()

players=[]
bullets=[]
frame_count=0
generation=0

zone_x=WIDTH//2
zone_y=HEIGHT//2
max_zone_radius=min(WIDTH,HEIGHT)//2
zone_radius=max_zone_radius

class NeuralNetwork:
    def __init__(self,weights=None):
        if weights is None:
            self.W1=np.random.randn(HIDDEN_SIZE,INPUT_SIZE)*0.5
            self.b1=np.zeros(HIDDEN_SIZE)
            self.W2=np.random.randn(OUTPUT_SIZE,HIDDEN_SIZE)*0.5
            self.b2=np.zeros(OUTPUT_SIZE)
        else:
            self.W1,self.b1,self.W2,self.b2=weights
    def forward(self,x):
        a1=np.tanh(self.W1@x+self.b1)
        return np.tanh(self.W2@a1+self.b2)
    def mutate(self):
        def m(w): return w+np.random.randn(*w.shape)*MUTATION_RATE
        return NeuralNetwork((m(self.W1),m(self.b1),m(self.W2),m(self.b2)))
    @staticmethod
    def crossover(a,b):
        def mix(x,y):
            mask=np.random.rand(*x.shape)<0.5
            return np.where(mask,x,y)
        return NeuralNetwork((mix(a.W1,b.W1),mix(a.b1,b.b1),mix(a.W2,b.W2),mix(a.b2,b.b2)))

def compute_state(ind):
    enemies=[p for p in players if p!=ind]
    if enemies:
        e=min(enemies,key=lambda p:(p.x-ind.x)**2+(p.y-ind.y)**2)
        dx=e.x-ind.x
        dy=e.y-ind.y
        d=math.hypot(dx,dy)
        a=math.atan2(dy,dx)-ind.dir
    else:
        d=0
        a=0
    dz=math.hypot(ind.x-zone_x,ind.y-zone_y)/zone_radius
    return np.array([
        ind.x/WIDTH,
        ind.y/HEIGHT,
        math.tanh(d/300),
        math.sin(a),
        math.cos(a),
        dz,
        math.cos(ind.dir),
        math.sin(ind.dir),
        zone_radius/max_zone_radius
    ])

class Ind:
    def __init__(self,x,y,model):
        self.x=x
        self.y=y
        self.vx=0
        self.vy=0
        self.dir=random.uniform(-math.pi,math.pi)
        self.lastShot=0
        self.health=BASE_HEALTH
        self.model=model
        self.fitness=0
        self.alive=True
    def decide(self):
        s=compute_state(self)
        o=self.model.forward(s)
        speed=(o[0]+1)/2
        self.vx=speed*PLAYER_SPEED*math.cos(self.dir)
        self.vy=speed*PLAYER_SPEED*math.sin(self.dir)
        self.dir+=o[1]*TURN_SPEED
        self.dir=(self.dir+math.pi)%(2*math.pi)-math.pi
        if o[2]>0.3:
            self.fire()
    def update(self):
        self.lastShot+=0.05
        self.x+=self.vx
        self.y+=self.vy
        self.x=max(10,min(WIDTH-10,self.x))
        self.y=max(10,min(HEIGHT-10,self.y))
        dist=math.hypot(self.x-zone_x,self.y-zone_y)
        if dist>zone_radius:
            self.health-=ZONE_DAMAGE
            self.fitness-=2
        else:
            self.fitness+=2
            self.fitness+=1-dist/zone_radius
        if self.health<=0:
            self.alive=False
        self.fitness+=0.5
    def fire(self):
        if self.lastShot>COOLDOWN:
            bullets.append(Bullet(self))
            self.lastShot=0
    def hit(self):
        self.health-=BULLET_DAMAGE
        if self.health<=0:
            self.alive=False
    def draw(self):
        pygame.draw.circle(screen,BLUE,(int(self.x),int(self.y)),PLAYER_SIZE)
        ex=self.x+15*math.cos(self.dir)
        ey=self.y+15*math.sin(self.dir)
        pygame.draw.line(screen,BLACK,(int(self.x),int(self.y)),(int(ex),int(ey)),2)

class Bullet:
    def __init__(self,p):
        self.p=p
        self.x=p.x
        self.y=p.y
        self.dir=p.dir
        self.vel=10
        self.dist=0
        self.alive=True
    def update(self):
        self.x+=self.vel*math.cos(self.dir)
        self.y+=self.vel*math.sin(self.dir)
        self.dist+=self.vel
        self.vel*=0.99
        if self.dist>BULLET_RANGE:
            self.alive=False
    def hit(self):
        for pl in players:
            if pl!=self.p and pl.alive:
                if math.hypot(pl.x-self.x,pl.y-self.y)<PLAYER_SIZE:
                    pl.hit()
                    self.p.fitness+=300
                    self.alive=False
                    return
    def draw(self):
        pygame.draw.circle(screen,RED,(int(self.x),int(self.y)),BULLET_SIZE)

def new_generation(sorted_players):
    global players,bullets,frame_count,generation,zone_radius
    bullets.clear()
    players.clear()
    if len(sorted_players)==0:
        for _ in range(POPULATION_SIZE):
            players.append(Ind(random.randint(50,WIDTH-50),random.randint(50,HEIGHT-50),NeuralNetwork()))
        frame_count=0
        zone_radius=max_zone_radius
        generation+=1
        return
    elite_count=max(1,min(ELITE_COUNT,len(sorted_players)))
    elites=sorted_players[:elite_count]
    for p in elites:
        players.append(Ind(random.randint(50,WIDTH-50),random.randint(50,HEIGHT-50),p.model))
    while len(players)<POPULATION_SIZE:
        if len(elites)>=2:
            p1,p2=random.sample(elites,2)
        else:
            p1=p2=elites[0]
        child=NeuralNetwork.crossover(p1.model,p2.model).mutate()
        players.append(Ind(random.randint(50,WIDTH-50),random.randint(50,HEIGHT-50),child))
    frame_count=0
    zone_radius=max_zone_radius
    generation+=1

players=[Ind(random.randint(50,WIDTH-50),random.randint(50,HEIGHT-50),NeuralNetwork()) for _ in range(POPULATION_SIZE)]

running=True
while running:
    # clock.tick(60)
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
    frame_count+=1
    zone_radius=max(40,zone_radius-ZONE_SHRINK_RATE)
    pygame.draw.circle(screen,GREEN,(zone_x,zone_y),int(zone_radius),1)
    for p in players:
        p.decide()
        p.update()
        if p.alive:
            p.draw()
    for b in bullets:
        b.update()
        b.hit()
        if b.alive:
            b.draw()
    bullets[:]=[b for b in bullets if b.alive]
    players[:]=[p for p in players if p.alive]
    if frame_count>GENERATION_TIME or len(players)<=ELITE_COUNT:
        players.sort(key=lambda p:p.fitness,reverse=True)
        new_generation(players)
        print(generation)
    pygame.display.flip()

pygame.quit()
