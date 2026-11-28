#!/bin/sh
# WBI en el arnés (FILM-PB-1): emula el apagado «warm» de im.elf de punta a punta y deja la salida en SALIDA/.
# El shim hace de upm.ko: inyecta en la cola 0x94016a la cadena que en la cámara manda upm
#   0x920143 (UPM_CMD_OFF, w1 = factor; 0x27 = tipo 8/modo 2, 7 = interruptor) → inact_all
#   0x92014B                                                                     → sus_all_i (incluye SyncAndroid_sus)
#   0x92014D                                                                     → sus_all_u
#   0x92014F                                                                     → im.elf abre /sys/power/state y escribe warm|mem (capturado en /cam/tmp/power_state)
# ANDROIDFS=real: /android/data y data/{data,system} son tmpfs de verdad (estado de la cámara al apagar), mount de /dev/ramN → tmpfs, umount real.
# Uso: wbi_apagado.sh DIR_TRABAJO SALIDA [factor_hex=27]
# Límite: no es el kernel de Sony: no fabrica la imagen (warm.c) ni reanuda; solo la parte de usuario hasta el write.
set -e
W=$1; O=$2; F=${3:-27}; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$O"
# Tiempos en hex (s desde el arranque de im.elf); cada fase espera a la anterior: ajustar si el TCG va más lento.
HARNESS_OUT=$O SHIMENV="WAIT=${WAIT:-700} CVWAIT=0 ANDROIDFS=real FULLLOG=1 SYNCMBX=94016a SELFQ='*' DEVREADWAKE=1 SKIPSUS=libObj.so@7d6d90,libInfraHdmi.so@34e80,libUsbControl.so@10d20 ${SHIMEXTRA} INJECT='3c@94016a:920143:$F;50@94016a:92014b;${T4D:-78}@94016a:92014d;${T4F:-1f4}@94016a:92014f:0'" \
  python3 "$HERE/run.py" "$W" "$HERE/im.sh" "${SECS:-760}" > "$O/run.txt" 2>&1
grep -a -E "POWERSTATE escrito|WBIFS" "$O/run.txt" || true
