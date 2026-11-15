"""G63 — Flicker Scan (Silent): ajuste «Flicker Scan» Off/50 Hz/60 Hz (`cfw_ajustes`) que redondea la exposición electrónica al múltiplo más cercano del periodo del parpadeo.

Se inserta en la cueva de Silent (`patch_silent_r5` + tope de `patch_silent_r5_sublinea`) justo tras calcular las líneas n (r2): con P = 584 (100 Hz) o 486 (120 Hz) líneas
de 17,135 µs, si n >= P, n = P·round(n/P) (bucle de restas, sin `udiv`). Con n < P (más rápido que 1/100 o 1/120) no se toca: las bandas no se pueden evitar.
shortcut: redondeo al más cercano (±P/2 ≈ ±0,5 EV como máximo en 1/60…1/100, el AE no lo sabe), P fijo por redondeo de la línea medida; ajustar P si la línea real difiere.
Solo bytes del `av-cam` del `.dat`; sin construir CFW. `python3 scripts/g63/flicker_scan_patch.py` = autocomprobación con Unicorn.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/g22"), str(ROOT / "scripts/g38"), str(ROOT / "scripts/gui")]
import cfw_ajustes as cfw
import patch_silent_r5 as R
import patch_silent_r5_sublinea as S
from e25_24 import patch_bionz as PB
from e25_24.thumb import bl

AJ = cfw.POR_ID["flicker_scan"]


def post_asm() -> str:
    return f"""
        mov r7, r2
        {cfw.leer_asm(AJ, "fl")}
        cbz r0, nada
        cmp r7, r0
        blo nada
        lsrs r1, r0, #1
        adds r1, r1, r7
        movs r2, #0
    lazo:
        cmp r1, r0
        blo fin
        subs r1, r1, r0
        adds r2, #1
        b lazo
    fin:
        mul r7, r2, r0
    nada:
        mov r2, r7
    """


def apply_bytes(data: bytes) -> bytes:
    """Como `patch_silent_r5_sublinea.apply_bytes` pero con la pieza de Flicker Scan en la cueva."""
    if len(data) != PB.SIZE:
        raise PB.ImageError("tamaño inesperado")
    h = R.HOOK - R.BASE
    if data[h:h + 4] != R.HOOK_OLD:
        raise PB.ImageError("enganche distinto del original")
    if any(data[R.CAVE - R.BASE:R.CAVE_END - R.BASE]):
        raise PB.ImageError("la cueva no está a cero")
    old = (R.R5_FULL, R.R5_LAG)
    R.R5_FULL, R.R5_LAG = S.R5_TOPE + 1, S.R5_BASE - (S.R5_TOPE + 1)
    try:
        code = R.cave_bytes(post_asm())
    finally:
        R.R5_FULL, R.R5_LAG = old
    out = bytearray(data)
    out[R.CAVE - R.BASE:R.CAVE - R.BASE + len(code)] = code
    out[h:h + 4] = bl(R.HOOK, R.CAVE)
    return bytes(out)


def emular(img: bytes, tv: int, opcion: int, silent: int = 1):
    """(r0, cap+0x64c = r5, cap+0x655) con el ajuste en la opción `opcion` (0 Off, 1 50 Hz, 2 60 Hz)."""
    return R.emular(img, tv, silent, backup=opcion)


def lineas(r5: int) -> int:
    return 4252 - r5

