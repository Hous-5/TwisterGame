import pygame
import random
import asyncio
import logging
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
        self.setup_logger()
        pygame.init()
        pygame.mixer.init()
        self.setup_game_components()
        self.setup_display()
        self.initialize_game_state()
        self.player_name = ""
        self.is_authenticated = False

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def setup_game_components(self):
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.font_manager = FontManager(FONT_FILE)
        self.loop = asyncio.get_event_loop()

    def setup_display(self):
        self.real_screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen_width, self.screen_height = self.real_screen.get_size()
        self.screen = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Twister Game")
        self.calculate_scaling()
        self.game_menu = GameMenu(self.screen, self.sound_manager, self.font_manager)

    def calculate_scaling(self):
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

    def initialize_game_state(self):
        self.player = None
        self.dots = []
        self.twister = None
        self.score = 0
        self.game_over = False
        self.clockwise = True
        self.difficulty_multiplier = 1
        self.frames_since_last_spawn = 0
        self.time = 0
        self.background_particles = []
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.dots.clear()
        self.twister = Twister()
        self.score = 0
        self.game_over = False
        self.clockwise = True
        self.difficulty_multiplier = 1
        self.frames_since_last_spawn = 0
        self.time = 0
        self.background_particles = [BackgroundParticle() for _ in range(50)]
        self.logger.info(f"Game reset. Score: {self.score}")

    async def login_or_register(self):
        self.logger.info("Attempting to log in or register...")
        username = self.player_name
        password = "password"  # In a real game, you'd have a secure way to get this

        success, message = await server_comm.login(username, password)
        if not success:
            self.logger.info("Login failed. Attempting to register.")
            success, message = await server_comm.register(username, password)
            if success:
                self.logger.info("Registration successful. Logging in.")
                success, message = await server_comm.login(username, password)

        self.is_authenticated = success
        self.logger.info("Logged in successfully!" if success else f"Authentication failed: {message}")
        return success

    async def submit_game_score(self):
        if not self.is_authenticated:
            self.logger.warning("Not authenticated. Attempting to log in.")
            success = await self.login_or_register()
            if not success:
                self.logger.error("Authentication failed. Unable to submit score.")
                return

        success, message = await server_comm.submit_score(self.player_name, self.score)
        if success:
            self.logger.info("Score submitted successfully!")
            await self.fetch_leaderboard()
        else:
            self.logger.error(f"Failed to submit score: {message}")

    async def fetch_leaderboard(self):
        self.logger.info("Fetching leaderboard data...")
        try:
            result = await server_comm.get_leaderboard()
            self.logger.info(f"Raw result from get_leaderboard: {result}")
            
            if isinstance(result, tuple) and len(result) == 2:
                data, error = result
                if error is None:
                    # Unwrap the nested list
                    if isinstance(data, list) and len(data) > 0:
                        if isinstance(data[0], list):
                            data = data[0]
                        self.game_menu.leaderboard_data = data
                        self.game_menu.leaderboard_error = None
                    else:
                        self.game_menu.leaderboard_data = []
                        self.game_menu.leaderboard_error = "Invalid data format"
                    self.logger.info(f"Leaderboard data set in game_menu: {self.game_menu.leaderboard_data}")
                else:
                    self.logger.error(f"Error fetching leaderboard: {error}")
                    self.game_menu.leaderboard_data = []
                    self.game_menu.leaderboard_error = str(error) if error else "Unknown error"
            else:
                self.logger.error(f"Unexpected result format from get_leaderboard: {result}")
                self.game_menu.leaderboard_data = []
                self.game_menu.leaderboard_error = "Unexpected data format"
            
            self.logger.info(f"Final leaderboard_data in game_menu: {self.game_menu.leaderboard_data}")
            self.logger.info(f"Final leaderboard_error in game_menu: {self.game_menu.leaderboard_error}")
        except Exception as e:
            self.logger.error(f"Unexpected error while fetching leaderboard: {str(e)}")
            self.logger.exception("Exception details:")
            self.game_menu.leaderboard_data = []
            self.game_menu.leaderboard_error = f"Unexpected error: {str(e)}"

    async def display_player_stats(self):
        if self.is_authenticated:
            stats, error = await server_comm.get_player_stats()
            if stats:
                self.logger.info(f"Player: {stats['username']}")
                self.logger.info(f"Games played: {stats['games_played']}")
                self.logger.info(f"Average score: {stats['average_score']:.2f}")
                self.logger.info(f"Highest score: {stats['highest_score']}")
                # You would typically render this information on the screen
                # instead of logging it
            else:
                self.logger.error(f"Failed to get player stats: {error}")
        else:
            self.logger.warning("Not authenticated. Please log in to view stats.")

    def run(self):
        running = True
        game_state = "main"

        while running:
            self.clock.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    running = False
                else:
                    game_state = self.handle_event(event, game_state)

            game_state = self.update_game_state(game_state)
            self.render_game_state(game_state)

            scaled_surface = pygame.transform.scale(self.screen, (self.game_width, self.game_height))
            self.real_screen.fill((0, 0, 0))
            self.real_screen.blit(scaled_surface, self.game_pos)
            pygame.display.flip()

        pygame.quit()

    def handle_event(self, event, game_state):
        scaled_event = self.scale_event(event)
        
        if game_state in ["main", "settings", "game_over", "leaderboard"]:
            return self.handle_menu_event(scaled_event)
        elif game_state == "game":
            return self.handle_game_input(scaled_event)
        elif game_state == "enter_name":
            return self.handle_name_input(event, game_state)
        
        return game_state

    def handle_menu_event(self, event):
        new_state = self.game_menu.handle_input(event)
        if new_state == "login":
            asyncio.run(self.login_or_register())
        elif new_state in ["game", "restart"]:
            self.reset_game()
            return "game"
        return new_state

    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.clockwise = not self.clockwise
        elif event.type == pygame.MOUSEBUTTONDOWN and self.game_over:
            return "menu"
        return "game"

    def handle_name_input(self, event, game_state):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key == pygame.K_RETURN:
                self.game_menu.set_player_score(self.player_name, self.score)
                asyncio.run(self.submit_game_score())
                game_state = "game_over"
                self.game_menu.set_game_over()
            elif len(self.player_name) < 10:  # Limit name length
                self.player_name += event.unicode
        return game_state

    def update_game_state(self, game_state):
        if game_state in ["main", "settings", "game_over", "leaderboard"]:
            self.game_menu.update()
        elif game_state == "game":
            if self.game_over:
                return "enter_name"
            self.update_game()
        return game_state

    def update_game(self):
        self.player.move(self.clockwise, self.difficulty_multiplier)
        self.update_dots()
        self.spawn_new_dot()
        self.difficulty_multiplier *= DIFFICULTY_INCREASE_RATE

        if self.game_over:
            self.sound_manager.play_game_over()
            self.game_menu.set_game_over()
            self.logger.info(f"Game over. Final score: {self.score}")

    def update_dots(self):
        for dot in self.dots[:]:
            dot.move(self.difficulty_multiplier)
            if dot.distance > RING_RADIUS + DOT_RADIUS:
                self.dots.remove(dot)
            elif self.player.collides_with(dot):
                if dot.good:
                    self.score += 1
                    self.logger.info(f"Score increased: {self.score}")
                    self.sound_manager.play_collect()
                    self.dots.remove(dot)
                else:
                    self.game_over = True
                    self.sound_manager.play_game_over()
                    self.game_menu.set_game_over()
                    self.logger.info(f"Game over. Final score: {self.score}")
                    return "game_over"

    def spawn_new_dot(self):
        self.frames_since_last_spawn += 1
        if self.frames_since_last_spawn >= DOT_SPAWN_RATE:
            self.dots.append(Dot())
            self.frames_since_last_spawn = 0

    def render_game_state(self, game_state):
        if game_state in ["main", "settings", "game_over", "leaderboard"]:
            self.game_menu.draw()
        elif game_state == "game":
            self.draw_game()
        elif game_state == "enter_name":
            self.draw_name_input()

    def draw_game(self):
        self.draw_background()
        pygame.draw.circle(self.screen, WHITE, (GAME_WIDTH // 2, GAME_HEIGHT // 2), RING_RADIUS, RING_THICKNESS)
        for dot in self.dots:
            dot.draw(self.screen)
        self.player.draw(self.screen)
        self.twister.update()
        self.twister.draw(self.screen)
        self.draw_score()

    def draw_background(self):
        self.screen.fill(BACKGROUND_COLOR)
        for particle in self.background_particles:
            particle.move()
            particle.draw(self.screen)

    def draw_score(self):
        font = self.font_manager.get_font(BASE_FONT_SIZE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(midtop=(GAME_WIDTH // 8, 10))
        self.screen.blit(score_text, score_rect)

    def draw_name_input(self):
        self.screen.fill(BLACK)
        font = self.font_manager.get_font(BASE_FONT_SIZE)
        
        prompt = font.render("Enter your name:", True, WHITE)
        prompt_rect = prompt.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50))
        self.screen.blit(prompt, prompt_rect)
        
        name = font.render(self.player_name, True, WHITE)
        name_rect = name.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 50))
        self.screen.blit(name, name_rect)

    def scale_event(self, event):
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            x, y = event.pos
            scaled_x = (x - self.game_pos[0]) * (GAME_WIDTH / self.game_width)
            scaled_y = (y - self.game_pos[1]) * (GAME_HEIGHT / self.game_height)
            scaled_x = max(0, min(GAME_WIDTH, scaled_x))
            scaled_y = max(0, min(GAME_HEIGHT, scaled_y))
            return pygame.event.Event(event.type, {'pos': (scaled_x, scaled_y), 'button': getattr(event, 'button', None)})
        return event

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    game = TwisterGame()
    game.run()