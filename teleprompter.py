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


def run_windows_smoke() -> int:
    """Abre uma janela real e confirma que o Windows aceitou a proteção."""
    if sys.platform != "win32":
        print("windows smoke skipped: not Windows")
        return 0

    import tkinter as tk

    root = tk.Tk()
    try:
        root.title("Ghost Teleprompter")
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0.92)
        root.geometry("560x95+20+20")
        root.update()
        root.geometry("720x140+20+20")
        root.update()
        if root.winfo_width() != 720 or root.winfo_height() != 140:
            print("windows smoke failed: window did not resize", file=sys.stderr)
            return 1
        if not _exclude_from_capture(root):
            print("windows smoke failed: capture protection was rejected", file=sys.stderr)
            return 1
        print("windows gui and capture protection ok")
        return 0
    finally:
        root.destroy()


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

    grip_ids = [
        canvas.create_line(0, 0, 0, 0, fill="#777777", width=2),
        canvas.create_line(0, 0, 0, 0, fill="#777777", width=2),
        canvas.create_line(0, 0, 0, 0, fill="#777777", width=2),
    ]

    root.minsize(360, 72)
    root.maxsize(1000, 300)
    drag = {
        "mode": "idle",
        "x": 0,
        "y": 0,
        "w": WINDOW_W,
        "h": WINDOW_H,
        "resume": False,
    }

    def start_drag(event: tk.Event) -> None:
        nonlocal playing
        if event.x >= canvas.winfo_width() - 24 and event.y >= canvas.winfo_height() - 24:
            drag["mode"] = "resize"
            drag["x"] = event.x_root
            drag["y"] = event.y_root
            drag["w"] = root.winfo_width()
            drag["h"] = root.winfo_height()
            drag["resume"] = playing
            playing = False
            return
        drag["mode"] = "move"
        drag["x"] = event.x_root - root.winfo_x()
        drag["y"] = event.y_root - root.winfo_y()

    def on_drag(event: tk.Event) -> None:
        if drag["mode"] == "resize":
            width = min(1000, max(360, drag["w"] + event.x_root - drag["x"]))
            height = min(300, max(72, drag["h"] + event.y_root - drag["y"]))
            root.geometry(f"{width}x{height}+{root.winfo_x()}+{root.winfo_y()}")
            return
        if drag["mode"] == "move":
            root.geometry(f"+{event.x_root - drag['x']}+{event.y_root - drag['y']}")

    def max_offset() -> float:
        bbox = canvas.bbox(text_id)
        if not bbox:
            return 0.0
        text_h = bbox[3] - bbox[1]
        return max(0.0, text_h + pad * 2 - max(1, canvas.winfo_height()))

    def place_text() -> None:
        canvas.coords(text_id, canvas.winfo_width() / 2, pad - offset)

    def update_layout(width: int, height: int, reflow: bool) -> None:
        nonlocal pad, offset
        width = max(1, width)
        height = max(1, height)
        for index, grip_id in enumerate(grip_ids):
            inset = 5 + index * 5
            canvas.coords(grip_id, width - inset, height - 3, width - 3, height - inset)
        for grip_id in grip_ids:
            canvas.tag_raise(grip_id)
        if not reflow:
            place_text()
            return
        pad = height * 0.45
        canvas.itemconfigure(text_id, width=max(100, width - 28))
        offset = min(offset, max_offset())
        place_text()

    def resize_layout(event: tk.Event) -> None:
        update_layout(event.width, event.height, reflow=drag["mode"] != "resize")

    def finish_drag(event: tk.Event) -> None:
        nonlocal playing
        was_resizing = drag["mode"] == "resize"
        drag["mode"] = "idle"
        if was_resizing:
            update_layout(canvas.winfo_width(), canvas.winfo_height(), reflow=True)
            playing = bool(drag["resume"])

    canvas.bind("<ButtonPress-1>", start_drag)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", finish_drag)
    canvas.bind("<Configure>", resize_layout)

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
            protected = _exclude_from_capture(root)
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


def _exclude_from_capture(root) -> bool:
    if sys.platform != "win32":
        return True
    import ctypes
    from ctypes import wintypes

    root.update_idletasks()
    user32 = ctypes.windll.user32
    user32.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user32.GetAncestor.restype = wintypes.HWND
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.GetParent.restype = wintypes.HWND
    user32.SetWindowDisplayAffinity.argtypes = [wintypes.HWND, wintypes.DWORD]
    user32.SetWindowDisplayAffinity.restype = wintypes.BOOL

    widget_hwnd = wintypes.HWND(root.winfo_id())
    hwnd = user32.GetAncestor(widget_hwnd, 2)  # GA_ROOT
    if not hwnd:
        hwnd = widget_hwnd
    WDA_EXCLUDEFROMCAPTURE = 0x00000011
    if user32.SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE):
        return True

    parent = user32.GetParent(widget_hwnd)
    return bool(parent and user32.SetWindowDisplayAffinity(parent, WDA_EXCLUDEFROMCAPTURE))


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(run_check())
    if "--windows-smoke" in sys.argv:
        sys.exit(run_windows_smoke())
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
