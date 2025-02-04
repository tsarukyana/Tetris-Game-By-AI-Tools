import pygame
import random

# Initialize Pygame and its font module
pygame.init()
pygame.font.init()

# --------------------
# Global Game Settings
# --------------------
# Screen dimensions
s_width = 800
s_height = 700

# Playable area dimensions (a 10x20 grid)
play_width = 300  # 10 blocks * 30 pixels each
play_height = 600  # 20 blocks * 30 pixels each
block_size = 30

# Top left coordinates for the play area (to center it on the window)
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height - 50

# -------------------------
# Define the Tetris Shapes
# -------------------------
# Each shape is defined as a list of rotations.
# Each rotation is a 5x5 grid (string list) where '0' indicates a block.
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
      '..0..',
      '.00..',
      '.0...',
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

# List of all shapes and corresponding colors (RGB)
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),  # S: green
    (255, 0, 0),  # Z: red
    (0, 255, 255),  # I: cyan
    (255, 255, 0),  # O: yellow
    (255, 165, 0),  # J: orange
    (0, 0, 255),  # L: blue
    (128, 0, 128)  # T: purple
]


# ---------------------
# Piece Class
# ---------------------
class Piece:
    def __init__(self, x, y, shape):
        self.x = x  # grid x position
        self.y = y  # grid y position
        self.shape = shape
        # Color is chosen based on the shape's index
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # current rotation state


# -----------------------------
# Grid and Game Utility Functions
# -----------------------------
def create_grid(locked_positions={}):
    """
    Create a grid (20 rows x 10 columns) filled with (0,0,0) (black).
    Locked positions (where pieces have landed) are filled with their color.
    """
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid


def convert_shape_format(piece):
    """
    Convert the shape format into positions on the grid.
    The shape’s strings are parsed and the offsets computed.
    """
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                # Adjust by -2 and -4 to center the shape in the 5x5 grid
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions


def valid_space(piece, grid):
    """
    Check if the positions of the current piece are within the grid and not occupied.
    """
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True


def check_lost(positions):
    """
    Check if any of the locked positions are above the visible grid.
    """
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False


def get_shape():
    """
    Return a random new piece starting near the top middle of the grid.
    """
    return Piece(5, 0, random.choice(shapes))


def draw_text_middle(text, size, color, surface):
    """
    Draw centered text on the surface.
    """
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(
        label,
        (top_left_x + play_width / 2 - label.get_width() / 2,
         top_left_y + play_height / 2 - label.get_height() / 2)
    )


def draw_grid(surface, grid):
    """
    Draw grid lines on the play area.
    """
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        # Draw horizontal lines
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            # Draw vertical lines
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))


def clear_rows(grid, locked):
    """
    Check for complete rows in the grid and remove them.
    Moves all rows above cleared rows down.
    """
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            # Remove positions in the full row from locked positions
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except KeyError:
                    continue
    if inc > 0:
        # Shift every position above the cleared row down by the number of cleared rows.
        for key in sorted(list(locked), key=lambda x: x[1], reverse=True):
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc


def draw_next_shape(piece, surface):
    """
    Display the next piece on the side.
    """
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(
                    surface, piece.color,
                    (sx + j * block_size, sy + i * block_size, block_size, block_size), 0
                )
    surface.blit(label, (sx + 10, sy - 30))


def update_score(new_score):
    """
    Update the high score stored in a text file.
    """
    score = max_score()
    with open('scores.txt', 'w') as f:
        if int(score) > new_score:
            f.write(str(score))
        else:
            f.write(str(new_score))


def max_score():
    """
    Read the high score from a file.
    """
    try:
        with open('scores.txt', 'r') as f:
            lines = f.readlines()
            score = lines[0].strip()
    except Exception:
        score = "0"
    return score


def draw_window(surface, grid, score=0, last_score=0):
    """
    Draw the main game window including the grid, title, score, and high score.
    """
    surface.fill((0, 0, 0))

    # Draw Tetris title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (top_left_x + play_width / 2 - label.get_width() / 2, 30))

    # Current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))
    sx = top_left_x - 200
    sy = top_left_y + 200
    surface.blit(label, (sx + 20, sy + 160))

    # High score
    label = font.render('High Score: ' + last_score, 1, (255, 255, 255))
    sx = top_left_x - 200
    sy = top_left_y + 100
    surface.blit(label, (sx + 20, sy + 160))

    # Draw the grid blocks
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(
                surface, grid[i][j],
                (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0
            )

    # Draw a red border around the play area
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 4)
    draw_grid(surface, grid)


# ---------------------
# Main Game Loop
# ---------------------
def main(win):
    last_score = max_score()
    locked_positions = {}  # (x, y):(R, G, B)
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27  # lower is faster
    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        # Increase fall_time based on clock ticks
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Gradually speed up the falling pieces
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        # Move the current piece down based on fall_speed
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling (keyboard input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                if event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                if event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                if event.key == pygame.K_UP:
                    # Rotate the piece
                    current_piece.rotation = (current_piece.rotation + 1) % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = (current_piece.rotation - 1) % len(current_piece.shape)

        # Add piece to the grid for drawing
        shape_pos = convert_shape_format(current_piece)
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # If piece has landed, lock it in and get a new piece
        if change_piece:
            for pos in shape_pos:
                locked_positions[(pos[0], pos[1])] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Increase score for each cleared row
            cleared = clear_rows(grid, locked_positions)
            if cleared:
                score += cleared * 10

        # Redraw the window and update display
        draw_window(win, grid, score, last_score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check if the game is over
        if check_lost(locked_positions):
            draw_text_middle("YOU LOST!", 80, (255, 255, 255), win)
            pygame.display.update()
            pygame.time.delay(1500)
            run = False
            update_score(score)


# ---------------------
# Main Menu Function
# ---------------------
def main_menu(win):
    """
    Displays the start screen and waits for a key press to start the game.
    """
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle("Press Any Key To Play", 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()


# ---------------------
# Program Entry Point
# ---------------------
if __name__ == '__main__':
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    main_menu(win)
