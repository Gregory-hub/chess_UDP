import re

import chess

from .UDPClient import UDPClient


class Game:
    def __init__(self, on_connect: callable, on_opponent_connect: callable, on_receive_start_command: callable):
        self.udp_client = UDPClient()
        self.chessboard = None
        self.player_color = None
        self.game_is_played = False

        self.on_connect = on_connect
        self.on_opponent_connect = on_opponent_connect
        self.on_receive_start_command = on_receive_start_command


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

        self.udp_client.start_receiving()
        self.game_is_played = True

        # while self.game_is_played:
        #     if self.chessboard.turn != self.player_color and not self.udp_client.message_read:
        #         message = self.udp_client.get_last_message()
        #         if self.__is_valid_uci(message):
        #             if self.chessboard.is_legal(chess.Move.from_uci(message)):
        #                 self.chessboard.push_uci(message)
        #                 print(f"\nOpponents move: {message}")
        #                 print(self.chessboard)

        #     elif self.chessboard.turn == self.player_color:
        #         print("Make move (uci format, examples: b1c3, e7e8q)")
        #         input_str = ""
        #         ok_move = False
        #         while not ok_move:
        #             try:
        #                 input_str = input(">> ")
        #             except KeyboardInterrupt:
        #                 print()
        #                 self.udp_client.shut_down()
        #                 exit(0)
        #             ok_move = True
        #             if not self.__is_valid_uci(input_str):
        #                 print("Invalid uci. Try again")
        #                 ok_move = False

        #             elif not self.chessboard.is_legal(chess.Move.from_uci(input_str)):
        #                 print("Illegal move. Try again")
        #                 ok_move = False

        #         self.udp_client.send_to_opponent(input_str)
        #         self.chessboard.push_uci(input_str)
        #         print(f"\nYour move: {input_str}")
        #         print(self.chessboard)
        #         print("Waiting for opponent to move")

        #     if (self.__game_ended()):
        #         self.game_is_played = False
        #         print("Termination:", self.chessboard.outcome().termination)
        #         print("Winner:", self.chessboard.outcome().winner)


    def __is_valid_uci(self, move: str) -> bool:
        return re.match('[a-h][0-9][a-h][0-9]q?', move)


    def __game_ended(self) -> bool:
        return self.chessboard.outcome() is not None
