import pygame
import logging
from game_settings import *

logger = logging.getLogger(__name__)

class LoginMenu:
    def __init__(self, screen, font_manager, server_comm):
        self.screen = screen
        self.font_manager = font_manager
        self.server_comm = server_comm
        self.username = ""
        self.password = ""
        self.active_field = "username"
        self.message = ""
        self.message_color = WHITE
        self.is_registering = False

    async def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.active_field = "password" if self.active_field == "username" else "username"
            elif event.key == pygame.K_RETURN:
                if self.username and self.password:
                    if self.is_registering:
                        success, message = await self.server_comm.register(self.username, self.password)
                        if success:
                            self.message = "Registration successful! Please log in."
                            self.message_color = GREEN
                            self.is_registering = False
                        else:
                            self.message = f"Registration failed: {message}"
                            self.message_color = RED
                    else:
                        success, message = await self.server_comm.login(self.username, self.password)
                        if success:
                            self.message = "Login successful!"
                            self.message_color = GREEN
                            return "success", self.username
                        else:
                            self.message = f"Login failed: {message}"
                            self.message_color = RED
                else:
                    self.message = "Please enter both username and password"
                    self.message_color = RED
            elif event.key == pygame.K_BACKSPACE:
                if self.active_field == "username":
                    self.username = self.username[:-1]
                else:
                    self.password = self.password[:-1]
            elif event.key == pygame.K_ESCAPE:
                return "back", ""
            else:
                if self.active_field == "username":
                    self.username += event.unicode
                else:
                    self.password += event.unicode
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.register_button_rect.collidepoint(event.pos):
                self.is_registering = not self.is_registering
        return None, ""

    def draw(self):
        self.screen.fill(BLACK)
        title_font = self.font_manager.get_font(BASE_FONT_SIZE * 2)
        regular_font = self.font_manager.get_font(BASE_FONT_SIZE)

        title = title_font.render("Login" if not self.is_registering else "Register", True, WHITE)
        title_rect = title.get_rect(center=(GAME_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        username_text = regular_font.render("Username:", True, WHITE)
        username_rect = username_text.get_rect(topleft=(100, 150))
        self.screen.blit(username_text, username_rect)

        username_input = regular_font.render(self.username, True, WHITE)
        username_input_rect = pygame.Rect(100, 180, 200, 30)
        pygame.draw.rect(self.screen, WHITE if self.active_field == "username" else GREY, username_input_rect, 2)
        self.screen.blit(username_input, (username_input_rect.x + 5, username_input_rect.y + 5))

        password_text = regular_font.render("Password:", True, WHITE)
        password_rect = password_text.get_rect(topleft=(100, 250))
        self.screen.blit(password_text, password_rect)

        password_input = regular_font.render("*" * len(self.password), True, WHITE)
        password_input_rect = pygame.Rect(100, 280, 200, 30)
        pygame.draw.rect(self.screen, WHITE if self.active_field == "password" else GREY, password_input_rect, 2)
        self.screen.blit(password_input, (password_input_rect.x + 5, password_input_rect.y + 5))

        if self.message:
            message_text = regular_font.render(self.message, True, self.message_color)
            message_rect = message_text.get_rect(center=(GAME_WIDTH // 2, 350))
            self.screen.blit(message_text, message_rect)

        register_text = "Switch to Login" if self.is_registering else "Switch to Register"
        register_button = regular_font.render(register_text, True, WHITE)
        self.register_button_rect = register_button.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 100))
        self.screen.blit(register_button, self.register_button_rect)

        action_text = "Register" if self.is_registering else "Login"
        instructions = regular_font.render(f"Press ENTER to {action_text}, ESC to go back", True, WHITE)
        instructions_rect = instructions.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT - 50))
        self.screen.blit(instructions, instructions_rect)