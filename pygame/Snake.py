import pygame
import time
import random
import math

# Константы
WIDTH = 1000
HEIGHT = 600
SNAKE_BLOCK_SIZE = 20
SNAKE_SPEED = 10
WHITE = (255, 255, 255)
YELLOW = (255, 255, 102)
BLACK = (0, 0, 0)
RED = (213, 50, 80)
GREEN = (0, 255, 0)
BLUE = (50, 153, 213)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GOLD = (255, 215, 0)
BOOST_PROBABILITY = 0.005
BOOST_RADIUS = 20
FOOD_COLORS = {
    "apple": (255, 0, 0, 1),
    "banana": (255, 255, 0, 3),
    "cherry": (255, 0, 255, 5)
}

pygame.init()
# Начальная настройка окна
dis = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Realistic Snake')

FULLSCREEN = False

# Загрузка ресурсов
try:
    snake_head_img = pygame.image.load("ikefo9ec.png").convert_alpha()
    snake_head2_img = pygame.image.load("ikefo8ec.png").convert_alpha()
    snake_body_img = pygame.image.load("gac3dbz4.png").convert_alpha()
    snake_body2_img = pygame.image.load("gac3dbz3.png").convert_alpha()
    apple_img = pygame.image.load("appl.png").convert_alpha()
    banana_img = pygame.image.load("banan.png").convert_alpha()
    cherry_img = pygame.image.load("cherry.png").convert_alpha()
    obstacle_img = pygame.image.load("4njxi20w.png").convert_alpha()
    background_img = pygame.image.load("wp6eo9hc.png").convert()

    snake_head_img = pygame.transform.scale(snake_head_img, (SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE))
    snake_body_img = pygame.transform.scale(snake_body_img, (SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE))
    snake_head2_img = pygame.transform.scale(snake_head2_img, (SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE))
    snake_body2_img = pygame.transform.scale(snake_body2_img, (SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE))
    apple_img = pygame.transform.scale(apple_img, (int(SNAKE_BLOCK_SIZE * 1.5), int(SNAKE_BLOCK_SIZE * 1.5)))
    banana_img = pygame.transform.scale(banana_img, (int(SNAKE_BLOCK_SIZE * 1.5), int(SNAKE_BLOCK_SIZE * 1.5)))
    cherry_img = pygame.transform.scale(cherry_img, (int(SNAKE_BLOCK_SIZE * 1.5), int(SNAKE_BLOCK_SIZE * 1.5)))
    obstacle_img = pygame.transform.scale(obstacle_img, (SNAKE_BLOCK_SIZE, SNAKE_BLOCK_SIZE))
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


except FileNotFoundError as e:
    print(f"Ошибка загрузки изображения: {e}.  Убедитесь, что файлы существуют!")
    pygame.quit()
    quit()

font_style = pygame.font.SysFont("bahnschrift", 36)
score_font = pygame.font.SysFont("comicsansms", 48)
title_font = pygame.font.SysFont("comicsansms", 80)
menu_font = pygame.font.SysFont("comicsansms", 50)
gameover_font = pygame.font.SysFont("comicsansms", 60)
clock = pygame.time.Clock()


try:
    menu_background_img = pygame.image.load("menu_bg.png").convert()
    gameover_background_img = pygame.image.load("gameover_bg.png").convert()

    menu_background_img = pygame.transform.scale(menu_background_img, (WIDTH, HEIGHT))
    gameover_background_img = pygame.transform.scale(gameover_background_img, (WIDTH, HEIGHT))
except FileNotFoundError as e:
    print(f"Ошибка загрузки фонового изображения: {e}. Убедитесь, что файлы существуют!")
    pygame.quit()
    quit()


def your_score(score, surface, x, y):
    value = score_font.render("Ваш счёт: " + str(score), True, YELLOW)
    surface.blit(value, [x, y])


