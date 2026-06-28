import pygame
from game_config import *
from game_logic import *
from game_structures import ButtonData
from game_state import game_state

font_big = None
font_medium = None
font_small = None
screen = None
image_manager = None


def init_render(screen_obj, img_manager):
    global screen, image_manager, font_big, font_medium, font_small
    
    screen = screen_obj
    image_manager = img_manager
    
    # Загружаем шрифты из файлов
    try:
        font_path = 'game/assets/fonts/diarysecrets.ttf'
        font_big = pygame.font.Font(font_path, 48)
        font_medium = pygame.font.Font(font_path, 32)
        font_small = pygame.font.Font(font_path, 24)
    except:
        # Если шрифт не найден, используем системный
        font_big = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)

def draw_card(card):
    if card.state == CardState.BACK:
        img = image_manager.get_card_image('back', is_back=True)
    else:
        img = image_manager.get_card_image(card.name)
    
    if img:
        img_scaled = pygame.transform.smoothscale(img, (card.width, card.height))
        screen.blit(img_scaled, (card.x, card.y))
        
        if card.state == CardState.REVEALED and card.card_type == CardType.PRODUCT:
            price_txt = font_medium.render(f"{card.buy_price}", True, COLORS['dark_brown'])
            screen.blit(price_txt, (card.x + 15, card.y + 10))
            
        if card.state == CardState.INVENTORY and card.card_type == CardType.PRODUCT:
            price_txt = font_medium.render(f"{card.sell_price}", True, COLORS['dark_brown'])
            screen.blit(price_txt, (card.x + 15, card.y + 10))

def draw_recipient(recip):
    # Рисуем фон карточки
    pygame.draw.rect(screen, COLORS['white'], (recip.x, recip.y, recip.width, recip.height))
    pygame.draw.rect(screen, COLORS['dark_brown'], (recip.x, recip.y, recip.width, recip.height), 2)
    
    # Внутренняя рамка (меньше)
    pygame.draw.rect(screen, COLORS['dark_brown'], (recip.x + 10, recip.y + 10, recip.width - 20, 70), 1)
    
    # Иконка региона (меньше)
    font_icon = pygame.font.Font(None, 48)  # Уменьшил с 72 до 48
    icon = recip.name[0] if recip.name else "?"
    icon_surf = font_icon.render(icon, True, COLORS['dark_brown'])
    icon_rect = icon_surf.get_rect(center=(recip.x + recip.width//2, recip.y + 50))
    screen.blit(icon_surf, icon_rect)
    
    # Название региона (меньше)
    name_surface = font_small.render(recip.name, True, COLORS['dark_brown'])  # Используем small вместо medium
    name_rect = name_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 110))
    screen.blit(name_surface, name_rect)

    # Информация о доставке
    info_surface = font_small.render(f"Доставка: {recip.distance} ходов", True, COLORS['black'])
    info_rect = info_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 155))
    screen.blit(info_surface, info_rect)

    # Риск
    risk = min(0.95, 0.05 + recip.distance * 0.03)
    risk_color = COLORS['red'] if risk > 0.5 else COLORS['green']
    risk_surface = font_small.render(f"Риск: {int(risk * 100)}%", True, risk_color)
    risk_rect = risk_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 185))
    screen.blit(risk_surface, risk_rect)
    
    # Кнопка выбора (меньше)
    select_rect = pygame.Rect(recip.x + 20, recip.y + 215, recip.width - 40, 28)
    pygame.draw.rect(screen, COLORS['button_brown'], select_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], select_rect, 2)
    select_text = font_small.render("Выбрать", True, COLORS['white'])
    select_text_rect = select_text.get_rect(center=(select_rect.centerx, select_rect.centery))
    screen.blit(select_text, select_text_rect)
    
def draw_background(bg_type):
    bg = image_manager.get_background(bg_type)
    if bg:
        screen.blit(pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))
    else:
        screen.fill(COLORS['beige'])

def draw_rules():
    draw_background('rules')

def draw_menu():
    draw_background('menu')

def draw_levels():
    draw_background('levels')

def center_text(text, font, color, rect):
        surf = font.render(text, True, color)
        screen.blit(surf, surf.get_rect(center=rect.center))

