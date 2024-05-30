import tkinter as tk
from random import choice
import chess

from .UIChessPiece import UIChessPiece


class UIChessBoard:
    def __init__(self, master, color, size=8, padding=20):
        self.master = master
        self.size = size
        self.padding = padding
        self.player_color = color
        self.player_colors = ["light goldenrod", "brown"]
        self.sq_outline_color = "dark gray"
        self.sq_marker_color = "dark gray"

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

        self.position = [[' ' for j in range (self.size)] for i in range (self.size)]
        self.selected_piece_coords = [None, None]

        self.refresh_board()


    def create_board(self) -> None:
        if self.square_size == 0:
            return
        self.board.bind("<Button-1>", self.highlight_square)
        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2

        for row in range(self.size):
            for col in range(self.size):
                color = self.player_colors[(row + col) % 2]
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
                piece = self.position[i][j]
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


    def highlight_square(self, event) -> None:
        if hasattr(self, 'id'):
            self.board.delete(self.id)

        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2
        # font_size = min(self.square_size // 2, 32)
        col = (event.x - x_offset) // self.square_size
        row = (event.y - y_offset) // self.square_size

        if not (0 <= col < self.size and 0 <= row < self.size):
            return

        x1 = x_offset + col * self.square_size
        y1 = y_offset + row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size

        if self.selected_piece_coords != [col, row]:
            self.id = self.board.create_rectangle(x1, y1, x2, y2, outline=self.sq_outline_color, width=4)
            self.selected_piece_coords = [col, row]
        else:
            self.selected_piece_coords = [None, None]
        # selected_piece = None
        # for piece in self.board.find_all():
        #     if self.board.type(piece) == "text":
        #         piece_coords = self.board.coords(piece)
        #         piece_col = (piece_coords[0] - x_offset) // self.square_size
        #         piece_row = (piece_coords[1] - y_offset) // self.square_size
        #         if piece_row == row and piece_col == col:
        #             selected_piece = piece
        #             break
        # self.board.bind("<Button-1>", self.highlight_square)
        # if selected_piece:
        #     self.board.delete("possible_moves")

        #     possible_moves = self.get_possible_moves(self.size)
        #     for move in possible_moves:
        #         move_col = x_offset + move[1] * self.square_size + self.square_size // 2
        #         move_row = y_offset + move[0] * self.square_size + self.square_size // 2
        #         self.board.create_oval(move_col - self.square_size // 4, move_row - self.square_size // 4,
        #                                move_col + self.square_size // 4, move_row + self.square_size // 4,
        #                                outline='blue', tags='possible_moves')
