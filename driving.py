from math import sin, cos, degrees
from random import randint, random, choice
import pygame
import numpy as np
import os

WIDTH, HEIGHT = 1200, 800
BLACK = (0,0,0)
GREEN = (0,200,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

car_img = pygame.image.load('./driving_assets/car.png').convert_alpha()
car_img = pygame.transform.scale_by(car_img, 6)

class NeuralNetwork:
    def __init__(self, layers):
        self.layers = layers
        self.w = [np.random.randn(layers[i], layers[i+1]) for i in range(len(layers)-1)]
        self.b = [np.zeros((1, layers[i+1])) for i in range(len(layers)-1)]

    def copy(self):
        nn = NeuralNetwork(self.layers)
        nn.w = [w.copy() for w in self.w]
        nn.b = [b.copy() for b in self.b]
        return nn

    def mutate(self, rate=0.03, scale=0.2):
        for i in range(len(self.w)):
            mask = np.random.rand(*self.w[i].shape) < rate
            self.w[i] += mask * np.random.randn(*self.w[i].shape) * scale
            self.b[i] += (np.random.rand(*self.b[i].shape) < rate) * np.random.randn(*self.b[i].shape) * scale

    def crossover(self, other):
        child = self.copy()
        for i in range(len(self.w)):
            m = np.random.rand(*self.w[i].shape) < 0.5
            child.w[i][m] = other.w[i][m]
            mb = np.random.rand(*self.b[i].shape) < 0.5
            child.b[i][mb] = other.b[i][mb]
        return child

    def forward(self, x):
        a = x
        for i in range(len(self.w)-1):
            a = np.maximum(0, a @ self.w[i] + self.b[i])
        return np.tanh(a @ self.w[-1] + self.b[-1])

    def save(self, filename):
        w_arr = np.empty(len(self.w), dtype=object)
        b_arr = np.empty(len(self.b), dtype=object)

        for i in range(len(self.w)):
            w_arr[i] = self.w[i]
            b_arr[i] = self.b[i]

        np.savez(
            filename,
            w=w_arr,
            b=b_arr,
            layers=np.array(self.layers, dtype=int)
        )



    def load(self, filename):
        data = np.load(filename, allow_pickle=True)

        if "layers" in data:
            self.layers = data["layers"].tolist()
        else:
            self.layers = [w.shape[0] for w in data["w"]]
            self.layers.append(data["w"][-1].shape[1])

        self.w = [w.copy() for w in data["w"]]
        self.b = [b.reshape(1, -1).copy() for b in data["b"]]



class Car:
    def __init__(self, nn):
        self.nn = nn
        self.reset()

    def reset(self):
        self.x = WIDTH//2
        self.y = HEIGHT//2
        self.rot = random() * 6.28
        self.vel = pygame.Vector2(0,0)
        self.fitness = 0
        self.alive = True
        self.prev_dist = None
        self.stuck_timer = 0

    def state(self, target):
        dx = target[0] - self.x
        dy = target[1] - self.y
        fx = sin(self.rot)
        fy = -cos(self.rot)
        goal_forward = (fx*dx + fy*dy) / WIDTH
        goal_side = (fx*dy - fy*dx) / HEIGHT
        speed = self.vel.length() / 5
        return np.array([[speed, goal_forward, goal_side]])

    def update(self, target):
        if not self.alive:
            return

        throttle, steer = self.nn.forward(self.state(target))[0]

        forward = pygame.Vector2(sin(self.rot), -cos(self.rot))
        right = pygame.Vector2(forward.y, -forward.x)

        self.vel += forward * throttle * 0.2
        fs = self.vel.dot(forward) * 0.95
        ss = self.vel.dot(right) * 0.5
        self.rot += steer * (abs(fs)*0.02 + 0.02)
        self.vel = forward * fs + right * ss

        self.x += self.vel.x
        self.y += self.vel.y

        if self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT:
            self.alive = False
            self.fitness -= 50
            return

        dist = ((target[0]-self.x)**2 + (target[1]-self.y)**2) ** 0.5

        if self.prev_dist is not None:
            self.fitness += self.prev_dist - dist

        if self.vel.length() < 0.05:
            self.stuck_timer += 1
            if self.stuck_timer > 60:
                self.alive = False
                self.fitness -= 20
        else:
            self.stuck_timer = 0

        if dist < 20:
            self.fitness += 200
            self.alive = False

        self.prev_dist = dist

    def draw(self):
        img = pygame.transform.rotate(car_img, -degrees(self.rot))
        r = img.get_rect(center=(self.x,self.y))
        screen.blit(img, r.topleft)

POP_SIZE = 40
ELITE = 8
GEN_TIME = 600
MODEL_FILE = "driving_model.npz"

population = []
base_nn = NeuralNetwork([3,32,32,2])

if os.path.exists(MODEL_FILE):
    base_nn.load(MODEL_FILE)
    population = [Car(base_nn.copy()) for _ in range(POP_SIZE)]
else:
    population = [Car(NeuralNetwork([3,32,32,2])) for _ in range(POP_SIZE)]

frame = 0
generation = 1
target = [randint(100, WIDTH-100), randint(100, HEIGHT-100)]

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    alive = False
    for car in population:
        car.update(target)
        if car.alive:
            alive = True
            car.draw()

    pygame.draw.rect(screen, GREEN, (target[0]-10, target[1]-10, 20, 20))
    pygame.display.flip()
    clock.tick(60)

    frame += 1
    if frame > GEN_TIME or not alive:
        population.sort(key=lambda c: c.fitness, reverse=True)
        elites = population[:ELITE]

        elites[0].nn.save(MODEL_FILE)

        new_pop = [Car(e.nn.copy()) for e in elites]
        while len(new_pop) < POP_SIZE:
            p1, p2 = choice(elites), choice(elites)
            nn = p1.nn.crossover(p2.nn)
            nn.mutate()
            new_pop.append(Car(nn))

        population = new_pop
        for car in population:
            car.reset()

        target = [randint(100, WIDTH-100), randint(100, HEIGHT-100)]
        frame = 0
        generation += 1
        print("Generation", generation, "Best fitness", elites[0].fitness)

pygame.quit()
