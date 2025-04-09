# This is a simulation where there is 3 tribes with each one eating another.
# The equation is linear so don't expect any inteligent comportment.
# It's simple but fun to watch. For the more serious projects I will maybe post them later.

import numpy as np
import pygame

# Initialize pygame
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# AI Model Parameters
INPUT_SIZE = 8 
OUTPUT_SIZE = 2
MUTATION_RATE = 0.1
ENERGY_TO_REPRODUCE = 100
ENERGY_LOSS_PER_TICK = 1 # lose energy when it is near a wall 
EAT_DISTANCE = 10

class Individual:
    def __init__(self, x, y, vx=0, vy=0, tribe=0, model=None):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.tribe = tribe  # 0, 1, or 2
        self.color = [RED, BLUE, GREEN][tribe]
        self.energy = 50
        
        if model is None:
            self.model = np.random.randn(OUTPUT_SIZE, INPUT_SIZE)
        else:
            self.model = model + (np.random.randn(OUTPUT_SIZE, INPUT_SIZE) * MUTATION_RATE)
    
    def update_position(self):
        self.x += self.vx
        self.y += self.vy
        self.x = max(10, min(WIDTH-10, self.x))
        self.y = max(10, min(HEIGHT-10, self.y))
        if (self.x==10 or self.x==WIDTH-10 or self.y==10 or self.y==HEIGHT-10):
            self.energy -= ENERGY_LOSS_PER_TICK
    
    def decide_movement(self, state):
        output = np.dot(self.model, state)
        self.vx, self.vy = np.tanh(output)
    
    def eat(self, other):
        if np.linalg.norm([self.x - other.x, self.y - other.y]) < EAT_DISTANCE:
            self.energy += 110
            return True
        return False
    
    def reproduce(self):
        if self.energy >= ENERGY_TO_REPRODUCE:
            self.energy /= 2
            return Individual(self.x, self.y, tribe=self.tribe, model=self.model)
        return None
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)

def compute_state(x, y, vx, vy, prey_positions, predator_positions, k=3):
    def get_nearest(positions, k):
        if not positions:
            return np.zeros(k), np.zeros(k)
        distances = np.array([np.linalg.norm([x - px, y - py]) for px, py in positions])
        angles = np.array([np.arctan2(py - y, px - x) for px, py in positions])
        sorted_indices = np.argsort(distances)[:k]
        return distances[sorted_indices], angles[sorted_indices]
    
    d_prey, theta_prey = get_nearest(prey_positions, k)
    d_pred, theta_pred = get_nearest(predator_positions, k)
    
    avg_d_prey = np.mean(d_prey) if len(d_prey) > 0 else 0
    avg_theta_prey = np.mean(theta_prey) if len(theta_prey) > 0 else 0
    avg_d_pred = np.mean(d_pred) if len(d_pred) > 0 else 0
    avg_theta_pred = np.mean(theta_pred) if len(theta_pred) > 0 else 0
    
    state = np.array([x, y, vx, vy, avg_d_prey, avg_theta_prey, avg_d_pred, avg_theta_pred])
    return state

num_individuals = 20
tribes = [
    [Individual(np.random.randint(0, WIDTH), np.random.randint(0, HEIGHT), tribe=i) for _ in range(num_individuals)]
    for i in range(3)
]

lastIndTribe = [0,0,0]
score = [0,0,0]

running = True
while running:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    new_individuals = []
    
    for i in range(3):
        prey_positions = [(p.x, p.y) for p in tribes[(i + 1)%3]]  # Eats this
        predator_positions = [(p.x, p.y) for p in tribes[(i - 1)%3]]  # Gets eaten by this
        ally_position = [(p.x, p.y) for p in tribes[i%3]]
        
        for ind in tribes[i]:
            state = compute_state(ind.x, ind.y, ind.vx, ind.vy, prey_positions, predator_positions)
            ind.decide_movement(state)
            ind.update_position()
            
            for prey in tribes[(i + 1) % 3][:]:
                if ind.eat(prey):
                    tribes[(i + 1) % 3].remove(prey)
            
            offspring = ind.reproduce()
            if offspring:
                new_individuals.append(offspring)
            
            if ind.energy > 0:
                ind.draw(screen)
            else:
                tribes[i].remove(ind)
            if len(tribes[i%3])==1:
                lastIndTribe[i%3]=ind.model

    
    for new_ind in new_individuals:
        tribes[new_ind.tribe].append(new_ind)
    if  len(tribes[0])+len(tribes[1])+len(tribes[2])==1:
        if len(tribes[0])==1:
            print("red win")
            score[0]+=1
        elif len(tribes[1])==1:
            print("blue win")
            score[1]+=1
        else:
            print("green win")
            score[2]+=1
        
        tribes = [
    [Individual(np.random.randint(0, WIDTH), np.random.randint(0, HEIGHT), tribe=i,model=lastIndTribe[i]) for _ in range(num_individuals)]
    for i in range(3)]
    
    pygame.display.flip()
    clock.tick(0)

pygame.quit()
print(score)