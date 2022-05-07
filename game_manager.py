import cell, cells, consts, player
import pygame
import threading

class GameManager:
    def __init__(self, caption='Mine Sweeper', fps=60):
        pygame.init()
        pygame.font.init()
        self.__game_over = False
        self.fps = fps
        self.display = pygame.display.set_mode((consts.WIDTH, consts.HEIGHT))
        pygame.display.set_caption(caption)

        self.cells = cells.Cells(self.display)

        self.players = [player.Player('ID', consts.NAME)]
        
    
    def update(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(self.fps)
            self.display.fill(consts.BACKGROUND)
            self.listen()

            t = threading.Thread(target=self.cells.draw_all)
            t.start()
            t.join()

            t = threading.Thread(target=self.draw_score_board)
            t.start()
            t.join()

            # Should be last
            t = threading.Thread(target=self.check_win)
            t.start()
            t.join()

            if not self.__game_over:
                pygame.display.update()

    
    def add_player(self, player): 
        self.players.append(player)
        print(len(self.players))


    
    def listen(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.__game_over = True
                return

            if self.__game_over: continue
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                c = self.cells.get_selected_cell(pos)
                if c and event.button == 1: 
                    self.cells.reveal(c.rel_pos)
                    if c.is_bomb:
                            self.players[0].score -= consts.BOMB
                    else: self.players[0].score += consts.SAFE

                if c and event.button == 3: 
                    if c.state != cell.Cell.FLAGGED: 
                        c.toggle_flag()
                        if not c.is_bomb:
                            self.players[0].score -= consts.FLAG
                            self.cells.reveal(c.rel_pos)
                        else: self.players[0].score += consts.FLAG
                    


    def check_win(self):
        bombs, found = self.cells.count_bomb()
        exploded = self.cells.count_exploded_bombs()

        font = pygame.font.SysFont(consts.FONT_NAME, consts.FONT_SIZE * 5, True)

        if False:
            self.display.fill(consts.BACKGROUND)
            self.__game_over = True
            txt = font.render('YOU LOST!', 1, consts.LOSE_COLOR)
            self.display.blit(txt, (consts.WIDTH/2 - txt.get_width()/2, consts.HEIGHT/2 - txt.get_height()/2))
        elif bombs == found:
            self.display.fill(consts.BACKGROUND)
            self.__game_over = True
            if self.players[0].score > 0: txt = font.render('YOU WON!', 1, consts.WIN_COLOR)
            else: txt = font.render('YOU LOST!', 1, consts.LOSE_COLOR)
            self.display.blit(txt, (consts.WIDTH/2 - txt.get_width()/2, consts.HEIGHT/2 - txt.get_height()/2))
            self.draw_scores((consts.WIDTH/2 + 5, consts.HEIGHT/2 + txt.get_height()/2), consts.FOREGROUND)
        else: self.__game_over = False

        pygame.display.update()


    def draw_score_board(self):
        flagged = self.cells.count_flagged()
        bombs, _ = self.cells.count_bomb()
        font = pygame.font.SysFont(consts.FONT_NAME, consts.FONT_SIZE)
        txt = font.render(f'Bombs remaining {bombs - flagged}', 1, consts.FOREGROUND)
        self.display.blit(txt, (consts.WIDTH - txt.get_width() - 10, 10))

    
    def draw_scores(self, pos, color):
        font = pygame.font.SysFont(consts.FONT_NAME, 3 * consts.FONT_SIZE // 2, True)
        add = 0
        
        for player in self.players:
            txt = font.render(f'{player.name} Score : {player.score}', 1, color)
            self.display.blit(txt, (pos[0] - txt.get_width()/2, pos[1] + add))
            add += txt.get_height() + txt.get_height() // 2