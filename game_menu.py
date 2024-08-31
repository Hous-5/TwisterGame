import pygame
from game_settings import *
from server_communication import server_comm
import asyncio

class GameMenu:
    def __init__(self, screen, sound_manager, font_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.font_manager = font_manager
        self.selected_item = -1
        self.hovered_item = -1
        self.current_menu = "main"
        self.main_menu_items = ["Start Game", "Leaderboard", "Settings", "Quit"]
        self.settings_items = ["Master Volume", "Music Volume", "SFX Volume", "Back to Main Menu"]
        self.game_over_items = ["Submit Score", "Restart", "Back to Main Menu"]
        self.leaderboard_items = ["Back to Main Menu"]
        self.leaderboard_data = []
        self.player_name = ""
        self.player_score = 0
        self.leaderboard_error = None
        self.loop = asyncio.get_event_loop()
        self.submission_message = ""
        self.submission_message_timer = 0

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.move_selection(-1)
            elif event.key == pygame.K_DOWN:
                self.move_selection(1)
            elif event.key == pygame.K_RETURN:
                return self.select_item(self.get_active_item())
            elif self.current_menu == "settings" and event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.adjust_volume(self.get_active_item(), -0.1 if event.key == pygame.K_LEFT else 0.1)
        elif event.type == pygame.MOUSEMOTION:
            self.handle_mouse_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                return self.handle_mouse_click(event.pos)
        return self.current_menu
    
    def move_selection(self, direction):
        items = self.get_current_items()
        if self.selected_item == -1:
            self.selected_item = 0 if direction > 0 else len(items) - 1
        else:
            self.selected_item = (self.selected_item + direction) % len(items)
        self.sound_manager.play_menu_select()

    def handle_mouse_hover(self, pos):
        previous_hover = self.hovered_item
        self.hovered_item = -1
        items = self.get_current_items()
        for i, _ in enumerate(items):
            if self.get_item_rect(i).collidepoint(pos):
                self.hovered_item = i
                if self.hovered_item != previous_hover:
                    self.sound_manager.play_menu_select()
                break

    def handle_mouse_click(self, pos):
        items = self.get_current_items()
        for i, _ in enumerate(items):
            item_rect = self.get_item_rect(i)
            if item_rect.collidepoint(pos):
                if self.current_menu == "settings" and i < len(items) - 1:
                    # Handle volume bar click
                    volume_rect = pygame.Rect(item_rect.x, item_rect.y + 40, item_rect.width, 20)
                    if volume_rect.collidepoint(pos):
                        new_volume = (pos[0] - volume_rect.x) / volume_rect.width
                        self.adjust_volume(i, new_volume - self.get_volume(i))
                else:
                    return self.select_item(i)
        return self.current_menu

    def get_active_item(self):
        return self.hovered_item if self.hovered_item != -1 else self.selected_item

    def select_item(self, index):
        if index == -1:
            return self.current_menu
        
        if self.current_menu == "main":
            if self.main_menu_items[index] == "Start Game":
                return "game"
            elif self.main_menu_items[index] == "Leaderboard":
                self.current_menu = "leaderboard"
                self.selected_item = 0
                self.hovered_item = -1
                self.fetch_leaderboard()
            elif self.main_menu_items[index] == "Settings":
                self.current_menu = "settings"
                self.selected_item = 0
                self.hovered_item = -1
            elif self.main_menu_items[index] == "Quit":
                pygame.quit()
                quit()
        elif self.current_menu in ["settings", "leaderboard"]:
            if self.get_current_items()[index] == "Back to Main Menu":
                self.current_menu = "main"
                self.selected_item = 0
                self.hovered_item = -1
        elif self.current_menu == "game_over":
            if self.game_over_items[index] == "Submit Score":
                self.submit_score()
            elif self.game_over_items[index] == "Restart":
                return "restart"
            elif self.game_over_items[index] == "Back to Main Menu":
                self.current_menu = "main"
                self.selected_item = -1
                self.hovered_item = -1
        return self.current_menu

    def get_item_rect(self, index):
        items = self.get_current_items()
        if self.current_menu == "settings":
            total_height = len(items) * 100  # Increased spacing for settings menu
            start_y = (GAME_HEIGHT - total_height) // 2
            return pygame.Rect(GAME_WIDTH // 4, start_y + index * 100, GAME_WIDTH // 2, 80)
        else:
            total_height = len(items) * 60
            start_y = (GAME_HEIGHT - total_height) // 2
            return pygame.Rect(GAME_WIDTH // 4, start_y + index * 60, GAME_WIDTH // 2, 60)

    def adjust_volume(self, index, change):
        if index == 0:
            self.sound_manager.set_master_volume(self.sound_manager.master_volume + change)
        elif index == 1:
            self.sound_manager.set_music_volume(self.sound_manager.music_volume + change)
        elif index == 2:
            self.sound_manager.set_sfx_volume(self.sound_manager.sfx_volume + change)

    def get_volume(self, index):
        if index == 0:
            return self.sound_manager.master_volume
        elif index == 1:
            return self.sound_manager.music_volume
        elif index == 2:
            return self.sound_manager.sfx_volume
        return 0

    def draw(self):
        self.screen.fill(BLACK)
        font = self.font_manager.get_font(BASE_FONT_SIZE)
        
        if self.current_menu == "settings":
            self.draw_settings_menu(font)
        elif self.current_menu == "leaderboard":
            self.draw_leaderboard(font)
        else:  # main menu and game over menu
            self.draw_centered_menu(font)

    def draw_centered_menu(self, font):
        items = self.get_current_items()
        for i, item in enumerate(items):
            color = ORANGE if i == self.get_active_item() else WHITE
            text = font.render(item, True, color)
            text_rect = self.get_item_rect(i)
            text_rect.center = (GAME_WIDTH // 2, text_rect.centery)
            self.screen.blit(text, text_rect)

    def draw_settings_menu(self, font):
        items = self.get_current_items()
        for i, item in enumerate(items):
            color = ORANGE if i == self.get_active_item() else WHITE
            
            if i < len(items) - 1:  # For volume options
                value = self.get_volume(i)
                
                # Draw text with percentage
                text = f"{item}: {int(value * 100)}%"
                text_surface = font.render(text, True, color)
                text_rect = self.get_item_rect(i)
                text_pos = (text_rect.left, text_rect.top + 10)  # Adjust vertical position
                self.screen.blit(text_surface, text_pos)

                # Draw volume bar
                bar_rect = pygame.Rect(text_rect.left, text_rect.top + 40, text_rect.width, 20)  # Adjust vertical position
                pygame.draw.rect(self.screen, GREY, bar_rect)
                pygame.draw.rect(self.screen, color, (bar_rect.x, bar_rect.y, bar_rect.width * value, bar_rect.height))
            else:  # For "Back to Main Menu" option
                text = font.render(item, True, color)
                text_rect = self.get_item_rect(i)
                text_rect.center = (GAME_WIDTH // 2, text_rect.centery)
                self.screen.blit(text, text_rect)

    def draw_leaderboard(self, font):
        self.screen.fill(BLACK)
        title = font.render("Leaderboard", True, WHITE)
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        print(f"Drawing leaderboard. Current data: {self.leaderboard_data}")  # Debug print

        if self.leaderboard_error:
            error_text = font.render(self.leaderboard_error, True, RED)
            error_rect = error_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
            self.screen.blit(error_text, error_rect)
        else:
            start_y = 100
            for i, entry in enumerate(self.leaderboard_data):
                if isinstance(entry, dict):
                    name, score = entry['name'], entry['score']
                elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                    name, score = entry
                else:
                    print(f"Unexpected leaderboard entry format: {entry}")  # Debug print
                    continue
                
                text = font.render(f"{i+1}. {name}: {score}", True, WHITE)
                text_rect = text.get_rect(center=(GAME_WIDTH // 2, start_y + i * 40))
                self.screen.blit(text, text_rect)

        if self.submission_message and self.submission_message_timer > 0:
            message_text = font.render(self.submission_message, True, GREEN)
            message_rect = message_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 100))
            self.screen.blit(message_text, message_rect)

        # Draw "Back to Main Menu" button
        back_rect = self.get_item_rect(0)  # There's only one item in leaderboard_items
        color = ORANGE if self.get_active_item() == 0 else WHITE
        pygame.draw.rect(self.screen, color, back_rect, 2)  # Draw a border
        back_text = font.render("Back to Main Menu", True, color)
        text_rect = back_text.get_rect(center=back_rect.center)
        self.screen.blit(back_text, text_rect)

    def fetch_leaderboard(self):
        print("Fetching leaderboard data...")  # Debug print
        try:
            self.leaderboard_data = self.loop.run_until_complete(server_comm.get_leaderboard())
            self.leaderboard_error = None
            print(f"Leaderboard data fetched: {self.leaderboard_data}")  # Debug print
        except Exception as e:
            print(f"Error fetching leaderboard: {str(e)}")  # Debug print
            self.leaderboard_error = str(e)
            self.leaderboard_data = []

    def submit_score(self):
        print(f"Submitting score: {self.player_name} - {self.player_score}")  # Debug print
        try:
            success = self.loop.run_until_complete(server_comm.submit_score(self.player_name, self.player_score))
            if success:
                print("Score submitted successfully. Fetching updated leaderboard.")  # Debug print
                self.submission_message = "Score submitted successfully!"
                self.submission_message_timer = 180  # Display for 3 seconds (60 fps * 3)
                self.fetch_leaderboard()  # Refresh leaderboard data immediately
                self.current_menu = "leaderboard"
            else:
                print("Failed to submit score.")  # Debug print
                self.submission_message = "Failed to submit score. Please try again."
                self.submission_message_timer = 180
        except Exception as e:
            print(f"Error submitting score: {str(e)}")  # Debug print
            self.submission_message = f"Error: {str(e)}"
            self.submission_message_timer = 180

    def update(self):
        # Update volume text in settings menu
        self.settings_items = [
            "Master Volume",
            "Music Volume",
            "SFX Volume",
            "Back to Main Menu"
        ]
        if self.submission_message_timer > 0:
            self.submission_message_timer -= 1
        if self.submission_message_timer == 0:
            self.submission_message = ""

    def set_player_score(self, name, score):
        self.player_name = name
        self.player_score = score
        print(f"Player score set: {self.player_name} - {self.player_score}")  # Debug print

    def get_current_items(self):
        if self.current_menu == "main":
            return self.main_menu_items
        elif self.current_menu == "settings":
            return self.settings_items
        elif self.current_menu == "game_over":
            return self.game_over_items
        elif self.current_menu == "leaderboard":
            return self.leaderboard_items
        return []

    def set_game_over(self):
        self.current_menu = "game_over"
        self.selected_item = 0
        self.hovered_item = -1