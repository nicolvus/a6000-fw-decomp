#!/bin/bash
# Espera a que la sonda enumere y lanza el P1 de R48/R49 (forzar modo actualizador); sale al terminar openocd.
D=$(dirname "$0"); export LOGF=$D/p1.log
until lsusb | grep -q 2e8a:000c; do sleep 1; done
echo "sonda detectada $(date +%T)" >> $LOGF
sleep 2
openocd -f "$D/../../e26-recovery/r48_updater_swd.cfg" > $D/openocd.log 2>&1
echo "openocd salió rc=$? $(date +%T)" >> $LOGF
