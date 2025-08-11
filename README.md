# Voice-Controlled Tic-Tac-Toe (LLM + STT) 🎮

An educational project built as a springboard for a future commercial deployment with a similar concept and tech stack.

## Repository Branches

This repo contains three branches representing implementation stages. The final version lives in: `final-version`.

Example progression: `base-version` → `second-version` → `final-version`.

## Concept 💡

An interactive Tic-Tac-Toe game controlled by voice commands. User commands are:

- transcribed to text by an STT model,
- interpreted by an LLM,
- validated and executed by the game logic.

## What’s Included

- game logic (board, win conditions, draw, occupied cells),
- LLM integration to interpret text commands,
- endpoint testing via FastAPI,
- a simple Streamlit app for entering commands and playing,
- speech-to-text (Whisper / `gpt-4o-mini-transcribe`),
- full pipeline wiring: STT → LLM → game logic,
- final tests,
- a lightweight HTML/JS front for quick clicking and board preview.

## How It Works (Flow) ⚙️

1. The user records or uploads an audio file with a command (e.g., “X top-left corner”).
2. The STT model transcribes the audio and fills the text field.
3. The user can optionally edit the text and confirm.
4. The LLM parses the command into a move (position, symbol).
5. The game logic validates and applies the move, then returns the status:
   - cell occupied,
   - win,
   - draw,
   - continue.
6. A board reset is available to start a new game.

## Demo

Add a link here to a short screen recording that shows the app in action.

## Tech Stack

- Python
- FastAPI
- OpenAI API
- GPT-4o-mini (LLM)
- Whisper / `gpt-4o-mini-transcribe` (STT)
- Streamlit
- HTML + JavaScript

## Final Notes

The code and architecture are optimized for fast iteration: simple endpoints, clear logic, and a lightweight front for testing. This makes it easy to port the solution into a larger project or swap components (e.g., STT/LLM models) without changing the rest of the flow.
