import pygame
import random
from enum import Enum

# Инициализация Pygame
pygame.init()
pygame.font.init()

# Proverka

# Константы
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Цвета
COLORS = {
    'background': (255, 232, 217),
    'dark_brown': (42, 26, 14),
    'brown': (78, 36, 4),
    'light_brown': (153, 88, 42),
    'beige': (254, 250, 224),
    'dark_beige': (211, 190, 160),
    'button_brown': (170, 122, 101),
    'white': (255, 255, 255),
    'black': (28, 28, 28),
    'red': (147, 41, 41),
    'green': (60, 120, 60),
}

# Сезоны
class Season(Enum):
    WINTER = "Зима"
    SPRING = "Весна"
    SUMMER = "Лето"
    AUTUMN = "Осень"

# Типы карт
class CardType(Enum):
    PRODUCT = "product"
    EVENT = "event"
    NEGATIVE = "negative"

# Состояния карты
class CardState(Enum):
    BACK = 1
    REVEALED = 2
    INVENTORY = 3

# Окна
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

# Структуры данных
class ButtonData:
    def __init__(self, x, y, width, height, text, color, text_color, action, data=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.text_color = text_color
        self.action = action
        self.data = data

class CardData:
    def __init__(self, name, card_type, state, x, y, width=240, height=360,
                 buy_price=0, sell_price=0, base_buy=0, base_sell=0,
                 description="", effect_duration=0, effects=None, risk_mod=0):
        self.name = name
        self.card_type = card_type
        self.state = state
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.buy_price = buy_price
        self.sell_price = sell_price
        self.base_buy = base_buy
        self.base_sell = base_sell
        self.description = description
        self.effect_duration = effect_duration
        self.effects = effects if effects is not None else {}
        self.risk_mod = risk_mod
        self.target_x = x
        self.velocity_x = 0

class RecipientData:
    def __init__(self, name, region, distance, x, y, width=200, height=300):
        self.name = name
        self.region = region
        self.distance = distance
        self.x = x
        self.y = y
        self.width = width
        self.height = height

# Товары
PRODUCTS = {
    "Пшеница": {"buy": 8, "sell": 5, "season_effects": {"Лето": 90, "Зима": 80}, 
                "desc": "Самая распространенная культура в королевстве!"},
    "Рыба": {"buy": 12, "sell": 8, "season_effects": {"Осень": 40, "Весна": 70},
             "desc": "Рыболовный промысел во все времена кормил жителей юга!"},
    "Уголь": {"buy": 10, "sell": 6, "season_effects": {"Зима": 150, "Лето": -30},
              "desc": "Лучший источник тепла и энергии!"},
    "Шерсть": {"buy": 15, "sell": 10, "season_effects": {"Зима": 140, "Весна": -10},
               "desc": "Теплое шерстяное одеяло сможет согреть даже самой суровой зимой!"},
    "Железо": {"buy": 20, "sell": 14, "season_effects": {"Осень": 50, "Лето": -10},
               "desc": "Основа прогресса, найдет свое место во всех уголках страны!"},
    "Вино": {"buy": 25, "sell": 18, "season_effects": {"Осень": 50, "Зима": 70},
             "desc": "Никто не откажется от бокала вина на праздничном столе!"},
    "Лекарства": {"buy": 30, "sell": 22, "season_effects": {"Весна": 40, "Зима": 140},
                  "desc": "Крайне редки и сложны в изготовлении!"},
    "Меха": {"buy": 35, "sell": 25, "season_effects": {"Зима": 160, "Лето": -50},
             "desc": "Ни одна зима на севере не обходится без теплой меховой одежды!"},
    "Специи": {"buy": 40, "sell": 30, "season_effects": {"Осень": 50, "Зима": 70},
               "desc": "Вкусная еда требует много разных специй!"},
    "Драгоценные камни": {"buy": 80, "sell": 60, "season_effects": {},
                          "desc": "Символ богатства и высокого статуса!"}
}

# События
EVENTS = {
    "Война": {"duration": 8, "effects": {"Уголь": 200, "Железо": 200, "Шерсть": 200, 
                                          "Вино": -20, "Лекарства": 300, "Меха": 140,
                                          "Специи": -20, "Драгоценные камни": -30},
              "risk_mod": 20, "desc": "На границе страны вспыхнула война!"},
    "Эпидемия": {"duration": 10, "effects": {"Лекарства": 550, "Рыба": 50},
                 "risk_mod": 30, "desc": "Чума бушует на улицах королевства, будьте осторожны!"},
    "Сухой закон": {"duration": 7, "effects": {"Вино": -40},
                    "risk_mod": 0, "desc": "Король изъявил сегодня же запретить вино во всей стране!"},
    "Праздник": {"duration": 4, "effects": {"Драгоценные камни": 300, "Специи": 300, "Вино": 300},
                 "risk_mod": 0, "desc": "Возрадуйтесь, сегодня праздник!"},
    "Шахтёрская забастовка": {"duration": 4, "effects": {"Уголь": 300, "Железо": 320},
                              "risk_mod": 0, "desc": "Низкие потолки в шахтах и плохой воздух вынудили рабочих взбунтоваться!"}
}

# Негативные эффекты
NEGATIVE_EVENTS = {
    "Разбойники": {"desc": "В этот раз покупатели не дождутся своих товаров!", "duration": 1},
    "Неудачное вложение": {"desc": "В следующий раз стоит аккуратнее вкладывать своё золото!", "duration": 1}
}

# Регионы
REGIONS = {
    "Горный": {"effects": {"Пшеница": 50, "Рыба": 50, "Уголь": -20, "Железо": -10,
                           "Вино": 50, "Лекарства": 70, "Специи": 90, "Драгоценные камни": -10}},
    "Приморье": {"effects": {"Пшеница": 30, "Рыба": -10, "Уголь": 50, "Железо": 50,
                             "Вино": -10, "Специи": 40, "Драгоценные камни": 60}},
    "Тайга": {"effects": {"Пшеница": 40, "Уголь": 60, "Железо": 40, "Вино": 50,
                          "Лекарства": -10, "Специи": 50, "Драгоценные камни": -10}},
    "Степь": {"effects": {}}
}

# Позиции карт
CARD_POSITIONS = [(65, 177), (372, 177), (683, 177), (986, 177)]
CARD_POSITIONS_OFFSCREEN_LEFT = [(-245, 177), (-245, 177), (-245, 177), (-245, 177)]
CARD_POSITIONS_OFFSCREEN_RIGHT = [(SCREEN_WIDTH + 245, 177), (SCREEN_WIDTH + 245, 177), 
                                   (SCREEN_WIDTH + 245, 177), (SCREEN_WIDTH + 245, 177)]

# Глобальные переменные
screen = None
clock = None
running = True
font_big = None
font_medium = None
font_small = None

current_window = Window.MENU
lvl = 1
is_pro = True
balance = 300
target_sum = 1000
step = 1
season = Season.SUMMER
has_revealed_card_this_turn = False  # Флаг: открывал ли игрок карту в этом ходу
waiting_for_action = False  # Ждём действие после открытия карты
current_open_card_index = -1  # Индекс открытой карты

last_bought_card = None # Последняя купленная карта

field_cards = []
new_field_cards = []
inventory = []
sent_products = []
active_events = []

selected_product = None
selected_recipient = None
selected_card_index = None

buttons = {}
close_button = None
skip_turn_button = None
rules_back_button = None
region_buttons = []
recipient_buttons = []
game_over_buttons = []

current_prices = {}

# Анимация
is_animating = False
animation_progress = 0
animation_speed = 15

# Расчет цены покупки товара с учетом действующих событий и текущего времени года
def calculate_buy_price(product_name):
    global season, active_events
    base_price = PRODUCTS[product_name]['buy']
    modifier = 1.0
    
    season_effects = PRODUCTS[product_name].get('season_effects', {})
    if season.value in season_effects:
        modifier += season_effects[season.value] / 100
    
    for event in active_events:
        if product_name in event.get('effects', {}):
            modifier += event['effects'][product_name] / 100
    
    price = base_price * modifier
    return max(base_price * 0.2, min(base_price * 2.5, price))

# Расчет цены продажи товара с учетом действующих событий, времени года и региона
def calculate_sell_price(product_name, region=None):
    global season, active_events
    base_price = PRODUCTS[product_name]['sell']
    modifier = 1.0
    
    season_effects = PRODUCTS[product_name].get('season_effects', {})
    if season.value in season_effects:
        modifier += season_effects[season.value] / 100
    
    for event in active_events:
        if product_name in event.get('effects', {}):
            modifier += event['effects'][product_name] / 100
    
    if region and region in REGIONS:
        region_effects = REGIONS[region].get('effects', {})
        if product_name in region_effects:
            modifier += region_effects[product_name] / 100
    
    price = base_price * modifier
    return max(base_price, min(base_price * 4, price))

# Функция, обновляющая цены
def update_prices():
    global current_prices, inventory, field_cards
    
    for product_name in PRODUCTS:
        current_prices[product_name] = {
            'buy': calculate_buy_price(product_name),
            'sell': calculate_sell_price(product_name)
        }
    
    for card in inventory:
        if card.card_type == CardType.PRODUCT:
            card.buy_price = calculate_buy_price(card.name)
            card.sell_price = calculate_sell_price(card.name)
    
    for card in field_cards:
        if card.card_type == CardType.PRODUCT and card.state != CardState.BACK:
            card.buy_price = calculate_buy_price(card.name)
            card.sell_price = calculate_sell_price(card.name)


def generate_random_card():
    rand = random.random()
    
    if rand < 0.7:
        product_name = random.choice(list(PRODUCTS.keys()))
        product = PRODUCTS[product_name]
        return {
            'name': product_name,
            'type': CardType.PRODUCT,
            'buy': calculate_buy_price(product_name),
            'sell': calculate_sell_price(product_name),
            'base_buy': product['buy'],
            'base_sell': product['sell'],
            'desc': product['desc']
        }
    elif rand < 0.9:
        event_name = random.choice(list(EVENTS.keys()))
        event = EVENTS[event_name]
        return {
            'name': event_name,
            'type': CardType.EVENT,
            'desc': event['desc'],
            'duration': event['duration'],
            'effects': event['effects'],
            'risk_mod': event['risk_mod']
        }
    else:
        if (lvl == 1):
            if last_bought_card == None:
                product_name = random.choice(list(PRODUCTS.keys()))
                product = PRODUCTS[product_name]
                return {
                    'name': product_name,
                    'type': CardType.PRODUCT,
                    'buy': calculate_buy_price(product_name),
                    'sell': calculate_sell_price(product_name),
                    'base_buy': product['buy'],
                    'base_sell': product['sell'],
                    'desc': product['desc']
                }
            neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))
            while neg_name == "Разбойники": neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))                
            neg = NEGATIVE_EVENTS[neg_name]
        else:
            neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))
            while last_bought_card == None and neg_name == "Неудачное вложение": neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))
            neg = NEGATIVE_EVENTS[neg_name]
        return {
            'name': neg_name,
            'type': CardType.NEGATIVE,
            'desc': neg['desc'],
            'duration': neg['duration']
        }


