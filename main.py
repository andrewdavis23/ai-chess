import time
import random
import chess
import os
import json
from openai import OpenAI 

PLAYER_NONE = "_"*10
white_player = PLAYER_NONE
black_player = PLAYER_NONE
wait_time = 0.6
emojis = True

def load_api_keys():
    """Loads all API keys from a local JSON file into a Python dictionary."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "keys.json")
    
    with open(file_path, "r") as file:
        keys = json.load(file)
    
    return keys

def random_bot(board):
    """Selects a completely random move from all legal options."""
    legal_moves = list(board.legal_moves)
    return random.choice(legal_moves)

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

class LLMplayer:
    def __init__(self, provider_name, api_key):
        self.provider_name = provider_name
        self.api_key = api_key

        if provider_name == "Gemini":
            self.base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"
            self.model_name = "gemini-2.5-flash"
        elif provider_name == "Grok":
            self.base_url = "https://api.x.ai/v1"
            self.model_name = "grok-2-latest"
        elif provider_name == "OpenAI":
            self.base_url = "https://api.openai.com/v1"
            self.model_name = "gpt-4o-mini"
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def get_move(self, board):
        """Prompts LLM using Forsyth–Edwards Notation (FEN). Response is in Universal Chess Notation (UCI) format."""       
        board_fen = board.fen()
        legal_moves_list = [move.uci() for move in board.legal_moves]
        player_color = "White" if board.turn == chess.WHITE else "Black"
        move_string = "NO RESPONSE GIVEN"

        prompt = f"""
            You are an expert chess engine playing as {player_color}.
            Current board position (FEN format): {board_fen}
            Your available legal moves are: {legal_moves_list}
            
            Your return prompt should be your chosen four-character UCI code from the list of legal moves.
            Do not, at any point, return anything other than the UCI code.
            """

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )

            # clean response text
            move_string = json.loads(response.text).strip().lower()
            return chess.Move.from_uci(move_string)
        
        except Exception as e:
            print(f"{self.provider_name} responded with {move_string} causing error: {e}. Playing move from zombie bot.")
            return zombie_bot(board)

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

def choose_player(color_label: str):
    """Unified selection menu to set either the White or Black player type."""
    global white_player, black_player, keys
    
    print(f"\n--- Select {color_label} Player ---")
    print("1 - Random Bot\n2 - Zombie Bot\n3 - me (you)\n4 - Gemini AI\n5 - Grok\n6 - OpenAI")
    choice = input("Selection: ")
    
    # Determine which runtime variable string we are modifying
    selection_map = {"1": "Random Bot", "2": "Zombie Bot", "3": "You", "4": "Gemini", "5": "Grok", "6": "OpenAI"}
    player_type = selection_map.get(choice, PLAYER_NONE)
        
    if choice in ("4","5","6"):
        if f"{player_type.upper()}_API_KEY" not in keys:
            print(f"Error: {player_type.upper()}_API_KEY not found in keys.json. Selection cleared.")
            print(keys)
            player_type = PLAYER_NONE

    if color_label.lower() == "white":
        white_player = player_type
    else:
        black_player = player_type

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

    if white_player == PLAYER_NONE or black_player == PLAYER_NONE:
        print("\nError: Assign both players before starting.")
        return
        
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
    }

    for player in [white_player, black_player]:
        if player in ["Gemini", "Grok", "OpenAI"]:
            key_name = f"{player.upper()}_API_KEY"
            # Instantiate the class right here
            ai_instance = LLMplayer(provider_name=player, api_key=keys.get(key_name))
            # Map the player string directly to the function that returns a move
            player_map[player] = ai_instance.get_move

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
        
        time.sleep(wait_time)
        turn_count += 1

    # Determine the final result once the loop exits
    print("🏁 GAME OVER 🏁")
    print(f"Winner: {"White" if board.outcome().winner else "Black"}")
    print(f"Reason: {board.outcome().termination.name}")
    print(f"Result: {board.result()}")

menu_actions = {
    1: lambda: choose_player("White"),
    2: lambda: choose_player("Black"),
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
