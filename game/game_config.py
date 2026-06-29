import pygame
from enum import Enum

pygame.init()
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/music.mp3')
pygame.mixer.music.play(loops=-1)

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Цвета
COLORS = {
    'beige': (255, 232, 217),
    'dark_brown': (42, 26, 14),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'red': (147, 41, 41),
    'green': (46, 125, 50),
    'button_brown': (139, 69, 19),
    'dark_beige': (210, 180, 140)
}

class Season(Enum):
    WINTER = "Зима"
    SPRING = "Весна"
    SUMMER = "Лето"
    AUTUMN = "Осень"

class CardType(Enum):
    PRODUCT = "product"
    EVENT = "event"
    NEGATIVE = "negative"

class CardState(Enum):
    BACK = 1
    REVEALED = 2
    INVENTORY = 3

class Window(Enum):
    MENU = 1
    LEVELS = 2
    RULES = 3
    MAIN = 4
    EVENTS = 5
    GAME_OVER = 6
    SELL_REGIONS = 7
    RECIPIENT = 8
    PAUSE = 9

# Позиции карт на поле (x, y)
CARD_POSITIONS = [(65, 177), (372, 177), (683, 177), (986, 177)]

# Позиции для анимации (за экраном справа и слева)
CARD_POSITIONS_OFFSCREEN_RIGHT = [(1500, 177), (1500, 177), (1500, 177), (1500, 177)]
CARD_POSITIONS_OFFSCREEN_LEFT = [(-300, 177), (-300, 177), (-300, 177), (-300, 177)]
# Размеры карт в инвентаре
INVENTORY_CARD_WIDTH = 70
INVENTORY_CARD_HEIGHT = 100
INVENTORY_START_X = 218
INVENTORY_START_Y = 553
INVENTORY_SPACING = 85
MAX_INVENTORY_SIZE = 8
ANIMATION_SPEED = 35