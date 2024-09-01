import pygame
from game_settings import *

class PauseMenu:
    def __init__(self, screen, sound_manager, font_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.font_manager = font_manager
        self.options = ["Resume", "Quit to Menu"]
        self.selected_option = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                self.sound_manager.play_menu_select()
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                self.sound_manager.play_menu_select()
            elif event.key == pygame.K_RETURN:
                self.sound_manager.play_menu_click()
                return self.options[self.selected_option].lower()
        return None

    def update(self):
        return None

    def draw(self):
        # Draw a semi-transparent overlay
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Draw "Paused" text
        font = self.font_manager.get_font(BASE_FONT_SIZE * 2)
        text = font.render("Paused", True, WHITE)
        text_rect = text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 4))
        self.screen.blit(text, text_rect)

        # Draw menu options
        font = self.font_manager.get_font(BASE_FONT_SIZE)
        for i, option in enumerate(self.options):
            color = ORANGE if i == self.selected_option else WHITE
            text = font.render(option, True, color)
            text_rect = text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + i * 50))
            self.screen.blit(text, text_rect)