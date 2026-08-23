# Ghost Teleprompter for Mac

A compact native macOS teleprompter that stays near the camera and scrolls copied text automatically.

Download the ready-to-run DMG from the [download site](https://aelise08.github.io/teleprompter/). It supports Apple Silicon and Intel Macs running macOS 13 or newer. No Python, Git, terminal, browser, or account is required.

## Use

1. Copy your script with `Cmd+C`.
2. Open Teleprompter.
3. Drag the strip near the camera.
4. Make a short test recording before an important session.

The app sets `NSWindow.sharingType = .none`. The strip was absent in local screenshot, native recording, and ScreenCaptureKit tests, but Apple classifies this behavior as legacy; verify it with the recorder you intend to use.

## Build

With Xcode Command Line Tools installed:

```sh
./build.sh app
```

This compiles and installs `Teleprompter.app` in `/Applications`.

## License

MIT.
