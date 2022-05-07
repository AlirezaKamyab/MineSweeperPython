import cell, consts
import random
import threading

class Cells:
    def __init__(self, display, bomb_count=consts.BOMB_COUNT,
                 sx=consts.SX, sy=consts.SY, cw=consts.CELL_WIDTH, ch=consts.CELL_HEIGHT):
        self.sx = sx
        self.sy = sy
        self.cw = cw
        self.ch = ch
        self.display = display
        self.bomb_count = bomb_count
        self.cells = []
        self.initialize()


    def initialize(self):
        x0, y0 = 0, 0
        for i in range(self.sx):
            inner = []
            for j in range(self.sy):
                inner.append(cell.Cell(self.display, (x0 + self.cw * i, y0 + self.ch * j), (self.cw, self.ch), 0, (i, j)))
            self.cells.append(inner)
        self.__set_bombs()
        self.__set_numbers()

    
    def draw_all(self):
        for i in self.cells:
            for j in i:
                j.draw()


    def __set_bombs(self):
        rand = random.Random()
        bombs = [x for x in range(1, self.sx * self.sy + 1)]
        while len(bombs) > self.bomb_count:
            safe = rand.randint(0, len(bombs) - 1)
            bombs.pop(safe)

        cnt = 1
        for i in range(self.sx):
            for j in range(self.sy):
                if cnt in bombs: 
                    self.cells[i][j].set_bomb()
                cnt += 1


    def __set_numbers(self):
        H = [-1, 0, 1]
        V = [-1, 0, 1]

        for i in range(self.sx):
            for j in range(self.sy):
                if self.cells[i][j].is_bomb:
                    self.cells[i][j].number = 9
                    continue 

                cnt = 0
                for h in H:
                    if not (0 <= i + h < self.sx): continue
                    for v in V:
                        if h == 0 and v == 0: continue
                        if not (0 <= j + v < self.sy): continue
                        if self.cells[i + h][j + v].is_bomb: cnt += 1
                self.cells[i][j].number = cnt


    def reveal(self, pos):
        H = [-1, 0, 1]
        V = [-1, 0, 1]
        i, j = pos[0], pos[1]

        if self.cells[i][j].state != cell.Cell.HIDDEN and self.cells[i][j].state != cell.Cell.FLAGGED: return
        self.cells[i][j].reveal() 
        if self.cells[i][j].is_bomb: return

        for h in H:
            if not (0 <= i + h < self.sx): continue
            for v in V:
                if h == 0 and v == 0: continue
                if not (0 <= j + v < self.sy): continue

                next = self.cells[i + h][j + v]
                if next.number == 0:
                    t = threading.Thread(target=self.reveal, args=((i + h, j + v), ))
                    t.start()
                    t.join()
                    continue

                if self.cells[i][j].number == 0:
                    next.reveal()
                            

    
    def get_selected_cell(self, pos):
        for i in range(self.sx):
            for j in range(self.sy):
                if self.cells[i][j].is_on_cell(pos): return self.cells[i][j]
        
        return None

    
    def count_flagged(self):
        cnt = 0
        for i in self.cells:
            for j in i:
                if j.state == cell.Cell.FLAGGED: cnt += 1
        
        return cnt


    def count_bomb(self):
        found = 0
        for i in self.cells:
            for j in i:
                if j.is_bomb and (j.state == cell.Cell.FLAGGED or j.state == cell.Cell.BOMB): found += 1
        
        return self.bomb_count, found


    def count_exploded_bombs(self):
        cnt = 0
        for i in self.cells:
            for j in i:
                if j.state == cell.Cell.BOMB: cnt += 1

        return cnt