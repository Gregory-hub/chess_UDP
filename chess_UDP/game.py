import re

import chess

from .UDPClient import UDPClient


class Game:
    def __init__(
            self,
            on_connect: callable,
            on_opponent_connect: callable,
            on_receive_start_command: callable,
            on_receive_move_command: callable
        ):
        self.udp_client = UDPClient()
        self.chessboard = None
        self.player_color = None
        self.game_is_played = False

        self.on_connect = on_connect
        self.on_opponent_connect = on_opponent_connect
        self.on_receive_start_command = on_receive_start_command
        self.on_receive_move_command = on_receive_move_command


    def start_udp_client(self, ip: str, port: int) -> None:
        self.udp_client.start(ip, port)


    def create_game(self, player_color: chess.Color) -> None:
        self.chessboard = chess.Board()
        self.player_color = player_color


    def start_waiting_for_opponent(self) -> None:
        self.udp_client.on_connect = self.on_opponent_connect
        self.udp_client.wait_for_connection('b' if self.player_color else 'w')
    

    def start_waiting_for_game_to_start(self, on_start_game_command: callable) -> None:
        self.udp_client.wait_for_game_to_start(on_start_game_command)


    def connect_to_game(self, game_ip: str, game_port: int) -> None:
        self.udp_client.on_connect = self.on_connect
        self.udp_client.try_to_connect(game_ip, game_port)


    def send_start_command(self) -> None:
        self.udp_client.send_to_opponent("/start")


    def start_game(self) -> None:
        if self.chessboard is None:
            raise ReferenceError("Chessboard is not created")

        self.udp_client.start_receiving(self.on_receive_move_command)
        self.game_is_played = True


    def try_to_make_move(self, move_uci: str) -> bool:
        success = False
        if not self.is_current_players_turn():
            success = False
        elif not self.is_valid_uci(move_uci):
            success = False
        elif self.chessboard.is_legal(chess.Move.from_uci(move_uci)):
            self.udp_client.send_to_opponent(move_uci)
            self.chessboard.push_uci(move_uci)
            if self.game_ended():
                self.game_is_played = False
            success = True

        return success


    def process_opponents_move(self, move_uci: str) -> bool:
        success = False
        if self.is_current_players_turn():
            success = False
        elif not self.is_valid_uci(move_uci):
            success = False
        elif self.chessboard.is_legal(chess.Move.from_uci(move_uci)):
            self.chessboard.push_uci(move_uci)
            if self.game_ended():
                self.game_is_played = False
            success = True

        return success


    def is_current_players_turn(self) -> bool:
        return self.chessboard.turn == self.player_color


    def is_valid_uci(self, move: str) -> bool:
        return re.match('[a-h][0-9][a-h][0-9]q?', move)


    def game_ended(self) -> bool:
        return self.chessboard.outcome() is not None

    
    def get_game_result(self) -> chess.Outcome | None:
        return self.chessboard.outcome()
