from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List

from app.game_logic import TicTacToeBoard
from app.nlp_utils import apply_move_from_text
from app.stt import transcribe_filelike, STTError, DEFAULT_STT_MODEL, DEFAULT_PROMPT

app = FastAPI(title="Tic-Tac-Toe LLM + STT")

# ===== CORS (dev) =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # w produkcji zawęź do zaufanych originów
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Stan gry =====
board = TicTacToeBoard()

# ===== Schemas =====
class MoveResponse(BaseModel):
    success: bool
    message: str
    board: List[List[Optional[str]]]
    board_display: str
    winner: Optional[str] = None
    is_full: bool = False
    move: Optional[Dict[str, Any]] = None

class TextCommand(BaseModel):
    text: str = Field(
        ...,
        description="Write a command to play a move, e.g., 'X plays at row 1, column 2'"
    )
    model: Optional[str] = Field("gpt-4o-mini", description="OpenAI model to use for parsing")
    temperature: float = Field(0.2, ge=0.0, le=1.0, description="Temperature for LLM")

class ParsedMove(BaseModel):
    player: Literal["X", "O"]
    row: int
    col: int


# ===== Podgląd stanu (debug) =====
@app.get("/state", response_model=MoveResponse)
def get_board_state():
    winner = board.check_winner()
    return MoveResponse(
        success=True,
        message="Current board state.",
        board=board.get_state(),
        board_display=board.get_display(),
        winner=winner,
        is_full=board.is_full(),
    )


# ===== LLM flow: tekst -> walidacja -> ruch =====
@app.post("/move_from_text", response_model=MoveResponse)
def move_from_text(cmd: TextCommand):
    """
    1) LLM parsuje
    2) Walidujemy względem planszy
    3) Jeśli legalny — wykonujemy i zwracamy stan gry
    """
    try:
        result = apply_move_from_text(
            board=board,
            text=cmd.text,
            model=cmd.model or "gpt-4o-mini",
            temperature=cmd.temperature,
        )
        # result to słownik zgodny z MoveResponse (+ move)
        return MoveResponse(**result)
    except ValueError as e:
        # gdy llm_parse_move zwróci niepoprawne dane itp.
        raise HTTPException(status_code=400, detail=str(e))  
    

# ===== Reset gry =====    
@app.post("/reset")
def reset_board():
    board.reset()
    return {"message": "Board reset."}


# ---------- Audio: transkrypcja ----------
class STTResponse(BaseModel):
    transcript: str
    model: str

ALLOWED_AUDIO_MIME = {
    "audio/mpeg", "audio/mp3",
    "audio/wav", "audio/x-wav",
    "audio/webm",
    "audio/mp4", "audio/m4a",
    "audio/aac", "audio/ogg",
    "application/octet-stream",  # niektóre przeglądarki
}

@app.post("/stt/transcribe", response_model=STTResponse)
async def stt_transcribe(
    file: UploadFile = File(..., description="Plik audio z poleceniem ruchu"),
    model: str = DEFAULT_STT_MODEL,
    prompt: Optional[str] = DEFAULT_PROMPT,
):
    if file.content_type not in ALLOWED_AUDIO_MIME:
        raise HTTPException(
            status_code=400,
            detail=f"Nieobsługiwany typ pliku: {file.content_type}. Wgraj mp3/m4a/wav/webm.",
        )
    try:
        transcript = transcribe_filelike(
            file_obj=file.file,
            filename=file.filename or "audio_input",
            model=model,
            prompt=prompt,
        )
    except STTError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return STTResponse(transcript=transcript, model=model)

