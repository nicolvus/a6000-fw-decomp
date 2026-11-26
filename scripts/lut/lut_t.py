"""G115 (LUT-T-1) — curva 1D tras la gamma para el ajuste «LUT»: ganchos en las llamadas a `FUN_43852f7c`, almacenamiento compacto y referencia de la expansión.

Reutiliza el mecanismo ya probado de la función Film (`film_patch`, G98/G111), que es el de la «gamma extendida» de Sony
(`CameraEx.setExtendedGammaTable`): en las cuatro llamadas a `FUN_43852f7c` que construyen la curva —`0x438548b0`, `0x43854c46`,
`0x43854ff6`, `0x43b098cc`, con `r0` = objeto de tono e indicadores ya copiados de la config— se pone `bd5 = 1`, `be1 = 8`,
`bd1 = bd3 = 0` y `c68[8]` (`0x440013ec`) = un búfer propio de la curva. Así la curva se aplica a los DOS consumidores:
la curva de 512 puntos (`FUN_438538e4`) y la rejilla de 96 nodos que va al hardware (`FUN_43853200`). Con el ajuste «LUT» en Off
la cueva no escribe ni un byte del objeto (indicadores y `c68[8]` de fábrica): el comportamiento es el de fábrica.

`FUN_43852f7c` se elige en vez de las llamadas a `FUN_438538e4` (la propuesta de G92 §3) porque cubre también la rejilla de 96
nodos; una sola pareja de ganchos sirve a los dos consumidores.

La curva (1024 u16 sobre el código de gamma) se guarda compacta: 33 nodos cada 32 códigos (`nodos`/`expande`), un registro de 68 B
(`u16 nº de nodos` + 33 u16). Medido (20 000 colores uniformes, ΔE2000 medio, contra la función de la LUT —la misma que genera
los `.cube` 33³ de G95—): película 0,198 con la curva exacta de 1024 frente a 0,202 con los 33 nodos; la desviación máxima es de 3
códigos de 1023.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(Path(__file__).parent)]
import avcam_dinamico as D
import cfw_ajustes as cfw

NN, PASO = 33, 32                      # nodos y paso en códigos de gamma (33 nodos cubren 0…1023: 32 tramos de 32 + el extremo)
REC = 2 + 2 * NN                      # registro compacto: u16 nº de nodos (0 = sin curva) + 33 u16
C68_8 = 0x440013EC                     # c68[8]: ranura libre de la tabla de gamma extendida (G92 §3)
IDENTIDAD = 0x43BFAF2A                 # curva identidad de fábrica de esa ranura
SITIOS_T = (0x438548B0, 0x43854C46, 0x43854FF6, 0x43B098CC)   # `bl FUN_43852f7c` (mismos que `film_patch`; hay test de que coinciden)
F_PREP = 0x43852F7C
BK_T_OFF = 16 + D.SD_RANURAS * D.LUT_BYTES             # 0x1900: justo detrás de las 6 tablas del blob (16 + 6·1064)

# Zona de la curva en el `.dat`. G107 §3: ZONA_A es la tabla T1 de estabilización y ZONA_B las tablas BOKS del YC de captura
# (las dos «a cero» en fábrica, pero VIVAS), así que aquí no se escribe nada nuevo. Se usa un tramo del hueco G18 que ningún
# otro parche ocupa: 0x43FB8360…0x43FB8EE0 (2944 B), por detrás de la tabla de ISO (`iso_avcam_patch`: cueva 0x43FB8280,
# tabla 0x43FB82A0 + 0x30 entradas = …0x43FB8360). Ocupantes conocidos de G18: PP ≤ 0x43FB7EC0, bulb timer 0x43FB7F00,
# gancho JPEG 0x43FB7F80…0x43FB7FC4, Film 0x43FB7E80…0x43FB811C, ISO 0x43FB8280…0x43FB8360.
# Verificación: G107 §3 da el hueco G18 por libre con 0 referencias relativas al PC ni `adr`, y los bytes están a cero en
# el fichero (lo comprueba `apply_bytes`); NO se ha re-hecho aquí un barrido independiente de `ldr/add pc` (límite del informe).
ZONA_T18 = (0x43FB8360, 0x43FB8EE0)
T_TABLAS = ZONA_T18[0]                                  # 3 registros de 68 B (0x43FB8360…0x43FB842C)
T_CELDA = T_TABLAS + 3 * REC                            # celda de 4 B con el búfer de la curva expandida
T_CODIGO = (T_CELDA + 4 + 3) & ~3                       # cueva de la curva (0x43FB8430)
AJ = cfw.POR_ID["lut"]


# ---------- curva compacta ----------
def curva_valores(t) -> list[int]:
    """1024 valores (lista) desde una lista/array o desde 2048 B little-endian."""
    if isinstance(t, (bytes, bytearray)):
        assert len(t) == 2048, len(t)
        return list(struct.unpack("<1024H", bytes(t)))
    t = [int(v) for v in t]
    assert len(t) == 1024
    return t


def nodos(t) -> list[int]:
    """1024 u16 → 33 nodos: `T[i·32]` (i = 0…31) y `T[1023]` como extremo."""
    t = [int(v) for v in t]
    assert len(t) == 1024
    return [t[i * PASO] for i in range(NN - 1)] + [t[1023]]


def expande(n) -> list[int]:
    """33 nodos → 1024 u16, réplica exacta de lo que hace la cueva (interpolación lineal con redondeo)."""
    assert len(n) == NN
    out = []
    for i in range(1024):
        k = min(i // PASO, NN - 2)
        f = i - k * PASO
        out.append((n[k] * (PASO - f) + n[k + 1] * f + PASO // 2) // PASO)
    out[1023] = n[NN - 1]                              # el extremo se copia tal cual (la cueva también lo hace): blanco exacto
    return out


def registro(n) -> bytes:
    """Registro de 68 B: `u16 nº de nodos` + 33 u16 (0xFFFF… = sin curva cuando se pasa `None`)."""
    return struct.pack(f"<H{NN}H", 0 if n is None else NN, *([0] * NN if n is None else n))


def lee_registro(b: bytes) -> list[int] | None:
    k, *n = struct.unpack_from(f"<H{NN}H", b)
    return n if k == NN else None


_T_DEFECTO: list[bytes] = []


def t_por_defecto() -> list[bytes]:
    """Registros de las 3 tablas del `.dat`: solo la película lleva curva (medido: teal&orange 0,065→0,201 e identidad 0,027→0,072 empeoran)."""
    if not _T_DEFECTO:
        import cube_a6000 as C
        import tono_post as P
        ch = C.descompone(C.lut_pelicula, usa_M=False, usa_T=True, usa_L=True)
        _T_DEFECTO.extend([registro(None), registro(nodos(P.curva_post(ch))), registro(None)])
    return list(_T_DEFECTO)


# ---------- cueva ----------
def _c(r: str, v: int) -> str:
    return f"movw {r}, #{v & 0xFFFF:#x}\n    movt {r}, #{v >> 16:#x}\n"


def asm(inicio: int, sd: bool = False, ajuste=None) -> str:
    """Fuente Thumb de la cueva. `sd`: la curva se busca antes en el blob de Backup `0x150005` (G89, ranuras 1…6) que en el `.dat`."""
    ajuste = ajuste or AJ                 # el build con SD pasa `lut_patch.AJ_SD` (7 opciones)
    blob = f"""
