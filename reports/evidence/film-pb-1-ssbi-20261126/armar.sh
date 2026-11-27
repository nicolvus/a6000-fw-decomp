#!/usr/bin/env bash
# Arma la captura interruptor→warm con el break.cfg verificado (el que convirtió mem→warm).
# Uso: bash armar.sh   → imprime ARMED y deja openocd vigilando ~340 s, o sale ≠0.
set -u
CFG=${1:-break-off.cfg}
D=/tmp/a6000-interruptor-warm-verificado
cd "$D"
pgrep -x openocd >/dev/null && { echo "ERROR openocd ya en marcha (PID $(pgrep -x openocd))"; exit 2; }
[ "$CFG" = break.cfg ] && grep -q 'read_reg $b 4' break.cfg && { echo "ERROR break.cfg contiene la comprobación de búfer que bloquea"; exit 2; }
rm -f fin-captura
n=$(ls swd-*.log 2>/dev/null | wc -l)
for intento in 1 2 3; do
    [ -s swd.log ] && mv swd.log "swd-$((n++)).log"
    (nohup openocd -f "$CFG" > swd.log 2>&1 &)
    for _ in $(seq 1 25); do
        grep -qE 'ARMED|FIN|Error' swd.log && break
        sleep 1
    done
    if grep -q ARMED swd.log && pgrep -x openocd >/dev/null; then
        grep ARMED swd.log; exit 0
    fi
    grep -q 'cannot read IDR' swd.log && { echo "ERROR sin SWD: ¿cámara apagada?"; exit 3; }
    echo "intento $intento falló: $(grep -E 'INTERRUPTED|Error|FIN' swd.log | tr '\n' ' ')"
    while pgrep -x openocd >/dev/null; do sleep 1; done
    sleep 2
done
exit 1
