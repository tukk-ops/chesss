from pieces import King

def is_in_check(color, piece_list):
    king = next((p for p in piece_list if isinstance(p, King) and p.color == color), None)
    if not king: return True
    for p in piece_list:
        if p.color != color:
            if (king.x, king.y) in p.get_valid_moves(piece_list):
                return True
    return False

def get_legal_moves(piece, piece_list):
    pseudo_moves = piece.get_valid_moves(piece_list)
    legal_moves = []
    orig_x, orig_y = piece.x, piece.y
    for mx, my in pseudo_moves:
        target = next((p for p in piece_list if p.x == mx and p.y == my), None)
        if target: piece_list.remove(target)
        piece.x, piece.y = mx, my
        if not is_in_check(piece.color, piece_list):
            legal_moves.append((mx, my))
        piece.x, piece.y = orig_x, orig_y
        if target: piece_list.append(target)
    return legal_moves
