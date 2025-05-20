from anytree import Node, RenderTree
from anytree.exporter import DotExporter
import os

class Piece:
    def __init__(self, color):
        self.color = color
        self.name = "?"

    def can_move(self, board, start, end):
        return False

    def __str__(self):
        return self.symbol_white if self.color == 'white' else self.symbol_black


class Pawn(Piece):
    symbol_white = '♙'
    symbol_black = '♟'

    def __init__(self, color):
        super().__init__(color)
        self.name = "Pawn"

    def can_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        direction = 1 if self.color == 'white' else -1
        if start_col == end_col:
            if end_row == start_row + direction:
                if board[end_row][end_col] is None:
                    return True
            elif (end_row == start_row + 2 * direction and
                  (self.color == 'white' and start_row == 1 or self.color == 'black' and start_row == 6)):
                if board[start_row + direction][start_col] is None and board[end_row][end_col] is None:
                    return True
        if abs(end_col - start_col) == 1 and end_row == start_row + direction:
            target_piece = board[end_row][end_col]
            if target_piece is not None and target_piece.color != self.color:
                return True
        return False


class Rook(Piece):
    symbol_white = '♖'
    symbol_black = '♜'

    def __init__(self, color):
        super().__init__(color)
        self.name = "Rook"
        self.has_moved = False  # Track if the rook has moved

    def can_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        if start_row != end_row and start_col != end_col:
            return False
        if start_row == end_row:
            step = 1 if end_col > start_col else -1
            for c in range(start_col + step, end_col, step):
                if board[start_row][c] is not None:
                    return False
        else:
            step = 1 if end_row > start_row else -1
            for r in range(start_row + step, end_row, step):
                if board[r][start_col] is not None:
                    return False
        target_piece = board[end_row][end_col]
        if target_piece is None or target_piece.color != self.color:
            return True
        return False


class Knight(Piece):
    symbol_white = '♘'
    symbol_black = '♞'

    def __init__(self, color):
        super().__init__(color)
        self.name = "Knight"

    def can_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True
        return False


class Bishop(Piece):
    symbol_white = '♗'
    symbol_black = '♝'

    def __init__(self, color):
        super().__init__(color)
        self.name = "Bishop"

    def can_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)
        if row_diff != col_diff:
            return False
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1
        r, c = start_row + row_step, start_col + col_step
        while r != end_row and c != end_col:
            if board[r][c] is not None:
                return False
            r += row_step
            c += col_step
        target_piece = board[end_row][end_col]
        if target_piece is None or target_piece.color != self.color:
            return True
        return False


class Queen(Piece):
    symbol_white = '♕'
    symbol_black = '♛'

    def __init__(self, color):
        super().__init__(color)
        self.name = "Queen"

    def can_move(self, board, start, end):
        return Rook(self.color).can_move(board, start, end) or Bishop(self.color).can_move(board, start, end)


class King(Piece):
    symbol_white = '♔'
    symbol_black = '♚'

    def __init__(self, color):
        super().__init__(color)
        self.name = "King"
        self.has_moved = False  # Track if the king has moved

    def can_move(self, board, start, end):
        start_row, start_col = start
        end_row, end_col = end
        row_diff = abs(end_row - start_row)
        col_diff = abs(end_col - start_col)

        # Castling logic
        if (row_diff == 0 and col_diff == 2) and not self.has_moved:
            # Kingside castling
            if end_col == start_col + 2:
                rook = board[start_row][start_col + 3]
                if isinstance(rook, Rook) and not rook.has_moved:
                    # Check empty squares between king and rook
                    if board[start_row][start_col + 1] is None and board[start_row][start_col + 2] is None:
                        return True
            # Queenside castling
            elif end_col == start_col - 2:
                rook = board[start_row][start_col - 4]
                if isinstance(rook, Rook) and not rook.has_moved:
                    # Check empty squares between king and rook
                    if (board[start_row][start_col - 1] is None and
                        board[start_row][start_col - 2] is None and
                        board[start_row][start_col - 3] is None):
                        return True

        # Normal king move
        if max(row_diff, col_diff) == 1:
            target_piece = board[end_row][end_col]
            if target_piece is None or target_piece.color != self.color:
                return True
        return False


