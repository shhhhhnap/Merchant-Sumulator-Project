import random
import pygame
from game_config import *
from game_logic import *
from game_animation import init_field_cards, start_animation
from game_state import game_state
from game_structures import CardData, RecipientData, ButtonData

def skip_turn():
    if not game_state.waiting_for_action and not game_state.has_revealed_card_this_turn and not game_state.is_animating:
        end_turn()

def show_region_selection():
    game_state.current_window = Window.SELL_REGIONS
    game_state.region_buttons = []

    num_regions = random.randint(1, 4)
    region_names = ["Горный", "Приморье", "Тайга", "Степь"]
    random.shuffle(region_names)

    # Уменьшенные карточки, чтобы помещались все 4
    if num_regions <= 2:
        CARD_WIDTH = 250
        CARD_HEIGHT = 320
        CARD_SPACING = 40
    elif num_regions == 3:
        CARD_WIDTH = 220
        CARD_HEIGHT = 300
        CARD_SPACING = 30
    else:  # 4 региона
        CARD_WIDTH = 190
        CARD_HEIGHT = 280
        CARD_SPACING = 20
    
    spacing = CARD_WIDTH + CARD_SPACING
    
    total_width = num_regions * CARD_WIDTH + (num_regions - 1) * CARD_SPACING
    start_x = (SCREEN_WIDTH - total_width) // 2

    for i in range(num_regions):
        region_name = region_names[i % len(region_names)]
        distance = random.randint(1, 9)
        
        x = start_x + i * spacing
        
        recipient = RecipientData(
            name=region_name,
            region=region_name,
            distance=distance,
            x=x,
            y=160,  # Немного ниже, чтобы поместился заголовок
            width=CARD_WIDTH,
            height=CARD_HEIGHT
        )
        button = ButtonData(
            recipient.x, recipient.y, recipient.width, recipient.height,
            region_name, COLORS['beige'], COLORS['dark_brown'],
            "select_region", recipient
        )
        game_state.region_buttons.append(button)

def confirm_sell():
    if game_state.selected_product and game_state.selected_recipient:
        risk = min(0.95, 0.05 + game_state.selected_recipient.distance * 0.03)
        
        for event in game_state.active_events:
            risk += event.get('risk_mod', 0) / 100
        risk = min(0.95, risk)
        
        if random.random() > risk:
            game_state.sent_products.append((game_state.selected_product, game_state.selected_recipient, game_state.selected_recipient.distance))
            game_state.inventory.pop(game_state.selected_card_index)
        else:
            game_state.inventory.pop(game_state.selected_card_index)
        
        game_state.selected_product = None
        game_state.selected_recipient = None
        game_state.selected_card_index = None
        game_state.current_window = Window.MAIN
        end_turn()

