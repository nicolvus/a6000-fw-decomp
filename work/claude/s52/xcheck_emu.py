#!/usr/bin/env python3
"""Arnés Unicorn mínimo e independiente (Claude, S52 fase C) para SetExposure IMX235 0x436f4168 / IMX210 0x436d6f6c.

Diferencias con el arnés Codex: arranca en la ENTRADA real de la función (incluye prólogo y escrituras SHR), resuelve
GOT/PIC con los bytes del blob, sustituye cada `bl` externo por retorno (r0 = puntero a zona de trabajo) y se detiene en
el bloque común posterior al switch. Rellena los campos con 0x00 y con 0xff para separar bits puestos/borrados.
Uso: ~/.venvs/re/bin/python -I work/claude/s52/xcheck_emu.py  -> JSON por stdout. No ejecuta firmware real en hardware."""
import json
import struct
import sys
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_WRITE,
    UC_MODE_THUMB,
    UC_PROT_ALL,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_SP,
)

ROOT = Path(__file__).resolve().parents[3]
B = 0x43541000
OBJ, PAR, SCR, STK, STOPA = 0x60000000, 0x60100000, 0x60200000, 0x60400000, 0x60500000
CFG = {  # entrada, rango de la función, dirección de parada (tras el switch), offset de la comprobación ==0x11
    'imx235': ('a7s', 0x436f4168, 0x436f4400, 0x436f430a, 0x1ac),
    'imx210': ('a6000', 0x436d6f6c, 0x436d7300, 0x436d71e4, 0x170),
}


def run(sensor, mode, fill):
    fw, entry, end, stop, _off11 = CFG[sensor]
    blob = (ROOT / f'work/claude/input/{fw}-av-cam.bin').read_bytes()
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    size = (len(blob) + 0x10fffff) & ~0xfffff  # blob + 16 MiB de RAM para globals más allá del fichero
    uc.mem_map(B, size, UC_PROT_ALL)
    uc.mem_write(B, blob)
    for a in (OBJ, PAR, SCR, STK, STOPA):
        uc.mem_map(a, 0x100000, UC_PROT_ALL)
    uc.mem_write(OBJ, bytes([0]) * 0x1000)
    uc.mem_write(SCR, struct.pack('<I', SCR + 0x100) * 0x400)
    par = bytearray(0x40)
    struct.pack_into('<HHH', par, 0, 0x1234, 0x0567, 0x0789)  # +0 +4 +6 (SHR y similares)
    par[8], par[9], par[0x14] = 0x12, mode, 0x34
    struct.pack_into('<H', par, 0x0c, 0x0abc); struct.pack_into('<H', par, 0x10, 0x0def)
    uc.mem_write(PAR, bytes(par))
    writes, calls = [], []

    def on_code(u, addr, sz, _):
        if addr == stop:
            u.emu_stop(); return
        if not (entry <= addr < end) and not (STOPA <= addr < STOPA + 0x10):
            calls.append(hex(addr))
            u.reg_write(UC_ARM_REG_R0, SCR)
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))

    def on_write(u, acc, addr, sz, val, _):
        if B <= addr < B + size or OBJ <= addr < OBJ + 0x1000:
            writes.append((addr, sz, val))

    uc.hook_add(UC_HOOK_CODE, on_code)
    uc.hook_add(UC_HOOK_MEM_WRITE, on_write)
    # rellenar con `fill` el byte que la función modifica: se detecta en una pasada previa (dirección = campo GOT)
    if fill is not None:
        for a, v in fill.items():
            uc.mem_write(a, bytes([v]))
    uc.reg_write(UC_ARM_REG_R0, OBJ); uc.reg_write(UC_ARM_REG_R1, PAR)
    uc.reg_write(UC_ARM_REG_SP, STK + 0x80000); uc.reg_write(UC_ARM_REG_LR, STOPA | 1)
    err = None
    try:
        uc.emu_start(entry | 1, stop, count=20000)
    except UcError as e:  # frontera explícita
        err = str(e)
    final = {}
    for a, sz, v in writes:
        final[a] = (sz, v)
    return {'sensor': sensor, 'mode': mode, 'calls': calls, 'error': err,
            'final': {hex(a): hex(v) for a, (sz, v) in sorted(final.items()) if sz == 1},
            'final_wide': {hex(a): hex(v) for a, (sz, v) in sorted(final.items()) if sz != 1}}


def main():
    out = []
    for s in CFG:
        for m in (0, 1, 2, 3, 4):
            base = run(s, m, None)
            addrs = [int(a, 16) for a in base['final']]
            r0 = run(s, m, {a: 0x00 for a in addrs})
            rf = run(s, m, {a: 0xff for a in addrs})
            out.append({'sensor': s, 'mode': m, 'calls': r0['calls'], 'error': r0['error'],
                        'bytes_init00': r0['final'], 'bytes_initff': rf['final'], 'wide': r0['final_wide']})
    json.dump(out, sys.stdout, indent=1)


if __name__ == '__main__':
    main()
