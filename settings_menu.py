import pygame
from game_settings import *

class SettingsMenu:
    def __init__(self, screen, sound_manager, font_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.font_manager = font_manager
        self.settings = [
            ("Master Volume", lambda: self.sound_manager.master_volume),
            ("Music Volume", lambda: self.sound_manager.music_volume),
            ("SFX Volume", lambda: self.sound_manager.sfx_volume)
        ]
        self.selected_setting = 0
        self.slider_rects = []

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_setting = (self.selected_setting - 1) % len(self.settings)
            elif event.key == pygame.K_DOWN:
                self.selected_setting = (self.selected_setting + 1) % len(self.settings)
            elif event.key == pygame.K_LEFT:
                self.adjust_setting(-0.1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_setting(0.1)
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return "back"
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                for i, rect in enumerate(self.slider_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_setting = i
                        self.adjust_setting_to_mouse(event.pos, rect)
        elif event.type == pygame.MOUSEMOTION:
            if event.buttons[0]:  # Left mouse button held down
                for i, rect in enumerate(self.slider_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_setting = i
                        self.adjust_setting_to_mouse(event.pos, rect)
        return None

    def adjust_setting(self, change):
        setting_name, get_value = self.settings[self.selected_setting]
        if setting_name == "Master Volume":
            self.sound_manager.set_master_volume(get_value() + change)
        elif setting_name == "Music Volume":
            self.sound_manager.set_music_volume(get_value() + change)
        elif setting_name == "SFX Volume":
            self.sound_manager.set_sfx_volume(get_value() + change)

    def adjust_setting_to_mouse(self, pos, rect):
        value = (pos[0] - rect.x) / rect.width
        value = max(0, min(1, value))
        setting_name, _ = self.settings[self.selected_setting]
        if setting_name == "Master Volume":
            self.sound_manager.set_master_volume(value)
        elif setting_name == "Music Volume":
            self.sound_manager.set_music_volume(value)
        elif setting_name == "SFX Volume":
            self.sound_manager.set_sfx_volume(value)

    def draw(self):
        self.screen.fill(BLACK)
        font = self.font_manager.get_font(BASE_FONT_SIZE * 2)
        title = font.render("Settings", True, WHITE)
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 6))
        self.screen.blit(title, title_rect)

        font = self.font_manager.get_font(BASE_FONT_SIZE)
        self.slider_rects = []
        
        for i, (setting_name, get_value) in enumerate(self.settings):
            color = ORANGE if i == self.selected_setting else WHITE
            
            # Draw text
            text = font.render(setting_name, True, color)
            text_rect = text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + i * 100 - 20))
            self.screen.blit(text, text_rect)

            # Draw slider
            slider_rect = pygame.Rect(GAME_WIDTH // 4, GAME_HEIGHT // 2 + i * 100 + 10, GAME_WIDTH // 2, 10)
            pygame.draw.rect(self.screen, WHITE, slider_rect, 2)
            filled_width = int(slider_rect.width * get_value())
            pygame.draw.rect(self.screen, color, (slider_rect.x, slider_rect.y, filled_width, slider_rect.height))
            
            # Draw slider handle
            handle_pos = (slider_rect.x + filled_width, slider_rect.centery)
            pygame.draw.circle(self.screen, color, handle_pos, 8)
            
            self.slider_rects.append(slider_rect)

        back_text = font.render("Press ESC or ENTER to go back", True, WHITE)
        back_rect = back_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)