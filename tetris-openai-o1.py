import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# ---------------------------
# Global Game Configuration
# ---------------------------
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 500
PLAY_WIDTH = 300  # 10 columns * 30 size
PLAY_HEIGHT = 600  # 20 rows * 30 size
BLOCK_SIZE = 30

# Rows and columns based on Tetris standard
GRID_ROWS = 20
GRID_COLS = 10

# Position of the play area on the screen
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 20

# Define shapes (Tetrominoes)
# Each shape is represented by a list of strings.
# Each string is a row in the shape's grid.
# "0" means the block is part of the shape; "." means empty space.
SHAPES = [
    [".....",
     ".....",
     "..00.",
     "..00.",
     "....."],  # Square (O shape)

    [".....",
     "..0..",
     "..0..",
     "..0..",
     "..0.."],  # Line (I shape)

    [".....",
     ".....",
     "..00.",
     ".00..",
     "....."],  # S shape

    [".....",
     ".....",
     ".00..",
     "..00.",
     "....."],  # Z shape

    [".....",
     "..0..",
     "..000",
     ".....",
     "....."],  # T shape

    [".....",
     ".00..",
     "..0..",
     "..0..",
     "....."],  # J shape

    [".....",
     "..00.",
     "..0..",
     "..0..",
     "....."]  # L shape
]

# Colors for each shape (in RGB)
SHAPE_COLORS = [
    (255, 215, 0),  # Yellow (Square)
    (0, 255, 255),  # Cyan (Line)
    (0, 255, 0),  # Green (S)
    (255, 0, 0),  # Red (Z)
    (128, 0, 128),  # Purple (T)
    (0, 0, 255),  # Blue (J)
    (255, 165, 0)  # Orange (L)
]


class Piece:
    """
    Represents a single Tetris piece with:
    - shape: the 2D pattern (list of strings)
    - color: RGB color
    - x, y positions on the grid (upper-left of the bounding box)
    - rotation state
    """

    def __init__(self, x, y, shape, color):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = 0  # index indicating which rotation is current

    def rotate(self):
        """Changes the rotation of the piece (mod 4)."""
        self.rotation = (self.rotation + 1) % 4


def create_grid(locked_positions={}):
    """
    Create a 2D grid (list of lists) for the playing field.
    locked_positions is a dict that maps (col, row) -> color for tiles that are already placed.
    """
    grid = [[(0, 0, 0) for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

    for (col, row), color in locked_positions.items():
        if row >= 0:
            grid[row][col] = color

    return grid


def convert_shape_format(piece):
    """
    Convert the piece's shape strings into a list of (x, y) grid positions.
    Apply the current rotation of the piece.
    """
    positions = []
    shape_format = piece.shape[piece.rotation % len(piece.shape)]

    # shape_format is a list of strings, each representing a row
    # or a single string with new lines. Usually we store shape as a list of strings
    # so let's handle it carefully.
    if isinstance(shape_format, str):
        shape_format = shape_format.split('\n') if '\n' in shape_format else [shape_format]

    # If the shape has multiple rotations stored as separate lists, you might see code
    # that cycles through piece.rotation. In this code, each shape is just one layout
    # but we interpret rotation by rotating visually. We'll do that in a simplified manner:
    # We'll parse the shape as if it's not rotated, then rotate it in 90-degree increments.

    # For an actual robust rotation, you'd do something more advanced. Here, we'll keep
    # the shape as a 5x5 minimal bounding box and rotate by matrix transformation.

    # We'll handle the shape as a 2D array
    shape_matrix = []
    for row in piece.shape:
        shape_matrix.append(list(row))

    # shape_matrix is a list of 5 strings, each string of length 5.
    # Let's rotate it 'piece.rotation' times by 90 degrees:
    for _ in range(piece.rotation):
        shape_matrix = list(zip(*shape_matrix[::-1]))
        # After the zip, we might have tuples, so convert each row to a list (or str)
        shape_matrix = [list(row) for row in shape_matrix]

    # Now flatten shape_matrix to get the positions of '0'
    for i, row in enumerate(shape_matrix):
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    return positions


def valid_space(piece, grid):
    """
    Check if the piece's positions are within valid spaces on the grid
    (i.e., inside boundary and not colliding with locked positions).
    """
    accepted_positions = [
        [(col, row) for col in range(GRID_COLS) if grid[row][col] == (0, 0, 0)]
        for row in range(GRID_ROWS)
    ]
    accepted_positions = [col_row for row in accepted_positions for col_row in row]

    formatted_positions = convert_shape_format(piece)

    for pos in formatted_positions:
        x, y = pos
        if x < 0 or x >= GRID_COLS or y < 0 or y >= GRID_ROWS:
            return False
        if (x, y) not in accepted_positions:
            return False

    return True


def check_lost(positions):
    """If any locked position is above the top of the screen, the player loses."""
    for (col, row) in positions:
        if row < 1:
            return True
    return False


def get_shape():
    """Return a new random Piece."""
    i = random.randint(0, len(SHAPES) - 1)
    shape_5x5 = SHAPES[i]
    color = SHAPE_COLORS[i]
    return Piece(GRID_COLS // 2 - 2, 0, SHAPES[i:], color)


def draw_text_middle(surface, text, size, color):
    """Draw text in the middle of the screen."""
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)
    label_rect = label.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    surface.blit(label, label_rect)


def draw_grid(surface, grid):
    """Draw the grid lines for the Tetris board."""
    for row in range(GRID_ROWS):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X, TOP_LEFT_Y + row * BLOCK_SIZE),
                         (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + row * BLOCK_SIZE))
    for col in range(GRID_COLS):
        pygame.draw.line(surface, (128, 128, 128), (TOP_LEFT_X + col * BLOCK_SIZE, TOP_LEFT_Y),
                         (TOP_LEFT_X + col * BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))


