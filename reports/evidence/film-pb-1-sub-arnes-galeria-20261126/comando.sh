#!/bin/sh
# FILM-PB-1 / sub-arnés-galeria — intento de reproducir 0xB0100002 en el arnés QEMU (sin cámara).
# Ejecutar desde la raíz del repo.  Nada de esto toca la cámara ni flashea: todo ocurre en qemu-system-arm.
# Sesión medida: 25-11-2026 22:30–22:47 (-03).  Perfil `arnes2`, puerto 8612, SD emulada propia en $H/A6000-SD.
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd)   # reports/evidence/<x>/ → raíz
cd "$REPO"
H=${H:-/tmp/fpb1/home}
G=reports/evidence/film-pb-1-sub-arnes-galeria-20261126/galeria.py

# 0) Tarjeta emulada: un clip real (fuera del repo) + el índice AV sintético del informe sub-avin-20261127
mkdir -p "$H/A6000-SD/DCIM/100MSDCF" "$H/A6000-SD/MP_ROOT/100ANV01" "$H/A6000-SD/AVF_INFO"
cp -n /home/nicolas/Documents/a6000/MAH04198.MP4            "$H/A6000-SD/MP_ROOT/100ANV01/"
cp -n reports/evidence/film-pb-1-sub-avin-20261127/AVIN0001_sintetico.INP "$H/A6000-SD/AVF_INFO/AVIN0001.INP"

# 1) Arnés (en una terminal; arranque en frío ≈ 100–160 s hasta la primera pantalla)
#    SD_ESTRUCTURA=1 → sd_image.py crea AVF_INFO/ y PRIVATE/M4ROOT/{CLIP,SUB,THMBNL,GENERAL} (opt-in documentado)
#    TRACELIB/TRACEFN2/TRACEDEREF/TRACEREP → trampas UDF en libmpr (0x5BAD00, 0x6E8430, 0x6E80A4, 0x61A8F0, 0x608698)
#    WAITLOG=1000 → reenvía a live/<perfil>/shim.log solo las esperas >1 s y todas las líneas [shim] (TRACE/DEREF)
#    LOGMARK → además las trazas del firmware cuyo texto contenga «OPENHOT» o «viewUnified» (apertura/cierre de vistas)
HOME=$H SD_ESTRUCTURA=1 LIVE_REINTENTOS=1 \
SHIMEXTRA='WAITLOG=1000 LOGMARK=OPENHOT,viewUnified TRACELIB=libmpr.so TRACEFN2=5bad00,6e8430,6e80a4,61a8f0,608698 TRACEDEREF=d0:0:7 TRACEREP=1 TRACEMAX=4' \
.venv/bin/python3 scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir arnes2 --puerto 8612

# 2) Galería (en otra terminal, con la UI ya dibujada)
.venv/bin/python3 $G --puerto=8612 estado
.venv/bin/python3 $G --puerto=8612 captura /tmp/fpb1/00-stlrec.png
.venv/bin/python3 $G --puerto=8612 tecla reproduccion            # clave 0x1f7, índice 0x1f (KEY_TACT_PLAY)
.venv/bin/python3 $G --puerto=8612 linea "O view/INDEX_PLAYBACK 0"
.venv/bin/python3 $G --puerto=8612 captura /tmp/fpb1/01-index-pb.png
.venv/bin/python3 $G --puerto=8612 linea "O view/SINGLEPB 0"
.venv/bin/python3 $G --puerto=8612 captura /tmp/fpb1/02-singlepb.png

# 3) Lectura del resultado (lo que hay que mirar)
grep -a "TRACE \|DEREF " analysis/gui/g22/harness/live/arnes2/shim.log | tail -40
grep -ao "TRACE [0-9a-f]*" analysis/gui/g22/harness/live/arnes2/shim.log | sort | uniq -c   # recuento por punto
grep -a "LOGMARK" analysis/gui/g22/harness/live/arnes2/shim.log | tail -20                  # Vn B/E = vista abre/cierra

# 4) Cierre
curl -s -X POST http://127.0.0.1:8612/salir
