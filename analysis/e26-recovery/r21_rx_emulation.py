"""E26-R21 — Unicorn: el BootROM real recibe un byte por MODEREG bit 1 (BOOT_SERIAL_IN).

Solo se modelan entradas: MODEREG, GPIO(4,RDATA) y un tiempo virtual (+1 tick por lectura de
temporizador; reiniciado por las escrituras que hace el BootROM a `0xf2403000/0xf2403100`).
La forma de onda es una trama 8O1 con periodo `period` ticks. OFFLINE; no toca hardware.
"""

import bisect
import struct
from pathlib import Path

from unicorn import (
    UC_ARCH_ARM,
    UC_HOOK_CODE,
    UC_HOOK_MEM_READ,
    UC_HOOK_MEM_UNMAPPED,
    UC_HOOK_MEM_WRITE,
    UC_MODE_ARM,
    UC_PROT_ALL,
    Uc,
    UcError,
)
from unicorn.arm_const import (
    UC_ARM_REG_CPSR,
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R4,
    UC_ARM_REG_R7,
)

ROM = (
    Path(__file__).resolve().parents[1]
    / "camera-dumps/updater-20261020-175427/bootrom.bin"
)
BASE, ESRAM = 0xFFFF0000, 0xC0000000
MODEREG, GPIO4 = 0xF2915010, 0xF2910410


def frame(byte: int, parity_ok: bool = True) -> list[int]:
    """Niveles de la trama: inicio 0, 8 datos LSB primero, paridad impar, parada 1."""
    bits = [(byte >> i) & 1 for i in range(8)]
    par = 1 - (sum(bits) & 1)  # impar: el bit es 1 si el XOR de los datos es 0
    return [0, *bits, par if parity_ok else par ^ 1, 1]


WINDOW = {
    1: (0x38D, 0x4A0),
    0: (0xB18, 0xE74),
}  # (ancho mínimo, tiempo máximo) del tren por perfil


def waveform(
    bit21: int,
    period: int,
    byte: int,
    parity_ok: bool,
    edges: int,
    t0: int,
    width: int | None = None,
):
    """Lista de (instante, nivel): `edges` flancos separados `width` ticks; el último es el de inicio."""
    lo, hi = WINDOW[bit21]
    width = width or (lo + hi) // 2
    last = 0  # el último flanco cae al nivel de inicio (0)
    first = last if edges % 2 else 1 - last  # nivel tras el 1.er flanco
    wf = [(0, 1 - first)]
    for k in range(edges):
        wf.append((t0 + k * width, first if k % 2 == 0 else 1 - first))
    t = t0 + (edges - 1) * width
    for i, lv in enumerate(frame(byte, parity_ok)):
        wf.append((t + i * period, lv))
    wf.append((t + 11 * period, 1))
    return wf


def run(
    bit21: int,
    period: int,
    byte: int = 0xA5,
    parity_ok: bool = True,
    edges: int = 60,
    t0: int = 3000,
    limit: int = 3_000_000,
):
    wf = waveform(bit21, period, byte, parity_ok, edges, t0)
    gpio4 = (1 << 22) | (bit21 << 21)
    d = ROM.read_bytes()
    uc = Uc(UC_ARCH_ARM, UC_MODE_ARM)
    uc.mem_map(BASE, 0x6000, UC_PROT_ALL)
    uc.mem_write(BASE, d)
    uc.mem_map(ESRAM, 0x100000, UC_PROT_ALL)
    st = {"t": 0, "base": {0: 0, 1: 0}, "n": 0, "marks": {}, "byte": None, "err": None}

    times = [tt for tt, _ in wf]

    def level(t: int) -> int:
        return wf[bisect.bisect_right(times, t) - 1][1]

    def on_read(u, access, addr, size, value, ud):
        if addr == MODEREG:
            u.mem_write(addr, struct.pack("<I", 1 | (level(st["t"]) << 1)))
        elif addr == GPIO4:
            u.mem_write(addr, struct.pack("<I", gpio4))
        elif addr in (0xF240300C, 0xF240310C):
            st["t"] += 1
            u.mem_write(addr, struct.pack("<I", st["t"] - st["base"][(addr >> 8) & 1]))

    def on_write(u, access, addr, size, value, ud):
        if addr in (0xF2403000, 0xF2403100) and value == 0x1030:
            st["base"][(addr >> 8) & 1] = st["t"]

    def unmapped(u, access, addr, size, value, ud):
        u.mem_map(addr & ~0xFFF, 0x1000, UC_PROT_ALL)
        return True

    def on_code(u, pc, size, ud):
        st["n"] += 1
        if pc == 0xFFFF0114:  # espera en ms de la ruta normal; no es decisión
            u.reg_write(UC_ARM_REG_PC, u.reg_read(UC_ARM_REG_LR))
        if (
            pc == 0xFFFF064C
        ):  # `beq` + `bls.w` (T3): Unicorn rechaza el segundo; se resuelven a mano
            cpsr = u.reg_read(UC_ARM_REG_CPSR)
            z, c = bool(cpsr & (1 << 30)), bool(cpsr & (1 << 29))
            dest = 0xFFFF074C if z else 0xFFFF0848 if not c else 0xFFFF0652
            u.reg_write(UC_ARM_REG_PC, dest | 1)
        if pc in (0xFFFF06D4, 0xFFFF072C, 0xFFFF0758) and pc not in st["marks"]:
            st["marks"][pc] = st["t"]
            if pc == 0xFFFF06D4:
                st["byte"] = u.reg_read(UC_ARM_REG_R7)
            if pc == 0xFFFF0758:
                st["err"] = u.reg_read(UC_ARM_REG_R4)
        if pc == 0xFFFF0D62 and st["err"] is None:
            st["err"] = "blink"
        if st["n"] > limit or 0xFFFF072C in st["marks"] or 0xFFFF0758 in st["marks"]:
            u.emu_stop()

    uc.hook_add(UC_HOOK_MEM_UNMAPPED, unmapped)
    uc.hook_add(UC_HOOK_MEM_READ, on_read, begin=0, end=0xFFFFFFFF)
    uc.hook_add(UC_HOOK_MEM_WRITE, on_write, begin=0xF2403000, end=0xF2403200)
    uc.hook_add(UC_HOOK_CODE, on_code, begin=BASE, end=BASE + 0x6000)
    try:
        uc.emu_start(BASE, 0, count=limit * 2)
    except UcError as e:
        print("UcError", e, hex(uc.reg_read(UC_ARM_REG_PC)))
    ok = 0xFFFF072C in st["marks"]
    return {
        "parity_ok_reached": ok,
        "byte": st["byte"],
        "error": st["err"],
        "t": st["t"],
    }


if __name__ == "__main__":
    for b21, per in ((0, 250), (1, 84), (0, 84), (1, 250)):
        print(f"bit21={b21} periodo={per}:", run(b21, per))
    print("paridad errónea bit21=0/250:", run(0, 250, parity_ok=False))