def draw_snake(surface, snake_list, x1_change, y1_change, snake_head_img, snake_body_img):
    for i, segment in enumerate(snake_list):
        x, y = segment
        if i == len(snake_list) - 1:
            if x1_change > 0:
                rotated_head = pygame.transform.rotate(snake_head_img, 270)
            elif x1_change < 0:
                rotated_head = pygame.transform.rotate(snake_head_img, 90)
            elif y1_change > 0:
                rotated_head = pygame.transform.rotate(snake_head_img, 180)
            else:
                rotated_head = snake_head_img
            surface.blit(rotated_head, (x, y))
        else:
            surface.blit(snake_body_img, (x, y))


def message(msg, font, color, surface, x_pos=None, y_pos=None):
    mesg = font.render(msg, True, color)
    msg_rect = mesg.get_rect()

    if x_pos is None:
        x_pos = (WIDTH - msg_rect.width) // 2
    if y_pos is None:
        y_pos = (HEIGHT - msg_rect.height) // 2

    surface.blit(mesg, [x_pos, y_pos])


def generate_obstacles(num_obstacles):
    obstacles = []
    for _ in range(num_obstacles):
        for _ in range(100):
            x = round(random.randrange(0, int((WIDTH - SNAKE_BLOCK_SIZE) / SNAKE_BLOCK_SIZE))) * SNAKE_BLOCK_SIZE
            y = round(random.randrange(0, int((HEIGHT - SNAKE_BLOCK_SIZE) / SNAKE_BLOCK_SIZE))) * SNAKE_BLOCK_SIZE

            if not ((x > WIDTH / 2 - 50 and x < WIDTH / 2 + 50) and (y > HEIGHT / 2 - 50 and y < HEIGHT / 2 + 50)):
                obstacles.append((x, y))
                break
        else:
            print("Warning: Could not find a valid position for an obstacle")

    return obstacles


def check_collisions(x1, y1, obstacles, invincible, snake_list=None):
    if invincible:
        return False
    if (x1, y1) in obstacles:
        return True

    # Проверка столкновения с самим собой
    if snake_list:
        for i, segment in enumerate(snake_list[:-1]):
            if (x1, y1) == segment:
                return True
    return False

def generate_food():
    food_types = list(FOOD_COLORS.keys())
    food_type = random.choice(food_types)
    foodx = round(random.randrange(0, int((WIDTH - SNAKE_BLOCK_SIZE * 1.5) / SNAKE_BLOCK_SIZE))) * SNAKE_BLOCK_SIZE
    foody = round(random.randrange(0, int((HEIGHT - SNAKE_BLOCK_SIZE * 1.5) / SNAKE_BLOCK_SIZE))) * SNAKE_BLOCK_SIZE
    return foodx, foody, food_type


def draw_food(surface, foodx, foody, food_type, apple_img, banana_img, cherry_img):
    if food_type == "apple":
        surface.blit(apple_img, (foodx, foody))
    elif food_type == "banana":
        surface.blit(banana_img, (foodx, foody))
    elif food_type == "cherry":
        surface.blit(cherry_img, (foodx, foody))
    else:
        pygame.draw.rect(surface, FOOD_COLORS[food_type][:3],
                         [foodx, foody, int(SNAKE_BLOCK_SIZE * 1.5), int(SNAKE_BLOCK_SIZE * 1.5)])


class Snake:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.x_change = 0
        self.y_change = 0
        self.snake_list = []
        self.length_of_snake = 1
        self.color = color
        self.score = 0

    def move(self):
        self.x += self.x_change
        self.y += self.y_change

        # Туннелирование
        if self.x >= WIDTH:
            self.x = 0
        elif self.x < 0:
            self.x = WIDTH - SNAKE_BLOCK_SIZE
        elif self.y >= HEIGHT:
            self.y = 0
        elif self.y < 0:
            self.y = HEIGHT - SNAKE_BLOCK_SIZE


    def reset(self, x, y):
        self.x = x
        self.y = y
        self.x_change = 0
        self.y_change = 0
        self.snake_list = []
        self.length_of_snake = 1
        self.score = 0

