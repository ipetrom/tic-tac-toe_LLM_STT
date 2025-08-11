from __future__ import annotations

import io
from typing import BinaryIO, Optional

from openai import OpenAI, APIConnectionError, APIStatusError
from dotenv import load_dotenv

load_dotenv()  # wczyta OPENAI_API_KEY z .env, jeśli używasz

# Inicjalizacja klienta raz na moduł
_client = OpenAI()

DEFAULT_STT_MODEL = "gpt-4o-mini-transcribe"
DEFAULT_PROMPT = (
    "The audio is a Polish command related to playing Tic-Tac-Toe. "
    "Transcribe it in Polish, keeping game terms like 'krzyżyk', 'kółko', 'lewy górny róg', 'środek', etc."
)

class STTError(RuntimeError):
    """Błąd w trakcie transkrypcji (opakowanie wyjątków SDK)."""
    pass


def _call_stt(file_obj: BinaryIO, filename: str, prompt: Optional[str], model: str) -> str:
    """
    Niskopoziomowe wywołanie OpenAI STT. Zwraca czysty tekst transkrypcji.
    """
    try:
        resp = _client.audio.transcriptions.create(
            model=model,
            file=(filename, file_obj),  # zapewnia nazwę pliku w multipart form-data
            response_format="text",
            prompt=prompt or DEFAULT_PROMPT,
        )
    except (APIConnectionError, APIStatusError) as e:
        raise STTError(f"Transkrypcja nieudana (API): {e}") from e
    except Exception as e:
        raise STTError(f"Transkrypcja nieudana: {e}") from e

    # W zależności od wersji SDK odpowiedź bywa stringiem albo obiektem z polem `.text`
    if isinstance(resp, str):
        return resp.strip()
    text = getattr(resp, "text", None)
    if isinstance(text, str):
        return text.strip()

    # Fallback — jeśli format odpowiedzi się zmienił
    return str(resp).strip()


def transcribe_file(
    path: str,
    *,
    model: str = DEFAULT_STT_MODEL,
    prompt: Optional[str] = None,
) -> str:
    """
    Transkrybuje plik z dysku. Zwraca czysty tekst.
    """
    try:
        with open(path, "rb") as f:
            return _call_stt(f, filename=path.split("/")[-1], prompt=prompt, model=model)
    except FileNotFoundError as e:
        raise STTError(f"Plik nie istnieje: {path}") from e


def transcribe_filelike(
    file_obj: BinaryIO,
    filename: str,
    *,
    model: str = DEFAULT_STT_MODEL,
    prompt: Optional[str] = None,
) -> str:
    """
    Transkrybuje dowolny strumień pliku (np. UploadFile.file w FastAPI). Zwraca czysty tekst.
    """
    # Upewnij się, że wskaźnik jest na początku
    try:
        if hasattr(file_obj, "seek"):
            file_obj.seek(0)
    except Exception:
        # w razie braku seek — skopiuj do bufora
        file_bytes = file_obj.read()
        file_obj = io.BytesIO(file_bytes)

    return _call_stt(file_obj, filename=filename, prompt=prompt, model=model)
