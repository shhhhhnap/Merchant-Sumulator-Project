from game_config import CARD_POSITIONS, CARD_POSITIONS_OFFSCREEN_RIGHT, CARD_POSITIONS_OFFSCREEN_LEFT, CardState, ANIMATION_SPEED
from game_structures import CardData
from game_logic import generate_random_card
from game_state import game_state

def init_field_cards():
    game_state.field_cards = []
    for x, y in CARD_POSITIONS:
        card_data = generate_random_card()
        card = CardData(
            name=card_data['name'],
            card_type=card_data['type'],
            state=CardState.BACK,
            x=x, y=y,
            buy_price=card_data.get('buy_price', 0),
            sell_price=card_data.get('sell_price', 0),
            base_buy=card_data.get('base_buy', 0),
            base_sell=card_data.get('base_sell', 0),
            description=card_data.get('desc', ''),
            effect_duration=card_data.get('duration', 0),
            effects=card_data.get('effects', {}),
            risk_mod=card_data.get('risk_mod', 0)
        )
        card.target_x = x
        card.velocity_x = 0
        game_state.field_cards.append(card)

def init_new_field_cards():
    game_state.new_field_cards = []
    for i, (x, y) in enumerate(CARD_POSITIONS_OFFSCREEN_LEFT):
        card_data = generate_random_card()
        card = CardData(
            name=card_data['name'],
            card_type=card_data['type'],
            state=CardState.BACK,
            x=x, y=y,
            buy_price=card_data.get('buy_price', 0),
            sell_price=card_data.get('sell_price', 0),
            base_buy=card_data.get('base_buy', 0),
            base_sell=card_data.get('base_sell', 0),
            description=card_data.get('desc', ''),
            effect_duration=card_data.get('duration', 0),
            effects=card_data.get('effects', {}),
            risk_mod=card_data.get('risk_mod', 0)
        )
        card.target_x = CARD_POSITIONS[i][0]
        card.velocity_x = 0
        game_state.new_field_cards.append(card)

def start_animation():
    game_state.is_animating = True
    game_state.animation_progress = 0

    # Старые карты улетают вправо
    for i, card in enumerate(game_state.field_cards):
        card.target_x = CARD_POSITIONS_OFFSCREEN_RIGHT[i][0]
        card.velocity_x = ANIMATION_SPEED

    # Новые карты готовятся слева
    init_new_field_cards()
    for card in game_state.new_field_cards:
        card.velocity_x = ANIMATION_SPEED

def update_animation():
    if not game_state.is_animating:
        return

    game_state.animation_progress += 1
    all_complete = True

    # Двигаем старые карты
    for card in game_state.field_cards:
        if abs(card.x - card.target_x) > card.velocity_x:
            if card.x < card.target_x:
                card.x += card.velocity_x
            else:
                card.x -= card.velocity_x
            all_complete = False
        else:
            card.x = card.target_x

    # Двигаем новые карты
    for card in game_state.new_field_cards:
        if abs(card.x - card.target_x) > card.velocity_x:
            if card.x < card.target_x:
                card.x += card.velocity_x
            else:
                card.x -= card.velocity_x
            all_complete = False
        else:
            card.x = card.target_x

    if all_complete:
        game_state.field_cards = game_state.new_field_cards
        game_state.new_field_cards = []
        game_state.is_animating = False