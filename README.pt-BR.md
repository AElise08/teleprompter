<!-- Read this in other languages: [English 🇺🇸](README.md) -->

# Ghost Teleprompter 👻

**Um teleprompter invisível na sua gravação de tela.**

Ele fica como uma faixa fininha logo abaixo da câmera do Mac, pra você ler olhando pra lente. Você vê. O Loom, o QuickTime, o Zoom, o Meet e até os prints **não** veem — o texto nunca aparece na gravação.

É tão invisível que nem sai num print da sua própria tela. (Sim, isso deu trabalho pra fazer a imagem de demonstração deste README.)

```
        ┌── câmera ──┐
   ╭────────────────────────╮   ← você vê esta faixa
   │  Olhe para a câmera.    │   ← a gravação não vê nada
   │  O texto sobe sozinho.  │
   ╰────────────────────────╯
```

## Por que é diferente

- **Some de verdade da captura.** Usa o `NSWindow.sharingType = .none` do macOS — a mesma flag que gerenciadores de senha usam pra sumir de prints. O gravador simplesmente pula essa janela.
- **Zero dependências.** Um arquivo Swift, binário de ~150 KB. Sem Node, sem Python, sem navegador, sem Electron. Só as Command Line Tools do Xcode, que você provavelmente já tem.
- **Sem editar arquivo.** Copie qualquer texto (`Cmd+C`) de onde quiser — Notas, ChatGPT, um doc — e a faixa troca **sozinha**, uma frase por linha.
- **Não atrapalha.** Fica embaixo do notch, rola sozinha, sem ícone no Dock, e dá pra arrastar.

## Instalar

```sh
git clone git@github.com:AElise08/teleprompter.git
cd teleprompter
./build.sh app        # compila e instala o Teleprompter.app em /Applications
```

Depois abra **Teleprompter** pelo Spotlight (`Cmd+Espaço`) ou arraste pro Dock.

Sem instalar o app, só rodar:

```sh
./build.sh
```

> Não quer clonar nada? Veja o [`SEED.md`](SEED.md) — cole esse arquivo único em qualquer IA de código (Cursor, Copilot, etc.) e ela gera este app inteiro do zero pra você.

## Como usar

1. **Copie** seu roteiro com `Cmd+C` de qualquer lugar.
2. **Abra** o Ghost Teleprompter — a faixa já mostra seu texto, uma frase por linha.
3. **Arraste** pra baixo da câmera e grave. Leia olhando pra lente. O texto não vai no vídeo.

> Teste rápido: grave 5 segundos no Loom com a faixa visível e veja o replay. Se você não enxergar o texto, está perfeito.

## Controles

| Tecla | Ação |
|---|---|
| **Espaço** | Pausa / continua |
| **↑ / ↓** | Velocidade |
| **+ / −** | Tamanho da fonte |
| **V** | Recarrega do que está copiado |
| **R** | Recomeça do topo |
| **0** | Velocidade padrão |
| **Q** | Fecha |
| arrastar | Move a faixa |

## Como o truque funciona

Toda janela do macOS tem um `sharingType`. Coloque em `.none` e o sistema exclui os pixels dessa janela das APIs de captura e dos prints — mas continua desenhando ela na sua tela física. O Ghost Teleprompter é só uma faixa sem borda, sempre por cima, com essa flag ligada, mais um auto-scroll e um observador da área de transferência. É essa a ideia inteira.

Veja o [`SEED.md`](SEED.md) pra especificação completa.

## Requisitos

- macOS 13 ou mais novo
- Xcode Command Line Tools (`xcode-select --install`)

## Licença

MIT — faça o que quiser. ⭐ Se te salvou de uma regravação, uma estrela cai bem.
