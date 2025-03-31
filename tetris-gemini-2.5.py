import pygame
import random
import sys
import time

# --- Constants ---
# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
PLAY_WIDTH = 300  # 300 // 30 = 10 blocks wide
PLAY_HEIGHT = 600  # 600 // 30 = 20 blocks high
BLOCK_SIZE = 30

# Grid position on screen
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT

# Grid dimensions
GRID_COLS = 10
GRID_ROWS = 20

# Colors (RGB)
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

# Tetromino Shapes (using coordinates relative to top-left of a 4x4 grid)
# Indexed by rotation state
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '...0.',
      '..00.',
      '..0..',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# List of shapes and their corresponding colors
SHAPES = [S, Z, I, O, J, L, T]
SHAPE_COLORS = [GREEN, RED, CYAN, YELLOW, BLUE, ORANGE, MAGENTA]


# --- Piece Class ---
class Piece:
    def __init__(self, x, y, shape_index):
        self.x = x
        self.y = y
        self.shape_index = shape_index
        self.shape = SHAPES[shape_index]
        self.color = SHAPE_COLORS[shape_index]
        self.rotation = 0  # Index for shape rotation state

    def get_formatted_shape(self):
        """ Returns the current rotation's shape definition """
        return self.shape[self.rotation % len(self.shape)]

    def get_positions(self):
        """ Returns a list of (row, col) grid coordinates for the piece's blocks """
        positions = []
        shape_format = self.get_formatted_shape()
        # Iterate through the 5x5 format string
        for i, line in enumerate(shape_format):
            row = list(line)
            for j, column in enumerate(row):
                if column == '0':
                    # Adjust for piece's top-left position (self.x, self.y)
                    # The format is relative, usually centered, adjust row/col offsets
                    # Example: A '.' at (0,0) in format maps to (y-2, x-2) approx
                    # Simpler: Assume format's top-left (0,0) maps to piece's (y,x)
                    positions.append((self.y + i, self.x + j))

        # Adjust offsets if needed based on how shapes are defined (center vs top-left)
        # This current implementation assumes the '0's are relative to piece's (y,x)
        # A common convention is relative to a pivot point, often near the center.
        # Let's adjust slightly to center better for a 5x5 representation
        offset_y = -2
        offset_x = -2
        final_positions = []
        for pos in positions:
            final_positions.append((pos[0] + offset_y, pos[1] + offset_x))

        return final_positions


# --- Game Functions ---

