import random
from game_config import *
from game_state import game_state

def generate_random_card():
    products = ["Пшеница", "Рыба", "Уголь", "Шерсть", "Железо", "Вино", "Лекарства", "Меха", "Специи", "Драгоценные камни"]
    events = ["Война", "Эпидемия", "Сухой закон", "Праздник", "Шахтёрская забастовка"]
    negatives = ["Разбойники", "Неудачное вложение"]
    
    rand = random.random()

    if rand < 0.7:
        name = random.choice(products)
        base_buy = random.randint(8, 80)
        return {
            'name': name,
            'type': CardType.PRODUCT,
            'buy_price': base_buy,
            'sell_price': int(base_buy * 0.7),
            'base_buy': base_buy,
            'base_sell': int(base_buy * 0.7)
        }
    elif rand < 0.9:
        name = random.choice(events)
        durations = {"Война": 8, "Эпидемия": 10, "Сухой закон": 7, "Праздник": 4, "Шахтёрская забастовка": 4}
        effects = {
            "Война": {"Уголь": 80, "Железо": 100, "Меха": 40},
            "Эпидемия": {"Лекарства": 150},
            "Сухой закон": {"Вино": -80},
            "Праздник": {"Драгоценные камни": 50, "Специи": 80, "Вино": 70},
            "Шахтёрская забастовка": {"Уголь": 100, "Железо": 120}
        }
        risk_mod = 0
        if name == "Война": risk_mod = 20
        if name == "Эпидемия": risk_mod = 30
        
        return {
            'name': name,
            'type': CardType.EVENT,
            'duration': durations[name],
            'effects': effects.get(name, {}),
            'risk_mod': risk_mod
        }
    else:
        name = random.choice(negatives)
        return {
            'name': name,
            'type': CardType.NEGATIVE
        }

def calculate_buy_price(product_name):
    base_prices = {"Пшеница": 8, "Рыба": 12, "Уголь": 10, "Шерсть": 15, "Железо": 20, 
                   "Вино": 25, "Лекарства": 30, "Меха": 35, "Специи": 40, "Драгоценные камни": 80}
    base = base_prices.get(product_name, 10)
    return int(base * random.uniform(0.9, 1.1))

def calculate_sell_price(product_name, region=None):
    base_prices = {"Пшеница": 5, "Рыба": 8, "Уголь": 6, "Шерсть": 10, "Железо": 14, 
                   "Вино": 18, "Лекарства": 22, "Меха": 25, "Специи": 30, "Драгоценные камни": 60}
    base = base_prices.get(product_name, 5)
    
    multiplier = 1.0
    
    # Сезонность
    if game_state.season == Season.WINTER:
        if product_name in ["Уголь", "Меха", "Лекарства"]: multiplier += 0.3
        if product_name in ["Пшеница", "Рыба"]: multiplier -= 0.1
    elif game_state.season == Season.SUMMER:
        if product_name in ["Пшеница", "Рыба"]: multiplier += 0.2
        if product_name in ["Уголь", "Меха"]: multiplier -= 0.2
        
    # События
    for event in game_state.active_events:
        if product_name in event['effects']:
            multiplier += event['effects'][product_name] / 100.0
            
    # Регион (только для 2 уровня)
    if region and game_state.lvl == 2:
        if region == "Горный":
            if product_name in ["Пшеница", "Рыба", "Лекарства"]: multiplier += 0.2
            if product_name in ["Уголь", "Железо"]: multiplier -= 0.3
        elif region == "Приморье":
            if product_name in ["Уголь", "Железо"]: multiplier += 0.1
            if product_name in ["Рыба"]: multiplier -= 0.4
            
    final_price = base * multiplier
    return max(1, int(final_price))

def apply_negative_effect(effect_name):
    if effect_name == "Разбойники":
        if game_state.sent_products:
            game_state.sent_products.pop(0)
    elif effect_name == "Неудачное вложение":
        if game_state.inventory:
            game_state.inventory.pop()

def update_prices():
    for card in game_state.inventory:
        card.sell_price = calculate_sell_price(card.name)

def restart_game():
    game_state.balance = 300
    game_state.step = 1
    game_state.season = Season.SUMMER
    game_state.inventory = []
    game_state.sent_products = []
    game_state.active_events = []
    game_state.field_cards = []
    game_state.new_field_cards = []
    game_state.waiting_for_action = False
    game_state.has_revealed_card_this_turn = False
    game_state.current_open_card_index = -1
    game_state.last_bought_card = None

def end_turn():
    game_state.waiting_for_action = False
    game_state.has_revealed_card_this_turn = False
    game_state.current_open_card_index = -1

    # Списание 5% от баланса за ход
    game_state.balance = int(game_state.balance * 0.95)

    if game_state.balance <= 0:
        game_state.current_window = Window.GAME_OVER
        return

    new_sent_products = []
    for card, recipient, distance in game_state.sent_products:
        if distance > 1:
            new_sent_products.append((card, recipient, distance - 1))
        else:
            sell_price = calculate_sell_price(card.name, recipient.region)
            game_state.balance += sell_price
    game_state.sent_products = new_sent_products

    new_events = []
    for event in game_state.active_events:
        if event['duration'] > 1:
            event['duration'] -= 1
            new_events.append(event)
    game_state.active_events = new_events

    game_state.step += 1
    if game_state.step > 32:
        game_state.step = 1

    if 1 <= game_state.step <= 8:
        game_state.season = Season.SUMMER
    elif 9 <= game_state.step <= 18:
        game_state.season = Season.AUTUMN
    elif 19 <= game_state.step <= 27:
        game_state.season = Season.WINTER
    else:
        game_state.season = Season.SPRING

    update_prices()
    
    from game_animation import start_animation
    start_animation()

    if game_state.balance >= game_state.target_sum:
        if game_state.lvl == 1:
            game_state.is_pro = True
        game_state.current_window = Window.GAME_OVER