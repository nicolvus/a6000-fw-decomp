"""Referencias PIC a cadenas en av-cam (Thumb): `ldr rN,[pc,#imm]` + `add rN,pc` con palabra relativa en el pool.

Solo bytes originales. Una referencia prueba que el código forma la dirección de la cadena, no que la emita.
shortcut: solo codificaciones Thumb-16 de ldr/add; las formas .w no se reconocen (se anota si faltan).
"""
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
SUFFIX = "firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
FIRMWARE = {
    "a6000": ROOT / "firmware/extracted/fw321" / SUFFIX,
    "a7s": ROOT / "firmware/extracted/a7s-fw320/payload" / SUFFIX,
    "a6300": ROOT / "firmware/extracted/a6300-fw201/payload" / SUFFIX,
}
WINDOW = 12  # halfwords entre el ldr y el add


def load(model: str) -> bytes:
    return FIRMWARE[model].read_bytes()


def pic_refs(blob: bytes) -> list[dict]:
    """Lista de {ldr, add, reg, target} para cada par ldr-literal/add-pc reconocido."""
    hw = struct.unpack_from(f"<{len(blob) // 2}H", blob)
    out = []
    n = len(hw)
    for i in range(n):
        h = hw[i]
        if h & 0xF800 != 0x4800:
            continue
        reg, imm = (h >> 8) & 7, (h & 0xFF) * 4
        ldr = BASE + 2 * i
        pool = ((ldr + 4) & ~3) + imm - BASE
        if pool + 4 > len(blob):
            continue
        word = struct.unpack_from("<I", blob, pool)[0]
        for j in range(i + 1, min(i + 1 + WINDOW, n)):
            if hw[j] == 0x4478 + reg:  # add rN, pc (N<8)
                add = BASE + 2 * j
                out.append({"ldr": ldr, "add": add, "reg": reg, "target": (word + add + 4) & 0xFFFFFFFF})
                break
            if hw[j] & 0xF800 == 0x4800 and (hw[j] >> 8) & 7 == reg:
                break  # el registro se recarga antes del add
    return out


def next_call(blob: bytes, start: int, limit: int = 24) -> tuple[int, int] | None:
    """Primer BL/B.W (Thumb-2) en las `limit` halfwords tras `start`: (dirección, destino)."""
    for k in range(limit):
        a = start + 2 * k
        o = a - BASE
        if o + 4 > len(blob):
            return None
        h1, h2 = struct.unpack_from("<HH", blob, o)
        if h1 & 0xF800 == 0xF000 and h2 & 0xD000 in (0xD000, 0x9000):
            s, j1, j2 = (h1 >> 10) & 1, (h2 >> 13) & 1, (h2 >> 11) & 1
            i1, i2 = ~(j1 ^ s) & 1, ~(j2 ^ s) & 1
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
            if s:
                imm -= 1 << 25
            return a, (a + 4 + imm) & 0xFFFFFFFF
    return None


def branch_sites(blob: bytes, target: int) -> list[int]:
    """Direcciones de BL/B.W (Thumb-2, alineados a halfword) cuyo destino es `target`."""
    out = []
    for o in range(0, len(blob) - 3, 2):
        h1, h2 = struct.unpack_from("<HH", blob, o)
        if h1 & 0xF800 == 0xF000 and h2 & 0xD000 in (0xD000, 0x9000):
            r = next_call(blob, BASE + o, 1)
            if r and r[1] == target:
                out.append(r[0])
    return out
