#!/bin/sh
# Reproducción completa de la parte DATOS (volumen + AVF_INFO) y de la corrida del arnés.
# Perfil de arnés: analysis/gui/g22/harness/live/davf2 (el nombre debe dejar el camino de mon.sock < 108 B).
# La tarjeta del invitado sale de $HOME/A6000-SD (sd_emu.SD_DEFECTO); no hace falta tocar HOME.
set -e
cd "$(dirname "$0")/../../../.."                     # raíz del repo
E=reports/evidence/film-pb-1-sub-arnes-datos-avf-20261126

# 1) tarjeta: MP4 en la ruta de la plantilla del binario + AVF_INFO/AVIN0001.INP con la rejilla 0x80 B
.venv/bin/python3 "$E/gen_tarjeta.py" $HOME/A6000-SD --extra-dir MP_ROOT/103ANV01

# 1b) copia del clip en la ruta XAVC S (para que esa carpeta también tenga un clip)
cp $HOME/A6000-SD/MP_ROOT/100ANV01/MAH04198.MP4 $HOME/A6000-SD/PRIVATE/M4ROOT/CLIP/C0001.MP4

# 2) imagen FAT32 (la MISMA función que usa live.py: cabeza de 4 GiB)
.venv/bin/python3 - <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, 'scripts/gui/harness')
import sd_image
print('sectores', sd_image.construye(Path('~/A6000-SD').expanduser(), Path('/tmp/fpb1-datos2/img/sd.head'), 4.0, completa=False))
PY

# 3) copia extraída de la imagen + auditoría (0 avisos)
mkdir -p /tmp/fpb1-datos2/copia
MTOOLS_SKIP_CHECK=1 mcopy -i /tmp/fpb1-datos2/img/sd.head -s -m -Q \
    ::/AVF_INFO ::/MP_ROOT ::/DCIM ::/PRIVATE /tmp/fpb1-datos2/copia/
.venv/bin/python3 "$E/audita_tarjeta_copia.py" /tmp/fpb1-datos2/copia

# 4) arnés con la SD emulada y trampas en la cadena del IFO MP4 (o: sh scripts/gui/harness/estable.sh davf5 live)
LIVE_REINTENTOS=1 LIVE_ARRANQUE_MAX=900 \
SHIMEXTRA='WAITLOG=6000 WLALL=1 TRACELIB=libmpr.so TRACEFN2=5bad00,6e80a4,67ca6c,67c8cc,698fb8,627bec,625c4c,626db8 TRACEMAX=2 TRACEREP=1' \
.venv/bin/python3 scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir davf5 --puerto 8627

# Con la UI arriba (≈2–6 min):  curl -s -X POST --data '{"k":"reproduccion","v":1,"i":0}' http://127.0.0.1:8624/tecla
# Volcado de /sd.img del invitado: curl -s -X POST http://127.0.0.1:8624/sd-volcado   (→ live/davf2/sd-volcado.img)
