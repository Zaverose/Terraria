import pygame
import sys
import environment as env
import game_settings as gs
from player import Player

pygame.init()
window = pygame.display.set_mode((1400, 800))
pygame.display.set_caption("Minecraft 2D")
clock = pygame.time.Clock()

# rendering messages and fonts
font = pygame.font.SysFont("Arial", 25) # sets a Font object
greeting_msg = font.render("Press 'Q' to exit the game", False, (230, 230, 230))
greeting_msg_rect = greeting_msg.get_rect(topleft=(0, 0))

# Inventory screen
font = pygame.font.SysFont("Arial", 40)
game_over_msg = font.render("INVENTORY", False, (230, 230, 230))
game_over_msg_rect = greeting_msg.get_rect(midbottom=(700, 300))

WORLD_DIMENSIONS = (80, 140)

BLOCK_DIMENSIONS = 10

BLOCK_COLORS = {"BACKGROUND" : (0, 150, 230), "DIRT" : (165, 42, 42), "STONE" : (128, 128, 128),
                "COAL" : (0, 0, 0), "IRON" : (128, 0, 0), "DIAMOND" : (0, 255, 255),
                "WOOD" : (181, 101, 29), "LEAF" : (0, 255, 0)}


# Initializing the game
game_settings = gs.Game_Settings(BLOCK_DIMENSIONS, WORLD_DIMENSIONS, BLOCK_COLORS)
environment = env.Environment(window, game_settings)
environment.create_environment()
player = Player(window)

# global to be used in while loop
menu = False

while True:
    while menu:
        player.display_inventory(environment)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    sys.exit()
                if event.key == pygame.K_p:
                    menu = False

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            player.breaking = True
        if event.type == pygame.MOUSEBUTTONUP:
            player.breaking = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                sys.exit()
            if event.key == pygame.K_a:
                player.left = True
            if event.key == pygame.K_d:
                player.right = True
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_p:
                menu = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                player.left = False
            if event.key == pygame.K_d:
                player.right = False
        elif event.type == pygame.QUIT:
            sys.exit()

    window.fill(BLOCK_COLORS["BACKGROUND"])
    environment.draw_environment()
    player.update(environment)
    player.draw(window)
    pygame.display.flip()
    clock.tick(30)
