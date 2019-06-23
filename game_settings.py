# contains the class and functions for the game's settings

class Game_Settings():
    '''A class to hold the game's settings'''

    def __init__(self, block_size, block_dimensions, colors):
        self.block_size = block_size # the side length (pixels) of blocks in this world
        self.block_dimensions = block_dimensions # the (height, width) of the world (measured in blocks)
        self.colors = colors # dictionary {"BLOCK_NAME" : (R, G, B)} contains the RGB values of each block
