import tkinter as tk
from random import choice
import chess

from .UIChessPiece import UIChessPiece


class UIChessBoard:
    def __init__(self, master: tk.Tk, color: chess.Color, get_possible_moves_fn: callable, size: int = 8, padding: int = 20):
        self.master = master
        self.size = size
        self.padding = padding
        self.player_color = color
        self.turn = chess.WHITE
        self.board_colors = ["light goldenrod", "brown"]
        self.sq_outline_color = "dark gray"
        self.sq_marker_color = "dark gray"
        self.oval_color = "dark gray"

        self.PIECE_SYMBOLS = {
            "r":"♖",
            "n":"♘",
            "b":"♗",
            "q":"♕",
            "k":"♔",
            "p":"♙",
            "R":"♜",
            "N":"♞",
            "B":"♝",
            "Q":"♛",
            "K":"♚",
            "P":"♟"
        }

        self.board = tk.Canvas(self.master)
        self.board.pack(fill=tk.BOTH, expand=True)
        self.board.bind("<Configure>", self.refresh_board)
        self.square_size = 0
        self.id_highlighted_rect = None
        self.ids_highlighted_ovals = []

        self.position = [[' ' for j in range (self.size)] for i in range (self.size)]
        self.selected_piece_coords = [None, None]

        self.get_possible_moves_fn = get_possible_moves_fn

        self.refresh_board()


    def create_board(self) -> None:
        if self.square_size == 0:
            return
        self.board.bind("<Button-1>", self.process_click_square)
        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2

        for row in range(self.size):
            for col in range(self.size):
                color = self.board_colors[(row + col) % 2]
                x1 = x_offset + col * self.square_size
                y1 = y_offset + row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.board.create_rectangle(x1, y1, x2, y2, fill=color, width=0)


    def update_position(self, fen: str) -> None:
        self.position = self.fen_to_position(fen)


    def draw_pieces(self) -> None:
        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2
        font_size = min(self.square_size // 2, 32)  # Set the maximum font size

        for i in range(self.size):
            for j in range(self.size):
                if self.player_color == chess.BLACK:
                    piece = self.position[i][j]
                else:
                    piece = self.position[7 - i][7 - j]
                if piece != ' ':
                    chess_piece = UIChessPiece(self.board, i, j, piece, font_size)
                    chess_piece.draw_piece(self.square_size, x_offset, y_offset)


    def fen_to_position(self, fen: str) -> list:
        pos_matrix = [[] for i in range(self.size)]
        pos = fen.split(' ')[0]
        rows = pos.split('/')
        for i in range(8):
            row = rows[i]
            j = 0
            for sq in row:
                if sq.isdigit():
                    pos_matrix[i].extend([' ' for j in range(int(sq))])
                    j += int(sq)
                else:
                    piece = self.PIECE_SYMBOLS[sq]
                    pos_matrix[i].append(piece)
                    j += 1
        return pos_matrix


    def refresh_board(self, event = None) -> None:
        self.square_size = min((self.master.winfo_width() - 2 * self.padding) // self.size, (self.master.winfo_height() - 2 * self.padding) // self.size)
        self.board.delete("all")
        self.create_board()
        self.draw_pieces()


    def process_click_square(self, event) -> None:
        if self.id_highlighted_rect is not None:
            self.board.delete(self.id_highlighted_rect)
            self.id_highlighted_rect = None

        if len(self.ids_highlighted_ovals) > 0:
            for id in self.ids_highlighted_ovals:
                self.board.delete(id)
            self.ids_highlighted_ovals.clear()

        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2
        col = (event.x - x_offset) // self.square_size
        row = (event.y - y_offset) // self.square_size

        self.highlight_square(x_offset, y_offset, row, col)
        if self.turn == self.player_color:
            self.mark_possible_moves(x_offset, y_offset, row, col)


    def highlight_square(self, x_offset, y_offset, row, col) -> None:
        if not (0 <= col < self.size and 0 <= row < self.size):
            return

        x1 = x_offset + col * self.square_size
        y1 = y_offset + row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size

        if self.selected_piece_coords != [row, col]:
            self.draw_rect(x1, y1, x2, y2)
            self.selected_piece_coords = [row, col]
        else:
            self.selected_piece_coords = [None, None]


    def mark_possible_moves(self, x_offset, y_offset, row, col) -> None:
        if self.player_color == chess.WHITE:
            row = 7 - row
            col = 7 - col
        possible_moves = self.get_possible_moves_fn(row, col)
        print(possible_moves)

        for row, col in possible_moves:
            if self.player_color == chess.WHITE:
                row = 7 - row
                col = 7 - col
            x1 = x_offset + col * self.square_size
            y1 = y_offset + row * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.draw_oval(x1, y1, x2, y2)


    def draw_rect(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.id_highlighted_rect = self.board.create_rectangle(x1, y1, x2, y2, outline=self.sq_outline_color, width=4)


    def draw_oval(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.ids_highlighted_ovals.append(self.board.create_oval(x1 + self.square_size // 4, y1 + self.square_size // 4, 
                                                          x2 - self.square_size // 4, y2 - self.square_size // 4,
                                                          outline=self.oval_color, width=2))