class GameState:
    def __init__(self):
        self.game_over = False
        self.game_close = False
        self.snake1 = Snake(WIDTH / 2 - 100, HEIGHT / 2, GREEN)
        self.snake2 = Snake(WIDTH / 2 + 100, HEIGHT / 2, BLUE)
        self.foodx, self.foody, self.food_type = generate_food()
        self.obstacles = []
        self.num_obstacles = 5  # Начальное количество препятствий
        self.obstacles = generate_obstacles(self.num_obstacles)
        self.obstacle_respawn_timer = 0
        self.obstacle_respawn_interval = 15

        self.length_boost_active = False
        self.length_boost_x = -100
        self.length_boost_y = -100
        self.length_boost_amount = 0
        self.length_boost_available = True
        self.length_boost_last_used = 0
        self.length_boost_start_time = 0

        self.slow_down_active = False
        self.slow_down_x = -100
        self.slow_down_y = -100
        self.slow_down_duration = 5
        self.slow_down_start_time = 0
        self.slow_down_available = True
        self.slow_down_cooldown = 15
        self.slow_down_last_used = 0

        self.invincible = False
        self.invincible_x = -100
        self.invincible_y = -100
        self.invincible_duration = 5
        self.invincible_start_time = 0
        self.invincible_available = True
        self.invincible_cooldown = 25
        self.invincible_last_used = 0

        self.current_speed = SNAKE_SPEED
        self.game_start_time = time.time()
        self.difficulty_timer = 0  # Таймер для увеличения сложности
        self.difficulty_interval = 30  # Увеличивать сложность каждые 30 секунд

    def reset(self):
        self.game_over = False
        self.game_close = False
        self.snake1.reset(WIDTH / 2 - 100, HEIGHT / 2)
        self.snake2.reset(WIDTH / 2 + 100, HEIGHT / 2)
        self.foodx, self.foody, self.food_type = generate_food()
        self.num_obstacles = 5
        self.obstacles = generate_obstacles(self.num_obstacles)
        self.obstacle_respawn_timer = 0

        self.length_boost_active = False
        self.length_boost_x = -100
        self.length_boost_y = -100
        self.length_boost_amount = 0
        self.length_boost_available = True
        self.length_boost_last_used = 0
        self.length_boost_start_time = 0

        self.slow_down_active = False
        self.slow_down_x = -100
        self.slow_down_y = -100
        self.slow_down_start_time = 0
        self.slow_down_available = True
        self.slow_down_last_used = 0

        self.invincible = False
        self.invincible_x = -100
        self.invincible_y = -100
        self.invincible_start_time = 0
        self.invincible_available = True
        self.invincible_last_used = 0

        self.current_speed = SNAKE_SPEED
        self.game_start_time = time.time()
        self.difficulty_timer = 0


def handle_boost(surface, boost_type, active, x, y, duration, available, cooldown, last_used, color, start_time,
                 snake_x, snake_y, snake_block_size, boost_radius, image=None):
    current_time = time.time()
    spawn_condition = available and (current_time - last_used > cooldown) and random.random() < BOOST_PROBABILITY

    if spawn_condition and not active:
        x = round(random.randrange(0, int((WIDTH - boost_radius * 2) / SNAKE_BLOCK_SIZE))) * SNAKE_BLOCK_SIZE + boost_radius
        y = round(random.randrange(0, int((HEIGHT - boost_radius * 2) / SNAKE_BLOCK_SIZE))) * SNAKE_BLOCK_SIZE + boost_radius
        active = True

    if active:
        if image:
            surface.blit(image, (x - boost_radius, y - boost_radius))
        distance = math.sqrt((x - snake_x) ** 2 + (y - snake_y) ** 2)
        if distance < boost_radius + snake_block_size / 2:
            active = False
            start_time = current_time
            last_used = current_time
            available = False

    return active, x, y, last_used, available, start_time