class ChessGame:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.place_pieces()
        self.move_history = []
        self.current_turn = 'white'

    def place_pieces(self):
        for c in range(8):
            self.board[1][c] = Pawn('white')
            self.board[6][c] = Pawn('black')
        self.board[0][0] = Rook('white')
        self.board[0][7] = Rook('white')
        self.board[7][0] = Rook('black')
        self.board[7][7] = Rook('black')
        self.board[0][1] = Knight('white')
        self.board[0][6] = Knight('white')
        self.board[7][1] = Knight('black')
        self.board[7][6] = Knight('black')
        self.board[0][2] = Bishop('white')
        self.board[0][5] = Bishop('white')
        self.board[7][2] = Bishop('black')
        self.board[7][5] = Bishop('black')
        self.board[0][3] = Queen('white')
        self.board[7][3] = Queen('black')
        self.board[0][4] = King('white')
        self.board[7][4] = King('black')

    def print_board(self):
        print("  a b c d e f g h")
        for row in range(7, -1, -1):
            print(str(row + 1) + " ", end="")
            for col in range(8):
                piece = self.board[row][col]
                print((str(piece) if piece else '.') + " ", end="")
            print(str(row + 1))
        print("  a b c d e f g h")

    def parse_position(self, pos_str):
        if len(pos_str) != 2:
            return None
        col_char, row_char = pos_str[0], pos_str[1]
        if col_char not in 'abcdefgh' or row_char not in '12345678':
            return None
        col = ord(col_char) - ord('a')
        row = int(row_char) - 1
        return (row, col)

    def is_valid_move(self, start, end):
        sr, sc = start
        er, ec = end
        if not (0 <= sr < 8 and 0 <= sc < 8 and 0 <= er < 8 and 0 <= ec < 8):
            return False, "Position out of bounds."
        piece = self.board[sr][sc]
        if piece is None:
            return False, "No piece at starting position."
        if piece.color != self.current_turn:
            return False, f"It is {self.current_turn}'s turn."
        if (er, ec) == (sr, sc):
            return False, "Cannot move to same position."
        if not piece.can_move(self.board, (sr, sc), (er, ec)):
            return False, f"{piece.name} cannot move like that."
        return True, ""

    def move_piece(self, start_str, end_str):
        start = self.parse_position(start_str)
        end = self.parse_position(end_str)
        if start is None or end is None:
            return False, "Invalid position input."
        valid, message = self.is_valid_move(start, end)
        if not valid:
            return False, message
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        captured = self.board[er][ec]

        # Handle castling
        if isinstance(piece, King) and abs(ec - sc) == 2:
            if ec > sc:  # Kingside castling
                rook = self.board[sr][sc + 3]
                if rook is None or rook.has_moved:
                    return False, "Castling not allowed: rook has moved or missing"
                self.board[sr][sc + 1] = rook
                self.board[sr][sc + 3] = None
                rook.has_moved = True
            else:  # Queenside castling
                rook = self.board[sr][sc - 4]
                if rook is None or rook.has_moved:
                    return False, "Castling not allowed: rook has moved or missing"
                self.board[sr][sc - 1] = rook
                self.board[sr][sc - 4] = None
                rook.has_moved = True

        self.board[er][ec] = piece
        self.board[sr][sc] = None
        piece.has_moved = True  # Mark piece as moved

        move_record = f"{piece.name} from {start_str} to {end_str}"
        if captured:
            move_record += f" capturing {captured.name}"
        self.move_history.append(move_record)
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'
        return True, "Move successful."

    def print_move_history(self):
        for idx, move in enumerate(self.move_history, start=1):
            print(f"{idx}. {move}")

    def generate_game_tree(self):
        root = Node("Partida", color="gold")
        current_node = root  # Solo necesitamos un nodo actual para agregar movimientos

        for i in range(len(self.move_history)):
            # Crear un nuevo nodo para cada movimiento realizado
            move_node = Node(self.move_history[i], parent=current_node, color="white" if i % 2 == 0 else "gray")
            current_node = move_node  # Actualizar el nodo actual al nuevo nodo creado

        def node_style(n):
            return f"fillcolor={n.color}, style=filled" if hasattr(n, 'color') else ""

        DotExporter(root, nodenamefunc=lambda n: n.name, nodeattrfunc=node_style).to_dotfile("game_tree.dot")
        os.system("dot -Tpng game_tree.dot -o game_tree.png")
        print("Árbol de partida generado en game_tree.png")


def main():
    game = ChessGame()
    print("Welcome to Python Chess Game!")
    print("Enter moves in format: e2 e4 or O-O / O-O-O for castling")
    while True:
        game.print_board()
        print(f"{game.current_turn.capitalize()}'s turn.")
        user_input = input("Your move (start end) or 'exit': ").strip()

        if user_input.lower() == 'exit':
            break

        # Handling castling commands O-O and O-O-O
        if user_input.upper() == 'O-O':
            # Kingside castling
            row = 0 if game.current_turn == 'white' else 7
            start = 'e' + str(row + 1)
            end = 'g' + str(row + 1)
            success, msg = game.move_piece(start, end)
            print(msg)
            continue
        elif user_input.upper() == 'O-O-O':
            # Queenside castling
            row = 0 if game.current_turn == 'white' else 7
            start = 'e' + str(row + 1)
            end = 'c' + str(row + 1)
            success, msg = game.move_piece(start, end)
            print(msg)
            continue

        # Normal move input
        if len(user_input.split()) != 2:
            print("Invalid input.")
            continue
        start, end = user_input.split()
        success, msg = game.move_piece(start, end)
        print(msg)
    print("Game over. Move history:")
    game.print_move_history()
    game.generate_game_tree()

if __name__ == "__main__":
    main()
