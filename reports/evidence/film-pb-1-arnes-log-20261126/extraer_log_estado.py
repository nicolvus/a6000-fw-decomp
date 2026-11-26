#!/usr/bin/env python3
"""Extrae y deduplica las líneas de log del MMgr de un estado.zst del arnés.

Uso: zstd -dc <estado.zst> | extraer_log_estado.py <salida.txt>
"""
import re
import sys

PAT = re.compile(
    rb"\[(AVIMMGR|MP4IFO|XAVCIFO|MMGR|AVI|MSV|DCF|MprIf|MprCnv|CACHE|StillCache)\]"
    rb"\[?[^\]\r\n]{0,6}\]?[^\r\n\x00]{0,160}"
)


def main(salida: str) -> None:
    vistos: set[bytes] = set()
    buf = b""
    with open(salida, "wb") as out:
        for chunk in iter(lambda: sys.stdin.buffer.read(1 << 20), b""):
            buf = buf[-4096:] + chunk
            for m in PAT.finditer(buf):
                s = m.group().strip()
                if len(s) < 8 or s in vistos:
                    continue
                vistos.add(s)
                out.write(s + b"\n")
    print(f"líneas únicas: {len(vistos)}")


if __name__ == "__main__":
    main(sys.argv[1])
