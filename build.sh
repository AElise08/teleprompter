#!/bin/zsh
# Compila o teleprompter e (opcional) gera o app pra arrastar pro Dock.
# Uso:  ./build.sh        -> compila e roda
#       ./build.sh app    -> gera Teleprompter.app e instala em /Applications
set -e
cd "$(dirname "$0")"

if [[ "$1" == "app" ]]; then
  APP="Teleprompter.app"
  rm -rf "$APP"
  mkdir -p "$APP/Contents/MacOS"
  swiftc -O teleprompter.swift -o "$APP/Contents/MacOS/Teleprompter"
  cp Info.plist "$APP/Contents/Info.plist"
  cp -R "$APP" /Applications/ 2>/dev/null || { mkdir -p ~/Applications && cp -R "$APP" ~/Applications/; }
  echo "Teleprompter.app instalado. Procure por 'Teleprompter' no Spotlight."
else
  swiftc -O teleprompter.swift -o teleprompter
  echo "Compilado. Abrindo..."
  ./teleprompter
fi
