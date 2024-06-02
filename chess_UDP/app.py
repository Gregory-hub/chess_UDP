import random
import tkinter as tk

import chess

from .game import Game
from .UI import UI


class App:
    def __init__(self):
        self.ui = UI(self, self.on_ui_move)
        self.game = Game(self.on_connect, self.on_opponent_connect, self.on_receive_start_command, self.on_receive_move)


    def start(self) -> None:
        self.ui.show_main_window()


    def create_game(self, color: str, ip: str, port: str) -> None:
        try:
            port = int(port)
        except ValueError:
            return

        if color == "Random":
            player_color = random.choice(['w', 'b'])
        elif color == "White":
            player_color = 'w'
        elif color == "Black":
            player_color = 'b'
        else:
            raise ValueError("Invalid color value")

        try:
            self.game.start_udp_client(ip, port)
        except ValueError:
            return
        self.game.create_game(chess.WHITE if player_color == 'w' else chess.BLACK)
        self.ui.show_wait_for_opponent_window(self.game.udp_client.ip, self.game.udp_client.port, self.game.player_color)
        self.wait_for_opponent()


    def wait_for_opponent(self) -> None:
        self.game.start_waiting_for_opponent()


    def on_opponent_connect(self) -> None:
        self.ui.modify_window_on_opponent_connect(self.game.udp_client.opponent_ip, self.game.udp_client.opponent_port)


    def connect(self, ip: str, port: str, opponent_ip: str, opponent_port: str) -> None:
        try:
            port = int(port)
            opponent_port = int(opponent_port)
        except ValueError:
            return

        if not (self.game.udp_client.ip_is_valid(ip) and self.game.udp_client.port_is_valid(port)):
            return
        if not (self.game.udp_client.ip_is_valid(opponent_ip) and self.game.udp_client.port_is_valid(opponent_port)):
            return

        try:
            self.game.start_udp_client(ip, port)
        except ValueError:
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


    def on_ui_move(self, init_row: int, init_col: int, row: int, col: int) -> None:
        if not self.game.game_is_played:
            return

        move_uci = self.construct_move(init_row, init_col, row, col)
        print(move_uci)
        success = self.game.try_to_make_move(move_uci)
        if success:
            self.ui.ui_chessboard.unhighlight_all()
            self.ui.ui_chessboard.update_position(self.game.chessboard.fen())
            self.ui.ui_chessboard.draw_pieces()

        if self.game.game_ended():
            self.ui.show_game_result_popup(self.get_outcome_message())


    def construct_move(self, init_row: int, init_col: int, row: int, col: int) -> None:
        init_sq = self.sq_coords_to_sq_string(init_row, init_col)
        sq = self.sq_coords_to_sq_string(row, col)
        move_uci = init_sq + sq

        piece = self.game.chessboard.piece_at(chess.parse_square(init_sq))
        condition = (init_row == 6 and row == 7 and self.game.player_color == chess.BLACK)
        condition = condition or (init_row == 1 and row == 0 and self.game.player_color == chess.WHITE)
        condition = condition and piece is not None and piece.piece_type == chess.PAWN
        if condition:
            move_uci += 'q'

        return move_uci


    def on_receive_move(self, message: str, ip: str, port: str) -> None:
        if ip != self.game.udp_client.opponent_ip or port != self.game.udp_client.opponent_port:
            return

        if not self.game.game_is_played:
            return
        
        success = self.game.process_opponents_move(message)
        if success:
            self.ui.ui_chessboard.unhighlight_all()
            self.ui.ui_chessboard.update_position(self.game.chessboard.fen())
            self.ui.ui_chessboard.draw_pieces()
        
        if self.game.game_ended():
            self.ui.show_game_result_popup(self.get_outcome_message())

    
    def get_outcome_message(self) -> str:
        message = ""
        outcome = self.game.get_game_result()
        if self.game.chessboard.is_checkmate():
            you_won = outcome.winner == self.game.player_color
            message = "You won" if you_won else "You lost"
            message += "\nCheckmate"
        elif self.game.chessboard.is_stalemate():
            message = "Draw\nStalemate"
        elif self.game.chessboard.is_insufficient_material():
            you_won = outcome.winner == self.game.player_color
            message = "Draw"
            message += "\nInsuffitient material"
        elif self.game.chessboard.is_seventyfive_moves():
            message = "Draw"
            message += "\nNo captures or pawn pushes in seventy five moves"
        elif self.game.chessboard.is_fivefold_repetition():
            message = "Draw"
            message += "\nFivefold repetition"

        return message


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
        return column_names[col] + str(8 - row)


    def sq_string_to_sq_coords(self, sq: str) -> list:
        column_names = "abcdefgh"
        return [8 - int(sq[1]), column_names.index(sq[0])]
