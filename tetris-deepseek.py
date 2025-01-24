import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_WIDTH = 300
GRID_HEIGHT = 600
BLOCK_SIZE = 30

TOP_LEFT_X = (SCREEN_WIDTH - GRID_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - GRID_HEIGHT - 20

# Color definitions
COLORS = [
    (0, 0, 0),
    (255, 0, 0),
    (0, 150, 0),
    (0, 0, 255),
    (255, 120, 0),
    (255, 255, 0),
    (180, 0, 255),
    (0, 220, 220)
]

# Tetromino shapes
SHAPES = [
    [[1, 5, 9, 13], [4, 5, 6, 7]],  # I
    [[4, 5, 9, 10], [2, 6, 5, 9]],  # Z
    [[6, 7, 9, 10], [1, 5, 6, 10]],  # S
    [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],  # J
    [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],  # L
    [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],  # T
    [[1, 2, 5, 6]],  # O
]


class Tetris:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.grid = [[0 for _ in range(10)] for _ in range(20)]
        self.current_piece = None
        self.next_piece = None
        self.game_over = False
        self.fall_speed = 0.5
        self.fall_time = 0

    def new_piece(self):
        if self.next_piece is None:
            self.current_piece = Piece(random.randint(0, 6))
            self.next_piece = Piece(random.randint(0, 6))
        else:
            self.current_piece = self.next_piece
            self.next_piece = Piece(random.randint(0, 6))

        if not self.valid_space(self.current_piece):
            self.game_over = True

    def valid_space(self, piece):
        accepted_pos = [[(j, i) for j in range(10) if self.grid[i][j] == 0] for i in range(20)]
        accepted_pos = [j for sub in accepted_pos for j in sub]

        formatted = piece.get_formatted_shape()
        for pos in formatted:
            if pos not in accepted_pos:
                if pos[1] > -1:
                    return False
        return True

    def clear_lines(self):
        lines_cleared = 0
        for i in range(len(self.grid)):
            row = self.grid[i]
            if 0 not in row:
                lines_cleared += 1
                del self.grid[i]
                self.grid.insert(0, [0 for _ in range(10)])

        if lines_cleared > 0:
            self.score += (lines_cleared ** 2) * 100
            self.level = 1 + self.score // 1000
            self.fall_speed = 0.5 - (self.level * 0.02)

    def lock_piece(self):
        for pos in self.current_piece.get_formatted_shape():
            x, y = pos
            if y > -1:
                self.grid[y][x] = self.current_piece.color
        self.clear_lines()
        self.new_piece()


class Piece:
    def __init__(self, shape_type):
        self.x = 4
        self.y = 0
        self.type = shape_type
        self.color = shape_type + 1
        self.rotation = 0
        self.shape = SHAPES[shape_type]

    def get_formatted_shape(self):
        positions = []
        format = self.shape[self.rotation % len(self.shape)]

        for i in format:
            x = (i % 4) + self.x
            y = (i // 4) + self.y
            positions.append((x, y))

        return positions

    def rotate(self):
        self.rotation += 1

    def move_down(self):
        self.y += 1

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1


def draw_grid(surface, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, COLORS[grid[i][j]],
                             (TOP_LEFT_X + j * BLOCK_SIZE,
                              TOP_LEFT_Y + i * BLOCK_SIZE,
                              BLOCK_SIZE - 1, BLOCK_SIZE - 1))


def draw_window(surface, game, next_piece):
    surface.fill((32, 32, 32))

    # Draw game title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + GRID_WIDTH / 2 - label.get_width() / 2, 20))

    # Draw next piece preview
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Piece', 1, (255, 255, 255))
    sx = TOP_LEFT_X + GRID_WIDTH + 50
    sy = TOP_LEFT_Y + GRID_HEIGHT / 2 - 100
    surface.blit(label, (sx, sy - 30))

    shape = next_piece.shape[next_piece.rotation % len(next_piece.shape)]
    for i in shape:
        x = (i % 4) * BLOCK_SIZE + sx
        y = (i // 4) * BLOCK_SIZE + sy
        pygame.draw.rect(surface, COLORS[next_piece.color],
                         (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    # Draw score and level
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render(f'Score: {game.score}', 1, (255, 255, 255))
    surface.blit(label, (sx, sy + 150))
    label = font.render(f'Level: {game.level}', 1, (255, 255, 255))
    surface.blit(label, (sx, sy + 180))

    # Draw game grid
    draw_grid(surface, game.grid)

    # Draw current piece
    if game.current_piece:
        for pos in game.current_piece.get_formatted_shape():
            x, y = pos
            if y >= 0:
                pygame.draw.rect(surface, COLORS[game.current_piece.color],
                                 (TOP_LEFT_X + x * BLOCK_SIZE,
                                  TOP_LEFT_Y + y * BLOCK_SIZE,
                                  BLOCK_SIZE - 1, BLOCK_SIZE - 1))

    # Draw grid border
    pygame.draw.rect(surface, (255, 255, 255),
                     (TOP_LEFT_X, TOP_LEFT_Y, GRID_WIDTH, GRID_HEIGHT), 4)


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')
    clock = pygame.time.Clock()

    game = Tetris()
    game.new_piece()

    fall_speed = game.fall_speed

    while not game.game_over:
        clock.tick()
        game.fall_time += clock.get_rawtime()

        # Piece falling
        if game.fall_time / 1000 >= fall_speed:
            game.fall_time = 0
            game.current_piece.move_down()
            if not game.valid_space(game.current_piece):
                game.current_piece.y -= 1
                game.lock_piece()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.current_piece.move_left()
                    if not game.valid_space(game.current_piece):
                        game.current_piece.move_right()
                if event.key == pygame.K_RIGHT:
                    game.current_piece.move_right()
                    if not game.valid_space(game.current_piece):
                        game.current_piece.move_left()
                if event.key == pygame.K_DOWN:
                    game.current_piece.move_down()
                    if not game.valid_space(game.current_piece):
                        game.current_piece.y -= 1
                if event.key == pygame.K_UP:
                    game.current_piece.rotate()
                    if not game.valid_space(game.current_piece):
                        game.current_piece.rotation -= 1
                if event.key == pygame.K_SPACE:
                    while game.valid_space(game.current_piece):
                        game.current_piece.move_down()
                    game.current_piece.y -= 1
                    game.lock_piece()

        draw_window(screen, game, game.next_piece)
        pygame.display.update()

    # Game over screen
    screen.fill((0, 0, 0))
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Game Over!', 1, (255, 255, 255))
    screen.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, 200))
    label = font.render(f'Final Score: {game.score}', 1, (255, 255, 255))
    screen.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, 300))
    label = font.render('Press any key to restart', 1, (255, 255, 255))
    screen.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, 400))
    pygame.display.update()

    # Wait for key press to restart
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                main()
                return


if __name__ == '__main__':
    main()