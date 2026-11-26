#!/usr/bin/env bash
# Variante DELIBERADAMENTE MAL: /usr recompuesto (TOC movido) y el WBI de Sony sin invalidar.
set -euo pipefail
export LC_ALL=C LANG=C
REPO=/home/nicolas/h-cfwreal
PY=/home/nicolas/a6000-arnes/.venv/bin/python
W=/home/nicolas/cfwbuild/tocmovido
N15_ORIG="$REPO/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15"
BASE_TAR="$REPO/firmware/extracted/fw321/firmware.tar"
S="$REPO/firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/share/app/string_vietnamese.uxc"
mkdir -p "$W/pkg/share/app"
cd "$REPO"
# una cadena MÁS LARGA refluye todo el cuerpo de la tabla => decenas de páginas cambian => el bloque crece
$PY scripts/gui/uxc_strings.py set "$S" 0xE001 'Extra fine (CFW G22-AUDIT-CFW)' "$W/pkg/share/app/string_vietnamese.uxc"
$PY - "$W/pkg/share/app/string_vietnamese.uxc" <<'EOF'
import hashlib, json, sys
from pathlib import Path
nuevo = Path(sys.argv[1]).read_bytes()
Path("/home/nicolas/cfwbuild/tocmovido/pkg/MANIFEST.json").write_text(json.dumps({
    "version": "3.41",
    "parcheados": {"share/app/string_vietnamese.uxc": hashlib.sha256(nuevo).hexdigest()},
    "recursos": [{"fichero": "share/app/string_vietnamese.uxc", "etiqueta": "Extra fine (CFW G22-AUDIT-CFW)"}]}, indent=1))
EOF
echo "== nflasha15 (TOC debería moverse)"
$PY scripts/gui/build_nflasha15.py "$N15_ORIG" "$W/pkg" "$W/nflasha15-tocmovido.bin"
$PY - "$N15_ORIG" "$W/nflasha15-tocmovido.bin" <<'EOF'
import sys
sys.path.insert(0, "scripts")
from pathlib import Path
from e25_27 import tpzl
a = tpzl.TpzlImage.parse(Path(sys.argv[1]).read_bytes())
b = tpzl.TpzlImage.parse(Path(sys.argv[2]).read_bytes())
d = [k for k in range(min(len(a.entries), len(b.entries))) if a.entries[k] != b.entries[k]]
print(f"   entradas distintas: {len(d)} (primera {d[0] if d else '-'}) de {len(b.entries)}")
EOF
echo "== .dat CON el WBI de Sony"
$PY scripts/gui/build_package_nflasha15.py "$W/nflasha15-tocmovido.bin" "$W/out" --base-tar "$BASE_TAR" --version 3.41
$PY - <<'EOF'
import hashlib, json
from pathlib import Path
p = Path("/home/nicolas/cfwbuild/tocmovido/out/package-3.41")
sha = hashlib.sha256((p / "share/app/string_vietnamese.uxc").read_bytes()).hexdigest() if (p / "share/app").is_dir() else None
man = json.loads(Path("/home/nicolas/cfwbuild/tocmovido/pkg/MANIFEST.json").read_text())
(p / "declara.json").write_text(json.dumps(man, indent=1))
print("dat", p / "firmware_packed.dat")
EOF
sha256sum "$W"/out/package-3.41/firmware_packed.dat
echo "== FIN"