def init_field_cards():
    global field_cards
    field_cards = []
    
    for x, y in CARD_POSITIONS:
        card_data = generate_random_card()
        card = CardData(
            name=card_data['name'],
            card_type=card_data['type'],
            state=CardState.BACK,
            x=x, y=y,
            buy_price=card_data.get('buy', 0),
            sell_price=card_data.get('sell', 0),
            base_buy=card_data.get('base_buy', 0),
            base_sell=card_data.get('base_sell', 0),
            description=card_data.get('desc', ''),
            effect_duration=card_data.get('duration', 0),
            effects=card_data.get('effects', {}),
            risk_mod=card_data.get('risk_mod', 0)
        )
        card.target_x=x
        card.velocity_x=0
        field_cards.append(card)


def init_new_field_cards():
    global new_field_cards
    new_field_cards = []
    
    for i, (x, y) in enumerate(CARD_POSITIONS_OFFSCREEN_LEFT):
        card_data = generate_random_card()
        card = CardData(
            name=card_data['name'],
            card_type=card_data['type'],
            state=CardState.BACK,
            x=x, y=y,
            buy_price=card_data.get('buy', 0),
            sell_price=card_data.get('sell', 0),
            base_buy=card_data.get('base_buy', 0),
            base_sell=card_data.get('base_sell', 0),
            description=card_data.get('desc', ''),
            effect_duration=card_data.get('duration', 0),
            effects=card_data.get('effects', {}),
            risk_mod=card_data.get('risk_mod', 0)
        )
        card.target_x=CARD_POSITIONS[i][0]
        card.velocity_x=0
        new_field_cards.append(card)


