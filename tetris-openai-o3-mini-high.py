import pygame
import random

# Initialize fonts in pygame
pygame.font.init()

#######################
# Global Configuration
#######################

# Screen dimensions (you can adjust these as needed)
s_width = 300   # overall window width
s_height = 600  # overall window height

# Play area dimensions (10 columns x 20 rows typical for Tetris)
play_width = 300  # 10 blocks wide (each block is 30 pixels)
play_height = 600  # 20 blocks tall (each block is 30 pixels)
block_size = 30   # size of a single block

# Top left position of the play area
top_left_x = (s_width - play_width) // 2
top_left_y = s_height - play_height

############################
# Define Tetris Shapes
############################

# Each shape is defined as a list of strings for each rotation.
# '0' represents a filled block, and '.' represents an empty space.
# The shapes are defined in a 5x5 grid so that rotations are easier to manage.

S = [['.....',
      '......',
      '..00..',
      '.00...',
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

# List of all shapes and corresponding colors
shapes = [S, Z, I, O, J, L, T]
shape_colors = [
    (0, 255, 0),    # S - green
    (255, 0, 0),    # Z - red
    (0, 255, 255),  # I - cyan
    (255, 255, 0),  # O - yellow
    (255, 165, 0),  # J - orange
    (0, 0, 255),    # L - blue
    (128, 0, 128)   # T - purple
]

############################
# Piece Class Definition
############################

class Piece:
    def __init__(self, x, y, shape):
        self.x = x  # x position on grid (in blocks)
        self.y = y  # y position on grid (in blocks)
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0  # initial rotation state

############################
# Helper Functions
############################

def create_grid(locked_positions={}):
    """
    Create a 2D grid (list of lists) representing the play area.
    Each cell holds a color (RGB tuple); (0,0,0) means empty.
    """
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]

    # Fill in the locked (already placed) positions
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j, i) in locked_positions:
                grid[i][j] = locked_positions[(j, i)]
    return grid

def convert_shape_format(piece):
    """
    Convert the shape format into actual positions on the grid.
    The shape is a list of strings (5x5); we map '0' to actual grid positions.
    The offsets (-2 for x, -4 for y) center the shape.
    """
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j - 2, piece.y + i - 4))
    return positions

def valid_space(piece, grid):
    """
    Check if the current positions of the piece are all valid (empty) in the grid.
    """
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0, 0, 0)] for i in range(20)]
    accepted_positions = [pos for sub in accepted_positions for pos in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        # Check if the position is out of bounds (but ignore positions above the grid)
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(locked_positions):
    """
    Check if any of the locked positions are above the top of the grid.
    """
    for pos in locked_positions:
        x, y = pos
        if y < 1:
            return True
    return False

def get_shape():
    """
    Return a new random piece.
    """
    return Piece(5, 0, random.choice(shapes))

def draw_text_middle(text, size, color, surface):
    """
    Draw text in the middle of the given surface.
    """
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2),
                         top_left_y + play_height / 2 - (label.get_height() / 2)))

def draw_grid(surface, grid):
    """
    Draw the grid lines on the play area.
    """
    sx = top_left_x
    sy = top_left_y
    for i in range(len(grid)):
        # Horizontal lines
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size),
                         (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            # Vertical lines
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy),
                             (sx + j * block_size, sy + play_height))

def clear_rows(grid, locked):
    """
    Check for complete rows and clear them. Then, move every row above down.
    Each cleared row adds to the score.
    """
    inc = 0
    # Start from the bottom of the grid
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        # If the row has no empty blocks
        if (0, 0, 0) not in row:
            inc += 1
            ind = i
            # Remove the positions in this row from the locked positions
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    # Move every locked position above down by the number of cleared rows
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1], reverse=True):
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)
    return inc

def draw_next_shape(piece, surface):
    """
    Draw the next shape that will fall on the side of the play area.
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
                # Draw each block of the shape
                pygame.draw.rect(surface, piece.color,
                                 (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)
    surface.blit(label, (sx + 10, sy - 30))

def draw_window(surface, grid, score=0):
    """
    Draw the entire game window: background, grid, title, score.
    """
    surface.fill((0, 0, 0))  # fill background with black

    # Draw the title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('Tetris', 1, (255, 255, 255))
    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # Draw the current score
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Score: ' + str(score), 1, (255, 255, 255))
    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    surface.blit(label, (sx + 20, sy + 160))

    # Draw each block in the grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j],
                             (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # Draw grid lines and border
    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

############################
# Main Game Loop
############################

def main(win):
    locked_positions = {}  # dictionary to hold locked (settled) pieces
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0  # timer for piece falling
    fall_speed = 0.27  # initial fall speed (in seconds)

    level_time = 0
    score = 0

    while run:
        grid = create_grid(locked_positions)
        # Update timers
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase difficulty over time by increasing fall speed
        if level_time / 1000 > 5:
            level_time = 0
            if fall_speed > 0.12:
                fall_speed -= 0.005

        # Handle automatic piece falling
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling (user input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()

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

        shape_pos = convert_shape_format(current_piece)

        # Draw the current piece on the grid
        for pos in shape_pos:
            x, y = pos
            if y > -1:  # only draw if inside the visible grid
                grid[y][x] = current_piece.color

        # If the piece has reached its final position, lock it and get the next piece
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            # Clear any filled rows and update the score (e.g., 10 points per cleared row)
            cleared_rows = clear_rows(grid, locked_positions)
            score += cleared_rows * 10

        draw_window(win, grid, score)
        draw_next_shape(next_piece, win)
        pygame.display.update()

        # Check if the player has lost (if blocks reach the top)
        if check_lost(locked_positions):
            draw_text_middle("YOU LOST", 80, (255, 255, 255), win)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

def main_menu(win):
    """
    Display the start screen until the user presses a key.
    """
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle("Press any key to begin.", 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(win)
    pygame.quit()

############################
# Program Entry Point
############################

if __name__ == '__main__':
    # Create the game window
    win = pygame.display.set_mode((s_width, s_height))
    pygame.display.set_caption('Tetris')
    main_menu(win)
