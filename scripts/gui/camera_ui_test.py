#!/usr/bin/env python3
"""Prueba reversible del menú «Silent Shooting» (A6300) en la A6000 por telnet + FTP temporal (montajes `bind` en RAM).

NADA toca la cámara sin `--execute`; sin él solo imprime lo que haría. Un reinicio de la cámara revierte los montajes.
Subcomandos:
  probe    lectura (más un montaje de prueba en /tmp): mounts, hashes de /usr, proceso de la UI, espacio, soporte de `mount --bind`
  deploy   sube el paquete a /android/silentmenu, comprueba md5 y monta cada fichero sobre su original (exige probe correcto)
  restart-ui  mata y relanza im.elf (cwd, entorno y argumentos del proceso actual); sin él el montaje no se ve
  revert   desmonta los `bind` y borra /tmp/silentmenu
Uso: camera_ui_test.py PAQUETE {probe|deploy|revert} [--execute] [--host IP]
Sin volcado NVRAM previo (decisión del usuario, 07-11-2026: ya hay suficientes copias).
La UI carga los .so al arrancar: el montaje solo se ve tras reiniciar la UI/cámara (reiniciar borra el montaje: ver docs/gui/g09 §7).
"""
import argparse
import json
import os
import secrets
import socket
import sys
import threading
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
from camera_telnet import run

REMOTE = "/android/data/silentmenu"  # vfat interno (nflasha17, 104 MB). /tmp es vfat de 5 MB; /android es tmpfs con ~14 MB libres; la SD es FUSE servido por im.elf (no vale como origen del bind)
TARGET = {"lib": "/usr/lib", "share/app": "/usr/share/app"}


def destino(rel: str) -> str:
    d, f = rel.rsplit("/", 1)
    return f"{TARGET[d]}/{f}"


def sh(host, cmd, execute, timeout=60.0):
    print(f"$ {cmd}")
    if not execute:
        return ""
    out = run(host, [cmd], timeout=timeout)[0].strip()
    print(out)
    return out


def probe(host, pkg, execute):
    man = json.loads((pkg / "MANIFEST.json").read_text())
    sh(host, "uname -a; busybox grep -E ' /usr | /tmp | /android | /setting ' /proc/mounts; busybox grep -E 'MemFree|Cached' /proc/meminfo", execute)
    ok = True
    for rel, m in sorted(man["md5"].items()):
        out = sh(host, f"busybox md5sum {destino(rel)}", execute)
        if execute and m["original"] not in out:
            print(f"  !! {rel}: el md5 de la cámara NO es el del firmware 3.21 de referencia ({m['original']})")
            ok = False
    sh(host, "for p in /proc/[0-9]*; do n=$(busybox grep Name $p/status | busybox cut -f2); case \"$n\" in im.elf|bootin.elf) "
             "echo \"${p#/proc/} $n ppid=$(busybox grep PPid $p/status | busybox cut -f2)\";; esac; done", execute)
    sh(host, "busybox grep -l viewUnified2 /proc/[0-9]*/maps 2>/dev/null", execute)
    sh(host, "mkdir -p /tmp/bt && : > /tmp/bt/a && : > /tmp/bt/b && busybox mount --bind /tmp/bt/a /tmp/bt/b && echo BIND_OK; "
             "busybox umount /tmp/bt/b; rm -rf /tmp/bt", execute)
    if execute:
        rw = sh(host, "busybox grep ' /android/data ' /proc/mounts", True)
        if " rw," not in rw:
            print("  !! /android/data no está montado rw")
            ok = False
    print("probe:", "OK" if ok else "FALLO" if execute else "(simulado)")
    return ok