def start_animation():
    global is_animating, animation_progress, field_cards, new_field_cards
    
    is_animating = True
    animation_progress = 0
    
    for i, card in enumerate(field_cards):
        card.target_x = CARD_POSITIONS_OFFSCREEN_RIGHT[i][0]
        card.velocity_x = animation_speed
    
    init_new_field_cards()
    
    for card in new_field_cards:
        card.velocity_x = animation_speed


def update_animation():
    global is_animating, animation_progress, field_cards, new_field_cards
    
    if not is_animating:
        return
    
    animation_progress += 1
    all_complete = True
    
    for card in field_cards:
        if abs(card.x - card.target_x) > card.velocity_x:
            if card.x < card.target_x:
                card.x += card.velocity_x
            else:
                card.x -= card.velocity_x
            all_complete = False
        else:
            card.x = card.target_x
    
    for card in new_field_cards:
        if abs(card.x - card.target_x) > card.velocity_x:
            if card.x < card.target_x:
                card.x += card.velocity_x
            else:
                card.x -= card.velocity_x
            all_complete = False
        else:
            card.x = card.target_x
    
    if all_complete:
        field_cards = new_field_cards
        new_field_cards = []
        is_animating = False


def init_buttons():
    global buttons, close_button, skip_turn_button, rules_back_button
    
    buttons = {
        Window.MENU: [
            ButtonData(490, 280, 300, 83, "Играть", COLORS['brown'], COLORS['beige'], "play"),
            ButtonData(490, 377, 300, 83, "Правила", COLORS['brown'], COLORS['beige'], "rules"),
            ButtonData(490, 474, 300, 83, "Выйти", COLORS['brown'], COLORS['beige'], "exit")
        ],
        Window.LEVELS: [
            ButtonData(345, 232, 295, 85, "1 уровень", COLORS['dark_brown'], COLORS['beige'], "level1"),
            ButtonData(660, 232, 295, 85, "2 уровень", COLORS['dark_brown'], COLORS['beige'], "level2"),
            ButtonData(500, 340, 300, 83, "Назад", COLORS['dark_brown'], COLORS['beige'], "back")
        ],
        Window.PAUSE: [
            ButtonData(490, 280, 300, 85, "Продолжить", COLORS['button_brown'], COLORS['black'], "resume"),
            ButtonData(490, 377, 300, 85, "Правила", COLORS['button_brown'], COLORS['black'], "rules"),
            ButtonData(490, 474, 300, 85, "Выйти", COLORS['button_brown'], COLORS['black'], "exit")
        ]
    }
    
    close_button = ButtonData(1200, 35, 40, 40, "X", COLORS['white'], COLORS['dark_brown'], "close")
    skip_turn_button = ButtonData(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 130, 50,
                                   "Пропустить ход", COLORS['button_brown'], COLORS['black'], "skip_turn")
    rules_back_button = ButtonData(50, 650, 150, 50, "Назад", COLORS['button_brown'], COLORS['black'], "back")


