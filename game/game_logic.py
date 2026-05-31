import random
from game_config import PRODUCTS, EVENTS, NEGATIVE_EVENTS, REGIONS, Season, CardType
from game_structures import CardData, RecipientData
from game_config import CardState

# Глобальные переменные
lvl = 1
is_pro = False
balance = 300
target_sum = 1000
step = 1
season = Season.SUMMER
has_revealed_card_this_turn = False
waiting_for_action = False
current_open_card_index = -1

last_bought_card = None
field_cards = []
new_field_cards = []
inventory = []
sent_products = []
active_events = []

current_prices = {}

# Анимация
is_animating = False
animation_progress = 0
animation_speed = 15

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
            neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))
            while (neg_name == "Разбойники"): neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))                
            neg = NEGATIVE_EVENTS[neg_name]
        else:
            neg_name = random.choice(list(NEGATIVE_EVENTS.keys()))
            neg = NEGATIVE_EVENTS[neg_name]
        return {
            'name': neg_name,
            'type': CardType.NEGATIVE,
            'desc': neg['desc'],
            'duration': neg['duration']
        }

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