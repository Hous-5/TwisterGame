import pygame
import math
from game_settings import *

class Player:
    def __init__(self):
        self.angle = 0
        self.update_position()
        self.image = pygame.image.load('Player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_RADIUS*2.3, PLAYER_RADIUS*2.3))

    def update_position(self):
        self.x = GAME_WIDTH // 2 + math.cos(self.angle) * RING_RADIUS
        self.y = GAME_HEIGHT // 2 + math.sin(self.angle) * RING_RADIUS    

    def move(self, clockwise, difficulty_multiplier):
        speed = PLAYER_SPEED * difficulty_multiplier
        if clockwise:
            self.angle += speed / RING_RADIUS
        else:
            self.angle -= speed / RING_RADIUS
        self.update_position()

    def draw(self, screen):
        image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, image_rect)

    def collides_with(self, dot):
        return math.hypot(dot.x - self.x, dot.y - self.y) < PLAYER_RADIUS + DOT_RADIUS