def draw_button(button):
    pygame.draw.rect(screen, button.color, (button.x, button.y, button.width, button.height))
    pygame.draw.rect(screen, COLORS['dark_brown'], (button.x, button.y, button.width, button.height), 2)
    text_surface = font_medium.render(button.text, True, button.text_color)
    text_rect = text_surface.get_rect(center=(button.x + button.width//2, button.y + button.height//2))
    screen.blit(text_surface, text_rect)


def draw_card(card, show_price=True, is_open_card=False):
    if card.state == CardState.BACK:
        pygame.draw.rect(screen, COLORS['brown'], (card.x, card.y, card.width, card.height))
        pygame.draw.rect(screen, COLORS['beige'], (card.x + 5, card.y + 5, card.width - 10, card.height - 10))
        center_x = card.x + card.width // 2
        center_y = card.y + card.height // 2
        pygame.draw.circle(screen, COLORS['brown'], (center_x, center_y), 40)
        pygame.draw.circle(screen, COLORS['beige'], (center_x, center_y), 30)
        question = font_medium.render("?", True, COLORS['brown'])
        question_rect = question.get_rect(center=(center_x, center_y))
        screen.blit(question, question_rect)
    else:
        pygame.draw.rect(screen, COLORS['beige'], (card.x, card.y, card.width, card.height))
        pygame.draw.rect(screen, COLORS['dark_brown'], (card.x, card.y, card.width, card.height), 3)
        
        img_rect = pygame.Rect(card.x + 10, card.y + 10, card.width - 20, 160)
        pygame.draw.rect(screen, COLORS['white'], img_rect)
        pygame.draw.rect(screen, COLORS['dark_brown'], img_rect, 2)
        
        name_surface = font_medium.render(card.name, True, COLORS['dark_brown'])
        name_rect = name_surface.get_rect(center=(card.x + card.width//2, card.y + 190))
        screen.blit(name_surface, name_rect)
        
        if show_price and card.card_type == CardType.PRODUCT and card.state == CardState.REVEALED:
            price_text = f"Цена: {int(card.buy_price)}"
            price_color = COLORS['brown']
            price_surface = font_small.render(price_text, True, price_color)
            price_rect = price_surface.get_rect(center=(card.x + card.width//2, card.y + 220))
            screen.blit(price_surface, price_rect)
            
            # Кнопка "Купить"
            pygame.draw.rect(screen, COLORS['button_brown'], (card.x + 16, card.y + 290, 95, 38))
            pygame.draw.rect(screen, COLORS['dark_brown'], (card.x + 16, card.y + 290, 95, 38), 2)
            buy_text = font_small.render("Купить", True, COLORS['beige'])
            buy_rect = buy_text.get_rect(center=(card.x + 16 + 47, card.y + 309))
            screen.blit(buy_text, buy_rect)
            
            # Кнопка "Отказаться"
            pygame.draw.rect(screen, COLORS['red'], (card.x + 129, card.y + 290, 95, 38))
            pygame.draw.rect(screen, COLORS['dark_brown'], (card.x + 129, card.y + 290, 95, 38), 2)
            skip_text = font_small.render("Отказ", True, COLORS['beige'])
            skip_rect = skip_text.get_rect(center=(card.x + 129 + 47, card.y + 309))
            screen.blit(skip_text, skip_rect)
            
        elif card.card_type != CardType.PRODUCT and card.state == CardState.REVEALED:
            desc_lines = card.description.split('\n')
            for i, line in enumerate(desc_lines[:2]):
                desc_surface = font_small.render(line[:25], True, COLORS['black'])
                screen.blit(desc_surface, (card.x + 15, card.y + 220 + i * 25))
            
            # Кнопка "Принять" для событий
            pygame.draw.rect(screen, COLORS['button_brown'], (card.x + 16, card.y + 307, 208, 38))
            pygame.draw.rect(screen, COLORS['dark_brown'], (card.x + 16, card.y + 307, 208, 38), 2)
            action_text = font_small.render("Принять", True, COLORS['beige'])
            action_rect = action_text.get_rect(center=(card.x + card.width//2, card.y + 326))
            screen.blit(action_text, action_rect)
        
        elif show_price and card.card_type == CardType.PRODUCT and card.state == CardState.INVENTORY:
            price_text = f"Цена: {int(card.sell_price)}"
            price_color = COLORS['green']
            price_surface = font_small.render(price_text, True, price_color)
            price_rect = price_surface.get_rect(center=(card.x + card.width//2, card.y + 220))
            screen.blit(price_surface, price_rect)


def draw_recipient(recip):
    pygame.draw.rect(screen, COLORS['beige'], (recip.x, recip.y, recip.width, recip.height))
    pygame.draw.rect(screen, COLORS['dark_brown'], (recip.x, recip.y, recip.width, recip.height), 2)
    
    img_rect = pygame.Rect(recip.x + 25, recip.y + 20, recip.width - 50, 100)
    pygame.draw.rect(screen, COLORS['white'], img_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], img_rect, 1)
    
    name_surface = font_medium.render(recip.name, True, COLORS['dark_brown'])
    name_rect = name_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 150))
    screen.blit(name_surface, name_rect)
    
    info_surface = font_small.render(f"Доставка: {recip.distance} ходов", True, COLORS['black'])
    info_rect = info_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 200))
    screen.blit(info_surface, info_rect)
    
    risk = min(0.95, 0.05 + recip.distance * 0.03)
    risk_surface = font_small.render(f"Риск: {int(risk * 100)}%", True, COLORS['red'])
    risk_rect = risk_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 230))
    screen.blit(risk_surface, risk_rect)


def is_hovered(button, pos):
    return button.x <= pos[0] <= button.x + button.width and button.y <= pos[1] <= button.y + button.height


def handle_button_action(action, data=None):
    global current_window, lvl, target_sum, balance, step, season, inventory
    global sent_products, active_events, last_bought_card
    global selected_product, selected_recipient, selected_card_index
    global is_pro, running, field_cards, is_animating
    global has_revealed_card_this_turn, waiting_for_action, current_open_card_index
    
    if action == "play":
        current_window = Window.LEVELS
    elif action == "rules":
        current_window = Window.RULES
    elif action == "exit":
        running = False
    elif action == "level1":
        lvl = 1
        target_sum = 1000
        restart_game()
        current_window = Window.MAIN
        init_field_cards()
    elif action == "level2":
        if is_pro:
            lvl = 2
            target_sum = 1500
            restart_game()
            current_window = Window.MAIN
            init_field_cards()
    elif action == "back":
        if current_window == Window.LEVELS:
            current_window = Window.MENU
        elif current_window == Window.RULES:
            current_window = Window.MENU
        elif current_window == Window.PAUSE:
            current_window = Window.MAIN
        elif current_window == Window.SELL_REGIONS:
            current_window = Window.MAIN
    elif action == "pause":
        current_window = Window.PAUSE
    elif action == "resume":
        current_window = Window.MAIN
    elif action == "close":
        if current_window == Window.RULES:
            current_window = Window.MENU
        elif current_window == Window.EVENTS:
            current_window = Window.MAIN
        elif current_window == Window.SELL_REGIONS:
            current_window = Window.MAIN
    elif action == "menu":
        restart_game()
        current_window = Window.MENU
    elif action == "restart":
        restart_game()
        current_window = Window.MAIN
        init_field_cards()
    elif action == "skip_turn":
        skip_turn()


def skip_turn():
    global waiting_for_action, has_revealed_card_this_turn
    
    # Можно пропустить ход только если ещё не открывали карту в этом ходу
    if not waiting_for_action and not has_revealed_card_this_turn and not is_animating:
        end_turn()


def handle_card_click(index, pos):
    global waiting_for_action, balance, inventory, last_bought_card
    global has_revealed_card_this_turn, current_open_card_index
    
    if is_animating:
        return
    
    card = field_cards[index]
    
    # Если карта ещё не перевёрнута и мы ещё не открывали карту в этом ходу
    if card.state == CardState.BACK and not waiting_for_action and not has_revealed_card_this_turn:
        # Переворачиваем карту
        card.state = CardState.REVEALED
        if card.card_type == CardType.PRODUCT:
            card.buy_price = calculate_buy_price(card.name)
        has_revealed_card_this_turn = True
        waiting_for_action = True
        current_open_card_index = index
        return
    
    # Если карта уже открыта и мы ждём действие
    if card.state == CardState.REVEALED and waiting_for_action and index == current_open_card_index:
        
        if card.card_type == CardType.PRODUCT:
            # Проверяем, нажата ли кнопка "Купить"
            # Кнопка "Купить" находится в области x: card.x + 16, y: card.y + 290, ширина 95, высота 38
            buy_button_rect = pygame.Rect(card.x + 16, card.y + 290, 95, 38)
            # Кнопка "Отказаться" находится в области x: card.x + 129, y: card.y + 290, ширина 95, высота 38
            skip_button_rect = pygame.Rect(card.x + 129, card.y + 290, 95, 38)
            
            if buy_button_rect.collidepoint(pos):
                # Попытка покупки
                if len(inventory) < 8:
                    if balance >= card.buy_price:
                        balance -= card.buy_price
                        new_card = CardData(
                            name=card.name,
                            card_type=card.card_type,
                            state=CardState.INVENTORY,
                            x=0, y=0,
                            buy_price=card.buy_price,
                            sell_price=calculate_sell_price(card.name),
                            base_buy=card.base_buy,
                            base_sell=card.base_sell,
                            description=card.description
                        )
                        new_card.target_x=0
                        new_card.velocity_x=0
                        inventory.append(new_card)
                        last_bought_card = new_card
                        waiting_for_action = False
                        has_revealed_card_this_turn = False
                        current_open_card_index = -1
                        end_turn()
                        return
                    else:
                        last_bought_card = None
            elif skip_button_rect.collidepoint(pos):
                # Отказ от покупки - просто завершаем ход
                last_bought_card = None
                waiting_for_action = False
                has_revealed_card_this_turn = False
                current_open_card_index = -1
                end_turn()
                return
        else:
            # Для событий и негативных эффектов - одна кнопка "Принять"
            # Кнопка "Принять" находится в области x: card.x + 16, y: card.y + 307, ширина 208, высота 38
            accept_button_rect = pygame.Rect(card.x + 16, card.y + 307, 208, 38)
            
            is_con = True
            if accept_button_rect.collidepoint(pos):
                if card.card_type == CardType.EVENT:
                    for i in active_events:
                        if (i["name"] == card.name): 
                            i["duration"] = card.effect_duration
                            is_con = False
                    if is_con:
                        active_events.append({
                        'name': card.name,
                        'duration': card.effect_duration,
                        'effects': card.effects,
                        'risk_mod': card.risk_mod
                        })
                elif card.card_type == CardType.NEGATIVE:
                    apply_negative_effect(card.name)
                
                waiting_for_action = False
                has_revealed_card_this_turn = False
                current_open_card_index = -1
                end_turn()
                return


def handle_inventory_click(index):
    global waiting_for_action, balance, inventory, selected_product
    global selected_card_index, current_window, has_revealed_card_this_turn
    
    if waiting_for_action or is_animating or has_revealed_card_this_turn:
        return
    
    card = inventory[index]
    card.sell_price = calculate_sell_price(card.name)
    
    if lvl == 1:
        balance += card.sell_price
        inventory.pop(index)
    else:
        selected_product = card
        selected_card_index = index
        show_region_selection()


def show_region_selection():
    global current_window, region_buttons
    
    current_window = Window.SELL_REGIONS
    region_buttons = []
    
    num_regions = random.randint(1, 4)
    region_names = list(REGIONS.keys())
    random.shuffle(region_names)
    
    for i in range(num_regions):
        region_name = region_names[i % len(region_names)]
        distance = random.randint(1, 9)
        recipient = RecipientData(
            name=region_name,
            region=region_name,
            distance=distance,
            x=50 + i * 220,
            y=150
        )
        button = ButtonData(
            recipient.x, recipient.y, recipient.width, recipient.height,
            region_name, COLORS['beige'], COLORS['dark_brown'],
            "select_region", recipient
        )
        region_buttons.append(button)


def confirm_sell():
    global selected_product, selected_recipient, selected_card_index
    global inventory, sent_products, current_window
    
    if selected_product and selected_recipient:
        risk = min(0.95, 0.05 + selected_recipient.distance * 0.03)
        
        for event in active_events:
            risk += event.get('risk_mod', 0) / 100
        risk = min(0.95, risk)
        
        if random.random() > risk:
            sent_products.append((selected_product, selected_recipient, selected_recipient.distance))
            inventory.pop(selected_card_index)
        
        selected_product = None
        selected_recipient = None
        selected_card_index = None
        current_window = Window.MAIN


def apply_negative_effect(effect_name):
    global sent_products, inventory, last_bought_card
    
    if effect_name == "Разбойники" and sent_products:
        max_risk = -1
        target_index = -1
        for i, (_, recipient, _) in enumerate(sent_products):
            risk = min(0.95, 0.05 + recipient.distance * 0.03)
            if risk > max_risk:
                max_risk = risk
                target_index = i
        if target_index >= 0:
            sent_products.pop(target_index)
    
    elif effect_name == "Неудачное вложение" and last_bought_card:
        if last_bought_card in inventory:
            inventory.remove(last_bought_card)
        last_bought_card = None


def end_turn():
    global waiting_for_action, has_revealed_card_this_turn, balance, step, season
    global sent_products, active_events, current_window, current_open_card_index
    
    waiting_for_action = False
    has_revealed_card_this_turn = False
    current_open_card_index = -1
    
    # Списание налога 5%
    balance = int(balance * 0.97)
    
    if balance <= 0:
        current_window = Window.GAME_OVER
        return
    
    # Обновление доставок
    new_sent_products = []
    for card, recipient, distance in sent_products:
        if distance > 1:
            new_sent_products.append((card, recipient, distance - 1))
        else:
            sell_price = calculate_sell_price(card.name, recipient.region)
            balance += sell_price
    sent_products = new_sent_products
    
    # Обновление активных событий
    new_events = []
    for event in active_events:
        if event['duration'] > 1:
            event['duration'] -= 1
            new_events.append(event)
    active_events = new_events
    
    # Обновление хода и сезона
    step += 1
    if step > 32:
        step = 1
    
    if 1 <= step <= 8:
        season = Season.SUMMER
    elif 9 <= step <= 18:
        season = Season.AUTUMN
    elif 19 <= step <= 27:
        season = Season.WINTER
    else:
        season = Season.SPRING
    
    update_prices()
    
    start_animation()
    
    if balance >= target_sum:
        if lvl == 1:
            global is_pro
            is_pro = True
        current_window = Window.GAME_OVER


def restart_game():
    global balance, step, season, inventory, sent_products, active_events
    global last_bought_card, is_animating
    global has_revealed_card_this_turn, waiting_for_action, current_open_card_index
    
    balance = 300
    step = 1
    season = Season.SUMMER
    inventory = []
    sent_products = []
    active_events = []
    last_bought_card = None
    is_animating = False
    has_revealed_card_this_turn = False
    waiting_for_action = False
    current_open_card_index = -1
    update_prices()


def draw_menu():
    screen.fill(COLORS['light_brown'])
    
    title_surface = font_big.render("Merchant Simulator", True, COLORS['beige'])
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
    screen.blit(title_surface, title_rect)
    
    for button in buttons[Window.MENU]:
        draw_button(button)


def draw_levels():
    screen.fill(COLORS['beige'])
    
    title_surface = font_big.render("Выберите уровень", True, COLORS['dark_brown'])
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2+10, 100))
    screen.blit(title_surface, title_rect)
    
    for button in buttons[Window.LEVELS]:
        draw_button(button)
    
    if not is_pro:
        info_surface = font_small.render("Уровень 2 доступен после прохождения уровня 1", 
                                          True, COLORS['red'])
        info_rect = info_surface.get_rect(center=(SCREEN_WIDTH//2, 450))
        screen.blit(info_surface, info_rect)


def draw_rules():
    screen.fill(COLORS['beige'])
    
    title_surface = font_big.render("Правила игры", True, COLORS['dark_brown'])
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(title_surface, title_rect)
    
    rules_text1 = [
        "Цель: накопить нужную сумму, не обанкротившись.",
        "",
        "Игровой процесс:",
        "• Перед вами 4 скрытые карты.",
        "• За один ход можно открыть ТОЛЬКО ОДНУ карту.",
        "• После открытия: купить товар, принять событие или отказаться.",
        "• Можно пропустить ход, не открывая карту.",
        "",
        "Зависимость цен от сезонов (жизненная логика):",
        "• Зимой дорожают: тёплые вещи (меха, шерсть), уголь, лекарства, вино",
        "• Летом дорожают: продукты (пшеница, рыба, специи)",
        "• Осенью дорожают: рыба, железо, вино, специи",
        "• Весной дорожают: лекарства, специи",
        "",
        "Зависимость цен от событий:",
        "• Война → дорожают ресурсы (уголь, железо, лекарства),",
        "  дешевеют предметы роскоши (вино, драгоценности, специи)",
        "• Эпидемия → резко дорожают лекарства, дешевеют рыба и мясо",
        "• Сухой закон → резко дешевеет вино",
        "• Праздник → дорожают вино, специи, драгоценности",
        "• Шахтёрская забастовка → дорожают уголь и железо",
        ""
    ]

    rules_text2 = [
        "Зависимость цен от региона (2 уровень):",
        "• Горный регион → дороже пшеница, рыба, лекарства, специи;",
        "  дешевле уголь, железо, драгоценности",
        "• Приморье → дороже уголь, железо, драгоценности, специи;",
        "  дешевле рыба и вино",
        "• Тайга → дороже пшеница, уголь, железо, вино, специи;",
        "  дешевле лекарства и драгоценности",
        "• Степь → базовые цены (без изменений)",
        "",
        "2 уровень: продажа через выбор региона доставки.",
        "Чем дальше регион, тем выше цена, но и риск потери товара.",
        "",
        "Поражение: баланс стал равен 0 или ниже.",
        "Победа: достигнута целевая сумма."
    ]
    
    y_offset = 100
    for line in rules_text1:
        text_surface = font_small.render(line, True, COLORS['black'])
        screen.blit(text_surface, (50, y_offset))
        y_offset += 22

    y_offset = 150
    for line in rules_text2:
        text_surface = font_small.render(line, True, COLORS['black'])
        screen.blit(text_surface, (730, y_offset))
        y_offset += 22
    
    draw_button(rules_back_button)


def draw_main():
    screen.fill(COLORS['beige'])
    
    balance_surface = font_medium.render(f"Баланс: {int(balance)} золотых", True, COLORS['brown'])
    screen.blit(balance_surface, (1050, 21))
    
    target_surface = font_medium.render(f"Цель: {target_sum}", True, COLORS['brown'])
    screen.blit(target_surface, (1070, 60))
    
    pause_button = ButtonData(40, 35, 50, 50, "-", COLORS['dark_brown'], COLORS['white'], "pause")
    draw_button(pause_button)
    
    draw_button(skip_turn_button)
    
    calendar_rect = pygame.Rect(400, 0, 480, 150)
    pygame.draw.rect(screen, COLORS['dark_beige'], calendar_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], calendar_rect, 2)
    
    season_surface = font_medium.render(f"Сезон: {season.value}", True, COLORS['dark_brown'])
    season_rect = season_surface.get_rect(center=(640, 50))
    screen.blit(season_surface, season_rect)
    
    step_surface = font_small.render(f"Ход: {step}/32", True, COLORS['dark_brown'])
    step_rect = step_surface.get_rect(center=(640, 90))
    screen.blit(step_surface, step_rect)
    
    if active_events:
        event_y = 160
        for event in active_events[:2]:
            event_surface = font_small.render(f"⚡{event['name']}: {event['duration']} ходов", 
                                               True, COLORS['red'])
            event_rect = event_surface.get_rect(center=(640, event_y))
            screen.blit(event_surface, event_rect)
            event_y += 20
    
    for card in field_cards:
        show_price = (card.state == CardState.REVEALED)
        draw_card(card, show_price)
    
    for card in new_field_cards:
        draw_card(card, False)
    
    inv_y = 553
    inv_bg = pygame.Rect(0, inv_y - 10, SCREEN_WIDTH, 180)
    pygame.draw.rect(screen, COLORS['dark_beige'], inv_bg)
    pygame.draw.rect(screen, COLORS['dark_brown'], inv_bg, 2)
    
    inv_title = font_medium.render("Инвентарь", True, COLORS['dark_brown'])
    screen.blit(inv_title, (10, inv_y - 5))
    
    for i in range(8):
        x = 218 + i * 85
        card_rect = pygame.Rect(x, inv_y, 70, 100)
        pygame.draw.rect(screen, COLORS['beige'], card_rect)
        pygame.draw.rect(screen, COLORS['dark_brown'], card_rect, 2)
        
        if i < len(inventory):
            card = inventory[i]
            card.sell_price = calculate_sell_price(card.name)
            
            name_surface = font_small.render(card.name[:8], True, COLORS['dark_brown'])
            screen.blit(name_surface, (x + 5, inv_y + 5))
            
            price_surface = font_small.render(f"{int(card.sell_price)}", True, COLORS['green'])
            screen.blit(price_surface, (x + 5, inv_y + 70))
            
            pygame.draw.rect(screen, COLORS['green'], (x + 5, inv_y + 80, 60, 15))
            sell_text = font_small.render("Продать", True, COLORS['white'])
            sell_rect = sell_text.get_rect(center=(x + 35, inv_y + 87))
            screen.blit(sell_text, sell_rect)


def draw_events_window():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(COLORS['dark_beige'])
    screen.blit(overlay, (0, 0))
    
    window_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 250, 600, 500)
    pygame.draw.rect(screen, COLORS['beige'], window_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], window_rect, 3)
    
    title_surface = font_big.render("Активные события", True, COLORS['dark_brown'])
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 200))
    screen.blit(title_surface, title_rect)
    
    if not active_events:
        text_surface = font_medium.render("Нет активных событий", True, COLORS['black'])
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text_surface, text_rect)
    else:
        y_offset = SCREEN_HEIGHT//2 - 120
        for event in active_events:
            event_surface = font_medium.render(
                f"{event['name']} - осталось: {event['duration']} ходов", 
                True, COLORS['dark_brown']
            )
            event_rect = event_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset))
            screen.blit(event_surface, event_rect)
            
            if event.get('effects'):
                effects_text = ", ".join([f"{k}: {v}%" for k, v in list(event['effects'].items())[:3]])
                if len(event['effects']) > 3:
                    effects_text += "..."
                effects_surface = font_small.render(effects_text, True, COLORS['black'])
                effects_rect = effects_surface.get_rect(center=(SCREEN_WIDTH//2, y_offset + 25))
                screen.blit(effects_surface, effects_rect)
            y_offset += 60
    
    draw_button(close_button)


def draw_game_over():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(COLORS['black'])
    screen.blit(overlay, (0, 0))
    
    window_rect = pygame.Rect(SCREEN_WIDTH//2 - 350, SCREEN_HEIGHT//2 - 200, 700, 400)
    pygame.draw.rect(screen, COLORS['dark_beige'], window_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], window_rect, 3)
    
    if balance <= 0:
        text = "ПОРАЖЕНИЕ!"
        color = COLORS['red']
        subtext = "Вы обанкротились..."
    else:
        text = "ПОБЕДА!"
        color = COLORS['green']
        subtext = f"Вы достигли цели в {target_sum} золотых!"
    
    title_surface = font_big.render(text, True, color)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(title_surface, title_rect)
    
    sub_surface = font_medium.render(subtext, True, COLORS['dark_brown'])
    sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 40))
    screen.blit(sub_surface, sub_rect)
    
    menu_button = ButtonData(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 + 50, 250, 80,
                           "Меню", COLORS['button_brown'], COLORS['black'], "menu")
    restart_button = ButtonData(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 50, 250, 80,
                               "Начать заново", COLORS['button_brown'], COLORS['black'], "restart")
    
    draw_button(menu_button)
    draw_button(restart_button)
    
    global game_over_buttons
    game_over_buttons = [menu_button, restart_button]


