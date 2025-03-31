import pygame
import random
import time

# Initialize pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Game dimensions
GRID_WIDTH = 10
GRID_HEIGHT = 20
BLOCK_SIZE = 30
GRID_LINE_WIDTH = 1
SCREEN_WIDTH = GRID_WIDTH * BLOCK_SIZE + 200  # Extra space for score, next piece
SCREEN_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
SIDEBAR_X = GRID_WIDTH * BLOCK_SIZE + 20

# Game settings
FPS = 60
INITIAL_FALL_SPEED = 0.5  # Blocks per second
LEVEL_SPEED_INCREASE = 0.05
LINES_PER_LEVEL = 10

# Tetromino shapes and rotations
SHAPES = {
    'I': [
        [[0, 0, 0, 0],
         [1, 1, 1, 1],
         [0, 0, 0, 0],
         [0, 0, 0, 0]],
        [[0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0],
         [0, 1, 0, 0]]
    ],
    'J': [
        [[1, 0, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 1],
         [0, 1, 0],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 0, 1]],
        [[0, 1, 0],
         [0, 1, 0],
         [1, 1, 0]]
    ],
    'L': [
        [[0, 0, 1],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 0],
         [0, 1, 1]],
        [[0, 0, 0],
         [1, 1, 1],
         [1, 0, 0]],
        [[1, 1, 0],
         [0, 1, 0],
         [0, 1, 0]]
    ],
    'O': [
        [[1, 1],
         [1, 1]]
    ],
    'S': [
        [[0, 1, 1],
         [1, 1, 0],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 0, 1]]
    ],
    'T': [
        [[0, 1, 0],
         [1, 1, 1],
         [0, 0, 0]],
        [[0, 1, 0],
         [0, 1, 1],
         [0, 1, 0]],
        [[0, 0, 0],
         [1, 1, 1],
         [0, 1, 0]],
        [[0, 1, 0],
         [1, 1, 0],
         [0, 1, 0]]
    ],
    'Z': [
        [[1, 1, 0],
         [0, 1, 1],
         [0, 0, 0]],
        [[0, 0, 1],
         [0, 1, 1],
         [0, 1, 0]]
    ]
}

# Tetromino colors
SHAPE_COLORS = {
    'I': CYAN,
    'J': BLUE,
    'L': ORANGE,
    'O': YELLOW,
    'S': GREEN,
    'T': MAGENTA,
    'Z': RED
}


class Tetromino:
    def __init__(self, shape=None):
        # Choose a random shape if none is provided
        if shape is None:
            self.shape_name = random.choice(list(SHAPES.keys()))
        else:
            self.shape_name = shape

        # Set initial rotation and get shape matrix
        self.rotation = 0
        self.shape_matrix = SHAPES[self.shape_name][self.rotation]
        self.color = SHAPE_COLORS[self.shape_name]

        # Set initial position
        self.x = GRID_WIDTH // 2 - len(self.shape_matrix[0]) // 2
        self.y = 0

    def rotate(self, grid):
        """Rotate the tetromino clockwise if possible"""
        next_rotation = (self.rotation + 1) % len(SHAPES[self.shape_name])
        next_shape = SHAPES[self.shape_name][next_rotation]

        # Check if rotation is valid
        if not self._check_collision(next_shape, self.x, self.y, grid):
            self.rotation = next_rotation
            self.shape_matrix = next_shape

    def move_left(self, grid):
        """Move the tetromino left if possible"""
        if not self._check_collision(self.shape_matrix, self.x - 1, self.y, grid):
            self.x -= 1

    def move_right(self, grid):
        """Move the tetromino right if possible"""
        if not self._check_collision(self.shape_matrix, self.x + 1, self.y, grid):
            self.x += 1

    def move_down(self, grid):
        """Move the tetromino down if possible, return True if it moved"""
        if not self._check_collision(self.shape_matrix, self.x, self.y + 1, grid):
            self.y += 1
            return True
        return False

    def hard_drop(self, grid):
        """Move the tetromino down until it collides"""
        while self.move_down(grid):
            pass

    def _check_collision(self, shape_matrix, x, y, grid):
        """Check if the tetromino would collide with the grid or boundaries"""
        for row in range(len(shape_matrix)):
            for col in range(len(shape_matrix[row])):
                if shape_matrix[row][col]:
                    # Check grid boundaries
                    if (y + row >= GRID_HEIGHT) or (x + col < 0) or (x + col >= GRID_WIDTH):
                        return True
                    # Check collision with other blocks in the grid
                    if y + row >= 0 and grid[y + row][x + col]:
                        return True
        return False

    def lock(self, grid):
        """Lock the tetromino into the grid"""
        for row in range(len(self.shape_matrix)):
            for col in range(len(self.shape_matrix[row])):
                if self.shape_matrix[row][col]:
                    if 0 <= self.y + row < GRID_HEIGHT and 0 <= self.x + col < GRID_WIDTH:
                        grid[self.y + row][self.x + col] = self.color
        return grid


