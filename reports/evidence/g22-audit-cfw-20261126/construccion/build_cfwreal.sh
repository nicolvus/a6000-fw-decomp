#!/usr/bin/env bash
# G22-AUDIT-CFW — CFW real instalable construido offline (sin cámara, sin flasheo).
export LC_ALL=C LANG=C
# /usr: string_english.uxc, id 0xE001 «Extra fine» → «Extra Fine» (misma longitud: diff mínimo).
set -euo pipefail
REPO=/home/nicolas/h-cfwreal
PY=/home/nicolas/a6000-arnes/.venv/bin/python
W=/home/nicolas/cfwbuild
N15_ORIG="$REPO/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15"
BASE_TAR="$REPO/firmware/extracted/fw321/firmware.tar"
S1="$REPO/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/share/app/string_english.uxc"
cd "$REPO"

echo "== 1. /usr: string_english.uxc 0xE001 'Extra fine' -> 'Extra Fine'"
$PY scripts/gui/uxc_strings.py set "$S1" 0xE001 'Extra Fine' "$W/pkg/share/app/string_english.uxc"
$PY - "$S1" "$W/pkg/share/app/string_english.uxc" <<'EOF'
import hashlib, json, sys
from pathlib import Path
viejo, nuevo = Path(sys.argv[1]).read_bytes(), Path(sys.argv[2]).read_bytes()
assert len(viejo) == len(nuevo), (len(viejo), len(nuevo))
dist = [i for i in range(len(viejo)) if viejo[i] != nuevo[i]]
print(f"   {len(nuevo)} B, {len(dist)} bytes distintos en {dist[:8]}")
man = {"version": "3.39",
       "parcheados": {"share/app/string_english.uxc": hashlib.sha256(nuevo).hexdigest()},
       "recursos": [{"fichero": "share/app/string_english.uxc", "etiqueta": "Extra Fine"}],
       "nota": "CFW de auditoría: un solo cambio de cadena en /usr, misma longitud (diff de 1 byte)"}
Path("/home/nicolas/cfwbuild/pkg/MANIFEST.json").write_text(json.dumps(man, indent=1))
EOF

echo "== 2. nflasha15 recompuesto (debugfs + TPZL)"
time $PY scripts/gui/build_nflasha15.py "$N15_ORIG" "$W/pkg" "$W/nflasha15-extrafine.bin"

echo "== 3a. .dat CON el WBI de Sony (acoplamiento roto: el TOC se mueve y la instantánea es la de Sony)"
time $PY scripts/gui/build_package_nflasha15.py "$W/nflasha15-extrafine.bin" "$W/out-conwbi" \
     --base-tar "$BASE_TAR" --version 3.39

echo "== 3b. .dat SIN el WBI (bien formado: arranque en frío, G11 §11)"
time $PY scripts/gui/build_package_nflasha15.py "$W/nflasha15-extrafine.bin" "$W/out-sinwbi" \
     --base-tar "$BASE_TAR" --version 3.40 --sin-wbi

echo "== 4. huellas"
sha256sum "$W"/out-conwbi/package-3.39/firmware_packed.dat "$W"/out-sinwbi/package-3.40/firmware_packed.dat
echo "== FIN"