def draw_sell_regions():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(COLORS['dark_brown'])
    screen.blit(overlay, (0, 0))
    
    title_surface = font_big.render("Выберите регион для продажи", True, COLORS['beige'])
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(title_surface, title_rect)
    
    if selected_product:
        product_surface = font_medium.render(
            f"Товар: {selected_product.name}", True, COLORS['beige']
        )
        product_rect = product_surface.get_rect(center=(SCREEN_WIDTH//2, 110))
        screen.blit(product_surface, product_rect)
    
    for button in region_buttons:
        draw_button(button)
        if button.data:
            draw_recipient(button.data)
    
    draw_button(close_button)


def draw_recipient_window():
    if selected_product and selected_recipient:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS['dark_brown'])
        screen.blit(overlay, (0, 0))
        
        window_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 200, 500, 400)
        pygame.draw.rect(screen, COLORS['beige'], window_rect)
        pygame.draw.rect(screen, COLORS['dark_brown'], window_rect, 3)
        
        title_surface = font_big.render("Подтверждение продажи", True, COLORS['dark_brown'])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        screen.blit(title_surface, title_rect)
        
        product_surface = font_medium.render(f"Товар: {selected_product.name}", True, COLORS['dark_brown'])
        product_rect = product_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
        screen.blit(product_surface, product_rect)
        
        region_surface = font_medium.render(
            f"Регион: {selected_recipient.region}", True, COLORS['dark_brown']
        )
        region_rect = region_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(region_surface, region_rect)
        
        delivery_surface = font_small.render(
            f"Доставка: {selected_recipient.distance} ходов", True, COLORS['black']
        )
        delivery_rect = delivery_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        screen.blit(delivery_surface, delivery_rect)
        
        risk = min(0.95, 0.05 + selected_recipient.distance * 0.03)
        for event in active_events:
            risk += event.get('risk_mod', 0) / 100
        risk = min(0.95, risk)
        
        risk_surface = font_small.render(f"Риск потери: {int(risk * 100)}%", True, COLORS['red'])
        risk_rect = risk_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        screen.blit(risk_surface, risk_rect)
        
        sell_price = calculate_sell_price(selected_product.name, selected_recipient.region)
        price_surface = font_medium.render(f"Цена продажи: {int(sell_price)} золотых", True, COLORS['green'])
        price_rect = price_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
        screen.blit(price_surface, price_rect)
        
        sell_button = ButtonData(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 150, 180, 50,
                               "Продать", COLORS['button_brown'], COLORS['black'], "confirm_sell")
        back_button = ButtonData(SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 150, 180, 50,
                               "Вернуться", COLORS['dark_beige'], COLORS['black'], "back_to_regions")
        
        draw_button(sell_button)
        draw_button(back_button)
        
        global recipient_buttons
        recipient_buttons = [sell_button, back_button]


