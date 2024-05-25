import tkinter as tk
from random import randint
import chess


class ChessPiece:
    def __init__(self, canvas, row, col, piece, font_size):
        self.canvas = canvas
        self.row = row
        self.col = col
        
        self.piece = piece
        self.font_size = font_size
        self.font = ("Arial", self.font_size)
        
    def draw_piece(self, square_size, x_offset, y_offset):
        x = x_offset + self.col * square_size + square_size // 2
        y = y_offset + self.row * square_size + square_size // 2
        self.font = ("Arial", self.font_size)
        self.canvas.create_text(x, y, text=self.piece, font=self.font)


    # def move_piece(self, event,square_size, x_offset, y_offset):
    #     col = (event.x - x_offset) // square_size
    #     row = (event.y - y_offset) // square_size


class ChessBoard:
    def __init__(self, master, color, size=8, padding=20):
        self.master = master
        self.size = size
        self.padding = padding
        self.color = color

        self.colors = ["light goldenrod", "brown"]
        if self.color == "White":
            self.piece_positions = {
                "♖": [(7, 0), (7, 7)],
                "♘": [(7, 1), (7, 6)],
                "♗": [(7, 2), (7, 5)],
                "♕": [(7, 3)],
                "♔": [(7, 4)],
                "♙": [(6, i) for i in range(8)],
                "♜": [(0, 0), (0, 7)],
                "♞": [(0, 1), (0, 6)],
                "♝": [(0, 2), (0, 5)],
                "♛": [(0, 3)],
                "♚": [(0, 4)],
                "♟": [(1, i) for i in range(8)]
            }
        elif self.color == "Black":
            self.piece_positions = {
                "♜": [(7, 0), (7, 7)],
                "♞": [(7, 1), (7, 6)],
                "♝": [(7, 2), (7, 5)],
                "♛": [(7, 3)],
                "♚": [(7, 4)],
                "♟": [(6, i) for i in range(8)],
                "♖": [(0, 0), (0, 7)],
                "♘": [(0, 1), (0, 6)],
                "♗": [(0, 2), (0, 5)],
                "♕": [(0, 3)],
                "♔": [(0, 4)],
                "♙": [(1, i) for i in range(8)]
            }
        else:
            print("ERROR")
        self.board = tk.Canvas(self.master)
        
        self.board.pack(fill=tk.BOTH, expand=True)
        self.board.bind("<Configure>", self.update_board)
        self.square_size = 0


    def create_board(self):
        if self.square_size == 0:
            return
        self.board.bind("<Button-1>", self.highlight_square)
        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2
        
        font_size = min(self.square_size // 2, 32)  # Set the maximum font size
        
        for row in range(self.size):
            for col in range(self.size):
                color = self.colors[(row + col) % 2]
                x1 = x_offset + col * self.square_size
                y1 = y_offset + row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.board.create_rectangle(x1, y1, x2, y2, fill=color, width=0)
        

        for piece, positions in self.piece_positions.items():
            for pos in positions:
                row, col = pos
                
                chess_piece = ChessPiece(self.board, row, col, piece, font_size)
                chess_piece.draw_piece(self.square_size, x_offset, y_offset)
        

    def get_possible_moves(self, board_size):
        board = chess.Board()
        board.clear_board()

        for piece, squares in self.piece_positions.items():
            for square in squares:
                board.set_piece_at(chess.square(square[0], square[1]), chess.Piece.from_symbol(piece))

        possible_moves = []
        for move in board.legal_moves:
            if move.from_square == chess.square(self.row, self.col):
                possible_moves.append((chess.square_rank(move.to_square), chess.square_file(move.to_square)))

        return possible_moves


    def update_board(self, event):
        self.square_size = min((self.master.winfo_width() - 2 * self.padding) // self.size, (self.master.winfo_height() - 2 * self.padding) // self.size)
        self.board.delete("all")
        self.create_board()


    def highlight_square(self, event):
        if hasattr(self, 'id'):  # Проверяем, существует ли уже идентификатор фигуры
            self.board.delete(self.id)  # Удаляем предыдущую фигуру
        x_offset = (self.master.winfo_width() - self.size * self.square_size) // 2
        y_offset = (self.master.winfo_height() - self.size * self.square_size) // 2
        font_size = min(self.square_size // 2, 32)  # Set the maximum font size
        col = (event.x - x_offset) // self.square_size
        row = (event.y - y_offset) // self.square_size
        x1 = x_offset + col * self.square_size
        y1 = y_offset + row * self.square_size
        x2 = x1 + self.square_size
        y2 = y1 + self.square_size

        self.id = self.board.create_rectangle(x1, y1, x2, y2, outline="green", width=2)
        selected_piece = None
        for piece in self.board.find_all():
            if self.board.type(piece) == "text":
                piece_coords = self.board.coords(piece)
                piece_col = (piece_coords[0] - x_offset) // self.square_size
                piece_row = (piece_coords[1] - y_offset) // self.square_size
                if piece_row == row and piece_col == col:
                    selected_piece = piece
                    break
        self.board.bind("<Button-1>", self.highlight_square)
        if selected_piece:
            self.board.delete("possible_moves")
            
            possible_moves = self.get_possible_moves(self.size)
            for move in possible_moves:
                move_col = x_offset + move[1] * self.square_size + self.square_size // 2
                move_row = y_offset + move[0] * self.square_size + self.square_size // 2
                self.board.create_oval(move_col - self.square_size // 4, move_row - self.square_size // 4,
                                       move_col + self.square_size // 4, move_row + self.square_size // 4,
                                       outline='blue', tags='possible_moves')


class Window:
    def __init__(self):
        self.widgets = []
        self.main_window = tk.Tk()
        self.main_window.geometry("500x500")
        self.main_window.title("Main Window")
        self.color = ""
        self.value_inside = " "
        self.chessboard = None


    def show_create_game_window(self):
        self.clear()
        options_list = ["Random", "White", "Black"]
        self.value_inside = tk.StringVar(self.main_window)
        self.value_inside.set(options_list[0]) 
        question_menu = tk.OptionMenu(self.main_window, self.value_inside, *options_list) 
        question_menu.pack(expand=True, anchor="center") 
        self.widgets.append(question_menu)
        create_game_button1 = tk.Button(self.main_window, text="Create Game", command=self.create_game)
        self.widgets.append(create_game_button1)
        create_game_button1.pack(expand=True, anchor="center")    


    def create_game(self):
        self.clear()
        self.color = self.value_inside.get()

        if (self.color == "Random"):
            b = randint(1,2)
            print(b)
            if b == 1: self.color = "White"
            elif b ==2: self.color = "Black"
        else:
            self.color = self.color 
        
        self.chessboard = ChessBoard(self.main_window, padding=30, color = self.color)


    def connect(self):
        self.clear()
        self.show_ip_window()


    def show_main_window(self):
        create_game_button = tk.Button(self.main_window, text="Create Game", command=self.show_create_game_window)
        self.widgets.append(create_game_button)
        create_game_button.pack(expand=True, anchor="center") 

        connect_button = tk.Button(self.main_window, text="Connect", command=self.connect)
        self.widgets.append(connect_button)
        connect_button.pack(expand=True, anchor="center") 

        self.main_window.mainloop()


    def show_ip_window(self):
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
        
        connect_button = tk.Button(self.main_window, text="Connect", command=self.connect)
        self.widgets.append(connect_button)
        connect_button.pack(expand=True,anchor="center") 


    def clear(self):
        for widget in self.widgets:
            widget.destroy()
        self.widgets.clear()    


if __name__ == "__main__":
    window = Window()
    window.show_main_window()
