# contains all the classes and functions pertaining to the environment in the game

import pygame
import random

pygame.init()


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


class Tree:
    '''A class to represent a tree'''

    def __init__(self):
        self.wood_height = random.randint(4, 7)
        self.leaf_spread = self.wood_height - 2
        self.wood_tag = 6
        self.leaf_tag = 7


class Ore:
    '''A class to represent an ore'''

    def __init__(self, tag, gen_bounds, spawn_prob, min_spawn):
        self.tag = tag # integer to ID in num_env
        self.gen_bounds = gen_bounds # the (min, max) number of blocks a cluster of this ore can have
        self.spawn_prob = spawn_prob # the probability (0, 100) that this ore will be chosen to spawn
        self.min_spawn = min_spawn # the minimum level (y) this ore can spawn at

    def set_start_spawn(self, game_settings):
        '''Set the starting spawn level for the ore'''
        self.start_spawn = random.randint(self.min_spawn, game_settings.block_dimensions[0] - 1)


class Environment():
    '''A class to hold the game environment'''

    diamond = Ore(5, (3, 9), 5, 60)
    iron = Ore(4, (2, 6), 25, 40)
    coal = Ore(3, (4, 12), 75, 0)
    ores = (diamond, iron, coal)

    valid_ores_nums = [2] # add stone's tag to the valid_ores list
    for ore in ores: # creates a list of block tags that an ore is allowed to replace when spawning (stone / other ores)
        valid_ores_nums.append(ore.tag)

    def __init__(self, screen, game_settings):
        self.screen = screen
        self.game_settings = game_settings
        self.num_env = [] # initialize an empty num_env that will become a 2D array to store block values
        self.surface_values = [] # list that will store the y value of the topmost stone block for each column
        self.initialize_env() # fill num_env with a bunch of 0's


    def initialize_env(self):
        '''Fills num_env with a bunch of 0's'''
        for row in range(self.game_settings.block_dimensions[0]):
            new = []
            for column in range(self.game_settings.block_dimensions[1]):
                new.append(0)
            self.num_env.append(new)


    def create_environment(self):
        '''Creates the environment'''
        self.create_stone() # creates stone
        self.create_dirt() # creates dirt layer on top
        for i in range(50):
            self.create_ore_cluster() # creates "n" random ore clusters
        for i in range(3):
            self.create_tree() # creates "n" trees

    def create_tree(self):
        '''Creates the trees'''
        tree = Tree() # instantiates a new tree object with a random tree height
        column = random.randint(0, self.game_settings.block_dimensions[1] - 1) # selects a random x value for tree
        can_plant = check_cols(self.num_env, column, 4, tree.wood_tag) # checks that no other tree is within 3 blocks
        if can_plant: # if no other tree is within 3 blocks
            row = self.surface_values[column] - 3 # find the starting y value for the trunk to begin
            for step in range(tree.wood_height): # loop as many times as the height of the tree is
                self.num_env[row][column] = tree.wood_tag # change the current position to be wood
                if row <= 0: # if you've hit the top of the screen, don't go further
                    row = 0
                else: # otherwise, keep climbing up
                    row -= 1
            self.create_leaves(tree, column)

    def create_leaves(self, tree, column):
        '''Creates the leaves on each tree
        ONLY TO BE USED IN THE 'create_tree' method'''
        end_row = self.surface_values[column] - 5 # find the end row
        start_row = self.surface_values[column] - 5 - tree.leaf_spread # find the start row
        if start_row > 0:
            spread = 0
            while spread < tree.leaf_spread:
                for row in range(start_row, end_row):
                    if row >= 0:
                        for col in range(column - spread, column + spread + 1):
                            if 0 <= col < self.game_settings.block_dimensions[1]:
                                if self.num_env[row][col] == 0:
                                    self.num_env[row][col] = tree.leaf_tag
                    spread += 1

    def create_stone(self):
        '''create the stone of the world'''
        highest_bound = self.game_settings.block_dimensions[0] // 5 # highest possible starting surface value
        lowest_bound = self.game_settings.block_dimensions[0] // 4 # lowest possible starting surface value
        surface_val = random.randint(highest_bound, lowest_bound) # pick a random spot between (inclusive) for surf_val
        for column in range(self.game_settings.block_dimensions[1]): # iterating through column by column
            for row in range(surface_val, self.game_settings.block_dimensions[0]):
                self.num_env[row][column] = 2
                if len(self.surface_values) <= column:
                    self.surface_values.append(row) # appends this row's top stone block to surface values
            surface_val += random.randint(0, self.game_settings.block_dimensions[0] // 40) * random.randint(-1, 1)
            # move the new surface value up or down a certain amount
            if surface_val < 4: # if new surface value is less than 4
                surface_val = 4 # set it to 4
            elif surface_val > self.game_settings.block_dimensions[0]: # if it's gone beyond bottom of the screen
                surface_val = self.game_settings.block_dimensions[0] # set it equal to the bottom of the screen

    def create_ore_cluster(self):
        '''creates a cluster of coal'''
        ore = self.pick_ore() # pick an ore to spawn
        ore.set_start_spawn(self.game_settings) # pick a random starting row (y)
        column = random.randint(0, self.game_settings.block_dimensions[1] - 1) # pick a random starting column (x)
        row = ore.start_spawn
        num_blocks = random.randint(ore.gen_bounds[0], ore.gen_bounds[1]) # initialize the # of blocks in this cluster
        for i in range(num_blocks): # loop as many times as there are blocks in this cluster
            if column < 0: # if too far left
                column = 0
            elif column >= self.game_settings.block_dimensions[1]: # if too far right
                column = self.game_settings.block_dimensions[1] - 1
            if row >= self.game_settings.block_dimensions[0]: # if too far down
                row = self.game_settings.block_dimensions[0] - 1
            elif row < self.surface_values[column]: # if too far up
                row = self.surface_values[column]
            self.num_env[row][column] = ore.tag # set the position as ore
            column += 1 * random.randint(-1, 1) # find new column (x)
            row += 1 * random.randint(-1, 1) # find new row (y)

    def pick_ore(self):
        '''selects an ore to generate'''
        num = random.randint(0, 100) # pick a random number 1 - 100
        for ore in Environment.ores: # for possible Ores
            if num < ore.spawn_prob: # if number chosen is less than that ore's spawn probability
                return ore # return it
        return Environment.ores[len(Environment.ores) - 1] # otherwise return the last Ore in the list (the most common)

    def create_dirt(self):
        '''creates a layer of 3 dirt on top of the stone'''
        for column in range(self.game_settings.block_dimensions[1]): # iterate through by column
            top_stone = self.surface_values[column] # locate the value of the top stone
            dirt_surface = self.surface_values[column] - 3 # create new surface value
            for row in range(dirt_surface, top_stone): # for values in between
                self.num_env[row][column] = 1 # turn those rows into dirt

    def draw_environment(self):
        '''draws the environment to the screen'''
        row_num = 0
        for row in self.num_env:
            block_num = 0
            for block in row:
                color = self.get_block_color(block)
                if color:
                    rect = pygame.Rect(0, 0, self.game_settings.block_size, self.game_settings.block_size)
                    rect.topleft = (block_num * self.game_settings.block_size, row_num * self.game_settings.block_size)
                    pygame.draw.rect(self.screen, color, rect)
                block_num += 1
            row_num += 1

    def get_block_color(self, block_id):
        '''draws given block to the screen'''
        if block_id:
            if block_id == 1:
                return self.game_settings.colors["DIRT"]
            elif block_id == 2:
                return self.game_settings.colors["STONE"]
            elif block_id == 3:
                return self.game_settings.colors["COAL"]
            elif block_id == 4:
                return self.game_settings.colors["IRON"]
            elif block_id == 5:
                return self.game_settings.colors["DIAMOND"]
            elif block_id == 6:
                return self.game_settings.colors["WOOD"]
            elif block_id == 7:
                return self.game_settings.colors["LEAF"]
        return None

    def get_block_name(self, block_id):
        if block_id:
            if block_id == 1:
                return "DIRT"
            elif block_id == 2:
                return "STONE"
            elif block_id == 3:
                return "COAL"
            elif block_id == 4:
                return "IRON"
            elif block_id == 5:
                return "DIAMOND"
            elif block_id == 6:
                return "WOOD"
            elif block_id == 7:
                return "LEAF"
        return None