# ===== Minimalny debug UI =====
@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse("""
<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <title>Tic-Tac-Toe LLM + STT (Debug UI)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body{font-family:ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;max-width:920px;margin:32px auto;padding:0 16px}
    .row{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
    .col{flex:1 1 320px}
    textarea{width:100%;min-height:120px;padding:8px;font-size:16px}
    button{padding:10px 14px;border:1px solid #ddd;border-radius:10px;background:#f8f8f8;cursor:pointer}
    button:disabled{opacity:.5;cursor:not-allowed}
    #board{display:grid;grid-template-columns:repeat(3,80px);grid-template-rows:repeat(3,80px);gap:6px;margin-top:8px}
    .cell{display:flex;align-items:center;justify-content:center;border:1px solid #bbb;border-radius:10px;font-size:28px;height:80px;width:80px;background:#fff}
    .status{margin:8px 0 16px;padding:8px 12px;background:#f5f5f5;border-radius:10px;border:1px solid #e5e5e5}
    .log{margin-top:16px;font-size:14px;line-height:1.4}
    .log p{margin:6px 0}
    .flex{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
  </style>
</head>
<body>
  <h1>🎮 Tic-Tac-Toe — LLM + STT</h1>
  <div class="status" id="status"></div>

  <div class="row">
    <div class="col">
      <div><strong>Plansza</strong></div>
      <div id="board"></div>
    </div>
    <div class="col">
      <div><strong>Polecenie</strong></div>
      <textarea id="cmd" placeholder="Np.: 'krzyżyk lewy górny róg' albo 'O środek'"></textarea>
      <div class="flex" style="margin-top:8px">
        <input type="file" id="audio" accept="audio/*">
        <button id="btnTranscribe">Transkrybuj z audio</button>
        <button id="btnMove">Zagraj ruch</button>
        <button id="btnReset">Reset</button>
      </div>
      <div class="log" id="log"></div>
    </div>
  </div>

<script>
const boardEl = document.getElementById('board');
const statusEl = document.getElementById('status');
const cmdEl = document.getElementById('cmd');
const audioEl = document.getElementById('audio');
const btnTranscribe = document.getElementById('btnTranscribe');
const btnMove = document.getElementById('btnMove');
const btnReset = document.getElementById('btnReset');
const logEl = document.getElementById('log');

let state = {
  board: [[null,null,null],[null,null,null],[null,null,null]],
  next_player: "X",
  game_over: false,
  winner: null
};

function renderBoard(){
  boardEl.innerHTML = '';
  for(let r=0;r<3;r++){
    for(let c=0;c<3;c++){
      const cell = document.createElement('div');
      cell.className = 'cell';
      const v = state.board?.[r]?.[c];
      cell.textContent = v ? v : '';
      boardEl.appendChild(cell);
    }
  }
}

function setStatus(msg){ statusEl.textContent = msg; }
function pushLog(type, text){
  const p = document.createElement('p');
  p.textContent = (type === 'error' ? '❌ ' : 'ℹ️ ') + text;
  logEl.prepend(p);
}

function updateFromResponse(resp){
  state.board = resp.board ?? state.board;
  state.winner = resp.winner ?? null;
  state.game_over = !!resp.game_over;
  state.next_player = resp.next_player ?? state.next_player;
  renderBoard();

  if (state.game_over) {
    if (state.winner) setStatus(`Koniec gry — wygrał ${state.winner}`);
    else setStatus(`Koniec gry — remis`);
    btnMove.disabled = true;
  } else {
    setStatus(''); // <--- usuń komunikat o turze
    btnMove.disabled = false;
  }
}

async function postJSON(url, data){
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(data)
  });
  const body = await res.json().catch(()=> ({}));
  if(!res.ok){ throw new Error(body?.detail || res.statusText || 'Błąd żądania'); }
  return body;
}

btnTranscribe.addEventListener('click', async () => {
  const f = audioEl.files?.[0];
  if(!f){ pushLog('error','Wybierz plik audio.'); return; }
  btnTranscribe.disabled = true;
  setStatus('Transkrybuję audio…');
  try {
    const fd = new FormData();
    fd.append('file', f, f.name);
    const res = await fetch('/stt/transcribe', { method:'POST', body: fd });
    const data = await res.json();
    if(!res.ok){ throw new Error(data?.detail || 'Błąd transkrypcji'); }
    cmdEl.value = data.transcript || '';
    pushLog('info','Transkrypcja gotowa. Możesz edytować tekst i kliknąć „Zagraj ruch”.');
    setStatus('Transkrypcja wstawiona do pola.');
  } catch (e){
    pushLog('error', e.message || String(e));
    setStatus('Błąd transkrypcji');
  } finally {
    btnTranscribe.disabled = false;
  }
});

btnMove.addEventListener('click', async () => {
  const text = (cmdEl.value || '').trim();
  if(!text){ pushLog('error','Polecenie jest puste.'); return; }
  btnMove.disabled = true;
  setStatus('Wykonuję ruch…');
  try {
    const data = await postJSON('/move_from_text', { text });
    updateFromResponse(data);
    pushLog(data.success ? 'info' : 'error', data.message || 'Brak wiadomości');
  } catch (e){
    pushLog('error', e.message || String(e));
    setStatus('Błąd wykonania ruchu');
  } finally {
    if(!state.game_over){ btnMove.disabled = false; }
  }
});

btnReset.addEventListener('click', async () => {
  btnMove.disabled = true;
  try {
    const res = await fetch('/reset', {method:'POST'});
    const data = await res.json();
    state.board = data.board;
    state.next_player = data.next_player;
    state.game_over = data.game_over;
    state.winner = null;
    renderBoard();
    setStatus(''); // zamiast setStatus(`Plansza zresetowana. Tura: ${state.next_player}`);
    logEl.innerHTML = ''; // czyści logi
    pushLog('info','Reset gry.');
    cmdEl.value = '';
  } catch (e){
    pushLog('error','Błąd resetu');
  } finally {
    btnMove.disabled = false;
  }
});

// Inicjalny render
renderBoard();
setStatus();
</script>
</body>
</html>
    """)
