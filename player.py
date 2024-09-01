import pygame
import math
from game_settings import *

class Player:
    def __init__(self):
        self.angle = 0
        self.update_position()
        self.image = pygame.image.load('Player.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_RADIUS*2.3, PLAYER_RADIUS*2.3))
        self.combo = 0
        self.combo_timer = 0
        self.score_multiplier = 1
        self.speed_multiplier = 1
        self.invincible = False

    def update_position(self):
        self.x = GAME_WIDTH // 2 + math.cos(self.angle) * RING_RADIUS
        self.y = GAME_HEIGHT // 2 + math.sin(self.angle) * RING_RADIUS    

    def move(self, clockwise, difficulty_multiplier):
        speed = PLAYER_SPEED * difficulty_multiplier * self.speed_multiplier
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
    
    def update(self, dt):
        self.combo_timer -= dt
        if self.combo_timer <= 0:
            self.combo = 0

    def increase_combo(self):
        self.combo += 1
        self.combo_timer = 2  # Reset combo timer to 2 seconds

    def get_score_multiplier(self):
        return self.score_multiplier * (1 + self.combo * 0.1)  # 10% increase per combo level