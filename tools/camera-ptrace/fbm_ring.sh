#!/bin/sh
# Deposita una línea en el anillo del monitor EX-PC del proceso MPR (im.elf) de la cámara, sin flashear nada.
#
#   sh fbm_ring.sh "FBM View"            # ejecuta la línea en la consola de FBM de la cámara
#   sh fbm_ring.sh "FBM InitB 6 3"
#   sh fbm_ring.sh                       # sólo muestra el estado del anillo
#
# Necesita root y /tmp/ptcall (tools/camera-ptrace/ptcall.c, ARM EABI estático: sh tools/camera-ptrace/build.sh).
# Formato del anillo: reports/film-pb-1-sub-consola-fbm-anillo-20261127.md §1.
#   X = *(u32*)(libmpr+0xA4FD88)      [X]=A índice de lectura  [X+4]=B índice de escritura
#   datos = X+0x10, 0x400 B, un hueco libre; línea terminada en CR (0x0D)
set -u
PT=${PT:-/tmp/ptcall}
LINEA=${1:-}

PID=$(pidof im.elf 2>/dev/null | cut -d' ' -f1)
[ -n "${PID:-}" ] || { echo "no encuentro im.elf (¿el MPR está arrancado?)"; exit 1; }
MAPS=/proc/$PID/maps
[ -r "$MAPS" ] || { echo "no puedo leer $MAPS (¿root?)"; exit 1; }
BASE=$(awk '/libmpr\.so/ && /r-xp/ { print "0x" substr($1,1,8); exit }' "$MAPS")
[ -n "${BASE:-}" ] || { echo "libmpr.so no está mapeado en $PID"; exit 1; }

# peek DIR LEN -> bytes en hex separados por espacio
peek() { "$PT" "$PID" 0 peek "$1" "$2" | sed 's/^[^:]*: *//; s/ *$//'; }
# hexd de una cadena (añade CR) -> "46 42 4d 20 ..."
hexd() { printf '%s\r' "$1" | od -An -v -tx1 | tr -s ' \n' '  ' | sed 's/^ *//; s/ *$//'; }
# u32 en hex a partir de 4 bytes en orden little endian
le32() { awk '{print $4 $3 $2 $1}'; }

XH=$(peek "$((BASE + 0xA4FD88))" 4 | le32)
[ -n "$XH" ] || { echo "no pude leer el descriptor en $BASE+0xA4FD88"; exit 1; }
X=$((0x$XH))
echo "libmpr base=$BASE  anillo X=0x$(printf %08x "$X")  (buf=0x$(printf %08x $((X + 0x10))) )"

HDR=$(peek "$X" 8)
A=$((0x$(echo "$HDR" | awk '{print $4 $3 $2 $1}')))
B=$((0x$(echo "$HDR" | awk '{print $8 $7 $6 $5}')))
LIBRES=$(( (A - B - 1) & 0x3ff ))
echo "A(lectura)=$A  B(escritura)=$B  libres=$LIBRES de 0x3ff"

[ -n "$LINEA" ] || exit 0
BYTES=$(hexd "$LINEA")
N=$(echo "$BYTES" | wc -w)
if [ "$N" -lt 1 ] || [ "$N" -gt 1000 ]; then echo "longitud no admitida: $N B"; exit 1; fi
if [ "$LIBRES" -lt "$N" ]; then echo "no caben $N B (libres $LIBRES)"; exit 1; fi

# 1) los bytes, desde X+0x10+B, partiendo en dos si el anillo da la vuelta
TRAMO1=$((0x400 - B)); [ "$TRAMO1" -gt "$N" ] && TRAMO1=$N
echo "depositando $N B en 0x$(printf %08x $((X + 0x10 + B))) (tramo1=$TRAMO1)"
L1=""; L2=""; I=0
for BY in $BYTES; do
    I=$((I + 1))
    if [ "$I" -le "$TRAMO1" ]; then L1="$L1 $BY"; else L2="$L2 $BY"; fi
done
[ -n "$L1" ] && { "$PT" "$PID" 0 poke "$((X + 0x10 + B))" $L1 || exit 1; }
[ -n "$L2" ] && { "$PT" "$PID" 0 poke "$((X + 0x10))" $L2 || exit 1; }

# 2) publicar el índice de escritura (un solo store: el monitor ve la línea entera de golpe)
NB=$(( (B + N) & 0x3ff ))
NH=$(printf '%02x %02x %02x %02x' $((NB & 0xff)) $(((NB >> 8) & 0xff)) $(((NB >> 16) & 0xff)) $(((NB >> 24) & 0xff)))
"$PT" "$PID" 0 poke "$((X + 4))" $NH || exit 1
echo "B publicado: $B -> $NB. La línea «$LINEA» queda para el monitor (consume en ~1 s)."
