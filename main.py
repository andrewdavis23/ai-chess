import time
import random
import chess
import os
import json
from google import genai
from google.genai import types

white_player = "_"*10
black_player = "_"*10
wait_time = 0.6
emojis = True

def load_api_keys():
    """Loads all API keys from a local JSON file into a Python dictionary."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "keys.json")
    
    with open(file_path, "r") as file:
        keys = json.load(file)
    
    return keys

# PLAYER 1: Random Legal Move
def random_bot(board):
    """Selects a completely random move from all legal options."""
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves)

# PLAYER 2: Most Valuable Piece or Random
def zombie_bot(board):
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

# PLAYER 3: User
def human_player(board):
    """Prompts user for a 4-character UCI move string and validates it."""
    while True:
        try:
            user_input = input("> ").strip().lower()

            move = chess.Move.from_uci(user_input)

            if move in board.legal_moves:
                return move
            else:
                print("Illegal move. Try again.")
        except ValueError:
            print("Invalid format. Example: e2e4")

# PLAYER 4: GEMINI
class GeminiPlayer:
    def __init__(self, api_key, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key)

    def get_move(self, board):        
        board_fen = board.fen()
        legal_moves_list = [move.uci() for move in board.legal_moves]
        player_color = "White" if board.turn == chess.WHITE else "Black"

        prompt = f"""
        You are an expert chess engine playing as {player_color}.
        Current board position (FEN format): {board_fen}
        Your available legal moves are: {legal_moves_list}
        
        Select the single best strategic move from your legal moves list.

        Your return prompt should be your chosen four-character UCI code from the list of legal moves.
        Do not, at any point, return anything other than the UCI code.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    # Bypass complex dictionaries; pass the native string class directly
                    response_mime_type="application/json",
                    response_schema=str, 
                    temperature=0.1,
                ),
            )
            
            # Clean up any unexpected outer quotes or spaces from the JSON format
            move_string = json.loads(response.text).strip().lower()
            return chess.Move.from_uci(move_string)
            
        except Exception as e:
            print(f"Error: {e}\nRaw Response: {response.text}")

def display_menu():
    """Let's user select the player types and wait time between moves."""
    menu_width = 30
    menu_lines = [
        "#" + "-"*menu_width + "#",
        f"|  1 - white = {white_player}".ljust(menu_width+1) +"|",
        f"|  2 - black = {black_player}".ljust(menu_width+1) +"|",
        f"|  3 - wait time = {wait_time} sec".ljust(menu_width+1) + "|",
        f"|  4 - piece emojis = {emojis}".ljust(menu_width+1) + "|",
        f"|  5 - play game".ljust(menu_width+1) +"|",
        f"|  0 - exit".ljust(menu_width+1) +"|",
        "#" + "-"*menu_width + "#",
        "Selection: "
    ]

    return "\n".join(menu_lines)

def print_emoji_board(board: chess.Board):
    """Renders the chess board using full-color graphic emojis and coordinates."""
    # Map python-chess internal tokens to standard graphic emojis
    emoji_map = {
        'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙', # White
        'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟', # Black
        '.': '·'                                                     # Empty Square
    }

    move_from = None
    move_to = None

    if board.move_stack:
        move_from = board.peek().from_square
        move_to = board.peek().to_square
    
    print("   a  b  c  d  e  f  g  h")
    print(" ┌────────────────────────┐")
    
    # Loop backwards from rank 8 down to rank 1
    for rank in range(8, 0, -1):
        row_string = f"{rank}│"
        for file in range(1, 9):
            # Get the piece object at the current target square index
            square = chess.square(file - 1, rank - 1)
            piece = board.piece_at(square)
            
            # Map token or fall back to empty square symbol
            symbol = piece.symbol() if piece else '.'
            if square == move_from:
                buffer = "[]"
            elif square == move_to:
                buffer = "> "
            else:
                buffer = "  "

            row_string += f"{buffer[0]}{emoji_map[symbol]}{buffer[1]}"
            
        row_string += f"│{rank}"
        print(row_string)
        
    print(" └────────────────────────┘")
    print("   a  b  c  d  e  f  g  h\n")

