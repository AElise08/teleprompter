#!/usr/bin/env bash
# macOS nativo (Swift) ou faixa portátil (Python) no Linux/Windows.
# Uso:
#   ./build.sh           -> no Mac, compila Swift e abre; no Linux, abre o Python
#   ./build.sh app       -> só macOS: instala Teleprompter.app
#   ./build.sh python    -> força a faixa Python (útil no Mac pra testar o mesmo código do Linux/Windows)
#   ./build.sh --check   -> verifica sem abrir janela (serve na VPS)
set -euo pipefail
cd "$(dirname "$0")"

os="$(uname -s 2>/dev/null || echo unknown)"
arg="${1:-}"

if [[ "$arg" == "--check" ]]; then
  python3 teleprompter.py --check
  exit 0
fi

if [[ "$arg" == "app" ]]; then
  if [[ "$os" != Darwin ]]; then
    echo "Teleprompter.app só existe no macOS. Aqui rode: python3 teleprompter.py"
    exit 1
  fi
  APP="Teleprompter.app"
  rm -rf "$APP"
  mkdir -p "$APP/Contents/MacOS"
  swiftc -O teleprompter.swift -o "$APP/Contents/MacOS/Teleprompter"
  cp Info.plist "$APP/Contents/Info.plist"
  cp -R "$APP" /Applications/ 2>/dev/null || { mkdir -p ~/Applications && cp -R "$APP" ~/Applications/; }
  echo "Teleprompter.app instalado. Procure por 'Teleprompter' no Spotlight."
  exit 0
fi

if [[ "$os" == Darwin && "$arg" != "python" ]]; then
  swiftc -O teleprompter.swift -o teleprompter
  echo "Compilado (macOS nativo). Abrindo..."
  ./teleprompter
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 não encontrado. Instale Python 3 e o pacote Tk (python3-tk)."
  exit 1
fi

echo "Abrindo faixa portátil (Python)..."
exec python3 teleprompter.py
