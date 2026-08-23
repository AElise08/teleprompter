# Ghost Teleprompter para Mac

Uma faixa compacta que fica perto da câmera do Mac e rola o roteiro automaticamente.

O aplicativo é nativo do macOS, não precisa de Python, Git, terminal, navegador nem cadastro. O roteiro permanece no computador.

## Baixar

Abra o [site de download](https://aelise08.github.io/teleprompter/) e aperte **Baixar para Mac**. O DMG funciona em Macs Apple Silicon e Intel com macOS 13 ou mais recente.

1. Abra o arquivo `.dmg` baixado.
2. Arraste **Teleprompter** para **Aplicativos**.
3. Se o macOS bloquear a primeira abertura, clique com o botão direito no aplicativo e escolha **Abrir**.

## Como usar

1. Copie o roteiro com `Cmd+C`.
2. Abra o Teleprompter.
3. Arraste a faixa para perto da câmera.
4. Faça uma gravação curta de teste antes da gravação importante.

O aplicativo usa `NSWindow.sharingType = .none`. A faixa ficou ausente nos testes locais com captura de tela, gravação nativa e ScreenCaptureKit, mas a Apple classifica esse recurso como legado; por isso, confirme o comportamento no gravador que será usado.

## Controles

| Tecla | Ação |
|---|---|
| Espaço | Pausa ou continua |
| ↑ / ↓ | Altera a velocidade |
| + / − | Altera o tamanho da fonte |
| V | Recarrega o texto copiado |
| R | Recomeça do topo |
| 0 | Volta à velocidade padrão |
| Q | Fecha |
| Arrastar | Move a faixa |
| Canto inferior direito | Redimensiona a faixa |

## Compilar pelo código

Requer o Xcode Command Line Tools:

```sh
./build.sh app
```

Esse comando compila e instala `Teleprompter.app` em `/Applications`.

## Licença

MIT.
