import pygame
import random
import math
from game_settings import *

class BackgroundParticle:
    def __init__(self):
        self.x = random.randint(0, GAME_WIDTH)
        self.y = random.randint(0, GAME_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        if self.x < 0 or self.x > GAME_WIDTH or self.y < 0 or self.y > GAME_HEIGHT:
            self.x = random.randint(0, GAME_WIDTH)
            self.y = random.randint(0, GAME_HEIGHT)

    def draw(self, screen):
        pygame.draw.circle(screen, LIGHT_GREY, (int(self.x), int(self.y)), self.size)