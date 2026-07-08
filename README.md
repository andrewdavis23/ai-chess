# The Project Goal
Learn how to connect to LLM API. Feed the state of a machine into the API and use the response to control that machine.

# Project Description
Using the python chess module, create a chess game that can be played in the terminal. Choose two players from a list of players which includes:
- the user
- simple bots created in python
- LLMs
Any two of these types of players can play chess. The user can either participate or observe.

# Files
## EX_terminal_menu.py
This is the framework for making a menu in terminal. The project uses a more developed version of this.
## keys.json
Contains the API keys for Gemini, Grok, and ChatGPT. The project (main.py) will look for this file in the directory where main.py is located.
## main.py
This is the project.

# Notes
- FEN = Forsyth–Edwards Notation = text format for a chess board used to prompt LLM
- UCI = Universal Chess Notation = four character string describing a move. Response format for LLM and user input.
- Was expecting the major pitfall to be the output of the LLM to be in the incorrect format. This wasn't a problem, but if it was I would use Pydantic to control the response format.
- The actual problems:
  - Gemini allows only 20 responses per project per day
  - Firewall blocks the connections to Grok AI
  - OpenAI has not been tested yet
- Zombie Bot
  - I call it that because it moves around the board randomly unless it is able to capture a piece. In that case it would capture the most valuable piece.
  - I'm so bad at chess that I lost to it. In my defence, the board is not very easy to read.
- The chess module prints out the board using "." for the empty squares and letters for the pieces. So, I wrote a function that turns the pieces into emojis.   

# To-do
- Currently white is always on bottom. If human player is black, flip the board. Built into module?
