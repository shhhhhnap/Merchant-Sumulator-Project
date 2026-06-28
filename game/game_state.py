from game_config import Window, Season, CardState, CardType
from game_structures import CardData, RecipientData, ButtonData

class GameState:
    """Централизованное состояние всей игры"""
    
    def __init__(self):
        # Окна и UI
        self.current_window = Window.MENU
        self.previous_window = Window.MENU
        self.running = True
        
        # Игровые параметры
        self.lvl = 1
        self.is_pro = True
        self.balance = 300
        self.target_sum = 1000
        self.step = 1
        self.season = Season.SUMMER
        
        # Игровые объекты
        self.inventory = []
        self.sent_products = []
        self.active_events = []
        self.field_cards = []
        self.new_field_cards = []
        self.last_bought_card = None
        
        # Состояния хода
        self.waiting_for_action = False
        self.has_revealed_card_this_turn = False
        self.current_open_card_index = -1
        
        # Анимация
        self.is_animating = False
        self.animation_progress = 0
        
        # Выбранные объекты для продажи
        self.selected_product = None
        self.selected_recipient = None
        self.selected_card_index = None
        self.region_buttons = []
        
        # Регионы для текущего хода (НОВЫЕ ПОЛЯ)
        self.regions_generated = False
        self.saved_region_buttons = []

# Создаем единственный экземпляр состояния
game_state = GameState()