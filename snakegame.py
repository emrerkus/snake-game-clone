import random
import json
import pygame
import os

pygame.init()
pygame.mixer.init()
channel = pygame.mixer.find_channel()
eat_sound = pygame.mixer.Sound("assets/eating_apple.mp3")
eat_sound.set_volume(0.7)
death_sound = pygame.mixer.Sound("assets/ugly-plankton.mp3")
bg_sound = pygame.mixer.Sound("assets/background_music.mp3")
bg_sound.set_volume(0.1)
bg_sound.play(-1)

running = True
restart = False
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 580
GRID_SIZE = 20
CELL_SIZE = 25
CELL_SPACING = 4
GAME_WIDTH = GAME_HEIGHT = GRID_SIZE * CELL_SIZE + (GRID_SIZE - 1) * CELL_SPACING + 4
POSSIBLE_DIRECTIONS = ["right", "left", "up", "down"]
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (204, 0, 204)
YELLOW = (230, 230, 0)

status = None
key_press_count = 0
ok_to_go = False
hue = 0
brightness = 100
is_paused = False
clock = pygame.time.Clock()
snake = [[10, 10], [10, 9], [10, 8]]
apple_x, apple_y = 0, 0
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")
direction = None
last_move_time = pygame.time.get_ticks()
produce_apple = True
speed = 150
apple_point = 10
apple_color = RED
stat_font_size = 18
text_font_size = 15
stat_font = pygame.font.Font("assets/Minecraft.ttf", 24)
paused_font = pygame.font.Font("assets/Minecraft.ttf", 48)
statistic_font = pygame.font.Font("assets/Minecraft.ttf", 28)
score = 0
snake_length = len(snake)
difficulty_table = {
    "Easy": 1,
    "Moderate": 1.2,
    "Hard": 1.5,
    "Expert": 2,
    "Impossible": 5
}
difficulty = difficulty_table["Easy"]


def load_highscore():
    if os.path.exists("db.json"):
        with open("db.json", "r") as f:
            data = json.load(f)
            return data.get("high_score")
    return 0


highscore = load_highscore()


def save_highscore():
    global highscore
    if score > highscore:
        with open("db.json", "w") as f:
            return json.dump({"high_score": score}, f, indent=4)


def check_boundaries():
    global snake, restart
    if snake[0][0] < 0 or snake[0][0] > 19:
        save_highscore()
        restart = True
    if snake[0][1] < 0 or snake[0][1] > 19:
        save_highscore()
        restart = True
    return True


def apple_coordinates():
    a_x = random.randint(0, 19)
    a_y = random.randint(0, 19)
    return a_x, a_y


def move_snake_regularly(d):
    global last_move_time, running
    current_time = pygame.time.get_ticks()
    if current_time - last_move_time >= speed:
        if not move_snake(d):
            restart_game()
        last_move_time = current_time


def move_snake(d):
    global snake, restart, ok_to_go
    head = None
    if d == "right":
        head = [snake[0][0] + 1, snake[0][1]]
    if d == "left":
        head = [snake[0][0] - 1, snake[0][1]]
    if d == "up":
        head = [snake[0][0], snake[0][1] - 1]
    if d == "down":
        head = [snake[0][0], snake[0][1] + 1]
    snake = [head] + snake[:-1]
    if snake[0] in snake[1:]:
        save_highscore()
        ok_to_go = False
        return False
    return True


def draw_snake():
    global snake
    for i in range(len(snake)):
        snake_x = snake[i][0] * (CELL_SIZE + CELL_SPACING) + 2
        snake_y = snake[i][1] * (CELL_SIZE + CELL_SPACING) + 2
        if check_boundaries():
            pygame.draw.rect(screen, (255, 255, 255), (snake_x, snake_y, CELL_SIZE, CELL_SIZE))


