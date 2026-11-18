#!/usr/bin/env python3
"""Ventana de captura alrededor de una acción física en la cámara (TRAZA-VM grupo 2, docs/gui/g85).

  camera_evento.py inicio NOMBRE        arranca `getevent -t` (teclas/dial) en segundo plano en la cámara
  camera_evento.py fin NOMBRE DESTINO   lo para y trae a DESTINO/NOMBRE/: búfer de log del firmware (RAM física
                                        0x83400000, 1,2 MiB) y su texto, logcat, dmesg, dumpsys battery,
                                        /proc/mounts y /proc/partitions, y el getevent
Solo lectura salvo ficheros temporales en tmpfs (/tmp y /android/mnt/obb = /mnt/obb en Android), que se borran.
Las órdenes de Android corren con root en el chroot /android mediante guiones cortos (run() pierde la salida de
líneas largas). A6000_HOST=ip."""
import re
import sys
from pathlib import Path

import camera_get as cg
from camera_telnet import run

OBB = cg.TMP_ROOT  # /android/mnt/obb


def android(nombre: str, orden: str, salida: str, fondo: bool = False) -> str:
    """Escribe un guion en el tmpfs y devuelve la orden corta que lo ejecuta en el chroot de Android."""
    run(cg.HOST, [f"echo 'PATH=/system/bin; {orden} > /mnt/obb/{salida} 2>&1' > {OBB}/{nombre}.sh"])
    return f"chroot /android /system/bin/sh /mnt/obb/{nombre}.sh" + (" &" if fondo else "")


def inicio(nombre: str) -> None:
    run(cg.HOST, [android("ge", "exec getevent -t", f"ge_{nombre}.txt", fondo=True)])
    print(f"getevent en marcha: {OBB}/ge_{nombre}.txt")


def fin(nombre: str, dest: Path) -> None:
    d = dest / nombre
    d.mkdir(parents=True, exist_ok=True)
    run(cg.HOST, ["killall getevent", android("lc", "logcat -d -v time", "logcat.txt"),
                  android("bt", "dumpsys battery", "bateria.txt"), f"dmesg > {OBB}/dmesg.txt",
                  f"cat /proc/mounts /proc/partitions > {OBB}/montajes.txt",
                  f"dd if=/dev/mem of=/tmp/log.bin bs=4096 skip={0x83400000 // 4096} count={0x130000 // 4096}"],
        timeout=120)
    try:
        for f in ("logcat.txt", "bateria.txt", "dmesg.txt", "montajes.txt", f"ge_{nombre}.txt", "/tmp/log.bin"):
            try:
                cg.traer(d, f if f.startswith("/") else f"{OBB}/{f}")
            except SystemExit as e:
                print(e)
    finally:
        run(cg.HOST, [f"rm -f /tmp/log.bin {OBB}/*.txt {OBB}/*.sh"])
    # Texto del búfer de log: tramos imprimibles de ≥ 6 caracteres.
    if (d / "log.bin").exists():
        txt = (d / "log.bin").read_bytes().decode("latin1")
        (d / "log.txt").write_text("\n".join(m.group(0) for m in re.finditer(r"[\x20-\x7e\t]{6,}", txt)))


def main() -> None:
    if len(sys.argv) >= 3 and sys.argv[1] == "inicio":
        inicio(sys.argv[2])
    elif len(sys.argv) >= 4 and sys.argv[1] == "fin":
        fin(sys.argv[2], Path(sys.argv[3]))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
