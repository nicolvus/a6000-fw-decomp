# Guion del guest (G22-B): arranca im.elf de la cámara bajo sonyshim.so y muestra el final filtrado del registro.
# Variables (vía SHIMENV de run.py): WAIT (s de espera, 50), TAILN (líneas finales, 40) y las del shim
# (VERB, TIDLOG, CVWAIT, POKE, SKIPFN, TRACEFN, TRACEPEEK, WATCH, DUMPAT, RCVSTACK, BKV).
[ -f /cam/harness.env ] && . /cam/harness.env
export LD_LIBRARY_PATH=/usr/lib
# IMSPLIT=1: como bootin.elf, un proceso im.elf por letra (s g r u l i a) y uno final sin argumentos; cada letra activa una fase del IMDB
# (u = fase 4: appFw.so → Application_System_Init, el hilo de la UI). Sin IMSPLIT: un solo proceso con todas las letras (modo histórico).
run_im() { ( LD_PRELOAD=/usr/lib/sonyshim.so chroot /cam /usr/bin/im.elf $1 > /tmp/$2.log 2>&1; echo "EXIT=$?" >> /tmp/$2.log ) & }
if [ -n "$IMSPLIT" ]; then
  for a in ${IMLETTERS:-s g r u l i a}; do run_im $a im_$a; done
  [ -n "$IMNOARG" ] && run_im "" im_n
  : > /tmp/im_s.log
else
  run_im "s g r u l i a" im_s
fi
sleep ${WAIT:-50}
if [ -n "$IMSPLIT" ]; then for a in ${IMLETTERS:-s g r u l i a} $([ -n "$IMNOARG" ] && echo n); do echo "== im_$a: $(grep -ac 'dlopen(.*) -> 0x' /tmp/im_$a.log) modulos, $(grep -ac '' /tmp/im_$a.log) lineas, EXIT: $(grep -a '^EXIT=' /tmp/im_$a.log)"; cat /tmp/im_$a.log >> /tmp/im_s.log; done; fi
P=$(pidof im.elf | cut -d' ' -f1)
echo "alive=$P threads=$(ls /proc/$P/task 2>/dev/null | wc -l) lineas=$(grep -ac '' /tmp/im_s.log) modulos=$(grep -ac 'dlopen(.*) -> 0x' /tmp/im_s.log)"
grep -a "EXIT=\|ABORT\|Segmentation\|Aborted\|dlopen(.*) -> 0x0\|respuesta a" /tmp/im_s.log | tail -8 | cut -c1-160
echo "--- ultimas lineas (filtradas)"
grep -av "snd_msg a la cola\|valloc\|uipc free\|wait_cb\|094_\|wai_sem\|sig_sem\|LOG $\|dynamic_id sem\|NOFILTER_x\|LOGRAW" /tmp/im_s.log | tail -${TAILN:-40} | cut -c1-190
if [ -n "$FULLLOG" ]; then  # registro completo del guest por la consola; run.py lo decodifica en DIR_TRABAJO/guest.log
  tr -d '\r' < /tmp/im_s.log > /cam/tmp/im_s.log  # el busybox del instalador no trae gzip: usar el de la cámara (chroot)
  if chroot /cam /bin/busybox gzip -c /dev/null > /dev/null 2>&1; then GZ="chroot /cam /bin/busybox gzip -9 -c /tmp/im_s.log"; else GZ="cat /cam/tmp/im_s.log"; fi
  echo "=====GUESTLOG-BEGIN $GZ"; $GZ | base64; echo "=====GUESTLOG-END"
fi
