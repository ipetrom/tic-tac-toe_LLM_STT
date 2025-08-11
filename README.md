# Voice‑Controlled Tic‑Tac‑Toe (LLM + STT) 🎮

An educational project built as a springboard for a future commercial deployment with a similar concept and tech stack.

<p align="left">
  <a href="https://www.python.org/"><img alt="Python" src="https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white"></a>
  <a href="https://streamlit.io/"><img alt="Streamlit" src="https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white"></a>
  <a href="https://platform.openai.com/"><img alt="OpenAI API" src="https://img.shields.io/badge/OpenAI%20API-enabled-412991?logo=openai&logoColor=white"></a>
</p>

> [!NOTE]
> The final, most complete implementation lives in the `final-version` branch.  
> Example progression: `base-version` → `second-version` → `final-version`.

---

## Table of Contents
- Overview
- Highlights
- What’s Included
- How It Works (Flow)
- Repository Branches
- Demo
- Tech Stack
- Final Notes

---

## Overview
An interactive Tic‑Tac‑Toe game controlled by voice commands:
- Commands are transcribed to text by an STT model.
- The LLM interprets the transcribed text into a move intent.
- Game logic validates and executes the move, returning the current game status.

> [!TIP]
> You can edit the transcribed text before confirming the move.

---

## Highlights ✨
- Voice input first: talk to place X/O.
- Clear separation of concerns: STT → LLM → Game Logic.
- Two simple fronts:
  - Streamlit for quick iteration.
  - Lightweight HTML/JS for clicking and board preview.
- Easy to swap models (Whisper/gpt‑4o‑mini‑transcribe, GPT‑4o‑mini).

---

## What’s Included
- Game logic (board, win conditions, draw, occupied cells).
- LLM integration to interpret text commands.
- Endpoint testing via FastAPI.
- A simple Streamlit app for entering commands and playing.
- Speech‑to‑text (Whisper / gpt‑4o‑mini‑transcribe).
- Full pipeline wiring: STT → LLM → game logic.
- Final tests.
- A lightweight HTML/JS front for quick clicking and board preview.

---

## How It Works (Flow) ⚙️

1) The user records or uploads an audio file with a command (e.g., “X top‑left corner”).  
2) The STT model transcribes the audio and fills the text field.  
3) The user can optionally edit the text and confirm.  
4) The LLM parses the command into a move (position, symbol).  
5) The game logic validates and applies the move, then returns the status:
   - cell occupied,
   - win,
   - draw,
   - continue.  
6) A board reset is available to start a new game.

```mermaid
flowchart LR
    A[User Audio Command] --> B[STT: Whisper / gpt-4o-mini-transcribe]
    B --> C[Transcribed Text]
    C --> D[LLM: GPT-4o-mini]
    D --> E[Parsed Move (symbol, position)]
    E --> F[Game Logic]
    F --> G{Status}
    G -->|win/draw/continue| H[UI: Streamlit / HTML+JS]
    H --> I[Reset Board (optional)]
```

---

## Repository Branches
- `base-version` – initial, minimal pipeline.
- `second-version` – expanded logic and integration.
- `final-version` – polished features and tests.

> [!IMPORTANT]
> Work against `final-version` for the most up‑to‑date code and examples.

---

## Demo
Add a link here to a short screen recording that shows the app in action.

- Suggested: a 30–60s clip showing voice input → transcription → move → status.

---

## Tech Stack
- Python
- FastAPI
- OpenAI API
- GPT‑4o‑mini (LLM)
- Whisper / gpt‑4o‑mini‑transcribe (STT)
- Streamlit
- HTML + JavaScript

---

## Final Notes
The code and architecture are optimized for fast iteration: simple endpoints, clear logic, and a lightweight front for testing. This makes it easy to port the solution into a larger project or swap components (e.g., STT/LLM models) without changing the rest of the flow.