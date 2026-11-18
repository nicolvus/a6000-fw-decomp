#!/bin/bash
# Breakpoints hardware de UN SOLO GOLPE en los 4 Cortex-A5 del BIONZ durante el arranque (TRAZA-VM S2, docs/gui/g85).
# Cada dirección para la CPU como mucho una vez: al saltar se leen pc, r0–r3, lr (ITR), se desarma esa dirección
# en los 4 núcleos y se reanuda. Máximo de paradas = nº de direcciones (≤ 3, los BRP del A5 sin enlazar que se usan).
# Seguro en el arranque, al contrario que un watchpoint que salta en cada fotograma (incidente S2, 17-11-2026).
# Solo registros de depuración (AP1) y lectura de RAM (AP0); r0 se restaura tras leer el pc. Sin escrituras de memoria.
# Uso: swd_bp_unico.sh SALIDA.log DIR[,DIR2[,DIR3]] [segundos=300]   (direcciones virtuales de av-cam; Thumb = par)
#   VOLCAR="r1:32,*sp+4:32": en cada golpe vuelca memoria desde un registro o desde el puntero guardado en sp+OFF
#   (palabras de 32 bit en hexadecimal tal cual se leen, little-endian).
# Arma cuando la RAM de av-cam está inicializada ([0x43eaeecc] != 0) y rearma las no disparadas si el SO las borra.
# Salida: «H <ms> core=<n> pc=<v> r0..r3 lr est=[0x43ede338]/[0x43ede320] flag=[0x43eaeecc]», «A», «E», «S».
set -u
OUT=${1:?uso: swd_bp_unico.sh SALIDA.log DIR[,DIR2[,DIR3]] [segundos]}
DIR=${2:?direcciones}; DUR=${3:-300}; STALL=${STALL:-5}; ARRANQUE=${ARRANQUE:-15}; VOLCAR=${VOLCAR:-}
[[ -e $OUT ]] && { echo "ERROR: $OUT ya existe; no se sobrescribe" >&2; exit 1; }
if pgrep -x openocd >/dev/null; then
  echo "ERROR: otra sesión de openocd ocupa la sonda (mátala por PID, nunca con pkill -f):" >&2
  pgrep -ax openocd >&2; exit 1
fi
(( $(tr ',' '\n' <<<"$DIR" | wc -l) <= 3 )) || { echo "ERROR: máximo 3 direcciones" >&2; exit 1; }

TMP=$(mktemp -d); OCD=; LOG=$TMP/ocd.log; COP=0
volcar() { local n; n=$(grep -acE '^[HAES] ' "$LOG"); [[ ${1:-} == vivo ]] && ((n--))
  ((n > COP)) && grep -aE '^[HAES] ' "$LOG" | sed -n "$((COP + 1)),${n}p" >> "$OUT"; ((n > COP)) && COP=$n; }
limpiar() {
  if [[ -n $OCD ]]; then kill -9 "$OCD" 2>/dev/null; wait "$OCD" 2>/dev/null; volcar; echo "S $(date +%s%3N) corte" >> "$OUT"
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
# Desarma los 3 BRP, quita HDBGen/ITRen y reanuda cualquier núcleo parado (también al salir).
proc desarma {} {
  foreach b $::CORES {
    catch { foreach k {0 1 2} { w1 [expr {$b + 0x140 + 4*$k}] 0 } }
    catch { if {[r1 [expr {$b + 0x088}]] & 1} { w1 [expr {$b + 0x090}] 0x6 } }
    catch { w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] & ~((1 << 14) | (1 << 13))}] }
  }
}
EOF
cat "$TMP/comun.cfg" > "$TMP/desarma.cfg"; printf 'desarma\nshutdown\n' >> "$TMP/desarma.cfg"

