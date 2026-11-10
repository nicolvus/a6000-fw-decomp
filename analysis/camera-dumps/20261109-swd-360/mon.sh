#!/bin/bash
# vigila por SWD la cueva, los ajustes de av-cam y la actividad; registra con hora
cd "$(dirname "$0")"; rm -f mon.log
while true; do
  t=$(date +%T)
  REQ="cave 0x83fb7400 8 cfg238 0x83edf8bc 4 cfg210 0x83edf894 4 g153 0x83edf7d7 1 tipo 0x83edf7bc 4" timeout 20 openocd -f rdx.cfg 2>&1 | grep -E "^(cave|cfg|g153|tipo)" | sed 's/@0x[0-9a-f]* = //' | tr '\n' ' ' | sed "s/^/$t /" >> mon.log; echo >> mon.log
done
