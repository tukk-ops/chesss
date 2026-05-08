import random
from constants import PIECE_VALUES
from pieces import Queen, Pawn
from logic import get_legal_moves

def evaluate_board(piece_list):
    score = 0
    for p in piece_list:
        val = PIECE_VALUES[p.__class__.__name__]
        score += val if p.color == "black" else -val
    return score

def ai_make_move(piece_list):
    all_possible_actions = []
    for p in [p for p in piece_list if p.color == "black"]:
        for m in get_legal_moves(p, piece_list):
            all_possible_actions.append((p, m))

    if not all_possible_actions:
        return None

    best_score = -float('inf')
    best_move = None
    random.shuffle(all_possible_actions)

    for piece, move in all_possible_actions:
        orig_pos = (piece.x, piece.y)
        target = next((p for p in piece_list if p.x == move[0] and p.y == move[1]), None)
        if target: piece_list.remove(target)
        piece.x, piece.y = move[0], move[1]
        current_eval = evaluate_board(piece_list)
        if current_eval > best_score:
            best_score = current_eval
            best_move = (piece, move, target)
        piece.x, piece.y = orig_pos
        if target: piece_list.append(target)

    return best_move # Returns (piece, move, target)
