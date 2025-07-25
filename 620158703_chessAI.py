import chess
import pygame
import random
import sys

# --- Constants for Pygame GUI ---
WIDTH = 600
HEIGHT = 600
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# --- Colors for the chessboard ---
LIGHT_SQUARE_COLOR = pygame.Color("#eeeed2")
DARK_SQUARE_COLOR = pygame.Color("#ADD8E6")

# --- Colors for highlights and messages ---
HIGHLIGHT_SELECTED_COLOR = (0, 255, 0, 100) # Green with transparency for selected square
HIGHLIGHT_MOVE_COLOR = (0, 0, 255, 100)     # Blue with transparency for legal moves
TEXT_COLOR = (0, 0, 0)                      # Black for general status text
CHECK_COLOR = (255, 0, 0)                   # Red for check message
STATUS_BAR_BG_COLOR = (200, 200, 200, 150)  # Light gray with transparency for status bar background

# --- Load Piece Images ---
def load_images():
    """
    Loads all chess piece images into the IMAGES dictionary,
    mapping the user's full file names to the internal piece symbols
    expected by the drawing logic.
    """
    # This map links the internal symbol (e.g., 'wp') to the actual filename prefix (e.g., 'white-pawn')
    piece_filename_map = {
        'wP': 'white-pawn', 'wR': 'white-rook', 'wN': 'white-knight',
        'wB': 'white-bishop', 'wQ': 'white-queen', 'wK': 'white-king',
        'bP': 'black-pawn', 'bR': 'black-rook', 'bN': 'black-knight',
        'bB': 'black-bishop', 'bQ': 'black-queen', 'bK': 'black-king'
    }

    for piece_key, filename_prefix in piece_filename_map.items():
        try:
            # Construct the image path using the filename prefix
            image_path = f"images/{filename_prefix}.png"
            IMAGES[piece_key] = pygame.transform.scale(pygame.image.load(image_path), (SQ_SIZE, SQ_SIZE))
        except pygame.error as e:
            print(f"Error loading image {image_path}: {e}")
            print("Please ensure you have an 'images' folder with all piece PNGs named correctly (e.g., white-pawn.png, black-king.png).")
            sys.exit()

