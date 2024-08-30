import pygame
import random
from player import Player
from dot import Dot
from twister import Twister
from background_particle import BackgroundParticle
from game_settings import *
from sound_manager import SoundManager

class TwisterGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Twister Game")
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.dots = []
        self.twister = Twister()
        self.score = 0
        self.game_over = False
        self.clockwise = True
        self.difficulty_multiplier = 1
        self.frames_since_last_spawn = 0
        self.time = 0
        self.background_particles = [BackgroundParticle() for _ in range(50)]

    def run(self):
        running = True
        game_state = "menu"
        menu_items = ["Start Game", "Settings", "Quit"]
        selected_item = -1
        hovered_item = -1

        while running:
            self.time += 1

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if game_state == "menu":
                        game_state = self.handle_menu_input(event, menu_items, selected_item)
                    elif game_state == "game":
                        self.handle_game_input(event)
                    elif game_state == "settings":
                        game_state = self.handle_settings_input(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left mouse button
                        self.sound_manager.play_menu_click()
                        if game_state == "menu":
                            game_state = self.handle_menu_click(event, menu_items)
                        elif game_state == "settings":
                            game_state = self.handle_settings_click(event)
                        elif game_state == "game" and self.game_over:
                            game_state = "menu"
                elif event.type == pygame.MOUSEMOTION:
                    if game_state == "menu":
                        hovered_item = self.handle_menu_hover(event, menu_items)
                    elif game_state == "settings":
                        hovered_item = self.handle_settings_hover(event)

            if game_state == "menu":
                self.draw_menu(menu_items, selected_item, hovered_item)
            elif game_state == "settings":
                self.draw_settings(selected_item, hovered_item)
            elif game_state == "game":
                self.update_game()
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()

    def handle_menu_hover(self, event, menu_items):
        for i, item in enumerate(menu_items):
            text_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 + i * 60, 200, 50)
            if text_rect.collidepoint(event.pos):
                return i
        return -1

    def handle_menu_input(self, event, menu_items, selected_item):
        if event.key == pygame.K_UP:
            selected_item = (selected_item - 1) % len(menu_items)
            self.sound_manager.play_menu_select()
        elif event.key == pygame.K_DOWN:
            selected_item = (selected_item + 1) % len(menu_items)
            self.sound_manager.play_menu_select()
        elif event.key == pygame.K_RETURN:
            self.sound_manager.play_menu_click()
            if menu_items[selected_item] == "Start Game":
                self.reset_game()
                return "game"
            elif menu_items[selected_item] == "Settings":
                return "settings"
            elif menu_items[selected_item] == "Quit":
                pygame.quit()
                quit()
        return "menu"

    def handle_game_input(self, event):
        if event.key == pygame.K_SPACE:
            self.clockwise = not self.clockwise

    def handle_settings_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.sound_manager.play_menu_click()
            return "menu"
        return "settings"

    def handle_menu_click(self, event, menu_items):
        for i, item in enumerate(menu_items):
            text_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50 + i * 60, 200, 50)
            if text_rect.collidepoint(event.pos):
                if item == "Start Game":
                    self.reset_game()
                    return "game"
                elif item == "Settings":
                    return "settings"
                elif item == "Quit":
                    pygame.quit()
                    quit()
        return "menu"

    def handle_settings_click(self, event):
        volumes = [
            ("Master Volume", self.sound_manager.master_volume),
            ("Music Volume", self.sound_manager.music_volume),
            ("SFX Volume", self.sound_manager.sfx_volume)
        ]
        
        for i, (label, value) in enumerate(volumes):
            bar_rect = pygame.Rect(50, 140 + i * 100, 300, 20)
            if bar_rect.collidepoint(event.pos):
                new_value = (event.pos[0] - bar_rect.x) / bar_rect.width
                if i == 0:
                    self.sound_manager.set_master_volume(new_value)
                elif i == 1:
                    self.sound_manager.set_music_volume(new_value)
                elif i == 2:
                    self.sound_manager.set_sfx_volume(new_value)
                return "settings"
        
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 75, 200, 50)
        if back_rect.collidepoint(event.pos):
            return "menu"
        
        return "settings"

    def handle_settings_hover(self, event):
        volumes = [
            ("Master Volume", self.sound_manager.master_volume),
            ("Music Volume", self.sound_manager.music_volume),
            ("SFX Volume", self.sound_manager.sfx_volume)
        ]
        
        for i in range(len(volumes)):
            bar_rect = pygame.Rect(50, 140 + i * 100, 300, 20)
            if bar_rect.collidepoint(event.pos):
                return i
        
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 75, 200, 50)
        if back_rect.collidepoint(event.pos):
            return 3
        
        return -1

    def update_game(self):
        if not self.game_over:
            self.player.move(self.clockwise, self.difficulty_multiplier)

            for dot in self.dots[:]:
                dot.move(self.difficulty_multiplier)
                if dot.distance > RING_RADIUS + DOT_RADIUS:
                    self.dots.remove(dot)
                elif self.player.collides_with(dot):
                    if dot.good:
                        self.score += 1
                        self.sound_manager.play_collect()
                        self.dots.remove(dot)
                    else:
                        self.game_over = True
                        self.sound_manager.play_game_over()

            self.frames_since_last_spawn += 1
            if self.frames_since_last_spawn >= DOT_SPAWN_RATE:
                self.dots.append(Dot())
                self.frames_since_last_spawn = 0

            self.difficulty_multiplier *= DIFFICULTY_INCREASE_RATE

    def draw_game(self):
        self.draw_background()
        pygame.draw.circle(self.screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), RING_RADIUS, RING_THICKNESS)
        for dot in self.dots:
            dot.draw(self.screen)
        self.player.draw(self.screen)
        self.twister.update()
        self.twister.draw(self.screen)

        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            self.draw_game_over()

    def draw_background(self):
        self.screen.fill(BACKGROUND_COLOR)
        for particle in self.background_particles:
            particle.move()
            particle.draw(self.screen)

    def draw_menu(self, menu_items, selected_item, hovered_item):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 48)
        for i, item in enumerate(menu_items):
            if i == selected_item:
                color = ORANGE
            elif i == hovered_item:
                color = ORANGE
            else:
                color = WHITE
            text = font.render(item, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50 + i * 60))
            self.screen.blit(text, text_rect)

    def draw_settings(self, selected_item, hovered_item):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        
        volumes = [
            ("Master Volume", self.sound_manager.master_volume),
            ("Music Volume", self.sound_manager.music_volume),
            ("SFX Volume", self.sound_manager.sfx_volume)
        ]
        
        for i, (label, value) in enumerate(volumes):
            if i == selected_item:
                color = ORANGE
            elif i == hovered_item:
                color = ORANGE
            else:
                color = WHITE
            text = font.render(label, True, color)
            self.screen.blit(text, (50, 100 + i * 100))
            
            bar_rect = pygame.Rect(50, 140 + i * 100, 300, 20)
            pygame.draw.rect(self.screen, GREY, bar_rect)
            pygame.draw.rect(self.screen, color, (50, 140 + i * 100, 300 * value, 20))
        
        back_color = ORANGE if hovered_item == 3 else WHITE
        back_text = font.render("Back to Menu", True, back_color)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def draw_game_over(self):
        font = pygame.font.Font(None, 72)
        game_over_text = font.render("Game Over", True, WHITE)
        restart_text = font.render("Click to Restart", True, WHITE)
        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 36))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 36))

if __name__ == "__main__":
    game = TwisterGame()
    game.run()