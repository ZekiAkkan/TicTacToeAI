import tensorflow as tf
from tensorflow import keras
import numpy as np
import pygame
import math
from database import DataBase

# TensorFlow modelini yükle
model = keras.models.load_model("tic_tac_toe_model_improved.keras")

# Oyun tahtası
board = [[0 for _ in range(3)] for _ in range(3)]

# İşaretler
PLAYER_X = -1
PLAYER_O = 1
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
font = pygame.font.SysFont(None, 48)

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

# Tahminleri ağırlıklandırma fonksiyonu
def weight_predictions(predictions):
    weighted_predictions = predictions.copy()

    # Kazanan hamleleri kontrol et ve ağırlıklandır
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                # Kazanma hamlesi kontrolü
                board[i][j] = PLAYER_O
                if check_winner() == PLAYER_O:
                    weighted_predictions[i * 3 + j] += 1.0
                board[i][j] = EMPTY

                # Rakibin kazanmasını engelleme hamlesi kontrolü
                board[i][j] = PLAYER_X
                if check_winner() == PLAYER_X:
                    weighted_predictions[i * 3 + j] += 0.5
                board[i][j] = EMPTY

    # Merkez hücreyi daha yüksek ağırlıkla değerlendir
    if board[1][1] == EMPTY:
        weighted_predictions[4] += 0.3

    # Köşeleri ve kenarları ağırlıklandır
    for move in [0, 2, 6, 8]:  # Köşeler
        if board[move // 3][move % 3] == EMPTY:
            weighted_predictions[move] += 0.2

    for move in [1, 3, 5, 7]:  # Kenarlar
        if board[move // 3][move % 3] == EMPTY:
            weighted_predictions[move] += 0.1

    return weighted_predictions

# En iyi hamleyi TensorFlow modeli ile bulma
def find_best_move():
    # Board'u modele uygun formatta hazırlayalım
    flat_board = np.array(board).flatten().astype(np.float32)
    flat_board[flat_board == PLAYER_X] = 1
    flat_board[flat_board == PLAYER_O] = 2
    flat_board[flat_board == EMPTY] = 0

    # Modelden tahmin yap
    predictions = model.predict(flat_board.reshape(1, -1)).flatten()

    # Tahminleri ağırlıklandır
    weighted_predictions = weight_predictions(predictions)

    # Geçerli en iyi hamleyi bul
    best_move = np.argmax(weighted_predictions)
    row, col = divmod(best_move, 3)

    if board[row][col] == EMPTY:
        return row, col
    else:
        # Eğer model dolu bir hücre seçerse, en yüksek puanlı diğer hücreleri dene
        sorted_moves = np.argsort(weighted_predictions)[::-1]
        for move in sorted_moves:
            row, col = divmod(move, 3)
            if board[row][col] == EMPTY:
                return row, col
        return None

# Sonucu ekranda göster
def show_result(message):
    text = font.render(message, True, BLACK)
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(2000)

# Oyun döngüsü
def main():
    db = DataBase()
    current_player = PLAYER_X  # İlk oyuncu X ile başlasın
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and current_player == PLAYER_X:
                x, y = pygame.mouse.get_pos()
                row, col = y // CELL_SIZE, x // CELL_SIZE
                if board[row][col] == EMPTY:
                    board[row][col] = PLAYER_X
                    db.veriEkle(board, PLAYER_X, row * 3 + col)
                    winner = check_winner()
                    if winner is not None or is_board_full():
                        running = False
                    else:
                        current_player = PLAYER_O

        if current_player == PLAYER_O and running:
            move = find_best_move()
            if move:
                row, col = move
                board[row][col] = PLAYER_O
                db.veriEkle(board, PLAYER_O, row * 3 + col)
                winner = check_winner()
                if winner is not None or is_board_full():
                    running = False
                else:
                    current_player = PLAYER_X

        draw_board()
        update_board()
        pygame.display.flip()

        winner = check_winner()
        if winner is not None or is_board_full():
            running = False

        clock.tick(30)

    winner = check_winner()
    if winner is not None:
        if winner == PLAYER_X:
            show_result("X wins!")
        else:
            show_result("O wins!")
    else:
        show_result("It's a tie!")

    pygame.quit()

if __name__ == "__main__":
    main()
