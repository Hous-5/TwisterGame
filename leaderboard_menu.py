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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
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

        back_text = regular_font.render("Press ESC to go back", True, WHITE)
        back_rect = back_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)