blob_lut:
    push {{r3, r4, r5, lr}}
    {_c('r4', D.LUT_CELDA)}
    ldr r5, [r4, #4]
    cmp r5, #0
    bne.w bl_leer
    movw r0, #{D.BK_TAM}
    {_c('r1', D.MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w bl_no
    str r0, [r4, #4]
    mov r5, r0
bl_leer:
    {_c('r0', D.BK_ID)}
    mov r1, r5
    bl #{cfw.BACKUP_READ:#x}
    ldr r0, [r5]
    {_c('r1', D.BK_MAGIC)}
    cmp r0, r1
    bne.w bl_no
    mov r0, r5
    pop {{r3, r4, r5, lr}}
    bx lr
bl_no:
    movs r0, #0
    pop {{r3, r4, r5, lr}}
    bx lr
""" if sd else ""
    sd_src = f"""
    bl blob_lut
    cmp r0, #0
    beq.w c_dat
    subs r1, r8, #1
    cmp r1, #{D.SD_RANURAS}
    bhs.w c_dat
    add r2, r0, r1
    ldrb r2, [r2, #8]
    cmp r2, #1
    bne.w c_dat
    movw r3, #{REC}
    mul r1, r1, r3
    add r0, r0, r1
    {_c('r5', BK_T_OFF)}
    add r5, r5, r0
    b.w c_nodos
""" if sd else ""
    return f"""
t_curva:
    push {{r4-r8, lr}}
    mov r4, r0
    bl lee_lut
    mov r8, r0
    cmp r0, #0
    beq.w c_off
{sd_src}c_dat:
    subs r1, r8, #1
    cmp r1, #3
    bhs.w c_off
    movw r3, #{REC}
    mul r1, r1, r3
    {_c('r2', T_TABLAS)}
    add r5, r2, r1
c_nodos:
    ldrh r0, [r5]
    cmp r0, #{NN}
    bne.w c_off
    {_c('r7', T_CELDA)}
    ldr r6, [r7]
    cmp r6, #0
    bne.w c_hay
    movw r0, #2048
    {_c('r1', D.MALLOC | 1)}
    blx r1
    cmp r0, #0
    beq.w c_off
    str r0, [r7]
    mov r6, r0
c_hay:
    adds r5, #2
    movs r3, #0
expande:
    lsrs r1, r3, #5
    adds r2, r1, #1
    lsls r2, r2, #1
    ldrh r2, [r5, r2]
    lsls r1, r1, #1
    ldrh r0, [r5, r1]
    subs r2, r2, r0
    and r1, r3, #{PASO - 1}
    mul r2, r2, r1
    adds r2, #16
    lsrs r2, r2, #5
    adds r0, r0, r2
    strh.w r0, [r6, r3, lsl #1]
    adds r3, #1
    cmp.w r3, #1024
    blo.w expande
    ldrh r0, [r5, #{2 * (NN - 1):#x}]
    strh.w r0, [r6, #2046]
    {_c('r1', C68_8)}
    str r6, [r1]
    movs r1, #1
    strb.w r1, [r4, #0xbd5]
    movs r1, #8
    strb.w r1, [r4, #0xbe1]
    movs r1, #0
    strb.w r1, [r4, #0xbd1]
    strb.w r1, [r4, #0xbd3]
    b.w c_fin
c_off:
    {_c('r7', T_CELDA)}
    ldr r6, [r7]
    cmp r6, #0
    beq.w c_fin
    {_c('r1', C68_8)}
    ldr r2, [r1]
    cmp r2, r6
    bne.w c_fin
    {_c('r2', IDENTIDAD)}
    str r2, [r1]
c_fin:
    mov r0, r4
    pop {{r4-r8, lr}}
    b.w #{F_PREP:#x}
{blob}lee_lut:
    push {{lr}}
{cfw.leer_asm(ajuste, "tl")}
    pop {{r3}}
    bx r3
    .align 2
"""


def cueva(sd: bool = False, ajuste=None) -> tuple[list[tuple[int, bytes]], int]:
    """(escrituras (va, bytes), entrada) de la cueva de la curva, en `T_CODIGO` (ventana de G18; no toca ZONA_A/ZONA_B)."""
    c = cfw.ensamblar(asm(T_CODIGO, sd, ajuste), T_CODIGO)
    assert T_CODIGO + len(c) <= ZONA_T18[1], hex(T_CODIGO + len(c))
    return [(T_CODIGO, c)], T_CODIGO


def escrituras(sd: bool = False, curvas: list[bytes] | None = None, ajuste=None) -> tuple[list[tuple[int, bytes]], int]:
    """Todo lo que añade la curva: 3 registros (68 B) + celda + código, en `ZONA_T18`. → (escrituras, entrada)."""
    curvas = curvas if curvas is not None else t_por_defecto()
    assert len(curvas) == 3 and all(len(x) == REC for x in curvas)
    esc, ent = cueva(sd, ajuste)
    return [(T_TABLAS, b"".join(curvas)), (T_CELDA, bytes(4))] + esc, ent


# ---------- emulación (Unicorn) ----------
BK_SIM, HEAP_SIM = 0x32000000, 0x31000000


def _stub_backup(ajuste, blob_sim: int) -> bytes:
    """Backup_read(id, buf) simulado: el id del ajuste devuelve 1 byte desde `BK_SIM+0x7000`, el id del blob devuelve 16 KB de `blob_sim`."""
    return cfw.ensamblar(f"""
    {_c('r2', ajuste.backup)}
    cmp r0, r2
    bne.w otro
    {_c('r2', BK_SIM + 0x7000)}
    ldrb r2, [r2]
    strb r2, [r1]
    movs r0, #0
    bx lr
otro:
    {_c('r2', blob_sim)}
    {_c('r3', D.BK_TAM)}
cp:
    ldrb r0, [r2], #1
    strb r0, [r1], #1
    subs r3, #1
    bne.w cp
    movs r0, #0
    bx lr
""", cfw.BACKUP_READ)


def _stub_malloc(cnt: int, heap: int) -> bytes:
    """`malloc(n)` simulado: devuelve `heap + n_llamada·0x8000` (búferes distintos para la curva y para el blob)."""
    return cfw.ensamblar(f"""
    {_c('r2', cnt)}
    ldr r1, [r2]
    lsls r3, r1, #15
    adds r1, #1
    str r1, [r2]
    {_c('r0', heap)}
    add r0, r0, r3
    bx lr
""", D.MALLOC)


def blob(tablas: dict | None = None, curvas: dict | None = None, letra: str = "E") -> bytes:
    """Blob de 16 KB del Backup `0x150005` como lo escribe `lutsd.c`: cabecera, 6 tablas de 1064 B y, en `BK_T_OFF`, los registros de curva
    (68 B por ranura). `tablas`/`curvas` = {ranura 1…6: bytes}; una ranura con tabla o curva queda válida en la máscara de `+8`."""
    tablas, curvas = tablas or {}, curvas or {}
    b = bytearray(D.BK_TAM)
    struct.pack_into("<I", b, 0, D.BK_MAGIC)
    b[4], b[6], b[14] = 1, D.SD_RANURAS, ord(letra)
    for k in range(1, D.SD_RANURAS + 1):
        if k in tablas:
            assert len(tablas[k]) == D.LUT_BYTES
            b[16 + (k - 1) * D.LUT_BYTES:16 + k * D.LUT_BYTES] = tablas[k]
        if k in curvas:
            assert len(curvas[k]) == REC
            b[BK_T_OFF + (k - 1) * REC:BK_T_OFF + k * REC] = curvas[k]
        if k in tablas or k in curvas:
            b[8 + k - 1] = 1
    return bytes(b)


def _monta(img: bytes, blob: bytes | None, malloc_ok: bool, ajuste):
    from unicorn import UC_ARCH_ARM, UC_MODE_THUMB, Uc
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(D.BASE & ~0xFFF, ((len(img) + (D.BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(D.BASE, img)
    m = {"stack": 0x10000000, "obj": 0x20000000, "end": 0x30000000, "cnt": 0x30100000}
    for a, s in ((m["stack"] - 0x10000, 0x20000), (m["obj"], 0x2000), (m["end"], 0x1000), (HEAP_SIM, 0x100000), (m["cnt"], 0x1000), (BK_SIM, 0x8000)):
        mu.mem_map(a, s)
    mu.mem_write(BK_SIM, blob if blob is not None else bytes(D.BK_TAM))
    mu.mem_write(cfw.BACKUP_READ, _stub_backup(ajuste, BK_SIM))
    mu.mem_write(D.MALLOC, _stub_malloc(m["cnt"], HEAP_SIM) if malloc_ok else _stub_malloc(m["cnt"], 0))
    return mu, m


def _objeto(mu, obj: int, gamma_idx: int, bd1: int) -> None:
    o = bytearray(0x2000)
    o[0xBD9], o[0xBD1], o[0xBDB], o[0xBDF], o[0xBDD] = gamma_idx, bd1, 3, 7, 3
    o[0x1AE:0x1AE + 192] = np.asarray(np.linspace(0, 2047, 96).astype(int), "<u2").tobytes()
    o[0x66E:0x66E + 1024] = np.asarray(np.arange(512) * 4, "<u2").tobytes()
    struct.pack_into("<H", o, 0x66C, 0x3FF)
    mu.mem_write(obj, bytes(o))


def _paso(mu, m, entrada) -> dict:
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_SP

    def llama(f):
        mu.reg_write(UC_ARM_REG_R0, m["obj"])
        mu.reg_write(UC_ARM_REG_SP, m["stack"] + 0x8000)
        mu.reg_write(UC_ARM_REG_LR, m["end"] | 1)
        mu.emu_start(f | 1, m["end"], count=20_000_000)
        return mu.reg_read(UC_ARM_REG_R0)
    llama(entrada if entrada is not None else F_PREP)
    ok = llama(0x43853200) == 0
    rejilla = list(struct.unpack("<96I", mu.mem_read(m["obj"], 384)))
    llama(0x438538E4)
    ptr = struct.unpack("<I", mu.mem_read(C68_8, 4))[0]
    paleta = list(struct.unpack("<1024H", mu.mem_read(ptr, 2048))) if ptr != IDENTIDAD else None
    return {"curva": list(struct.unpack("<512H", mu.mem_read(m["obj"] + 0x26E, 1024))), "rejilla": rejilla, "c68_8": ptr,
            "rejilla_ok": ok, "ind": {k: mu.mem_read(m["obj"] + v, 1)[0] for k, v in (("bd1", 0xBD1), ("bd3", 0xBD3), ("bd5", 0xBD5), ("be1", 0xBE1))},
            "paleta": paleta}


def emula_tono(img: bytes, opcion: int, blob: bytes | None = None, entrada: int | None = None,
               gamma_idx: int = 1, bd1: int = 1, malloc_ok: bool = True, ajuste=None) -> dict:
    """Un paso de la construcción de la curva como en `FUN_43854a28`: la cueva (`entrada`; None = `FUN_43852f7c` de fábrica) y después los dos consumidores
    reales, la rejilla de 96 nodos (`FUN_43853200`) y la curva de 512 puntos (`FUN_438538e4`).
    → {"curva": 512 valores de `obj+0x26e`, "rejilla": 96 u32 de `obj+0`, "c68_8": puntero de la ranura, "rejilla_ok", "ind": {bd1, bd3, bd5, be1}, "paleta": 1024 u16}."""
    ajuste = ajuste or AJ
    mu, m = _monta(img, blob, malloc_ok, ajuste)
    mu.mem_write(BK_SIM + 0x7000, bytes([opcion & 0xFF]))
    _objeto(mu, m["obj"], gamma_idx, bd1)
    return _paso(mu, m, entrada)


def emula_secuencia(img: bytes, opciones, blob: bytes | None = None, entrada: int | None = None, ajuste=None) -> list[dict]:
    """Varios pasos sobre el MISMO emulador (el objeto y `c68[8]` se conservan entre pasos): sirve para comprobar que al volver a Off se restaura la identidad."""
    ajuste = ajuste or AJ
    mu, m = _monta(img, blob, True, ajuste)
    _objeto(mu, m["obj"], 1, 1)
    out = []
    for o in opciones:
        mu.mem_write(BK_SIM + 0x7000, bytes([o & 0xFF]))
        out.append(_paso(mu, m, entrada))
    return out
