import pygame

class FontManager:
    def __init__(self, font_file):
        self.font_file = font_file
        self.fonts = {}
        self.scale_factor = 1

    def update_scale_factor(self, scale_factor):
        self.scale_factor = scale_factor
        self.fonts.clear()  # Clear cached fonts when scale changes

    def get_font(self, base_size):
        scaled_size = int(base_size * self.scale_factor)
        if scaled_size not in self.fonts:
            self.fonts[scaled_size] = pygame.font.Font(self.font_file, scaled_size)
        return self.fonts[scaled_size]