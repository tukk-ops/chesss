class Piece:
    def __init__(self, color, x, y):
        self.color = color
        self.x = x
        self.y = y

    def is_on_board(self, x, y): 
        return 0 <= x < 8 and 0 <= y < 8

    def get_piece_at(self, x, y, board_pieces):
        for p in board_pieces:
            if p.x == x and p.y == y: return p
        return None

    def check_cell_status(self, x, y, board_pieces):
        if not self.is_on_board(x, y): return -1
        target = self.get_piece_at(x, y, board_pieces)
        if target is None: return 0 
        return 1 if target.color == self.color else 2 

class Pawn(Piece):
    def get_valid_moves(self, board_pieces):
        moves = []
        direction = -1 if self.color == "white" else 1
        if self.check_cell_status(self.x, self.y + direction, board_pieces) == 0:
            moves.append((self.x, self.y + direction))
            start_row = 6 if self.color == "white" else 1
            if self.y == start_row and self.check_cell_status(self.x, self.y + 2*direction, board_pieces) == 0:
                moves.append((self.x, self.y + 2*direction))
        for dx in [-1, 1]:
            if self.check_cell_status(self.x + dx, self.y + direction, board_pieces) == 2:
                moves.append((self.x + dx, self.y + direction))
        return moves

class Knight(Piece):
    def get_valid_moves(self, board_pieces):
        moves = []
        for dx, dy in [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]:
            status = self.check_cell_status(self.x+dx, self.y+dy, board_pieces)
            if status in [0, 2]: moves.append((self.x+dx, self.y+dy))
        return moves

class King(Piece):
    def get_valid_moves(self, board_pieces):
        moves = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            status = self.check_cell_status(self.x+dx, self.y+dy, board_pieces)
            if status in [0, 2]: moves.append((self.x+dx, self.y+dy))
        return moves

class SlidingPiece(Piece):
    def get_sliding_moves(self, directions, board_pieces):
        moves = []
        for dx, dy in directions:
            nx, ny = self.x + dx, self.y + dy
            while self.is_on_board(nx, ny):
                status = self.check_cell_status(nx, ny, board_pieces)
                if status == 0: moves.append((nx, ny))
                elif status == 1: break
                elif status == 2: moves.append((nx, ny)); break
                nx += dx; ny += dy
        return moves

class Rook(SlidingPiece):
    def get_valid_moves(self, board_pieces): 
        return self.get_sliding_moves([(1,0),(-1,0),(0,1),(0,-1)], board_pieces)

class Bishop(SlidingPiece):
    def get_valid_moves(self, board_pieces): 
        return self.get_sliding_moves([(1,1),(1,-1),(-1,1),(-1,-1)], board_pieces)

class Queen(SlidingPiece):
    def get_valid_moves(self, board_pieces): 
        return self.get_sliding_moves([(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)], board_pieces)
