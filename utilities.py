def draw_text_centered(surface, text, font, color, center_position):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_position)
    surface.blit(text_surface, text_rect)