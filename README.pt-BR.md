
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

- **Some da captura no Mac e no Windows.** macOS usa `NSWindow.sharingType = .none`; Windows usa `WDA_EXCLUDEFROMCAPTURE`. No Linux a faixa roda, mas esconder da gravação não é API portátil.
- **Sem inchaço.** No Mac é um arquivo Swift (~150 KB). No Windows e no Linux é Python + Tk da biblioteca padrão — ainda sem Node, sem navegador, sem Electron.
- **Sem editar arquivo.** Copie qualquer texto (`Cmd+C`) de onde quiser — Notas, ChatGPT, um doc — e a faixa troca **sozinha**, uma frase por linha.
- **Não atrapalha.** Fica embaixo do notch, rola sozinha, sem ícone no Dock, e dá pra arrastar.

## Baixar e usar

### Não sou desenvolvedor

**[Abra o site de download](https://aelise08.github.io/teleprompter/)** e aperte o botão do seu computador. Há arquivos prontos para Mac, Windows e Linux — não precisa usar GitHub, Git, Python ou terminal.

- **Mac:** baixe o DMG e arraste o Teleprompter para Aplicativos. É o app Swift nativo original, universal para Apple Silicon e Intel.
- **Windows:** baixe e abra o EXE. Funciona no Windows 10 ou mais recente.
- **Linux:** baixe o `tar.gz`, extraia e abra o arquivo `GhostTeleprompter-Linux-x86_64` em um desktop Linux x86-64.

Os aplicativos ainda não têm assinatura comercial. O Mac ou o Windows pode mostrar um aviso na primeira abertura; confira que o arquivo veio da [página oficial de releases](https://github.com/AElise08/teleprompter/releases/latest).

### Quero executar pelo código

#### macOS (nativo — some da captura)

```sh
git clone https://github.com/AElise08/teleprompter.git
cd teleprompter
./build.sh app        # compila e instala o Teleprompter.app em /Applications
```

Depois abra **Teleprompter** pelo Spotlight (`Cmd+Espaço`) ou arraste pro Dock.

Sem instalar o app, só rodar:

```sh
./build.sh
```

#### Windows

Instale o [Python 3](https://www.python.org/downloads/) (marque **tcl/tk**). Depois:

```bat
git clone https://github.com/AElise08/teleprompter.git
cd teleprompter
teleprompter.bat
```

Ou `.\build.ps1`.

No Windows a faixa usa `SetWindowDisplayAffinity(WDA_EXCLUDEFROMCAPTURE)`: Loom/OBS/Win+Shift+S pulam ela, a mesma ideia do Mac.

#### Linux

Precisa de **sessão gráfica** (X11 funciona melhor). VPS sem desktop não mostra a faixa.

```sh
sudo apt install python3-tk    # Debian/Ubuntu
# Fedora: sudo dnf install python3-tkinter

git clone https://github.com/AElise08/teleprompter.git
cd teleprompter
./build.sh                     # ou: python3 teleprompter.py
```

No Linux não existe API portátil pra esconder a janela do gravador. A faixa fica por cima e rola; **pode aparecer** na gravação. Use Mac ou Windows quando a invisibilidade importar.

#### VPS Linux (sem tela)

```sh
python3 teleprompter.py --check
python3 -m unittest discover -s tests -v
```

Ou, se a VPS tiver Docker:

```sh
docker build -t ghost-teleprompter .
docker run --rm ghost-teleprompter
```

Isso valida o núcleo compartilhado. **Não** abre janela.

> Quer recriar o projeto com uma IA de código? Veja o [`SEED.md`](SEED.md), a especificação completa do produto.

## Como usar

1. **Copie** seu roteiro com `Cmd+C` no Mac ou `Ctrl+C` no Windows/Linux.
2. **Abra** o Ghost Teleprompter — a faixa já mostra seu texto, uma frase por linha.
3. **Arraste** pra baixo da câmera e grave. Leia olhando pra lente. O texto não vai no vídeo.

> Teste rápido: grave 5 segundos no Loom com a faixa visível e veja o replay. Se você não enxergar o texto, está perfeito.

## Controles


| Tecla      | Ação                          |
| ---------- | ----------------------------- |
| **Espaço** | Pausa / continua              |
| **↑ / ↓**  | Velocidade                    |
| **+ / −**  | Tamanho da fonte              |
| **V**      | Recarrega do que está copiado |
| **R**      | Recomeça do topo              |
| **0**      | Velocidade padrão             |
| **Q**      | Fecha                         |
| arrastar   | Move a faixa                  |


## Como o truque funciona

No **macOS**, a janela tem `sharingType`. Em `.none`, o compositor tira esses pixels das APIs de captura e dos prints — e continua desenhando na tela.

No **Windows**, `SetWindowDisplayAffinity(..., WDA_EXCLUDEFROMCAPTURE)` faz o mesmo.

No **Linux**, os compositors não expõem um equivalente portátil, então a faixa é uma janela normal sempre por cima.

Veja o [`SEED.md`](SEED.md) pra especificação completa.

## Requisitos

- **Downloads prontos:** macOS 13+, Windows 10 2004+ ou desktop Linux x86-64
- **Execução pelo código:** Xcode Command Line Tools no Mac; Python 3.9+ com Tk no Windows/Linux

## Licença

MIT — faça o que quiser. ⭐ Se te salvou de uma regravação, uma estrela cai bem.
