import pygame
import random
import math
from game_settings import *

class PowerUp:
    def __init__(self):
        self.angle = random.uniform(0, 2 * math.pi)
        self.distance = 50
        self.type = random.choice(["speed", "score", "invincibility"])
        self.update_position()
        self.duration = 5  # seconds

    def update_position(self):
        self.x = GAME_WIDTH // 2 + math.cos(self.angle) * self.distance
        self.y = GAME_HEIGHT // 2 + math.sin(self.angle) * self.distance

    def move(self, difficulty_multiplier):
        speed = PLAYER_SPEED * difficulty_multiplier
        self.angle += 0.02 * difficulty_multiplier
        self.distance += speed * 1.2
        self.update_position()

    def draw(self, screen):
        color = BLUE if self.type == "speed" else PURPLE if self.type == "score" else ORANGE
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), DOT_RADIUS)

class PowerUpManager:
    def __init__(self):
        self.power_ups = []
        self.active_power_up = None
        self.active_time = 0

    def spawn_power_up(self):
        if random.random() < 0.02:  # 2% chance to spawn a power-up each frame
            self.power_ups.append(PowerUp())

    def update(self, player, difficulty_multiplier, dt):
        self.spawn_power_up()
        
        for power_up in self.power_ups[:]:
            power_up.move(difficulty_multiplier)
            if player.collides_with(power_up):
                self.activate_power_up(power_up, player)
                self.power_ups.remove(power_up)

        if self.active_power_up:
            self.active_time += dt
            if self.active_time >= self.active_power_up.duration:
                self.deactivate_power_up(player)

    def activate_power_up(self, power_up, player):
        self.active_power_up = power_up
        self.active_time = 0
        if power_up.type == "speed":
            player.speed_multiplier = 2
        elif power_up.type == "score":
            player.score_multiplier = 2
        elif power_up.type == "invincibility":
            player.invincible = True

    def deactivate_power_up(self, player):
        if self.active_power_up.type == "speed":
            player.speed_multiplier = 1
        elif self.active_power_up.type == "score":
            player.score_multiplier = 1
        elif self.active_power_up.type == "invincibility":
            player.invincible = False
        self.active_power_up = None

    def draw(self, screen):
        for power_up in self.power_ups:
            power_up.draw(screen)