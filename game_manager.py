from distutils.command.config import config
import random
import cell, cells, consts, player, network, json, socket
import pygame
import threading

class GameManager:
    def __init__(self, host=None, gametype=3, caption='Mine Sweeper', fps=60):
        pygame.init()
        pygame.font.init()
        self.__game_over = False
        self.fps = fps
        self.display = pygame.display.set_mode((consts.WIDTH, consts.HEIGHT))
        pygame.display.set_caption(caption)

        ran = random.Random()
        self.players = [player.Player(ran.randint(0, 1000000000), consts.NAME)]
        self.host = host
        self.gametype = gametype

        self.__recved_config_file = False
        self.__recved_cells = False

        if gametype == 1:
            self.cells = cells.Cells(self.display)
            self.__recved_config_file = True
            self.__recved_cells = True
            self.host.start()
            threading.Thread(target=self.accept_players).start()
        elif gametype == 2:
            self.host.connect()
            threading.Thread(target=self.process_requests, args=(self.host.socket, )).start()
            self.host.send('Request Config file', 0)
        else:
            self.__recved_config_file = True
            self.__recved_cells = True
            self.cells = cells.Cells(self.display)
        
    
    def update(self):
        clock = pygame.time.Clock()
        while True:
            clock.tick(self.fps)
            self.display.fill(consts.BACKGROUND)
            self.listen()

            if not self.__recved_cells or not self.__recved_config_file: continue

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
                if not c or c.state == cell.Cell.REVEALED: continue
                if c and event.button == 1 and c.state == cell.Cell.HIDDEN: 
                    self.cells.reveal(c.rel_pos)
                    if c.is_bomb:
                            self.players[0].score -= consts.BOMB
                    else: self.players[0].score += consts.SAFE
                    
                    if self.gametype == 2: self.host.send([c.rel_pos, 0], 4)
                    else: self.host.sendall([c.rel_pos, 0], 4)


                if c and event.button == 3: 
                    if c.state != cell.Cell.FLAGGED: 
                        c.toggle_flag()
                        if not c.is_bomb:
                            self.players[0].score -= consts.FLAG
                            self.cells.reveal(c.rel_pos)
                        else: self.players[0].score += consts.FLAG

                        if self.gametype == 2: self.host.send([c.rel_pos, 1], 4)
                        else: self.host.sendall([c.rel_pos, 1], 4)

                if self.gametype == 2: self.host.send(self.dic_players(), 3)
                    

    def check_win(self):
        bombs, found = self.cells.count_bomb()

        if found != bombs: return

        font = pygame.font.SysFont(consts.FONT_NAME, consts.FONT_SIZE * 5, True)
        scores = [self.players[x].score for x in range(0, len(self.players))]
        winner_score = max(scores) if len(scores) > 0 else 0

        if self.players[0].score != winner_score:
            self.display.fill(consts.BACKGROUND)
            self.__game_over = True
            txt = font.render('YOU LOST!', 1, consts.LOSE_COLOR)
            self.display.blit(txt, (consts.WIDTH/2 - txt.get_width()/2, consts.HEIGHT/2 - txt.get_height()/2))
            self.draw_scores((consts.WIDTH/2 + 5, consts.HEIGHT/2 + txt.get_height()/2), consts.FOREGROUND)
        else:
            self.display.fill(consts.BACKGROUND)
            self.__game_over = True
            txt = font.render('YOU WON!', 1, consts.WIN_COLOR)
            self.display.blit(txt, (consts.WIDTH/2 - txt.get_width()/2, consts.HEIGHT/2 - txt.get_height()/2))
            self.draw_scores((consts.WIDTH/2 + 5, consts.HEIGHT/2 + txt.get_height()/2), consts.FOREGROUND)

        pygame.display.update()


    def draw_score_board(self):
        bombs, found = self.cells.count_bomb()
        font = pygame.font.SysFont(consts.FONT_NAME, consts.FONT_SIZE)
        txt = font.render(f'Bombs remaining {bombs - found}', 1, consts.FOREGROUND)
        self.display.blit(txt, (consts.WIDTH - txt.get_width() - 10, 10))
        self.draw_scores((consts.WIDTH - 10, 10 + txt.get_height() + 10), consts.FOREGROUND, True, consts.FONT_SIZE)

    
    def draw_scores(self, pos, color, corner = False, font_size = consts.FONT_SIZE * 2):
        font = pygame.font.SysFont(consts.FONT_NAME, font_size)
        add = 0
        
        for player in self.players:
            txt = font.render(f'{player.name} Score : {player.score}', 1, color)
            if not corner: self.display.blit(txt, (pos[0] - txt.get_width()/2, pos[1] + add))
            else: self.display.blit(txt, (pos[0] - txt.get_width(), pos[1] + add))
            add += txt.get_height()


    def accept_players(self):
        while True:
            try:
                p, a = self.host.socket.accept()
                self.host.connections.append(p)
                threading.Thread(target=self.process_requests, args=(p,)).start()
            except:
                break

    
    def process_requests(self, client:socket.socket):
        while True:
            try:
                data = client.recv(self.host.buffer_size)
                data = str(data, encoding='utf-8')
                if len(data) == 0: continue
                size_of_data = len(data)
                data = json.loads(data)
                print(f"Code {data['code']}, {size_of_data} Bytes recieved!")


                if data['code'] == 0: # Sending config file
                    file = open('config.json')
                    network.Network.sendwith(client, file.read(), 5)
                    file.close()
                    

                elif data['code'] == 1: # Sending cells
                    dic_cells = []
                    for i in self.cells.cells:
                        inner = []
                        for j in i:
                            inner.append({'state':j.state, 'number':j.number, 'is_bomb':j.is_bomb, 'pos':j.pos, 
                                                'rel_pos':j.rel_pos, 'size':j.size})
                        dic_cells.append(inner)
                        
                    network.Network.sendwith(client, dic_cells, 6)


                elif data['code'] == 2: # Sending players
                    network.Network.sendwith(client, self.dic_players(), 3)


                elif data['code'] == 3: # Recieve Players
                    if not self.__recved_cells or not self.__recved_config_file: continue
                    lst = data['data']
                    for p in lst:
                        if self.players[0].id == p['id']: continue
                        for mp in self.players:
                            if mp.id == p['id']: 
                                mp.score = p['score']
                                break
                        else:
                            newp = player.Player(p['id'], p['name'])
                            newp.score = p['score']
                            self.players.append(newp)


                elif data['code'] == 4: # Recieve New Action
                    if not self.__recved_cells or not self.__recved_config_file: continue
                    lst = data['data']
                    pos = lst[0]
                    rtype = lst[1]
                    c = self.cells.cells[pos[0]][pos[1]]
                    if rtype == 0: 
                        self.cells.reveal(pos)

                    if rtype == 1: 
                        if c.state != cell.Cell.FLAGGED: 
                            c.toggle_flag()
                            if not c.is_bomb:
                                self.cells.reveal(c.rel_pos)

                    if self.gametype == 1: 
                        client.send('Request players', 2)
                        self.host.sendall(self.dic_players(), 3)
                    else: self.host.send('Request players', 2)


                elif data['code'] == 5: # Receive Config file
                    config_data = data['data']
                    config_data = json.loads(config_data)
                    consts.WIDTH = config_data['Width']
                    consts.HEIGHT = config_data['Height']
                    consts.BOMB_COUNT = config_data['Bomb_Count']
                    consts.CELL_WIDTH = config_data['Cell_Width']
                    consts.CELL_HEIGHT = config_data['Cell_Height']
                    consts.BOMB = config_data['Bomb']
                    consts.SAFE = config_data['Safe']
                    consts.FLAG = config_data['Flag']
                    consts.SX = config_data['Sx']
                    consts.SY = config_data['Sy']
                    config_data['Name'] = consts.NAME

                    file = open('config.json', 'w')
                    file.write(json.dumps(config_data))
                    file.close()
                    self.__recved_config_file = True
                    self.cells = cells.Cells(self.display)
                    self.host.send('Request Cells', 1)


                elif data['code'] == 6: # Receive Cells
                    cell_data = data['data']
                    for i in cell_data:
                        for j in i:
                            x, y = j['rel_pos']
                            self.cells.cells[x][y].state = j['state']
                            self.cells.cells[x][y].is_bomb = j['is_bomb']
                            self.cells.cells[x][y].number = j['number']
                            self.cells.cells[x][y].pos = j['pos']
                            self.cells.cells[x][y].rel_pos = j['rel_pos']
                            self.cells.cells[x][y].size = j['size']

                    self.__recved_cells = True
                    self.host.send('Request Cells', 2)
                    self.host.send(self.dic_players(), 3)


                data['code'] = -1

            except ConnectionError as ex:
                print(f"Player {client.getsockname()} disconnected!")
                return
            except TypeError as ex:
                print(ex, type(ex))
                continue


    def dic_players(self):
        dic_players = []
        for i in range(len(self.players)):
            dic_players.append({'name':self.players[i].name, 'id':self.players[i].id, 'score':self.players[i].score})
        return dic_players

