# holds the Player class

import pygame
pygame.init()


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
        lcol = self.rect.left // environment.game_settings.block_size # same thing with column
        rcol = self.rect.right // environment.game_settings.block_size
        if self.jumping:
            row = (self.rect.top // environment.game_settings.block_size) # convert top of player from px to blcks
            if environment.num_env[row][lcol] != 0 and environment.num_env[row][rcol != 0]:
                self.rect.top = (row + 1) * environment.game_settings.block_size # keep player from traveling up
        else:
            row = (self.rect.bottom // environment.game_settings.block_size) # convert bottom of player from px to blcks
            if environment.num_env[row][lcol] != 0 and environment.num_env[row][rcol] != 0: # if the bottom is NOT touching empty space
                self.grounded = True # the player must be on the ground
                self.rect.bottom = row * environment.game_settings.block_size # set the bottom of the player as the blck
                self.yvel = 0 # set the y velocity as zero
            else: # if we are on empty space
                self.grounded = False # then we must be falling

    def check_left(self, lcol, top_row, bottom_row, environment):
        if self.rect.left % 10 == 0:
            lcol -= 1
        lblocks = [environment.num_env[i][lcol] for i in range(top_row, bottom_row)]
        # gets all possible block values that the player could collide with
        if any(lblocks):
            self.rect.left = (lcol + 1) * environment.game_settings.block_size
            return False
        else:
            return True

    def check_right(self, rcol, top_row, bottom_row, environment):
        if self.right:
            rblocks = [environment.num_env[i][rcol] for i in range(top_row, bottom_row)]
            # gets all possible block values that the player could collide with
            if any(rblocks):
                self.rect.right = rcol * environment.game_settings.block_size
                return False
            else:
                return True

    def check_side(self, environment):
        '''checks if there is a block to the side of the character'''
        bottom_row = (self.rect.bottom // environment.game_settings.block_size)
        top_row = (self.rect.top // environment.game_settings.block_size)
        lcol = self.rect.left // environment.game_settings.block_size # check if the left of player is not on ground
        rcol = self.rect.right // environment.game_settings.block_size
        if self.right:
            return self.check_right(rcol, top_row, bottom_row, environment)
        elif self.left:
            return self.check_left(lcol, top_row, bottom_row, environment)

    def update(self, environment):
        self.updatex(environment) # update the player's x coordinate
        self.updatey(environment) # update the player's y coordinate
        self.destroy(environment) # destroy a block if needed

    def updatex(self, environment):
        can_go = self.check_side(environment) # True if no block hindering movement
        if can_go:
            if self.left: # if going left
                self.rect.centerx -= self.xvel # move the player left by the current velocity
                if self.rect.left < 0: # keep the player on the screen
                    self.rect.left = 0
                    self.left = False
            else:
                if self.right: # if going right
                    self.rect.centerx += self.xvel # move the player right by the current velocity
                    if self.rect.right > self.screen_rect.right: # keep the player on the screen
                        self.rect.right = self.screen_rect.right
                        self.right = False

    def updatey(self, environment):
        self.check_underneath(environment) # True if there are no blocks hindering movement (up or down)
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
