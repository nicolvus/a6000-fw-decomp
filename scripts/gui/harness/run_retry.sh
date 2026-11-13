#!/bin/sh
# uso: run_retry.sh etiqueta "SHIMENV…"; repite (hasta 6) si el arranque cae por el SIGSEGV intermitente y no llega a «toActive»; deja /tmp/g_<etiqueta>.{out,log} y echo done al final
# Cada etiqueta usa su propio HARNESS_OUT (analysis/gui/g22/harness/runs/<etiqueta>), así que varias etiquetas pueden correr en paralelo.
cd "$(dirname "$0")/../../.."  # raíz del repo
O=analysis/gui/g22/harness/runs/$1; mkdir -p "$O"
for i in 1 2 3 4 5 6; do
  rm -f "$O/guest.log"
  HARNESS_OUT="$O" SHIMENV="$2" timeout 400 python3 scripts/gui/harness/run.py analysis/gui/g22/harness scripts/gui/harness/im.sh 250 > /tmp/g_$1.out 2>&1
  grep -aq "toActive" "$O/guest.log" 2>/dev/null && break
done
cp "$O/guest.log" /tmp/g_$1.log; cp "$O/gpu.txt" /tmp/g_$1_gpu.txt 2>/dev/null
echo done >> /tmp/g_$1.out
