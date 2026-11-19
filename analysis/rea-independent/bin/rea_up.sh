#!/usr/bin/env bash
# Idempotente: devuelve al instante si el demonio av-cam ya está listo; si no, lo lanza y espera.
# Uso: rea_up.sh [av-cam|av-cam-a7s]  -> imprime la ruta del socket. Consulta: q.py SOCK guion.json
set -euo pipefail
d="$(cd "$(dirname "$0")/.." && pwd)"; n="${1:-av-cam}"; sock="$d/out/$n.sock"
ok() { [ -e "$sock.ready" ] && python3 -c "import socket,sys;s=socket.socket(socket.AF_UNIX);s.settimeout(3);s.connect('$sock')" 2>/dev/null; }
if ! ok; then
  if [ "$n" = av-cam ] && systemctl --user cat rea-avcam >/dev/null 2>&1; then
    systemctl --user start --no-block rea-avcam   # el servicio es el único dueño: sin duplicados
  elif ! pgrep -f "session_daemon.py $sock" >/dev/null; then
    args="{\"path\":\"$d/input/$n.bin\",\"format\":\"raw-binary\",\"architecture\":\"arm\",\"entry_point\":\"0x43541000\",\"provider_id\":\"ghidra\"}"
    REA_DAEMON_IDLE_S="${REA_DAEMON_IDLE_S:-0}" setsid nohup python3 "$d/bin/session_daemon.py" "$sock" "$args" >"$d/logs/$n-daemon.log" 2>&1 &
  fi
  until ok; do sleep 5; done
fi
echo "$sock"
