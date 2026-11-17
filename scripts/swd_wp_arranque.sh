#!/bin/bash
# Watchpoint de escritura SWD en los 4 Cortex-A5 del BIONZ (TRAZA-VM S2, docs/gui/g85).
# Solo registros de depuración por AP1 (sin target de OpenOCD): arma DBGWVR/DBGWCR 0 y 1 (1–2 direcciones) + HDBGen,
# al saltar lee DBGWFAR (instrucción que escribe) y r0–r3/lr por ITR (solo MCR al DTR), desarma ese núcleo,
# reanuda (DBGDRCR) y rearma en la vuelta siguiente (REARMA ms, 0). Sin escrituras de memoria.
# El watchpoint del A5 es síncrono: la escritura no se completa hasta reanudar con el watchpoint desarmado;
# si se reanuda armado, la misma instrucción vuelve a saltar sin fin (MEDIDO 17-11-2026).
# Uso: swd_wp_arranque.sh SALIDA.log DIR_VIRTUAL[,DIR2] [segundos=240] [max_golpes=40]
#   IGNORA=0xLO-0xHI: golpes con WFAR en ese rango no se registran ni cuentan (p. ej. el memcpy
#   0x439c5320 que copia cada V los bloques 0x43eb2680<->0x43eaee84); salen como «I <ms> ignorados=n» cada 10 s.
#   Arma solo con el arranque terminado ([0x43ede338] == 2; NO sirve para trazar el arranque) y rearma si el SO borra los registros.
# Salida: «H <ms> core=<n> wfar=<pc+off> r0..r3 lr dscr=<v> <palabra>=<valor antes de la escritura> por dirección», «A <ms> armado», «E <ms> <motivo>», «S <ms> <motivo>».
# WFAR = dirección de la instrucción + 8 (ARM) o + 4 (Thumb).
set -u
OUT=${1:?uso: swd_wp_arranque.sh SALIDA.log DIR_VIRTUAL [segundos] [max_golpes]}
DIR=${2:?dirección virtual a vigilar}; DUR=${3:-240}; MAX=${4:-40}
STALL=${STALL:-5}; ARRANQUE=${ARRANQUE:-15}; IGNORA=${IGNORA:-0x0-0x0}; REARMA=${REARMA:-0}
[[ -e $OUT ]] && { echo "ERROR: $OUT ya existe; no se sobrescribe" >&2; exit 1; }
if pgrep -x openocd >/dev/null; then
  echo "ERROR: otra sesión de openocd ocupa la sonda (mátala por PID, nunca con pkill -f):" >&2
  pgrep -ax openocd >&2; exit 1
fi

TMP=$(mktemp -d); OCD=; LOG=$TMP/ocd.log; COP=0
volcar() { local n; n=$(grep -acE '^[HAESI] ' "$LOG"); [[ ${1:-} == vivo ]] && ((n--))
  ((n > COP)) && grep -aE '^[HAESI] ' "$LOG" | sed -n "$((COP + 1)),${n}p" >> "$OUT"; ((n > COP)) && COP=$n; }
limpiar() {
  if [[ -n $OCD ]]; then kill -9 "$OCD" 2>/dev/null; wait "$OCD" 2>/dev/null; volcar; echo "S $(date +%s%3N) corte" >> "$OUT"
    # Un núcleo pudo quedar parado o con el watchpoint armado: desarmar y reanudar.
    timeout 20 openocd -f "$TMP/desarma.cfg" >/dev/null 2>&1; fi
  rm -rf "$TMP"
}
trap limpiar EXIT
trap 'exit 130' INT TERM HUP

cat > "$TMP/comun.cfg" <<'EOF'
adapter driver cmsis-dap
adapter serial E6698030DF5B3936
transport select swd
adapter speed 1000
swd newdap chip tap -enable
dap create chip.dap -chain-position chip.tap
init
set CORES {0x80110000 0x80112000 0x80114000 0x80116000}
proc w1 {a v} { chip.dap apreg 1 0x04 $a; chip.dap apreg 1 0x0c $v }
proc r1 {a} { chip.dap apreg 1 0x04 $a; return [string trim [chip.dap apreg 1 0x0c]] }
proc r0 {a} { chip.dap apreg 0 0x04 $a; return [string trim [chip.dap apreg 0 0x0c]] }
proc ms {} { clock milliseconds }
# Desarma y reanuda los cuatro núcleos (se usa también al salir).
proc desarma {} {
  foreach b $::CORES {
    catch { w1 [expr {$b + 0x1c0}] 0; w1 [expr {$b + 0x1c4}] 0 }
    catch { if {[r1 [expr {$b + 0x088}]] & 1} { w1 [expr {$b + 0x090}] 0x6 } }
  }
}
EOF
cat "$TMP/comun.cfg" > "$TMP/desarma.cfg"; printf 'desarma\nshutdown\n' >> "$TMP/desarma.cfg"

