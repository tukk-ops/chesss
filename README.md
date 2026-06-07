西洋棋專案終極原始碼剖析報告
這份報告將以「函數等級」甚至「逐行細節」來拆解整個專案，並附上系統架構與狀態機的運作流程圖。適合開發者直接閱讀以進行二次開發或除錯。
1. main.py 深入剖析
__init__ 與介面綁定
python

self.canvas.bind("<Button-1>", self.handle_click)
<Button-1> 綁定了滑鼠左鍵。當玩家點擊畫布時，event.x 與 event.y 捕捉的是像素點。
棋盤為 480x480，分為 8x8 格，每格 60 像素。gx, gy = event.x // 60, event.y // 60 這一行將像素轉換為二維陣列索引。
promote_pawn(self, pawn, gx, gy) 阻斷式對話框
python

promo_win.transient(self.root)
promo_win.grab_set()
self.root.wait_window(promo_win)
transient: 確保對話框依附在主視窗之上。
grab_set(): 擷取所有 UI 事件，玩家在選完升變棋子前，無法點擊原來的棋盤。
wait_window(): 暫停程式執行緒，直到 promo_win 被 destroy() 才繼續執行後面的陣列替換操作。這是 Tkinter 常用的強制阻斷流法。
execute_ai_move(self) 非同步更新
python

self.root.after(600, self.execute_ai_move)
如果用 time.sleep(0.6) 會導致 UI 卡死。after 是 Tkinter 的事件迴圈計時器，能在 0.6 秒後觸發 AI 計算，讓 UI 能在此期間順暢繪製剛才玩家走的棋。
2. logic.py 深入剖析
get_legal_moves 的還原機制 (Backtracking)
python

orig_x, orig_y = piece.x, piece.y
for mx, my in pseudo_moves:
    target = next((p for p in piece_list if p.x == mx and p.y == my), None)
    if target: piece_list.remove(target)
    piece.x, piece.y = mx, my
    
    if not is_in_check(piece.color, piece_list):
        legal_moves.append((mx, my))
        
    piece.x, piece.y = orig_x, orig_y
    if target: piece_list.append(target)
next((p for p ...), None)：Pythonic 的尋找方式，若目標格子有棋子，就抓出來當作 target。
狀態保存：先保存 orig_x, orig_y。
狀態破壞：從陣列拔掉 target，把自己的座標改到 mx, my。
狀態驗證：呼叫 is_in_check。
狀態復原：把自己的座標改回去，如果剛才拔掉了 target，用 append 把它塞回陣列。這保證了檢查完後，真正的全域盤面不受污染。
3. ai.py 深入剖析
evaluate_board 評分邏輯
python

val = PIECE_VALUES[p.__class__.__name__]
score += val if p.color == "black" else -val
p.__class__.__name__ 會拿到類別字串，例如 "King" 或 "Pawn"。
黑方（AI）角度：所有黑棋的價值為正數，白棋為負數。盤面分數越高，代表黑棋子力比白棋強。
ai_make_move 決策邏輯
這段代碼包含了兩層迴圈：

收集階段：

python

for p in [p for p in piece_list if p.color == "black"]:
    for m in get_legal_moves(p, piece_list):
將所有黑棋能走的合法組合 (p, m) 放入 all_possible_actions 列表。

洗牌階段：

python

random.shuffle(all_possible_actions)
如果有多個走法導致相同的 best_score（例如第一回合，怎麼走分數都一樣），沒有洗牌會導致 AI 永遠走陣列的第一個元素。加上洗牌能讓 AI 落子具有隨機多樣性。

打分階段： 這段跟 logic.py 的模擬一模一樣，把棋子移過去，計算 evaluate_board，如果 current_eval > best_score，就覆蓋 best_move。

4. pieces.py 深入剖析
這個檔案示範了完美的 Python Duck Typing (鴨子型別) 與繼承。

check_cell_status
python

if target is None: return 0 
return 1 if target.color == self.color else 2
所有步長判斷都依賴這個函數。0 代表可以移動，1 代表被自己人卡死，2 代表可以移動並吃掉敵人。

SlidingPiece.get_sliding_moves (滑動軌跡演算法)
python

nx += dx; ny += dy
這是一段 Ray-casting (光線投射) 的變體：

迴圈設定每次步進 dx, dy。
只要還在棋盤內 (is_on_board) 就一直跑。
遇到 0 就加入陣列，然後繼續 nx += dx; ny += dy。
遇到 1 (友軍) 直接 break 終止該方向的光線。
遇到 2 (敵軍) 先把該點加入陣列（吃子），然後 break 終止該方向（不能穿透敵軍繼續走）。
具象化類別的實作
python

class Rook(SlidingPiece):
    def get_valid_moves(self, board_pieces): 
        return self.get_sliding_moves([(1,0),(-1,0),(0,1),(0,-1)], board_pieces)
車 (Rook) 只需要宣告這四個十字方向向量，複雜的光線投射邏輯全交給父類別 SlidingPiece 處理，極大地維持了代碼的 DRY (Don't Repeat Yourself) 原則。

5. constants.py
雖然只有五行，但將 PIECE_VALUES 與 SYMBOLS 獨立出來的好處是： 如果今天要設計「變種西洋棋」，或調整 AI 對王后與車的偏好（例如修改 Queen: 120 讓 AI 更瘋狂保后），開發者完全不需要去碰核心演算法，只需修改常數檔即可。

6. 
uiux的使用者介面，這種輔助介面，有多元的語言可供選擇 演算法，也是有更多元選擇，單依賴貪婪過於偏激，且在部分時刻，會沒感覺笨笨的。








<img width="1295" height="1552" alt="image" src="https://github.com/user-attachments/assets/627bf98e-25eb-40f7-aa47-ca2b63cc362f" />

