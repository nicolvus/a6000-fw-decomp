# T6 (guest): mide hasta dónde llega el Android 2.3.7 de nflasha16 sobre el kernel 6.12 de Debian. Solo emulador (no cámara).
# Variables (SHIMENV de run.py): MODE=probe|init|sm|zygote, WAIT=segundos.
export PATH=/bin:/sbin:/usr/bin:/usr/sbin
[ -f /cam/harness.env ] && . /cam/harness.env
echo "T6 uname: $(uname -r)"
insmod /cam/t6mod/${BINDERKO:-binder32}.ko devices=binder 2>&1 | tail -2
[ -f /cam/t6mod/ashmem.ko ] && insmod /cam/t6mod/ashmem.ko 2>&1 | tail -1          # build_ashmem.sh
U=${UIPCKO:-uipc_shared}; [ -f /cam/t6mod/$U.ko ] || U=uipc_stub                    # uipc_shared.ko: /dev/uipc entre procesos (build_uipc.sh)
[ -z "$NOUIPC" ] && insmod /cam/t6mod/$U.ko 2>&1 | tail -1 && echo "T6 uipc: $U"
echo "T6 binder: $(ls -l /dev/binder 2>&1 | cut -c1-60) | misc: $(grep -c binder /proc/misc)"
[ -e /dev/ashmem ] && echo "T6 ashmem: presente" || echo "T6 ashmem: AUSENTE (ashmem_linux no existe en 6.12)"
for d in proc sys dev; do mount --bind /$d /cam/and/$d; done
mount -t tmpfs tmpfs /cam/and/data; mount -t tmpfs tmpfs /cam/and/cache; mount -t tmpfs tmpfs /cam/and/mnt
mkdir -p /cam/and/dev/socket /cam/and/dev/pts; mount -t devpts devpts /cam/and/dev/pts 2>/dev/null
export LD_LIBRARY_PATH=/vendor/lib:/system/lib ANDROID_ROOT=/system ANDROID_DATA=/data
case "${MODE:-sm}" in
 sm)
  chroot /cam/and /system/bin/servicemanager > /tmp/sm.log 2>&1 &
  sleep 3; echo "T6 servicemanager: $(pidof servicemanager || echo MUERTO)"; head -5 /tmp/sm.log
  chroot /cam/and /system/bin/service list 2>&1 | head -5 ;;
 init)
  mkdir -p /cam/and/sbin; ln -sf /init /cam/and/sbin/ueventd
  # el init de Android monta su propio tmpfs en /dev: los «logs» (sin driver logger, retirado del kernel) se crean cuando existe /dev/socket; se leen con tr/grep
  ( while [ ! -d /cam/and/dev/socket ]; do sleep 0.2; done; mkdir -p /cam/and/dev/log; for l in main system radio events; do : > /cam/and/dev/log/$l; chmod 666 /cam/and/dev/log/$l; done ) &
  chroot /cam/and /init > /tmp/init.log 2>&1 &
  sleep ${WAIT:-40}
  echo "T6 procesos:"; ps | grep -vE "\[|ps$|grep" | tail -25
  tail -40 /tmp/init.log | cut -c1-200
  for l in main system; do echo "T6 log $l:"; tr -c '[:print:]' '\n' < /cam/and/dev/log/$l | grep -E '.{6,}' | tail -${LOGN:-60} | cut -c1-200; done ;;
zyg)  # sin init de Android (sin propiedades): servicemanager + zygote a mano; /dev es el devtmpfs del invitado, así que los «logs» persisten
  mkdir -p /cam/and/dev/log; for l in main system radio events; do : > /cam/and/dev/log/$l; chmod 666 /cam/and/dev/log/$l; done
  BCP=$(sed -n 's/^ *export BOOTCLASSPATH //p' /cam/and/init.rc | head -1)
  chroot /cam/and /system/bin/servicemanager > /tmp/sm.log 2>&1 &
  sleep 2
  env ANDROID_ROOT=/system ANDROID_DATA=/data ANDROID_ASSETS=/system/app EXTERNAL_STORAGE=/mnt/sdcard BOOTCLASSPATH="$BCP" LD_LIBRARY_PATH=/system/lib \
    chroot /cam/and $([ -x /cam/and/zygote_launch ] && echo /zygote_launch) /system/bin/app_process -Xzygote /system/bin --zygote --start-system-server > /tmp/zyg.log 2>&1 &
  ZP=$!
  sleep ${WAIT:-60}
  echo "T6 procesos:"; ps | grep -E "app_process|servicemanager|system_server"
  kill -0 $ZP 2>/dev/null && echo "T6 zygote vivo" || { wait $ZP; echo "T6 zygote salida=$?"; }
  echo "T6 data: $(ls /cam/and/data /cam/and/data/dalvik-cache 2>&1 | tr '\n' ' ' | cut -c1-300)"
  echo "T6 zyg.log:"; tail -20 /tmp/zyg.log | cut -c1-200
  for l in main system; do echo "T6 log $l:"; tr -c '[:print:]' '\n' < /cam/and/dev/log/$l | grep -E '.{6,}' | tail -${LOGN:-60} | cut -c1-200; done ;;
esac
dmesg | grep -vE "taints|verification" | tail -${DMN:-40} | cut -c1-220
