#!/usr/bin/env bash
# Compila o teleprompter nativo para macOS.
# Uso:
#   ./build.sh       -> compila e abre sem instalar
#   ./build.sh app   -> compila e instala em /Applications
set -euo pipefail
cd "$(dirname "$0")"

arg="${1:-}"

if [[ "$(uname -s)" != Darwin ]]; then
  echo "Este projeto funciona somente no macOS."
  exit 1
fi

if [[ "$arg" == app ]]; then
  APP="Teleprompter.app"
  rm -rf "$APP"
  mkdir -p "$APP/Contents/MacOS"
  swiftc -O teleprompter.swift -o "$APP/Contents/MacOS/Teleprompter"
  cp Info.plist "$APP/Contents/Info.plist"
  cp -R "$APP" /Applications/ 2>/dev/null || {
    mkdir -p ~/Applications
    cp -R "$APP" ~/Applications/
  }
  echo "Teleprompter.app instalado. Procure por 'Teleprompter' no Spotlight."
  exit 0
fi

if [[ -n "$arg" ]]; then
  echo "Uso: ./build.sh [app]"
  exit 1
fi

swiftc -O teleprompter.swift -o teleprompter
echo "Compilado. Abrindo..."
exec ./teleprompter
