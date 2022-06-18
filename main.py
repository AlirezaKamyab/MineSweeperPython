import game_manager, network, json, consts

def main():
    print('1- Host a game\n2- Connect to a game\n3- Single player\n4- Quit')
    r = input(">> ")

    if r == '1':
        host = network.Network(consts.IP, consts.PORT)
        g = game_manager.GameManager(host, 1)
        g.update()

    elif r == '2':
        host = network.Network(consts.IP, consts.PORT)
        g = game_manager.GameManager(host, 2)
        g.update()

    elif r == '3':
        g = game_manager.GameManager()
        g.update()
    else:
        pass


if __name__ == '__main__': main()