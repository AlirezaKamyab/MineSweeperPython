import pygame
import consts

class Cell:
    HIDDEN, BOMB, FLAGGED, REVEALED = 0, 1, 2, 3
    def __init__(self, surface, pos, size, number, rel_pos=(0, 0), font_size=consts.FONT_SIZE):
        self.pos = pos
        self.size = size
        self.color = consts.HIDDEN_COLOR
        self.surface = surface
        self.number = number
        self.is_bomb = False
        self.state = Cell.HIDDEN
        self.font_size = font_size
        self.rel_pos = rel_pos
        self.draw()

    @property
    def pos(self): 
        return self.__pos
    @property
    def size(self): 
        return self.__size
    @property
    def color(self): 
        return self.__color
    @property
    def number(self):
        return self.__number
    @property
    def font_size(self):
        return self.__font_size
    @property
    def state(self):
        return self.__state

    @pos.setter
    def pos(self, value): 
        self.__pos = value
    @size.setter
    def size(self, value): 
        self.__size = value
    @color.setter
    def color(self, value): 
        self.__color = value
    @number.setter
    def number(self, value):
        self.__number = value
    @font_size.setter
    def font_size(self, value):
        self.__font_size = value

    @state.setter
    def state(self, value):
        if value == Cell.HIDDEN:
            self.color = consts.HIDDEN_COLOR
        elif value == Cell.BOMB:
            self.color = consts.BOMB_COLOR
        elif value == Cell.FLAGGED:
            self.color = consts.FLAGGED_COLOR
        elif value == Cell.REVEALED:
            self.color = consts.REVEALED_COLOR
        else:
            self.__state = Cell.HIDDEN
            self.color = consts.HIDDEN_COLOR
            return 

        self.__state = value

    
    def set_bomb(self):
        self.is_bomb = True

    
    def is_on_cell(self, pos):
        if (self.pos[0] < pos[0] < (self.pos[0] + self.size[0])) and (self.pos[1] < pos[1] < (self.pos[1] + self.size[1])):
            return True
        else: return False


    def reveal(self):
        if self.state != Cell.HIDDEN: return
        if self.is_bomb:
            self.state = Cell.BOMB
        else:
            self.state = Cell.REVEALED


    def toggle_flag(self):
        if self.state == Cell.FLAGGED: self.state = Cell.HIDDEN
        elif self.state == Cell.HIDDEN: 
            self.state = Cell.FLAGGED
        else: return None


    def draw(self):
        pygame.draw.rect(self.surface, self.color, (self.pos, self.size), 0)
        pygame.draw.rect(self.surface, consts.FOREGROUND, (self.pos, self.size), 1)

        if self.state != Cell.REVEALED or self.number == 0: return

        __txtobj = pygame.font.SysFont(consts.FONT_NAME, self.font_size, True)
        txt = __txtobj.render(str(self.number), 1, consts.FOREGROUND)
        self.surface.blit(txt, (self.pos[0] + self.size[0] / 2 - txt.get_width() / 2, self.pos[1] + self.size[1] / 2 - txt.get_height() / 2))
