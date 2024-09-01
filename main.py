import pygame
import asyncio
import logging
from player import Player
from dot import Dot
from twister import Twister
from background_particle import BackgroundParticle
from game_settings import *
from sound_manager import SoundManager
from game_menu import GameMenu
from settings_menu import SettingsMenu
from pause_menu import PauseMenu
from leaderboard_menu import LeaderboardMenu
from login_menu import LoginMenu
from font_manager import FontManager
from server_communication import server_comm
from power_up import PowerUpManager
from achievements import AchievementManager
from particle import ParticleSystem

class GameState:
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    SETTINGS = 3
    PAUSED = 4
    LEADERBOARD = 5
    LOGIN = 6

class TwisterGame:
    def __init__(self):
        pygame.init()
        self.setup_logger()
        self.setup_display()
        self.setup_game_components()
        self.initialize_game_state()
        self.state = GameState.MENU
        self.previous_state = None
        self.score_submitted = False
        self.is_logged_in = False
        self.username = ""

    def setup_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def setup_display(self):
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Twister Game")

    def setup_game_components(self):
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.font_manager = FontManager(FONT_FILE)
        self.game_menu = GameMenu(self.screen, self.sound_manager, self.font_manager)
        self.settings_menu = SettingsMenu(self.screen, self.sound_manager, self.font_manager)
        self.pause_menu = PauseMenu(self.screen, self.sound_manager, self.font_manager)
        self.leaderboard_menu = LeaderboardMenu(self.screen, self.font_manager, server_comm)
        self.login_menu = LoginMenu(self.screen, self.font_manager, server_comm)
        self.power_up_manager = PowerUpManager()
        self.achievement_manager = AchievementManager()
        self.particle_system = ParticleSystem()

    def initialize_game_state(self):
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

    async def run(self):
        running = True
        while running:
            self.clock.tick(FPS)
            running = await self.handle_events()
            self.update()
            self.render()
            await asyncio.sleep(0)  # Allow other async operations to run
        pygame.quit()

    def setup_game_components(self):
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()
        self.font_manager = FontManager(FONT_FILE)
        self.game_menu = GameMenu(self.screen, self.sound_manager, self.font_manager)
        self.settings_menu = SettingsMenu(self.screen, self.sound_manager, self.font_manager)
        self.pause_menu = PauseMenu(self.screen, self.sound_manager, self.font_manager)
        self.leaderboard_menu = LeaderboardMenu(self.screen, self.font_manager, server_comm)
        self.login_menu = LoginMenu(self.screen, self.font_manager, server_comm)
        self.power_up_manager = PowerUpManager()
        self.achievement_manager = AchievementManager()
        self.particle_system = ParticleSystem()

    async def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if self.state == GameState.MENU:
                menu_action = self.game_menu.handle_input(event)
                if menu_action == "quit":
                    return False
                elif menu_action == "startgame":
                    self.state = GameState.PLAYING
                    self.initialize_game_state()
                elif menu_action == "settings":
                    self.state = GameState.SETTINGS
                elif menu_action == "leaderboard":
                    self.state = GameState.LEADERBOARD
                    await self.leaderboard_menu.fetch_leaderboard()
                elif menu_action == "login":
                    self.state = GameState.LOGIN
            elif self.state == GameState.PLAYING:
                self.handle_game_event(event)
            elif self.state == GameState.GAME_OVER:
                await self.handle_game_over_event(event)
            elif self.state == GameState.SETTINGS:
                settings_action = self.settings_menu.handle_input(event)
                if settings_action == "mainmenu":
                    self.state = GameState.MENU
            elif self.state == GameState.PAUSED:
                pause_action = self.pause_menu.handle_input(event)
                if pause_action == "resume":
                    self.state = GameState.PLAYING
                elif pause_action == "settings":
                    self.state = GameState.SETTINGS
                elif pause_action == "mainmenu":
                    self.state = GameState.MENU
            elif self.state == GameState.LEADERBOARD:
                leaderboard_action = self.leaderboard_menu.handle_input(event)
                if leaderboard_action == "mainmenu":
                    self.state = GameState.MENU
            elif self.state == GameState.LOGIN:
                login_action, username = await self.login_menu.handle_input(event)
                if login_action == "success":
                    self.is_logged_in = True
                    self.username = username
                    self.state = GameState.MENU
                elif login_action == "back":
                    self.state = GameState.MENU

        return True

    def handle_menu_event(self, event):
        action = self.game_menu.handle_input(event)
        if action == "startgame":
            self.logger.info("Starting new game")
            self.state = GameState.PLAYING
            self.initialize_game_state()
        elif action == "settings":
            self.logger.info("Entering settings menu")
            self.state = GameState.SETTINGS
        return action

    def handle_settings_event(self, event):
        action = self.settings_menu.handle_input(event)
        if action == "return":
            if self.previous_state == GameState.PAUSED:
                self.state = GameState.PLAYING
            else:
                self.state = self.previous_state or GameState.MENU
            self.previous_state = None

    def handle_pause_event(self, event):
        action = self.pause_menu.handle_input(event)
        if action == "resume":
            self.state = GameState.PLAYING
        elif action == "settings":
            self.previous_state = GameState.PAUSED
            self.state = GameState.SETTINGS
            self.settings_menu.set_previous_state(GameState.PAUSED)
        elif action == "quittomainmenu":
            self.state = GameState.MENU

    def update(self):
        if self.state == GameState.PLAYING:
            self.update_game()
        elif self.state == GameState.MENU:
            self.game_menu.update()
        elif self.state == GameState.SETTINGS:
            pass  # Settings menu doesn't need continuous updates
        elif self.state == GameState.PAUSED:
            pass  # Pause menu doesn't need continuous updates

    def handle_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.clockwise = not self.clockwise
            elif event.key == pygame.K_ESCAPE:
                self.state = GameState.PAUSED

    async def handle_game_over_event(self, event):
        if not self.score_submitted:
            await self.submit_score()
            self.score_submitted = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            self.state = GameState.MENU
            self.score_submitted = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.state = GameState.MENU
            self.score_submitted = False

    async def submit_score(self):
        if not self.is_logged_in:
            self.logger.error("Cannot submit score: Not logged in")
            return

        success, message = await server_comm.submit_score(self.score)
        if success:
            self.logger.info("Score submitted successfully!")
            await self.leaderboard_menu.fetch_leaderboard()
        else:
            self.logger.error(f"Failed to submit score: {message}")

    def update_game(self):
        self.player.move(self.clockwise, self.difficulty_multiplier)
        self.update_dots()
        self.spawn_new_dot()
        self.difficulty_multiplier *= DIFFICULTY_INCREASE_RATE
        self.power_up_manager.update(self.player, self.difficulty_multiplier, 1 / FPS)
        self.particle_system.update(1 / FPS)
        self.achievement_manager.update(self)

        if self.game_over:
            self.state = GameState.GAME_OVER
            self.sound_manager.play_game_over()

    def update_dots(self):
        for dot in self.dots[:]:
            dot.move(self.difficulty_multiplier)
            if dot.distance > RING_RADIUS + DOT_RADIUS:
                self.dots.remove(dot)
            elif self.player.collides_with(dot):
                if dot.good:
                    self.score += int(1 * self.player.get_score_multiplier())
                    self.player.increase_combo()
                    self.sound_manager.play_collect()
                    self.particle_system.create_particles(dot.x, dot.y, GREEN)
                    self.dots.remove(dot)
                else:
                    self.game_over = True
                    self.particle_system.create_particles(dot.x, dot.y, RED)

    def spawn_new_dot(self):
        self.frames_since_last_spawn += 1
        if self.frames_since_last_spawn >= DOT_SPAWN_RATE:
            self.dots.append(Dot())
            self.frames_since_last_spawn = 0

    def render(self):
        self.screen.fill(BACKGROUND_COLOR)
        if self.state == GameState.MENU:
            self.game_menu.draw(self.is_logged_in, self.username)
        elif self.state == GameState.PLAYING:
            self.render_game()
        elif self.state == GameState.GAME_OVER:
            self.render_game()
            self.render_game_over()
        elif self.state == GameState.SETTINGS:
            self.settings_menu.draw()
        elif self.state == GameState.PAUSED:
            self.render_game()
            self.pause_menu.draw(self.screen)
        elif self.state == GameState.LEADERBOARD:
            self.leaderboard_menu.draw()
        elif self.state == GameState.LOGIN:
            self.login_menu.draw()
        
        pygame.display.flip()

    def render_game(self):
        for particle in self.background_particles:
            particle.move()
            particle.draw(self.screen)
        pygame.draw.circle(self.screen, WHITE, (GAME_WIDTH // 2, GAME_HEIGHT // 2), RING_RADIUS, RING_THICKNESS)
        self.power_up_manager.draw(self.screen)
        for dot in self.dots:
            dot.draw(self.screen)
        self.player.draw(self.screen)
        self.twister.update()
        self.twister.draw(self.screen)
        self.draw_score()
        self.particle_system.draw(self.screen)

    def draw_score(self):
        font = self.font_manager.get_font(BASE_FONT_SIZE)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

    def render_game_over(self):
        overlay = pygame.Surface((GAME_WIDTH, GAME_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Semi-transparent black
        self.screen.blit(overlay, (0, 0))

        font = self.font_manager.get_font(BASE_FONT_SIZE * 2)
        game_over_text = font.render("Game Over", True, RED)
        game_over_rect = game_over_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, game_over_rect)

        font = self.font_manager.get_font(BASE_FONT_SIZE)
        score_text = font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 20))
        self.screen.blit(score_text, score_rect)

        instruction_text = font.render("Click or press Enter to return to main menu", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2 + 70))
        self.screen.blit(instruction_text, instruction_rect)

async def main():
    game = TwisterGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())