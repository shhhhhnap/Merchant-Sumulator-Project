import pygame
from game_config import COLORS, SCREEN_WIDTH, SCREEN_HEIGHT, CardState, CardType
from game_structures import CardData
from game_logic import field_cards, new_field_cards, inventory, active_events
from game_logic import balance, target_sum, season, step

# Глобальные переменные (будут установлены из main.py)
font_big = None
font_medium = None
font_small = None
screen = None
close_button = None
rules_back_button = None

def draw_button(button):
    pygame.draw.rect(screen, button.color, (button.x, button.y, button.width, button.height))
    pygame.draw.rect(screen, COLORS['dark_brown'], (button.x, button.y, button.width, button.height), 2)
    text_surface = font_medium.render(button.text, True, button.text_color)
    text_rect = text_surface.get_rect(center=(button.x + button.width//2, button.y + button.height//2))
    screen.blit(text_surface, text_rect)

def draw_card(card, show_price=True, is_open_card=False):
    if card.state == CardState.BACK:
        pygame.draw.rect(screen, COLORS['brown'], (card.x, card.y, card.width, card.height))
        pygame.draw.rect(screen, COLORS['beige'], (card.x + 5, card.y + 5, card.width - 10, card.height - 10))
        center_x = card.x + card.width // 2
        center_y = card.y + card.height // 2
        pygame.draw.circle(screen, COLORS['brown'], (center_x, center_y), 40)
        pygame.draw.circle(screen, COLORS['beige'], (center_x, center_y), 30)
        question = font_medium.render("?", True, COLORS['brown'])
        question_rect = question.get_rect(center=(center_x, center_y))
        screen.blit(question, question_rect)
    else:
        pygame.draw.rect(screen, COLORS['beige'], (card.x, card.y, card.width, card.height))
        pygame.draw.rect(screen, COLORS['dark_brown'], (card.x, card.y, card.width, card.height), 3)
        
        img_rect = pygame.Rect(card.x + 10, card.y + 10, card.width - 20, 160)
        pygame.draw.rect(screen, COLORS['white'], img_rect)
        pygame.draw.rect(screen, COLORS['dark_brown'], img_rect, 2)
        
        name_surface = font_medium.render(card.name, True, COLORS['dark_brown'])
        name_rect = name_surface.get_rect(center=(card.x + card.width//2, card.y + 190))
        screen.blit(name_surface, name_rect)
        
        if show_price and card.card_type == CardType.PRODUCT and card.state == CardState.REVEALED:
            price_text = f"Цена: {int(card.buy_price)}"
            price_surface = font_small.render(price_text, True, COLORS['brown'])
            price_rect = price_surface.get_rect(center=(card.x + card.width//2, card.y + 220))
            screen.blit(price_surface, price_rect)
            
            pygame.draw.rect(screen, COLORS['button_brown'], (card.x + 16, card.y + 290, 95, 38))
            pygame.draw.rect(screen, COLORS['dark_brown'], (card.x + 16, card.y + 290, 95, 38), 2)
            buy_text = font_small.render("Купить", True, COLORS['beige'])
            buy_rect = buy_text.get_rect(center=(card.x + 16 + 47, card.y + 309))
            screen.blit(buy_text, buy_rect)
            
            pygame.draw.rect(screen, COLORS['red'], (card.x + 129, card.y + 290, 95, 38))
            pygame.draw.rect(screen, COLORS['dark_brown'], (card.x + 129, card.y + 290, 95, 38), 2)
            skip_text = font_small.render("Отказ", True, COLORS['beige'])
            skip_rect = skip_text.get_rect(center=(card.x + 129 + 47, card.y + 309))
            screen.blit(skip_text, skip_rect)
            
        elif card.card_type != CardType.PRODUCT and card.state == CardState.REVEALED:
            desc_lines = card.description.split('\n')
            for i, line in enumerate(desc_lines[:2]):
                desc_surface = font_small.render(line[:25], True, COLORS['black'])
                screen.blit(desc_surface, (card.x + 15, card.y + 220 + i * 25))
            
            pygame.draw.rect(screen, COLORS['button_brown'], (card.x + 16, card.y + 307, 208, 38))
            pygame.draw.rect(screen, COLORS['dark_brown'], (card.x + 16, card.y + 307, 208, 38), 2)
            action_text = font_small.render("Принять", True, COLORS['beige'])
            action_rect = action_text.get_rect(center=(card.x + card.width//2, card.y + 326))
            screen.blit(action_text, action_rect)
        
        elif show_price and card.card_type == CardType.PRODUCT and card.state == CardState.INVENTORY:
            price_text = f"Цена: {int(card.sell_price)}"
            price_surface = font_small.render(price_text, True, COLORS['green'])
            price_rect = price_surface.get_rect(center=(card.x + card.width//2, card.y + 220))
            screen.blit(price_surface, price_rect)

def draw_recipient(recip):
    pygame.draw.rect(screen, COLORS['beige'], (recip.x, recip.y, recip.width, recip.height))
    pygame.draw.rect(screen, COLORS['dark_brown'], (recip.x, recip.y, recip.width, recip.height), 2)
    
    img_rect = pygame.Rect(recip.x + 25, recip.y + 20, recip.width - 50, 100)
    pygame.draw.rect(screen, COLORS['white'], img_rect)
    pygame.draw.rect(screen, COLORS['dark_brown'], img_rect, 1)
    
    name_surface = font_medium.render(recip.name, True, COLORS['dark_brown'])
    name_rect = name_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 150))
    screen.blit(name_surface, name_rect)
    
    info_surface = font_small.render(f"Доставка: {recip.distance} ходов", True, COLORS['black'])
    info_rect = info_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 200))
    screen.blit(info_surface, info_rect)
    
    risk = min(0.95, 0.05 + recip.distance * 0.03)
    risk_surface = font_small.render(f"Риск: {int(risk * 100)}%", True, COLORS['red'])
    risk_rect = risk_surface.get_rect(center=(recip.x + recip.width//2, recip.y + 230))
    screen.blit(risk_surface, risk_rect)