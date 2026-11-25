"""G89 — inyecta el userland de `lut_sd_userland` (hilo que lee los `.cube` de la SD) en `viewUnified2.so` (A6000 3.21).

Un único cambio de comportamiento: `DT_INIT` (`0xe596d`) pasa a un tramo nuevo que llama al `_init` original, resuelve `pthread_create` con `dlsym(RTLD_DEFAULT, …)` (el PLT
`dlsym` `0xe72e4` ya existe en la biblioteca) y arranca `lutsd_hilo(dlsym)` en un hilo. Código nuevo en un segmento LOAD R+X añadido al final del fichero (misma técnica que `pid_space`,
`fn_lut_menu`: tabla de cabeceras reubicada dentro del segmento); no se toca ningún byte de código original ni ninguna relocación, así que se puede aplicar antes o después de `pid_space.patch`.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / "gui"), str(Path(__file__).parent), str(Path(__file__).resolve().parents[1])]
import add_menu_entry as A
import cfw_ajustes
import lut_sd_userland as U

DT_INIT = 12
DLSYM_PLT = 0xE72E4          # viewUnified2.so 3.21: stub PLT (ARM) de `dlsym@plt`
INIT_ORIG = 0xE596D          # DT_INIT original (Thumb, bit 0 = 1)
STUB_TAM = 0x80


def _stub(va: int, init: int, dlsym: int, hilo: int) -> bytes:
    """Thumb: `_init` original; `pthread_create(&t, 0, lutsd_hilo, dlsym)` con la dirección resuelta en ejecución (los literales son desplazamientos relativos al literal)."""
    def src(lit_off: int) -> str:
        return f"""
        push {{r4-r7, lr}}
        sub sp, #8
        bl #{init & ~1:#x}
        movs r0, #0
        adr.w r1, nm
        blx #{dlsym:#x}
        cbz r0, fin
        mov r4, r0
        adr.w r6, lit
        ldr r3, [r6]
        add r3, r6
        ldr r2, [r6, #4]
        add r2, r6
        adds r2, #1
        mov r0, sp
        movs r1, #0
        blx r4
    fin:
        add sp, #8
        pop {{r4-r7, pc}}
        .align 2
    lit:
        .word {(dlsym - (va + lit_off)) & 0xFFFFFFFF}
        .word {(hilo - (va + lit_off)) & 0xFFFFFFFF}
    nm:
        .asciz "pthread_create"
        """
    # primera pasada: mide dónde cae `lit` (el tamaño del código no depende de los literales)
    probe = cfw_ajustes.ensamblar(src(0), va)
    lit_off = len(probe) - 8 - len("pthread_create") - 1
    out = cfw_ajustes.ensamblar(src(lit_off), va)
    assert len(out) == len(probe) <= STUB_TAM
    return out


def va_blob(d: bytes) -> int:
    """VA en que `patch` deja el código de `blob_sim` (para enlazarlo allí)."""
    segs = A._segments(d)
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    return (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN + STUB_TAM


def patch(d: bytes, blob_sim: tuple[bytes, dict[str, int]] | None = None, entrada: str = "lutsd_hilo") -> bytes:
    """`entrada`: función del hilo (G97 usa `films_hilo` del userland de películas)."""
    blob, sim = blob_sim or U.compila()
    segs = A._segments(d)
    dyn_off, dyn = A._dynamic(d, segs)
    tags = {t: v for t, v in dyn if t}
    assert tags[DT_INIT] == INIT_ORIG, hex(tags[DT_INIT])
    top = max(v + ms for t, _, v, _, _, ms, _, _ in segs if t == 1)
    new_va = (top + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    new_off = (len(d) + A.ALIGN - 1) // A.ALIGN * A.ALIGN
    code_va = new_va + STUB_TAM
    stub = _stub(new_va, INIT_ORIG, DLSYM_PLT, code_va + sim[entrada])
    seg = bytearray(stub.ljust(STUB_TAM, b"\0") + blob)
    seg += b"\0" * (-len(seg) % 16)
    phdr_off = new_off + len(seg)
    new_ph = [list(s) for s in segs] + [[1, new_off, new_va, new_va, 0, 0, 5, A.ALIGN]]      # R+X
    new_ph[-1][4] = new_ph[-1][5] = len(seg) + 32 * len(new_ph)
    seg += b"".join(struct.pack("<8I", *s) for s in new_ph)
    out = bytearray(d).ljust(new_off, b"\0") + seg
    struct.pack_into("<I", out, 28, phdr_off)
    struct.pack_into("<H", out, 44, len(new_ph))
    for i, (tg, _) in enumerate(dyn):
        if tg == DT_INIT:
            struct.pack_into("<I", out, dyn_off + 8 * i + 4, new_va | 1)
    return bytes(out)


if __name__ == "__main__":
    src, dst = sys.argv[1:3]
    Path(dst).write_bytes(patch(Path(src).read_bytes()))
    print(dst)
