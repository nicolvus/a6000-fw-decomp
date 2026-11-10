# Guion del guest (G22-B): arranca im.elf de la cámara bajo sonyshim.so y muestra el final filtrado del registro.
# Variables (vía SHIMENV de run.py): WAIT (s de espera, 50), TAILN (líneas finales, 40) y las del shim
# (VERB, TIDLOG, CVWAIT, POKE, SKIPFN, TRACEFN, TRACEPEEK, WATCH, DUMPAT, RCVSTACK, BKV).
[ -f /cam/harness.env ] && . /cam/harness.env
export LD_LIBRARY_PATH=/usr/lib
( LD_PRELOAD=/usr/lib/sonyshim.so chroot /cam /usr/bin/im.elf s g r u l i a > /tmp/im_s.log 2>&1; echo "EXIT=$?" >> /tmp/im_s.log ) &
sleep ${WAIT:-50}
P=$(pidof im.elf)
echo "alive=$P threads=$(ls /proc/$P/task 2>/dev/null | wc -l) lineas=$(grep -ac '' /tmp/im_s.log) modulos=$(grep -ac 'dlopen(.*) -> 0x' /tmp/im_s.log)"
grep -a "EXIT=\|ABORT\|Segmentation\|Aborted\|dlopen(.*) -> 0x0\|respuesta a" /tmp/im_s.log | tail -8 | cut -c1-160
echo "--- ultimas lineas (filtradas)"
grep -av "snd_msg a la cola\|valloc\|uipc free\|wait_cb\|094_\|wai_sem\|sig_sem\|LOG $\|dynamic_id sem\|NOFILTER_x\|LOGRAW" /tmp/im_s.log | tail -${TAILN:-40} | cut -c1-190
