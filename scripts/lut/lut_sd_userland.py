"""G89 (LUT-SD-1) — `.cube` desde la SD en la cámara: userland (C → Thumb, `userland/lutsd.c`) inyectado en `viewUnified2.so` + referencia Python bit a bit + arnés Unicorn.

Cadena: hilo del userland (proceso de `libObj`) → `Fsys_*` lee `X:/LUT/LUT<n>.cube` (n = 1…6) → muestreo directo de los 405 nodos 5×9×9 (Q16) → 21 bits/nodo → blob de 16 KB en el
id de Backup `BK_ID` (`Backup_write`) → `av-cam` lo lee con `Backup_read` (cueva de `avcam_dinamico.lut_unpack_sd_asm`) y desempaqueta a la tabla del ISP.
Blob: `LUTS` (u32), versión (u8 en +4), nº de ranuras (u8 en +6), `valida[8]` en +8, tablas de 1064 B desde +16 (ranura s en 16 + s·1064).
shortcut: muestreo en el nodo, no el ajuste por mínimos cuadrados del PC (`cube_a6000.ajusta_lut3d`, resuelve 405×405 con float): más error en .cube con detalle fino; si pesa, resolver en el PC (`--cubes`).
`python3 lut_sd_userland.py` = autocomprobación (compila y compara el ARM emulado con la referencia).
"""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(Path(__file__).parent)]
SRC = Path(__file__).parent / "userland/lutsd.c"
SLOTS, TAM_TABLA, BK_TAM, BK_ID, MAGIC = 6, 1064, 16384, 0x150005, 0x5354554C
BASE_COMPILADO = 0x10000


def compila() -> tuple[bytes, dict[str, int]]:
    """C → (binario plano Thumb independiente de posición, {símbolo: desplazamiento}). Necesita clang + ld.lld + llvm-objcopy/nm."""
    with tempfile.TemporaryDirectory() as d:
        o, e, b = f"{d}/l.o", f"{d}/l.elf", f"{d}/l.bin"
        subprocess.run(["clang", "--target=thumbv7a-none-eabi", "-mthumb", "-mfloat-abi=soft", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fropi",
                        "-fno-exceptions", "-fno-asynchronous-unwind-tables", "-nostdlib", "-Wall", "-Wextra", "-Werror", "-c", str(SRC), "-o", o], check=True)
        subprocess.run(["ld.lld", "-m", "armelf", "--omagic", f"-Ttext={BASE_COMPILADO:#x}", f"--entry={BASE_COMPILADO:#x}", "-o", e, o], check=True)
        subprocess.run(["llvm-objcopy", "-O", "binary", e, b], check=True)
        nm = subprocess.run(["llvm-nm", e], check=True, capture_output=True, text=True).stdout
        sim = {p[2]: int(p[0], 16) - BASE_COMPILADO for p in (ln.split() for ln in nm.splitlines()) if len(p) == 3 and p[1] in "Tt"}
        return Path(b).read_bytes(), sim


