import pygame
import random

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
BLOCK_SIZE = 30

# Game board dimensions
BOARD_WIDTH = 10
BOARD_HEIGHT = 20

# Define shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I-Shape
    [[1, 1], [1, 1]],  # O-Shape
    [[1, 1, 1], [0, 1, 0]],  # T-Shape
    [[1, 1, 1], [1, 0, 0]],  # L-Shape
    [[1, 1, 1], [0, 0, 1]],  # Reverse L-Shape
    [[1, 1, 0], [0, 1, 1]],  # S-Shape
    [[0, 1, 1], [1, 1, 0]]  # Z-Shape
]

COLORS = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")


# Function to draw the grid
def draw_grid():
    for x in range(0, SCREEN_WIDTH, BLOCK_SIZE):
        pygame.draw.line(screen, WHITE, (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, BLOCK_SIZE):
        pygame.draw.line(screen, WHITE, (0, y), (SCREEN_WIDTH, y))


# Function to draw a shape
def draw_shape(shape, x, y, color):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, color, (x + j * BLOCK_SIZE, y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))


# Main game loop
def game():
    clock = pygame.time.Clock()
    board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
    current_piece = random.choice(SHAPES)
    current_color = random.choice(COLORS)
    current_x, current_y = BOARD_WIDTH // 2 - len(current_piece[0]) // 2, 0

    fall_time = 0
    fall_speed = 0.3  # seconds per fall

    game_over = False

    while not game_over:
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            current_y += 1
            if not valid_space(current_piece, current_x, current_y):
                current_y -= 1
                board = place_shape(board, current_piece, current_x, current_y)
                current_piece = random.choice(SHAPES)
                current_color = random.choice(COLORS)
                current_x, current_y = BOARD_WIDTH // 2 - len(current_piece[0]) // 2, 0
                if not valid_space(current_piece, current_x, current_y):
                    game_over = True
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_x -= 1
                    if not valid_space(current_piece, current_x, current_y):
                        current_x += 1
                elif event.key == pygame.K_RIGHT:
                    current_x += 1
                    if not valid_space(current_piece, current_x, current_y):
                        current_x -= 1
                elif event.key == pygame.K_DOWN:
                    current_y += 1
                    if not valid_space(current_piece, current_x, current_y):
                        current_y -= 1
                elif event.key == pygame.K_UP:
                    rotated = rotate(current_piece)
                    if valid_space(rotated, current_x, current_y):
                        current_piece = rotated

        screen.fill(BLACK)
        draw_grid()
        draw_shape(current_piece, current_x * BLOCK_SIZE, current_y * BLOCK_SIZE, current_color)

        for y, row in enumerate(board):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, COLORS[cell - 1], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE))

        pygame.display.update()

        board = remove_full_rows(board)

    pygame.quit()


# Check if the shape can be placed at the given position
def valid_space(shape, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell and (
                    x + j < 0 or x + j >= BOARD_WIDTH or y + i >= BOARD_HEIGHT or (y + i >= 0 and board[y + i][x + j])):
                return False
    return True


# Place the shape on the board
def place_shape(board, shape, x, y):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                board[y + i][x + j] = COLORS.index(current_color) + 1
    return board


# Rotate the shape
def rotate(shape):
    return [list(reversed(col)) for col in zip(*shape)]


# Remove full rows
def remove_full_rows(board):
    rows_to_remove = [i for i, row in enumerate(board) if all(cell != 0 for cell in row)]
    for row in rows_to_remove:
        del board[row]
        board.insert(0, [0 for _ in range(BOARD_WIDTH)])
    return board


if __name__ == "__main__":
    game()