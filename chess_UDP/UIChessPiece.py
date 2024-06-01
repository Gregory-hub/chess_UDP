class UIChessPiece:
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