def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * (CELL_SIZE + CELL_SPACING) + 2
            y = row * (CELL_SIZE + CELL_SPACING) + 2
            pygame.draw.rect(screen, (64, 64, 64), (x, y, CELL_SIZE, CELL_SIZE))
            if row == 0 and col == 0:
                pygame.draw.rect(screen, apple_color, (col, row, 2, GAME_HEIGHT))
                pygame.draw.rect(screen, apple_color, (col, row, GAME_WIDTH, 2))
            if row == GRID_SIZE - 1 and col == 0:
                y = row * (CELL_SIZE + CELL_SPACING) + 2
                pygame.draw.rect(screen, apple_color, (col, y + CELL_SIZE, GAME_WIDTH, 2))
            if col == GRID_SIZE - 1 and row == 0:
                x = col * (CELL_SIZE + CELL_SPACING) + 2
                pygame.draw.rect(screen, apple_color, (x + CELL_SIZE, row, 2, GAME_HEIGHT))


def draw_apple():
    global produce_apple, apple_x, apple_y, apple_color, hue, brightness
    apple_color_impossible = pygame.Color(0)
    apple_color_impossible.hsva = (hue, 100, 100, 100)
    apple_color_expert = pygame.Color(0)
    apple_color_expert.hsva = (280, 100, brightness, 100)
    if produce_apple:
        apple_x, apple_y = apple_coordinates()
        produce_apple = False
    if update_difficulty() == "EASY":
        apple_color = RED
    elif update_difficulty() == "MODERATE":
        apple_color = GREEN
    elif update_difficulty() == "HARD":
        apple_color = BLUE
    elif update_difficulty() == "EXPERT":
        color_speed = 1
        apple_color = apple_color_expert
        brightness += color_speed
        if brightness >= 100:
            brightness = 50
    elif update_difficulty() == "IMPOSSIBLE":
        color_speed = 5
        apple_color = apple_color_impossible
        hue += color_speed
        if hue >= 360:
            hue = 0

    pygame.draw.rect(screen, apple_color,
                     (apple_x * (CELL_SIZE + CELL_SPACING) + 2, apple_y * (CELL_SIZE + CELL_SPACING) + 2,
                      CELL_SIZE, CELL_SIZE))


def is_eaten():
    global produce_apple, speed, score, snake_length
    if (snake[0][0], snake[0][1]) == (apple_x, apple_y):
        eat_sound.play()
        produce_apple = True
        if speed >= 2.5:
            speed -= 2.5
        score += int(apple_point * difficulty)
        snake_length += 1
        return True, snake[len(snake)-1]
    return False, snake[len(snake)-1]


def update_difficulty():
    global difficulty, difficulty_table, speed
    if 3 <= snake_length < 13:
        difficulty = difficulty_table["Easy"]
        return "EASY"
    elif 13 <= snake_length < 23:
        difficulty = difficulty_table["Moderate"]
        return "MODERATE"
    elif 23 <= snake_length < 33:
        difficulty = difficulty_table["Hard"]
        return "HARD"
    elif 33 <= snake_length < 43:
        difficulty = difficulty_table["Expert"]
        return "EXPERT"
    elif 43 <= snake_length:
        difficulty = difficulty_table["Impossible"]
        return "IMPOSSIBLE"
    return None


def calculate_spacing(text, font_size):
    stat_width = SCREEN_WIDTH - GAME_WIDTH
    text_len = len(text)
    spacing = (stat_width - text_len * font_size) // 2
    return spacing