cat "$TMP/comun.cfg" > "$TMP/wp.cfg"
cat >> "$TMP/wp.cfg" <<'EOF'
# Por dirección: WVR = palabra; WCR: BAS = byte dentro de la palabra, LSC=10 (escritura), PAC=11 (cualquier modo), E=1.
set WP {}
foreach a [split $DIR ,] { lappend WP [list [expr {$a & ~3}] [expr {((1 << ($a & 3)) << 5) | 0x10 | 0x6 | 1}]] }
proc arma {b} {
  w1 [expr {$b + 0xfb0}] 0xc5acce55
  w1 [expr {$b + 0x300}] 0
  w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] | (1 << 14)}]
  set k 0
  foreach p $::WP { w1 [expr {$b + 0x180 + 4*$k}] [lindex $p 0]; w1 [expr {$b + 0x1c0 + 4*$k}] [lindex $p 1]; incr k }
}
proc desarma_wp {b} { foreach k {0 1} { w1 [expr {$b + 0x1c0 + 4*$k}] 0 } }
proc armado_ok {b} { set k 0; foreach p $::WP { if {[r1 [expr {$b + 0x1c0 + 4*$k}]] != [lindex $p 1]} { return 0 }; incr k }; return 1 }
proc palabras {} { set o ""; foreach p $::WP { append o " [format %08x [lindex $p 0]]=[r0 [expr {[lindex $p 0] + 0x40000000}]]" }; return [string trim $o] }
# Lee r0–r3 y lr del núcleo parado: ITRen y «MCR p14,0,Rt,c0,c5,0» (copia Rt al DTR); luego quita ITRen.
proc lee_regs {b} {
  set d [r1 [expr {$b + 0x088}]]
  w1 [expr {$b + 0x088}] [expr {$d | (1 << 13)}]
  set out ""
  foreach {n rt} {r0 0 r1 1 r2 2 r3 3 lr 14} {
    w1 [expr {$b + 0x084}] [expr {0xEE000E15 | ($rt << 12)}]
    set k 0; while {!([r1 [expr {$b + 0x088}]] & (1 << 24)) && $k < 50} { incr k }
    append out " $n=[r1 [expr {$b + 0x08c}]]"
  }
  w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] & ~(1 << 13)}]
  return [string trim $out]
}
set fin [expr {[ms] + $REM * 1000}]; set armado 0; set golpes 0; set bad 0; set latido 0; set ignorados 0; set kk 0
while {[ms] < $fin && $golpes < $MAX} {
  if {[ms] - $latido > 1000} { echo "K [ms]"; set latido [ms]; incr kk; if {$kk % 10 == 0} { echo "I [ms] ignorados=$ignorados" } }
  if {[catch {r0 0x0} v] || $v ne "0xe59ff0e8"} { incr bad } else { set bad 0 }
  if {$bad > 8} { echo "E [ms] sin_alimentacion"; break }
  if {!$armado} {
    # Solo con av-cam ya arrancado ([0x43ede338] == 2): armar antes, con ~20 paradas/s por el memcpy,
    # dejó la cámara en bucle de reinicios y luego sin arrancar (MEDIDO 17-11-2026, g85 S2).
    if {![catch {r0 0x83ede338} v] && $v eq "0x00000002"} {
      if {[catch {foreach b $CORES { arma $b }} e]} { echo "E [ms] arma:$e" } else { set armado 1; echo "A [ms] armado $WP" }
    }
    after 100; continue
  }
  set i 0
  foreach b $CORES {
    if {[catch {
      set d [r1 [expr {$b + 0x088}]]
      if {$d & 1} {
        set f [r1 [expr {$b + 0x018}]]
        desarma_wp $b
        set regs [lee_regs $b]
        w1 [expr {$b + 0x090}] 0x6
        set pend($i) [ms]
        if {$f >= [lindex $IG 0] && $f <= [lindex $IG 1]} { incr ignorados } else {
          incr golpes
          echo "H [ms] core=$i wfar=$f $regs dscr=$d [palabras]"
        }
      } elseif {[info exists pend($i)]} {
        if {[ms] - $pend($i) >= $REARMA} { arma $b; unset pend($i) }
      } elseif {![armado_ok $b]} { arma $b; echo "A [ms] rearmado core=$i" }
    } e]} { echo "E [ms] core=$i $e" }
    incr i
  }
}
if {$golpes >= $MAX} { echo "E [ms] max_golpes" }
desarma
shutdown
EOF

: > "$OUT"
END=$((SECONDS + DUR))
while ((SECONDS < END)); do
  : > "$LOG"; COP=0
  openocd -c "set REM $((END - SECONDS)); set DIR $DIR; set MAX $MAX; set IG {${IGNORA/-/ }}; set REARMA $REARMA" -f "$TMP/wp.cfg" > "$LOG" 2>&1 &
  OCD=$!; motivo=fin; t=0; quieto=0; s0=
  while kill -0 "$OCD" 2>/dev/null; do
    sleep 1; ((t++))
    n=$(grep -acE '^[HAESI] ' "$LOG"); volcar vivo
    # Latido «K» cada segundo desde Tcl: si el log deja de crecer, la sesión está atascada.
    s=$(stat -c %s "$LOG"); if [[ $s0 == "$s" ]]; then ((quieto++)); else quieto=0; fi; s0=$s
    if ((quieto >= STALL && t > ARRANQUE)); then motivo=atasco; kill -9 "$OCD" 2>/dev/null; fi
  done
  wait "$OCD" 2>/dev/null; OCD=
  volcar; echo "S $(date +%s%3N) $motivo" >> "$OUT"
  grep -q -E '^E [0-9]+ max_golpes' "$OUT" && break
  sleep 0.3
done
