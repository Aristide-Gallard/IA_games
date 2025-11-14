from math import degrees, sin, cos
from random import randint
from os import path
import pygame
#import pytorch

WIDTH, HEIGHT = 1200, 800
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BROWN = (139, 69, 19)
LIGHT_BLUE = (150, 150, 255)
GREEN = (0, 200, 0)
grid_size = 20
points = 0

COLORS = [GRAY, BROWN, LIGHT_BLUE, GREEN, WHITE]

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

car_path = './driving_assets/car.png'
if path.exists(car_path):
    car_img = pygame.image.load(car_path).convert_alpha()
    car_img = pygame.transform.scale_by(car_img, 6)

# [rolling_resistance, forward_grip, lateral_grip, color]
terrainType = [
    [0.02, 0.4, 0.9, 0],   # Asphalt: moderate acceleration, good control
    [0.045, 0.28, 0.6, 1],   # Dirt: slower acceleration, more slide
    [0.0025, 0.2, 0.15, 2],  # Ice: minimal friction, very weak steering
    [0.055, 0.25, 0.7, 3],   # Grass: slower and draggier, still steerable
]


class Terrain:
    def __init__(self, type_index, pos):
        self.x, self.y = pos
        base_terrain = terrainType[type_index]
        self.rr = base_terrain[0]
        self.forward_grip = base_terrain[1]
        self.lateral_grip = base_terrain[2]
        self.width = grid_size
        self.height = grid_size
        self.color = COLORS[base_terrain[3]]
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)


    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Obstacle:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, grid_size, grid_size)


    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)


class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation = 0
        self.velocity = pygame.Vector2(0, 0)
        self.width = car_img.get_width()
        self.height = car_img.get_height()
        self.acceleration = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
      rotated_image = pygame.transform.rotate(car_img, - degrees(self.rotation))
      new_rect = rotated_image.get_rect(center=self.rect.center)
      surface.blit(rotated_image, new_rect.topleft)

    def get_terrain_under(self, terrains):
        for t in terrains:
            if self.rect.colliderect(t.rect):
                return t
        return None

    def move(self, keys, terrains, obstacles):
        terrain = self.get_terrain_under(terrains)
        rr, forward_grip, lateral_grip = 0.07, 0.97, 0.9
        if terrain:
            rr = terrain.rr
            forward_grip = terrain.forward_grip
            lateral_grip = terrain.lateral_grip

        accel_strength = 0.17 * forward_grip
        brake_strength = 0.1 * forward_grip

        if keys[pygame.K_z]:
            self.acceleration = accel_strength
        elif keys[pygame.K_s]:
            self.acceleration = -brake_strength
        else:
            self.acceleration = 0

        forward = pygame.Vector2(sin(self.rotation), -cos(self.rotation))
        right = pygame.Vector2(forward.y, -forward.x)

        self.velocity += forward * self.acceleration
        forward_speed = self.velocity.dot(forward)
        side_speed = self.velocity.dot(right)
        forward_speed *= (1 - rr)

        traction_limit = 4.0
        if abs(side_speed) < lateral_grip * traction_limit:
            side_speed *= 0.3
        else:
            side_speed *= 0.97

        speed_mag = abs(forward_speed)
        if speed_mag > 0.2:
            turn_rate = 0.03 + min(speed_mag * 0.015, 0.05)
            if keys[pygame.K_q]:
                self.rotation -= turn_rate
            if keys[pygame.K_d]:
                self.rotation += turn_rate

        self.velocity = forward * forward_speed + right * side_speed

        dx, dy = self.velocity.x, self.velocity.y
        next_rect = self.rect.move(dx, dy)
        for obs in obstacles:
            if next_rect.colliderect(obs.rect):
                dx *= -0.005
                dy *= -0.005
                next_rect = self.rect.move(dx, dy)

        self.x += dx
        self.y += dy
        self.x = max(0, min(self.x, WIDTH - self.width))
        self.y = max(0, min(self.y, HEIGHT - self.height))

        


car = Car(WIDTH // 2, HEIGHT // 2)
terrains = []
obstacles = []
currentTerrain = 0
objective = [randint(10,WIDTH-10), randint(10,HEIGHT-10)]

running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if event.button == 1:
                terrains.append(
                    Terrain(
                        currentTerrain,
                        (
                            pos[0] // grid_size * grid_size,
                            pos[1] // grid_size * grid_size,
                        ),
                    )
                )
            elif event.button == 3:
                obstacles.append(Obstacle(pos[0] // grid_size * grid_size,
                                          pos[1] // grid_size * grid_size))
            elif event.button == 4:
                if grid_size>10:
                    grid_size /= 2
            elif event.button ==5:
                grid_size *=2
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                currentTerrain = 0
                print("changing terrain")
            elif event.key == pygame.K_2:
                currentTerrain = 1
                print("changing terrain")
            elif event.key == pygame.K_3:
                currentTerrain = 2
                print("changing terrain")
            elif event.key == pygame.K_4:
                currentTerrain = 3
                print("changing terrain")

    keys = pygame.key.get_pressed()
    car.move(keys, terrains, obstacles)

    for t in terrains:
        t.draw(screen)
    for o in obstacles:
        o.draw(screen)
    car.draw(screen)
    pygame.draw.rect(screen, GREEN, (objective[0], objective[1], 20, 20))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
