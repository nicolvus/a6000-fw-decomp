#!/bin/bash
# Sondeo SWD de solo lectura mientras el usuario enciende la cámara; para al obtener el volcado del cargador.
D=$(cd "$(dirname "$0")" && pwd); t0=$(date +%s); n=0; last=""
while [ $(( $(date +%s)-t0 )) -lt 900 ]; do
  n=$((n+1)); rm -f $D/say.tmp
  LOGF=$D/say.tmp OUTF=$D/esram-0xc0000000.bin timeout 120 openocd -f $D/postfail_l2.cfg > $D/openocd-poll.out 2>&1
  if [ -s $D/say.tmp ]; then
    st="t=$(( $(date +%s)-t0 ))s usb=$(lsusb | grep -o '054c:[0-9a-f]*' | tr '\n' ' ') $(grep -E '^(pc|cpsr)=|ERROR|PC ' $D/say.tmp | tr '\n' ' ' | cut -c1-160)"
    { echo "== intento $n $st"; cat $D/say.tmp; } >> $D/poll.log
    [ "$st" != "$last" ] && echo "$st"; last="$st"
    grep -q "dump ok" $D/say.tmp && { echo "VOLCADO OK"; exit 0; }
  fi
  sleep 1
done
echo "fin sin volcado del cargador ($n intentos)"
