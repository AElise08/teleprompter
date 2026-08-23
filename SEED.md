# SEED.md: Ghost Teleprompter — Complete Specification

## Overview

This is a self-contained product specification ("seed") for **Ghost Teleprompter**, a tiny teleprompter that sits below the camera and, on macOS and Windows, is **invisible to screen recordings and screenshots**. This file is the complete source of truth: an AI coding agent can read it and rebuild the entire product from scratch, deterministically, with no further questions.

Two ways to use this seed:
1. **Clone the repo** and follow the per-OS build in the README.
2. **Paste this single file** into any AI coding agent (Cursor, Copilot, etc.) and let it generate the sources, then build.

## Core Purpose

"A creator films short-form video (e.g. with Loom) while reading a script. The script must be readable on screen, positioned right under the camera so the eyes stay on the lens — but it must NOT appear in the screen recording or in screenshots. The viewer sees a person talking to camera; they never see the words."

## The One Trick That Matters

**macOS.** A `NSWindow` exposes `sharingType`. Set it to `.none` and the compositor excludes that window's pixels from screen-capture APIs and screenshots, while still drawing it on the physical display.

**Windows.** `SetWindowDisplayAffinity(hwnd, WDA_EXCLUDEFROMCAPTURE)` (0x11) is the equivalent: the strip is drawn on the monitor but skipped by capture APIs (Windows 10 2004+).

**Linux.** There is no portable compositor API that excludes a window from PipeWire/X11 capture. The Linux build is still a always-on-top reading strip; invisibility is **not** guaranteed. Document that limit; do not fake it.

## Architecture

Two front ends, one formatting core:

- **macOS native:** `teleprompter.swift` — Swift + AppKit, `swiftc` only, ~150 KB binary / `.app` bundle. This remains the best Mac experience (no Dock icon, `sharingType = .none`).
- **Linux / Windows (and optional Mac):** `teleprompter.py` + `scriptfmt.py` — Python 3.9+ stdlib + Tk. No pip packages at runtime. Windows capture exclusion via `ctypes` / `user32`.
- **Shared formatting:** `scriptfmt.format_sentences` (collapse whitespace, one sentence per line). Covered by `tests/test_scriptfmt.py` so a headless Linux VPS can verify logic without a display.

No backend, no web server, no Node, no Electron, no second device.

## Build & Distribution

- macOS: `./build.sh` (`swiftc`) or `./build.sh app` → `Teleprompter.app` in `/Applications` (fallback `~/Applications`). `Info.plist` sets `LSUIElement = true`. Runtime `NSApplication.activationPolicy = .accessory`.
- Linux desktop: `python3 teleprompter.py` (package `python3-tk`). `./build.sh` on Linux takes this path.
- Windows: `python teleprompter.py` or `.\teleprompter.bat` / `.\build.ps1`. CI (`windows-latest`) builds `GhostTeleprompter.exe` with PyInstaller and uploads it as an artifact.
- Headless VPS: `python3 teleprompter.py --check` and `python3 -m unittest discover -s tests -v`. A typical VPS has no GUI; it cannot display the strip.
- CI must run unit tests + `--check` on ubuntu-latest, windows-latest, and macos-latest, compile Swift on macOS, and smoke the Tk window under Xvfb on Ubuntu.
- Public download site: GitHub Pages serves `docs/index.html`, with one OS-aware download button plus explicit Mac, Windows, and Linux buttons. Users must not need to understand GitHub Actions or install developer tools.
- Tagged releases: pushing a `v*` tag builds a universal native macOS DMG (Intel + Apple Silicon), a standalone Windows EXE, and a portable Linux x86-64 archive. The site links to GitHub's permanent `releases/latest/download/...` URLs.

## Window & Geometry

- Borderless, always on top, default **560 × 95 px**, centered horizontally, a few pixels below the top of the screen (under notch/camera).
- Dark translucent panel; draggable.
- **macOS:** `sharingType = .none`, `collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]`, `isMovableByWindowBackground = true`.
- **Windows:** `overrideredirect`, `-topmost`, `SetWindowDisplayAffinity(..., WDA_EXCLUDEFROMCAPTURE)`.
- **Linux:** `overrideredirect` + `-topmost` (X11). Wayland may ignore always-on-top / overlay; prefer an X11 session for the strip.

