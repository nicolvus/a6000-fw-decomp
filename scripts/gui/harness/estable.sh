#!/bin/sh
# Arnés de la UI (G22) en un solo comando: perfil limpio, instrumentación sólo por variables de entorno.
#
#   scripts/gui/harness/estable.sh <perfil> [live|seco|verifica|arma|limpia] [args]     (live por omisión)
#
#   live      pantalla en el navegador (live.py) + canal LIVE: único modo donde se pueden armar trampas en
#             caliente («E TRACEFN2=…» por POST /linea) y único que guarda/restaura estado.zst.
#   seco      arranque sin UI (run.py + im.sh): imprime «alive=… threads=… modulos=…» y termina solo.
#   verifica  arranque seco SIN instrumentar, con tope de tiempo: OK / NO / NO-CONCLUYENTE, códigos 0/1/75
#             (3 min de tope; con carga > 12 no concluye en vez de mentir).
#   arma      «arma <puerto> <línea>»: manda una línea al invitado (p. ej. «E TRACEFN2=5bad00») con vigilante.
#   limpia    borra de ESTE perfil lo pesado (initrd.gz, estado.zst, estado.tmp, consola.log): libera ~200 MB.
#
# Instrumentación (van al SHIMENV del invitado; ver docs/gui/g22-avcam-puente.md §5.41):
#   TRACEFN=off[,off…]        trampas de un solo uso en libObj (VA del ELF).
#   TRACELIB=libmpr.so        biblioteca a la que se refieren los desplazamientos de TRACEFN2.
#   TRACEFN2=off[,off…]       trampas en esa biblioteca, relativas a su base (se arman al cargarse).
#   TRACEREP=1                trampa repetible (UDF en la instrucción siguiente): SÓLO entradas de función.
#   TRACEDEREF=d0:0:7         volcado de palabras en el punto de la trampa; TRACEMAX=n; TRACEPEEK=off,…
#   WAITLOG=1000              (en SHIMEXTRA) manda todo el registro del shim a live/<perfil>/shim.log, con hora.
# Otras variables: PUERTO (live, 8600) · WAIT (seco, 130) · ESTABLE_WORK (DIR_TRABAJO) · SHIMEXTRA (extra crudo)
#   INTENTOS=n (reintentos del arranque seco; 2 en verifica, 1 en seco) · CHEQUEA=0 · FUERZA=1
#   ESTABLE_REUSA=1 (permitir un perfil que ya existe) · LIBDIR=… (dónde buscar la biblioteca del chequeo)
#
# Perfil = $ESTABLE_WORK/live/<perfil> (por omisión analysis/gui/g22/harness/live/<perfil>, gitignored). Se exige
# que NO exista: no se pisa el estado ni la nvram.json de otra prueba. Mismo SHIMENV ⇒ en frío siempre ≈2–3 min;
# en live, a los ≈190 s se guarda estado.zst y los arranques siguientes restauran en ≈7 s. Cambiar
# TRACEFN2/TRACELIB/SHIMEXTRA cambia la huella ⇒ borra el estado y vuelve a arrancar en frío (lo que se busca al
# instrumentar). Diagnóstico de los arranques que fallan: ver §2 del informe y `consola.log`/`last.log` del perfil.
set -u
AQUI=$(cd "$(dirname "$0")" && pwd); R=$(cd "$AQUI/../../.." && pwd)
W=${ESTABLE_WORK:-$R/analysis/gui/g22/harness}
PERFIL=${1:-}; MODO=${2:-live}; shift 2 2>/dev/null || shift $#
[ -n "$PERFIL" ] || { sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
PD=$W/live/$PERFIL

# Antes de gastar 3 minutos: los fallos que no son del arnés (ruta de socket de QEMU, disco, DIR_TRABAJO).
if [ -s "$W/vmlinuz" ] && [ -s "$W/base.cpio.gz" ] || [ "$MODO" = limpia ]; then :; else
    echo "falta DIR_TRABAJO ($W) con vmlinuz y base.cpio.gz; créalo con:" >&2
    echo "  sh $AQUI/setup.sh $W" >&2; exit 2; fi
LARGO=$(printf %s "$PD/ui.sock" | wc -c)   # QEMU: «Unix socket path … is too long. Path must be less than 108 bytes»
[ "$LARGO" -lt 108 ] || { echo "perfil demasiado largo: $PD/ui.sock tiene $LARGO B (máx 107). Nombre corto o ESTABLE_WORK menos profundo." >&2; exit 2; }
LIBRES=$(df -Pm "$W" | awk 'NR==2{print $4}'); [ "${LIBRES:-0}" -ge 1200 ] || {
    echo "quedan ${LIBRES:-?} MB en $W; un arranque en frío escribe initrd.gz (93–117 MB) + estado.zst (117 MB)." >&2
    echo "  libera con: sh $0 <perfil> limpia   (51 GB acumulados en analysis/gui/g22/harness/live)" >&2; exit 2; }
TLIBRES=$(df -Pm /tmp | awk 'NR==2{print $4}'); [ "${TLIBRES:-0}" -ge 400 ] || {
    echo "quedan ${TLIBRES:-?} MB en /tmp (run.py monta ahí el initrd, ~150 MB por arranque); TMPDIR=… o libera." >&2; exit 2; }

# La tarjeta que ve el invitado sale de $HOME/A6000-SD (sd_emu.SD_DEFECTO): con HOME cambiado (p. ej. HOME=/tmp/x)
# el invitado ve una tarjeta VACÍA y la enumeración no prueba nada. Se avisa y se anota en cada arranque.
TARJETA=$HOME/A6000-SD; CLIPS=$(find "$TARJETA" \( -iname '*.mp4' -o -iname '*.webm' \) 2>/dev/null | wc -l)
FOTOS=$(find "$TARJETA" -name 'DSC[0-9][0-9][0-9][0-9][0-9].*' 2>/dev/null | wc -l)
[ -d "$TARJETA" ] || echo "AVISO: no existe $TARJETA (HOME=$HOME): el invitado verá la tarjeta vacía." >&2

if [ "$MODO" != limpia ]; then
    if [ -e "$PD" ] && [ "${ESTABLE_REUSA:-0}" != 1 ]; then
        echo "el perfil '$PERFIL' ya existe ($PD: $(ls "$PD" | tr '\n' ' ')); usa otro nombre o ESTABLE_REUSA=1" >&2; exit 2; fi
    mkdir -p "$PD"
fi

# Instrumentación que viaja al invitado (sólo las variables puestas; SHIMEXTRA, si se usa, manda por ir después).
T=""
for v in TRACEFN TRACELIB TRACEFN2 TRACEDEREF TRACEREP TRACEMAX TRACEPEEK; do
    eval "val=\${$v:-}"; [ -n "$val" ] && T="$T $v=$val"; done

# Antes de armar nada: que los desplazamientos sean entradas de función (regla del informe §3). Armar fuera de
# una entrada mata im.elf (IMEXIT 139): con TRACEREP el UDF se escribe en «la instrucción siguiente», que a media
# instrucción no existe, y el manejador termina en signal(SIGILL, SIG_DFL).
chequeo() {  # $1 = off[,off…]; no arranca/arma si alguno no es entrada de función (salvo FUERZA=1)
    LIB=${LIBDIR:-$(ls "$R"/firmware/extracted/fw321/*/0700_part_image/dev/nflasha15_*/lib/"${TRACELIB:-libmpr.so}" 2>/dev/null | head -1)}
    [ -f "${LIB:-}" ] || { echo "  (chequeo omitido: no encuentro ${TRACELIB:-libmpr.so}; LIBDIR=… o CHEQUEA=0)" >&2; return 0; }
    SAL=$(python3 "$AQUI/chequea_trampas.py" "$LIB" "$1"); RC=$?
    printf '%s\n' "$SAL" | sed 's/^/  /'
    [ "$RC" = 0 ] || { [ "${FUERZA:-0}" = 1 ] || exit 3; }
}
[ -n "${TRACEFN2:-}" ] && [ "${CHEQUEA:-1}" != 0 ] && chequeo "$TRACEFN2"

CADENA="CVWAIT=0 POKE=fef348 OPENVIEW=view/ROOT,view/STLREC OPENVIEWAT=40 OPENVIEWGAP=14 CALMA=4 CALMA0=10 \
STARTEV=11004002:100,11004012,11004013 POSTROOTEV=11004002:e3 STARTGAP=f SALVAGE=0 SKIPFN=7fa3d4=0 \
ACKQ0=58003f KEYQ=7a0020 KEYONACTIVE=0 KEYINIT=7000001:1:177,7025:3:27 KEYINITON= \
KEYINITAFTER=not_user_operation OPENVIEWARG=3 NO4015E=1 BKMULTIPTR=1 FRONTRM=3 FRONTARG2=1 FRONTRMDELAY=3 \
INSHORT=1 SDIMG=1 SDSECT=8388608 NULLMWF=1 SYNCWAIT=37807c:300"

arranca_seco() {  # $1 = instrumentación (vacía en verifica) → deja last.log/stdout.txt en $PD y fija RES/TH/MOD/PID
    # Carga del anfitrión: el invitado va a 1× con el equipo libre (12 núcleos, 8 vCPU TCG) y a ≈0,25× con carga 36
    # (medido en esta sesión) → con la máquina cargada se alarga WAIT, si cabe en el tope de 3 min.
    # WAIT es tiempo DEL INVITADO: 100 s bastan para que la cadena abra view/STLREC (las CALMA del arranque suman
    # ≈67 s). Lo que hay que alargar con la carga es el tope de PARED (TOPE), no WAIT: subir WAIT sólo hace que el
    # invitado lento no llegue nunca dentro del mismo tope.
    CARGA1=$(cut -d' ' -f1 /proc/loadavg); WAIT0=${WAIT:-$([ "$MODO" = verifica ] && echo 100 || echo 130)}
    TOPE=${TOPE:-$([ "$MODO" = verifica ] && echo 172 || echo 600)}   # TOPE = tope de pared propio (172 s < 3 min)
    [ "$WAIT0" -gt $((TOPE - 35)) ] && WAIT0=$((TOPE - 35))   # la espera no puede comerse el tope
    LOG=$PD/last.log; : > "$LOG"; T0=$(date +%s)
    SHIMENV="WAIT=$WAIT0 $CADENA$1${SHIMEXTRA:+ $SHIMEXTRA}" HARNESS_OUT=$PD \
        setsid python3 "$AQUI/run.py" "$W" "$AQUI/im.sh" 600 > "$PD/stdout.txt" 2>&1 &
    RJ=$!; T_BOOT=""; T_ALIVE=""
    while kill -0 $RJ 2>/dev/null; do
        sleep 2; NOW=$(( $(date +%s) - T0 ))
        [ -z "$T_BOOT" ] && [ -s "$LOG" ] && T_BOOT=$NOW
        [ -z "$T_ALIVE" ] && grep -aq "alive=" "$LOG" 2>/dev/null && T_ALIVE=$NOW
        if [ "$NOW" -ge "$TOPE" ]; then  # tope propio: se corta el grupo (run.py no cierra QEMU si se le mata)
            kill -TERM -$RJ 2>/dev/null; sleep 3; kill -KILL -$RJ 2>/dev/null; break; fi
    done
    wait $RJ 2>/dev/null
    RES=$(grep -a "alive=" "$LOG" 2>/dev/null | tail -1)
    TH=$(echo "$RES" | sed -n 's/.*threads=\([0-9]*\).*/\1/p'); MOD=$(echo "$RES" | sed -n 's/.*modulos=\([0-9]*\).*/\1/p')
    PID=$(echo "$RES" | sed -n 's/^alive=\([0-9]*\).*/\1/p')
    MUERTO=$(grep -aq "IMEXIT\|Segmentation fault\|Aborted" "$LOG" 2>/dev/null && echo si || echo no)
    printf 'arranque: resumen %ss · total %ss · carga %s · tarjeta %s clip(s) %s foto(s) (HOME=%s)\n' "${T_ALIVE:-—}" \
        "$(( $(date +%s) - T0 ))" "$(cut -d' ' -f1-3 /proc/loadavg)" "$CLIPS" "$FOTOS" "$HOME"
}

case "$MODO" in
live)  # El supervisor de live.py mata el arranque en frío si no hay pantalla en LIVE_ARRANQUE_MAX (260 s) y
    # reintenta: con el equipo cargado eso se ve como «el tercer arranque falla» cuando sólo va a 0,4×. Se alarga
    # según la carga si el usuario no lo fija.
    if [ -z "${LIVE_ARRANQUE_MAX:-}" ]; then
        LIVE_ARRANQUE_MAX=$(python3 -c "l=float('$(cut -d' ' -f1 /proc/loadavg)'); print(int(260*min(3.0, max(1.0, l/6))))")
        export LIVE_ARRANQUE_MAX; fi
    echo "tarjeta: $CLIPS clip(s) y $FOTOS foto(s) en $TARJETA (HOME=$HOME) · perfil $PERFIL · http://127.0.0.1:${PUERTO:-8600}"
    exec python3 "$AQUI/live.py" "$W" --perfil-dir "$PERFIL" --puerto "${PUERTO:-8600}" ;;  # SHIMEXTRA entra en SHIMENV
