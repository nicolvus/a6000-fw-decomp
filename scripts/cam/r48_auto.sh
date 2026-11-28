#!/bin/bash
# Repite R48 (BootMode 3 por SWD) en cada apagado/encendido hasta que aparezca el actualizador (054c:03e2).
cd /tmp/r48
for n in $(seq 1 12); do
  rm -f r48.log; echo "intento $n: armando R48 $(date +%T)"
  LOGF=/tmp/r48/r48.log openocd -f r48_updater_swd.cfg > openocd-$n.out 2>&1
  cp r48.log r48-$n.log
  echo "intento $n fin: $(tail -1 r48.log)"
  for i in $(seq 1 30); do lsusb | grep -qi 054c:03e2 && { echo "UPDATER_OK intento=$n"; exit 0; }; sleep 2; done
  echo "intento $n: sin USB del actualizador; reintento (apaga y enciende la camara)"
done
echo "AGOTADOS"
