"""G32-D — indicador monocromo del núcleo (`av-cam.bin`, A6000 fw3.21) por tipo de Color Mode B&W, como la A7S. Solo construye bytes; no instala.

Original (`0x437a2728…0x437a2744`): monocromo = `caps[3]` bit 1 (Backup 0x30000, 0 en la NVRAM real) y saturación < −7.
A7S (`0x438c3b7a…0x438c3ba2`): lo mismo **o** id de Color Mode `0x17` (B&W). La A6000 no tiene ese id; el tipo llega en el resumen `+0x31`
(byte de `cfg+0x138`, `0x437aa8f8`), y B&W es el tipo 8 (G26/G27). Parche en sitio, sin cueva: monocromo = (tipo == 8); la saturación ya no lo dispara.
Requisito: la `libObj` debe enviar el tipo 8 tal cual (sin `patch_libobj_pp.patch_bw`, que lo convierte en Movie + saturación −8). Detalle: docs/gui/g33b-bw-balance-hilight.md §7.
"""
from keystone import KS_ARCH_ARM, KS_MODE_THUMB, Ks

BASE = 0x43541000
SITE, END = 0x437A2728, 0x437A2744          # termina justo antes de `strb.w r0, [r3, #0x88]`
ORIG = "23680121e87893f8247048f3cbfca36801282fd17fb217f1070f2bda"
BW = 8
ASM = f"""ldr r3, [r4]
movs r1, #1
ldrb.w r7, [r3, #0x24]
ldrb.w r0, [r3, #0x31]
ldr r3, [r4, #8]
cmp r0, #{BW}
bne #0x437a279c
movs r0, #1"""


def patches(base: bytes) -> list[tuple[int, bytes, str]]:
    assert base[SITE - BASE:END - BASE].hex() == ORIG, "sitio del indicador monocromo distinto del fw3.21"
    code = bytes(Ks(KS_ARCH_ARM, KS_MODE_THUMB).asm(ASM, SITE)[0])
    code += b"\x00\xbf" * ((END - SITE - len(code)) // 2)     # nop hasta el strb original
    assert len(code) == END - SITE
    return [(SITE, code, "monocromo por tipo B&W 0x437a2728")]
