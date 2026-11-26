#!/usr/bin/env bash
# Extrae el log del MMgr de TODOS los estado.zst del arnes.
# Uso: extraer_todos.sh
# Salida doble por perfil en reports/evidence/logs-arnes-todos/:
#   <perfil>.log.txt      -> salida literal de extraer_log_estado.py (dedup, patron por tag)
#   <perfil>.markers.txt  -> segunda pasada: cualquier linea (<=400 B, texto) con un marcador
#                            de la ruta de video, aunque no lleve tag entre corchetes
set -uo pipefail
cd "$(dirname "$0")/../../.." || exit 1

SRC=reports/evidence/film-pb-1-arnes-log-20261126/extraer_log_estado.py
OUT=reports/evidence/logs-arnes-todos
MARCADORES='AVIMMGR|MP4IFO|XAVCIFO|MMGR_ACSR|AviSeqPlay|SetLoadInfo|LoadSub|LoadExec|CreateAndLoad|StillCache|CheckMSId|Salvage|Load OK|LoadOK|Load Success'
mkdir -p "$OUT"

una() {
  local zst=$1 perfil out log mk
  perfil=$(basename "$(dirname "$zst")")
  out="$OUT/$perfil"
  log="$out.log.txt"
  mk="$out.markers.txt"
  if ! zstd -dc "$zst" 2>/dev/null | python3 "$SRC" "$log" >"$out.extract.txt" 2>&1; then
    echo "$perfil SIN-EXTRACCION" >>"$OUT/_estado.txt"
    return
  fi
  # segunda pasada: lineas con marcador aunque no lleven tag reconocido
  zstd -dc "$zst" 2>/dev/null | python3 -c '
import re, sys
pat = re.compile(sys.argv[1].encode())
vistos = set()
buf = b""
def emitir(b):
    for trozo in re.split(rb"[\r\n\x00]+", b):
        if len(trozo) < 8 or len(trozo) > 400:
            continue
        if not pat.search(trozo):
            continue
        s = bytes(c for c in trozo if 32 <= c < 127 or c == 9).strip()
        if len(s) < 8 or s in vistos:
            continue
        vistos.add(s)
        sys.stdout.buffer.write(s + b"\n")
for chunk in iter(lambda: sys.stdin.buffer.read(1 << 20), b""):
    buf = buf[-8192:] + chunk
    emitir(buf)
' "$MARCADORES" >"$mk" 2>/dev/null
  echo "$perfil OK $(wc -l <"$log") $(wc -l <"$mk")" >>"$OUT/_estado.txt"
}

export -f una
export OUT SRC MARCADORES
: >"$OUT/_estado.txt"
ls analysis/gui/g22/harness/live/*/estado.zst | xargs -P 6 -I{} bash -c 'una "$@"' _ {}
echo "=== FIN $(date -Is) ==="
wc -l <"$OUT/_estado.txt" | xargs echo "perfiles procesados:"
