import pygame
from game_settings import *

class Settings:
    def __init__(self, screen, sound_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.selected_item = 0
        self.hovered_item = -1
        self.volumes = [
            ("Master Volume", self.sound_manager.master_volume),
            ("Music Volume", self.sound_manager.music_volume),
            ("SFX Volume", self.sound_manager.sfx_volume)
        ]

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            return self.handle_key_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            return self.handle_mouse_click(event)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_hover(event)
        return "settings"

    def handle_key_input(self, event):
        if event.key == pygame.K_ESCAPE:
            self.sound_manager.play_menu_click()
            return "menu"
        elif event.key == pygame.K_UP:
            self.selected_item = (self.selected_item - 1) % (len(self.volumes) + 1)
        elif event.key == pygame.K_DOWN:
            self.selected_item = (self.selected_item + 1) % (len(self.volumes) + 1)
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.adjust_volume(self.selected_item, -0.1 if event.key == pygame.K_LEFT else 0.1)
        return "settings"

    def handle_mouse_click(self, event):
        for i, (label, value) in enumerate(self.volumes):
            bar_rect = self.get_volume_bar_rect(i)
            if bar_rect.collidepoint(event.pos):
                new_value = (event.pos[0] - bar_rect.x) / bar_rect.width
                self.adjust_volume(i, new_value - value)
                return "settings"
        
        back_rect = self.get_back_button_rect()
        if back_rect.collidepoint(event.pos):
            return "menu"
        
        return "settings"

    def handle_mouse_hover(self, event):
        self.hovered_item = -1
        for i in range(len(self.volumes)):
            if self.get_volume_bar_rect(i).collidepoint(event.pos):
                self.hovered_item = i
                return
        if self.get_back_button_rect().collidepoint(event.pos):
            self.hovered_item = len(self.volumes)

    def adjust_volume(self, index, change):
        if index < len(self.volumes):
            current_value = self.volumes[index][1]
            new_value = max(0, min(1, current_value + change))
            if index == 0:
                self.sound_manager.set_master_volume(new_value)
            elif index == 1:
                self.sound_manager.set_music_volume(new_value)
            elif index == 2:
                self.sound_manager.set_sfx_volume(new_value)
            self.volumes[index] = (self.volumes[index][0], new_value)

    def get_volume_bar_rect(self, index):
        return pygame.Rect(50, 140 + index * 100, 300, 20)

    def get_back_button_rect(self):
        return pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 75, 200, 50)

    def draw(self):
        self.screen.fill(BLACK)
        font = pygame.font.Font(None, 36)
        
        for i, (label, value) in enumerate(self.volumes):
            color = ORANGE if i == self.selected_item or i == self.hovered_item else WHITE
            text = font.render(label, True, color)
            self.screen.blit(text, (50, 100 + i * 100))
            
            bar_rect = self.get_volume_bar_rect(i)
            pygame.draw.rect(self.screen, GREY, bar_rect)
            pygame.draw.rect(self.screen, color, (bar_rect.x, bar_rect.y, bar_rect.width * value, bar_rect.height))
        
        back_color = ORANGE if self.selected_item == len(self.volumes) or self.hovered_item == len(self.volumes) else WHITE
        back_text = font.render("Back to Menu", True, back_color)
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)