import random
from game_config import *
from game_state import game_state

def generate_random_card():
    products = ["Пшеница", "Рыба", "Уголь", "Шерсть", "Железо", "Вино", "Лекарства", "Меха", "Специи", "Драгоценные камни"]
    events = ["Война", "Эпидемия", "Сухой закон", "Праздник", "Шахтёрская забастовка"]
    if game_state.lvl == 1:
        negatives = ["Неудачное вложение"]
    else:
        negatives = ["Разбойники", "Неудачное вложение"]
    
    rand = random.random()

    if rand < 0.85:
        name = random.choice(products)
        base_buy = random.randint(8, 80)
        return {
            'name': name,
            'type': CardType.PRODUCT,
            'buy_price': base_buy,
            'sell_price': int(base_buy * 0.7),
            'base_buy': base_buy,
            'base_sell': int(base_buy * 0.7),
            'desc': f"Купить за {base_buy}, продать за {int(base_buy * 0.7)}"
        }
    elif rand < 0.95:
        name = random.choice(events)
        durations = {
            "Война": 8, 
            "Эпидемия": 10, 
            "Сухой закон": 7, 
            "Праздник": 4, 
            "Шахтёрская забастовка": 4
        }
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
            'duration': durations.get(name, 4),
            'effects': effects.get(name, {}),
            'risk_mod': risk_mod,
            'desc': f"Событие: {name} на {durations.get(name, 4)} ходов"
        }
    else:
        name = random.choice(negatives)
        return {
            'name': name,
            'type': CardType.NEGATIVE,
            'desc': f"Негативное событие: {name}"
        }

def calculate_buy_price(product_name):
    base_prices = {"Пшеница": 8, "Рыба": 12, "Уголь": 10, "Шерсть": 15, "Железо": 20, 
                   "Вино": 25, "Лекарства": 30, "Меха": 35, "Специи": 40, "Драгоценные камни": 80}
    base = base_prices.get(product_name, 10)
    
    multiplier = 1.0
    
    # Сезонность (как в calculate_sell_price, но для товара без суффикса)
    if game_state.season == Season.SUMMER:
        if product_name in ["Пшеница"]: multiplier += 0.50
        if product_name in ["Уголь"]: multiplier -= 0.50
        if product_name in ["Железо"]: multiplier -= 0.30
        if product_name in ["Меха"]: multiplier -= 0.70
        if product_name in ["Шерсть"]: multiplier -= 0.40
        if product_name in ["Драгоценные камни"]: multiplier += 0.10
    elif game_state.season == Season.AUTUMN:
        if product_name in ["Пшеница"]: multiplier -= 0.30
        if product_name in ["Рыба"]: multiplier += 0.60
        if product_name in ["Железо"]: multiplier += 0.30
        if product_name in ["Вино"]: multiplier += 0.40
        if product_name in ["Специи"]: multiplier += 0.35
    elif game_state.season == Season.WINTER:
        if product_name in ["Железо"]: multiplier += 0.50
        if product_name in ["Уголь"]: multiplier += 0.70
        if product_name in ["Шерсть"]: multiplier += 0.60
        if product_name in ["Вино"]: multiplier += 0.50
        if product_name in ["Лекарства"]: multiplier += 0.60
        if product_name in ["Меха"]: multiplier += 0.80
        if product_name in ["Пшеница"]: multiplier += 0.50
        if product_name in ["Рыба"]: multiplier += 0.70
        if product_name in ["Специи"]: multiplier += 0.50
    elif game_state.season == Season.SPRING:
        if product_name in ["Рыба"]: multiplier += 0.40
        if product_name in ["Шерсть"]: multiplier -= 0.40
        if product_name in ["Лекарства"]: multiplier += 0.30
        if product_name in ["Специи"]: multiplier += 0.35
        if product_name in ["Пшеница"]: multiplier += 0.50
        
    # События (ищем эффекты по чистому имени и с суффиксом -инвентарь)
    for event in game_state.active_events:
        effects = event.get('effects', {})
        if product_name in effects:
            multiplier += effects[product_name] / 100.0
        elif (product_name + "-инвентарь") in effects:
            multiplier += effects[product_name + "-инвентарь"] / 100.0
            
    # Ограничения: 20%–250% от базовой цены покупки
    multiplier = max(0.20, min(2.50, multiplier))
    final_price = base * multiplier
    return max(1, int(final_price))

