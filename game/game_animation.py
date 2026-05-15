from game_config import CARD_POSITIONS, CARD_POSITIONS_OFFSCREEN_RIGHT
from game_structures import CardData
from game_logic import field_cards, new_field_cards, generate_random_card
from game_logic import is_animating, animation_progress, animation_speed

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

from game_config import CardState