def create_grid(locked_positions={}):
    """ Creates the game grid (list of lists) """
    # Initialize grid with black (empty) cells
    grid = [[BLACK for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    # Fill grid with colors of landed pieces
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if (c, r) in locked_positions:
                color = locked_positions[(c, r)]
                grid[r][c] = color
    return grid


def convert_shape_format(piece):
    """ Converts the string format shape into grid coordinates """
    positions = []
    shape_format = piece.get_formatted_shape()
    # Iterate through the 5x5 format string
    for i, line in enumerate(shape_format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Relative positions from piece's top-left (y, x)
                # Subtracting 2 centers the 5x5 shape format around the (y,x) point
                positions.append((piece.y + i - 2, piece.x + j - 2))
    return positions


def is_valid_space(piece, grid):
    """ Checks if the piece's current position is valid (within bounds, not colliding) """
    # Get all possible grid positions (including empty cells)
    accepted_pos = [[(c, r) for c in range(GRID_COLS) if grid[r][c] == BLACK] for r in range(GRID_ROWS)]
    # Flatten the list
    accepted_pos = [pos for sublist in accepted_pos for pos in sublist]

    formatted_shape = convert_shape_format(piece)

    for pos in formatted_shape:
        col, row = pos
        # Check if outside grid boundaries (left, right, bottom)
        if not (0 <= col < GRID_COLS and row < GRID_ROWS):
            return False
        # Check if below the top boundary (allow spawning above screen)
        if row < 0:
            continue  # Part of the shape is above the screen, which is okay initially
        # Check if the position is already occupied by a locked piece
        if (col, row) not in accepted_pos:
            return False
    return True


def check_lost(positions):
    """ Checks if any block is above the top boundary """
    for pos in positions:
        x, y = pos
        if y < 0:  # Actually checks if y < 0, should be y < 1 based on typical Tetris rules
            # Correct logic: Game over if a piece locks entirely above row 0 (or partially in row 0)
            # Simplified check: If any part locks above y=0 (index 0)
            # A better check is done *after* locking a piece. If a new piece spawns and
            # immediately collides, it's game over. Let's implement that instead.
            pass  # We will check game over on piece spawn

    # A better check: If a piece is locked and any part is above row 0 (index 0)
    # This check is typically done *after* locking.
    for pos in positions:
        x, y = pos
        if y < 0:  # If any block locks above the visible grid
            return True
    return False


def get_shape(shapes, shape_colors):
    """ Returns a random new piece """
    shape_index = random.randrange(len(shapes))
    # Initial position: Center horizontally, slightly above the visible grid
    return Piece(GRID_COLS // 2, 0, shape_index)  # Start at col 5, row 0 (top)


def draw_text_middle(surface, text, size, color):
    """ Draws text centered on the screen """
    font = pygame.font.SysFont('comicsansms', size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (SCREEN_WIDTH / 2 - label.get_width() / 2, SCREEN_HEIGHT / 2 - label.get_height() / 2))


def draw_grid_lines(surface, grid):
    """ Draws the grid lines on the play area """
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y
    # Horizontal lines
    for i in range(GRID_ROWS + 1):
        pygame.draw.line(surface, GRAY, (sx, sy + i * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + i * BLOCK_SIZE))
    # Vertical lines
    for j in range(GRID_COLS + 1):
        pygame.draw.line(surface, GRAY, (sx + j * BLOCK_SIZE, sy), (sx + j * BLOCK_SIZE, sy + PLAY_HEIGHT))


def clear_rows(grid, locked):
    """ Clears completed rows and shifts rows above down """
    rows_cleared = 0
    new_locked = {}
    rows_to_check = list(range(GRID_ROWS))
    rows_to_check.reverse()  # Check from bottom up

    rows_to_keep = []  # Rows indices that are *not* full

    for r in rows_to_check:
        row_full = True
        for c in range(GRID_COLS):
            if grid[r][c] == BLACK:
                row_full = False
                break
        if row_full:
            rows_cleared += 1
            # Don't add this row index to rows_to_keep
        else:
            rows_to_keep.insert(0, r)  # Add non-full rows to the top of the list

    if rows_cleared > 0:
        # Create new locked positions based on kept rows
        kept_locked_positions = {}
        for (c, r) in locked:
            if r in rows_to_keep:
                kept_locked_positions[(c, r)] = locked[(c, r)]

        # Shift rows down
        # Calculate how much each kept row needs to shift down
        shift_map = {kept_row: GRID_ROWS - 1 - i for i, kept_row in enumerate(reversed(rows_to_keep))}

        for (c, r) in kept_locked_positions:
            new_r = shift_map[r]
            new_locked[(c, new_r)] = kept_locked_positions[(c, r)]

        return rows_cleared, new_locked
    else:
        return 0, locked  # No changes


def draw_next_shape(piece, surface):
    """ Draws the next piece preview """
    font = pygame.font.SysFont('comicsansms', 30)
    label = font.render('Next Shape', 1, WHITE)

    sx = TOP_LEFT_X + PLAY_WIDTH + 40  # Position for next shape display
    sy = TOP_LEFT_Y + PLAY_HEIGHT / 2 - 100
    format = piece.get_formatted_shape()

    surface.blit(label, (sx, sy - 30))

    # Draw the piece shape centered in the preview area
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Adjust drawing position to center the 5x5 representation
                pygame.draw.rect(surface, piece.color,
                                 (sx + (j - 1.5) * BLOCK_SIZE, sy + (i - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(surface, GRAY,
                                 (sx + (j - 1.5) * BLOCK_SIZE, sy + (i - 1) * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE),
                                 1)  # Border


def draw_window(surface, grid, score=0, level=1, lines=0):
    """ Draws everything onto the game window """
    surface.fill(BLACK)  # Black background

    # Title
    font = pygame.font.SysFont('comicsansms', 40)
    label = font.render('TETRIS', 1, WHITE)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH / 2 - (label.get_width() / 2), 30))

    # Score, Level, Lines
    font = pygame.font.SysFont('comicsansms', 25)
    score_label = font.render(f'Score: {score}', 1, WHITE)
    level_label = font.render(f'Level: {level}', 1, WHITE)
    lines_label = font.render(f'Lines: {lines}', 1, WHITE)

    sx_info = TOP_LEFT_X - 120  # Position for score/level info
    sy_info = TOP_LEFT_Y + 100

    surface.blit(score_label, (sx_info, sy_info))
    surface.blit(level_label, (sx_info, sy_info + 40))
    surface.blit(lines_label, (sx_info, sy_info + 80))

    # Draw the grid cells based on their colors
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            pygame.draw.rect(surface, grid[r][c],
                             (TOP_LEFT_X + c * BLOCK_SIZE, TOP_LEFT_Y + r * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # Draw the grid border and lines
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)  # Border around play area
    draw_grid_lines(surface, grid)

    # draw_next_shape is called separately in main loop after grid update


# --- Main Game Loop ---
def main(win):
    locked_positions = {}  # (x, y): (r, g, b)
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape(SHAPES, SHAPE_COLORS)
    next_piece = get_shape(SHAPES, SHAPE_COLORS)
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0  # Time counter for increasing speed
    fall_speed = 0.50  # Seconds per grid block drop initially (Higher is slower)
    base_fall_speed = fall_speed  # Store initial speed
    paused = False

    score = 0
    level = 1
    lines_cleared_total = 0

    while run:
        grid = create_grid(locked_positions)  # Update grid based on locked pieces
        fall_time += clock.get_rawtime()  # Time since last frame in ms
        level_time += clock.get_rawtime()
        clock.tick()  # Control frame rate

        # --- Auto Fall Logic ---
        if not paused:
            # Convert fall_speed (seconds) to milliseconds
            if fall_time / 1000 >= fall_speed:
                fall_time = 0
                current_piece.y += 1
                # Check if the new position is valid
                if not is_valid_space(current_piece, grid) or current_piece.y > GRID_ROWS:
                    # If invalid after moving down, it hit something or went out of bounds
                    current_piece.y -= 1  # Revert the move
                    change_piece = True  # Lock the piece

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause Toggle
                    paused = not paused

                if not paused:
                    if event.key == pygame.K_LEFT:
                        current_piece.x -= 1
                        if not is_valid_space(current_piece, grid):
                            current_piece.x += 1  # Revert if invalid

                    elif event.key == pygame.K_RIGHT:
                        current_piece.x += 1
                        if not is_valid_space(current_piece, grid):
                            current_piece.x -= 1  # Revert

                    elif event.key == pygame.K_DOWN:
                        # Soft drop: Move down faster
                        current_piece.y += 1
                        if not is_valid_space(current_piece, grid):
                            current_piece.y -= 1  # Revert
                            # Optional: Could lock piece immediately on down press collision
                            # change_piece = True
                        else:
                            score += 1  # Small score bonus for soft drop

                    elif event.key == pygame.K_UP:
                        # Rotate
                        current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                        if not is_valid_space(current_piece, grid):
                            # Basic wall kick attempt (try moving left/right) - Very simple version
                            original_x = current_piece.x

                            # Try moving left
                            current_piece.x -= 1
                            if is_valid_space(current_piece, grid):
                                continue  # Keep rotated and moved position
                            current_piece.x = original_x  # Revert move left

                            # Try moving right
                            current_piece.x += 1
                            if is_valid_space(current_piece, grid):
                                continue  # Keep rotated and moved position
                            current_piece.x = original_x  # Revert move right

                            # If still invalid, revert rotation
                            current_piece.rotation = (current_piece.rotation - 1 + len(current_piece.shape)) % len(
                                current_piece.shape)


                    elif event.key == pygame.K_SPACE:
                        # Hard drop
                        original_y = current_piece.y
                        while is_valid_space(current_piece, grid):
                            current_piece.y += 1
                        current_piece.y -= 1  # Move back to last valid position
                        score += (current_piece.y - original_y) * 2  # Score bonus for hard drop distance
                        change_piece = True  # Lock immediately

        # --- Lock Piece Logic ---
        if change_piece and not paused:
            piece_pos = convert_shape_format(current_piece)
            for pos in piece_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color

            # --- Check for Cleared Rows ---
            rows_cleared_now, locked_positions = clear_rows(grid, locked_positions)

            # Update Score based on lines cleared at once
            if rows_cleared_now == 1:
                score += 40 * level
            elif rows_cleared_now == 2:
                score += 100 * level
            elif rows_cleared_now == 3:
                score += 300 * level
            elif rows_cleared_now >= 4:  # Tetris!
                score += 1200 * level

            lines_cleared_total += rows_cleared_now

            # --- Update Level and Speed ---
            # Simple level up every 10 lines
            new_level = (lines_cleared_total // 10) + 1
            if new_level > level:
                level = new_level
                # Increase speed (decrease fall_speed) - Make sure it doesn't get too fast
                fall_speed = max(0.1, base_fall_speed - (level - 1) * 0.05)
                print(f"Level Up! Level: {level}, Fall Speed: {fall_speed:.2f}")

            # --- Spawn Next Piece ---
            current_piece = next_piece
            next_piece = get_shape(SHAPES, SHAPE_COLORS)
            change_piece = False

            # --- Check Game Over ---
            # If the new piece spawns in an invalid position, game over
            if not is_valid_space(current_piece, grid):
                run = False  # End the game loop

        # --- Drawing ---
        # Draw static elements (grid, background, text)
        draw_window(win, grid, score, level, lines_cleared_total)

        # Draw the current piece
        if not paused:
            piece_pos = convert_shape_format(current_piece)
            for pos in piece_pos:
                # Only draw blocks that are within the visible grid area
                if pos[1] >= 0:  # Check row index (y)
                    pygame.draw.rect(win, current_piece.color,
                                     (TOP_LEFT_X + pos[0] * BLOCK_SIZE, TOP_LEFT_Y + pos[1] * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)
                    pygame.draw.rect(win, GRAY,  # Border for current piece
                                     (TOP_LEFT_X + pos[0] * BLOCK_SIZE, TOP_LEFT_Y + pos[1] * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 1)

        # Draw the next piece preview
        draw_next_shape(next_piece, win)

        # Draw Pause message
        if paused:
            draw_text_middle(win, "PAUSED", 60, WHITE)

        # Update the display
        pygame.display.update()

    # --- Game Over Screen ---
    draw_text_middle(win, f"GAME OVER! Score: {score}", 50, RED)
    pygame.display.update()
    pygame.time.wait(3000)  # Wait 3 seconds before closing


def main_menu(win):
    """ Displays the main menu """
    run = True
    while run:
        win.fill(BLACK)
        draw_text_middle(win, 'Press Any Key To Play Tetris', 40, WHITE)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                main(win)  # Start the game

    pygame.quit()


# --- Initialization ---
if __name__ == "__main__":
    pygame.font.init()
    pygame.mixer.init()  # If you want to add sound later

    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")

    main_menu(win)  # Start with the main menu