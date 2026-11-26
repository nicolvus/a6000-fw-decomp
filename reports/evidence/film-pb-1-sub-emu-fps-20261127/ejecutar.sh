#!/bin/sh
# Reproduce la evidencia de reports/film-pb-1-sub-emu-fps-20261127.md
# Dos corridas por fichero + control positivo de los hooks de E/S + MD5.
set -e
cd "$(dirname "$0")/../../.."
LIB=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so
E=reports/evidence/film-pb-1-sub-emu-fps-20261127

for f in orig198 conv198-25p; do
  for r in 1 2; do
    python3 "$E/emu_fps.py" --lib "$LIB" --file "/tmp/$f.mp4" > "$E/transcripcion-$f-r$r.txt"
  done
done
python3 "$E/emu_fps.py" --lib "$LIB" --file /tmp/orig198.mp4 --control > "$E/control-es.txt"
python3 "$E/emu_fps.py" --lib "$LIB" --file /tmp/orig198.mp4 --wrapper > "$E/transcripcion-orig198-wrapper6E8430.txt"

sha256sum "$LIB" > "$E/libmpr-sha256.txt"
md5sum "$E"/transcripcion-*.txt > "$E/md5.txt"
cat "$E/md5.txt"