def toggle_fullscreen():
    global FULLSCREEN, dis, WIDTH, HEIGHT, background_img

    FULLSCREEN = not FULLSCREEN

    if FULLSCREEN:

        WIDTH, HEIGHT = dis.get_width(), dis.get_height()
        dis = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        WIDTH, HEIGHT = dis.get_width(), dis.get_height()
    else:
        dis = pygame.display.set_mode((1000, 600))

    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))



def game_loop():
    global WIDTH, HEIGHT, background_img, menu_background_img, gameover_background_img

    game_state = GameState()

    while True: # Main loop
        # Menu
        menu_active = True
        while menu_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:  # Play
                        menu_active = False
                    elif event.key == pygame.K_2:  # Quit
                        pygame.quit()
                        quit()

            dis.blit(menu_background_img, (0, 0))
            message("Realistic Snake", title_font, GREEN, dis, y_pos=HEIGHT / 4 - 50)
            message("1 - Играть", menu_font, WHITE, dis, y_pos=HEIGHT / 2)
            message("2 - Выход", menu_font, WHITE, dis, y_pos=HEIGHT / 2 + 60)
            pygame.display.update()

        # Game
        game_state.reset()
        while not game_state.game_over:
            # Цикл обработки событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state.game_over = True
                if event.type == pygame.KEYDOWN:
                    if game_state.game_close:
                        if event.key == pygame.K_q:
                            game_state.game_over = True
                        if event.key == pygame.K_c:
                            game_state.reset()
                            game_state.game_close = False
                            continue
                    else:
                        # Управление игроком
                        if event.key == pygame.K_LEFT and game_state.snake1.x_change == 0:
                            game_state.snake1.x_change = -SNAKE_BLOCK_SIZE
                            game_state.snake1.y_change = 0
                        elif event.key == pygame.K_RIGHT and game_state.snake1.x_change == 0:
                            game_state.snake1.x_change = SNAKE_BLOCK_SIZE
                            game_state.snake1.y_change = 0
                        elif event.key == pygame.K_UP and game_state.snake1.y_change == 0:
                            game_state.snake1.y_change = -SNAKE_BLOCK_SIZE
                            game_state.snake1.x_change = 0
                        elif event.key == pygame.K_DOWN and game_state.snake1.y_change == 0:
                            game_state.snake1.y_change = SNAKE_BLOCK_SIZE
                            game_state.snake1.x_change = 0


                        if event.key == pygame.K_a and game_state.snake2.x_change == 0:
                            game_state.snake2.x_change = -SNAKE_BLOCK_SIZE
                            game_state.snake2.y_change = 0
                        elif event.key == pygame.K_d and game_state.snake2.x_change == 0:
                            game_state.snake2.x_change = SNAKE_BLOCK_SIZE
                            game_state.snake2.y_change = 0
                        elif event.key == pygame.K_w and game_state.snake2.y_change == 0:
                            game_state.snake2.y_change = -SNAKE_BLOCK_SIZE
                            game_state.snake2.x_change = 0
                        elif event.key == pygame.K_s and game_state.snake2.y_change == 0:
                            game_state.snake2.y_change = SNAKE_BLOCK_SIZE
                            game_state.snake2.x_change = 0
                        elif event.key == pygame.K_f:
                            toggle_fullscreen()
                            game_state.obstacles = generate_obstacles(10)

            # Экран проигрыша
            if game_state.game_close:
                dis.blit(gameover_background_img, (0, 0))
                message("Вы проиграли!", gameover_font, RED, dis, y_pos=HEIGHT / 4)
                message("Q - выход, C - новая игра", font_style, WHITE, dis, y_pos=HEIGHT / 2)

                your_score(game_state.snake1.score, dis, 0, 0)
                your_score(game_state.snake2.score, dis, 0, 50)
                pygame.display.update()
                continue


            game_state.snake1.move()
            game_state.snake2.move()

            # Проверка столкновений
            if check_collisions(game_state.snake1.x, game_state.snake1.y, game_state.obstacles, game_state.invincible, game_state.snake1.snake_list) or \
               check_collisions(game_state.snake1.x, game_state.snake1.y, [], game_state.invincible, game_state.snake2.snake_list):
                game_state.game_close = True

            if check_collisions(game_state.snake2.x, game_state.snake2.y, game_state.obstacles, game_state.invincible, game_state.snake2.snake_list) or \
               check_collisions(game_state.snake2.x, game_state.snake2.y, [], game_state.invincible, game_state.snake1.snake_list):
                game_state.game_close = True

            # Отрисовка
            dis.blit(background_img, (0, 0))
            draw_food(dis, game_state.foodx, game_state.foody, game_state.food_type, apple_img, banana_img, cherry_img)

            for obstacle in game_state.obstacles:
                dis.blit(obstacle_img, obstacle)

            # Обновление змейки
            snake1_head = []
            snake1_head.append(game_state.snake1.x)
            snake1_head.append(game_state.snake1.y)
            game_state.snake1.snake_list.append(snake1_head)
            if len(game_state.snake1.snake_list) > game_state.snake1.length_of_snake:
                del game_state.snake1.snake_list[0]
            for x in game_state.snake1.snake_list[:-1]:
                if x == snake1_head:
                    game_state.game_close = True

            draw_snake(dis, game_state.snake1.snake_list, game_state.snake1.x_change, game_state.snake1.y_change, snake_head_img,
                       snake_body_img)
            your_score(game_state.snake1.score, dis, 0, 0)

            snake2_head = []
            snake2_head.append(game_state.snake2.x)
            snake2_head.append(game_state.snake2.y)
            game_state.snake2.snake_list.append(snake2_head)
            if len(game_state.snake2.snake_list) > game_state.snake2.length_of_snake:
                del game_state.snake2.snake_list[0]
            for x in game_state.snake2.snake_list[:-1]:
                if x == snake2_head:
                    game_state.game_close = True
            draw_snake(dis, game_state.snake2.snake_list, game_state.snake2.x_change, game_state.snake2.y_change, snake_head2_img,
                       snake_body2_img)
            your_score(game_state.snake2.score, dis, 0, 50)


            game_state.obstacle_respawn_timer += clock.get_time() / 1000.0

            if game_state.obstacle_respawn_timer >= game_state.obstacle_respawn_interval:
                game_state.obstacles = generate_obstacles(10)
                game_state.obstacle_respawn_timer = 0

            # Столкновение с едой
            if game_state.snake1.x == game_state.foodx and game_state.snake1.y == game_state.foody:
                score_increase = FOOD_COLORS[game_state.food_type][3]
                game_state.snake1.score += score_increase
                game_state.snake1.length_of_snake += 1

                game_state.foodx, game_state.foody, game_state.food_type = generate_food()
                while (game_state.foodx, game_state.foody) in game_state.obstacles:
                    game_state.foodx, game_state.foody, game_state.food_type = generate_food()


            if game_state.snake2.x == game_state.foodx and game_state.snake2.y == game_state.foody:
                score_increase = FOOD_COLORS[game_state.food_type][3]
                game_state.snake2.score += score_increase
                game_state.snake2.length_of_snake += 1

                game_state.foodx, game_state.foody, game_state.food_type = generate_food()
                while (game_state.foodx, game_state.foody) in game_state.obstacles:
                    game_state.foodx, game_state.foody, game_state.food_type = generate_food()
            # Увеличение сложности
            game_state.difficulty_timer += clock.get_time() / 1000.0

            SNAKE_SPEED=10

            if game_state.difficulty_timer >= game_state.difficulty_interval:
                game_state.difficulty_timer = 0
                game_state.num_obstacles += 2  # Увеличиваем количество препятствий
                game_state.obstacles = generate_obstacles(game_state.num_obstacles)  # Генерируем новые препятствия
                SNAKE_SPEED *= 1.1
                game_state.current_speed = SNAKE_SPEED

            clock.tick(game_state.current_speed)

            pygame.display.update()

    pygame.quit()
    quit()


game_loop()