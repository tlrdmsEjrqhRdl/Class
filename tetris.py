import pygame
import random

# 초기화
pygame.init()

# 화면 설정 (크기 확장)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 840
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris by Jungeon")

# 색상 정의
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

COLORS = [
    (0, 255, 255),   # I
    (255, 165, 0),   # L
    (0, 0, 255),     # J
    (255, 255, 0),   # O
    (0, 255, 0),     # S
    (128, 0, 128),   # T
    (255, 0, 0)      # Z
]

SHAPES = [
    [[[1, 1, 1, 1]], [[1], [1], [1], [1]]],  # I
    [[[0, 0, 1], [1, 1, 1]], [[1, 0], [1, 0], [1, 1]],
     [[1, 1, 1], [1, 0, 0]], [[1, 1], [0, 1], [0, 1]]],  # L
    [[[1, 0, 0], [1, 1, 1]], [[1, 1], [1, 0], [1, 0]],
     [[1, 1, 1], [0, 0, 1]], [[0, 1], [0, 1], [1, 1]]],  # J
    [[[1, 1], [1, 1]]],  # O
    [[[0, 1, 1], [1, 1, 0]], [[1, 0], [1, 1], [0, 1]]],  # S
    [[[0, 1, 0], [1, 1, 1]], [[1, 0], [1, 1], [1, 0]],
     [[1, 1, 1], [0, 1, 0]], [[0, 1], [1, 1], [0, 1]]],  # T
    [[[1, 1, 0], [0, 1, 1]], [[0, 1], [1, 1], [1, 0]]]   # Z
]

# 게임 설정
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
TOP_LEFT_X = (SCREEN_WIDTH - GRID_WIDTH * BLOCK_SIZE) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - (GRID_HEIGHT * BLOCK_SIZE) - 50

# Piece 클래스
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = COLORS[SHAPES.index(shape)]
        self.rotation = 0

def create_grid(locked_pos={}):
    grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if (x, y) in locked_pos:
                grid[y][x] = locked_pos[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    shape = piece.shape[piece.rotation % len(piece.shape)]
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell == 1:
                positions.append((piece.x + j, piece.y + i))
    return positions

def valid_space(piece, grid):
    accepted = [[(j, i) for j in range(GRID_WIDTH) if grid[i][j] == BLACK] for i in range(GRID_HEIGHT)]
    accepted = [pos for row in accepted for pos in row]
    for pos in convert_shape_format(piece):
        if pos not in accepted and pos[1] > -1:
            return False
    return True

def check_lost(positions):
    return any(y < 1 for (x, y) in positions)

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text(surface, text, size, x, y):
    font = pygame.font.SysFont('malgungothic', size, bold=True)
    label = font.render(text, 1, WHITE)
    surface.blit(label, (x - label.get_width() / 2, y))

def draw_grid(surface, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    for i in range(GRID_HEIGHT + 1):
        pygame.draw.line(surface, GRAY, (TOP_LEFT_X, TOP_LEFT_Y + i * BLOCK_SIZE), (TOP_LEFT_X + GRID_WIDTH * BLOCK_SIZE, TOP_LEFT_Y + i * BLOCK_SIZE))
    for j in range(GRID_WIDTH + 1):
        pygame.draw.line(surface, GRAY, (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j * BLOCK_SIZE, TOP_LEFT_Y + GRID_HEIGHT * BLOCK_SIZE))

def clear_rows(grid, locked):
    cleared = 0
    for i in range(len(grid) - 1, -1, -1):
        if BLACK not in grid[i]:
            cleared += 1
            for j in range(GRID_WIDTH):
                try:
                    del locked[(j, i)]
                except:
                    pass
    if cleared:
        for key in sorted(locked.keys(), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < i:
                new_key = (x, y + cleared)
                locked[new_key] = locked.pop(key)
    return cleared

def draw_window(surface, grid, score, held):
    surface.fill(BLACK)
    draw_text(surface, 'TETRIS', 65, SCREEN_WIDTH / 2, 30)
    draw_text(surface, 'Score: ' + str(score), 30, SCREEN_WIDTH / 2, 100)

    # Hold 블럭
    if held:
        draw_text(surface, 'Hold', 25, 100, 200)
        shape = held.shape[0]
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(surface, held.color, (40 + j * BLOCK_SIZE, 220 + i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X - 2, TOP_LEFT_Y - 2, GRID_WIDTH * BLOCK_SIZE + 4, GRID_HEIGHT * BLOCK_SIZE + 4), 0)
    draw_grid(surface, grid)
    pygame.display.update()

# 게임 루프
def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    current_piece = get_shape()
    next_piece = get_shape()
    hold_piece = None
    hold_used = False
    change_piece = False
    score = 0

    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.4
    run = True

    while run:
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid):
                current_piece.y -= 1
                change_piece = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

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
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                if event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1
                    change_piece = True
                if event.key == pygame.K_c and not hold_used:
                    if not hold_piece:
                        hold_piece = current_piece
                        current_piece = next_piece
                        next_piece = get_shape()
                    else:
                        hold_piece, current_piece = current_piece, hold_piece
                        current_piece.x, current_piece.y = 5, 0
                    hold_used = True

        shape_pos = convert_shape_format(current_piece)
        for x, y in shape_pos:
            if y >= 0:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                locked_positions[pos] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            hold_used = False
            score += clear_rows(grid, locked_positions) * 10

        if check_lost(locked_positions):
            draw_text(screen, "GAME OVER", 60, SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            pygame.display.update()
            pygame.time.delay(2000)
            run = False

        draw_window(screen, grid, score, hold_piece)
        grid = create_grid(locked_positions)

if __name__ == '__main__':
    main()
    pygame.quit()
