# Guion del guest (G22-B): arranca im.elf de la cámara bajo sonyshim.so y muestra el final filtrado del registro.
# Variables (vía SHIMENV de run.py): WAIT (s de espera, 50), TAILN (líneas finales, 40) y las del shim
# (VERB, TIDLOG, CVWAIT, POKE, SKIPFN, TRACEFN, TRACEPEEK, WATCH, DUMPAT, RCVSTACK, BKV).
[ -f /cam/harness.env ] && . /cam/harness.env
export LD_LIBRARY_PATH=/usr/lib
# LIVE=auto (live.py): puerto virtio-serial «a6000ui» con el anfitrión; virtio_mmio es módulo en el kernel de Debian. El shim recibe la ruta /dev/vportNpM.
if [ -n "$LIVE" ]; then
  modprobe virtio_mmio
  for i in 1 2 3 4 5 6 7 8 9 10; do for f in /sys/class/virtio-ports/*/name; do [ "$(cat $f 2>/dev/null)" = a6000ui ] && LIVE=/dev/$(basename $(dirname $f)); done; [ -e "$LIVE" ] && break; sleep 1; done
  export LIVE; echo "LIVE=$LIVE"
fi
# NET (live.py, T5): lista «telnet,wifi». Emulador, no cámara: virtio-net con slirp de QEMU hace de enlace Wi-Fi (la cámara usa ath6kl_sdio + SDIO, sin emular).
# La interfaz se llama ath0 como en libNetService.so/pump.conf de la cámara. DHCP: udhcpc del instalador (la cámara usa su `pump`); telnetd es el busybox de la cámara en /cam
# como lo lanza OpenMemories Tweak (`busybox telnetd -l sh`, puerto 23, root sin contraseña). Resultado en /tmp/net.log (consola).
if [ -n "$NET" ]; then
  modprobe virtio_mmio; modprobe virtio_net
  for i in 1 2 3 4 5 6 7 8 9 10; do [ -e /sys/class/net/eth0 ] && break; sleep 1; done
  ip link set eth0 name ath0; ip link set ath0 up
  printf '%s\n' '#!/bin/sh' '[ "$1" = bound ] || [ "$1" = renew ] || exit 0' 'ip addr add $ip/${mask:-24} dev $interface' '[ -n "$router" ] && ip route add default via ${router%% *}' \
    'for d in $dns; do echo "nameserver $d"; done > /etc/resolv.conf; cp /etc/resolv.conf /cam/etc/resolv.conf' > /tmp/dhcp.sh; chmod +x /tmp/dhcp.sh
  udhcpc -i ath0 -n -q -s /tmp/dhcp.sh 2>&1 | tail -3
  case ",$NET," in *,telnet,*)
    # /cam no trae enlaces de applets (sh, ls…): se crean aparte en /cam/.net/bin (añadido del emulador) para no alterar el entorno de im.elf
    mkdir -p /cam/.net/bin /cam/dev/pts; mount -t devpts devpts /cam/dev/pts
    for a in $(chroot /cam /bin/busybox 2>&1 | sed -n '/Currently defined/,$p' | sed 1d | tr -d ' \n' | tr ',' ' '); do ln -sf /bin/busybox /cam/.net/bin/$a; done
    PATH=/.net/bin:/bin:/sbin:/usr/bin:/usr/sbin chroot /cam /bin/busybox telnetd -l /.net/bin/sh && echo "NET telnetd: puerto 23 (root, sin contraseña)" ;;
  esac
  ip -4 addr show ath0 | grep inet; echo "NET listo: $NET"
fi
# IMSPLIT=1: como bootin.elf, un proceso im.elf por letra (s g r u l i a) y uno final sin argumentos; cada letra activa una fase del IMDB
# (u = fase 4: appFw.so → Application_System_Init, el hilo de la UI). Sin IMSPLIT: un solo proceso con todas las letras (modo histórico).
run_im() { ( LD_PRELOAD=/usr/lib/sonyshim.so chroot /cam /usr/bin/im.elf $1 > /tmp/$2.log 2>&1; echo "EXIT=$?" >> /tmp/$2.log ) & }
if [ -n "$IMSPLIT" ]; then
  for a in ${IMLETTERS:-s g r u l i a}; do run_im $a imp_$a; done
  [ -n "$IMNOARG" ] && run_im "" imp_n
  : > /tmp/im_s.log
else
  run_im "${IMARGS:-s g r u l i a}" im_s
fi
# PMWAIT=s (diagnóstico, fuera del proceso im.elf): a los s segundos y cada PMEVERY (60) s vuelca por la consola comm/estado/wchan/syscall de cada hilo de im.elf y su mapa de módulos
# («PM» en consola.log); sirve para construir el grafo de espera de un interbloqueo (syscall: nº, argumentos, sp, pc).
if [ -n "$PMWAIT" ]; then
  echo 1 > /proc/sys/debug/exception-trace 2>/dev/null; ls /proc/sys/debug 2>/dev/null | sed "s/^/PM sysdebug /"
  ( sleep $PMWAIT; for r in 1 2 3; do PP=$(for d in /proc/[0-9]*; do echo "$(ls $d/task 2>/dev/null | wc -l) ${d#/proc/}"; done | sort -rn | head -1 | cut -d" " -f2); echo "PM-BEGIN $r pid=$PP"; tail -4 /tmp/im_s.log | cut -c1-200 | sed "s/^/PM imlog /"; grep -a -A12 "pila (sig 11" /tmp/im_s.log | tail -26 | cut -c1-150 | sed "s/^/PM segv /"; grep -a "EXIT=" /tmp/im_s.log | sed "s/^/PM imexit /"; dmesg | grep -a "unhandled\|segfault\|potentially" | tail -6 | sed "s/^/PM dmesg /"; ps | grep -a "im.elf\|busybox" | head -5 | sed "s/^/PM ps /"
      for t in /proc/$PP/task/*; do echo "PM $(basename $t) $(cat $t/comm) st=$(cut -d' ' -f3 $t/stat) wchan=$(cat $t/wchan) sys=$(cat $t/syscall)"; done
      [ $r = 1 ] && grep -a "\.so\|im.elf" /proc/$PP/maps | grep -a "r-xp\|r--p" | awk '{print "PMMAP",$1,$6}'
      echo "PM-END $r"; sleep ${PMEVERY:-60}; done ) &
fi
sleep ${WAIT:-50}
if [ -n "$IMSPLIT" ]; then for a in ${IMLETTERS:-s g r u l i a} $([ -n "$IMNOARG" ] && echo n); do echo "== imp_$a: $(grep -ac 'dlopen(.*) -> 0x' /tmp/imp_$a.log) modulos, $(grep -ac '' /tmp/imp_$a.log) lineas, EXIT: $(grep -a '^EXIT=' /tmp/imp_$a.log)"; echo "### imp_$a" >> /tmp/im_s.log; cat /tmp/imp_$a.log >> /tmp/im_s.log; done; fi
P=$(pidof im.elf | cut -d' ' -f1)
if [ -n "$TOPTHR" ]; then  # TOPTHR=1: hilos que más CPU gastan en 5 s (ticks de utime+stime), para buscar sondeos que roban CPU emulada
  for t in /proc/[0-9]*/task/*; do echo "$t $(cut -d' ' -f14,15 $t/stat 2>/dev/null) $(cat $t/comm 2>/dev/null)"; done > /tmp/top1; sleep 5
  for t in /proc/[0-9]*/task/*; do echo "$t $(cut -d' ' -f14,15 $t/stat 2>/dev/null) $(cat $t/comm 2>/dev/null)"; done > /tmp/top2
  awk 'NR==FNR{a[$1]=$2+$3;next}{d=$2+$3-a[$1]; if(d>2) print d, $1, $4}' /tmp/top1 /tmp/top2 | sort -rn | head -20 > /tmp/top3; sed 's/^/TOPTHR /' /tmp/top3
  # TOPTHR=2: además, 40 muestras de /proc/TID/syscall (nº de llamada, 2 primeros argumentos) de los 8 hilos más gastones → TOPSYS
  if [ "$TOPTHR" = 2 ]; then for t in $(head -8 /tmp/top3 | cut -d' ' -f2); do for i in $(seq 40); do echo "$(cat $t/comm) $(cut -d' ' -f1-3 $t/syscall 2>/dev/null)"; done; done | sort | uniq -c | sort -rn | head -40 | sed 's/^/TOPSYS /'; fi
fi
[ -n "$SYSTAT" ] && grep -a "SYSTAT" /tmp/im_s.log | tail -${SYSTATN:-60} | sed "s/^\[shim\] //"  # SYSTAT=1 (shim): ioctl emulados que giran, por hilo
echo "alive=$P threads=$(ls /proc/$P/task 2>/dev/null | wc -l) lineas=$(grep -ac '' /tmp/im_s.log) modulos=$(grep -ac 'dlopen(.*) -> 0x' /tmp/im_s.log)"
grep -a "EXIT=\|ABORT\|Segmentation\|Aborted\|dlopen(.*) -> 0x0\|respuesta a" /tmp/im_s.log | tail -8 | cut -c1-160
echo "--- ultimas lineas (filtradas)"
grep -av "snd_msg a la cola\|valloc\|uipc free\|wait_cb\|094_\|wai_sem\|sig_sem\|LOG $\|dynamic_id sem\|NOFILTER_x\|LOGRAW" /tmp/im_s.log | tail -${TAILN:-40} | cut -c1-190
if [ -n "$FULLLOG" ]; then  # registro completo del guest por la consola; run.py lo decodifica en DIR_TRABAJO/guest.log
  tr -d '\r' < /tmp/im_s.log > /cam/tmp/im_s.log  # el busybox del instalador no trae gzip: usar el de la cámara (chroot)
  if chroot /cam /bin/busybox gzip -c /dev/null > /dev/null 2>&1; then GZ="chroot /cam /bin/busybox gzip -9 -c /tmp/im_s.log"; else GZ="cat /cam/tmp/im_s.log"; fi
  echo "=====GUESTLOG-BEGIN $GZ"; $GZ | base64; echo "=====GUESTLOG-END"
  for f in /cam/tmp/area_*.bin /cam/tmp/gpu.txt; do [ -s "$f" ] || continue; b=${f##*/}; echo "=====GUESTFILE-BEGIN $b"; chroot /cam /bin/busybox gzip -1 -c /tmp/$b | base64; echo "=====GUESTFILE-END"; done
fi
