# Constants
GAME_WIDTH = 480
GAME_HEIGHT = 848
GAME_ASPECT_RATIO = GAME_WIDTH / GAME_HEIGHT
FONT_FILE = 'Roboto-Black.ttf'  # Replace with the path to your chosen font file
BASE_FONT_SIZE = 20  # This is the font size for the game's native resolution

FPS = 60
BACKGROUND_COLOR = (30, 30, 30) # Dark Background Color
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
GREY = (200, 200, 200)
LIGHT_GREY = (94, 94, 94) # Color for particles

# Game settings
RING_RADIUS = min(GAME_WIDTH, GAME_HEIGHT) // 3
PLAYER_RADIUS = 12
DOT_RADIUS = 8
PLAYER_SPEED = 4
DOT_SPAWN_RATE = 15
DIFFICULTY_INCREASE_RATE = 1.0002
RING_THICKNESS = 4