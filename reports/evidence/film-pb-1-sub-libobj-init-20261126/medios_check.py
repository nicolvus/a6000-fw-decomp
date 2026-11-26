"""¿Ejecuta o escribe algún inicializador de libObj en las direcciones de medios/IFO?

Ejecuta las 263 entradas de `.init_array` con el andamio de `init_emu.py` sin parar en los stubs
(suministro de PCs y direcciones escritas: superconjunto de lo que toca el código real) y
comprueba tres direcciones del diagnóstico de FILM-PB-1.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import init_emu as E                                          # noqa: E402
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_WRITE           # noqa: E402
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_SP    # noqa: E402

PUNTOS = (("ifoFramework (semáforo)", 0x5BAD00),
          ("AviMMgr::GetPlayMovieStatus", 0x60945C),
          ("GetPlayThumbnailInfo", 0x6E8430))


def main() -> None:
    im = E.Imagen(E.ORIG)
    m = E.Montaje(im)
    vistos, escritas = set(), set()
    m.mu.hook_add(UC_HOOK_CODE, lambda u, a, s, d: vistos.add(a))
    m.mu.hook_add(UC_HOOK_MEM_WRITE, lambda u, acc, addr, sz, val, d: escritas.add(addr))
    for entrada in im.entradas_init():
        m.mu.reg_write(UC_ARM_REG_SP, E.PILA_TOP)
        m.mu.reg_write(UC_ARM_REG_LR, E.SENTINELA)
        try:
            m.mu.emu_start(entrada | 1, E.SENTINELA, count=200_000)
        except Exception:                                     # noqa: BLE001, S110
            pass
    print("entradas=%d  PCs distintos=%d  direcciones escritas distintas=%d"
          % (len(im.entradas_init()), len(vistos), len(escritas)))
    print("(los PCs incluyen los stubs de importación: es un superconjunto)")
    for nombre, va in PUNTOS:
        print("  %-30s %#x  ejecutada=%s  escrita=%s" % (nombre, va, va in vistos, va in escritas))


if __name__ == "__main__":
    main()
