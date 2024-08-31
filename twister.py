import pygame
import math
from game_settings import *

class Twister:
    def __init__(self):
        self.x = GAME_WIDTH // 2
        self.y = GAME_HEIGHT // 2
        self.image = pygame.image.load('Center_Sun.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (140, 140))  # Adjust size as needed
        self.rotation = 0
        self.rotation_speed = 0  # Adjust this value to change rotation speed

    def update(self):
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        image_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, image_rect)

        # Draw central circles
        for i in range(2):  # Reduced from 3
            offset = i * 5  # Reduced offset
            x = self.x + math.cos(self.rotation + i * 2) * offset
            y = self.y + math.sin(self.rotation + i * 2) * offset