def handle_card_click(index, pos):
    if game_state.is_animating:
        return

    card = game_state.field_cards[index]
    print(f"[DEBUG] handle_card_click: card={card.name}, type={card.card_type}, state={card.state}")

    if card.state == CardState.BACK:
        if not game_state.waiting_for_action and not game_state.has_revealed_card_this_turn:
            card.state = CardState.REVEALED
            
            if card.card_type == CardType.PRODUCT:
                card.buy_price = calculate_buy_price(card.name)
            elif card.card_type == CardType.NEGATIVE:
                apply_negative_effect(card.name)
            
            game_state.last_bought_card = None
            game_state.has_revealed_card_this_turn = True
            game_state.waiting_for_action = True
            game_state.current_open_card_index = index
            print(f"[DEBUG] Card {index} revealed: {card.name}")
            return

    if card.state == CardState.REVEALED and game_state.waiting_for_action and index == game_state.current_open_card_index:
        print(f"[DEBUG] Card is REVEALED, waiting for action")
        
        buy_rect = pygame.Rect(card.x + 16, card.y + 190, 95, 38)
        skip_rect = pygame.Rect(card.x + 129, card.y + 190, 95, 38)
        accept_rect = pygame.Rect(card.x + 60, card.y + 190, 120, 38)

        print(f"[DEBUG] Click pos: {pos}")
        print(f"[DEBUG] accept_rect: {accept_rect}")
        print(f"[DEBUG] accept_rect.collidepoint(pos): {accept_rect.collidepoint(pos)}")

        if card.card_type == CardType.PRODUCT:
            print(f"[DEBUG] Processing PRODUCT card")
            if buy_rect.collidepoint(pos):
                if len(game_state.inventory) < 8 and game_state.balance >= card.buy_price:
                    game_state.balance -= card.buy_price
                    new_card = CardData(
                        name=(card.name + '-инвентарь'),
                        card_type=card.card_type,
                        state=CardState.INVENTORY,
                        x=0, y=0,
                        buy_price=card.buy_price,
                        sell_price=calculate_sell_price(card.name + '-инвентарь'),
                        base_buy=card.base_buy,
                        base_sell=card.base_sell,
                        description=card.description
                    )
                    game_state.inventory.append(new_card)
                    game_state.last_bought_card = new_card
                    print(f"[DEBUG] Bought {card.name} for {card.buy_price}")
                
                game_state.waiting_for_action = False
                game_state.has_revealed_card_this_turn = False
                game_state.current_open_card_index = -1
                end_turn()
                return
                
            elif skip_rect.collidepoint(pos):
                print("[DEBUG] Skipped card")
                game_state.waiting_for_action = False
                game_state.has_revealed_card_this_turn = False
                game_state.current_open_card_index = -1
                end_turn()
                return
        
        else:
            print(f"[DEBUG] Processing NON-PRODUCT card (EVENT or NEGATIVE)")
            if accept_rect.collidepoint(pos):
                print(f"[DEBUG] Accept button clicked!")
                
                if card.card_type == CardType.EVENT:
                    print(f"[DEBUG] ===== ADDING EVENT: {card.name} =====")
                    print(f"[DEBUG] Card data: name={card.name}, duration={card.effect_duration}, effects={card.effects}")
                    print(f"[DEBUG] Current active_events: {game_state.active_events}")
                    
                    event_exists = False
                    for event in game_state.active_events:
                        if event.get("name") == card.name:
                            event["duration"] = card.effect_duration
                            event_exists = True
                            print(f"[DEBUG] Updated existing event: {card.name}")
                            break
                    
                    if not event_exists:
                        new_event = {
                            'name': card.name,
                            'duration': card.effect_duration,
                            'effects': card.effects.copy() if card.effects else {},
                            'risk_mod': card.risk_mod
                        }
                        game_state.active_events.append(new_event)
                        print(f"[DEBUG] ADDED NEW EVENT: {new_event}")
                        print(f"[DEBUG] active_events now: {game_state.active_events}")
                    else:
                        print(f"[DEBUG] Event already exists, updated duration")
                    
                elif card.card_type == CardType.NEGATIVE:
                    print(f"[DEBUG] Applying NEGATIVE: {card.name}")
                    apply_negative_effect(card.name)
                
                game_state.waiting_for_action = False
                game_state.has_revealed_card_this_turn = False
                game_state.current_open_card_index = -1
                end_turn()
                return
            else:
                print(f"[DEBUG] Accept button NOT clicked")

def handle_inventory_click(index):
    if game_state.waiting_for_action or game_state.is_animating or game_state.has_revealed_card_this_turn:
        return

    card = game_state.inventory[index]
    card.sell_price = calculate_sell_price(card.name)

    if game_state.lvl == 1:
        game_state.balance += card.sell_price
        game_state.inventory.pop(index)
        print(f"[DEBUG] Sold {card.name} for {card.sell_price}")
    else:
        game_state.selected_product = card
        game_state.selected_card_index = index
        show_region_selection()

