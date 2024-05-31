import re

import chess

from .UDPClient import UDPClient


class Game:
    def __init__(self):
        self.udp_client = UDPClient()
        self.chessboard = None
        self.player_color = None
        self.game_is_played = False


    # def start(self) -> None:
    #     self.udp_client.start()

        # self.show_configure_host_screen()
        # while True:
        #     print("Type '/create' to create game, '/connect' to connect to a game")
        #     try:
        #         input_str = input(">> ")
        #     except KeyboardInterrupt:
        #         print()
        #         self.udp_client.shut_down()
        #         exit(0)

        #     if input_str == "/create":
        #         self.show_create_game_screen()
        #         self.create_game()
        #         self.udp_client.wait_for_connection('b' if self.player_color == chess.WHITE else 'w')
        #         while not self.udp_client.connected:
        #             pass
        #         self.start_game()
        #     elif input_str == "/connect":
        #         self.show_connect_screen()
        #         self.connect_to_game(self.udp_client.message_received)
        #         self.udp_client.message_read = True
        #         self.start_game()


    # def show_configure_host_screen(self) -> None:
    #     print(f"Running on {self.udp_client.ip}:{self.udp_client.port}")
    #     print("Choose address entry (Empty to keep current):")
    #     for i in range(len(self.udp_client.addresses)):
    #         address = self.udp_client.addresses[i]
    #         print(f"{i}: {address}")
    #     try:
    #         index = input(">> ")
    #     except KeyboardInterrupt:
    #         print()
    #         self.udp_client.shut_down()
    #         exit(0)
    #     if index != '':
    #         new_address = self.udp_client.addresses[int(index)]
    #     else:
    #         new_address = self.udp_client.ip

    #     try:
    #         new_port = input("Enter port number (Empty to keep current)\n>> ")
    #     except KeyboardInterrupt:
    #         print()
    #         self.udp_client.shut_down()
    #         exit(0)
    #     if new_port != '':
    #         new_port = int(new_port)
    #     else:
    #         new_port = None

    #     if new_address is not None or new_port is not None:
    #         self.udp_client.restart(ip_address=new_address, port=new_port)

    #     print(f"Running on {self.udp_client.ip}:{self.udp_client.port}")


    # def show_connect_screen(self) -> None:
    #     opponent_ip, opponent_port = None, None
    #     while opponent_ip is None or opponent_port is None:
    #         print(r"Enter server ip address and port ({address}:{port})")
    #         try:
    #             input_str = input(">> ")
    #         except KeyboardInterrupt:
    #             print()
    #             self.udp_client.shut_down()
    #             exit(0)
    #         opponent_ip, opponent_port = self.udp_client.extract_ip_and_port(input_str)
    #         if opponent_ip is None or opponent_port is None:
    #             print("Invalid ip or port. Try again")
    #             continue

    #     while self.udp_client.opponent_ip is None or self.udp_client.opponent_port is None:
    #         self.udp_client.try_to_connect(opponent_ip, opponent_port)
    #         while self.udp_client.thread_wait_for_connect_reply is not None:
    #             pass


    # def show_create_game_screen(self) -> None:
    #     input_str = ''
    #     while input_str not in ['w', 'b']:
    #         print("Enter your color ('w' for white, 'b' for black)")
    #         try:
    #             input_str = input(">> ")
    #         except KeyboardInterrupt:
    #             print()
    #             self.udp_client.shut_down()
    #             exit(0)
    #     if input_str not in ['w', 'b']:
    #         print("Invalid color. Try again")

    #     self.player_color = chess.WHITE if input_str == 'w' else chess.BLACK


    def create_game(self, player_color: chess.Color) -> None:
        self.chessboard = chess.Board()
        self.player_color = player_color


    def connect_to_game(self, color: str) -> None:
        self.chessboard = chess.Board()
        self.player_color = chess.WHITE if color == 'w' else chess.BLACK
        print("Connected, color =", color)


    def start_game(self) -> None:
        if self.chessboard is None:
            raise ReferenceError("Chessboard is not created")

        self.udp_client.start_receiving()
        self.game_is_played = True

        print("Game started")
        print("You play as", self.player_color)
        print(self.chessboard)
        while self.game_is_played:
            if self.chessboard.turn != self.player_color and self.udp_client.message_read == False:
                self.udp_client.message_read = True
                message = self.udp_client.message_received
                if self.__is_valid_uci(message):
                    if self.chessboard.is_legal(chess.Move.from_uci(message)):
                        self.chessboard.push_uci(message)
                        print(f"\nOpponents move: {message}")
                        print(self.chessboard)

            elif self.chessboard.turn == self.player_color:
                print("Make move (uci format, examples: b1c3, e7e8q)")
                input_str = ""
                ok_move = False
                while not ok_move:
                    try:
                        input_str = input(">> ")
                    except KeyboardInterrupt:
                        print()
                        self.udp_client.shut_down()
                        exit(0)
                    ok_move = True
                    if not self.__is_valid_uci(input_str):
                        print("Invalid uci. Try again")
                        ok_move = False

                    elif not self.chessboard.is_legal(chess.Move.from_uci(input_str)):
                        print("Illegal move. Try again")
                        ok_move = False

                self.udp_client.send_to_opponent(input_str)
                self.chessboard.push_uci(input_str)
                print(f"\nYour move: {input_str}")
                print(self.chessboard)
                print("Waiting for opponent to move")

            if (self.__game_ended()):
                self.game_is_played = False
                print("Termination:", self.chessboard.outcome().termination)
                print("Winner:", self.chessboard.outcome().winner)


    def __is_valid_uci(self, move: str) -> bool:
        return re.match('[a-h][0-9][a-h][0-9]q?', move)


    def __game_ended(self) -> bool:
        return self.chessboard.outcome() is not None
