"""S59: sondas de instrucciones originales; entradas etiquetadas como sintéticas."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "analysis/s58"))
import a7_verify as rows_probe
from tdis import data, u32
from unicorn.arm_const import (
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R3,
    UC_ARM_REG_R4,
    UC_ARM_REG_R5,
    UC_ARM_REG_R7,
    UC_ARM_REG_R9,
    UC_ARM_REG_SP,
)
from wtrace import W

GOT = 0x4401EEE4
STATE = u32("A6000", GOT + 0x6460)
GUARD = u32("A6000", GOT + 0x2F08)
SRC, DST, HANDLE = 0x45400000, 0x45500000, 0x45600000
COPY = [(0x43B7F878, 0x43B7F880), (0x439C5320, 0x439C5A04)]


def binary_sha():
    return hashlib.sha256(data("A6000")).hexdigest()


def machine(ranges, fill=0):
    return W(ambito=ranges + COPY, fill=fill)


def accessor():
    w = machine([(0x43AE84C0, 0x43AE84CC), (0x437876DC, 0x43787700)])
    w.w32(GUARD, 1)  # Objeto ya construido: precondición explícita, sin stub.
    return w.call(0x43AE84C0)


def copy_override(fill=0):
    w = machine([(0x43B00DA0, 0x43B00DAC)], fill)
    payload = bytes(range(80))
    w.u.mem_write(SRC, payload)
    w.u.mem_write(DST + 0xDB3, b"\xcc" * 82)
    w.call(0x43B00DA0, DST, SRC)
    return {"source": payload.hex(), "destination": w.rd(DST + 0xDB4, 80).hex(),
            "guards": (w.rd(DST + 0xDB3, 1) + w.rd(DST + 0xE04, 1)).hex(),
            "stubbed": w.stubbed}


def publish_override(enabled):
    w = machine([(0x43B00DD4, 0x43B00E40), (0x43B00DA0, 0x43B00DD4)])
    payload = bytes(range(80))
    w.u.mem_write(DST, bytes(0xF00))
    w.u.mem_write(DST + 0xD64, payload)
    w.u.mem_write(DST + 0xDB4, b"\xcc" * 80)
    w.u.mem_write(DST + 0x57C, bytes([enabled]))
    w.w32(DST + 0x568, 0)  # Evita ramas posteriores de copia de otros bloques.
    w.call(0x43B00DD4, DST)
    return {"source": payload.hex(), "published": w.rd(DST + 0xDB4, 80).hex(),
            "stubbed": w.stubbed}


def constructor_override():
    w = machine([(0x43B00B48, 0x43B00CB4), (0x439C5A04, 0x439C5B5C)])
    w.u.mem_write(DST, b"\xa5" * 0xF00)
    w.call(0x43B00B48, DST)
    return {"override": w.rd(DST + 0xDB4, 80).hex(),
            "gate": w.rd(DST + 0x57C, 1)[0], "stubbed": w.stubbed}


def consumer_slice(selector):
    """Bloque básico compuesto 437aad72..437aae0a; registros inicializados a mano."""
    w = machine([(0x437AAD72, 0x437AAE0A), (0x43AE84C0, 0x43AE84CC),
                 (0x437876DC, 0x43787700)])
    payload = bytes(range(1, 25))
    w.w32(GUARD, 1)
    w.u.mem_write(STATE + 0xDD0, payload)
    w.w32(SRC + 0xB4, selector)
    w.w32(HANDLE, DST)
    w.u.mem_write(DST + 0x13C, b"\xcc" * 24)
    w.u.reg_write(UC_ARM_REG_R3, SRC)
    w.u.reg_write(UC_ARM_REG_R4, HANDLE)
    w.u.reg_write(UC_ARM_REG_SP, 0x444FFE00)
    w.u.emu_start(0x437AAD73, 0x437AAE0A, count=1000)
    if w.u.reg_read(UC_ARM_REG_PC) != 0x437AAE0A:
        raise RuntimeError("No se completó el bloque consumidor")
    return {"selector": selector, "source": payload.hex(),
            "output": w.rd(DST + 0x13C, 24).hex(), "stubbed": w.stubbed}


def snapshot():
    w = machine([(0x4383D18C, 0x4383D3B8)])
    w.u.mem_write(SRC, bytes(0x900))
    w.w32(SRC + 0x4C0, 0x12345678)
    w.u.mem_write(SRC + 0x4C4, bytes(range(48)))
    w.call(0x4383D18C, SRC, SRC + 0x1000, SRC + 0x2000, SRC + 0x3000,
           stack=(DST,))
    return {"clock_word": w.r32(DST + 0x5C), "M": w.rd(DST + 0x60, 48).hex(),
            "stubbed": w.stubbed}


def clock_object_binding():
    """Argumentos reales del llamador; detiene antes de ejecutar 43844e80."""
    w = machine([(0x437B5B2E, 0x437B5BA4)])
    sp = 0x444FFE00
    w.u.reg_write(UC_ARM_REG_SP, sp)
    w.u.reg_write(UC_ARM_REG_R4, 0x8693B0)
    w.u.emu_start(0x437B5B2F, 0x437B5BA4, count=1000)
    if w.u.reg_read(UC_ARM_REG_PC) != 0x437B5BA4:
        raise RuntimeError("No se completó el bloque de argumentos")
    return {"ae_source": w.u.reg_read(UC_ARM_REG_R1),
            "histogram_object": w.r32(sp + 0x18), "stubbed": w.stubbed}


def vdnum_slice(raw):
    """437aab48..56, después de LDRH: clamp inferior sin límite signed16."""
    if not 0 <= raw <= 0xFFFF:
        raise ValueError("La entrada procede de LDRH")
    w = machine([(0x437AAB48, 0x437AAB56)])
    w.u.reg_write(UC_ARM_REG_R1, raw)
    w.u.reg_write(UC_ARM_REG_R5, SRC)
    w.u.reg_write(UC_ARM_REG_R9, DST)
    w.u.emu_start(0x437AAB49, 0x437AAB56, count=100)
    if w.u.reg_read(UC_ARM_REG_PC) != 0x437AAB56:
        raise RuntimeError("No se completó el bloque VdNum")
    return w.r16(DST + 0xCC)


def host_slice(n, svr, vd, mode=0):
    """Cálculo host original, incluyendo N=0, caso 9 y clamp de bit15.

    Solo las dos funciones de diagnóstico salen del ámbito y se omiten.
    """
    w = machine([(0x438110BE, 0x4381112A), (0x43550000, 0x43570000)])
    w.w32(DST + 0x1F8, n)
    w.w32(DST + 0x1FC, mode)
    w.w32(HANDLE + 8, SRC)
    w.w16(SRC + 0xCC, vd)
    w.u.mem_write(SRC + 0x14E, bytes([svr]))
    w.u.reg_write(UC_ARM_REG_R4, DST)
    w.u.reg_write(UC_ARM_REG_R7, HANDLE)
    w.u.reg_write(UC_ARM_REG_SP, 0x444FFE00)
    w.u.emu_start(0x438110BF, 0x4381112A, count=10000)
    if w.u.reg_read(UC_ARM_REG_PC) != 0x4381112A:
        raise RuntimeError("No se completó el cálculo host")
    return {"value": w.u.reg_read(UC_ARM_REG_R0), "stubbed": w.stubbed}


def compatibility():
    """Cálculo host original frente al productor real; NO prueba alcanzabilidad."""
    w = W(ambito=rows_probe.AMB)
    out = []
    for n in (2, 4, 6, 8, 12):
        for svr in (1, 2, 4):
            for vd in (1, 2, 3):
                if n < vd:
                    continue
                g = dict(b0=[100] * 4, c0=[0] * 4, d0=[0] * 4,
                         **{"10": 4176, "14": 4, "18": 0, "28": 0, "2a": 0,
                            "2c": 0, "2e": 0, "38": vd, "16": svr, "24": 0,
                            "3a": 0, "163": 0, "164": 0, "190": 0, "30": n, "34": 0})
                actual = rows_probe.real(w, g)[0]["svd"]
                out.append({"N": n, "svr": svr, "vd": vd, "producer": actual,
                            "host": host_slice(n, svr, vd)["value"],
                            "reachability": "NO VERIFICADO"})
    return out


def main():
    print(json.dumps({"sha256": binary_sha(), "state": hex(STATE),
                      "accessor": hex(accessor()), "copy": copy_override(),
                      "constructor": constructor_override(),
                      "publish": [publish_override(x) for x in (0, 1)],
                      "consumer": [consumer_slice(x) for x in (0, 1, 2)],
                      "snapshot": snapshot(), "clock_binding": clock_object_binding(),
                      "vdnum": [{"raw": x, "vdnum": vdnum_slice(x)} for x in
                                (0, 0x2FFF, 0x3000, 0x3001, 0xAFFF, 0xB000, 0xFFFF)],
                      "host_edges": [{"inputs": x, "result": host_slice(*x)} for x in
                                     ((0, 4, 3, 0), (1, 1, 2, 0), (6, 4, 3, 0),
                                      (6, 4, 1, 9), (6, 4, 3, 9))],
                      "synthetic_compatibility": compatibility()}, indent=2))


if __name__ == "__main__":
    main()
