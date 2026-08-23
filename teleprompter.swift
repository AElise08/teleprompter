import Cocoa

// Janela sem borda que ainda pode receber teclado/foco
final class TPWindow: NSWindow {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }
}

// Alça discreta no canto inferior direito para redimensionar a faixa.
final class ResizeHandleView: NSView {
    private var startMouse = NSPoint.zero
    private var startFrame = NSRect.zero
    var onResizeStart: (() -> Void)?
    var onResizeEnd: (() -> Void)?

    // Impede que o NSWindow interprete o mesmo gesto como movimento da faixa.
    override var mouseDownCanMoveWindow: Bool { false }

    override func draw(_ dirtyRect: NSRect) {
        NSColor.white.withAlphaComponent(0.38).setStroke()
        for offset: CGFloat in [6, 10, 14] {
            let path = NSBezierPath()
            path.lineWidth = 1.5
            path.move(to: NSPoint(x: bounds.maxX - offset, y: 3))
            path.line(to: NSPoint(x: bounds.maxX - 3, y: offset))
            path.stroke()
        }
    }

    override func mouseDown(with event: NSEvent) {
        guard let window else { return }
        startMouse = NSEvent.mouseLocation
        startFrame = window.frame
        onResizeStart?()
    }

    override func mouseDragged(with event: NSEvent) {
        guard let window else { return }
        let mouse = NSEvent.mouseLocation
        let width = min(1000, max(360, startFrame.width + mouse.x - startMouse.x))
        let height = min(300, max(72, startFrame.height - (mouse.y - startMouse.y)))
        let frame = NSRect(
            x: startFrame.minX,
            y: startFrame.maxY - height,
            width: width,
            height: height)
        window.setFrame(frame, display: true)
    }

    override func mouseUp(with event: NSEvent) {
        onResizeEnd?()
    }
}

let DEFAULT_TEXT = """
Copie o seu roteiro com Cmd+C e reabra: o teleprompter usa o que você copiou.
Esta faixa fica embaixo da câmera e não aparece na gravação do Loom.
Espaço pausa. Setas mudam a velocidade. Mais e menos mudam o tamanho. V recarrega do que você copiou. R recomeça. Q fecha.
"""

// Quebra o texto em uma frase por linha
func formatSentences(_ raw: String) -> String {
    let collapsed = raw
        .replacingOccurrences(of: "\\s+", with: " ", options: .regularExpression)
        .trimmingCharacters(in: .whitespacesAndNewlines)
    return collapsed.replacingOccurrences(
        of: "([.!?…]+[\"')\\]]?)\\s+", with: "$1\n", options: .regularExpression)
}

