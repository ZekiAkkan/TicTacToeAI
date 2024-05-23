import pygame
import math
from database import DataBase
import tensorflow as tf
from tensorflow import keras
import numpy as np

# TensorFlow modelini yükle
try:
    model = keras.models.load_model("tic_tac_toe_model_improved.keras")
except Exception as e:
    print(f"Model yüklenirken bir hata oluştu: {e}")
    exit()

# Oyun tahtası
board = [[0 for _ in range(3)] for _ in range(3)]

# İşaretler
PLAYER_X = 1
PLAYER_O = -1
EMPTY = 0

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Oyun alanı
WIDTH, HEIGHT = 300, 300
LINE_WIDTH = 5
CELL_SIZE = WIDTH // 3

# Pygame başlatma
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("XOX Game")
clock = pygame.time.Clock()

# Oyun tahtasını çiz
def draw_board():
    screen.fill(WHITE)
    for i in range(1, 3):
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), LINE_WIDTH)

# X ve O çiz
def draw_X(x, y):
    padding = CELL_SIZE * 0.2  # X işaretinin hücre kenarlarından uzaklığı
    pygame.draw.line(screen, RED, 
                     (x * CELL_SIZE + padding, y * CELL_SIZE + padding), 
                     (x * CELL_SIZE + CELL_SIZE - padding, y * CELL_SIZE + CELL_SIZE - padding), 
                     LINE_WIDTH)
    pygame.draw.line(screen, RED, 
                     (x * CELL_SIZE + padding, y * CELL_SIZE + CELL_SIZE - padding), 
                     (x * CELL_SIZE + CELL_SIZE - padding, y * CELL_SIZE + padding), 
                     LINE_WIDTH)

def draw_O(x, y):
    pygame.draw.circle(screen, BLUE, (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3, LINE_WIDTH)

# Oyun tahtasını güncelle
def update_board():
    for i in range(3):
        for j in range(3):
            if board[i][j] == PLAYER_X:
                draw_X(j, i)
            elif board[i][j] == PLAYER_O:
                draw_O(j, i)

# Oyun durumu kontrolü
def check_winner():
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] != EMPTY:
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] != EMPTY:
            return board[0][i]
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] != EMPTY:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] != EMPTY:
        return board[0][2]
    return None

# Oyun alanı dolu mu?
def is_board_full():
    return all([cell != EMPTY for row in board for cell in row])

# En iyi hamleyi TensorFlow modeli ile bulma
def find_best_move():
    # Board'u modele uygun formatta hazırlayalım
    flat_board = np.array(board).flatten().astype(np.float32)
    flat_board[flat_board == PLAYER_X] = 1
    flat_board[flat_board == PLAYER_O] = 2
    flat_board[flat_board == EMPTY] = 0

    # Modelden tahmin yap
    predictions = model.predict(flat_board.reshape(1, -1)).flatten()

    # Geçerli en iyi hamleyi bul
    best_move = np.argmax(predictions)
    row, col = divmod(best_move, 3)

    if board[row][col] == EMPTY:
        return row, col
    else:
        # Eğer model dolu bir hücre seçerse, en yüksek puanlı diğer hücreleri dene
        sorted_moves = np.argsort(predictions)[::-1]
        for move in sorted_moves:
            row, col = divmod(move, 3)
            if board[row][col] == EMPTY:
                return row, col
        return None

# Kazanan mesajı
def show_winner(winner):
    font = pygame.font.Font(None, 74)
    if winner == PLAYER_X:
        text = font.render("X Wins!", True, RED)
    elif winner == PLAYER_O:
        text = font.render("O Wins!", True, BLUE)
    else:
        text = font.render("It's a tie!", True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(3000)

# Oyun döngüsü
def main():
    db = DataBase()
    current_player = PLAYER_X  # İlk oyuncu X ile başlasın
    running = True

    # İlk hamle olarak yapay zeka (X) oynar
    move = find_best_move()
    if move:
        row, col = move
        board[row][col] = PLAYER_X
        db.veriEkle(board, PLAYER_X, row * 3 + col)
        current_player = PLAYER_O

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and current_player == PLAYER_O:
                x, y = pygame.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE
                if board[row][col] == EMPTY:
                    board[row][col] = PLAYER_O
                    db.veriEkle(board, PLAYER_O, row * 3 + col)
                    winner = check_winner()
                    if winner is not None or is_board_full():
                        running = False
                    else:
                        current_player = PLAYER_X

        if current_player == PLAYER_X and running:
            move = find_best_move()
            if move:
                row, col = move
                board[row][col] = PLAYER_X
                db.veriEkle(board, PLAYER_X, row * 3 + col)
                winner = check_winner()
                if winner is not None or is_board_full():
                    running = False
                else:
                    current_player = PLAYER_O

        draw_board()
        update_board()
        pygame.display.flip()

        winner = check_winner()
        if winner is not None or is_board_full():
            running = False

        clock.tick(30)

    winner = check_winner()
    show_winner(winner)
    pygame.quit()

if __name__ == "__main__":
    main()
