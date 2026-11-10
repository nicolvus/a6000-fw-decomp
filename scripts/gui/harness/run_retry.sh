#!/bin/sh
# uso: run_retry.sh etiqueta "SHIMENV…"; repite (hasta 6) si el arranque cae por el SIGSEGV intermitente y no llega a «toActive»; deja /tmp/g_<etiqueta>.{out,log} y echo done al final
cd "$(dirname "$0")/../../.."  # raíz del repo
for i in 1 2 3 4 5 6; do
  SHIMENV="$2" timeout 400 python3 scripts/gui/harness/run.py analysis/gui/g22/harness scripts/gui/harness/im.sh 250 > /tmp/g_$1.out 2>&1
  n=$(wc -l < analysis/gui/g22/harness/guest.log)
  grep -aq "toActive" analysis/gui/g22/harness/guest.log && break
done
cp analysis/gui/g22/harness/guest.log /tmp/g_$1.log; cp analysis/gui/g22/harness/gpu.txt /tmp/g_$1_gpu.txt 2>/dev/null
echo done >> /tmp/g_$1.out
