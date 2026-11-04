#!/usr/bin/env python3
"""E26-R54: aplica el parche de RAM de E25-11 solo con EFCS desactivado (modo Electronic del 3.30) y lo revierte con EFCS activado.

Uso: camera_silent_follow.py [segundos] [velocidad, p. ej. 250]   (telnet 23; sin app ni adb)
Sondea el ajuste EFCS (bloque 0x43edf684 + 0x210) cada ~2 s; tras cambiarlo en el menú, esperar unos 3 s antes de disparar.
Al terminar (o con Ctrl-C) deja el código original."""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import camera_silent as S

LIVE_EFCS = 0x83EDF894  # físico; 1 = EFCS desactivado = Electronic


def main() -> None:
    secs = float(sys.argv[1]) if len(sys.argv) > 1 else 1800
    r5 = S.r5_for(1 / float(sys.argv[2] if len(sys.argv) > 2 else 250))
    end, n = time.time() + secs, 0
    try:
        while time.time() < end:
            electronic = S.rd(LIVE_EFCS, 1) == "01"
            patched = not S.is_original()
            if electronic and not patched:
                tok = f"f{n}"
                S.apply(r5, tok)
                S.run(S.HOST, [f"touch {S.FLAG}{tok}"])  # parche estable mientras siga en Electronic
                n += 1
                print(time.strftime("%H:%M:%S"), "Electronic: parche aplicado, r5 =", r5, flush=True)
            elif not electronic and patched:
                S.revert(f"f{n - 1}")
                print(time.strftime("%H:%M:%S"), "EFCS/mecánico: código original =", S.is_original(), flush=True)
            time.sleep(1)
    finally:
        if not S.is_original():
            S.revert("fin")
        print("fin; original =", S.is_original(), flush=True)


if __name__ == "__main__":
    main()
