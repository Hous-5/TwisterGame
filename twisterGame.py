import pygame
import math
import random

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1280
FPS = 60
BACKGROUND_COLOR = (30, 30, 30) # Dark Background Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GREY = (200, 200, 200)
LIGHT_GREY = (94, 94, 94) # Color for particles

# Game settings
RING_RADIUS = min(SCREEN_WIDTH, SCREEN_HEIGHT) // 3
PLAYER_RADIUS = 20
DOT_RADIUS = 10
PLAYER_SPEED = 4
DOT_SPAWN_RATE = 10
DIFFICULTY_INCREASE_RATE = 1.0002
RING_THICKNESS = 13

# Initialize the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Twister Game")
clock = pygame.time.Clock()

# Load image assets
player_image = pygame.image.load('Player.png').convert_alpha()
twister_image = pygame.image.load('Center_Sun.png').convert_alpha()

# Resize images if necessary
player_image = pygame.transform.scale(player_image, (PLAYER_RADIUS*2.3, PLAYER_RADIUS*2.3))
twister_image = pygame.transform.scale(twister_image, (170, 170))  # Adjust size as needed

# Load sounds
pygame.mixer.music.load('endlessmotion.mp3')  # Replace with your music file
collect_sound = pygame.mixer.Sound('coin_collect.wav')  # Replace with your collect sound file
game_over_sound = pygame.mixer.Sound('game_over.wav')  # Replace with your game over sound file
menu_select_sound = pygame.mixer.Sound('menu_select.wav')  # Replace with your menu select sound file
menu_click_sound = pygame.mixer.Sound('menu_click.wav')  # Replace with your menu click sound file

# Volume settings
master_volume = 0.5
music_volume = 0.25
sfx_volume = 0.25

def update_volumes():
    pygame.mixer.music.set_volume(master_volume * music_volume)
    collect_sound.set_volume(master_volume * sfx_volume)
    game_over_sound.set_volume(master_volume * sfx_volume)
    menu_select_sound.set_volume(master_volume * sfx_volume)
    menu_click_sound.set_volume(master_volume * sfx_volume)

update_volumes()
pygame.mixer.music.play(-1)  # -1 means loop indefinitely

class Player:
    def __init__(self):
        self.angle = 0
        self.update_position()
        self.image = player_image

    def update_position(self):
        self.x = SCREEN_WIDTH // 2 + math.cos(self.angle) * RING_RADIUS
        self.y = SCREEN_HEIGHT // 2 + math.sin(self.angle) * RING_RADIUS    

    def move(self, clockwise):
        speed = PLAYER_SPEED * difficulty_multiplier
        if clockwise:
            self.angle += speed / RING_RADIUS
        else:
            self.angle -= speed / RING_RADIUS
        self.update_position()

    def draw(self):
        # Calculate the position to center the image on the player's position
        image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(self.image, image_rect)

class Dot:
    def __init__(self):
        self.angle = random.uniform(0, 2 * math.pi)
        self.distance = 50
        self.good = random.choice([True, False])
        self.update_position()

    def update_position(self):
        self.x = SCREEN_WIDTH // 2 + math.cos(self.angle) * self.distance
        self.y = SCREEN_HEIGHT // 2 + math.sin(self.angle) * self.distance

    def move(self):
        speed = PLAYER_SPEED * difficulty_multiplier
        self.angle += 0.02 * difficulty_multiplier
        self.distance += speed * 1.2
        self.update_position()

    def draw(self):
        color = GREEN if self.good else RED
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), DOT_RADIUS)

class Twister:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.image = twister_image
        self.rotation = 0
        self.rotation_speed = 0  # Adjust this value to change rotation speed

    def update(self):
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation -= 360

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, self.rotation)
        image_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, image_rect)

        # Draw central circles
        for i in range(2):  # Reduced from 3
            offset = i * 5  # Reduced offset
            x = self.x + math.cos(self.rotation + i * 2) * offset
            y = self.y + math.sin(self.rotation + i * 2) * offset

class BackgroundParticle:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2)
        self.angle = random.uniform(0, 2 * math.pi)

    def move(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        if self.x < 0 or self.x > SCREEN_WIDTH or self.y < 0 or self.y > SCREEN_HEIGHT:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)

    def draw(self):
        pygame.draw.circle(screen, LIGHT_GREY, (int(self.x), int(self.y)), self.size)

def draw_background(time, particles):
    # Dark Grey background
    screen.fill(BACKGROUND_COLOR)

    # Draw and move particles
    for particle in particles:
        particle.move()
        particle.draw()

def draw_menu(menu_items, selected_item, hovered_item):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 48)
    menu_rects = []
    for i, item in enumerate(menu_items):
        if i == selected_item:
            color = ORANGE
        elif i == hovered_item:
            color = ORANGE
        else:
            color = WHITE
        text = font.render(item, True, color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100 + i * 60))
        screen.blit(text, text_rect)
        menu_rects.append(text_rect)
    return menu_rects

def draw_settings(selected_item, hovered_item):
    screen.fill((0, 0, 0))
    font = pygame.font.Font(None, 36)
    
    volumes = [
        ("Master Volume", master_volume),
        ("Music Volume", music_volume),
        ("SFX Volume", sfx_volume)
    ]
    
    volume_rects = []
    for i, (label, value) in enumerate(volumes):
        if i == selected_item:
            color = ORANGE
        elif i == hovered_item:
            color = ORANGE
        else:
            color = WHITE
        text = font.render(label, True, color)
        screen.blit(text, (50, 100 + i * 100))
        
        bar_rect = pygame.Rect(50, 140 + i * 100, 300, 20)
        pygame.draw.rect(screen, GREY, bar_rect)
        pygame.draw.rect(screen, color, (50, 140 + i * 100, 300 * value, 20))
        volume_rects.append(bar_rect)
        
    back_text = font.render("Back to Menu", True, WHITE if hovered_item != 3 else ORANGE)
    back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
    screen.blit(back_text, back_rect)
    
    return volume_rects, back_rect

