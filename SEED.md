# Ghost Teleprompter — especificação para Mac

## Objetivo

Aplicativo nativo e pequeno para macOS. Ele mostra o roteiro em uma faixa sem borda, sempre visível e posicionada perto da câmera, com rolagem automática.

## Arquitetura

- `teleprompter.swift`: aplicativo AppKit completo.
- `Info.plist`: metadados do bundle e modo sem ícone no Dock.
- `build.sh`: compilação local e instalação em `/Applications`.
- `.github/workflows/release.yml`: DMG universal para Apple Silicon e Intel.
- `docs/index.html`: página pública de download somente para Mac.

Não há versão Windows, Linux, Python, Docker, servidor, Node ou Electron.

## Comportamento

- Janela sem borda, translúcida e sempre no topo.
- Tamanho inicial de 560 × 95 pontos.
- Redimensionamento entre 360 × 72 e 1000 × 300 pontos.
- Texto branco centralizado, 22 pontos por padrão.
- Texto carregado da área de transferência e atualizado quando o usuário copia outro roteiro.
- Rolagem automática suave e controles descritos no README.
- `NSWindow.sharingType = .none` para solicitar exclusão das capturas compatíveis.

Como a Apple classifica `NSWindowSharingNone` como legado, o produto não deve prometer invisibilidade absoluta. Oriente sempre uma gravação curta de teste no gravador escolhido.

## Distribuição

O download público é `GhostTeleprompter-macOS.dmg`, criado ao publicar uma tag `v*`. O aplicativo exige macOS 13 ou mais recente e não possui assinatura comercial.
