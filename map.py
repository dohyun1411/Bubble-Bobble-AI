import random

import pygame

from config import *


class Brick(pygame.sprite.Sprite):

    def __init__(self, image, x_index, y_index):
        super(Brick, self).__init__()

        self.image = image
        self.x_index = x_index
        self.y_index = y_index

        x = x_index * BrickConfig.size + BrickConfig.size / 2
        y = MapConfig.top_y - y_index * MapConfig.interval
        self.pos = (x, y)
        self.rect = self.image.get_rect(center=self.pos)


class Map:

    group = pygame.sprite.Group()
    
    def __init__(self, brick_image):
        # for floor in range(MapConfig.num_floor):
        for floor in range(3):
            if floor == 0: # bottom
                floor_type = MapConfig.bottom_floor_type
            else:
                # random_index = random.randint(0, len(MapConfig.floor_types) - 1)
                # random_index = 1
                floor_type = MapConfig.floor_types[floor]
                
            for i, char in enumerate(floor_type):
                if char == '_':
                    Map.group.add(Brick(brick_image, i, floor))