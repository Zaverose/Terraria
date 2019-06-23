import pygame
import sys
import environment as env
import game_settings as gs

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


def check_cols(arr, start, spread, element, two_sided=True):
    '''checks if an element exists in a 2-D array on the left or right of the column col to a 'spread' of range.
    returns True if the element is not within the spread, false if it is.
    Assumes the array is rectangular (width and length are constant)'''
    length = len(arr)
    left_bound, right_bound = 0, len(arr[0]) - 1 # assumption of rectangular array
    if two_sided:
        for i in range(spread): # for place in spread
            for row in range(length): # for row in current column
                if start + i > right_bound: # if we've gone past the right border of the array
                    break # break this loop
                else:
                    if element == arr[row][start + i]: # if the element is equal to
                        return False
                if start - i < left_bound:
                    break
                else:
                    if element == arr[row][start - i]:
                        return False
    return True


class Player():
    '''A class to represent the player'''

    color = (0, 100, 100)
    width = 8
    height = 20
    gravity = -1.5

    def __init__(self, screen):
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.rect = pygame.Rect(0, 0, Player.width, Player.height)
        self.yvel = 0
        self.max_y_vel = 9
        self.xvel = 5
        # Movement Flags
        self.grounded = False
        self.jumping = False
        self.left = False
        self.right = False
        # Action Flags
        self.breaking = False

        # Inventory
        self.inventory = {}
        self.inv_screen_bounds = pygame.Rect(500, 300, 400, 100)


    def draw(self, screen):
        pygame.draw.rect(screen, Player.color, self.rect)

    def check_underneath(self, environment):
        '''checks if there is a block underneath or above the character currently'''
        col = (self.rect.centerx // environment.game_settings.block_size) # same thing with column
        if self.jumping:
            row = (self.rect.top // environment.game_settings.block_size) # convert top of player from px to blcks
            if environment.num_env[row][col] != 0:
                self.rect.top = (row + 1) * environment.game_settings.block_size # keep player from traveling up
        else:
            row = (self.rect.bottom // environment.game_settings.block_size) # convert bottom of player from px to blcks
            if environment.num_env[row][col] != 0: # if the bottom is NOT touching empty space
                self.grounded = True # the player must be on the ground
                self.rect.bottom = row * environment.game_settings.block_size # set the bottom of the player as the blck
                self.yvel = 0 # set the y velocity as zero
            else: # if we are on empty space
                self.grounded = False # then we must be falling

    def check_side(self, environment):
        '''checks if there is a block to the side of the character'''
        bottom_row = (self.rect.bottom // environment.game_settings.block_size)
        top_row = (self.rect.top // environment.game_settings.block_size)
        lcol = self.rect.left // environment.game_settings.block_size # check if the left of player is not on ground
        rcol = self.rect.right // environment.game_settings.block_size
        if self.right:
            rblocks = [environment.num_env[i][rcol] for i in range(top_row, bottom_row)]
            # gets all possible block values that the player could collide with
            if any(rblocks):
                self.rect.right = rcol * environment.game_settings.block_size
                return False
            else:
                return True
        elif self.left:
            if self.rect.left % 10 == 0:
                lcol -= 1
            lblocks = [environment.num_env[i][lcol] for i in range(top_row, bottom_row)]
            # gets all possible block values that the player could collide with
            if any(lblocks):
                self.rect.left = (lcol + 1) * environment.game_settings.block_size
                return False
            else:
                return True

    def update(self, environment):
        self.updatex(environment)
        self.updatey(environment)
        self.destroy(environment)

    def updatex(self, environment):
        can_go = self.check_side(environment)
        if can_go:
            if self.left:
                self.rect.centerx -= self.xvel
                if self.rect.left < 0:
                    self.rect.left = 0
                    self.left = False
            else:
                if self.right:
                    self.rect.centerx += self.xvel
                    if self.rect.right > self.screen_rect.right:
                        self.rect.right = self.screen_rect.right
                        self.right = False

    def updatey(self, environment):
        self.check_underneath(environment)
        if not self.grounded:
            self.yvel -= Player.gravity
            if self.yvel > self.max_y_vel:
                self.yvel = self.max_y_vel
            if self.yvel >= 0:
                self.jumping = False
            self.rect.centery += self.yvel
        if self.rect.bottom >= self.screen_rect.bottom:
            self.rect.bottom = self.screen_rect.bottom
            self.grounded = True
            self.yvel = 0

    def jump(self):
        self.yvel = -10
        self.grounded = False
        self.jumping = True

    def destroy(self, environment):
        '''destroys a block'''
        if self.breaking:
            blck_sz = environment.game_settings.block_size
            mouse_cord = pygame.mouse.get_pos()
            xbounds = (self.rect.left - blck_sz * 10, self.rect.right + blck_sz * 10)
            ybounds = (self.rect.top - blck_sz * 10, self.rect.bottom + blck_sz * 10)
            if xbounds[0] < mouse_cord[0] < xbounds[1] and ybounds[0] < mouse_cord[1] < ybounds[1]:
                mouse_block = (mouse_cord[0] // blck_sz, mouse_cord[1] // blck_sz)
                tag = environment.num_env[mouse_block[1]][mouse_block[0]]
                if tag != 0:
                    block_name = environment.get_block_name(tag)
                    if block_name in self.inventory:
                        self.inventory[block_name] += 1
                    else:
                        self.inventory[block_name] = 1
                    environment.num_env[mouse_block[1]][mouse_block[0]] = 0

    def display_inventory(self, environment):
        font = pygame.font.SysFont("Arial", 40)
        inventory_msg = font.render("INVENTORY", False, (230, 230, 230))
        inventory_rect = inventory_msg.get_rect(midbottom=(700, 300))
        pygame.draw.rect(self.screen, (255, 255, 255), self.inv_screen_bounds)
        self.screen.blit(inventory_msg, inventory_rect)
        block = pygame.Rect(self.inv_screen_bounds.left + 10, self.inv_screen_bounds.top + 10, 40, 40)
        top = block.top + 30
        left = block.left + 30
        font = pygame.font.SysFont("Arial", 20)
        for name, value in self.inventory.items():
            block_msg = font.render(str(value), False, (0, 0, 0))
            block_rect = block_msg.get_rect(topleft=(left, top))
            pygame.draw.rect(self.screen, environment.game_settings.colors[name], block)
            self.screen.blit(block_msg, block_rect)
            left += 50
            block.left += 50


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

# globals to be used in while loop
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
