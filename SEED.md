# SEED.md: Ghost Teleprompter — Complete Specification

## Overview

This is a self-contained product specification ("seed") for **Ghost Teleprompter**, a tiny native macOS teleprompter that sits below the camera and is **invisible to screen recordings and screenshots**. This file is the complete source of truth: an AI coding agent can read it and rebuild the entire product from scratch, deterministically, with no further questions.

Two ways to use this seed:
1. **Clone the repo** and run `./build.sh app`. All files are already here.
2. **Paste this single file** into any AI coding agent (Cursor, Copilot, etc.) and let it generate the one Swift file, then build it. The seed is written so the rebuild matches the original.

## Core Purpose

"A creator films short-form video (e.g. with Loom) while reading a script. The script must be readable on screen, positioned right under the camera so the eyes stay on the lens — but it must NOT appear in the screen recording or in screenshots. The viewer sees a person talking to camera; they never see the words."

## The One Trick That Matters

A macOS `NSWindow` exposes a `sharingType` property. Set it to `.none` and the window compositor excludes that window's pixels from screen-capture APIs (ScreenCaptureKit / legacy capture) and from screenshots, while still drawing the window on the physical display. This single flag is the entire product's reason to exist. Everything else is a thin reading surface around it.

## Architecture

**One process, one file.** A single Swift source file built with `swiftc`. No backend, no web server, no second device, no bundled runtime.

- Language: Swift + AppKit (Cocoa)
- Toolchain: Xcode Command Line Tools only (`swiftc`)
- No package manager, no Node, no Python, no browser engine, no third-party libraries
- Output: a ~150 KB self-contained binary, optionally wrapped in a `.app` bundle

## Build & Distribution

- `swiftc -O teleprompter.swift -o teleprompter` produces the binary.
- A `build.sh app` path wraps the binary in `Teleprompter.app/Contents/MacOS/` with an `Info.plist` and installs it to `/Applications` (fallback `~/Applications`).
- `Info.plist` sets `LSUIElement = true` (agent app: no Dock icon, launchable from Spotlight / draggable to Dock).
- The app is also set to `NSApplication.activationPolicy = .accessory` at runtime.

## Window & Geometry

- Borderless (`styleMask = [.borderless]`), `level = .statusBar` (floats above normal windows).
- `isOpaque = false`, clear background, `hasShadow = false`; content view is a rounded (corner radius ~16) translucent black panel (~80% alpha).
- **`sharingType = .none`** — the defining flag.
- `collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]`.
- `isMovableByWindowBackground = true` — the operator drags the strip to sit under the camera.
- A custom `NSWindow` subclass overrides `canBecomeKey`/`canBecomeMain` to `true` so the borderless window can take keyboard focus.
- Default size **560 × 95 px**, centered horizontally, top edge ~6 px below the visible frame's top (just under the notch/menu bar). Compact by design: shows about two lines.

## Reading Surface

- `NSScrollView` (scrollers hidden, transparent) containing a non-editable, non-selectable `NSTextView`.
- Text: white, system font, weight semibold, **22 px** default, centered, line spacing ~6.
- **One sentence per line** (see formatting below).
- Lead-in / lead-out padding equal to ~45% of the visible height (via `textContainerInset`) so the first line eases in and the last eases out.
- Auto-scroll: a 60 fps timer advances the clip view's bounds origin by a per-tick `speed` (default **0.4 px/tick**). Stops at the bottom.

## Sentence Formatting

Given raw pasted text: collapse all whitespace runs to single spaces, trim, then insert a line break after every sentence terminator — `.`, `!`, `?`, `…` (optionally followed by a closing quote/paren) when followed by whitespace. Result: one sentence per line.

## Text Input — the clipboard watcher (no file editing)

- On launch, load the script from the **system clipboard** if it holds non-empty text; otherwise fall back to `~/teleprompter/script.txt`; otherwise a built-in default.
- A 0.5 s timer polls `NSPasteboard.general.changeCount`. When it changes AND the clipboard holds non-empty text, the strip **automatically** reloads: reformat to one-sentence-per-line, scroll to top, resume playing.
- Net effect: the operator copies any text anywhere (`Cmd+C`) and the strip updates itself within ~0.5 s. There is **no in-app editor and no required file step**.

## Keyboard Controls

A local key monitor (active when the strip has focus) handles:

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

1. **Invisible to capture.** With the strip visible on screen, a screen recording (Loom/QuickTime) AND a screenshot both show NO trace of the strip or its text.
2. **Positioned under the camera.** Default placement is a centered strip just below the notch; it is draggable to fine-tune.
3. **Copy-to-update.** Copying text in any app updates the strip within ~0.5 s, reformatted one sentence per line, scrolled to top.
4. **Reads like a teleprompter.** Auto-scrolls smoothly; speed and font size adjustable live; pause keeps position.
5. **Minimal footprint.** Single Swift file; no dependencies beyond Xcode CLT; ~150 KB binary; no Dock icon.
6. **No dead controls.** Every key listed does what the table says; no console errors over a sustained session.

## What Is NOT In This Product

- No web server, no WebSocket, no React/Vite/Node, no Python, no Playwright/Chromium.
- No two-device / phone-as-display model.
- No speech-to-text, no calibration, no "speed training."
- No script library / save-open-delete UI.
- No on-screen captions baked into the video.
- No mirror-for-glass-rig requirement (the operator reads directly off the display near the lens).
- No decorative layers, particles, or animation libraries.

## Execution Model

Build it in one pass. Pick sensible defaults where this spec is silent and keep going; do not escalate. The deliverable is a working `.app` plus a runnable source file, satisfying every Acceptance Criterion. Verify the invisibility criterion by reasoning about `sharingType = .none`; the human confirms with a real 5-second screen recording.

## Why This Beats a Web Teleprompter

A browser-based teleprompter renders inside a tab or window that a full-screen recorder will happily capture, and it drags in a server, a frontend build, and often a headless browser. Ghost Teleprompter is one OS-level flag and a scroll loop: nothing to capture, nothing to install, nothing to maintain.
