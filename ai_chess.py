import time
import random
import chess

# --- AI PLAYER 1: The Chaos Agent ---
def random_bot(board):
    """Selects a completely random move from all legal options."""
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves)

# --- AI PLAYER 2: The Materialistic Agent ---
def piece_picker_bot(board):
    """
    Evaluates every legal move. If a move captures a piece, 
    it scores it based on standard chess values (Queen=9, Rook=5, etc.).
    Chooses the highest-scoring move, or defaults to random.
    """
    # Standard piece values for evaluating captures
    values = {
        chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, 
        chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
    }
    
    legal_moves = list(board.legal_moves)
    best_move = None
    best_score = -1

    for move in legal_moves:
        score = 0
        # Check if the move is a capture
        if board.is_capture(move):
            # Find out what piece sits on the target square
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score = values.get(captured_piece.piece_type, 0)
        
        # Keep track of the highest scoring capture
        if score > best_score:
            best_score = score
            best_move = move

    # If no captures are available (score is 0), just pick a random move
    return best_move if best_score > 0 else random.choice(legal_moves)

# --- THE GAME ENGINE LOOP ---
def play_game():
    # Initialize a fresh chess board array state
    board = chess.Board()
    turn_count = 1

    print("♟️ Chess Simulation Initiated. White (Random) vs. Black (Piece Picker) ♟️\n")

    # Keep looping until the python-chess engine declares the game over
    while not board.is_game_over():
        print(f"--- Turn {turn_count} ---")
        
        if board.turn == chess.WHITE:
            # White's Turn: Call Bot 1
            chosen_move = piece_picker_bot(board)
            print(f"White (Random) plays: {board.san(chosen_move)}")
        else:
            # Black's Turn: Call Bot 2
            chosen_move = piece_picker_bot(board)
            print(f"Black (Piece Picker) plays: {board.san(chosen_move)}")

        # Execute the move on the board
        board.push(chosen_move)
        
        # Print the current ascii layout of the board to the terminal
        print(board)
        print("\n")
        
        turn_count += 1
        time.sleep(0.5) # Pause for half a second so you can watch the loop play out

    # Determine the final result once the loop exits
    print("🏁 GAME OVER 🏁")
    print(f"Reason: {board.outcome().termination.name}")
    print(f"Result: {board.result()}")

if __name__ == "__main__":
    play_game()