cat "$TMP/comun.cfg" > "$TMP/bp.cfg"
cat >> "$TMP/bp.cfg" <<'EOF'
# BVR = palabra; BCR: BAS = 0b1111 si la dirección es múltiplo de 4 (instrucción ARM o Thumb en esa palabra),
# 0b1100 si es la media palabra alta (Thumb); PMC=11, E=1, coincidencia de dirección.
set BP {}
foreach a [split $DIR ,] { lappend BP [list $a [expr {$a & ~3}] [expr {((($a & 2) ? 0xc : 0xf) << 5) | 0x6 | 1}]] }
array set hecho {}
proc arma {b} {
  w1 [expr {$b + 0xfb0}] 0xc5acce55
  w1 [expr {$b + 0x300}] 0
  w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] | (1 << 14)}]
  set k 0
  foreach p $::BP {
    if {![info exists ::hecho($k)]} { w1 [expr {$b + 0x100 + 4*$k}] [lindex $p 1]; w1 [expr {$b + 0x140 + 4*$k}] [lindex $p 2] }
    incr k
  }
}
proc armado_ok {b} {
  set k 0
  foreach p $::BP { if {![info exists ::hecho($k)] && [r1 [expr {$b + 0x140 + 4*$k}]] != [lindex $p 2]} { return 0 }; incr k }
  return 1
}
# ITR (siempre ARM en estado de depuración): MCR p14,0,Rt,c0,c5,0 = Rt -> DTRTX; MRC p14,0,r0,c0,c5,0 = DTRRX -> r0.
proc itr {b ins} { w1 [expr {$b + 0x084}] $ins; set k 0; while {!([r1 [expr {$b + 0x088}]] & (1 << 24)) && $k < 50} { incr k } }
proc lee {b rt} { itr $b [expr {0xEE000E15 | ($rt << 12)}]; return [r1 [expr {$b + 0x08c}]] }
# RAM del núcleo: virtual 0x40000000–0x7fffffff = física + 0x40000000 (MEDIDO); el resto se lee tal cual.
proc va2pa {a} { return [expr {($a >= 0x40000000 && $a < 0x80000000) ? $a + 0x40000000 : $a}] }
proc lee_regs {b} {
  w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] | (1 << 13)}]
  set out ""; foreach {n rt} {r0 0 r1 1 r2 2 r3 3 sp 13 lr 14} { set v($n) [lee $b $rt]; append out " $n=$v($n)" }
  # VOLCAR: «rN:len» vuelca len bytes desde el valor de rN; «*sp+OFF:len» desde la palabra en sp+OFF (núcleo aún parado).
  foreach e $::VOLCAR {
    lassign [split $e :] q n
    if {[string index $q 0] eq "*"} { lassign [split [string range $q 1 end] +] rg off } else { set rg $q; set off "" }
    # Registro no leído aún (r4–r12): leerlo ahora con el núcleo parado.
    if {![info exists v($rg)]} { set v($rg) [lee $b [string range $rg 1 end]] }
    if {$off ne ""} { set a [r0 [va2pa [expr {$v($rg) + $off}]]] } else { set a $v($rg) }
    set h ""; for {set k 0} {$k < $n} {incr k 4} { append h [format %08x [r0 [va2pa [expr {$a + $k}]]]] }
    append out " mem($e)@[format 0x%08x $a]=$h"
  }
  # pc: «mov r0, pc» (pc + 8 en ARM, + 4 en Thumb) y restaurar r0 desde el DTR.
  itr $b 0xE1A0000F; set pc [lee $b 0]
  w1 [expr {$b + 0x080}] $v(r0); itr $b 0xEE100E15
  w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] & ~(1 << 13)}]
  return [list $pc [string trim $out]]
}
set fin [expr {[ms] + $REM * 1000}]; set armado 0; set bad 0; set latido 0
while {[ms] < $fin && [array size hecho] < [llength $BP]} {
  if {[ms] - $latido > 1000} { echo "K [ms]"; set latido [ms] }
  if {[catch {r0 0x0} v] || $v ne "0xe59ff0e8"} { incr bad } else { set bad 0 }
  if {$bad > 8} { echo "E [ms] sin_alimentacion"; break }
  if {!$armado} {
    if {![catch {r0 0x83eaeecc} v] && $v ne "0x00000000"} {
      if {[catch {foreach b $CORES { arma $b }} e]} { echo "E [ms] arma:$e" } else { set armado 1; echo "A [ms] armado $BP" }
    }
    after 50; continue
  }
  set i 0
  foreach b $CORES {
    if {[catch {
      set d [r1 [expr {$b + 0x088}]]
      if {$d & 1} {
        # Primero desarmar en los 4 núcleos (antes de leer registros, que tarda ~20 ms): si no, los demás núcleos
        # pasan por la misma dirección y paran también (MEDIDO 17-11-2026: 4 paradas en vez de 1).
        foreach c $CORES { foreach k {0 1 2} { w1 [expr {$c + 0x140 + 4*$k}] 0 } }
        # Pase lo que pase al leer, el núcleo se reanuda: un error aquí lo dejaba parado (MEDIDO 17-11-2026: núcleo 2 parado ≈ 3 s).
        if {[catch {lassign [lee_regs $b] pcraw regs} e]} { set pcraw 0; set regs "lectura:$e" ; catch { w1 [expr {$b + 0x088}] [expr {[r1 [expr {$b + 0x088}]] & ~(1 << 13)}] } }
        # Qué BRP saltó: el pc leído menos 4 (Thumb) o 8 (ARM) coincide con su dirección.
        set k 0; set cual -1
        foreach p $BP { set a [lindex $p 0]; if {$pcraw - 4 == $a || $pcraw - 8 == $a} { set cual $k }; incr k }
        # Sin identificar cuál saltó, se dan todas por disparadas (nunca una segunda parada por la misma causa).
        if {$cual < 0} { set n [llength $BP]; for {set k 0} {$k < $n} {incr k} { set hecho($k) 1 } } else { set hecho($cual) 1 }
        w1 [expr {$b + 0x090}] 0x6
        # Rearmar las que faltan en los núcleos en marcha.
        foreach c $CORES { if {!([r1 [expr {$c + 0x088}]] & 1)} { arma $c } }
        echo "H [ms] core=$i pc=$pcraw bp=[expr {$cual < 0 ? "?" : [lindex [lindex $BP $cual] 0]}] $regs dscr=$d est=[r0 0x83ede338]/[r0 0x83ede320] flag=[r0 0x83eaeecc]"
      } elseif {![armado_ok $b]} { arma $b; echo "A [ms] rearmado core=$i" }
    } e]} { echo "E [ms] core=$i $e" }
    incr i
  }
}
if {[array size hecho] >= [llength $BP]} { echo "E [ms] todos_disparados" }
desarma
shutdown
EOF

: > "$OUT"
END=$((SECONDS + DUR))
while ((SECONDS < END)); do
  : > "$LOG"; COP=0
  openocd -c "set REM $((END - SECONDS)); set DIR $DIR; set VOLCAR {${VOLCAR//,/ }}" -f "$TMP/bp.cfg" > "$LOG" 2>&1 &
  OCD=$!; motivo=fin; t=0; quieto=0; s0=
  while kill -0 "$OCD" 2>/dev/null; do
    sleep 1; ((t++)); volcar vivo
    s=$(stat -c %s "$LOG"); if [[ $s0 == "$s" ]]; then ((quieto++)); else quieto=0; fi; s0=$s
    if ((quieto >= STALL && t > ARRANQUE)); then motivo=atasco; kill -9 "$OCD" 2>/dev/null; fi
  done
  wait "$OCD" 2>/dev/null; OCD=
  volcar; echo "S $(date +%s%3N) $motivo" >> "$OUT"
  grep -q -E '^E [0-9]+ todos_disparados' "$OUT" && break
  sleep 0.3
done
