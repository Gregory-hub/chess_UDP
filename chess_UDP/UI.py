import tkinter as tk
from tkinter import messagebox

import chess

from .UIChessBoard import UIChessBoard


class UI:
    def __init__(self, app, on_move: callable):
        self.app = app

        self.widgets = []
        self.main_window = tk.Tk()
        self.main_window.geometry("800x800")
        self.main_window.state("zoomed")
        self.main_window.title("Main Window")
        self.ui_chessboard = None

        self.FONT = ("Arial", 12)

        self.opponent_label_text = None
        self.start_button = None
        self.opponent_address_label_text = None

        self.on_move = on_move


    def show_main_window(self) -> None:
        self.clear()

        self.add_top_frame()

        create_game_button = tk.Button(self.main_window, text="Create Game", command=self.show_create_game_window)
        self.widgets.append(create_game_button)
        create_game_button.pack(expand=True, anchor="center") 

        connect_button = tk.Button(self.main_window, text="Connect", command=self.show_connect_window)
        self.widgets.append(connect_button)
        connect_button.pack(expand=True, anchor="center") 

        self.add_bottom_frame()

        self.main_window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.main_window.mainloop()


    def show_create_game_window(self) -> None:
        self.clear()

        self.add_top_frame()

        address_frame = tk.Frame(self.main_window)
        self.widgets.append(address_frame)

        frame_ip = tk.LabelFrame(address_frame, text="IP", border=0, font=self.FONT)
        self.widgets.append(frame_ip)
        frame_ip.pack(expand=True, side="left")
        ips = self.app.get_available_ips()
        ip_value = tk.StringVar(frame_ip)
        ip_value.set(ips[0]) 
        ip_menu = tk.OptionMenu(frame_ip, ip_value, *ips)
        self.widgets.append(ip_menu)
        ip_menu.pack(expand=True)

        frame_port = tk.LabelFrame(address_frame, text="Port", border=0, font=self.FONT)
        self.widgets.append(frame_port)
        frame_port.pack(expand=True, side="right")
        entry_port = tk.Entry(frame_port, width=5)
        entry_port.insert(0, self.app.get_default_port(ip_value.get()))
        self.widgets.append(entry_port)
        entry_port.pack(expand=True)

        address_frame.pack(expand=True)

        color_frame = tk.LabelFrame(self.main_window, text="Color", border=0, font=self.FONT)
        self.widgets.append(color_frame)
        options_list = ["Random", "White", "Black"]
        color_value = tk.StringVar(color_frame)
        color_value.set(options_list[0]) 
        question_menu = tk.OptionMenu(color_frame, color_value, *options_list) 
        self.widgets.append(question_menu)
        question_menu.pack(expand=True)

        color_frame.pack(expand=True)

        create_game_button = tk.Button(self.main_window, text="Create Game", command=lambda: self.app.create_game(color_value.get(), ip_value.get(), entry_port.get()))
        self.widgets.append(create_game_button)
        create_game_button.pack(expand=True)

        self.add_bottom_frame()


    def show_wait_for_opponent_window(self, ip: str, port: int, color: bool) -> None:
        self.clear()

        self.add_top_frame()

        top_text_frame = tk.Frame(self.main_window)
        self.widgets.append(top_text_frame)
        game_address_text = tk.Text(top_text_frame, height=1, borderwidth=0, font=self.FONT)
        self.widgets.append(game_address_text)
        game_address_text.insert(1.0, f"Game is running on {ip}:{port}")
        game_address_text.configure(state="disabled")
        game_address_text.tag_configure("center", justify='center')
        game_address_text.tag_add("center", 1.0, "end")
        game_address_text.pack()
        label = tk.Label(top_text_frame, text=f"You play as {'White' if color else 'Black'}", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        label = tk.Label(top_text_frame, text="Waiting for opponent...", font=self.FONT)
        self.widgets.append(label)
        label.pack()

        top_text_frame.pack(expand=True)

        bottom_text_frame = tk.Frame(self.main_window)
        self.widgets.append(bottom_text_frame)

        self.opponent_label_text = tk.StringVar(bottom_text_frame)
        self.opponent_label_text.set("Opponent not connected")
        opponent_label = tk.Label(bottom_text_frame, textvariable=self.opponent_label_text, font=self.FONT)
        self.widgets.append(opponent_label)
        opponent_label.pack()
        self.opponent_address_label_text = tk.StringVar(bottom_text_frame)
        self.opponent_address_label_text.set("")
        opponent_label = tk.Label(bottom_text_frame, textvariable=self.opponent_address_label_text, font=self.FONT)
        self.widgets.append(opponent_label)
        opponent_label.pack()

        self.start_button = tk.Button(bottom_text_frame, text="Start", command=self.app.start_game)
        self.widgets.append(self.start_button)
        self.start_button.pack(expand=True) 
        self.start_button["state"] = "disabled"

        bottom_text_frame.pack(expand=True)

        self.add_bottom_frame()


    def modify_window_on_opponent_connect(self, opponent_ip: str, opponent_port: int) -> None:
        if self.start_button is None or self.opponent_label_text is None:
            raise ValueError("Not on 'wait for opponent window")

        self.opponent_label_text.set("Opponent connected")
        self.opponent_address_label_text.set(f"Opponent: {opponent_ip}:{opponent_port}")
        self.start_button["state"] = "active"


    def show_game_window(self, fen: str, player_color: chess.Color) -> None:
        self.clear()
        self.ui_chessboard = UIChessBoard(
            self.main_window, 
            self.app,
            padding=30, 
            color=player_color,
            on_move=self.on_move
        )
        self.ui_chessboard.update_position(fen)
        self.ui_chessboard.refresh_board()


    def show_connect_window(self) -> None:
        self.clear()

        self.add_top_frame()

        address_frame = tk.Frame(self.main_window)
        self.widgets.append(address_frame)
        address_frame.pack(expand=True)

        label = tk.Label(address_frame, text="Your ip and port", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        frame_ip = tk.LabelFrame(address_frame, text="IP", border=0, font=self.FONT)
        self.widgets.append(frame_ip)
        frame_ip.pack(expand=True, side="left")
        ips = self.app.get_available_ips()
        ip_value = tk.StringVar(frame_ip)
        ip_value.set(ips[0]) 
        ip_menu = tk.OptionMenu(frame_ip, ip_value, *ips)
        self.widgets.append(ip_menu)
        ip_menu.pack(expand=True)

        frame_port = tk.LabelFrame(address_frame, text="Port", border=0, font=self.FONT)
        self.widgets.append(frame_port)
        frame_port.pack(expand=True, side="right")
        entry_port = tk.Entry(frame_port, width=5)
        entry_port.insert(0, self.app.get_default_port(ip_value.get()))
        self.widgets.append(entry_port)
        entry_port.pack(expand=True)

        opponent_address_frame = tk.Frame(self.main_window)
        self.widgets.append(opponent_address_frame)
        opponent_address_frame.pack(expand=True)

        label = tk.Label(opponent_address_frame, text="Opponent's ip and port", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        frame_opponent_ip = tk.LabelFrame(opponent_address_frame, text="IP", border=0, font=self.FONT)
        self.widgets.append(frame_opponent_ip)
        frame_opponent_ip.pack(expand=True, side="left")
        entry_opponent_ip = tk.Entry(frame_opponent_ip)
        self.widgets.append(entry_opponent_ip)
        entry_opponent_ip.pack(expand=True)

        frame_opponent_port = tk.LabelFrame(opponent_address_frame, text="Port", border=0, font=self.FONT)
        self.widgets.append(frame_opponent_port)
        frame_opponent_port.pack(expand=True, side="right")
        entry_opponent_port = tk.Entry(frame_opponent_port, width=5)
        self.widgets.append(entry_opponent_port)
        entry_opponent_port.pack(expand=True)

        connect_command = lambda: self.app.connect(ip_value.get(), entry_port.get(), entry_opponent_ip.get(), entry_opponent_port.get())
        connect_button = tk.Button(self.main_window, text="Connect", command=connect_command)
        self.widgets.append(connect_button)
        connect_button.pack(expand=True, anchor="center") 

        self.add_bottom_frame()


    def show_wait_for_connect_reply_window(self, opponent_ip: str, opponent_port: int) -> None:
        self.clear()

        self.add_top_frame()

        label = tk.Label(self.main_window, text=f"Your ip and port: {self.app.game.udp_client.ip}:{self.app.game.udp_client.port}", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        label = tk.Label(self.main_window, text=f"Connection request sent to {opponent_ip}:{opponent_port}", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        label = tk.Label(self.main_window, text="Waiting for opponent to accept...", font=self.FONT)
        self.widgets.append(label)
        label.pack()

        self.add_bottom_frame()


    def show_wait_for_game_to_start_window(self) -> None:
        self.clear()

        self.add_top_frame()

        label = tk.Label(self.main_window, text=f"Your ip and port: {self.app.game.udp_client.ip}:{self.app.game.udp_client.port}", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        label = tk.Label(self.main_window, text=f"Opponent's ip and port {self.app.game.udp_client.opponent_ip}:{self.app.game.udp_client.opponent_port}", font=self.FONT)
        self.widgets.append(label)
        label.pack()
        label = tk.Label(self.main_window, text="Waiting for opponent to start game...", font=self.FONT)
        self.widgets.append(label)
        label.pack()

        self.add_bottom_frame()


    def show_game_result_popup(self, message: str) -> None:
        messagebox.showinfo("Game ended", message)


    def add_top_frame(self) -> None:
        top_frame = tk.Frame(self.main_window)
        self.widgets.append(top_frame)
        top_frame.pack(expand=True, side="top")


    def add_bottom_frame(self) -> None:
        bottom_frame = tk.Frame(self.main_window)
        self.widgets.append(bottom_frame)
        bottom_frame.pack(expand=True, side="bottom")


    def clear(self) -> None:
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()
        if self.ui_chessboard is not None:
            self.ui_chessboard.board.destroy()
            self.ui_chessboard = None

        self.opponent_label_text = None
        self.opponent_address_label_text = None
        self.start_button = None


    def on_shut_down(self) -> None:
        self.clear()
        self.main_window.destroy()


    def on_closing(self) -> None:
        self.app.shut_down()
