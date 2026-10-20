#!/usr/bin/env python3
"""Ejecuta comandos en el telnetd de la cámara (OpenMemories Tweak, root, sin login).

Uso: camera_telnet.py [--host 192.168.1.29] 'cmd1' 'cmd2' ...
Cada comando se envía con un marcador de fin para delimitar su salida.
"""
import argparse
import re
import socket
import time

IAC = 255


def _clean(data: bytes) -> str:
    out, i = bytearray(), 0
    while i < len(data):
        if data[i] == IAC and i + 2 < len(data):
            i += 3
        else:
            out.append(data[i])
            i += 1
    return out.decode("utf-8", "replace").replace("\r", "")


def run(host: str, cmds: list[str], port: int = 23, timeout: float = 20.0) -> list[str]:
    s = socket.create_connection((host, port), timeout=timeout)
    s.settimeout(0.5)

    def drain(until: bytes | None = None) -> bytes:
        buf, end = b"", time.time() + timeout
        while time.time() < end:
            try:
                chunk = s.recv(65536)
            except socket.timeout:
                if until is None:
                    break
                continue
            if not chunk:
                break
            buf += chunk
            if until and until in buf:
                break
        return buf

    drain()
    results = []
    for n, c in enumerate(cmds):
        mark = f"__END{n}__"
        sep = "\n" if c.rstrip().endswith("&") else "; "  # "&; echo" es error de sintaxis
        s.sendall(f"{c}{sep}echo {mark}\n".encode())
        raw = _clean(drain(f"\n{mark}".encode()))
        body = raw.rsplit(mark, 1)[0]
        # elimina el eco del comando 
        body = re.sub(r"^.*?echo " + mark + r"\n", "", body, count=1, flags=re.S)
        results.append(body)
    s.close()
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="192.168.1.29")
    ap.add_argument("cmds", nargs="+")
    a = ap.parse_args()
    for c, r in zip(a.cmds, run(a.host, a.cmds)):
        print(f"$ {c}\n{r}")
