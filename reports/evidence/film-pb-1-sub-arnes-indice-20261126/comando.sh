#!/bin/sh
# FILM-PB-1 / sub-arnes-indice — comprobar si el .INP sintetico enumera el clip en el arnes QEMU (sin camara).
# Ejecutar desde la raiz del repo. No toca la camara ni flashea: todo ocurre en qemu-system-arm.
# Sesion: 25-11-2026 23:06-23:45 (-03). Perfil propio `arnes-ind` (no se toca el arnes compartido).
set -e
REPO=$(cd "$(dirname "$0")/../../.." && pwd); cd "$REPO"
H=${H:-/tmp/fpb1/home}          # OJO: sd_emu.raiz_sd() = Path.home()/"A6000-SD"; HOME decide QUE tarjeta se monta

# 0) Tarjeta emulada: el clip (fuera del repo) donde estaba en la tarjeta real (103ANV01) + el .INP nuevo
mkdir -p "$H/A6000-SD/DCIM/100MSDCF" "$H/A6000-SD/MP_ROOT/103ANV01" "$H/A6000-SD/AVF_INFO"
cp -n /home/nicolas/Documents/a6000/MAH04198.MP4 "$H/A6000-SD/MP_ROOT/103ANV01/"
cp reports/evidence/film-pb-1-sub-arnes-indice-20261126/AVIN0001_MAH04198.INP "$H/A6000-SD/AVF_INFO/AVIN0001.INP"
# (el original sintetico del arnes queda intacto en reports/evidence/film-pb-1-sub-avin-20261127/)

# 1) Un unico arranque en frio. SD_ESTRUCTURA=1 crea AVF_INFO/ y PRIVATE/M4ROOT/{CLIP,SUB,THMBNL,GENERAL}.
#    Trampas UDF en libmpr (entradas de funcion, offsets relativos a la base de la biblioteca):
#      60c958 AviMMgr::Mount            14b660 avi_man_NewAviFileManager
#      13e474 Fsys_FindFirst            7203c0 MprIf::GetAVIndexContentInfoList
#      6146a4 AviMMgr::GetIndexFilteringInfo   6e8430 GetPlayThumbnailInfo   61a8f0 isSupportContent
#      5bad00 ifoFramework_Semaphore::Acquire
HOME=$H SD_ESTRUCTURA=1 LIVE_REINTENTOS=1 \
SHIMEXTRA='WAITLOG=1000 LOGMARK=TRACELIB,AVIMMGR,MP4IFO,ContentCount,AccessPath TRACELIB=libmpr.so TRACEFN2=5bad00,6e8430,61a8f0,60c958,7203c0,6146a4,14b660,13e474 TRACEDEREF=d0:0:7 TRACEREP=1 TRACEMAX=4' \
.venv/bin/python3 scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir arnes-ind --puerto 8622
#    (el nombre de perfil tiene que ser corto: live/<perfil>/ui.sock no puede pasar de 108 B; "arnes-indice" falla)

# 2) Lectura del resultado
grep -a "TRACE \|DEREF" analysis/gui/g22/harness/live/arnes-ind/shim.log
.venv/bin/python3 reports/evidence/film-pb-1-sub-arnes-indice-20261126/galeria.py --puerto=8622 estado
curl -s -X POST http://127.0.0.1:8622/salir
