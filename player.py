import pygame
import consts, cell, cells

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.score = 0