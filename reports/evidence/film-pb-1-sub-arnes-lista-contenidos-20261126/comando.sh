#!/bin/sh
# FILM-PB-1 / lista de contenidos de la galería — comando único reproducible (arnés QEMU, sin cámara).
#   sh reports/evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/comando.sh <puerto> <perfil>
# Requisitos: la tarjeta que ve el invitado es $HOME/A6000-SD (sd_emu.SD_DEFECTO). Debe tener al menos
#   AVF_INFO/AVIN0001.INP  (384 B, registro de MAH04198.MP4)  y
#   MP_ROOT/100ANV01/MAH04198.MP4  y  PRIVATE/M4ROOT/CLIP/C0001.MP4 (mismo tamaño que el del .INP).
# 1) arranque (arranque en frío ≈2-4 min según carga; estable.sh sube LIVE_ARRANQUE_MAX solo)
#    TRACELIB=libmpr.so TRACEFN2=7203c0,7202c8,454162,6146a4,720a30,71e9dc,7352cc \
#    TRACEFN=598930 TRACEREP=1 TRACEMAX=64 PUERTO=8641 \
#    SHIMEXTRA='WAITLOG=1000 LOGMARK=viewUnified,OPENHOT,Vn,Vd,M015' \
#    sh scripts/gui/harness/estable.sh lc1 live
# 2) esta maniobra, con la primera pantalla ya dibujada
set -u
P=${1:-8641}; EV=$(dirname "$0"); C="python3 $EV/ctl.py --puerto=$P"
$C esperafotograma 600
$C linea "E WLALL=1"                 # registro del firmware + líneas del shim (dlopen) → shim.log
$C linea "M @M015"                   # PRECREATE: publica «solicitar modelo» @M015 (ModelIndexPb)
$C espera 4
$C linea "O view/INDEX_PLAYBACK 0"   # abre la galería
$C espera 6
$C linea "F 125104"                  # getCurrentFuncEventMode (0x15 = índice arriba)
$C refrescar
$C captura "$EV/index-tras-maniobra.png" 60
$C linea "E WLALL="
echo "--- recuento ---"
S=analysis/gui/g22/harness/live/lc1/shim.log
grep -ao "TRACE [0-9a-f]*" "$S" | sort | uniq -c
grep -a "LOGMARK" "$S" | grep -a "Vn \|Vd \|Vo " | tail -20
grep -ac "dlopen(libInfraScalarMpr" "$S"
