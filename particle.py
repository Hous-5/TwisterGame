import pygame
import random
import math

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = random.randint(2, 5)
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.lifetime = random.uniform(0.5, 1.5)

    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * dt
        self.y += math.sin(self.angle) * self.speed * dt
        self.lifetime -= dt
        self.radius = max(0, self.radius - dt)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.radius))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self, dt):
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)