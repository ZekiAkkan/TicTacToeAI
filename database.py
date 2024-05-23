import sqlite3
import csv
import numpy as np

# Veritabanı sınıfı
class DataBase:
    
    def __init__(self):
        self.conn = sqlite3.connect("game_database.db")
        self.cursor = self.conn.cursor()
        self.__tabloOlustur()

    def __tabloOlustur(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS MoveTablo (
                h1 INT, h2 INT, h3 INT, 
                h4 INT, h5 INT, h6 INT, 
                h7 INT, h8 INT, h9 INT,
                player_move INT, move_pos INT
            )
        """)
        self.conn.commit()

    def veriEkle(self, board, player_move, move_pos):
        flat_board = [cell for row in board for cell in row]
        self.cursor.execute("""
            INSERT INTO MoveTablo (
                h1, h2, h3, h4, h5, h6, h7, h8, h9, player_move, move_pos
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (*flat_board, player_move, int(move_pos)))
        self.conn.commit()

    def get_all_moves(self):
        self.cursor.execute("SELECT * FROM MoveTablo")
        return self.cursor.fetchall()

# Veritabanından verileri al ve CSV dosyasına yaz
def export_to_csv():
    conn = sqlite3.connect("game_database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MoveTablo")
    data = cursor.fetchall()

    with open("tic_tac_toe_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        # Sütun başlıkları
        writer.writerow(["h1", "h2", "h3", "h4", "h5", "h6", "h7", "h8", "h9", "player_move", "move_pos"])
        # Veriler
        for row in data:
            writer.writerow(row)

    conn.close()

# CSV dosyasına veri aktarımı
export_to_csv()
