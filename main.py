import tkinter as tk
from tkinter import messagebox
from constants import SYMBOLS, LIGHT_COLOR, DARK_COLOR
from pieces import Pawn, Knight, Bishop, Rook, Queen, King
from logic import is_in_check, get_legal_moves
from ai import ai_make_move

class ChessApp:
    def __init__(self, root):
        self.root = root
        self.root.title("西洋棋：多功能對戰版")
        
        self.game_mode = tk.StringVar(value="PVE")
        
        self.canvas = tk.Canvas(root, width=480, height=480)
        self.canvas.grid(row=0, column=0, padx=10, pady=10)
        
        self.info_panel = tk.Frame(root)
        self.info_panel.grid(row=0, column=1, sticky="ns", padx=10)
        
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

    def handle_click(self, event):
        if self.is_game_over: return
        if self.game_mode.get() == "PVE" and self.current_turn == "black": return
        
        gx, gy = event.x // 60, event.y // 60
        if self.selected_piece and (gx, gy) in self.valid_moves:
            target = next((p for p in self.pieces if p.x == gx and p.y == gy), None)
            if target: self.pieces.remove(target)
            self.selected_piece.x, self.selected_piece.y = gx, gy
            
            if isinstance(self.selected_piece, Pawn):
                if (self.selected_piece.color == "white" and gy == 0) or \
                   (self.selected_piece.color == "black" and gy == 7):
                    self.promote_pawn(self.selected_piece, gx, gy)
                    return
            self.end_turn()
        else:
            clicked = next((p for p in self.pieces if p.x == gx and p.y == gy), None)
            if clicked and clicked.color == self.current_turn:
                self.selected_piece = clicked
                self.valid_moves = get_legal_moves(clicked, self.pieces)
            else:
                self.selected_piece, self.valid_moves = None, []
        self.render()

    def promote_pawn(self, pawn, gx, gy):
        self.render()
        promo_win = tk.Toplevel(self.root)
        promo_win.title("選擇升變")
        
        x = self.root.winfo_rootx() + 50
        y = self.root.winfo_rooty() + 100
        promo_win.geometry(f"+{x}+{y}")
        promo_win.transient(self.root)
        promo_win.grab_set()

        tk.Label(promo_win, text="請選擇要升變的棋子：", font=("Arial", 12)).pack(pady=10)
        btn_frame = tk.Frame(promo_win)
        btn_frame.pack(pady=10)

        chosen_cls = [Queen]
        def on_choose(cls):
            chosen_cls[0] = cls
            promo_win.destroy()

        piece_options = [(Queen, "♕ 皇后"), (Rook, "♖ 城堡"), (Bishop, "♗ 主教"), (Knight, "♘ 騎士")]
        for cls, text in piece_options:
            tk.Button(btn_frame, text=text, font=("Arial", 12), width=8, command=lambda c=cls: on_choose(c)).pack(side="left", padx=5)

        self.root.wait_window(promo_win)
        
        color = pawn.color
        self.pieces.remove(pawn)
        self.pieces.append(chosen_cls[0](color, gx, gy))
        self.end_turn()

    def end_turn(self):
        self.current_turn = "black" if self.current_turn == "white" else "white"
        self.selected_piece, self.valid_moves = None, []
        self.render()
        self.check_end_game()
        
        if not self.is_game_over and self.game_mode.get() == "PVE" and self.current_turn == "black":
            self.root.after(600, self.execute_ai_move)

    def execute_ai_move(self):
        move_data = ai_make_move(self.pieces)
        if move_data:
            p, m, t = move_data
            if t: self.pieces.remove(t)
            p.x, p.y = m[0], m[1]
            
            if isinstance(p, Pawn) and p.y == 7:
                self.pieces.remove(p)
                self.pieces.append(Queen("black", p.x, p.y))
            self.end_turn()
        else:
            self.check_end_game()

    def check_end_game(self):
        has_moves = any(get_legal_moves(p, self.pieces) for p in self.pieces if p.color == self.current_turn)
        if not has_moves:
            self.is_game_over = True
            if is_in_check(self.current_turn, self.pieces):
                winner = "白棋" if self.current_turn == "black" else "黑棋"
                messagebox.showinfo("結束", f"將死！勝者：{winner}")
            else:
                messagebox.showinfo("結束", "逼和！")

    def render(self):
        self.canvas.delete("all")
        for r in range(8):
            for c in range(8):
                color = LIGHT_COLOR if (r + c) % 2 == 0 else DARK_COLOR
                self.canvas.create_rectangle(c*60, r*60, (c+1)*60, (r+1)*60, fill=color, outline="")
        for mx, my in self.valid_moves:
            self.canvas.create_oval(mx*60+22, my*60+22, (mx+1)*60-22, (my+1)*60-22, fill="gray", stipple="gray50")
        for p in self.pieces:
            color = "white" if p.color == "white" else "black"
            if p == self.selected_piece:
                self.canvas.create_rectangle(p.x*60, p.y*60, (p.x+1)*60, (p.y+1)*60, outline="yellow", width=3)
            self.canvas.create_text(p.x*60+30, p.y*60+30, text=SYMBOLS[p.__class__.__name__], fill=color, font=("Arial", 32))
        
        mode_str = "(AI)" if (self.game_mode.get() == "PVE" and self.current_turn == "black") else ""
        self.turn_label.config(text=f"回合：{'白棋' if self.current_turn == 'white' else '黑棋'} {mode_str}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChessApp(root)
    root.mainloop()
