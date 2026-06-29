import pygame
import os

class ImageManager:
    def __init__(self):
        self.backgrounds = {}
        self.card_images = {}
        self.card_cache = {}
        self.load_all_images()

    def load_image(self, filename, size=None):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_path = os.path.join(current_dir, 'assets', filename)
        
        paths = [
            assets_path,
            os.path.join('assets', filename),
            filename,
        ]
        
        for path in paths:
            try:
                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    if size:
                        img = pygame.transform.smoothscale(img, size)
                    return img
            except:
                continue
        
        print(f"[WARN] File not found: {filename}")
        return None

    def load_all_images(self):
        backgrounds = {
            'menu': 'background_main.png',
            'levels': 'background_levels.png',
            'defeat': 'background_defeat.png',
            'win': 'background_win.png',
            'pause': 'Background_pause.png',
            'events': 'bacground_active_events.png',
            'main': 'background_play.png',
            'rules': 'background_rules.png'
        }
        
        print("[INFO] Loading backgrounds...")
        for key, filename in backgrounds.items():
            self.backgrounds[key] = self.load_image(filename)
            if self.backgrounds[key]:
                print(f"[OK] Loaded: {filename}")
            else:
                print(f"[FAIL] Failed to load: {filename}")
        
        products = {
            "Пшеница": "card_product_wheat.png",
            "Рыба": "card_product_fish.png",
            "Уголь": "card_product_coal.png",
            "Шерсть": "card_product_wool.png",
            "Железо": "card_product_iron.png",
            "Вино": "card_product_wine.png",
            "Лекарства": "card_product_medicine.png",
            "Меха": "card_product_furs.png",
            "Специи": "card_product_spices.png",
            "Драгоценные камни": "card_product_precious_stones.png",
            "Пшеница-инвентарь": "card_product_wheat_inventory.png",
            "Рыба-инвентарь": "card_product_fish_inventory.png",
            "Уголь-инвентарь": "card_product_coal_inventory.png",
            "Шерсть-инвентарь": "card_product_wool_inventory.png",
            "Железо-инвентарь": "card_product_iron_inventory.png",
            "Вино-инвентарь": "card_product_wine_inventory.png",
            "Лекарства-инвентарь": "card_product_medicine_inventory.png",
            "Меха-инвентарь": "card_product_furs_inventory.png",
            "Специи-инвентарь": "card_product_spices_inventory.png",
            "Драгоценные камни-инвентарь": "card_product_precious_stones_inventory.png",
            "back": "card_product_back.png",
        }
        
        print("[INFO] Loading product cards...")
        for key, filename in products.items():
            self.card_images[key] = self.load_image(filename, (240, 180))
            if self.card_images[key]:
                print(f"[OK] Loaded: {filename}")
            else:
                print(f"[FAIL] Failed to load: {filename}")
        
        events = {
            "Война": "card_event_war.png",
            "Эпидемия": "card_service_epidemic.png",
            "Сухой закон": "card_service_prohibition.png",
            "Праздник": "card_service_holiday.png",
            "Шахтёрская забастовка": "card_service_miners_strike.png",
            "Разбойники": "card_negative_bandits.png",
            "Неудачное вложение": "card_negative_bad_investment.png"
        }
        
        print("[INFO] Loading event cards...")
        for key, filename in events.items():
            self.card_images[key] = self.load_image(filename, (240, 180))
            if self.card_images[key]:
                print(f"[OK] Loaded: {filename}")
            else:
                print(f"[FAIL] Failed to load: {filename}")
        
        # self.card_images['back'] = self.create_card_back()
        # print("[OK] Card back created")

    # def create_card_back(self):
    #     surf = pygame.Surface((240, 180))
    #     surf.fill((101, 67, 33))
    #     pygame.draw.rect(surf, (139, 69, 19), (5, 5, 230, 170), 2)
    #     pygame.draw.rect(surf, (139, 69, 19), (10, 10, 220, 160), 1)
    #     font = pygame.font.Font(None, 72)
    #     text = font.render("?", True, (210, 180, 140))
    #     text_rect = text.get_rect(center=(120, 90))
    #     surf.blit(text, text_rect)
    #     return surf

    def get_background(self, name):
        return self.backgrounds.get(name)

    def get_card_image(self, name, width=None, height=None, is_back=False):
        """Возвращает картинку карты с возможностью масштабирования"""
        if is_back:
            img = self.card_images.get('back')
        else:
            img = self.card_images.get(name)
        
        if img is None:
            return None
        
        # Если размер не указан, возвращаем оригинал
        if width is None or height is None:
            return img
        
        # Масштабируем с кэшированием
        width = int(width)
        height = int(height)
        cache_key = f"{name}_{width}_{height}"
        
        if cache_key in self.card_cache:
            return self.card_cache[cache_key]
        
        scaled_img = pygame.transform.smoothscale(img, (width, height))
        self.card_cache[cache_key] = scaled_img
        return scaled_img