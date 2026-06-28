import pygame
import sys
from game_config import *
from game_logic import *
from game_images import ImageManager
from game_render import init_render, draw_menu, draw_levels, draw_rules, draw_main, draw_pause, draw_game_over, draw_events_window, draw_sell_regions, draw_recipient_window
from game_animation import update_animation, init_field_cards
from game_handlers import handle_click
from game_state import game_state
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

pygame.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Merchant Simulator")
clock = pygame.time.Clock()

print("[INFO] Initializing ImageManager...")
image_manager = ImageManager()

# Инициализация рендера
init_render(SCREEN, image_manager)

# Инициализация карт
init_field_cards() 
update_prices()

print("[INFO] Starting game loop...")
while game_state.running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_state.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle_click(event.pos)
    
    # Обновление анимаций
    update_animation()
    
    # Отрисовка текущего окна
    if game_state.current_window == Window.MENU:
        draw_menu()
    elif game_state.current_window == Window.LEVELS:
        draw_levels()
    elif game_state.current_window == Window.RULES:
        draw_rules()
    elif game_state.current_window == Window.MAIN:
        draw_main()
    elif game_state.current_window == Window.PAUSE:
        draw_pause()
    elif game_state.current_window == Window.EVENTS:
        draw_events_window()
    elif game_state.current_window == Window.GAME_OVER:
        draw_game_over()
    elif game_state.current_window == Window.SELL_REGIONS:
        draw_sell_regions()
    elif game_state.current_window == Window.RECIPIENT:
        draw_recipient_window()
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
print("[INFO] Game closed")