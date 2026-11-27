#!/usr/bin/env bash
# Gera as imagens do README a partir dos HTML desta pasta (Chrome headless, 2x).
# Uso: bash assets/fonte/gerar.sh
set -e
cd "$(dirname "$0")"
CHROME="${CHROME:-/c/Program Files/Google/Chrome/Application/chrome.exe}"
gerar() { # nome largura altura
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --default-background-color=00000000 --force-device-scale-factor=2 \
    --virtual-time-budget=4000 --window-size="$2,$3" \
    --screenshot="$(cygpath -w "$PWD/../$1.png" 2>/dev/null || echo "$PWD/../$1.png")" \
    "file:///$(cygpath -m "$PWD/$1.html" 2>/dev/null || echo "$PWD/$1.html")"
}
gerar banner 1280 520
gerar etapas 1280 400
gerar instalar 1280 300
gerar premium 1280 700
gerar complementos 1280 300
gerar selos 1280 72
