<!-- Read this in other languages: [Português 🇧🇷](README.pt-BR.md) -->

# Ghost Teleprompter 👻

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

- **Truly invisible to capture.** Uses macOS `NSWindow.sharingType = .none`, the same flag password managers use to hide from screenshots. Screen recorders skip the window entirely.
- **Zero dependencies, zero bloat.** One Swift file, ~150 KB binary. No Node, no Python, no browser, no Electron. Just the Xcode Command Line Tools you probably already have.
- **No file editing.** Copy any text (`Cmd+C`) anywhere — Notes, ChatGPT, a doc — and the strip updates **by itself**, one sentence per line.
- **Gets out of your way.** Lives below the notch, auto-scrolls, no Dock icon, draggable.

## Install

```sh
git clone git@github.com:AElise08/teleprompter.git
cd teleprompter
./build.sh app        # compiles and installs Teleprompter.app into /Applications
```

Then open **Teleprompter** from Spotlight (`Cmd+Space`) or drag it to your Dock.

No app, just run it:

```sh
./build.sh
```

> Don't want to clone anything? See [`SEED.md`](SEED.md) — paste that single file into any AI coding agent (Cursor, Copilot, etc.) and it will generate this whole app for you from scratch.

## Use it

1. **Copy** your script anywhere with `Cmd+C`.
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

## How the trick works

A macOS window has a `sharingType`. Set it to `.none` and the compositor excludes that window's pixels from screen capture APIs and screenshots — while still drawing it on your physical display. Ghost Teleprompter is just a borderless, always-on-top strip with that one flag set, plus an auto-scroller and a clipboard watcher. That's the whole idea.

See [`SEED.md`](SEED.md) for the full product spec.

## Requirements

- macOS 13 or newer
- Xcode Command Line Tools (`xcode-select --install`)

## License

MIT — do whatever you want. ⭐ If it saved you a take, a star is appreciated.
