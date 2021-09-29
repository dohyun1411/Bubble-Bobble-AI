import pygame

from config import *


class Boom(pygame.sprite.Sprite):

    group = pygame.sprite.Group()

    def __init__(self, image, pos, i):
        super(Boom, self).__init__()
        self.i = i
        self.image = image
        self.pos = pos
        self.rect = image.get_rect(center=pos)
        self.boom_delay = 0
        Boom.group.add(self)
    
    def act(self):
        self.boom_delay += 1
        if self.boom_delay > BoomConfig.delay:
            Boom.group.remove(self)