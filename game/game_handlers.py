import random
import pygame
from game_config import Window, Season, CardType, CardState, REGIONS, SCREEN_WIDTH, SCREEN_HEIGHT
from game_structures import ButtonData, CardData, RecipientData
from game_logic import *
from game_animation import init_field_cards, start_animation

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
    
    if not waiting_for_action and not has_revealed_card_this_turn and not is_animating:
        end_turn()

def end_turn():
    global waiting_for_action, has_revealed_card_this_turn, balance, step, season
    global sent_products, active_events, current_window, current_open_card_index
    
    waiting_for_action = False
    has_revealed_card_this_turn = False
    current_open_card_index = -1
    
    balance = int(balance * 0.97)
    
    if balance <= 0:
        current_window = Window.GAME_OVER
        return
    
    new_sent_products = []
    for card, recipient, distance in sent_products:
        if distance > 1:
            new_sent_products.append((card, recipient, distance - 1))
        else:
            sell_price = calculate_sell_price(card.name, recipient.region)
            balance += sell_price
    sent_products = new_sent_products
    
    new_events = []
    for event in active_events:
        if event['duration'] > 1:
            event['duration'] -= 1
            new_events.append(event)
    active_events = new_events
    
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

def handle_card_click(index, pos):
    global waiting_for_action, balance, inventory, last_bought_card
    global has_revealed_card_this_turn, current_open_card_index
    
    if is_animating:
        return
    
    card = field_cards[index]
    
    if card.state == CardState.BACK and not waiting_for_action and not has_revealed_card_this_turn:
        card.state = CardState.REVEALED
        if card.card_type == CardType.PRODUCT:
            card.buy_price = calculate_buy_price(card.name)
        has_revealed_card_this_turn = True
        waiting_for_action = True
        current_open_card_index = index
        return
    
    if card.state == CardState.REVEALED and waiting_for_action and index == current_open_card_index:
        
        if card.card_type == CardType.PRODUCT:
            buy_button_rect = pygame.Rect(card.x + 16, card.y + 290, 95, 38)
            skip_button_rect = pygame.Rect(card.x + 129, card.y + 290, 95, 38)
            
            if buy_button_rect.collidepoint(pos):
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
                        inventory.append(new_card)
                        last_bought_card = new_card
                waiting_for_action = False
                has_revealed_card_this_turn = False
                current_open_card_index = -1
                end_turn()
                return
            elif skip_button_rect.collidepoint(pos):
                waiting_for_action = False
                has_revealed_card_this_turn = False
                current_open_card_index = -1
                end_turn()
                return
        else:
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

# Импорты для использования
from game_config import COLORS