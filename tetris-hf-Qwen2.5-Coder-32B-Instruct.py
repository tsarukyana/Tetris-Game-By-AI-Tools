import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 0, 1], [1, 1, 1]],  # L
    [[1, 0, 0], [1, 1, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
]

# Colors for each shape
SHAPE_COLORS = [CYAN, YELLOW, PURPLE, ORANGE, BLUE, GREEN, RED]

# Game variables
grid_width = 10
grid_height = 20
grid = [[BLACK] * grid_width for _ in range(grid_height)]

# Current piece
current_piece = None
next_piece = None
current_x = 0
current_y = 0

# Clock
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 500  # milliseconds

# Initialize game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

def create_piece():
    global current_piece, next_piece, current_x, current_y
    current_piece = next_piece if next_piece else random.choice(SHAPES)
    next_piece = random.choice(SHAPES)
    current_x = grid_width // 2 - len(current_piece[0]) // 2
    current_y = 0

def draw_grid():
    for y in range(grid_height):
        for x in range(grid_width):
            pygame.draw.rect(screen, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pygame.draw.rect(screen, WHITE, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_piece(piece, offset_x, offset_y, color):
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, ((offset_x + x) * BLOCK_SIZE, (offset_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(screen, WHITE, ((offset_x + x) * BLOCK_SIZE, (offset_y + y) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def check_collision(piece, offset_x, offset_y):
    for y, row in enumerate(piece):
        for x, cell in enumerate(row):
            if cell:
                if offset_x + x < 0 or offset_x + x >= grid_width or offset_y + y >= grid_height or grid[offset_y + y][offset_x + x] != BLACK:
                    return True
    return False

def lock_piece():
    global grid
    for y, row in enumerate(current_piece):
        for x, cell in enumerate(row):
            if cell:
                grid[current_y + y][current_x + x] = SHAPE_COLORS[SHAPES.index(current_piece)]

def clear_lines():
    global grid
    lines_cleared = 0
    new_grid = [row for row in grid if BLACK in row]
    lines_cleared = grid_height - len(new_grid)
    grid = [[BLACK] * grid_width for _ in range(lines_cleared)] + new_grid
    return lines_cleared

def game_over():
    font = pygame.font.SysFont('Arial', 45)
    text = font.render('Game Over', True, RED)
    screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.delay(2000)
    pygame.quit()
    quit()

def main():
    global current_piece, next_piece, current_x, current_y, fall_time

    create_piece()

    running = True
    while running:
        screen.fill(BLACK)
        draw_grid()
        draw_piece(current_piece, current_x, current_y, SHAPE_COLORS[SHAPES.index(current_piece)])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if not check_collision(current_piece, current_x - 1, current_y):
                        current_x -= 1
                if event.key == pygame.K_RIGHT:
                    if not check_collision(current_piece, current_x + 1, current_y):
                        current_x += 1
                if event.key == pygame.K_DOWN:
                    if not check_collision(current_piece, current_x, current_y + 1):
                        current_y += 1
                if event.key == pygame.K_UP:
                    rotated_piece = list(zip(*current_piece[::-1]))
                    if not check_collision(rotated_piece, current_x, current_y):
                        current_piece = rotated_piece

        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time > fall_speed:
            if not check_collision(current_piece, current_x, current_y + 1):
                current_y += 1
            else:
                lock_piece()
                clear_lines()
                create_piece()
                if check_collision(current_piece, current_x, current_y):
                    game_over()
            fall_time = 0

        pygame.display.flip()

if __name__ == '__main__':
    main()