def calculate_sell_price(product_name, region=None, distance=None):
    base_prices = {"Пшеница-инвентарь": 7, "Рыба-инвентарь": 10, "Уголь-инвентарь": 8, "Шерсть-инвентарь": 13, "Железо-инвентарь": 17, 
                   "Вино-инвентарь": 22, "Лекарства-инвентарь": 25, "Меха-инвентарь": 30, "Специи-инвентарь": 35, "Драгоценные камни-инвентарь": 70}
    base = base_prices.get(product_name, 5)
    
    multiplier = 1.0
    
    # Сезонность (Таблица 3)
    if game_state.season == Season.SUMMER:
        if product_name in ["Пшеница-инвентарь"]: multiplier += 0.50
        if product_name in ["Уголь-инвентарь"]: multiplier -= 0.50
        if product_name in ["Железо-инвентарь"]: multiplier -= 0.30
        if product_name in ["Меха-инвентарь"]: multiplier -= 0.70
        if product_name in ["Шерсть-инвентарь"]: multiplier -= 0.40
        if product_name in ["Драгоценные камни-инвентарь"]: multiplier += 0.10
    elif game_state.season == Season.AUTUMN:
        if product_name in ["Пшеница-инвентарь"]: multiplier -= 0.30
        if product_name in ["Рыба-инвентарь"]: multiplier += 0.60
        if product_name in ["Железо-инвентарь"]: multiplier += 0.30
        if product_name in ["Вино-инвентарь"]: multiplier += 0.40
        if product_name in ["Специи-инвентарь"]: multiplier += 0.35
    elif game_state.season == Season.WINTER:
        if product_name in ["Железо-инвентарь"]: multiplier += 0.50
        if product_name in ["Уголь-инвентарь"]: multiplier += 0.70
        if product_name in ["Шерсть-инвентарь"]: multiplier += 0.60
        if product_name in ["Вино-инвентарь"]: multiplier += 0.50
        if product_name in ["Лекарства-инвентарь"]: multiplier += 0.60
        if product_name in ["Меха-инвентарь"]: multiplier += 0.80
        if product_name in ["Пшеница-инвентарь"]: multiplier += 0.50
        if product_name in ["Рыба-инвентарь"]: multiplier += 0.70
        if product_name in ["Специи-инвентарь"]: multiplier += 0.50
    elif game_state.season == Season.SPRING:
        if product_name in ["Рыба-инвентарь"]: multiplier += 0.40
        if product_name in ["Шерсть-инвентарь"]: multiplier -= 0.40
        if product_name in ["Лекарства-инвентарь"]: multiplier += 0.30
        if product_name in ["Специи-инвентарь"]: multiplier += 0.35
        if product_name in ["Пшеница-инвентарь"]: multiplier += 0.50
        
    # События
    clean_name = product_name.replace("-инвентарь", "")
    for event in game_state.active_events:
        effects = event.get('effects', {})
        if product_name in effects:
            multiplier += effects[product_name] / 100.0
        elif clean_name in effects:
            multiplier += effects[clean_name] / 100.0
            
    # Регион (только для 2 уровня) — Таблица 2
    if region and game_state.lvl == 2:
        if region == "Горный":
            if product_name in ["Пшеница-инвентарь"]: multiplier += 0.20
            if product_name in ["Рыба-инвентарь"]: multiplier += 0.20
            if product_name in ["Вино-инвентарь"]: multiplier += 0.10
            if product_name in ["Лекарства-инвентарь"]: multiplier += 0.30
            if product_name in ["Специи-инвентарь"]: multiplier += 0.30
            if product_name in ["Уголь-инвентарь"]: multiplier -= 0.40
            if product_name in ["Железо-инвентарь"]: multiplier -= 0.30
            if product_name in ["Драгоценные камни-инвентарь"]: multiplier -= 0.30
        elif region == "Приморье":
            if product_name in ["Уголь-инвентарь"]: multiplier += 0.20
            if product_name in ["Железо-инвентарь"]: multiplier += 0.10
            if product_name in ["Драгоценные камни-инвентарь"]: multiplier += 0.30
            if product_name in ["Пшеница-инвентарь"]: multiplier += 0.10
            if product_name in ["Специи-инвентарь"]: multiplier += 0.10
            if product_name in ["Рыба-инвентарь"]: multiplier -= 0.40
            if product_name in ["Вино-инвентарь"]: multiplier -= 0.20
        elif region == "Тайга":
            if product_name in ["Пшеница-инвентарь"]: multiplier += 0.10
            if product_name in ["Вино-инвентарь"]: multiplier += 0.10
            if product_name in ["Специи-инвентарь"]: multiplier += 0.10
            if product_name in ["Уголь-инвентарь"]: multiplier += 0.20
            if product_name in ["Железо-инвентарь"]: multiplier += 0.10
            if product_name in ["Лекарства-инвентарь"]: multiplier -= 0.20
            if product_name in ["Драгоценные камни-инвентарь"]: multiplier -= 0.10
        # Степь — без изменений (базовые цены)

    if distance is not None and distance > 0:
        risk = 0.05 + distance * 0.03
        for event in game_state.active_events:
            risk += event.get('risk_mod', 0) / 100.0
        risk = min(0.95, risk)
        multiplier *= (1 + risk)   # цена растёт с риском
            
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
    
    # Сбрасываем регионы
    game_state.regions_generated = False
    game_state.saved_region_buttons = []
    game_state.region_buttons = []
    game_state.selected_product = None
    game_state.selected_recipient = None
    game_state.selected_card_index = None

def end_turn():
    game_state.waiting_for_action = False
    game_state.has_revealed_card_this_turn = False
    game_state.current_open_card_index = -1

    # Списание 1% от баланса за ход
    game_state.balance = int(game_state.balance * 0.99)

    if game_state.balance <= 0:
        game_state.current_window = Window.GAME_OVER
        return

    new_sent_products = []
    for item in game_state.sent_products:
        card, recipient, distance, price = item   # распаковываем с ценой
        if distance > 1:
            new_sent_products.append((card, recipient, distance - 1, price))
        else:
            game_state.balance += price
            print(f"[DEBUG] Delivered {card.name} for {price}")
    game_state.sent_products = new_sent_products

    # Обновляем события - уменьшаем длительность
    new_events = []
    for event in game_state.active_events:
        if event.get('duration', 0) > 1:
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
    
    # Сбрасываем регионы для следующего хода
    game_state.regions_generated = False
    game_state.saved_region_buttons = []
    game_state.region_buttons = []
    game_state.selected_product = None
    game_state.selected_recipient = None
    game_state.selected_card_index = None
    
    from game_animation import start_animation
    start_animation()

    if game_state.balance >= game_state.target_sum:
        if game_state.lvl == 1:
            game_state.is_pro = True
        game_state.current_window = Window.GAME_OVER