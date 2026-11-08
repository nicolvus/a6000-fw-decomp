#!/usr/bin/env python3
"""Prueba reversible del menú «Silent Shooting» (A6300) en la A6000 por telnet + FTP temporal (montajes `bind` en RAM).

NADA toca la cámara sin `--execute`; sin él solo imprime lo que haría. Un reinicio de la cámara revierte los montajes.
Subcomandos:
  probe    lectura (más un montaje de prueba en /tmp): mounts, hashes de /usr, proceso de la UI, espacio, soporte de `mount --bind`
  deploy   sube el paquete a /android/silentmenu, comprueba md5 y monta cada fichero sobre su original (exige probe correcto)
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

REMOTE = "/android/silentmenu"  # tmpfs en RAM (/tmp de la cámara es vfat de 5 MB: no cabe el paquete, ~12 MB)
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
    sh(host, "uname -a; grep -E ' /usr | /tmp | /android | /setting ' /proc/mounts; df /android /tmp | tail -n 3", execute)
    ok = True
    for rel, m in sorted(man["md5"].items()):
        out = sh(host, f"busybox md5sum {destino(rel)}", execute)
        if execute and m["original"] not in out:
            print(f"  !! {rel}: el md5 de la cámara NO es el del firmware 3.21 de referencia ({m['original']})")
            ok = False
    sh(host, "for p in /proc/[0-9]*; do c=$(tr '\\0' ' ' < $p/cmdline 2>/dev/null); case \"$c\" in *im.elf*|*orb-server*|*init*) "
             "echo \"${p#/proc/} ppid=$(grep PPid $p/status | cut -f2) $c\";; esac; done", execute)
    sh(host, "grep -l viewUnified2 /proc/[0-9]*/maps 2>/dev/null", execute)
    sh(host, "mkdir -p /tmp/bt && : > /tmp/bt/a && : > /tmp/bt/b && busybox mount --bind /tmp/bt/a /tmp/bt/b && echo BIND_OK; "
             "busybox umount /tmp/bt/b; rm -rf /tmp/bt", execute)
    if execute:
        free = sh(host, "df -k /android | tail -n 1 | tr -s ' ' | cut -d' ' -f4", True)
        if not free.isdigit() or int(free) < 16384:
            print(f"  !! espacio libre en /android insuficiente ({free} KB; hacen falta ~16 MB)")
            ok = False
    print("probe:", "OK" if ok else "FALLO" if execute else "(simulado)")
    return ok


def deploy(host, pkg, execute):
    man = json.loads((pkg / "MANIFEST.json").read_text())
    if execute and not probe(host, pkg, True):
        sys.exit("probe fallido: no se despliega")
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


def revert(host, pkg, execute):
    man = json.loads((pkg / "MANIFEST.json").read_text())
    for rel in sorted(man["md5"]):
        sh(host, f"busybox umount {destino(rel)}; echo rc=$?", execute)
    sh(host, f"rm -rf {REMOTE}", execute)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paquete", type=Path)
    ap.add_argument("accion", choices=("probe", "deploy", "revert"))
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--host", default=os.environ.get("A6000_HOST", "192.168.1.29"))
    a = ap.parse_args()
    {"probe": lambda: probe(a.host, a.paquete, a.execute), "deploy": lambda: deploy(a.host, a.paquete, a.execute),
     "revert": lambda: revert(a.host, a.paquete, a.execute)}[a.accion]()


if __name__ == "__main__":
    main()
