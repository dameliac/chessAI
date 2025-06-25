import chess
import random

# -----------------------------
# board_utils.py
# -----------------------------
def display_board(board):
    """
    Prints the current board state.
    """
    print(board)

def evaluate_board(board):
    """
    Evaluates the current board state and returns a score based on material.
    Positive values favor white, negative values favor black.
    """
    if board.is_checkmate():
        return float('inf') if board.turn == chess.BLACK else float('-inf')
    if board.is_stalemate() or board.is_insufficient_material():
        return 0

    piece_values = {
        chess.PAWN: 1,
        chess.KNIGHT: 3,
        chess.BISHOP: 3,
        chess.ROOK: 5,
        chess.QUEEN: 9,
        chess.KING: 0  # The king is invaluable
    }

    value = 0
    for piece_type in piece_values:
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    return value


# -----------------------------
# minimax.py
# -----------------------------
def minimax_alpha_beta(board, depth, alpha, beta, is_maximizing):
    """
    Minimax algorithm with alpha-beta pruning.
    Returns the best evaluation score from the current position.
    """
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    if is_maximizing:
        max_eval = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval = minimax_alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def get_best_move(board, depth):
    """
    Returns the best move for the current board state using Minimax with Alpha-Beta pruning.
    """
    best_move = None
    max_eval = float('-inf')

    for move in board.legal_moves:
        board.push(move)
        eval = minimax_alpha_beta(board, depth - 1, float('-inf'), float('inf'), False)
        board.pop()
        if eval > max_eval:
            max_eval = eval
            best_move = move
    return best_move


# -----------------------------
# game.py (main script)
# -----------------------------
def play_game():
    """
    Main game loop where the AI plays against a human.
    """
    board = chess.Board()

    while not board.is_game_over():
        display_board(board)

        if board.turn == chess.WHITE:
            print("\nAI (White) is thinking...")
            move = get_best_move(board, 3)
            if move is None:
                print("No valid moves! Game over.")
                break
            print(f"AI Move: {move}")
        else:
            user_input = input("\nYour move (as Black, e.g., e7e5): ")
            try:
                move = chess.Move.from_uci(user_input)
                if move not in board.legal_moves:
                    print("Illegal move. Try again.")
                    continue
            except:
                print("Invalid format. Use UCI like e2e4.")
                continue

        board.push(move)

    display_board(board)
    print("\nGame Over! Result:", board.result())


# -----------------------------
# Run the Game
# -----------------------------
if __name__ == "__main__":
    play_game()
