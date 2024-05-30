import random
import tkinter as tk

from .game import Game
from .UI import UI


class App:
    def __init__(self):
        self.ui = UI(self.create_game, self.connect)
        self.game = Game()


    def start(self) -> None:
        self.ui.show_main_window()
        # self.ui.show_create_game_window(self.create_game)


    def create_game(self, color_value: tk.StringVar) -> None:
        color = color_value.get()

        if color == "Random":
            self.ui.color = random.choice(['w', 'b'])
        elif color == "White":
            self.ui.color = 'w'
        elif color == "Black":
            self.ui.color = 'b'
        else:
            raise ValueError("Invalid color value")

        self.game.create_game()
        self.ui.show_game_window(self.game.chessboard.fen())


    def connect(self) -> None:
        pass
