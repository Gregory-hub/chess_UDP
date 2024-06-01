import random
import tkinter as tk

import chess

from .game import Game
from .UI import UI


class App:
    def __init__(self):
        self.ui = UI(self)
        self.game = Game(self.on_connect, self.on_opponent_connect, self.on_receive_start_command)


    def start(self) -> None:
        self.ui.show_main_window()


    def create_game(self, color_value: tk.StringVar, ip: str, port: int) -> None:
        color = color_value.get()

        if color == "Random":
            player_color = random.choice(['w', 'b'])
        elif color == "White":
            player_color = 'w'
        elif color == "Black":
            player_color = 'b'
        else:
            raise ValueError("Invalid color value")

        self.game.start_udp_client(ip, port)
        self.game.create_game(chess.WHITE if player_color == 'w' else chess.BLACK)
        self.ui.show_wait_for_opponent_window(self.game.udp_client.ip, self.game.udp_client.port, self.game.player_color)
        self.wait_for_opponent()


    def wait_for_opponent(self) -> None:
        self.game.start_waiting_for_opponent()


    def on_opponent_connect(self) -> None:
        self.ui.modify_window_on_opponent_connect(self.game.udp_client.opponent_ip, self.game.udp_client.opponent_port)


    def connect(self, ip: str, port: int, opponent_ip: str, opponent_port: int) -> None:
        self.game.start_udp_client(ip, port)
        if not (self.game.udp_client.ip_is_valid(ip) and self.game.udp_client.port_is_valid(port)):
            return
        if not (self.game.udp_client.ip_is_valid(opponent_ip) and self.game.udp_client.port_is_valid(opponent_port)):
            return

        self.ui.show_wait_for_connect_reply_window(opponent_ip, opponent_port)
        self.game.connect_to_game(opponent_ip, opponent_port)


    def on_connect(self) -> None:
        color_str = self.game.udp_client.get_last_message()
        self.game.create_game(chess.WHITE if color_str == 'w' else chess.BLACK)
        self.game.start_waiting_for_game_to_start(self.on_receive_start_command)
        self.ui.show_wait_for_game_to_start_window()


    def start_game(self) -> None:
        self.game.send_start_command()
        self.game.start_game()
        self.ui.show_game_window(self.game.chessboard.fen(), self.game.player_color)


    def on_receive_start_command(self) -> None:
        self.game.start_game()
        self.ui.show_game_window(self.game.chessboard.fen(), self.game.player_color)


    def shut_down(self) -> None:
        self.game.udp_client.shut_down()
        self.ui.on_shut_down()


    def get_available_ips(self) -> list:
        return self.game.udp_client.addresses


    def get_default_port(self, ip: str) -> int:
        return self.game.udp_client.get_valid_port(ip)


    def get_possible_moves(self, row: int, col: int) -> list:
        piece_sq = self.sq_coords_to_sq_string(row, col)
        if self.game.chessboard.piece_at(chess.parse_square(piece_sq)) is None:
            return []

        moves = []
        for move in self.game.chessboard.legal_moves:
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
