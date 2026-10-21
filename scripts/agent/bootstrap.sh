#!/usr/bin/env bash
# Reconstruye desde cero lo que no está en Git (firmware, venv, REA, Ghidra, JDK, av-cam.bin).
# Idempotente: cada paso se salta si ya está hecho. Uso: scripts/agent/bootstrap.sh [--dry-run]
# Se detiene (exit != 0) en el primer fallo; el paso fallido se imprime con "FALLO:".
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
DMG_URL='https://support.d-imaging.sony.co.jp/download/NEX/AcicwqgUEQ/Update_ILCE6000V321.dmg?fm=am'
DMG=firmware/original/Update_ILCE6000V321.dmg
DMG_SHA=844349ff7edddc294c0fddd90a454848eeda8987b6bf043c9757982b3a42ba3e
FDAT=firmware/extracted/fw321/firmware.fdat
FDAT_SHA=603b42ec9d2dd66b91e38c15a6a23e860fb8af46a072050903506672036f0f90
AVCAM_SRC=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin
step() { echo "== $*"; }
run() { if [ $DRY = 1 ]; then echo "   [dry] $*"; else "$@"; fi; }
sha_ok() { [ -f "$1" ] && [ "$(sha256sum "$1" | cut -d' ' -f1)" = "$2" ]; }
trap 'echo "FALLO: paso anterior (ver docs/agent/bootstrap-desde-cero.md § Límites)"' ERR

step "0. Requisitos"
for c in git python3 curl 7z node npm unzip tar; do command -v $c >/dev/null || { echo "falta $c (instálalo y reintenta)"; exit 1; }; done

step "1. Firmware 3.21 (.dmg)"
if sha_ok $DMG $DMG_SHA; then echo "   ya verificado"; else
  run mkdir -p firmware/original; run curl -fL -o $DMG "$DMG_URL"
  [ $DRY = 1 ] || sha_ok $DMG $DMG_SHA || { echo "SHA-256 del .dmg distinto: Sony cambió el archivo; NO continuar sin revisar"; exit 1; }
fi

step "2. Entornos Python (.venv del proyecto y venv de fwtool)"
[ -d .venv ] || { run python3 -m venv .venv; run .venv/bin/pip install -q pytest ruff mypy pyyaml capstone unicorn; }
[ -d .venv-fwtool ] || { run python3 -m venv .venv-fwtool; run .venv-fwtool/bin/pip install -q -r references/fwtool/requirements.txt; }

step "3. Desempaquetado con fwtool"
if sha_ok $FDAT $FDAT_SHA; then echo "   ya extraído y verificado"; else
  run 7z x -y $DMG -ofirmware/extracted/updater >/dev/null
  run .venv-fwtool/bin/python references/fwtool/fwtool.py unpack \
    -f firmware/extracted/updater/Update_ILCE6000V321/Resources/FirmwareUpdater.app/Contents/Resources/FirmwareData_ILCE6000V321.dat \
    -o firmware/extracted/fw321 || echo "AVISO: fwtool falló; usar el procedimiento alterno de docs/firmware-analysis.md y reintentar"
  [ $DRY = 1 ] || sha_ok $FDAT $FDAT_SHA || { echo "firmware.fdat no coincide (o falta): revisar paso 3"; exit 1; }
fi

step "4. Inventario y atlas ELF"
[ -f reports/inventory.json ] || run .venv/bin/python -m src.inventory firmware/extracted/fw321 reports/inventory.json
run .venv/bin/python -m src.atlas

step "5. REA, Ghidra y JDK (versiones fijadas en reports/rea-provider-downloads.json)"
[ -d tools/rea/node_modules ] || run bash -c 'cd tools/rea && npm ci'
mkdir -p tools/providers
if [ ! -d tools/providers/ghidra_12.1.4_PUBLIC ] || [ ! -d tools/providers/jdk-21.0.12.1+1 ]; then
  run .venv/bin/python - <<'PY'
import json, hashlib, urllib.request, zipfile, tarfile, pathlib
d = {x["name"]: x for x in json.load(open("reports/rea-provider-downloads.json"))}
p = pathlib.Path("tools/providers"); p.mkdir(exist_ok=True)
for name, x in d.items():
    f = p / name
    if not f.exists(): urllib.request.urlretrieve(x["url"], f)
    assert hashlib.sha256(f.read_bytes()).hexdigest() == x["expected"], f"hash {name}"
    (zipfile.ZipFile(f).extractall(p) if name.endswith(".zip") else tarfile.open(f).extractall(p))
PY
fi
run ./scripts/rea doctor --client codex --provider ghidra --json >/dev/null || echo "AVISO: rea doctor con problemas (ver docs/STATE.md)"

step "6. av-cam.bin para REA"
run mkdir -p analysis/rea-independent/input
[ -f analysis/rea-independent/input/av-cam.bin ] || run cp $AVCAM_SRC analysis/rea-independent/input/av-cam.bin

step "7. .mcp.json (directorio padre del repo, rutas absolutas del clon)"
ROOT=$(pwd); MCP="$ROOT/../.mcp.json"
if [ ! -f "$MCP" ] && [ $DRY = 0 ]; then
cat > "$MCP" <<JSON
{"mcpServers":{
 "sony-a6000-knowledge":{"command":"$ROOT/.venv/bin/python3","args":["$ROOT/scripts/knowledge/mcp_server.py"],"env":{"SONY_A6000_KB_ROOT":"$ROOT"}},
 "rea":{"command":"$ROOT/scripts/rea","args":["mcp"],"env":{"REA_GHIDRA_STARTUP_TIMEOUT_MS":"900000","GHIDRA_MAXMEM":"3G"}}}}
JSON
else echo "   existe o dry-run"; fi

step "8. Grafo de conocimiento y verificación"
for s in index_docs build_graph; do run .venv/bin/python scripts/knowledge/$s.py >/dev/null; done
run .venv/bin/python scripts/agent/check_env.py --sha || true
run .venv/bin/python -m pytest tests -q -x || echo "AVISO: tests con fallos; anotar cuáles antes de tocar nada"
echo "LISTO. Siguiente: leer knowledge/CURRENT.md y docs/agent/bootstrap-desde-cero.md"
