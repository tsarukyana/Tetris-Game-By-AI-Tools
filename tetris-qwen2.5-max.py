import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255),  # Cyan
    (255, 255, 0),  # Yellow
    (255, 165, 0),  # Orange
    (0, 0, 255),    # Blue
    (0, 255, 0),    # Green
    (255, 0, 0),    # Red
    (128, 0, 128)   # Purple
]

# Shapes and their rotations
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

class Tetris:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0

    def new_piece(self):
        shape = random.choice(SHAPES)
        color = random.randint(1, len(COLORS))
        return {'shape': shape, 'color': color, 'x': self.width // 2 - len(shape[0]) // 2, 'y': 0}

    def valid_move(self, piece, x, y):
        for row in range(len(piece['shape'])):
            for col in range(len(piece['shape'][row])):
                if piece['shape'][row][col]:
                    new_x = x + col
                    new_y = y + row
                    if new_x < 0 or new_x >= self.width or new_y >= self.height or (new_y >= 0 and self.grid[new_y][new_x]):
                        return False
        return True

    def place_piece(self):
        for row in range(len(self.current_piece['shape'])):
            for col in range(len(self.current_piece['shape'][row])):
                if self.current_piece['shape'][row][col]:
                    self.grid[self.current_piece['y'] + row][self.current_piece['x'] + col] = self.current_piece['color']
        self.clear_lines()
        self.current_piece = self.new_piece()
        if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
            self.game_over = True

    def clear_lines(self):
        lines_cleared = 0
        for row in range(self.height):
            if all(self.grid[row]):
                del self.grid[row]
                self.grid.insert(0, [0 for _ in range(self.width)])
                lines_cleared += 1
        self.score += lines_cleared ** 2

    def rotate_piece(self, piece):
        rows = len(piece['shape'])
        cols = len(piece['shape'][0])
        rotated = [[0 for _ in range(rows)] for _ in range(cols)]
        for row in range(rows):
            for col in range(cols):
                rotated[col][rows - 1 - row] = piece['shape'][row][col]
        return rotated

def draw_grid(screen, game):
    for row in range(game.height):
        for col in range(game.width):
            color = BLACK if game.grid[row][col] == 0 else COLORS[game.grid[row][col] - 1]
            pygame.draw.rect(screen, color, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            pygame.draw.rect(screen, GRAY, (col * BLOCK_SIZE, row * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def draw_piece(screen, piece):
    for row in range(len(piece['shape'])):
        for col in range(len(piece['shape'][row])):
            if piece['shape'][row][col]:
                color = COLORS[piece['color'] - 1]
                pygame.draw.rect(screen, color, ((piece['x'] + col) * BLOCK_SIZE, (piece['y'] + row) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(screen, GRAY, ((piece['x'] + col) * BLOCK_SIZE, (piece['y'] + row) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris(SCREEN_WIDTH // BLOCK_SIZE, SCREEN_HEIGHT // BLOCK_SIZE)
    fall_time = 0
    fall_speed = 500  # milliseconds

    running = True
    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime()
        clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    if game.valid_move(game.current_piece, game.current_piece['x'] - 1, game.current_piece['y']):
                        game.current_piece['x'] -= 1
                elif event.key == pygame.K_RIGHT:
                    if game.valid_move(game.current_piece, game.current_piece['x'] + 1, game.current_piece['y']):
                        game.current_piece['x'] += 1
                elif event.key == pygame.K_DOWN:
                    if game.valid_move(game.current_piece, game.current_piece['x'], game.current_piece['y'] + 1):
                        game.current_piece['y'] += 1
                elif event.key == pygame.K_UP:
                    rotated = game.rotate_piece(game.current_piece)
                    if game.valid_move({'shape': rotated, 'color': game.current_piece['color'], 'x': game.current_piece['x'], 'y': game.current_piece['y']}, game.current_piece['x'], game.current_piece['y']):
                        game.current_piece['shape'] = rotated

        if fall_time > fall_speed:
            fall_time = 0
            if game.valid_move(game.current_piece, game.current_piece['x'], game.current_piece['y'] + 1):
                game.current_piece['y'] += 1
            else:
                game.place_piece()

        draw_grid(screen, game)
        draw_piece(screen, game.current_piece)

        if game.game_over:
            print(f"Game Over! Your score: {game.score}")
            running = False

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()