#!/bin/sh
# Bucle de senser_sfr_scan.py: tras cada fallo espera a que la cámara vuelva (almacenamiento masivo) y reanuda. Máximo 40 intentos.
# Uso: senser_sfr_scan.sh OUTDIR [INICIO] [FIN]
cd "$(dirname "$0")/.."
PY=${PMCA_PY:-$HOME/.local/share/pmca-venv/bin/python}
i=0
while [ $i -lt 40 ] && [ ! -f "$1/.fin" ]; do
  i=$((i+1))
  for t in $(seq 1 40); do lsusb | grep -q "054c:07c4" && break; sleep 5; done
  "$PY" -W ignore scripts/senser_sfr_scan.py "$@" 2>&1 | grep -E "^(FALLO|CUELGUE|FIN|0x)"
  sleep 20
done
python3 -c "import json;s=json.load(open('$1/state.json'));print('ok=%d bad=%d intentos=$i'%(len(s['ok']),len(s['bad'])))"