# ---------- referencia (mismo orden de operaciones enteras que el C) ----------
def _q16(s: str) -> tuple[int, str]:
    neg, e10, m, i = False, 0, 0, 0
    while i < len(s) and s[i] in " \t":
        i += 1
    if i < len(s) and s[i] in "+-":
        neg = s[i] == "-"
        i += 1
    while i < len(s) and s[i].isdigit():
        if m < 10**17:
            m = m * 10 + int(s[i])
        else:
            e10 += 1
        i += 1
    if i < len(s) and s[i] == ".":
        i += 1
        while i < len(s) and s[i].isdigit():
            if m < 10**17:
                m = m * 10 + int(s[i])
                e10 -= 1
            i += 1
    if i < len(s) and s[i] in "eE":
        i += 1
        en, x = False, 0
        if i < len(s) and s[i] in "+-":
            en = s[i] == "-"
            i += 1
        while i < len(s) and s[i].isdigit():
            if x < 1000:
                x = x * 10 + int(s[i])
            i += 1
        e10 += -x if en else x
    while e10 > 0 and m < 10**14:
        m *= 10
        e10 -= 1
    d = 1
    while e10 < 0 and d < 10**17:
        d *= 10
        e10 += 1
    v = min(((m << 16) + (d >> 1)) // d, 0x7FFFFFFF)
    return (-v if neg else v), s[i:]


def lee_cube_q16(texto: str):
    """Mismo análisis que `linea()` del C → (n, lo, hi, cubo plano Q16) o None si no es válido."""
    n, lo, hi, cub = 0, [0] * 3, [65536] * 3, None
    filled = 0
    for ln in texto.split("\n"):
        ln = ln.split("#")[0][:95].lstrip(" \t\r")
        if not ln:
            continue
        if ln.startswith("LUT_3D_SIZE"):
            t = ln[11:].lstrip(" \t")
            k = 0
            while k < len(t) and t[k].isdigit():
                k += 1
            n = int(t[:k] or 0)
            if n < 2 or n > 64 or cub is not None:
                return None
            cub = [0] * (n ** 3 * 3)
        elif ln.startswith(("DOMAIN_MIN", "DOMAIN_MAX")):
            d, s = (lo if ln[8] == "I" else hi), ln[10:]
            for k in range(3):
                d[k], s = _q16(s)
        elif ln.startswith(("LUT_1D", "LUT_3D_INPUT")):
            return None
        elif ln[0].isdigit() or ln[0] in "-+.":
            if cub is None or filled >= n ** 3:
                return None
            s = ln
            for k in range(3):
                cub[filled * 3 + k], s = _q16(s)
            filled += 1
    return (n, lo, hi, cub) if cub is not None and filled == n ** 3 else None


def _tri(n, lo, hi, cub, x):
    i0, f = [], []
    for k in range(3):
        den = hi[k] - lo[k]
        u = 0
        if den > 0 and x[k] > lo[k]:
            u = ((x[k] - lo[k]) << 16) // den
        u = min(u, 65536) * (n - 1)
        i = min(u >> 16, n - 2)
        i0.append(i)
        f.append(u - (i << 16))
    out = []
    for ch in range(3):
        acc = 0
        for d in range(8):
            dr, dg, db = d & 1, (d >> 1) & 1, (d >> 2) & 1
            w = ((f[0] if dr else 65536 - f[0]) * (f[1] if dg else 65536 - f[1])) >> 16
            w = (w * (f[2] if db else 65536 - f[2])) >> 16
            acc += w * cub[(((i0[2] + db) * n + i0[1] + dg) * n + i0[0] + dr) * 3 + ch]
        out.append(acc >> 16)
    return out


def _ycc(rgb):
    y = (19595 * rgb[0] + 38470 * rgb[1] + 7471 * rgb[2]) >> 16
    return [y, ((rgb[2] - y) * 36984) >> 16, ((rgb[0] - y) * 46743) >> 16]


def referencia(texto: str) -> bytes | None:
    """Tabla de 1064 B (405 nodos × 21 bits) que debe producir el ARM, o None si el `.cube` no es válido."""
    c = lee_cube_q16(texto)
    if c is None:
        return None
    n, lo, hi, cub = c
    sat = lambda q: max(-64, min(63, q))
    cl = lambda v: max(0, min(65536, v))
    z = []
    for i in range(405):
        j, a, b = i // 81, i // 9 % 9, i % 9
        y, cb, cr = j * 16384, a * 8192 - 32768, b * 8192 - 32768
        r = cl(y + ((91882 * cr) >> 16))
        bl = cl(y + ((116131 * cb) >> 16))
        n16 = ((y << 16) - 19595 * r - 7471 * bl) >> 16
        g = cl((n16 * 111642) >> 16)
        rgb = [r, g, bl]
        u, t = _ycc(rgb), _ycc(_tri(n, lo, hi, cub, rgb))
        z.append([(t[0] - u[0] + 8) >> 4, ((t[1] - u[1]) * 5456 + 32768) >> 16, ((t[2] - u[2]) * 5456 + 32768) >> 16])
    bits = 0
    for i in range(405):                      # G90: v = z − Σ Δ²z/12 (21/256), Δ² solo con ambos vecinos
        j, a, b = i // 81, i // 9 % 9, i % 9
        q = []
        for k in range(3):
            l = 0
            for ok, paso in ((0 < j < 4, 81), (0 < a < 8, 9), (0 < b < 8, 1)):
                if ok:
                    l += z[i + paso][k] - 2 * z[i][k] + z[i - paso][k]
            q.append(sat((z[i][k] - ((21 * l) >> 8) + 8) >> 4))
        bits |= (((q[0] & 127) << 14) | ((q[1] & 127) << 7) | (q[2] & 127)) << (21 * i)
    return bits.to_bytes(TAM_TABLA, "little")


def blob_esperado(cubes: dict[int, str]) -> bytes:
    """Blob de Backup que escribe el userland para `{ranura 1…6: texto .cube}` (las no válidas quedan a 0)."""
    b = bytearray(BK_TAM)
    struct.pack_into("<I", b, 0, MAGIC)
    b[4], b[6] = 1, SLOTS
    for s in range(SLOTS):
        t = referencia(cubes[s + 1]) if (s + 1) in cubes else None
        if t:
            b[8 + s] = 1
            b[16 + s * TAM_TABLA:16 + (s + 1) * TAM_TABLA] = t
    return bytes(b)


# ---------- arnés Unicorn: ARM compilado + `dlsym`/Fsys/Backup simulados con el contrato leído del código real ----------
class Camara:
    """Estado del mundo simulado: tarjeta (letra o None), ficheros `{n: bytes}`, Backup del id `BK_ID`, contadores."""

    def __init__(self, ficheros: dict[int, bytes] | None = None, letra: str | None = "E", backup: bytes | None = None):
        self.ficheros, self.letra, self.backup = ficheros or {}, letra, backup or bytes(BK_TAM)
        self.escrituras = 0
        self.aperturas: list[str] = []
        self.log: list = []
        self.pasos: list = []            # un evento por cada `sleep`: callable(cam) o None; al agotarse se detiene la emulación


def emula(cam: Camara, blob: bytes | None = None, sim: dict | None = None, max_instr: int = 3_000_000_000) -> Camara:
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_SP,
    )
    if blob is None or sim is None:
        blob, sim = compila()
    code, stubs, heap, stack = 0x10000000, 0x20000000, 0x30000000, 0x40000000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for a, s in ((code, 0x10000), (stubs, 0x1000), (heap, 0x8000000), (stack, 0x20000)):
        mu.mem_map(a, s)
    mu.mem_write(code, blob)
    nombres = ["dlsym", "dlopen", "malloc", "free", "sleep", "Fsys_Open", "Fsys_Read", "Fsys_Close", "Fsys_GetDriveLetter", "Backup_read", "Backup_write"]
    dir_ = {n: stubs + 0x10 * i for i, n in enumerate(nombres)}
    inv = {a: n for n, a in dir_.items()}
    estado = {"brk": heap, "h": 0, "pos": 0, "sleeps": 0}
    leer_c = lambda a: _cstr(mu, a)

    def hook(mu, addr, size, _):
        n = inv.get(addr)
        if n is None:
            return
        r = lambda k: mu.reg_read(UC_ARM_REG_R0 + k)
        ret = 0
        if n == "dlsym":
            nm = leer_c(r(1))
            ret = dir_[nm] | 1 if nm in dir_ else 0
        elif n == "dlopen":
            ret = 1 if leer_c(r(0)) in ("libInfraFsys.so", "libbackup.so") else 0
        elif n == "malloc":
            ret = estado["brk"]
            estado["brk"] += (r(0) + 15) & ~15
        elif n == "free":
            ret = 0
        elif n == "sleep":
            estado["sleeps"] += 1
            if not cam.pasos:
                mu.emu_stop()
            else:
                ev = cam.pasos.pop(0)
                if ev:
                    ev(cam)
        elif n == "Fsys_GetDriveLetter":
            d = leer_c(r(0))
            ret = ord(cam.letra) if cam.letra and d == "/dev/mmca" else 0
            cam.log.append(("drive", d, ret))
        elif n == "Fsys_Open":
            p = leer_c(r(0))
            cam.aperturas.append(p)
            ok = cam.letra and p.startswith(cam.letra + ":/LUT/LUT") and p.endswith(".cube") and r(2) == 1
            k = int(p[10]) if ok else 0
            if ok and k in cam.ficheros:
                estado["pos"] = 0
                estado["h"] = k
                mu.mem_write(r(1), struct.pack("<i", 7))
            else:
                ret = -1 & 0xFFFFFFFF
        elif n == "Fsys_Read":
            f = cam.ficheros[estado["h"]]
            ch = f[estado["pos"]:estado["pos"] + r(2)]
            mu.mem_write(r(1), ch)
            estado["pos"] += len(ch)
            ret = len(ch)
        elif n == "Fsys_Close":
            ret = 0
        elif n == "Backup_read":
            assert r(0) == BK_ID
            mu.mem_write(r(1), cam.backup)
        elif n == "Backup_write":
            assert r(0) == BK_ID >> 16 and r(1) == BK_ID
            cam.backup = bytes(mu.mem_read(r(2), BK_TAM))
            cam.escrituras += 1
        mu.reg_write(UC_ARM_REG_R0, ret)
        mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR) | 1)

    mu.hook_add(UC_HOOK_CODE, hook, begin=stubs, end=stubs + 0x100)
    mu.reg_write(UC_ARM_REG_SP, stack + 0x20000 - 16)
    mu.reg_write(UC_ARM_REG_LR, stubs + 0xF00)               # retorno inesperado → fin
    mu.reg_write(UC_ARM_REG_R0, dir_["dlsym"] | 1)
    try:
        mu.emu_start((code + sim["lutsd_hilo"]) | 1, stubs + 0xF00, count=max_instr)
    except Exception as e:
        raise RuntimeError(f"emulación: {e}") from e
    return cam


def _cstr(mu, a: int) -> str:
    out = bytearray()
    while (c := mu.mem_read(a + len(out), 1)[0]):
        out.append(c)
    return out.decode()


if __name__ == "__main__":
    import numpy as np
    sys.path.insert(0, str(Path(__file__).parent))
    import cube_a6000 as C
    with tempfile.TemporaryDirectory() as d:
        txt = {}
        for k, (n, f) in enumerate(((17, C.SINT["pelicula"]), (32, C.SINT["teal_orange"]), (33, C.SINT["identidad"])), 1):
            p = Path(d) / f"{k}.cube"
            C.escribe_cube(p, f, n, f"t{k}")
            txt[k] = p.read_text()
        cam = Camara({k: v.encode() for k, v in txt.items()}, backup=None)
        cam.pasos = [None]
        emula(cam)
        esp = blob_esperado(txt)
        print("blob igual a la referencia:", cam.backup == esp, "escrituras:", cam.escrituras, "válidas:", list(cam.backup[8:14]), "aperturas:", cam.aperturas[:3])
        print("tabla 1 no nula:", bool(np.any(np.frombuffer(cam.backup[16:16 + TAM_TABLA], np.uint8))))