def update_stats():
    global score, snake_length, highscore

    color_white = (255, 255, 255)

    score_spacing = calculate_spacing(str(score), stat_font_size)
    highscore_spacing = calculate_spacing(str(highscore), stat_font_size)
    length_spacing = calculate_spacing(str(snake_length), stat_font_size)
    difficulty_spacing = calculate_spacing(update_difficulty(), stat_font_size)

    txt_score_spacing = calculate_spacing("Score", text_font_size)
    txt_highscore_spacing = calculate_spacing("        ", text_font_size)
    txt_length_spacing = calculate_spacing("SnakeLength", text_font_size)
    txt_difficulty_spacing = calculate_spacing("       ", text_font_size)

    stat_title = stat_font.render("Game Stats", True, color_white)
    highscore_text = stat_font.render("HighScore", True, color_white)
    score_text = stat_font.render("Score", True, color_white)
    length_text = stat_font.render("Snake Length", True, color_white)
    difficulty_text = stat_font.render("Difficulty", True, color_white)

    highscore_stat = statistic_font.render(str(highscore), True, YELLOW)
    score_stat = statistic_font.render(str(score), True, YELLOW)
    length_stat = statistic_font.render(str(snake_length), True, YELLOW)
    difficulty_stat = statistic_font.render(update_difficulty(), True, YELLOW)

    mark_stat1 = stat_font.render("Made by", True, (204, 0, 102))
    mark_stat2 = stat_font.render("Emre Erkus", True, (204, 0, 102))

    screen.blit(stat_title, (GAME_WIDTH + 40, 40))
    screen.blit(highscore_text, (GAME_WIDTH + txt_highscore_spacing, 120))
    screen.blit(highscore_stat, (GAME_WIDTH + highscore_spacing, 150))
    screen.blit(score_text, (GAME_WIDTH + txt_score_spacing, 200))
    screen.blit(score_stat, (GAME_WIDTH + score_spacing, 230))
    screen.blit(length_text, (GAME_WIDTH + txt_length_spacing, 280))
    screen.blit(length_stat, (GAME_WIDTH + length_spacing, 310))
    screen.blit(difficulty_text, (GAME_WIDTH + txt_difficulty_spacing, 360))
    screen.blit(difficulty_stat, (GAME_WIDTH + difficulty_spacing, 390))
    screen.blit(mark_stat1, (GAME_WIDTH + 55, 500))
    screen.blit(mark_stat2, (GAME_WIDTH + 35, 530))


def grow():
    global snake, status
    status = is_eaten()
    if status[0]:
        new_head = status[1]
        snake += [new_head]


def restart_game():
    global snake, score, speed, key_press_count, ok_to_go, direction, apple_color, difficulty, snake_length, highscore
    death_sound.play()
    save_highscore()
    bg_sound.stop()
    bg_sound.play(-1)
    highscore = load_highscore()
    snake = [[10, 10], [10, 9], [10, 8]]
    score = 0
    speed = 150
    key_press_count = 0
    ok_to_go = False
    direction = None
    apple_color = RED
    difficulty = difficulty_table["Easy"]
    snake_length = len(snake)


def general_keyboard_control():
    global running, direction, last_move_time, is_paused, ok_to_go, snake, key_press_count, status, restart
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            grow()
            if event.key in (pygame.K_UP, pygame.K_w):
                key_press_count += 1
                if key_press_count == 1:
                    snake = [[10, 8], [10, 9], [10, 10]]
                if direction != "up" and direction != "down" and not is_paused:
                    direction = "up"
                    if not move_snake(direction):
                        restart = True
                    last_move_time = pygame.time.get_ticks()
                ok_to_go = True
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                key_press_count += 1
                if direction != "down" and direction != "up" and not is_paused:
                    direction = "down"
                    if not move_snake(direction):
                        restart = True
                    last_move_time = pygame.time.get_ticks()
                ok_to_go = True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                key_press_count += 1
                if direction != "left" and direction != "right" and not is_paused:
                    direction = "left"
                    if not move_snake(direction):
                        restart = True
                    last_move_time = pygame.time.get_ticks()
                ok_to_go = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                key_press_count += 1
                if direction != "right" and direction != "left" and not is_paused:
                    direction = "right"
                    if not move_snake(direction):
                        restart = True
                    last_move_time = pygame.time.get_ticks()
                ok_to_go = True
            elif event.key == pygame.K_TAB and ok_to_go:
                is_paused = not is_paused


while running:
    if restart:
        restart_game()
        restart = False
    general_keyboard_control()
    if channel and not is_paused:
        channel.unpause()
    if not is_paused:
        screen.fill((0, 0, 0))
        update_stats()
        draw_grid()
        draw_snake()
        draw_apple()
        grow()
        if ok_to_go:
            move_snake_regularly(direction)
        else:
            start_text = paused_font.render("Press any ASWD", True, (255, 128, 0))
            tab_text = paused_font.render("'TAB' to pause", True, (255, 128, 0))
            screen.blit(start_text, (130, GAME_HEIGHT / 2 - 50))
            screen.blit(tab_text, (150, GAME_HEIGHT / 2))
    else:
        pause_text = paused_font.render("PAUSED", True, (255, 128, 0))
        screen.blit(pause_text, (GAME_WIDTH / 2 - 24*3, GAME_HEIGHT / 2 - 24))
        if channel:
            channel.pause()
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
