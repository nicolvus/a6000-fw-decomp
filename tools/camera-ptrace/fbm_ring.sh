#!/bin/sh
# Deposita una línea en el anillo del monitor EX-PC del proceso MPR (im.elf) de la cámara, sin flashear nada.
#
#   sh fbm_ring.sh "FBM View"            # ejecuta la línea en la consola de FBM de la cámara
#   sh fbm_ring.sh "FBM InitB 6 3"
#   sh fbm_ring.sh                       # sólo muestra el estado del anillo (X, A, B y hueco libre)
#
# Necesita root, /tmp/ptcall (tools/camera-ptrace/ptcall.c, ARM EABI estático: sh tools/camera-ptrace/build.sh)
# y, para la cámara, /proc montado (para sacar la base de libmpr.so). Sin dependencias de awk/sed/od/cut:
# todo el trabajo de bytes lo hace `ptcall ... ring`, que además publica B en un solo store.
#
# Formato del anillo (reports/film-pb-1-sub-consola-fbm-anillo-20261127.md §1):
#   X = *(u32*)(libmpr+0xA4FD88)   [X]=A índice de lectura   [X+4]=B índice de escritura
#   datos = X+0x10, 0x400 B, un hueco siempre libre; línea terminada en CR (0x0D)
set -u
PT=${PT:-/tmp/ptcall}          # ruta de ptcall
LINEA=${1:-}                   # línea a depositar (sin CR; lo pone ptcall)
PID=${PID:-}                   # proceso (def. pidof im.elf)
TID=${TID:-0}                  # hilo al que engancharse (0 = el principal)
BASE=${BASE:-}                 # VA de libmpr.so (si no se pasa, se lee de /proc/PID/maps)

[ -x "$PT" ] || { echo "falta $PT (sh tools/camera-ptrace/build.sh)"; exit 1; }
if [ -z "${PID:-}" ]; then
    PID=$(pidof im.elf 2>/dev/null)
    PID=${PID%% *}
fi
[ -n "${PID:-}" ] || { echo "no encuentro im.elf (¿el MPR está arrancado?)"; exit 1; }

if [ -z "${BASE:-}" ]; then
    MAPS=/proc/$PID/maps
    [ -r "$MAPS" ] || { echo "no puedo leer $MAPS (¿root?); si no hay /proc pasa BASE=0x..."; exit 1; }
    # /proc/PID/maps va ordenado por dirección: el PRIMER mapeo de libmpr.so es su base de carga
    # (offset 0). Si el binario estuviera precargado en otro sitio, se comprueba a ojo con el eco.
    while IFS= read -r l; do
        case "$l" in
            *libmpr.so) set -- $l; BASE="0x${1%%-*}"; echo "maps: $l" >&2; break ;;
        esac
    done < "$MAPS"
    [ -n "${BASE:-}" ] || { echo "libmpr.so no está mapeado en $PID"; exit 1; }
fi

if [ -z "${LINEA:-}" ]; then            # estado: A, B y hueco libre (lo imprime ptcall ring con línea vacía)
    exec "$PT" "$PID" "$TID" ring "$BASE" ""
fi
exec "$PT" "$PID" "$TID" ring "$BASE" "$LINEA"