# Maybe could adjust this to read the api key
def available_players():
    return "1 - Random Bot\n2 - Zombie Bot\n3 - me (you)\n4 - Gemini AI"

def choose_white_player():
    global white_player, keys
    print("\n--- Select White Player ---")
    print(available_players())
    choice = input("Selection: ")
    if choice == "1": white_player = "Random Bot"
    elif choice == "2": white_player = "Zombie Bot"
    elif choice == "3": white_player = "You"
    elif choice == "4": 
        if not keys.get("GEMINI_API_KEY"):
            print("Error: GEMINI not found in keys.json")
        else:
            white_player = "Gemini"
    
def choose_black_player():
    global black_player
    print("\n--- Select Black Player ---")
    print(available_players())
    choice = input("Selection: ")
    if choice == "1": black_player = "Random Bot"
    elif choice == "2": black_player = "Zombie Bot"
    elif choice == "3": black_player = "You"
    elif choice == "4": 
        if not keys.get("GEMINI_API_KEY"):
            print("Error: GEMINI not found in keys.json")
        else:
            black_player = "Gemini"

def choose_wait_time():
    global wait_time
    try:
        wait_time = float(input("Enter delay between turns (seconds): "))
    except ValueError:
        print("Invalid number.")

def choose_emojis():
    global emojis
    emojis = not emojis

def play_game():
    global keys
    observe = True # Are we observing bots or playing against one?
    if white_player == "You" or black_player == "You":
        observe = False
    if white_player == "none" or black_player == "none":
        print("\nError: Assign both players before starting.")
        return
    if white_player == "You" and black_player == "You":
        print("\nYou know, I was going to throw an error and say that you can't play against yourself, but whatever go ahead and try it.")
    gemini_instance = None
    if white_player == "Gemini" or black_player == "Gemini":
        gemini_instance = GeminiPlayer(api_key=keys.get("GEMINI_API_KEY"))
    
    print(f"\n Match Started: \u2659 {white_player} vs {black_player} \u265F")

    # Initialize a fresh chess board array state
    board = chess.Board()
    turn_count = 1

    if emojis:
        print_emoji_board(board)
    else:
        print(board)

    player_map = {
        "Random Bot": random_bot,
        "Zombie Bot": zombie_bot,
        "You": human_player,
        "Gemini": gemini_instance.get_move if gemini_instance else None
    }

    print(f"♟️ White ({white_player}) vs. Black ({black_player}) ♟️\n")

    # Keep looping until the python-chess engine declares the game over
    while not board.is_game_over():
        print(f"--- Turn {turn_count} ---")
        
        if board.turn == chess.WHITE:
            current_action = player_map.get(white_player)
            chosen_move = current_action(board)
            print(f"White ({white_player}) plays: {board.uci(chosen_move)}")
        else:
            current_action = player_map.get(black_player)
            chosen_move = current_action(board)
            print(f"Black ({black_player}) plays: {board.uci(chosen_move)}")

        # Execute the move on the board
        board.push(chosen_move)
        
        # Print the current ascii layout of the board to the terminal
        if emojis:
            print_emoji_board(board)
        else:
            print(board)
        
        turn_count += 1
        if observe:
            time.sleep(wait_time)

    # Determine the final result once the loop exits
    print("🏁 GAME OVER 🏁")
    print(f"Winner: {"White" if board.outcome().winner else "Black"}")
    print(f"Reason: {board.outcome().termination.name}")
    print(f"Result: {board.result()}")

menu_actions = {
    1: choose_white_player,
    2: choose_black_player,
    3: choose_wait_time,
    4: choose_emojis,
    5: play_game
}

try:
    keys = load_api_keys()
except FileNotFoundError:
    keys = {}

while True:
    try:
        x = int(input(display_menu()))
    except ValueError:
        print("Enter a number.")
        continue

    if x == 0:
        break
    
    action = menu_actions.get(x)
    if action:
        action()
    else:
        print("Invalid selection.")
