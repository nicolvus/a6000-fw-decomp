#!/usr/bin/env python3
"""Cuenta ocurrencias reales de cadenas clave en el flujo descomprimido.

Sirve para separar un literal de .rodata (constante en todos los perfiles) de una
linea EMITIDA (aparece una vez mas). Uso: zstd -dc estado.zst | contar_agujas.py
Salida: perfil<TAB>aguja<TAB>n   (una linea por aguja)
"""
import sys

AGUJAS = [
    b"FlashLoadMp4 : MP4 Load Completed",
    b"FlashLoadDcf : DCF Flash Load Success.",
    b"LoadAvi :  Load OK",
    b"DCF Disc Load Success",
    b"Dcf Re-Load Success",
    b"MountCmd : Flash Mount Error",
    b"FlashLoadMp4 : CreateAndLoad Error",
    b"ErrCd: 0xB0800001",
    b"LoadSub : MP4 Load Error.",
    b"AviSeqPlay.cpp Error=",
    b"PlayMovie",
    b"PbStart",
]

CARRY = 256
cuentas = [0] * len(AGUJAS)
buf = b""
while True:
    ch = sys.stdin.buffer.read(1 << 22)
    if not ch:
        break
    buf += ch
    cuerpo, buf = buf[:-CARRY], buf[-CARRY:]
    for i, a in enumerate(AGUJAS):
        cuentas[i] += cuerpo.count(a)
for a, n in zip(AGUJAS, cuentas):
    print(f"{a.decode('ascii', 'replace')}\t{n}")
