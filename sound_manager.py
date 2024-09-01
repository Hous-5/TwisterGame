import pygame

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.load_sounds()
        self.master_volume = 0.75
        self.music_volume = 0.03
        self.sfx_volume = 0.3
        self.update_volumes()
        pygame.mixer.music.play(-1)  # -1 means loop indefinitely

    def load_sounds(self):
        pygame.mixer.music.load('endlessmotion.mp3')
        self.collect_sound = pygame.mixer.Sound('coin_collect.wav')
        self.game_over_sound = pygame.mixer.Sound('game_over.wav')
        self.menu_select_sound = pygame.mixer.Sound('menu_select.wav')
        self.menu_click_sound = pygame.mixer.Sound('menu_click.wav')

    def update_volumes(self):
        pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
        self.collect_sound.set_volume(self.master_volume * self.sfx_volume)
        self.game_over_sound.set_volume(self.master_volume * self.sfx_volume)
        self.menu_select_sound.set_volume(self.master_volume * self.sfx_volume)
        self.menu_click_sound.set_volume(self.master_volume * self.sfx_volume)

    def play_collect(self):
        self.collect_sound.play()

    def play_game_over(self):
        self.game_over_sound.play()

    def play_menu_select(self):
        self.menu_select_sound.play()

    def play_menu_click(self):
        self.menu_click_sound.play()

    def set_master_volume(self, volume):
        self.master_volume = max(0, min(1, volume))
        self.update_volumes()

    def set_music_volume(self, volume):
        self.music_volume = max(0, min(1, volume))
        self.update_volumes()

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0, min(1, volume))
        self.update_volumes()