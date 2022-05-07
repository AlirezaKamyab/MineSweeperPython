import json

f = open('config.json')
c = json.loads(f.read())
f.close()

WIDTH = c['Width']
HEIGHT = c['Height']
FONT_NAME = c['Font_Name']
SX = c['Sx']
SY = c['Sy']
CELL_WIDTH = c['Cell_Width']
CELL_HEIGHT = c['Cell_Height']
BOMB_COUNT = c['Bomb_Count']
BOMB_COLOR = c['Bomb_Color']
FLAGGED_COLOR = c['Flagged_Color']
HIDDEN_COLOR = c['Hidden_Color']
REVEALED_COLOR = c['Revealed_Color']
WIN_COLOR = c['Win_Color']
LOSE_COLOR = c['Lose_Color']
FOREGROUND = c['Foreground']
BACKGROUND = c['Background']
FONT_SIZE = c['Font_Size']