def draw_main():
    draw_background('main')
    
    # Баланс и цель
    info_rect = pygame.Rect(515, 0, 250, 60)
    balance_rect = pygame.Rect(960, 0, 320, 60)
    
    money_rect = pygame.Rect(balance_rect.x, balance_rect.y, balance_rect.width, 30)
    center_text(f"Баланс: {int(game_state.balance)} зол.", font_medium, COLORS['dark_brown'], money_rect)
    target_rect = pygame.Rect(balance_rect.x, balance_rect.y + 30, balance_rect.width, 30)
    center_text(f"Цель: {game_state.target_sum}", font_medium, COLORS['dark_brown'], target_rect)
    season_rect = pygame.Rect(info_rect.x, info_rect.y, info_rect.width, 30)
    center_text(f"Сезон: {game_state.season.value}", font_medium, COLORS['dark_brown'], season_rect)
    step_rect = pygame.Rect(info_rect.x, info_rect.y + 30, info_rect.width, 30)
    center_text(f"Ход: {game_state.step}/32", font_small, COLORS['dark_brown'], step_rect)
    
    # Активные события
    # if game_state.active_events:
    #     for i, event in enumerate(game_state.active_events[:2]):
    #         event_text = font_small.render(f"{event['name']}: {event['duration']} ходов", True, COLORS['black'])
    #         screen.blit(event_text, (590, 160 + i * 20))

    # Карты на поле
    for card in game_state.field_cards:
        draw_card(card)

    # ===== ИНВЕНТАРЬ (РИСУЕМ КАРТЫ ПОВЕРХ ФОНА) =====
    inventory_positions = [
        (182, 552), (309, 552), (436, 552), (563, 552),
        (690, 552), (817, 552), (945, 552), (1072, 552)
    ]
    
    for i, card in enumerate(game_state.inventory):
        if i >= len(inventory_positions):
            break
            
        x, y = inventory_positions[i]
        
        # Рисуем карту в инвентаре
        img = image_manager.get_card_image(card.name, width=90, height=138)
        
        if img:
            screen.blit(img, (x, y))
        else:
            pygame.draw.rect(screen, COLORS['white'], (x, y, 70, 100))
            pygame.draw.rect(screen, COLORS['dark_brown'], (x, y, 70, 100), 2)
            font_icon = pygame.font.Font(None, 40)
            icon = card.name[0] if card.name else "?"
            icon_surf = font_icon.render(icon, True, COLORS['dark_brown'])
            icon_rect = icon_surf.get_rect(center=(x + 35, y + 50))
            screen.blit(icon_surf, icon_rect)

    # Кнопка пропуска хода
    skip_rect = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 70, 90, 50)
    pygame.draw.rect(screen, COLORS['button_brown'], skip_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], skip_rect, 2)
    skip_text = font_small.render("Пропуск", True, COLORS['white'])
    skip_text_rect = skip_text.get_rect(center=(skip_rect.centerx, skip_rect.centery))
    screen.blit(skip_text, skip_text_rect)

def draw_pause():
    draw_background('pause')

def draw_game_over():
    if game_state.balance <= 0:
        draw_background('defeat')
    else:
        draw_background('win')

def decline_hod(count):
    """Простая функция склонения без внешних библиотек"""
    try:
        count = int(count)
        if count % 100 in (11, 12, 13, 14):
            return f"{count} ходов"
        elif count % 10 == 1:
            return f"{count} ход"
        elif count % 10 in (2, 3, 4):
            return f"{count} хода"
        else:
            return f"{count} ходов"
    except (ValueError, TypeError):
        return f"{count} ходов"

def draw_events_window():
    draw_background('events')
    
    def center_text(text, font, color, y):
        surf = font.render(text, True, color)
        text_rect = surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        screen.blit(surf, text_rect)
    
    if game_state.active_events:
        y = 250
        for event in game_state.active_events:
            name = event.get('name', 'Событие')
            duration = event.get('duration', 0)
            effects = event.get('effects', {})
            
            # Формируем текст с эффектами
            effects_text = ""
            if effects:
                effect_parts = []
                for k, v in effects.items():
                    if v > 0:
                        effect_parts.append(f"{k}: +{v}%")
                    else:
                        effect_parts.append(f"{k}: {v}%")
                if effect_parts:
                    effects_text = f" ({', '.join(effect_parts)})"
            
            hod_text = decline_hod(duration)
            full_text = f"{name} - {hod_text}{effects_text}"
            
            center_text(full_text, font_medium, COLORS['dark_brown'], y)
            y += 50
    else:
        center_text("Нет активных событий", font_medium, COLORS['dark_brown'], 300)