def draw_pause():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill(COLORS['black'])
    screen.blit(overlay, (0, 0))
    
    window_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 200, 500, 400)
    pygame.draw.rect(screen, COLORS['beige'], window_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], window_rect, 3)
    
    title_surface = font_big.render("Пауза", True, COLORS['dark_brown'])
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120))
    screen.blit(title_surface, title_rect)
    
    y_offset = SCREEN_HEIGHT//2 - 50
    for button in buttons[Window.PAUSE]:
        button.y = y_offset
        draw_button(button)
        y_offset += 100


def handle_click(pos):
    global current_window, selected_recipient, selected_product, selected_card_index
    global inventory, sent_products
    
    if current_window in buttons:
        for button in buttons[current_window]:
            if is_hovered(button, pos):
                handle_button_action(button.action, button.data)
                return
    
    if current_window in [Window.RULES, Window.EVENTS, Window.SELL_REGIONS, Window.GAME_OVER]:
        if is_hovered(close_button, pos):
            handle_button_action("close")
            return
    
    if current_window == Window.RULES:
        if is_hovered(rules_back_button, pos):
            handle_button_action("back")
            return
    
    if current_window == Window.MAIN:
        pause_button = ButtonData(40, 35, 50, 50, "▷", COLORS['dark_brown'], COLORS['white'], "pause")
        if is_hovered(pause_button, pos):
            current_window = Window.PAUSE
            return
        
        if is_hovered(skip_turn_button, pos) and not waiting_for_action and not has_revealed_card_this_turn and not is_animating:
            skip_turn()
            return
        
        calendar_rect = pygame.Rect(400, 0, 480, 200)
        if calendar_rect.collidepoint(pos):
            current_window = Window.EVENTS
            return
        
        for i, card in enumerate(field_cards):
            card_rect = pygame.Rect(card.x, card.y, card.width, card.height)
            if card_rect.collidepoint(pos):
                handle_card_click(i, pos)
                return
        
        for i, card in enumerate(inventory):
            card_rect = pygame.Rect(218 + i * 85, 553, 70, 100)
            if card_rect.collidepoint(pos):
                handle_inventory_click(i)
                return
    
    if current_window == Window.SELL_REGIONS:
        for i, button in enumerate(region_buttons):
            if is_hovered(button, pos):
                selected_recipient = button.data
                current_window = Window.RECIPIENT
                return
    
    if current_window == Window.RECIPIENT:
        sell_button = ButtonData(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 150, 180, 50,
                               "Продать", COLORS['button_brown'], COLORS['black'], "confirm_sell")
        back_button = ButtonData(SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 150, 180, 50,
                               "Вернуться", COLORS['dark_beige'], COLORS['black'], "back_to_regions")
        
        if is_hovered(sell_button, pos):
            confirm_sell()
        elif is_hovered(back_button, pos):
            current_window = Window.SELL_REGIONS
    
    if current_window == Window.GAME_OVER:
        menu_button = ButtonData(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 + 50, 250, 80,
                               "Меню", COLORS['button_brown'], COLORS['black'], "menu")
        restart_button = ButtonData(SCREEN_WIDTH//2 + 50, SCREEN_HEIGHT//2 + 50, 250, 80,
                               "Начать заново", COLORS['button_brown'], COLORS['black'], "restart")
        
        if is_hovered(menu_button, pos):
            restart_game()
            current_window = Window.MENU
        elif is_hovered(restart_button, pos):
            restart_game()
            current_window = Window.MAIN
            init_field_cards()


def run():
    global screen, clock, running, font_big, font_medium, font_small
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Merchant Simulator")
    clock = pygame.time.Clock()
    
    font_big = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    
    init_buttons()
    init_field_cards()
    update_prices()
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                handle_click(event.pos)
        
        update_animation()
        
        if current_window == Window.MENU:
            draw_menu()
        elif current_window == Window.LEVELS:
            draw_levels()
        elif current_window == Window.RULES:
            draw_rules()
        elif current_window == Window.MAIN:
            draw_main()
        elif current_window == Window.EVENTS:
            draw_events_window()
        elif current_window == Window.GAME_OVER:
            draw_game_over()
        elif current_window == Window.SELL_REGIONS:
            draw_sell_regions()
        elif current_window == Window.RECIPIENT:
            draw_recipient_window()
        elif current_window == Window.PAUSE:
            draw_pause()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()


if __name__ == "__main__":
    run()