## Reading Surface

- Centered white semibold text, **22 px** default, wrapped to the strip width.
- **One sentence per line** (see formatting below).
- Lead-in / lead-out padding ~45% of visible height so the first line eases in and the last eases out.
- Auto-scroll ~60 fps by a per-tick `speed` (default **0.4 px/tick**). Stops at the bottom.

## Sentence Formatting

Given raw pasted text: collapse all whitespace runs to single spaces, trim, then insert a line break after every sentence terminator — `.`, `!`, `?`, `…` (optionally followed by a closing quote/paren) when followed by whitespace. Result: one sentence per line.

## Text Input — the clipboard watcher (no file editing)

- On launch, load the script from the **system clipboard** if it holds non-empty text; otherwise fall back to `~/teleprompter/script.txt` (Windows: `%USERPROFILE%\teleprompter\script.txt`); otherwise a built-in default.
- A 0.5 s timer polls the clipboard. On Windows use `GetClipboardSequenceNumber`; elsewhere compare clipboard text. When it changes AND the clipboard holds non-empty text, the strip **automatically** reloads: reformat to one-sentence-per-line, scroll to top, resume playing.
- Net effect: the operator copies any text anywhere and the strip updates itself within ~0.5 s. There is **no in-app editor and no required file step**.

## Keyboard Controls

Active when the strip has focus:

| Key | Action |
|---|---|
| Space | Toggle play/pause (pause keeps position) |
| ↑ / ↓ | Speed ± 0.2, clamped [0.1, 8] |
| ← / PageUp | Jump to top |
| → / PageDown | Jump to end |
| + / − | Font size ± 2, clamped [14, 80], keeping scroll fraction |
| V | Reload from clipboard now |
| R | Restart from top and play |
| 0 | Reset speed to default |
| Q | Quit |

## Acceptance Criteria

1. **Invisible to capture (macOS + Windows).** With the strip visible, a screen recording AND a screenshot show NO trace of the strip. On Linux this criterion is waived; the strip must still read and scroll.
2. **Positioned under the camera.** Default placement is a centered strip near the top; it is draggable to fine-tune.
3. **Copy-to-update.** Copying text in any app updates the strip within ~0.5 s, reformatted one sentence per line, scrolled to top.
4. **Reads like a teleprompter.** Auto-scrolls smoothly; speed and font size adjustable live; pause keeps position.
5. **Minimal footprint.** macOS: single Swift file, Xcode CLT only. Linux/Windows: Python stdlib + Tk, no pip at runtime.
6. **No dead controls.** Every key listed does what the table says.
7. **Headless verification.** `python3 teleprompter.py --check` and the unit tests pass on Linux without a display.

## What Is NOT In This Product

- No web server, no WebSocket, no React/Vite/Node, no Playwright/Chromium.
- No two-device / phone-as-display model.
- No speech-to-text, no calibration, no "speed training."
- No script library / save-open-delete UI.
- No on-screen captions baked into the video.
- No mirror-for-glass-rig requirement (the operator reads directly off the display near the lens).
- No decorative layers, particles, or animation libraries.
- No claim of capture-invisibility on Linux.

## Execution Model

Build it in one pass. Pick sensible defaults where this spec is silent and keep going; do not escalate. Deliver a working macOS `.app`, a runnable Python strip for Linux/Windows, tests that pass headless, and CI on the three OSes. Verify macOS invisibility by `sharingType = .none` and Windows invisibility by `WDA_EXCLUDEFROMCAPTURE`; the human confirms with a real screen recording on a machine that has a display.

## Why This Beats a Web Teleprompter

A browser-based teleprompter renders inside a tab or window that a full-screen recorder will happily capture, and it drags in a server, a frontend build, and often a headless browser. Ghost Teleprompter is an OS-level exclusion flag (where the OS has one) plus a scroll loop: nothing extra to install on macOS, and on Windows/Linux only Python+Tk.
