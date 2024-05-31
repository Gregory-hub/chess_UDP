import random
import tkinter as tk

import chess

from .game import Game
from .UI import UI


class App:
    def __init__(self):
        self.ui = UI(self.create_game, self.connect, self.get_possible_moves)
        self.game = Game()


    def start(self) -> None:
        self.ui.show_main_window()
        # self.ui.show_create_game_window(self.create_game)


    def create_game(self, color_value: tk.StringVar) -> None:
        color = color_value.get()

        if color == "Random":
            player_color = random.choice(['w', 'b'])
        elif color == "White":
            player_color = 'w'
        elif color == "Black":
            player_color = 'b'
        else:
            raise ValueError("Invalid color value")

        self.game.create_game(chess.WHITE if player_color == 'w' else chess.BLACK)
        self.ui.show_game_window(self.game.chessboard.fen(), self.game.player_color)


    def connect(self) -> None:
        pass


    def get_possible_moves(self, row: int, col: int) -> list:
        piece_sq = self.sq_coords_to_sq_string(row, col)
        print(piece_sq)
        print("-----------------------")
        if self.game.chessboard.piece_at(chess.parse_square(piece_sq)) is None:
            return []

        moves = []
        for move in self.game.chessboard.legal_moves:
            print(move.uci())
            uci = move.uci()
            if uci[:2] == piece_sq:
                moves.append(self.sq_string_to_sq_coords(uci[2:]))

        return moves


    def sq_coords_to_sq_string(self, row: int, col: int) -> str:
        column_names = "abcdefgh"
        return column_names[col] + str(row + 1)


    def sq_string_to_sq_coords(self, sq: str) -> list:
        column_names = "abcdefgh"
        return [int(sq[1]) - 1, column_names.index(sq[0])]