class TetrisGame:
    def __init__(self):
        # Initialize game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris")
        self.clock = pygame.time.Clock()

        # Initialize game state
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.paused = False

        # Initialize scoring and level
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_speed = INITIAL_FALL_SPEED

        # Initialize timing
        self.last_fall_time = time.time()

        # Initialize fonts
        self.font = pygame.font.SysFont('Arial', 24)
        self.big_font = pygame.font.SysFont('Arial', 36)

    def run(self):
        """Main game loop"""
        running = True

        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if not self.game_over and not self.paused:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            self.current_piece.move_left(self.grid)
                        elif event.key == pygame.K_RIGHT:
                            self.current_piece.move_right(self.grid)
                        elif event.key == pygame.K_DOWN:
                            self.current_piece.move_down(self.grid)
                        elif event.key == pygame.K_UP:
                            self.current_piece.rotate(self.grid)
                        elif event.key == pygame.K_SPACE:
                            self.current_piece.hard_drop(self.grid)
                            self._lock_piece_and_get_new()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r and self.game_over:
                        self._reset_game()

            # Game logic (only if game is not over or paused)
            if not self.game_over and not self.paused:
                current_time = time.time()
                if current_time - self.last_fall_time > 1.0 / self.fall_speed:
                    # Try to move piece down
                    if not self.current_piece.move_down(self.grid):
                        self._lock_piece_and_get_new()
                    self.last_fall_time = current_time

            # Draw everything
            self._draw()

            # Cap the FPS
            self.clock.tick(FPS)

        pygame.quit()

    def _lock_piece_and_get_new(self):
        """Lock the current piece into the grid and get a new piece"""
        # Lock the current piece
        self.grid = self.current_piece.lock(self.grid)

        # Check for completed lines
        self._check_lines()

        # Get new pieces
        self.current_piece = self.next_piece
        self.next_piece = Tetromino()

        # Check if the new piece can be placed
        for row in range(len(self.current_piece.shape_matrix)):
            for col in range(len(self.current_piece.shape_matrix[row])):
                if (self.current_piece.shape_matrix[row][col] and
                        self.grid[self.current_piece.y + row][self.current_piece.x + col]):
                    self.game_over = True

    def _check_lines(self):
        """Check for completed lines and clear them"""
        lines_to_clear = []

        # Find lines to clear
        for row in range(GRID_HEIGHT):
            if all(self.grid[row]):
                lines_to_clear.append(row)

        if lines_to_clear:
            # Update score based on number of lines cleared
            lines_count = len(lines_to_clear)
            if lines_count == 1:
                self.score += 100 * self.level
            elif lines_count == 2:
                self.score += 300 * self.level
            elif lines_count == 3:
                self.score += 500 * self.level
            elif lines_count == 4:  # Tetris!
                self.score += 800 * self.level

            # Update lines cleared and level
            self.lines_cleared += lines_count
            old_level = self.level
            self.level = self.lines_cleared // LINES_PER_LEVEL + 1

            # Increase speed if level increased
            if self.level > old_level:
                self.fall_speed = INITIAL_FALL_SPEED + (self.level - 1) * LEVEL_SPEED_INCREASE

            # Clear the lines
            for row in lines_to_clear:
                # Remove the line
                self.grid.pop(row)
                # Add a new empty line at the top
                self.grid.insert(0, [None for _ in range(GRID_WIDTH)])

    def _draw(self):
        """Draw the game"""
        # Clear the screen
        self.screen.fill(BLACK)

        # Draw the grid
        self._draw_grid()

        # Draw the current piece
        self._draw_tetromino(self.current_piece)

        # Draw sidebar
        self._draw_sidebar()

        # Draw overlay messages
        if self.game_over:
            self._draw_game_over()
        elif self.paused:
            self._draw_paused()

        # Update the display
        pygame.display.flip()

    def _draw_grid(self):
        """Draw the game grid"""
        # Draw grid background
        grid_rect = pygame.Rect(0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE)
        pygame.draw.rect(self.screen, BLACK, grid_rect)

        # Draw grid lines
        for x in range(0, GRID_WIDTH * BLOCK_SIZE + 1, BLOCK_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, GRID_HEIGHT * BLOCK_SIZE), GRID_LINE_WIDTH)
        for y in range(0, GRID_HEIGHT * BLOCK_SIZE + 1, BLOCK_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (GRID_WIDTH * BLOCK_SIZE, y), GRID_LINE_WIDTH)

        # Draw locked blocks
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if self.grid[row][col]:
                    self._draw_block(col, row, self.grid[row][col])

    def _draw_tetromino(self, tetromino):
        """Draw a tetromino"""
        for row in range(len(tetromino.shape_matrix)):
            for col in range(len(tetromino.shape_matrix[row])):
                if tetromino.shape_matrix[row][col]:
                    self._draw_block(tetromino.x + col, tetromino.y + row, tetromino.color)

    def _draw_block(self, x, y, color):
        """Draw a single block at grid coordinates (x, y)"""
        # Skip if block is outside the visible grid
        if y < 0:
            return

        rect = pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, WHITE, rect, 1)  # Block border

    def _draw_sidebar(self):
        """Draw the sidebar with score, level, and next piece"""
        # Draw next piece preview
        next_text = self.font.render("Next:", True, WHITE)
        self.screen.blit(next_text, (SIDEBAR_X, 20))

        # Calculate position for next piece preview
        preview_x = SIDEBAR_X + 30
        preview_y = 60

        # Create a centered preview of the next piece
        for row in range(len(self.next_piece.shape_matrix)):
            for col in range(len(self.next_piece.shape_matrix[row])):
                if self.next_piece.shape_matrix[row][col]:
                    preview_rect = pygame.Rect(
                        preview_x + col * BLOCK_SIZE,
                        preview_y + row * BLOCK_SIZE,
                        BLOCK_SIZE, BLOCK_SIZE
                    )
                    pygame.draw.rect(self.screen, self.next_piece.color, preview_rect)
                    pygame.draw.rect(self.screen, WHITE, preview_rect, 1)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (SIDEBAR_X, 160))

        # Draw level
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (SIDEBAR_X, 200))

        # Draw lines cleared
        lines_text = self.font.render(f"Lines: {self.lines_cleared}", True, WHITE)
        self.screen.blit(lines_text, (SIDEBAR_X, 240))

        # Draw controls hint
        controls_y = 300
        controls_text = [
            "Controls:",
            "←/→: Move",
            "↑: Rotate",
            "↓: Soft drop",
            "Space: Hard drop",
            "P: Pause"
        ]

        for i, text in enumerate(controls_text):
            ctrl_text = self.font.render(text, True, WHITE)
            self.screen.blit(ctrl_text, (SIDEBAR_X, controls_y + i * 30))

    def _draw_game_over(self):
        """Draw game over message"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.big_font.render("GAME OVER", True, WHITE)
        restart_text = self.font.render("Press R to restart", True, WHITE)

        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))

        self.screen.blit(game_over_text, text_rect)
        self.screen.blit(restart_text, restart_rect)

    def _draw_paused(self):
        """Draw pause message"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        paused_text = self.big_font.render("PAUSED", True, WHITE)
        text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(paused_text, text_rect)

    def _reset_game(self):
        """Reset the game state"""
        self.grid = [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = Tetromino()
        self.next_piece = Tetromino()
        self.game_over = False
        self.paused = False
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.fall_speed = INITIAL_FALL_SPEED
        self.last_fall_time = time.time()


if __name__ == "__main__":
    game = TetrisGame()
    game.run()