import pygame
import random

pygame.init()

# Define some colors
black    = (   0,   0,   0)
white    = ( 255, 255, 255)
gray     = ( 128, 128, 128)

size = (400, 500)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Tetris")

# Loop until the user clicks the close button.
done = False
clock = pygame.time.Clock()

class Shape:
    def __init__(self):
        self.x = 5
        self.y = 0
        self.color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        self.blocks = []

    def move_down(self, grid):
        if self.y + len(self.blocks) == len(grid):
            return False
        for i, row in enumerate(self.blocks):
            for j, val in enumerate(row):
                if val and grid[self.y + i + 1][self.x + j]:
                    return False
        self.y += 1
        return True

    def move_side(self, grid, dx):
        if self.x + len(self.blocks[0]) == len(grid[0]) and dx == 1:
            return
        if self.x == 0 and dx == -1:
            return
        for i, row in enumerate(self.blocks):
            for j, val in enumerate(row):
                if val and grid[self.y + i][self.x + j + dx]:
                    return
        self.x += dx

class I_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[1, 1, 1, 1]]

class J_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[1, 0, 0], [1, 1, 1]]

class L_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[0, 0, 1], [1, 1, 1]]

class O_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[1, 1], [1, 1]]

class S_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[0, 1, 1], [1, 1, 0]]

class T_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[0, 1, 0], [1, 1, 1]]

class Z_Shape(Shape):
    def __init__(self):
        super().__init__()
        self.blocks = [[1, 1, 0], [0, 1, 1]]

shapes = [I_Shape, J_Shape, L_Shape, O_Shape, S_Shape, T_Shape, Z_Shape]

# Create a grid
grid_width = 10
grid_height = 20
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

# Create a shape
shape = random.choice(shapes)()

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                shape.move_side(grid, -1)
            elif event.key == pygame.K_RIGHT:
                shape.move_side(grid, 1)
            elif event.key == pygame.K_DOWN:
                shape.move_down(grid)

    # --- Game logic should go here
    if not shape.move_down(grid):
        # Add the shape to the grid
        for i, row in enumerate(shape.blocks):
            for j, val in enumerate(row):
                if val:
                    grid[shape.y + i][shape.x + j] = 1

        # Check for full rows
        for i, row in enumerate(grid):
            if all(row):
                del grid[i]
                grid.insert(0, [0 for _ in range(grid_width)])

        # Create a new shape
        shape = random.choice(shapes)()

    # --- Screen-clearing code goes here

    # Here, we clear the screen to white. Don't put anything above this, or it will be erased with this command.

    screen.fill(black)

    # --- Drawing code should go here
    for i, row in enumerate(grid):
        for j, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, white, [j * 20 + 100, i * 20 + 50, 20, 20], 0)

    for i, row in enumerate(shape.blocks):
        for j, val in enumerate(row):
            if val:
                pygame.draw.rect(screen, shape.color, [(shape.x + j) * 20 + 100, (shape.y + i) * 20 + 50, 20, 20], 0)

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # --- Limit to 60 frames per second
    clock.tick(60)

# Close the window and quit.
pygame.quit()