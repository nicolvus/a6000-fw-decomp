"""G92 — curva 1D propia DESPUÉS de la gamma (ranura libre de la cadena de tono de `av-cam`) + LUT 3D 5×9×9.

La gamma que llega al procesador la compone `FUN_438538e4` (512 puntos en `obj+0x26e`, 11 bits) como cadena de tablas:
`gamma[bd9·2+bd6]` → una de: `c5c[bdb]` (Black Gamma, si `bd1`), `c5c[bdb]∘c60[bdd]` (si `bd3`) o `c68[be1]` (si `bd5`).
`c68` = puntero `0x440013cc`, 14 tablas de 1024 u16 (entrada = código de gamma 0…1023); **6 y 8…13 apuntan a la
identidad `0x43bfaf2a`** ⇒ libres. Poner una curva propia en `c68[8]` y `bd5 = 1`, `be1 = 8` (con `bd1 = bd3 = 0`)
aplica T a R, G y B por igual tras la gamma elegida por el usuario, en todos los modos que usan esa curva.

`emula(...)` ejecuta la función real con Unicorn; `curva_post(cadena)` da la tabla de 1024 u16 de una `cube_a6000.Cadena`.
"""
from __future__ import annotations

import struct
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
BASE = 0x43541000
F_CADENA = 0x438538E4          # FUN_438538e4(obj): compone la curva de 512 puntos
TAB_GAMMA = 0x44001404         # punteros de gamma, índice bd9·2 + bd6
TAB_C68 = 0x440013CC           # 14 punteros (be1); 6 y 8…13 = identidad
IDENTIDAD = 0x43BFAF2A
RANURA = 8


def _u32(img: bytes, a: int) -> int:
    return struct.unpack_from("<I", img, a - BASE)[0]


def gamma(img: bytes, idx: int, foto: int = 0) -> np.ndarray:
    p = _u32(img, TAB_GAMMA + 4 * (idx * 2 + foto))
    return np.frombuffer(img[p - BASE:p - BASE + 4096], "<u2").astype(int)


def emula(img: bytes, gamma_idx: int, tabla: np.ndarray | None = None, bd5: int = 1, be1: int = RANURA,
          bd1: int = 0, bd3: int = 0, x: np.ndarray | None = None) -> np.ndarray:
    """Ejecuta FUN_438538e4 sobre un objeto mínimo; `tabla` (1024 u16) sustituye a c68[be1]. → 512 valores de obj+0x26e."""
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(BASE, (len(img) + 0xFFF) & ~0xFFF)
    mu.mem_write(BASE, img)
    obj, pila, tab, ret = 0x60000000, 0x61000000, 0x62000000, 0x63000000
    for a in (obj, pila, tab, ret):
        mu.mem_map(a, 0x10000)
    o = bytearray(0x1000)
    o[0xBD9], o[0xBD6], o[0xBD1], o[0xBD3], o[0xBD5], o[0xBE1] = gamma_idx, 0, bd1, bd3, bd5, be1
    o[0xBDF], o[0xBDB], o[0xBDD] = 7, 3, 3                      # sin knee/contraste (valores neutros del propio código)
    o[0x66E:0x66E + 1024] = np.asarray(np.arange(512) * 4 if x is None else x, "<u2").tobytes()
    struct.pack_into("<H", o, 0x66C, 0x3FF)
    mu.mem_write(obj, bytes(o))
    if tabla is not None:
        mu.mem_write(tab, np.asarray(tabla, "<u2").tobytes())
        mu.mem_write(TAB_C68 + 4 * be1, struct.pack("<I", tab))
    mu.reg_write(UC_ARM_REG_R0, obj)
    mu.reg_write(UC_ARM_REG_SP, pila + 0x8000)
    mu.reg_write(UC_ARM_REG_LR, ret | 1)
    mu.emu_start(F_CADENA | 1, ret, count=5_000_000)
    return np.frombuffer(mu.mem_read(obj + 0x26E, 1024), "<u2").astype(int)


def curva_post(cadena) -> np.ndarray:
    """T de una `cube_a6000.Cadena` (sin matriz) como tabla de 1024 u16 sobre el código de gamma (entrada = salida de la gamma)."""
    v = np.arange(1024) / 1023
    t = cadena.pre_lut(np.repeat(v[:, None], 3, 1))[:, 1]       # sin M las tres columnas son iguales
    return np.clip(np.round(np.maximum.accumulate(t) * 1023), 0, 1023).astype(np.uint16)
