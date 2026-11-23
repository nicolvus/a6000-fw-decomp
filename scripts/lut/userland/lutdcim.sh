#!/bin/sh
# G91 — en la cámara (telnet): aplica un .cube completo a todos los JPEG de DCIM que aún no
# tengan copia en LUT_OUT. Los originales no se tocan.
# Uso: sh lutdcim.sh [LUT/LUT1.cube] [calidad]      (rutas relativas a la SD)
SD=/android/mnt/sdcard
CUBE=$SD/${1:-LUT/LUT1.cube}
Q=${2:-98}
OUT=$SD/LUT_OUT/$(basename "$CUBE" .cube)
BIN=/tmp/lutjpg
[ -x $BIN ] || { cp $SD/LUT/lutjpg $BIN && chmod 755 $BIN; } || exit 1
mkdir -p "$OUT" || exit 1
n=0
for f in $SD/DCIM/*/*.JPG; do
    [ -f "$f" ] || continue
    o=$OUT/$(basename "$(dirname "$f")")_$(basename "$f")   # 100MSDCF_DSC01234.JPG: sin choques entre carpetas
    [ -f "$o" ] && continue
    $BIN -q $Q "$CUBE" "$f" "$o" && n=$((n + 1)) || echo "fallo: $f"
done
echo "$n fotos -> $OUT"