def deploy(host, pkg, execute):
    man = json.loads((pkg / "MANIFEST.json").read_text())
    if execute and not probe(host, pkg, True):
        sys.exit("probe fallido: no se despliega")
    active = sh(host, "busybox ls -l /proc/[0-9]*/fd 2>/dev/null | busybox grep -o 'share/app/string_[a-z]*.uxc' | busybox sort -u", execute).split()
    keep = {f"share/app/{Path(a).name}" for a in active}
    man["md5"] = {r: m for r, m in man["md5"].items() if r.startswith("lib/") or r in keep or not execute}
    print("ficheros a desplegar:", sorted(man["md5"]))
    user, pw = "a6000", secrets.token_hex(8)
    ip = "0.0.0.0"
    if execute:
        from pyftpdlib.authorizers import DummyAuthorizer
        from pyftpdlib.handlers import FTPHandler
        from pyftpdlib.servers import FTPServer

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect((host, 23))
            ip = s.getsockname()[0]
        auth = DummyAuthorizer()
        auth.add_user(user, pw, str(pkg), perm="elr")
        FTPHandler.authorizer = auth
        server = FTPServer((ip, 2121), FTPHandler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        sh(host, f"mkdir -p {REMOTE}", execute)
        for rel in sorted(man["md5"]):
            name = rel.replace("/", "_")
            sh(host, f"busybox ftpget -P 2121 -u {user} -p {pw} {ip} {REMOTE}/{name} {rel}; echo rc=$?", execute, 600)
            out = sh(host, f"busybox md5sum {REMOTE}/{name}", execute)
            if execute and man["md5"][rel]["parcheado"] not in out:
                sys.exit(f"md5 incorrecto tras la subida de {rel}; nada montado (revert para limpiar)")
        for rel in sorted(man["md5"]):
            sh(host, f"busybox mount --bind {REMOTE}/{rel.replace('/', '_')} {destino(rel)} && echo MONTADO {destino(rel)}", execute)
    finally:
        if execute:
            server.close_all()
    print("Montado. La UI sigue con los .so antiguos hasta reiniciarla; ver docs/gui/g09 §7 (reiniciar la cámara borra el montaje).")


UI_ENV = "LT_ABORTREASON=0 HOME=/ TERM=linux TOPRC=/etc/toprc PATH=/sbin:/bin:/usr/sbin:/usr/bin:/devel/usr/bin MALLOC_OPTIONS=gfffffffff"
UI_CMD = "/usr/bin/im.elf debug s g r u l i a lazy-global"  # copiado de /proc/<pid>/cmdline y environ del im.elf en marcha


def restart_ui(host, execute):
    """Mata y relanza im.elf con el mismo cwd, entorno y argumentos (ppid=1, sin supervisor en la cámara)."""
    pid = sh(host, "for p in /proc/[0-9]*; do [ \"$(busybox grep Name $p/status | busybox cut -f2)\" = im.elf ] && echo ${p#/proc/}; done", execute)
    sh(host, f"busybox kill {pid.split()[-1] if pid else '<pid>'}; busybox sleep 2", execute)
    sh(host, f"cd /usr/share/app && busybox env -i {UI_ENV} busybox nohup {UI_CMD} </dev/null >/dev/console 2>&1 &", execute)
    sh(host, "busybox sleep 6; for p in /proc/[0-9]*; do [ \"$(busybox grep Name $p/status | busybox cut -f2)\" = im.elf ] && echo im.elf ${p#/proc/} && busybox grep viewUnified2 $p/maps; done", execute, 90)


def revert(host, pkg, execute):
    man = json.loads((pkg / "MANIFEST.json").read_text())
    for rel in sorted(man["md5"]):
        sh(host, f"busybox umount {destino(rel)} 2>/dev/null; echo {rel} rc=$?", execute)
    sh(host, f"rm -rf {REMOTE}", execute)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paquete", type=Path)
    ap.add_argument("accion", choices=("probe", "deploy", "restart-ui", "revert"))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--host", default=os.environ.get("A6000_HOST", "192.168.1.29"))
    a = ap.parse_args()
    {"probe": lambda: probe(a.host, a.paquete, a.execute), "deploy": lambda: deploy(a.host, a.paquete, a.execute),
     "restart-ui": lambda: restart_ui(a.host, a.execute), "revert": lambda: revert(a.host, a.paquete, a.execute)}[a.accion]()


if __name__ == "__main__":
    main()
