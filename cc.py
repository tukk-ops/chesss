import tkinter as tk
from tkinter import messagebox
import random

# --- 1. 棋子類別體系 (延續原有設計) ---
# 包含 Piece, Pawn, King, Knight, SlidingPiece, Rook, Bishop, Queen
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

class King(Piece):
    def get_valid_moves(self, board_pieces):
        moves = []
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]:
            status = self.check_cell_status(self.x+dx, self.y+dy, board_pieces)
            if status in [0, 2]: moves.append((self.x+dx, self.y+dy))
        return moves

class Knight(Piece):
    def get_valid_moves(self, board_pieces):
        moves = []
        for dx, dy in [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]:
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
    def get_valid_moves(self, board_pieces): return self.get_sliding_moves([(1,0),(-1,0),(0,1),(0,-1)], board_pieces)
class Bishop(SlidingPiece):
    def get_valid_moves(self, board_pieces): return self.get_sliding_moves([(1,1),(1,-1),(-1,1),(-1,-1)], board_pieces)
class Queen(SlidingPiece):
    def get_valid_moves(self, board_pieces): return self.get_sliding_moves([(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)], board_pieces)

# --- 2. 整合版遊戲主程式 ---
class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("西洋棋：多功能對戰版")
        self.symbols = {"Pawn": "♙", "Knight": "♘", "Bishop": "♗", "Rook": "♖", "Queen": "♕", "King": "♔"}
        self.piece_values = {"Pawn": 10, "Knight": 30, "Bishop": 30, "Rook": 50, "Queen": 90, "King": 900}
        
        # 遊戲模式狀態： "PVE" (人機) 或 "PVP" (雙人)
        self.game_mode = tk.StringVar(value="PVE")
        
        # UI 佈局
        self.canvas = tk.Canvas(root, width=480, height=480)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        self.info_panel = tk.Frame(root)
        self.info_panel.grid(row=0, column=1, sticky="ns", padx=10)
        
        # 模式選擇區
        tk.Label(self.info_panel, text="遊戲模式：", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        tk.Radiobutton(self.info_panel, text="玩家 vs AI", variable=self.game_mode, value="PVE", command=self.init_game).pack(anchor="w")
        tk.Radiobutton(self.info_panel, text="玩家 vs 玩家", variable=self.game_mode, value="PVP", command=self.init_game).pack(anchor="w")
        
        self.turn_label = tk.Label(self.info_panel, text="回合：白棋", font=("Arial", 16), width=14)
        self.turn_label.pack(pady=20)
        
        tk.Button(self.info_panel, text="重新開始", command=self.init_game, width=15).pack(side="bottom", pady=20)
        
        self.canvas.bind("<Button-1>", self.handle_click)
        self.init_game()

    def init_game(self):
        self.pieces = []
        self.current_turn = "white"
        self.selected_piece, self.valid_moves = None, []
        self.is_game_over = False
        
        layout = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(layout):
            self.pieces.append(cls("black", i, 0))
            self.pieces.append(Pawn("black", i, 1))
            self.pieces.append(cls("white", i, 7))
            self.pieces.append(Pawn("white", i, 6))
        self.render()

    # --- 邏輯判定 (參考原代碼設計) ---
    def is_in_check(self, color, piece_list):
        king = next((p for p in piece_list if isinstance(p, King) and p.color == color), None)
        if not king: return True
        for p in piece_list:
            if p.color != color:
                if (king.x, king.y) in p.get_valid_moves(piece_list):
                    return True
        return False

    def get_legal_moves(self, piece):
        pseudo_moves = piece.get_valid_moves(self.pieces)
        legal_moves = []
        orig_x, orig_y = piece.x, piece.y
        for mx, my in pseudo_moves:
            target = next((p for p in self.pieces if p.x == mx and p.y == my), None)
            if target: self.pieces.remove(target)
            piece.x, piece.y = mx, my
            if not self.is_in_check(piece.color, self.pieces):
                legal_moves.append((mx, my))
            piece.x, piece.y = orig_x, orig_y
            if target: self.pieces.append(target)
        return legal_moves

    # --- AI 決策邏輯 (參考原代碼設計) ---
    def evaluate_board(self):
        score = 0
        for p in self.pieces:
            val = self.piece_values[p.__class__.__name__]
            score += val if p.color == "black" else -val
        return score

    def ai_make_move(self):
        if self.is_game_over or self.game_mode.get() != "PVE": return

        all_possible_actions = []
        for p in [p for p in self.pieces if p.color == "black"]:
            for m in self.get_legal_moves(p):
                all_possible_actions.append((p, m))

        if not all_possible_actions:
            self.check_end_game()
            return

        best_score = -float('inf')
        best_move = None
        random.shuffle(all_possible_actions)

        for piece, move in all_possible_actions:
            orig_pos = (piece.x, piece.y)
            target = next((p for p in self.pieces if p.x == move[0] and p.y == move[1]), None)
            if target: self.pieces.remove(target)
            piece.x, piece.y = move[0], move[1]
            current_eval = self.evaluate_board()
            if current_eval > best_score:
                best_score = current_eval
                best_move = (piece, move, target)
            piece.x, piece.y = orig_pos
            if target: self.pieces.append(target)

        p, m, t = best_move
        if t: self.pieces.remove(t)
        p.x, p.y = m[0], m[1]
        
        if isinstance(p, Pawn) and p.y == 7:
            self.pieces.remove(p)
            self.pieces.append(Queen("black", p.x, p.y))
        self.end_turn()

    # --- 滑鼠點擊處理 (整合雙模式判斷) ---
    def handle_click(self, event):
        if self.is_game_over: return
        
        # 在人機模式下，黑棋回合禁止點擊
        if self.game_mode.get() == "PVE" and self.current_turn == "black": return
        
        gx, gy = event.x // 60, event.y // 60
        if self.selected_piece and (gx, gy) in self.valid_moves:
            target = next((p for p in self.pieces if p.x == gx and p.y == gy), None)
            if target: self.pieces.remove(target)
            self.selected_piece.x, self.selected_piece.y = gx, gy
            
            # 升變邏輯
            if isinstance(self.selected_piece, Pawn):
                if (self.selected_piece.color == "white" and gy == 0) or \
                   (self.selected_piece.color == "black" and gy == 7):
                    color = self.selected_piece.color
                    self.pieces.remove(self.selected_piece)
                    self.pieces.append(Queen(color, gx, gy))
            self.end_turn()
        else:
            clicked = next((p for p in self.pieces if p.x == gx and p.y == gy), None)
            # 選取規則：必須選取當前回合顏色的棋子
            if clicked and clicked.color == self.current_turn:
                self.selected_piece = clicked
                self.valid_moves = self.get_legal_moves(clicked)
            else:
                self.selected_piece, self.valid_moves = None, []
        self.render()

    def end_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"
        self.selected_piece, self.valid_moves = None, []
        self.render()
        self.check_end_game()
        
        # 如果是人機模式，切換到黑棋時呼叫 AI
        if not self.is_game_over and self.game_mode.get() == "PVE" and self.current_turn == "black":
            self.root.after(600, self.ai_make_move)

    def check_end_game(self):
        has_moves = any(self.get_legal_moves(p) for p in self.pieces if p.color == self.current_turn)
        if not has_moves:
            self.is_game_over = True
            if self.is_in_check(self.current_turn, self.pieces):
                winner = "白棋" if self.current_turn == "black" else "黑棋"
                messagebox.showinfo("結束", f"將死！勝者：{winner}")
            else:
                messagebox.showinfo("結束", "逼和！")

    def render(self):
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                color = "#ebecd0" if (r + c) % 2 == 0 else "#779556"
                self.canvas.create_rectangle(c*60, r*60, (c+1)*60, (r+1)*60, fill=color, outline="")
        for mx, my in self.valid_moves:
            self.canvas.create_oval(mx*60+22, my*60+22, (mx+1)*60-22, (my+1)*60-22, fill="gray", stipple="gray50")
        for p in self.pieces:
            color = "white" if p.color == "white" else "black"
            if p == self.selected_piece:
                self.canvas.create_rectangle(p.x*60, p.y*60, (p.x+1)*60, (p.y+1)*60, outline="yellow", width=3)
            # 使用更精緻的符號顯示
            self.canvas.create_text(p.x*60+30, p.y*60+30, text=self.symbols[p.__class__.__name__], fill=color, font=("Arial", 32))
        
        mode_str = "(AI)" if (self.game_mode.get() == "PVE" and self.current_turn == "black") else ""
        self.turn_label.config(text=f"回合：{'白棋' if self.current_turn == 'white' else '黑棋'} {mode_str}")

if __name__== "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()