def draw_sell_regions():
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(200)
    overlay.fill(COLORS['beige'])
    screen.blit(overlay, (0, 0))
    
    # ===== СТРЕЛОЧКА НАЗАД (60, 70) =====
    arrow_x = 60
    arrow_y = 70
    
    # Рисуем круглую кнопку
    pygame.draw.circle(screen, COLORS['dark_brown'], (arrow_x, arrow_y), 30)
    pygame.draw.circle(screen, COLORS['beige'], (arrow_x, arrow_y), 27)
    pygame.draw.circle(screen, COLORS['dark_brown'], (arrow_x, arrow_y), 27, 2)
    
    # Рисуем стрелку влево (отцентрирована внутри круга)
    arrow_size = 12
    arrow_points = [
        (arrow_x + arrow_size - 5, arrow_y - 10),  # Верхняя точка (сдвинута влево на 5)
        (arrow_x - arrow_size + 2 - 5, arrow_y),    # Острие стрелы (сдвинуто влево на 5)
        (arrow_x + arrow_size - 5, arrow_y + 10),   # Нижняя точка (сдвинута влево на 5)
    ]
    pygame.draw.polygon(screen, COLORS['dark_brown'], arrow_points)
    
    # Подпись "Назад" под стрелкой
    back_text = font_small.render("Назад", True, COLORS['dark_brown'])
    back_rect = back_text.get_rect(center=(arrow_x, arrow_y + 50))
    screen.blit(back_text, back_rect)
    
    # ===== ЗАГОЛОВОК =====
    title = font_big.render("Выберите регион для продажи", True, COLORS['dark_brown'])
    title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 50))
    screen.blit(title, title_rect)

    if game_state.selected_product:
        product_text = font_medium.render(f"Товар: {game_state.selected_product.name}", True, COLORS['dark_brown'])
        product_rect = product_text.get_rect(center=(SCREEN_WIDTH//2, 110))
        screen.blit(product_text, product_rect)

    for button in game_state.region_buttons:
        draw_recipient(button.data)

def draw_recipient_window():
    if game_state.selected_product and game_state.selected_recipient:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS['dark_brown'])
        screen.blit(overlay, (0, 0))
        
        window_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 200, 500, 400)
        pygame.draw.rect(screen, COLORS['beige'], window_rect)
        pygame.draw.rect(screen, COLORS['beige'], window_rect, 3)
        
        title = font_big.render("Подтверждение продажи", True, COLORS['dark_brown'])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 150))
        screen.blit(title, title_rect)
        
        product_text = font_medium.render(f"Товар: {game_state.selected_product.name}", True, COLORS['dark_brown'])
        product_rect = product_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 70))
        screen.blit(product_text, product_rect)
        
        region_text = font_medium.render(f"Регион: {game_state.selected_recipient.region}", True, COLORS['dark_brown'])
        region_rect = region_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30))
        screen.blit(region_text, region_rect)
        
        distance_text = font_small.render(f"Доставка: {game_state.selected_recipient.distance} ходов", True, COLORS['black'])
        distance_rect = distance_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        screen.blit(distance_text, distance_rect)
        
        risk = min(0.95, 0.05 + game_state.selected_recipient.distance * 0.03)
        for event in game_state.active_events:
            risk += event.get('risk_mod', 0) / 100
        risk = min(0.95, risk)
        
        risk_text = font_small.render(f"Риск потери: {int(risk * 100)}%", True, COLORS['red'])
        risk_rect = risk_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
        screen.blit(risk_text, risk_rect)
        
        sell_price = calculate_sell_price(game_state.selected_product.name, game_state.selected_recipient.region)
        price_text = font_medium.render(f"Цена продажи: {int(sell_price)} золотых", True, COLORS['green'])
        price_rect = price_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90))
        screen.blit(price_text, price_rect)
        
        sell_button_rect = pygame.Rect(SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 150, 180, 50)
        pygame.draw.rect(screen, COLORS['button_brown'], sell_button_rect)
        pygame.draw.rect(screen, COLORS['dark_brown'], sell_button_rect, 2)
        sell_text = font_medium.render("Продать", True, COLORS['white'])
        sell_text_rect = sell_text.get_rect(center=(SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT//2 + 175))
        screen.blit(sell_text, sell_text_rect)
        
        back_button_rect = pygame.Rect(SCREEN_WIDTH//2 + 20, SCREEN_HEIGHT//2 + 150, 180, 50)
        pygame.draw.rect(screen, COLORS['dark_beige'], back_button_rect)
        pygame.draw.rect(screen, COLORS['dark_brown'], back_button_rect, 2)
        back_text = font_medium.render("Вернуться", True, COLORS['black'])
        back_text_rect = back_text.get_rect(center=(SCREEN_WIDTH//2 + 110, SCREEN_HEIGHT//2 + 175))
        screen.blit(back_text, back_text_rect)