func loadScript() -> String {
    if let cb = NSPasteboard.general.string(forType: .string),
       !cb.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        return formatSentences(cb)
    }
    let path = ("~/teleprompter/script.txt" as NSString).expandingTildeInPath
    if let t = try? String(contentsOfFile: path, encoding: .utf8),
       !t.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty {
        return formatSentences(t)
    }
    return DEFAULT_TEXT
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    var window: TPWindow!
    var scrollView: NSScrollView!
    var textView: NSTextView!
    var timer: Timer?
    var clipTimer: Timer?
    var lastChange = 0
    var speed: CGFloat = 0.4      // pixels por tick (~60fps)
    var fontSize: CGFloat = 22
    var playing = true
    var resumeAfterResize = false
    var rawText = DEFAULT_TEXT

    func applicationDidFinishLaunching(_ n: Notification) {
        NSApp.setActivationPolicy(.accessory) // sem ícone no Dock

        rawText = loadScript()

        // Geometria: faixa centralizada logo abaixo do notch
        let screen = NSScreen.main ?? NSScreen.screens.first!
        let vf = screen.visibleFrame
        let w: CGFloat = 560
        let h: CGFloat = 95
        let x = vf.midX - w / 2
        let y = vf.maxY - h - 6
        let rect = NSRect(x: x, y: y, width: w, height: h)

        window = TPWindow(contentRect: rect, styleMask: [.borderless],
                          backing: .buffered, defer: false)
        window.level = .statusBar
        window.isOpaque = false
        window.backgroundColor = .clear
        window.hasShadow = false
        window.sharingType = .none        // <<< invisível pra gravação de tela e prints
        window.collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary, .stationary]
        window.isMovableByWindowBackground = true

        // Fundo arredondado translúcido
        let container = NSView(frame: NSRect(origin: .zero, size: rect.size))
        container.wantsLayer = true
        container.layer?.backgroundColor = NSColor.black.withAlphaComponent(0.80).cgColor
        container.layer?.cornerRadius = 16
        window.contentView = container

        let inset: CGFloat = 13
        let svFrame = NSRect(x: inset, y: inset,
                             width: rect.width - inset * 2,
                             height: rect.height - inset * 2)
        scrollView = NSScrollView(frame: svFrame)
        scrollView.hasVerticalScroller = false
        scrollView.hasHorizontalScroller = false
        scrollView.drawsBackground = false
        scrollView.autoresizingMask = [.width, .height]

        textView = NSTextView(frame: NSRect(x: 0, y: 0, width: svFrame.width, height: 100))
        textView.isEditable = false
        textView.isSelectable = false
        textView.drawsBackground = false
        textView.isVerticallyResizable = true
        textView.isHorizontallyResizable = false
        textView.textContainer?.widthTracksTextView = true
        scrollView.documentView = textView
        container.addSubview(scrollView)

        let resizeHandle = ResizeHandleView(frame: NSRect(x: rect.width - 22, y: 0, width: 22, height: 22))
        resizeHandle.autoresizingMask = [.minXMargin, .maxYMargin]
        resizeHandle.onResizeStart = { [weak self] in
            guard let self else { return }
            self.resumeAfterResize = self.playing
            self.playing = false
        }
        resizeHandle.onResizeEnd = { [weak self] in
            guard let self else { return }
            self.relayout()
            self.playing = self.resumeAfterResize
        }
        container.addSubview(resizeHandle)

        applyText()

        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)

        NSEvent.addLocalMonitorForEvents(matching: .keyDown) { [weak self] e in
            (self?.handleKey(e) ?? false) ? nil : e
        }

        timer = Timer.scheduledTimer(withTimeInterval: 1.0 / 60.0, repeats: true) { [weak self] _ in
            self?.tick()
        }
        RunLoop.main.add(timer!, forMode: .common)

        // Observa a área de transferência: ao copiar (Cmd+C), troca o texto sozinho
        lastChange = NSPasteboard.general.changeCount
        clipTimer = Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { [weak self] _ in
            self?.watchClipboard()
        }
        RunLoop.main.add(clipTimer!, forMode: .common)
    }

    func watchClipboard() {
        let pb = NSPasteboard.general
        guard pb.changeCount != lastChange else { return }
        lastChange = pb.changeCount
        guard let s = pb.string(forType: .string),
              !s.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        rawText = formatSentences(s)
        applyText()
        scrollTop()
        playing = true
    }

    func applyText() {
        let style = NSMutableParagraphStyle()
        style.lineSpacing = 6
        style.paragraphSpacing = 4
        style.alignment = .center
        let attr = NSAttributedString(string: rawText, attributes: [
            .font: NSFont.systemFont(ofSize: fontSize, weight: .semibold),
            .foregroundColor: NSColor.white,
            .paragraphStyle: style
        ])
        textView.textStorage?.setAttributedString(attr)
        relayout()
    }

    func relayout() {
        let clipH = scrollView.contentSize.height
        let pad = clipH * 0.45                       // espaço pra entrar e sair suave
        textView.textContainerInset = NSSize(width: 0, height: pad)
        textView.textContainer?.containerSize =
            NSSize(width: scrollView.contentSize.width, height: .greatestFiniteMagnitude)
        guard let lm = textView.layoutManager, let tc = textView.textContainer else { return }
        lm.ensureLayout(for: tc)
        let used = lm.usedRect(for: tc).size.height
        let docH = max(used + pad * 2, clipH)
        textView.minSize = NSSize(width: scrollView.contentSize.width, height: docH)
        textView.frame = NSRect(x: 0, y: 0, width: scrollView.contentSize.width, height: docH)
    }

    func tick() {
        guard playing else { return }
        let clip = scrollView.contentView
        var o = clip.bounds.origin
        let maxY = textView.frame.height - clip.bounds.height
        if maxY <= 0 { return }
        o.y += speed
        if o.y >= maxY { o.y = maxY; playing = false }
        clip.scroll(to: o)
        scrollView.reflectScrolledClipView(clip)
    }

    func scrollTop() {
        let clip = scrollView.contentView
        clip.scroll(to: NSPoint(x: 0, y: 0))
        scrollView.reflectScrolledClipView(clip)
    }

    func scrollEnd() {
        let clip = scrollView.contentView
        let maxY = max(0, textView.frame.height - clip.bounds.height)
        clip.scroll(to: NSPoint(x: 0, y: maxY))
        scrollView.reflectScrolledClipView(clip)
    }

    func setSpeed(_ s: CGFloat) { speed = min(8, max(0.1, s)) }

    func changeFont(_ d: CGFloat) {
        let clip = scrollView.contentView
        let maxY = max(1, textView.frame.height - clip.bounds.height)
        let frac = clip.bounds.origin.y / maxY
        fontSize = min(80, max(14, fontSize + d))
        applyText()
        let newMax = max(0, textView.frame.height - clip.bounds.height)
        clip.scroll(to: NSPoint(x: 0, y: frac * newMax))
        scrollView.reflectScrolledClipView(clip)
    }

    func handleKey(_ e: NSEvent) -> Bool {
        switch e.keyCode {
        case 49: playing.toggle(); return true              // espaço
        case 126: setSpeed(speed + 0.2); return true        // ↑
        case 125: setSpeed(speed - 0.2); return true        // ↓
        case 123, 116: scrollTop(); return true             // ← / PageUp
        case 124, 121: scrollEnd(); return true             // → / PageDown
        default: break
        }
        switch (e.charactersIgnoringModifiers ?? "").lowercased() {
        case "+", "=": changeFont(2); return true
        case "-", "_": changeFont(-2); return true
        case "r": scrollTop(); playing = true; return true
        case "v": rawText = loadScript(); applyText(); scrollTop(); playing = true; return true
        case "0": setSpeed(0.4); return true
        case "q": NSApp.terminate(nil); return true
        default: return false
        }
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.run()