# -----------------------------
# board_utils
# -----------------------------
def evaluate_board(board):
    """
    Evaluates the current board state and returns a score based on material.
    Positive values favour white, negative values favour black.
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
        chess.KING: 0
    }

    value = 0
    for piece_type in piece_values:
        value += len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
        value -= len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
    return value

# -----------------------------
# minimax
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
    else: # is_minimizing
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
    # Initialize max_eval based on whose turn it is for the AI
    max_eval = float('-inf') if board.turn == chess.WHITE else float('inf')

    legal_moves_list = list(board.legal_moves)
    random.shuffle(legal_moves_list) # Add randomness for moves with equal evaluation

    for move in legal_moves_list:
        board.push(move)
        # The AI is playing for the current board.turn.
        # The next recursive call will evaluate the opponent's response, so `is_maximizing` flips.
        eval = minimax_alpha_beta(board, depth - 1, float('-inf'), float('inf'), not board.turn)
        board.pop()

        if board.turn == chess.WHITE: # AI is White (maximizing player)
            if eval > max_eval:
                max_eval = eval
                best_move = move
        else: # AI is Black (minimizing player)
            if eval < max_eval: # For minimizing player, we look for the smallest eval
                max_eval = eval
                best_move = move
    return best_move

# -----------------------------
# Pygame GUI Functions
# -----------------------------

def draw_board(screen):
    """
    Draws the chessboard squares.
    """
    colors = [LIGHT_SQUARE_COLOR, DARK_SQUARE_COLOR]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            pygame.draw.rect(screen, color, pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    """
    Draws the chess pieces on the board.
    """
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board.piece_at(chess.square(c, 7 - r)) # Convert Pygame row to chess rank
            if piece:
                piece_symbol = piece.symbol()
                # Construct the key for the IMAGES dictionary (e.g., 'wp', 'bK')
                img_name = ('b' if piece_symbol.islower() else 'w') + piece_symbol.upper()
                screen.blit(IMAGES[img_name], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_highlights(screen, sq_selected, legal_moves_highlights):
    """
    Draws highlights for the selected square and legal moves.
    """
    s = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA) # Create a transparent surface
    s.fill(HIGHLIGHT_SELECTED_COLOR) # Fill with transparent green for selected square

    # Highlight the selected square
    if sq_selected:
        r, c = sq_selected
        screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

    # Highlight legal moves with a transparent blue circle
    for r, c in legal_moves_highlights:
        center_x = c * SQ_SIZE + SQ_SIZE // 2
        center_y = r * SQ_SIZE + SQ_SIZE // 2
        pygame.draw.circle(screen, HIGHLIGHT_MOVE_COLOR, (center_x, center_y), SQ_SIZE // 3)

def draw_game_status(screen, message, color):
    """
    Displays game status messages at the top of the screen with a background.
    """
    font = pygame.font.Font(None, 36) # Smaller font for status bar
    text_surface = font.render(message, True, color)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, SQ_SIZE // 4))

    # Create a surface for the background with transparency
    bg_surface = pygame.Surface(text_rect.size, pygame.SRCALPHA)
    bg_surface.fill(STATUS_BAR_BG_COLOR) # Fill with the chosen background color

    # Blit the background surface first, then the text
    screen.blit(bg_surface, text_rect.topleft)
    screen.blit(text_surface, text_rect)


def display_game_over_message(screen, message):
    """
    Displays the final game over message centered on the screen.
    """
    font = pygame.font.Font(None, 74)
    text = font.render(message, True, CHECK_COLOR) # Uses CHECK_COLOR (red) for game over
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(text, text_rect)

def main():
    """
    Main function to run the chess game with Pygame GUI.
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Chess AI")
    clock = pygame.time.Clock()
    screen.fill(LIGHT_SQUARE_COLOR)

    board = chess.Board()
    load_images()

    running = True
    sq_selected = () # (row, col) of the square clicked (empty tuple means no square selected)
    player_clicks = [] # list of (row, col) for two clicks (start and end square)
    legal_moves_highlights = [] # list of (row, col) for legal destination squares to highlight

    game_over = False
    AI_DEPTH = 3 # AI search depth

    # --- NEW: Define AI's color and initialize ai_thinking ---
    AI_COLOR = chess.WHITE # AI plays as White
    ai_thinking = False

    # Check if AI should make the very first move
    if board.turn == AI_COLOR:
        ai_thinking = True
    # --- END NEW ---

    game_status_text = "" # Text for the status bar

    # Main game loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not game_over:
                    # --- NEW: Only allow human clicks if it's the human's turn ---
                    if board.turn != AI_COLOR:
                        location = pygame.mouse.get_pos() # Get mouse click coordinates (x, y)
                        col = location[0] // SQ_SIZE       # Convert x to column index
                        row = location[1] // SQ_SIZE       # Convert y to row index

                        clicked_pygame_square = (row, col) # Pygame (row, col) of the clicked square
                        clicked_chess_square = chess.square(col, 7 - row) # Convert to python-chess square

                        if sq_selected == clicked_pygame_square: # User clicked the same square twice (deselect)
                            sq_selected = ()
                            player_clicks = []
                            legal_moves_highlights = []
                        elif not sq_selected: # First click: try to select a piece
                            piece_on_clicked_square = board.piece_at(clicked_chess_square)
                            # Ensure human can only select their own pieces
                            if piece_on_clicked_square and piece_on_clicked_square.color == board.turn:
                                # Valid first click: select the piece and find its legal moves
                                sq_selected = clicked_pygame_square
                                player_clicks.append(sq_selected)
                                legal_moves_highlights = []
                                for move in board.legal_moves:
                                    if move.from_square == clicked_chess_square:
                                        target_row = 7 - chess.square_rank(move.to_square)
                                        target_col = chess.square_file(move.to_square)
                                        legal_moves_highlights.append((target_row, target_col))
                            else: # Clicked on an empty square or opponent's piece first (invalid selection)
                                sq_selected = () # Ensure nothing is selected
                                player_clicks = []
                                legal_moves_highlights = []
                        else: # Second click: attempt to make a move
                            player_clicks.append(clicked_pygame_square)
                            start_row, start_col = player_clicks[0]
                            end_row, end_col = player_clicks[1]

                            start_square_uci = chess.square_name(chess.square(start_col, 7 - start_row))
                            end_square_uci = chess.square_name(chess.square(end_col, 7 - end_row))
                            move_uci = start_square_uci + end_square_uci

                            # Pawn promotion handling: default to queen if pawn reaches last rank
                            piece_on_start_square = board.piece_at(chess.parse_square(start_square_uci))
                            if piece_on_start_square and piece_on_start_square.piece_type == chess.PAWN:
                                if (board.turn == chess.WHITE and end_row == 0) or \
                                   (board.turn == chess.BLACK and end_row == 7):
                                    move_uci += 'q' # Append 'q' for queen promotion

                            try:
                                move = chess.Move.from_uci(move_uci)
                                if move in board.legal_moves:
                                    board.push(move) # Make the move on the chess board
                                    game_over = board.is_game_over() # Check if game ended
                                    sq_selected = () # Reset selection
                                    player_clicks = [] # Clear clicks
                                    legal_moves_highlights = [] # Clear highlights after successful move

                                    # --- NEW: Check if it's AI's turn after human move ---
                                    if not game_over and board.turn == AI_COLOR:
                                        ai_thinking = True
                                    # --- END NEW ---
                                else:
                                    # If illegal move, keep the first click selection to allow user to try another destination
                                    print("Illegal move. Try again.")
                                    player_clicks = [sq_selected] # Keep the first clicked square in player_clicks
                            except ValueError as e:
                                # If UCI format is invalid, clear everything to force re-selection
                                print(f"Invalid move format or parsing error: {e}. Input UCI: {move_uci}")
                                sq_selected = ()
                                player_clicks = []
                                legal_moves_highlights = []
                    else:
                        print("It's the AI's turn!") # Inform user if they click when it's AI's turn
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: # 'r' key to reset the board
                    board = chess.Board()
                    game_over = False
                    ai_thinking = False
                    sq_selected = ()
                    player_clicks = []
                    legal_moves_highlights = []
                    # --- NEW: Re-check initial AI turn after reset ---
                    if board.turn == AI_COLOR:
                        ai_thinking = True
                    # --- END NEW ---
                    print("Board reset!")
                if event.key == pygame.K_z: # 'z' key to undo the last move(s)
                    if board.fullmove_number > 1: # Ensure there's at least one move to undo
                        # Undo human's move
                        if board.turn != AI_COLOR: # If it was human's turn, undo their move
                            board.pop()
                        # If AI just moved (and it's now human's turn), undo its move too
                        if board.fullmove_number > 1 and board.turn == AI_COLOR:
                             board.pop()

                        game_over = False
                        ai_thinking = False
                        sq_selected = ()
                        player_clicks = []
                        legal_moves_highlights = []
                        # --- NEW: Re-check AI turn after undo ---
                        if not game_over and board.turn == AI_COLOR:
                            ai_thinking = True
                        # --- END NEW ---
                        print("Last move(s) undone.")


        # AI's turn to make a move
        if not game_over and ai_thinking:
            print(f"\nAI ({'White' if AI_COLOR == chess.WHITE else 'Black'}) is thinking...")
            ai_move = get_best_move(board, AI_DEPTH)
            if ai_move:
                board.push(ai_move) # Make the AI's move
                print(f"AI Move: {ai_move}")
                game_over = board.is_game_over() # Check if game ended after AI's move
            else:
                print("AI could not find a valid move. Game over.")
                game_over = True # End game if AI has no valid moves
            ai_thinking = False # AI has finished thinking and made its move

        # --- Update Game Status Text ---
        if not game_over:
            turn_color_name = "White" if board.turn == chess.WHITE else "Black"
            game_status_text = f"{turn_color_name} to Move"
            if board.is_check():
                game_status_text += f" - {turn_color_name} in Check!"
                status_text_color = CHECK_COLOR # Red for check message
            else:
                status_text_color = TEXT_COLOR # Black for regular status
        else:
            game_status_text = "" # Clear status bar if game is over
            status_text_color = TEXT_COLOR # Default color, not displayed but good practice

        # --- Drawing everything on the screen ---
        draw_board(screen)
        draw_highlights(screen, sq_selected, legal_moves_highlights) # Draw highlights first
        draw_pieces(screen, board)

        # Display game over message or status bar
        if game_over:
            display_game_over_message(screen, f"Game Over! {board.result()}")
        else:
            draw_game_status(screen, game_status_text, status_text_color)

        pygame.display.flip() # Update the full display Surface to the screen
        clock.tick(MAX_FPS) # Control the frame rate

    pygame.quit() # Uninitialize Pygame modules
    sys.exit() # Exit the program cleanly

if __name__ == "__main__":
    main()
