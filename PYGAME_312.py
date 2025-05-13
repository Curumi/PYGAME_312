import pygame
import random
import os
import sys

# --- Инициализация ---
pygame.init()
pygame.mixer.init()

# --- Настройки ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
BACKGROUND_COLOR = (30, 30, 30)
FPS = 60

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Пазл-игра")
clock = pygame.time.Clock()

# --- Загрузка шрифта и фона ---
try:
    custom_font = pygame.font.Font("fonts/TeletactileRus.ttf", 48)
    custom_small_font = pygame.font.Font("fonts/TeletactileRus.ttf", 32)
except:
    custom_font = pygame.font.SysFont('arial', 48)
    custom_small_font = pygame.font.SysFont('arial', 32)

background_image = pygame.image.load("assets/menu_background.jpg")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Загрузка жуткой музыки ---
try:
    pygame.mixer.music.load("assets/scary_music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except Exception as e:
    print("Не удалось загрузить музыку:", e)

# --- Глобальное состояние ---
player_name = ""
current_state = "splash"
game_started = False

# --- Кнопки ---
class Button:
    def __init__(self, text, pos, size=(300, 60)):
        self.text = text
        self.rect = pygame.Rect(pos, size)
        self.font = custom_small_font

    def draw(self, surface):
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- Экраны ---
def show_splash():
    screen.fill(BACKGROUND_COLOR)
    title = custom_font.render("Добро пожаловать в Пазл-игру!", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
    pygame.display.flip()
    pygame.time.wait(2000)
    return "menu"

def show_menu():
    global current_state
    buttons = [
        Button("Играть", (350, 300)),
        Button("Имя игрока", (350, 400)),
        Button("Выход", (350, 500))
    ]
    while current_state == "menu":
        screen.blit(background_image, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for i, button in enumerate(buttons):
                if button.is_clicked(event):
                    if i == 0:
                        return "game"
                    elif i == 1:
                        return "name"
                    elif i == 2:
                        pygame.quit()
                        sys.exit()

        for button in buttons:
            button.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

def name_input():
    global player_name, current_state
    input_box = pygame.Rect(300, 350, 400, 60)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive

    while current_state == "name":
        screen.fill((50, 50, 50))
        label = custom_font.render("Введите имя игрока:", True, (255, 255, 255))
        screen.blit(label, (300, 250))
        txt_surface = custom_small_font.render(player_name, True, color)
        width = max(400, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 15))
        pygame.draw.rect(screen, color, input_box, 2)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "menu"
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
                else:
                    if len(player_name) < 15:
                        player_name += event.unicode

        pygame.display.flip()
        clock.tick(FPS)

# --- Игровая логика ---
def run_game():
    global current_state

    ROWS, COLS = 5, 5
    MARGIN = 2
    SELECT_COLOR = (0, 255, 0)

    picture_folder = 'picture'
    pictures = [f for f in os.listdir(picture_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
    picture = random.choice(pictures)
    image = pygame.image.load(os.path.join(picture_folder, picture))
    image_width, image_height = image.get_size()
    TILE_WIDTH = image_width // COLS
    TILE_HEIGHT = image_height // ROWS

    tiles = []
    for i in range(ROWS):
        for j in range(COLS):
            rect = pygame.Rect(j * TILE_WIDTH, i * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT)
            tile = image.subsurface(rect)
            tiles.append(tile)

    origin_tiles = tiles.copy()
    random.shuffle(tiles)

    selected = None
    swaps = 0
    completed = False

    def draw_tiles():
        for i in range(len(tiles)):
            tile = tiles[i]
            row = i // ROWS
            col = i % COLS
            x = col * (TILE_WIDTH + MARGIN) + MARGIN
            y = row * (TILE_HEIGHT + MARGIN) + MARGIN
            screen.blit(tile, (x, y))
            if i == selected:
                pygame.draw.rect(screen, SELECT_COLOR, (x - 2, y - 2, TILE_WIDTH + 4, TILE_HEIGHT + 4), 3)

    def is_puzzle_completed():
        return all(tile == origin_tiles[i] for i, tile in enumerate(tiles))

    def draw_info():
        name_text = custom_small_font.render(f"Игрок: {player_name}", True, (255, 255, 255))
        swaps_text = custom_small_font.render(f"Ходы: {swaps}", True, (255, 255, 255))
        screen.blit(name_text, (20, SCREEN_HEIGHT - 80))
        screen.blit(swaps_text, (20, SCREEN_HEIGHT - 50))
        if completed:
            complete_text = custom_small_font.render("Пазл собран!", True, (0, 255, 0))
            screen.blit(complete_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT - 60))

    while current_state == "game":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not completed:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i in range(len(tiles)):
                    row = i // ROWS
                    col = i % COLS
                    x = col * (TILE_WIDTH + MARGIN) + MARGIN
                    y = row * (TILE_HEIGHT + MARGIN) + MARGIN
                    if x <= mouse_x <= x + TILE_WIDTH and y <= mouse_y <= y + TILE_HEIGHT:
                        if selected is not None and selected != i:
                            tiles[i], tiles[selected] = tiles[selected], tiles[i]
                            selected = None
                            swaps += 1
                            completed = is_puzzle_completed()
                        elif selected == i:
                            selected = None
                        else:
                            selected = i

        screen.fill(BACKGROUND_COLOR)
        draw_tiles()
        draw_info()
        pygame.display.flip()
        clock.tick(FPS)

# --- Основной цикл ---
while True:
    if current_state == "splash":
        current_state = show_splash()
    elif current_state == "menu":
        current_state = show_menu()
    elif current_state == "name":
        current_state = name_input()
    elif current_state == "game":
        current_state = run_game()
