import pygame
import random
import asyncio
from player import Player
from dot import Dot
from twister import Twister
from background_particle import BackgroundParticle
from game_settings import *
from sound_manager import SoundManager
from game_menu import GameMenu
from font_manager import FontManager
from server_communication import server_comm

class TwisterGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.real_screen.get_size()
        self.screen = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Twister Game")
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.font_manager = FontManager(FONT_FILE)
        self.calculate_scaling()
        self.loop = asyncio.get_event_loop()
        self.game_menu = GameMenu(self.screen, self.sound_manager, self.font_manager)
        self.reset_game()
        self.player_name = ""
        self.is_authenticated = False

    def calculate_scaling(self):
        # Calculate the scaling factor and position to maintain aspect ratio
        screen_aspect_ratio = self.screen_width / self.screen_height
        game_aspect_ratio = GAME_WIDTH / GAME_HEIGHT

        if screen_aspect_ratio > game_aspect_ratio:
            self.game_height = self.screen_height
            self.game_width = int(self.game_height * game_aspect_ratio)
        else:
            self.game_width = self.screen_width
            self.game_height = int(self.game_width / game_aspect_ratio)

        self.scale_factor = self.game_height / GAME_HEIGHT
        self.game_pos = ((self.screen_width - self.game_width) // 2, 
                         (self.screen_height - self.game_height) // 2)
        
        self.font_manager.update_scale_factor(self.scale_factor)
    
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
        print(f"Game reset. Score: {self.score}")  # Debug print

    async def login_or_register(self):
        print("Attempting to log in or register...")
        username = self.player_name
        password = "password"  # In a real game, you'd have a secure way to get this

        # Try to login
        print(f"Attempting to log in with username: {username}")
        success, message = await server_comm.login(username, password)
        if not success:
            # If login fails, try to register
            print("Login failed. Attempting to register.")
            success, message = await server_comm.register(username, password)
            if success:
                print("Registration successful. Logging in.")
                success, message = await server_comm.login(username, password)

        if success:
            print("Logged in successfully!")
            self.is_authenticated = True
            return True
        else:
            print(f"Authentication failed: {message}")
            self.is_authenticated = False
            return False

    async def submit_game_score(self):
        if not self.is_authenticated:
            print("Not authenticated. Please log in to submit score.")
            success = await self.login_or_register()
            if not success:
                print("Authentication failed. Unable to submit score.")
                return

        success, message = await server_comm.submit_score(self.player_name, self.score)
        if success:
            print("Score submitted successfully!")
            await self.fetch_leaderboard()
        else:
            print(f"Failed to submit score: {message}")

    async def fetch_leaderboard(self):
        print("Fetching leaderboard data...")
        data, error = await server_comm.get_leaderboard()
        if error is None:
            self.game_menu.leaderboard_data = data
            self.game_menu.leaderboard_error = None
            print("Leaderboard data fetched successfully.")
        else:
            print(f"Failed to get leaderboard: {error}")
            self.game_menu.leaderboard_data = []
            self.game_menu.leaderboard_error = error


    async def display_player_stats(self):
        if self.is_authenticated:
            stats, error = await server_comm.get_player_stats()
            if stats:
                print(f"Player: {stats['username']}")
                print(f"Games played: {stats['games_played']}")
                print(f"Average score: {stats['average_score']:.2f}")
                print(f"Highest score: {stats['highest_score']}")
                # You would typically render this information on the screen
                # instead of printing it
            else:
                print(f"Failed to get player stats: {error}")
        else:
            print("Not authenticated. Please log in to view stats.")


    def run(self):
        running = True
        game_state = "main"

        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False
                elif game_state in ["main", "settings", "game_over", "leaderboard"]:
                    scaled_event = self.scale_event(event)
                    new_state = self.game_menu.handle_input(scaled_event)
                    if new_state == "login":
                        asyncio.run(self.login_or_register())
                    elif new_state in ["game", "restart"]:
                        self.reset_game()
                        game_state = "game"
                    else:
                        game_state = new_state
                elif game_state == "game":
                    game_state = self.handle_game_input(self.scale_event(event))
                elif game_state == "enter_name":
                    self.handle_name_input(event)
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.game_menu.set_player_score(self.player_name, self.score)
                        asyncio.run(self.submit_game_score())
                        game_state = "game_over"
                        self.game_menu.set_game_over()

            if game_state in ["main", "settings", "game_over", "leaderboard"]:
                self.game_menu.update()
                self.game_menu.draw()
            elif game_state == "game":
                new_state = self.update_game()
                if new_state == "game_over":
                    game_state = "enter_name"
                self.draw_game()
            elif game_state == "enter_name":
                self.draw_name_input()

            scaled_surface = pygame.transform.scale(self.screen, (self.game_width, self.game_height))
            self.real_screen.fill((0, 0, 0))
            self.real_screen.blit(scaled_surface, self.game_pos)
            pygame.display.flip()

        pygame.quit()

    def scale_event(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            x, y = event.pos
            scaled_x = (x - self.game_pos[0]) * (GAME_WIDTH / self.game_width)
            scaled_y = (y - self.game_pos[1]) * (GAME_HEIGHT / self.game_height)
            scaled_x = max(0, min(GAME_WIDTH, scaled_x))
            scaled_y = max(0, min(GAME_HEIGHT, scaled_y))
            return pygame.event.Event(event.type, {'pos': (scaled_x, scaled_y), 'button': event.button if hasattr(event, 'button') else None})
        return event
    
    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.clockwise = not self.clockwise
        elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
            return "menu"
        return "game"

    def handle_name_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                pass  # Handle in the main loop
            elif len(self.player_name) < 10:  # Limit name length
                self.player_name += event.unicode

    def draw_name_input(self):
        self.screen.fill(BLACK)
        font = self.font_manager.get_font(BASE_FONT_SIZE)
        
        prompt = font.render("Enter your name:", True, WHITE)
        prompt_rect = prompt.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50))
        self.screen.blit(prompt, prompt_rect)
        
        name = font.render(self.player_name, True, WHITE)
        name_rect = name.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 50))
        self.screen.blit(name, name_rect)

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
                        print(f"Score increased: {self.score}")  # Debug print
                        self.sound_manager.play_collect()
                        self.dots.remove(dot)
                    else:
                        self.game_over = True
                        self.sound_manager.play_game_over()
                        self.game_menu.set_game_over()
                        print(f"Game over. Final score: {self.score}")  # Debug print
                        return "game_over"

            self.frames_since_last_spawn += 1
            if self.frames_since_last_spawn >= DOT_SPAWN_RATE:
                self.dots.append(Dot())
                self.frames_since_last_spawn = 0

            self.difficulty_multiplier *= DIFFICULTY_INCREASE_RATE

        if self.game_over:
            self.sound_manager.play_game_over()
            return "game_over"

        return "game"

    def draw_game(self):
        self.draw_background()
        pygame.draw.circle(self.screen, WHITE, (GAME_WIDTH // 2, GAME_HEIGHT // 2), RING_RADIUS, RING_THICKNESS)
        for dot in self.dots:
            dot.draw(self.screen)
        self.player.draw(self.screen)
        self.twister.update()
        self.twister.draw(self.screen)

        font = self.font_manager.get_font(BASE_FONT_SIZE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(midtop=(GAME_WIDTH // 8, 10))
        self.screen.blit(score_text, score_rect)

    def draw_background(self):
        self.screen.fill(BACKGROUND_COLOR)
        for particle in self.background_particles:
            particle.move()
            particle.draw(self.screen)


if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    game = TwisterGame()
    game.run()