seco|verifica)
    [ "$MODO" = verifica ] && T=""    # «en seco» = sin instrumentar; para instrumentado se usa `seco`
    N=0; NINT=${INTENTOS:-$([ "$MODO" = verifica ] && echo 2 || echo 1)}
    while : ; do
        N=$((N + 1)); arranca_seco "$T"
        if [ "$MODO" = seco ]; then
            echo "perfil=$PERFIL ${RES:-sin resumen} (registro: $PD/last.log)"; exit $([ -n "$PID" ] && echo 0 || echo 1); fi
        if [ -n "$PID" ] && [ "${TH:-0}" -ge "${MIN_THREADS:-60}" ] && [ "${MOD:-0}" -ge "${MIN_MODULOS:-60}" ] && [ "$MUERTO" = no ]; then
            echo "OK   arnés en la pantalla de disparo: threads=$TH modulos=$MOD intento=$N/$NINT (perfil $PERFIL, $PD)"; exit 0; fi
        if [ "$MUERTO" = no ] && python3 -c "import sys; sys.exit(0 if float('$CARGA1') > 12 else 1)"; then
            echo "NO-CONCLUYENTE  carga $CARGA1 > 12: el invitado va a menos de 1× y no alcanza WAIT=$WAIT0 s propios dentro de los $TOPE s del tope (no es un fallo del arnés). Repite con carga < 12 o alarga: TOPE=400 WAIT=$WAIT0 sh $0 $PERFIL verifica (perfil $PERFIL)"; exit 75; fi
        [ "$N" -lt "$NINT" ] || break
        echo "reintento $((N + 1))/$NINT: el arranque $N no llegó (${RES:-sin resumen}, muerte=$MUERTO); el SEGV de arranque de im.elf es intermitente (§5.41)"
        WAIT0=$(( WAIT0 - 15 ))   # al reintentar se acorta la espera: el reloj del tope de 3 min manda
    done
    echo "NO   ${RES:-sin resumen (im.elf no llegó a los ${WAIT:-130} s)} · muerte detectada=$MUERTO · intentos=$N (perfil $PERFIL, $PD)"; exit 1 ;;
