#!/usr/bin/env python3
"""Ghost Teleprompter — faixa portátil (Linux, Windows, macOS).

No macOS o binário Swift (`./build.sh`) continua sendo o caminho nativo,
com exclusão de captura via NSWindow.sharingType. Este arquivo é o app
que roda onde não há AppKit: Windows (some da captura com
SetWindowDisplayAffinity) e Linux (faixa por cima; a exclusão de captura
não é API padrão do desktop).
"""
from __future__ import annotations

import sys

from scriptfmt import format_sentences, load_script

WINDOW_W = 560
WINDOW_H = 95
DEFAULT_SPEED = 0.4
DEFAULT_FONT = 22


def run_check() -> int:
    formatted = format_sentences("Olá. Mundo!")
    if formatted != "Olá.\nMundo!":
        print("check failed:", repr(formatted), file=sys.stderr)
        return 1
    script = load_script(None)
    if not script.strip():
        print("check failed: empty default script", file=sys.stderr)
        return 1
    print("check ok")
    print(formatted)
    return 0


def run_app() -> None:
    import tkinter as tk
    from tkinter import font as tkfont

    if sys.platform == "darwin":
        family = "Helvetica Neue"
    elif sys.platform == "win32":
        family = "Segoe UI"
    else:
        family = "DejaVu Sans"

    raw_text = load_script(None)
    speed = DEFAULT_SPEED
    font_size = DEFAULT_FONT
    playing = True
    offset = 0.0
    last_clip = ""
    last_clip_seq: int | None = None
    protected = False

    root = tk.Tk()
    root.title("Ghost Teleprompter")
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    try:
        root.attributes("-alpha", 0.92)
    except tk.TclError:
        pass
    try:
        if sys.platform == "win32":
            root.attributes("-toolwindow", True)
    except tk.TclError:
        pass

    sw = root.winfo_screenwidth()
    x = max(0, (sw - WINDOW_W) // 2)
    root.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+8")
    root.configure(bg="#111111")

    canvas = tk.Canvas(
        root,
        width=WINDOW_W,
        height=WINDOW_H,
        bg="#111111",
        highlightthickness=0,
        bd=0,
    )
    canvas.pack(fill="both", expand=True)

    text_font = tkfont.Font(family=family, size=font_size, weight="bold")
    pad = WINDOW_H * 0.45
    inner_w = WINDOW_W - 28
    text_id = canvas.create_text(
        WINDOW_W / 2,
        pad,
        text=raw_text,
        fill="white",
        font=text_font,
        width=inner_w,
        anchor="n",
        justify="center",
    )

    drag = {"x": 0, "y": 0}

    def start_drag(event: tk.Event) -> None:
        drag["x"] = event.x_root - root.winfo_x()
        drag["y"] = event.y_root - root.winfo_y()

    def on_drag(event: tk.Event) -> None:
        root.geometry(f"+{event.x_root - drag['x']}+{event.y_root - drag['y']}")

    canvas.bind("<ButtonPress-1>", start_drag)
    canvas.bind("<B1-Motion>", on_drag)

    def max_offset() -> float:
        bbox = canvas.bbox(text_id)
        if not bbox:
            return 0.0
        text_h = bbox[3] - bbox[1]
        return max(0.0, text_h + pad * 2 - WINDOW_H)

    def place_text() -> None:
        canvas.coords(text_id, WINDOW_W / 2, pad - offset)

    def apply_text(reset_scroll: bool) -> None:
        nonlocal offset
        canvas.itemconfigure(text_id, text=raw_text, font=text_font)
        canvas.update_idletasks()
        if reset_scroll:
            offset = 0.0
        else:
            offset = min(offset, max_offset())
        place_text()

    def tick() -> None:
        nonlocal playing, offset, protected
        if not protected:
            _exclude_from_capture(root)
            protected = True
        if playing:
            cap = max_offset()
            if cap > 0:
                offset = min(offset + speed, cap)
                if offset >= cap - 0.01:
                    playing = False
                place_text()
        root.after(16, tick)

    def watch_clip() -> None:
        nonlocal raw_text, playing, last_clip, last_clip_seq
        seq = _clipboard_sequence()
        text = _clipboard_text(root)
        changed = False
        if seq is not None:
            if last_clip_seq is None:
                last_clip_seq = seq
            elif seq != last_clip_seq:
                last_clip_seq = seq
                changed = True
        elif text != last_clip:
            changed = True
        last_clip = text
        if changed and text.strip():
            raw_text = format_sentences(text)
            apply_text(reset_scroll=True)
            playing = True
        root.after(500, watch_clip)

    def set_speed(value: float) -> None:
        nonlocal speed
        speed = min(8.0, max(0.1, value))

    def change_font(delta: int) -> None:
        nonlocal font_size, offset
        span = max(1.0, max_offset())
        frac = offset / span
        font_size = min(80, max(14, font_size + delta))
        text_font.configure(size=font_size)
        apply_text(reset_scroll=False)
        offset = frac * max_offset()
        place_text()

    def handle_key(event: tk.Event) -> str | None:
        nonlocal playing, raw_text
        key = event.keysym
        char = event.char or ""
        if key in ("space",):
            playing = not playing
        elif key in ("Up",):
            set_speed(speed + 0.2)
        elif key in ("Down",):
            set_speed(speed - 0.2)
        elif key in ("Left", "Prior"):
            offset_reset()
        elif key in ("Right", "Next"):
            jump_end()
        elif key in ("plus", "equal") or char in "+=":
            change_font(2)
        elif key in ("minus", "underscore") or char in "-_":
            change_font(-2)
        elif char.lower() == "r":
            offset_reset()
            playing = True
        elif char.lower() == "v":
            raw_text = load_script(_clipboard_text(root))
            apply_text(reset_scroll=True)
            playing = True
        elif char == "0":
            set_speed(DEFAULT_SPEED)
        elif char.lower() == "q":
            root.destroy()
            return "break"
        else:
            return None
        return "break"

    def offset_reset() -> None:
        nonlocal offset
        offset = 0.0
        place_text()

    def jump_end() -> None:
        nonlocal offset, playing
        offset = max_offset()
        playing = False
        place_text()

    def boot_script() -> None:
        nonlocal raw_text
        clip = _clipboard_text(root)
        if clip.strip():
            raw_text = load_script(clip)
            apply_text(reset_scroll=True)

    root.bind("<Key>", handle_key)
    canvas.bind("<Key>", handle_key)
    root.after(0, lambda: (root.focus_force(), canvas.focus_set()))
    last_clip = _clipboard_text(root)
    last_clip_seq = _clipboard_sequence()
    apply_text(reset_scroll=True)
    boot_script()
    tick()
    watch_clip()
    root.mainloop()


def _clipboard_text(root) -> str:
    import tkinter as tk

    try:
        return root.clipboard_get()
    except tk.TclError:
        return ""


def _clipboard_sequence() -> int | None:
    if sys.platform != "win32":
        return None
    import ctypes

    try:
        return int(ctypes.windll.user32.GetClipboardSequenceNumber())
    except Exception:
        return None


def _exclude_from_capture(root) -> None:
    if sys.platform != "win32":
        return
    import ctypes

    root.update_idletasks()
    user32 = ctypes.windll.user32
    hwnd = int(root.winfo_id())
    ancestor = user32.GetAncestor(hwnd, 2)  # GA_ROOT
    if ancestor:
        hwnd = ancestor
    WDA_EXCLUDEFROMCAPTURE = 0x00000011
    if user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE) == 0:
        parent = user32.GetParent(int(root.winfo_id()))
        if parent:
            user32.SetWindowDisplayAffinity(parent, WDA_EXCLUDEFROMCAPTURE)


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(run_check())
    try:
        run_app()
    except ModuleNotFoundError as exc:
        if exc.name != "tkinter":
            raise
        print(
            "Este app precisa do Tk (janela gráfica).\n"
            "  Debian/Ubuntu:  sudo apt install python3-tk\n"
            "  Fedora:         sudo dnf install python3-tkinter\n"
            "  Windows:        instale Python em python.org e marque tcl/tk\n"
            "VPS sem desktop:  python3 teleprompter.py --check",
            file=sys.stderr,
        )
        sys.exit(1)
