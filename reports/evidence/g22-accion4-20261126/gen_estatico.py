#!/usr/bin/env python3
"""Vuelca la evidencia estática de G22-ACCION4 (docs/gui/g22-reproduccion-dispatch.md §10) desde los ELF 3.21.

uso: python3 gen_estatico.py [DIR_LIB]   (por defecto analysis/gui/g22/harness/stage/cam/usr/lib)
No arranca ninguna VM. Las direcciones son VA del ELF (= desplazamiento de fichero en estos binarios).
"""
import struct
import sys
from pathlib import Path

from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

LIB = Path(sys.argv[1] if len(sys.argv) > 1 else
           Path(__file__).resolve().parents[3] / "analysis/gui/g22/harness/stage/cam/usr/lib")


def read(name):
    return (LIB / name).read_bytes()


def u16(d, va):
    return struct.unpack_from("<H", d, va)[0]


def u32(d, va):
    return struct.unpack_from("<I", d, va)[0]


def dis(d, va, n):
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
    return [f"{i.address:08x}  {i.bytes.hex():10s} {i.mnemonic:8s} {i.op_str}"
            for i in md.disasm(d[va:va + n], va)]


def tabla(d, va, n=19):
    return [(u32(d, va + 8 * k), u32(d, va + 8 * k + 4)) for k in range(n)]


out = []
sd = read("libScalarDaemon.so")
vu = read("viewUnified2.so")
lo = read("libObj.so")

out.append("== 1. la tabla {código -> acción}: 19 pares de 8 B, idénticos en las dos copias ==")
a = tabla(sd, 0x19DB0C)
b = tabla(vu, 0x3A03D4)
out.append(f"libScalarDaemon.so+0x19db0c (VIVA, leída por convertViewEventToAB) y "
           f"viewUnified2.so+0x3a03d4 (MUERTA, leída por 0x1906a8): iguales = {a == b}")
for (ca, va_), (cb, vb) in zip(a, b):
    out.append(f"  {ca:#010x} -> {va_:3d}    |    {cb:#010x} -> {vb:3d}")
out.append("  (fin de tabla: la entrada 20 ya no es un par; el lector corta en 19, `cmp r3,#0x13`)")

out.append("")
out.append("== 2. convertViewEventToAB (libScalarDaemon+0x13a704, 48 B, símbolo _Z21convertViewEventToABTjRj) ==")
out += ["  " + s for s in dis(sd, 0x13A704, 0x30)]
out.append(f"  literal PIC en 0x13a730 = {u32(sd, 0x13A730):#010x} -> tabla = "
           f"{u32(sd, 0x13A730) + 0x13A712 + 4:#x}")
out.append("  máscara: 0x150100f2 & ~0xf = 0x%08x ; 0x150100f1 & ~0xf = 0x%08x -> fila "
           "{0x150100f0 -> 4} -> ACCIÓN 4" % (0x150100F2 & ~0xF, 0x150100F1 & ~0xF))

out.append("")
out.append("== 3. el lector de la copia MUERTA (viewUnified2+0x1906a8) y sus consumidores ==")
out += ["  " + s for s in dis(vu, 0x1906A8, 0x2C)]
out.append("  mismo esquema que el vivo pero sobre 0x3a03d4; 0 ramas y 0 punteros en las 8 vistas y libObj")

out.append("")
out.append("== 4. el consumo en la capa de vista (libObj) ==")
for va, n, lab in ((0x1170E8, 0x8C, "ScalarView::TriggerTableEvent(unsigned)"),
                   (0x1208D2, 0x1A, "compone el id de vista (getView()<<12)+id+0x13000000"),
                   (0x1208EC, 0x48, "ViewBase::transformByTriggerTable"),
                   (0x120935, 0x34, "ViewBase::transformByTriggerTableForFuncEvent")):
    out.append(f"-- {lab}  libObj+{va:#x}")
    out += ["  " + s for s in dis(lo, va, n)]

out.append("")
out.append("== 5. el puente al daemon: ScalarView::EventHandler(Event*, m) (libObj+0x116bd0) ==")
out += ["  " + s for s in dis(lo, 0x116C00, 0x40)]
out.append("  en 0x116c28: blx ScalarDaemonIf::onSystemEventReceived(Event&, ViewBase*)  (PLT 0xddd4c)")

out.append("")
out.append("== 6. la vía de tecla del daemon (no usa 0x1501xxxx: usa KEY_CODE) ==")
for va, n, lab in ((0xDA20C, 0x40, "InputServantObserver::notifyKeyEventCallback"),
                   (0xD37B8, 0x0E, "ScalarDaemon::onKeyEventReceived(KEY_CODE, KEY_STATE)"),
                   (0xD5654, 0x40, "EventDispatcher::dispatchKeyEvent(KEY_CODE, KEY_STATE)")):
    out.append(f"-- {lab}  libScalarDaemon+{va:#x}")
    out += ["  " + s for s in dis(sd, va, n)]

txt = "\n".join(out)
Path("estatico.txt").write_text(txt + "\n", encoding="utf-8")
print(txt)