def clear_rows(grid, locked_positions):
    """
    Check if any rows are completely filled, remove them and shift everything above down.
    Return the number of cleared rows.
    """
    cleared_rows = 0
    for row in range(GRID_ROWS - 1, -1, -1):
        if (0, 0, 0) not in grid[row]:
            # This row is full; remove it
            cleared_rows += 1
            # Move row above down
            for col in range(GRID_COLS):
                try:
                    del locked_positions[(col, row)]
                except KeyError:
                    pass
    if cleared_rows > 0:
        # Shift rows down
        # Start from bottom row and move upwards
        for (col, row) in sorted(list(locked_positions), key=lambda x: x[1])[::-1]:
            new_row = row + cleared_rows
            locked_positions[(col, new_row)] = locked_positions.pop((col, row))

    return cleared_rows


def draw_next_shape(piece, surface):
    """Draw the next shape preview on the right side of the screen."""
    font = pygame.font.SysFont("comicsans", 30)
    label = font.render("Next Shape", 1, (255, 255, 255))

    start_x = TOP_LEFT_X + PLAY_WIDTH + 20
    start_y = TOP_LEFT_Y + PLAY_HEIGHT // 2 - 100

    surface.blit(label, (start_x, start_y - 30))

    shape_matrix = []
    for row in piece.shape:
        shape_matrix.append(list(row))

    # Rotate piece zero times (just show initial layout)
    for i, row in enumerate(shape_matrix):
        for j, col in enumerate(row):
            if col == '0':
                pygame.draw.rect(surface, piece.color,
                                 (start_x + j * BLOCK_SIZE,
                                  start_y + i * BLOCK_SIZE,
                                  BLOCK_SIZE, BLOCK_SIZE), 0)


def draw_window(surface, grid, score=0):
    """Draw the main game window (grid, score, etc.)."""
    surface.fill((0, 0, 0))

    # Title
    font = pygame.font.SysFont("comicsans", 60)
    label = font.render("TETRIS", 1, (255, 255, 255))
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH // 2 - label.get_width() // 2, 30))

    # Current Score
    font = pygame.font.SysFont("comicsans", 30)
    score_label = font.render(f"Score: {score}", 1, (255, 255, 255))
    surface.blit(score_label, (TOP_LEFT_X - 120, TOP_LEFT_Y + 50))

    # Draw the play area
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            pygame.draw.rect(surface, grid[row][col],
                             (TOP_LEFT_X + col * BLOCK_SIZE,
                              TOP_LEFT_Y + row * BLOCK_SIZE,
                              BLOCK_SIZE, BLOCK_SIZE), 0)

    # Draw the grid lines
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0),
                     (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 5)


def main(surface):
    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.35  # Lower = faster drop
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Piece falls automatically
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                # Lock piece positions in the grid
                for pos in convert_shape_format(current_piece):
                    locked_positions[(pos[0], pos[1])] = current_piece.color
                change_piece = True

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1

                elif event.key == pygame.K_DOWN:
                    # Move piece down faster
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

                elif event.key == pygame.K_UP:
                    # Rotate
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        # Revert rotation
                        current_piece.rotation = (current_piece.rotation - 1) % 4

        # If piece locked, generate a new piece
        if change_piece:
            cleared_rows = clear_rows(grid, locked_positions)
            score += cleared_rows * 10
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Check if game over
            if check_lost(locked_positions):
                run = False

        draw_window(surface, grid, score)
        draw_next_shape(next_piece, surface)
        pygame.display.update()

    # Display "You Lost"
    draw_text_middle(surface, "YOU LOST", 40, (255, 255, 255))
    pygame.display.update()
    pygame.time.delay(2000)


def main_menu():
    """Main menu that starts the game."""
    surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris')

    run = True
    while run:
        surface.fill((0, 0, 0))
        draw_text_middle(surface, "Press Any Key To Play", 30, (255, 255, 255))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(surface)
    pygame.quit()


if __name__ == "__main__":
    main_menu()