def handle_click(pos):
    # ===== ГЛАВНОЕ МЕНЮ =====
    if game_state.current_window == Window.MENU:
        if 508 <= pos[0] <= 760 and 335 <= pos[1] <= 400:
            game_state.current_window = Window.LEVELS
            return
        if 508 <= pos[0] <= 760 and 420 <= pos[1] <= 485:
            game_state.previous_window = Window.MENU
            game_state.current_window = Window.RULES
            return
        if 508 <= pos[0] <= 760 and 505 <= pos[1] <= 570:
            game_state.running = False
            return
        return

    # ===== ВЫБОР УРОВНЯ =====
    if game_state.current_window == Window.LEVELS:
        if 345 <= pos[0] <= 640 and 325 <= pos[1] <= 387:
            print("[INFO] Starting Level 1...")
            game_state.lvl = 1
            game_state.target_sum = 1000
            restart_game()
            init_field_cards()
            update_prices()
            game_state.current_window = Window.MAIN
            return
        if 657 <= pos[0] <= 915 and 321 <= pos[1] <= 393:
            if game_state.is_pro:
                print("[INFO] Starting Level 2...")
                game_state.lvl = 2
                game_state.target_sum = 1500
                restart_game()
                init_field_cards()
                update_prices()
                game_state.current_window = Window.MAIN
            else:
                print("[WARN] Level 2 locked!")
            return
        if 511 <= pos[0] <= 765 and 426 <= pos[1] <= 500:
            game_state.current_window = Window.MENU
            return
        return

    # ===== ПАУЗА =====
    if game_state.current_window == Window.PAUSE:
        if 511 <= pos[0] <= 770 and 266 <= pos[1] <= 337:
            game_state.current_window = Window.MAIN
            return
        if 511 <= pos[0] <= 770 and 357 <= pos[1] <= 428:
            game_state.previous_window = Window.PAUSE  # <-- Запоминаем, что были в PAUSE
            game_state.current_window = Window.RULES
            return
        if 511 <= pos[0] <= 770 and 448 <= pos[1] <= 518:
            game_state.running = False
            return
        return

  
    # ===== ОСНОВНОЙ ЭКРАН =====
    if game_state.current_window == Window.MAIN:
        # Пауза
        if 25 <= pos[0] <= 65 and 15 <= pos[1] <= 55:
            game_state.current_window = Window.PAUSE
            return
        
        # Карты на поле
        for i, card in enumerate(game_state.field_cards):
            if pygame.Rect(card.x, card.y, card.width, card.height).collidepoint(pos):
                handle_card_click(i, pos)
                return
        
        # Инвентарь
        for i in range(len(game_state.inventory)):
            inv_rect = pygame.Rect(187 + i * 127, 673, 80, 10)
            if inv_rect.collidepoint(pos):
                handle_inventory_click(i)
                return
        
        # События/Календарь
        if pygame.Rect(515, 0, 250, 60).collidepoint(pos):
            game_state.current_window = Window.EVENTS
            return
        
        
        # Пропуск хода
        skip_rect = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 80, 130, 50)
        if skip_rect.collidepoint(pos):
            if not game_state.waiting_for_action and not game_state.has_revealed_card_this_turn and not game_state.is_animating:
                skip_turn()
            return

    # ===== ПРАВИЛА =====
    if game_state.current_window == Window.RULES:
        if 30 <= pos[0] <= 70 and 30 <= pos[1] <= 70:
            game_state.current_window = game_state.previous_window
            return
        return

    # ===== СОБЫТИЯ =====
    if game_state.current_window == Window.EVENTS:
        if 1200 <= pos[0] <= 1240 and 35 <= pos[1] <= 75:
            game_state.current_window = Window.MAIN
            return

    # ===== ВЫБОР РЕГИОНА =====
    if game_state.current_window == Window.SELL_REGIONS:
        # Кнопка-стрелочка назад (60, 70)
        if 60 <= pos[0] <= 110 and 70 <= pos[1] <= 120:  # 50x50 область для стрелки
            game_state.current_window = Window.MAIN
            game_state.selected_product = None
            game_state.selected_card_index = None
            return
        
        if 1200 <= pos[0] <= 1240 and 35 <= pos[1] <= 75:
            game_state.current_window = Window.MAIN
            game_state.selected_product = None
            game_state.selected_card_index = None
            return
        
        for button in game_state.region_buttons:
            if pygame.Rect(button.x, button.y, button.width, button.height).collidepoint(pos):
                game_state.selected_recipient = button.data
                game_state.current_window = Window.RECIPIENT
                return

    # ===== ПОДТВЕРЖДЕНИЕ ПРОДАЖИ =====
    if game_state.current_window == Window.RECIPIENT:
        if game_state.selected_product and game_state.selected_recipient:
            if SCREEN_WIDTH//2 - 200 <= pos[0] <= SCREEN_WIDTH//2 - 20 and SCREEN_HEIGHT//2 + 150 <= pos[1] <= SCREEN_HEIGHT//2 + 200:
                confirm_sell()
                return
            if SCREEN_WIDTH//2 + 20 <= pos[0] <= SCREEN_WIDTH//2 + 200 and SCREEN_HEIGHT//2 + 150 <= pos[1] <= SCREEN_HEIGHT//2 + 200:
                game_state.current_window = Window.SELL_REGIONS
                return

    # ===== КОНЕЦ ИГРЫ =====
    if game_state.current_window == Window.GAME_OVER:
        if SCREEN_WIDTH//2 - 300 <= pos[0] <= SCREEN_WIDTH//2 - 50 and SCREEN_HEIGHT//2 + 50 <= pos[1] <= SCREEN_HEIGHT//2 + 130:
            restart_game()
            game_state.current_window = Window.MENU
            return
        if SCREEN_WIDTH//2 + 50 <= pos[0] <= SCREEN_WIDTH//2 + 300 and SCREEN_HEIGHT//2 + 50 <= pos[1] <= SCREEN_HEIGHT//2 + 130:
            restart_game()
            init_field_cards()
            update_prices()
            game_state.current_window = Window.MAIN
            return