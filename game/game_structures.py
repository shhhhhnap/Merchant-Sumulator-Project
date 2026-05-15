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