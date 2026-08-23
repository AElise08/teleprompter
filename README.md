<!-- Read this in other languages: [Português 🇧🇷](README.pt-BR.md) -->

# Ghost Teleprompter

**A teleprompter that's invisible to your screen recording.**

It sits as a thin strip right below your Mac's camera so your eyes stay on the lens while you read. You see it. Loom, QuickTime, Zoom, Meet and even screenshots **don't** — the text never shows up in the recording.

It's so invisible that it won't even appear in a screenshot of your own desktop. (Yes, that made writing this README's demo image annoying.)

```
        ┌─ camera ─┐
   ╭───────────────────────╮   ← you see this strip
   │  Olhe para a câmera.   │   ← screen recorder sees nothing
   │  O texto sobe sozinho. │
   ╰───────────────────────╯
```

## Why it's different

- **Truly invisible to capture (macOS + Windows).** macOS uses `NSWindow.sharingType = .none`; Windows uses `WDA_EXCLUDEFROMCAPTURE`. Linux can still run the strip, but capture exclusion is not a portable desktop API.
- **Zero bloat.** On a Mac it's one Swift file (~150 KB). On Windows and Linux it's Python + Tk from the stdlib — still no Node, no browser, no Electron.
- **No file editing.** Copy any text (`Cmd+C`) anywhere — Notes, ChatGPT, a doc — and the strip updates **by itself**, one sentence per line.
- **Gets out of your way.** Lives below the notch, auto-scrolls, no Dock icon, draggable.

## Download and use

### I just want the app

**[Open the download site](https://aelise08.github.io/teleprompter/)** and press the button for your computer. Ready-to-run downloads are available for macOS, Windows, and Linux — no GitHub, Git, Python, or terminal required.

- **macOS:** download the DMG and drag Teleprompter to Applications. This is the original native Swift app, universal for Apple Silicon and Intel.
- **Windows:** download and open the EXE. Windows 10 or newer is required.
- **Linux:** download the `tar.gz`, extract it, and open `GhostTeleprompter-Linux-x86_64` on an x86-64 Linux desktop.

The apps do not have commercial code-signing certificates yet. macOS or Windows may show a warning on first launch; verify that the file came from the [official release page](https://github.com/AElise08/teleprompter/releases/latest).

### I want to run from source

#### macOS (native — invisible to capture)

```sh
git clone https://github.com/AElise08/teleprompter.git
cd teleprompter
./build.sh app        # compiles and installs Teleprompter.app into /Applications
```

Then open **Teleprompter** from Spotlight (`Cmd+Space`) or drag it to your Dock.

No app, just run it:

```sh
./build.sh
```

#### Windows

Install [Python 3](https://www.python.org/downloads/) (check **tcl/tk**). Then:

```bat
git clone https://github.com/AElise08/teleprompter.git
cd teleprompter
teleprompter.bat
```

Or `.\build.ps1`.

The Windows strip uses `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)` so Loom/OBS/Win+Shift+S skip it, same idea as on a Mac.

#### Linux (desktop, not a typical VPS)

You need a **graphical session** (X11 works best). A headless VPS cannot show the strip.

```sh
sudo apt install python3-tk    # Debian/Ubuntu
# Fedora: sudo dnf install python3-tkinter

git clone https://github.com/AElise08/teleprompter.git
cd teleprompter
./build.sh                     # or: python3 teleprompter.py
```

Linux has no portable “hide this window from the recorder” API. The strip still sits on top and scrolls; it **may appear** in the recording. Use macOS or Windows when invisibility matters.

#### Linux VPS (no display)

```sh
python3 teleprompter.py --check
python3 -m unittest discover -s tests -v
```

Or, if the VPS has Docker:

```sh
docker build -t ghost-teleprompter .
docker run --rm ghost-teleprompter
```

That proves the shared formatting/core. It does **not** launch a window.

> Want to rebuild the project with a coding agent? See [`SEED.md`](SEED.md), the complete product specification.

## Use it

1. **Copy** your script with `Cmd+C` on macOS or `Ctrl+C` on Windows/Linux.
2. **Open** Ghost Teleprompter — the strip already shows your text, one sentence per line.
3. **Drag** it under your camera and start recording. Read to the lens. The text isn't in the video.

> Quick check: record 5 seconds in Loom with the strip visible and watch the replay. If you can't see the text, you're good.

## Controls

| Key | Action |
|---|---|
| **Space** | Play / pause |
| **↑ / ↓** | Speed up / down |
| **+ / −** | Font size |
| **V** | Reload from clipboard |
| **R** | Restart from top |
| **0** | Reset speed |
| **Q** | Quit |
| drag | Move the strip |
| bottom-right corner | Resize the strip |

## How the trick works

On **macOS**, a window has `sharingType`. Set it to `.none` and the compositor excludes those pixels from capture APIs and screenshots — while still drawing them on the display.

On **Windows**, `SetWindowDisplayAffinity(..., WDA_EXCLUDEFROMCAPTURE)` does the same job.

On **Linux**, compositors do not expose a portable equivalent, so the strip is a normal always-on-top window.

See [`SEED.md`](SEED.md) for the full product spec.

## Requirements

- **Ready-made downloads:** macOS 13+, Windows 10 2004+, or an x86-64 Linux desktop
- **Running from source:** Xcode Command Line Tools on macOS; Python 3.9+ with Tk on Windows/Linux

## License

MIT — do whatever you want. ⭐ If it saved you a take, a star is appreciated.
