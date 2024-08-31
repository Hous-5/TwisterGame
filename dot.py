import pygame
import random
import math
from game_settings import *

class Dot:
    def __init__(self):
        self.angle = random.uniform(0, 2 * math.pi)
        self.distance = 50
        self.good = random.choice([True, False])
        self.update_position()

    def update_position(self):
        self.x = GAME_WIDTH // 2 + math.cos(self.angle) * self.distance
        self.y = GAME_HEIGHT // 2 + math.sin(self.angle) * self.distance

    def move(self, difficulty_multiplier):
        speed = PLAYER_SPEED * difficulty_multiplier
        self.angle += 0.02 * difficulty_multiplier
        self.distance += speed * 1.2
        self.update_position()

    def draw(self, screen):
        color = GREEN if self.good else RED
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), DOT_RADIUS)