import tkinter as tk

from .UIChessBoard import UIChessBoard


class UI:
    def __init__(self, create_game_command: callable, connect_command: callable):
        self.widgets = []
        self.main_window = tk.Tk()
        self.main_window.geometry("800x800")
        self.main_window.state("zoomed")
        self.main_window.title("Main Window")
        self.color = ""
        self.ui_chessboard = None

        self.create_game_command = create_game_command
        self.connect_command = connect_command


    def show_main_window(self) -> None:
        self.clear()
        create_game_button = tk.Button(self.main_window, text="Create Game", command=self.show_create_game_window)
        self.widgets.append(create_game_button)
        create_game_button.pack(expand=True, anchor="center") 

        connect_button = tk.Button(self.main_window, text="Connect", command=self.show_connect_window)
        self.widgets.append(connect_button)
        connect_button.pack(expand=True, anchor="center") 

        self.main_window.mainloop()


    def show_create_game_window(self) -> None:
        self.clear()
        options_list = ["Random", "White", "Black"]
        value = tk.StringVar(self.main_window)
        value.set(options_list[0]) 
        question_menu = tk.OptionMenu(self.main_window, value, *options_list) 
        question_menu.pack(expand=True, anchor="center") 
        self.widgets.append(question_menu)

        create_game_button = tk.Button(self.main_window, text="Create Game", command=lambda: self.create_game_command(value))
        create_game_button.pack(expand=True, anchor="center")    
        self.widgets.append(create_game_button)


    def show_game_window(self, fen: str) -> None:
        self.clear()
        self.ui_chessboard = UIChessBoard(self.main_window, padding=30, color=self.color)
        self.ui_chessboard.update_position(fen)
        self.ui_chessboard.draw_pieces()


    def show_connect_window(self) -> None:
        self.clear()
        label1 = tk.Label(text="IP")
        label2 = tk.Label(text="Port")
        label1.pack(expand=True, anchor="w")
        label2.pack(expand=True, anchor="e")
        frame = tk.Frame(borderwidth=1)
        self.widgets.append(frame)
        frame.pack(expand=True, anchor="center")
        entryip = tk.Entry(frame)
        self.widgets.append(entryip)

        entryip.grid(row=0,columnspan=2,column=1)
        entryport = tk.Entry(frame, width = 5)

        entryport.grid(row=0,column=3,)
        self.widgets.append(entryport)
        
        connect_button = tk.Button(self.main_window, text="Connect", command=self.connect_command)
        self.widgets.append(connect_button)
        connect_button.pack(expand=True,anchor="center") 


    def clear(self) -> None:
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()    
        if self.ui_chessboard is not None:
            self.ui_chessboard.board.destroy()
            self.ui_chessboard = None