# Game variables
player = Player()
dots = []
twister = Twister()
score = 0
game_over = False
clockwise = True
difficulty_multiplier = 1
frames_since_last_spawn = 0
time = 0

# Create background particles
background_particles = [BackgroundParticle() for _ in range(50)]

# Menu variables
menu_items = ["Start Game", "Settings", "Quit"]
selected_item = -1
hovered_item = -1
game_state = "menu"

# Game loop
running = True
menu_rects = []  # Initialize menu_rects as an empty list
while running:
    time += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                prev_selected = selected_item
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(menu_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(menu_items)
                if selected_item != prev_selected:
                    menu_select_sound.play()
                if event.key == pygame.K_RETURN:
                    menu_click_sound.play()
                    if menu_items[selected_item] == "Start Game":
                        game_state = "game"
                        player = Player()
                        dots = []
                        score = 0
                        game_over = False
                        difficulty_multiplier = 1
                        frames_since_last_spawn = 0
                    elif menu_items[selected_item] == "Settings":
                        game_state = "settings"
                    elif menu_items[selected_item] == "Quit":
                        running = False
            elif game_state == "game":
                if event.key == pygame.K_SPACE:
                    clockwise = not clockwise
            elif game_state == "settings":
                prev_selected = selected_item
                if event.key == pygame.K_ESCAPE:
                    menu_click_sound.play()
                    game_state = "menu"
                elif event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % 4
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % 4
                if selected_item != prev_selected:
                    menu_select_sound.play()
                if event.key == pygame.K_LEFT:
                    if selected_item < 3:
                        if selected_item == 0:
                            master_volume = max(0, master_volume - 0.1)
                        elif selected_item == 1:
                            music_volume = max(0, music_volume - 0.1)
                        elif selected_item == 2:
                            sfx_volume = max(0, sfx_volume - 0.1)
                        update_volumes()
                elif event.key == pygame.K_RIGHT:
                    if selected_item < 3:
                        if selected_item == 0:
                            master_volume = min(1, master_volume + 0.1)
                        elif selected_item == 1:
                            music_volume = min(1, music_volume + 0.1)
                        elif selected_item == 2:
                            sfx_volume = min(1, sfx_volume + 0.1)
                        update_volumes()
                elif event.key == pygame.K_RETURN and selected_item == 3:
                    menu_click_sound.play()
                    game_state = "menu"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                menu_click_sound.play()
                if game_state == "menu":
                    for i, rect in enumerate(menu_rects):
                        if rect.collidepoint(event.pos):
                            if menu_items[i] == "Start Game":
                                game_state = "game"
                                player = Player()
                                dots = []
                                score = 0
                                game_over = False
                                difficulty_multiplier = 1
                                frames_since_last_spawn = 0
                            elif menu_items[i] == "Settings":
                                game_state = "settings"
                            elif menu_items[i] == "Quit":
                                running = False
                elif game_state == "settings":
                    for i, rect in enumerate(volume_rects):
                        if rect.collidepoint(event.pos):
                            x = (event.pos[0] - rect.x) / rect.width
                            if i == 0:
                                master_volume = max(0, min(1, x))
                            elif i == 1:
                                music_volume = max(0, min(1, x))
                            elif i == 2:
                                sfx_volume = max(0, min(1, x))
                            update_volumes()
                    if back_rect.collidepoint(event.pos):
                        game_state = "menu"
                elif game_state == "game" and game_over:
                    game_state = "menu"
        elif event.type == pygame.MOUSEMOTION:
            if game_state == "menu":
                hovered_item = -1
                for i, rect in enumerate(menu_rects):
                    if rect.collidepoint(event.pos):
                        hovered_item = i
                        break
            elif game_state == "settings":
                hovered_item = -1
                for i, rect in enumerate(volume_rects):
                    if rect.collidepoint(event.pos):
                        hovered_item = i
                        break
                if back_rect.collidepoint(event.pos):
                    hovered_item = 3

    if game_state == "menu":
        menu_rects = draw_menu(menu_items, selected_item, hovered_item)
    elif game_state == "settings":
        volume_rects, back_rect = draw_settings(selected_item, hovered_item)
    elif game_state == "game":
        if not game_over:
            player.move(clockwise)

            for dot in dots[:]:
                dot.move()
                if dot.distance > RING_RADIUS + DOT_RADIUS:
                    dots.remove(dot)
                elif math.hypot(dot.x - player.x, dot.y - player.y) < PLAYER_RADIUS + DOT_RADIUS:
                    if dot.good:
                        score += 1
                        collect_sound.play()
                        dots.remove(dot)
                    else:
                        game_over = True
                        game_over_sound.play()

            frames_since_last_spawn += 1
            if frames_since_last_spawn >= DOT_SPAWN_RATE:
                dots.append(Dot())
                frames_since_last_spawn = 0

            difficulty_multiplier *= DIFFICULTY_INCREASE_RATE

        draw_background(time, background_particles)
        pygame.draw.circle(screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), RING_RADIUS, RING_THICKNESS)
        for dot in dots:
            dot.draw()
        player.draw()
        twister.update()
        twister.draw()

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("Game Over", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 36))
            restart_text = font.render("Click to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 36))

    pygame.display.flip()
    clock.tick(FPS)