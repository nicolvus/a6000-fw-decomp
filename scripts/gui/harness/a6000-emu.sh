#!/bin/sh
# Acceso directo del emulador: arranca el lanzador (si no corre ya) y abre el configurador en el navegador por defecto.
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
PUERTO="${A6000_EMU_PUERTO:-8700}"
URL="http://127.0.0.1:$PUERTO/"
LOG="${XDG_CACHE_HOME:-$HOME/.cache}/a6000-emu"
mkdir -p "$LOG"
if ! curl -fs -m 2 "${URL}api/estado" >/dev/null 2>&1; then
  nohup "$REPO/.venv/bin/python" "$REPO/scripts/gui/harness/lanzador.py" --puerto "$PUERTO" >"$LOG/lanzador.log" 2>&1 &
  for _ in $(seq 1 40); do curl -fs -m 1 "${URL}api/estado" >/dev/null 2>&1 && break; sleep 0.25; done
fi
exec xdg-open "$URL"
