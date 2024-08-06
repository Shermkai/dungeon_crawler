import pygame

# Global constants
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
height = screen.get_height()
width = screen.get_width()

# Load sound effects
click_sound = pygame.mixer.Sound("sounds/click.wav")
oof_sound = pygame.mixer.Sound("sounds/oof.mp3")
slash_sound = pygame.mixer.Sound("sounds/slash.mp3")
slime_sound = pygame.mixer.Sound("sounds/slime.mp3")
rattle_sound = pygame.mixer.Sound("sounds/rattle.mp3")
