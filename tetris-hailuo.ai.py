import pygame
import random

# Initialize Pygame
pygame.init()

# Game Constants
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 255),  # Cyan - I
    (0, 0, 255),    # Blue - J
    (255, 165, 0),  # Orange - L
    (255, 255, 0),  # Yellow - O
    (0, 255, 0),    # Green - S
    (128, 0, 128),  # Purple - T
    (255, 0, 0)     # Red - Z
]

# Tetromino Shapes
SHAPES = [
    [['.....',
      '.....',
      '..O..',
      '..O..',
      '..O..',
      '..O..',
      '.....'],
     ['.....',
      '.....',
      '.....',
      'OOOO',
      '.....',
      '.....',
      '.....']],
    [['.....',
      '.....',
      '..O..',
      '..O..',
      '..OO.',
      '.....',
      '.....'],
     ['.....',
      '.....',
      '.....',
      '.OOO.',
      '..O..',
      '.....',
      '.....']],
    [['.....',
      '.....',
      '.OO..',
      '..O..',
      '..O..',
      '.....',
      '.....'],
     ['.....',
      '.....',
      '..O..',
      '..O..',
      '.OO..',
      '.....',
      '.....']],
    [['.....',
      '.....',
      '..OO.',
      '..OO.',
      '.....',
      '.....',
      '.....']],
    [['.....',
      '.....',
      '...O.',
      '.OOO.',
      '.....',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '..O..',
      '..OO.',
      '.....',
      '.....',
      '.....']],
    [['.....',
      '.....',
      '..O..',
      '.OOO.',
      '.....',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '..OO.',
      '..O..',
      '.....',
      '.....',
      '.....']],
    [['.....',
      '.....',
      '.OO..',
      '..OO.',
      '.....',
      '.....',
      '.....'],
     ['.....',
      '..O..',
      '.OO..',
      '.O...',
      '.....',
      '.....',
      '.....']]
]

class Tetromino:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

    def image(self):
        return SHAPES[self.shape][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape])

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    format = piece.image()

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == 'O':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(x, y) for x in range(GRID_WIDTH) if grid[y][x] == BLACK] for y in range(GRID_HEIGHT)]
    accepted_positions = [x for sub in accepted_positions for x in sub]
    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    return Tetromino(GRID_WIDTH // 2, 0, random.randint(0, len(SHAPES) - 1))

def draw_grid(surface, grid):
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Draw grid lines
    for y in range(GRID_HEIGHT):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))
    for x in range(GRID_WIDTH):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))

def clear_rows(grid, locked):
    increment = 0
    for y in range(GRID_HEIGHT -1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            increment +=1
            ind = y
            for x in range(GRID_WIDTH):
                try:
                    del locked[(x, y)]
                except:
                    continue
    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                new_key = (x, y + increment)
                locked[new_key] = locked.pop(key)
    return increment

def draw_window(surface, grid, score=0):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    # Display Score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f"Score: {score}", 1, WHITE)
    surface.blit(label, (SCREEN_WIDTH - label.get_width() - 10, 10))
    pygame.display.update()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()
    grid = create_grid()
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    locked_positions = {}
    score = 0
    fall_time = 0
    fall_speed = 0.5

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y +=1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -=1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -=1
                    if not valid_space(current_piece, grid):
                        current_piece.x +=1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x +=1
                    if not valid_space(current_piece, grid):
                        current_piece.x -=1
                elif event.key == pygame.K_DOWN:
                    current_piece.y +=1
                    if not valid_space(current_piece, grid):
                        current_piece.y -=1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()

        shape_pos = convert_shape_format(current_piece)

        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        draw_window(screen, grid, score)

        if check_lost(locked_positions):
            run = False

    pygame.quit()
    print(f"Game Over! Final Score: {score}")

if __name__ == "__main__":
    main()