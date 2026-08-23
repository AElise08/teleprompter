"""Formatação do roteiro — sem GUI, dá pra testar em qualquer SO (inclusive VPS)."""
from __future__ import annotations

import re
from pathlib import Path

DEFAULT_TEXT = """
Copie o seu roteiro (Ctrl+C ou Cmd+C) e a faixa atualiza sozinha.
Esta faixa fica embaixo da câmera. No Mac e no Windows ela some da gravação de tela.
Espaço pausa. Setas mudam a velocidade. Mais e menos mudam o tamanho. V recarrega do que você copiou. R recomeça. Q fecha.
""".strip()

_SENTENCE_BREAK = re.compile(r'([.!?…]+["\')\]]?)\s+')


def format_sentences(raw: str) -> str:
    collapsed = re.sub(r"\s+", " ", raw).strip()
    return _SENTENCE_BREAK.sub(r"\1\n", collapsed)


def script_file_path() -> Path:
    return Path.home() / "teleprompter" / "script.txt"


def load_script(clipboard: str | None) -> str:
    if clipboard and clipboard.strip():
        return format_sentences(clipboard)
    path = script_file_path()
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    if text.strip():
        return format_sentences(text)
    return DEFAULT_TEXT
