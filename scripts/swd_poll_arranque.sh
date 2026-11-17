#!/bin/bash
# Sondeo SWD SOLO LECTURA durante el arranque del BIONZ (TRAZA-VM S1, docs/gui/g85).
# Reabre la sesión cuando el DAP no responde, se corta la alimentación o OpenOCD se atasca,
# y nunca deja un openocd huérfano ocupando la sonda.
# Uso: swd_poll_arranque.sh SALIDA.log [segundos=240]
#   Variables: STALL (s sin líneas nuevas = sesión atascada, 5), ARRANQUE (s máximos sin
#   ninguna lectura tras abrir, 15), SELFTEST=1 (sale tras la primera sesión con datos).
# Salida: «P <ms_epoch> [0x43ede338] [0x43ede320] [0x43eaeecc]», «E <ms> <motivo>», «S <ms> <fin|atasco|sin_datos|corte>».
# RAM física = dirección virtual de av-cam + 0x40000000 (leer 0x43… directamente atasca los AP).
set -u
OUT=${1:?uso: swd_poll_arranque.sh SALIDA.log [segundos=240]}; DUR=${2:-240}
STALL=${STALL:-5}; ARRANQUE=${ARRANQUE:-15}; SELFTEST=${SELFTEST:-0}
[[ -e $OUT ]] && { echo "ERROR: $OUT ya existe; no se sobrescribe" >&2; exit 1; }
if pgrep -x openocd >/dev/null; then
  echo "ERROR: otra sesión de openocd ocupa la sonda (mátala por PID, nunca con pkill -f):" >&2
  pgrep -ax openocd >&2; exit 1
fi
command -v openocd >/dev/null || { echo "ERROR: falta openocd" >&2; exit 1; }

TMP=$(mktemp -d); OCD=; LOG=$TMP/ocd.log
# Copia al log de salida las líneas nuevas (en vivo: hasta la penúltima, que puede estar a medias; al cerrar: todas).
COP=0
volcar() { local n; n=$(grep -acE '^[PE] ' "$LOG"); [[ ${1:-} == vivo ]] && ((n--))
  ((n > COP)) && grep -aE '^[PE] ' "$LOG" | sed -n "$((COP + 1)),${n}p" >> "$OUT"; ((n > COP)) && COP=$n; }
limpiar() {
  if [[ -n $OCD ]]; then kill -9 "$OCD" 2>/dev/null; wait "$OCD" 2>/dev/null; volcar; echo "S $(date +%s%3N) corte" >> "$OUT"; fi
  rm -rf "$TMP"
}
trap limpiar EXIT
trap 'exit 130' INT TERM HUP

cat > "$TMP/poll.cfg" <<'EOF'
adapter driver cmsis-dap
adapter serial E6698030DF5B3936
transport select swd
adapter speed 1000
swd newdap chip tap -enable
dap create chip.dap -chain-position chip.tap
init
proc rd {a} { chip.dap apreg 0 0x04 $a; return [string trim [chip.dap apreg 0 0x0c]] }
set fin [expr {[clock milliseconds] + $REM * 1000}]
set bad 0
while {[clock milliseconds] < $fin} {
  if {[catch {echo [format "P %d %s %s %s" [clock milliseconds] [rd 0x83ede338] [rd 0x83ede320] [rd 0x83eaeecc]]} e]} {
    echo "E [clock milliseconds] lectura:$e"
  }
  # Vector de reset: deja de leerse igual al cortar la alimentación; sin esto la sesión queda colgada.
  if {[catch {rd 0x0} v] || $v ne "0xe59ff0e8"} {incr bad} else {set bad 0}
  if {$bad > 8} {echo "E [clock milliseconds] sin_alimentacion"; break}
  after 150
}
shutdown
EOF

: > "$OUT"
END=$((SECONDS + DUR))
while ((SECONDS < END)); do
  : > "$LOG"; COP=0
  openocd -c "set REM $((END - SECONDS))" -f "$TMP/poll.cfg" > "$LOG" 2>&1 &
  OCD=$!; motivo=fin; n0=0; quieto=0; t=0
  while kill -0 "$OCD" 2>/dev/null; do
    sleep 1; ((t++))
    n=$(grep -acE '^[PE] ' "$LOG"); volcar vivo
    if ((n > 0 && n == n0)); then ((quieto++)); else quieto=0; fi; n0=$n
    if ((quieto >= STALL)); then motivo=atasco; kill -9 "$OCD" 2>/dev/null; fi
    if ((n == 0 && t >= ARRANQUE)); then motivo=sin_datos; kill -9 "$OCD" 2>/dev/null; fi
  done
  wait "$OCD" 2>/dev/null; OCD=
  ((n0 == 0)) && [[ $motivo == fin ]] && motivo=sin_datos
  volcar; echo "S $(date +%s%3N) $motivo" >> "$OUT"
  [[ $SELFTEST == 1 && $motivo != sin_datos ]] && break
  sleep 0.3
done
