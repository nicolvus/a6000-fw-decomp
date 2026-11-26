#!/bin/sh
# Reproducción exacta de la sesión (26-11-2026). Arnés G22 en modo live, sin navegador.
# Perfil nuevo (pbvid2), tarjeta del anfitrión $HOME/A6000-SD (3 clip(s) y 3 foto(s)).
set -x
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter)"

# 1. Arranque en frío (~3 min): perfiles pbvid1 (puerto 8799) y pbvid2 (8801)
PUERTO=8801 scripts/gui/harness/estable.sh pbvid2 live > analysis/gui/g22/harness/live-pbvid2.out 2>&1 &
# ... esperar a «primer fotograma»:  curl -s http://127.0.0.1:8801/estado

# 2. Instrumentación en caliente (no cambia la huella: sin reinicio)
D="python3 scripts/gui/harness/e2e_drv.py 8801"; export KEYWAIT=2
$D linea='E WAITLOG=1000' linea='E LOGMARK=Vn,Vd,Vo' \
   linea='E TRACELIB=libmpr.so' linea='E TRACEREP=1' linea='E TRACEDEREF=d0:0:7' \
   linea='E TRACEFN2=437bc0,6e8430,7229e0,44ee9c,61a8f0'
# confirmación (el LOG de armado solo se ve con WLALL=1)
$D linea='E WLALL=1' linea='E TRACEFN2=437bc0,6e8430,7229e0,44ee9c,61a8f0' linea='E WLALL='
#   → «TRACELIB libmpr.so base 0xadaab000: TRACEFN2 armadas en caliente (5)»

# 3. Intento de reproducción: tecla Reproducción (0x1f7), menú, vista forzada, cursores + Intro
$D reproduccion                        # sin efecto (ver 21-run2-reproduccion.png)
$D menu                                # 22-run2-menu.png
$D menu
$D linea='O view/INDEX_PLAYBACK 0'     # fuerza viewManagerIf::openView (23-run2-index-playback.png)
$D 'abajo*2' intro                     # 24-run2-intro-en-rejilla.png
$D linea='O view/INDEX_PLAYBACK 3'     # 25-run2-index-arg3.png

# 4. Control de que la trampa dispara (función conocida y llamable con «F»)
$D linea='E TRACELIB=libObj.so' linea='E TRACEFN2=125104' linea='F 125104'
#   → «TRACE 125104 n=1 r0=0 …» (una sola línea TRACE en todo el registro)

# 5. Recuento
grep -ac 'TRACE ' analysis/gui/g22/harness/live/pbvid2/shim.log      # = 1 (solo el control)
