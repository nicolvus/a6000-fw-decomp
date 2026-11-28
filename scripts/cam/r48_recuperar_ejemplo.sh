#!/bin/bash
cd /tmp/r48
rm -f auto.log r48.log
./auto.sh > auto.log 2>&1 || exit 1
grep -q UPDATER_OK auto.log || exit 1
R=/home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
S=/tmp/claude-1000/-home-nicolas-Documents-a6000/fe0b7d92-e05d-4ac7-a8ea-9eece9d74ea8/scratchpad
esperar() { for i in $(seq 1 60); do lsusb | grep -qi 054c:03e2 && break; sleep 3; done; sleep 25; }
sleep 20; cd $R
esperar
$S/venv/bin/python -u scripts/cam/ushell.py $R "ls -l /setting; busybox rm /setting/init_bk.bak; echo rm=\$?; busybox sync; ls -l /setting" > analysis/gui/ushell-rm-initbk-5-20261128.log 2>&1
echo "EXIT ushell $?" >> analysis/gui/ushell-rm-initbk-5-20261128.log
esperar
cd $R/references/pmca
L=$R/analysis/gui/install-revivir-408-b.log
PYTHONPATH=. $S/venv/bin/python -u pmca-console.py firmware -f $R/build/wbi_propio/revivir/package-4.08/firmware_packed.dat > $L 2>&1
echo "EXIT $?" >> $L
