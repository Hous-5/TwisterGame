import pygame
from game_settings import *

class GameMenu:
    def __init__(self, screen, sound_manager, font_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.font_manager = font_manager
        self.menu_items = ["Start Game", "Settings", "Leaderboard", "Quit"]
        self.selected_item = 0
        self.hovered_item = -1
        self.item_rects = []

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_item = (self.selected_item - 1) % len(self.menu_items)
                self.sound_manager.play_menu_select()
            elif event.key == pygame.K_DOWN:
                self.selected_item = (self.selected_item + 1) % len(self.menu_items)
                self.sound_manager.play_menu_select()
            elif event.key == pygame.K_RETURN:
                self.sound_manager.play_menu_click()
                return self.menu_items[self.selected_item].lower().replace(" ", "")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for i, rect in enumerate(self.item_rects):
                    if rect.collidepoint(event.pos):
                        self.sound_manager.play_menu_click()
                        return self.menu_items[i].lower().replace(" ", "")
        elif event.type == pygame.MOUSEMOTION:
            self.hovered_item = -1
            for i, rect in enumerate(self.item_rects):
                if rect.collidepoint(event.pos):
                    self.hovered_item = i
                    break
        return None

    def update(self):
        pass  # Add any necessary updates here

    def draw(self):
        self.screen.fill(BLACK)
        font = self.font_manager.get_font(BASE_FONT_SIZE * 2)
        title = font.render("Twister Game", True, WHITE)
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 4))
        self.screen.blit(title, title_rect)

        font = self.font_manager.get_font(BASE_FONT_SIZE)
        self.item_rects = []
        for i, item in enumerate(self.menu_items):
            color = ORANGE if i == self.selected_item or i == self.hovered_item else WHITE
            text = font.render(item, True, color)
            text_rect = text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + i * 50))
            self.screen.blit(text, text_rect)
            self.item_rects.append(text_rect)

        # Draw a rectangle around the selected or hovered item
        if self.hovered_item != -1:
            pygame.draw.rect(self.screen, ORANGE, self.item_rects[self.hovered_item], 2)
        elif self.selected_item != -1:
            pygame.draw.rect(self.screen, ORANGE, self.item_rects[self.selected_item], 2)