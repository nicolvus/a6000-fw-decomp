#!/usr/bin/env python3
"""Descarga fotos de la SD de la cámara sin USB ni adb: la cámara las sube con `ftpput` (busybox) a un FTP temporal del PC.

Uso: camera_pull.py DESTINO [N=1]   (las N últimas DSC*.ARW de la carpeta DCIM más reciente; telnet 23)
El FTP escucha solo durante la descarga, en la IP del PC hacia la cámara, con usuario y clave de un solo uso."""
import os
import secrets
import socket
import sys
import threading
from pathlib import Path

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from camera_telnet import run

HOST = os.environ.get("A6000_HOST", "192.168.1.29")
DCIM = "/android/mnt/sdcard/DCIM"


def local_ip() -> str:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((HOST, 23))
        return s.getsockname()[0]


def newest(n: int) -> tuple[str, list[str]]:
    folder = sorted(run(HOST, [f"ls {DCIM}"])[0].split())[-1]
    files = sorted(f for f in run(HOST, [f"ls {DCIM}/{folder}"])[0].split() if f.startswith("DSC") and f.endswith(".ARW"))
    return folder, files[-n:]


def main() -> None:
    dest = Path(sys.argv[1])
    dest.mkdir(parents=True, exist_ok=True)
    folder, files = newest(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    user, pw = "a6000", secrets.token_hex(8)
    auth = DummyAuthorizer()
    auth.add_user(user, pw, str(dest), perm="elw")
    handler = FTPHandler
    handler.authorizer = auth
    server = FTPServer((local_ip(), 2121), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        for f in files:
            out = run(HOST, [f"busybox ftpput -P 2121 -u {user} -p {pw} {local_ip()} {f} {DCIM}/{folder}/{f}; echo rc=$?"], timeout=300)[0]
            size = (dest / f).stat().st_size if (dest / f).exists() else 0
            print(f, out.strip()[-300:], f"{size} B", flush=True)
    finally:
        server.close_all()


if __name__ == "__main__":
    main()
