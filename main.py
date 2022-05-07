import game_manager, consts
from player import Player


def main():
    g = game_manager.GameManager()
    g.add_player(Player('ID', 'Alireza'))
    g.update()


if __name__ == '__main__': main()