arma)  # «E TRACEFN2=…» y compañía, en caliente, con vigilante: si im.elf muere se ve aquí y en consola.log
    P=${1:-${PUERTO:-8600}}; shift $(( $# > 0 ? 1 : 0 )); LINEA="$*"
    [ -n "$LINEA" ] || { echo "uso: estable.sh <perfil> arma <puerto> <línea>" >&2; exit 2; }
    case "$LINEA" in *TRACEFN2=*) O=${LINEA#*TRACEFN2=}; O=${O%% *}; [ "${CHEQUEA:-1}" != 0 ] && chequeo "$O" ;; esac
    f() { curl -s -m 5 "http://127.0.0.1:$P/estado" | sed -n 's/.*"fotogramas": *\([0-9]*\).*/\1/p'; }
    A=$(f); echo "fotogramas antes: ${A:-?}"
    curl -s -m 5 -X POST --data-binary "$LINEA" "http://127.0.0.1:$P/linea" >/dev/null || { echo "no responde 127.0.0.1:$P" >&2; exit 1; }
    sleep 12; B=$(f); echo "fotogramas después: ${B:-?} (12 s)"
    if [ -z "$B" ]; then echo "VM CAÍDA tras la línea: mira $PD/consola.log (IMEXIT) y $PD/shim.log"; exit 1; fi
    echo "VM VIVA; línea entregada. Regla: sólo entradas de función, de una en una (chequea_trampas.py)."; exit 0 ;;
limpia)  # libera lo pesado sin tocar nvram.json ni av-cam.bin del perfil
    [ -d "$PD" ] || { echo "no existe $PD" >&2; exit 1; }
    du -sm "$PD" 2>/dev/null; ( cd "$PD" && rm -f initrd.gz estado.zst estado.tmp estado.zst.tmp consola.log shim.log last.log stdout.txt )
    echo "perfil $PERFIL limpio: $(du -sm "$PD" 2>/dev/null | cut -f1) MB (nvram.json/av-cam.bin intactos)"; exit 0 ;;
*)  echo "modo desconocido: $MODO (live|seco|verifica|arma|limpia)" >&2; exit 2 ;;
esac
