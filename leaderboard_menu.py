import pygame
from game_settings import *

class LeaderboardMenu:
    def __init__(self, screen, font_manager, server_comm):
        self.screen = screen
        self.font_manager = font_manager
        self.server_comm = server_comm
        self.leaderboard_data = []
        self.loading = True
        self.error = None
        self.main_menu_button_rect = None
        self.is_main_menu_button_selected = False

    async def fetch_leaderboard(self):
        self.loading = True
        self.error = None
        try:
            self.leaderboard_data = await self.server_comm.get_leaderboard()
            self.loading = False
        except Exception as e:
            self.error = str(e)
            self.loading = False

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            if self.main_menu_button_rect and self.main_menu_button_rect.collidepoint(event.pos):
                return "mainmenu"
        elif event.type == pygame.MOUSEMOTION:
            if self.main_menu_button_rect and self.main_menu_button_rect.collidepoint(event.pos):
                self.is_main_menu_button_selected = True
            else:
                self.is_main_menu_button_selected = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return "mainmenu"
        return None

    def draw(self):
        self.screen.fill(BLACK)
        title_font = self.font_manager.get_font(BASE_FONT_SIZE * 2)
        regular_font = self.font_manager.get_font(BASE_FONT_SIZE)

        title = title_font.render("Leaderboard", True, WHITE)
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        if self.loading:
            loading_text = regular_font.render("Loading...", True, WHITE)
            loading_rect = loading_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
            self.screen.blit(loading_text, loading_rect)
        elif self.error:
            error_text = regular_font.render(f"Error: {self.error}", True, RED)
            error_rect = error_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
            self.screen.blit(error_text, error_rect)
        else:
            for i, entry in enumerate(self.leaderboard_data[:10]):  # Display top 10
                text = regular_font.render(f"{i+1}. {entry['name']}: {entry['score']}", True, WHITE)
                text_rect = text.get_rect(left=100, top=100 + i * 40)
                self.screen.blit(text, text_rect)

        # Draw Main Menu button
        main_menu_text = regular_font.render("Main Menu", True, ORANGE if self.is_main_menu_button_selected else WHITE)
        self.main_menu_button_rect = main_menu_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 50))
        pygame.draw.rect(self.screen, ORANGE if self.is_main_menu_button_selected else WHITE, self.main_menu_button_rect, 2)
        self.screen.blit(main_menu_text, self.main_menu_button_rect)