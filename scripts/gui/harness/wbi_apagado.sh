#!/bin/sh
# WBI en el arnés (FILM-PB-1): emula el apagado «warm» de im.elf de punta a punta y deja la salida en SALIDA/.
# El shim hace de upm.ko: inyecta en la cola 0x94016a la cadena que en la cámara manda upm
#   0x920143 (UPM_CMD_OFF, w1 = factor; 0x27 = tipo 8/modo 2, 7 = interruptor) → inact_all
#   0x92014B                                                                     → sus_all_i (incluye SyncAndroid_sus)
#   0x92014D                                                                     → sus_all_u
#   0x92014F                                                                     → im.elf abre /sys/power/state y escribe warm|mem (capturado en /cam/tmp/power_state)
# ANDROIDFS=real: /android/data y data/{data,system} son tmpfs de verdad (estado de la cámara al apagar), mount de /dev/ramN → tmpfs, umount real.
# HOLD=1: dos procesos reales sujetan ficheros del vfat /android/data (como zygote/dhcpcd en la cámara) y el EBUSY sale solo, sin imponerlo.
# Uso: [BUSY=1|HOLD=1] wbi_apagado.sh DIR_TRABAJO SALIDA [factor_hex=27]
# Límite: no es el kernel de Sony: no fabrica la imagen (warm.c) ni reanuda; solo la parte de usuario hasta el write.
set -e
W=$1; O=$2; F=${3:-27}; HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$O"
# WBICHAIN encadena las fases por eventos del registro de im.elf (sin tiempos fijos). BUSY=1: umount(/android/data) devuelve EBUSY como en la cámara (dato medido).
HARNESS_OUT=$O SHIMENV="WAIT=${WAIT:-420} CVWAIT=0 ANDROIDFS=real FULLLOG=1 SYNCMBX=94016a SELFQ='*' DEVREADWAKE=1 SKIPSUS=libObj.so@7d6d90,libInfraHdmi.so@34e80,libUsbControl.so@10d20 ${BUSY:+ANDROIDBUSY=1} ${HOLD:+ANDROIDHOLD=1} ${SHIMEXTRA} WBICHAIN=$F WBIAT=60" \
  python3 "$HERE/run.py" "$W" "$HERE/im.sh" "${SECS:-480}" > "$O/run.txt" 2>&1
grep -a -E "POWERSTATE escrito|WBIFS" "$O/run.txt" || true
