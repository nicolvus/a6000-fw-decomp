#!/usr/bin/env python3
"""G27 — S-Gamut3 y S-Gamut3.Cine de la A6300 en el núcleo `av-cam.bin` de la A6000 fw3.21. NO instala nada.

La A6300 convierte el tipo de Color Mode en un id (tabla `av-cam-a6300 0x43dcecb6`: 10 → 0x18 S-Gamut3, 11 → 0x19 S-Gamut3.Cine) y un `switch` lo convierte en
(índice de matriz, índice de conjunto de deltas): 0x18 → (0x13, 0x1a), 0x19 → (0xf, 0x19). Matrices (9 s16) y conjuntos (24 s8) están en la propiedad de Backup
`0x30001` (NVRAM, preset `CX79100_*`); la A6000 no los trae. Aquí se copian al hueco libre del núcleo (tras las 8 curvas de pp_curves_patch.py) y se añade
el código mínimo, todo como lista de escrituras (dirección, bytes) para el mismo `pp_ram.sh` que las curvas:
  1. tabla tipo→id de 11 entradas (la A6000 tiene 7; los tipos 8 y 9 siguen dando id 0 = Movie) y `cmp #6 → #10`;
  2. casos 0x18/0x19 en el `switch` de ids (`0x437a4cd4`, gancho en su `bhi.w` por defecto) con matrices 0x10/0x11 y conjunto 0x19 propios de la A6000;
  3. la función de matrices (`0x437a4b40`) y la de deltas (`0x437a44d0`) aceptan los índices nuevos y leen los datos del hueco.
Orden de escritura: datos → tabla de tipos → ganchos de código (un parche a medias deja el comportamiento original para los tipos 10/11).
Riesgo (G25): un parche de código por `/dev/mem` puede no verse si la caché de instrucciones conserva esas líneas. NO probado en cámara.
"""
import io
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import patch_libobj_pp as P

ROOT = Path(__file__).resolve().parents[2]
BASE = 0x43541000
PRESET_A6300 = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0110_backup/SYSMUSASHI-DSLR/DX/CX79100_E38.bin"
CAVE = 0x43FB7400                                   # SLOT0 + 8·STRIDE de pp_curves_patch; el hueco llega a 0x43FB8EE0
TABLA_TIPOS, MAT_S3, MAT_CINE, SET = CAVE, CAVE + 0x10, CAVE + 0x22, CAVE + 0x34
CODE_SW, CODE_MX, CODE_DL = CAVE + 0x50, CAVE + 0x90, CAVE + 0xD0
ID_S3, ID_CINE = 0x18, 0x19                         # ids de la A6300
IDX_S3, IDX_CINE, IDX_SET = 0x10, 0x11, 0x19        # índices nuevos: matrices 0x10/0x11 (A7S usa 0x10; +0x322/+0x334 libres) y conjunto 0x19 (en la A6300 0x19 = 0x1a)
TIPOS = bytes([0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0, 0, ID_S3, ID_CINE, 0])    # tipo 1…11 (+ relleno)

TIPO_CMP, TIPO_LIT, TIPO_PC, TABLA_ORIG = 0x437AA816, 0x437AAFE0, 0x437AA822, 0x43CA66F2      # `cmp r0,#6` · literal de `ldr.w r2,[pc,#0x7c4]` (tabla = TIPO_PC + literal)
SW_SITE, SW_DEFECTO, SW_TBH, SW_EPILOGO = 0x437A4DB2, 0x437A4F7E, 0x437A4DB6, 0x437A4FAE
MX_GATE, MX_SITE, MX_NORMAL, MX_F, MX_SIGUE = 0x437A4B42, 0x437A4B62, 0x437A4B66, 0x437A4B76, 0x437A4B7A
DL_GATE, DL_SITE, DL_NORMAL, DL_M18, DL_SIGUE = 0x437A44D2, 0x437A44FA, 0x437A44FE, 0x437A450C, 0x437A4510
ORIG = {TIPO_CMP: "0628", SW_SITE: "00f2e480", MX_GATE: "0f29", MX_SITE: "0f2907d0", DL_GATE: "1829", DL_SITE: "182c06d0"}
HI, EQ, HS, LO = 8, 0, 2, 3


def _hw(*w):
    return P._hw(*w)


def movt(rd, v):
    return _hw(0xF2C0 | ((v >> 11) & 1) << 10 | (v >> 12), ((v >> 8) & 7) << 12 | rd << 8 | (v & 0xFF))


def dir32(rd, v):                                    # movw + movt
    return P.movw(rd, v & 0xFFFF) + movt(rd, v >> 16)


def cmp_w(rn, v):                                    # cmp.w rn,#imm8 (T2)
    return _hw(0xF1B0 | rn, 0x0F00 | v)


def asm(at, items):
    """Ensamblador de dos pasadas: items = bytes | ("L", etiqueta) | (tamaño, f(pos, etiquetas) -> bytes)."""
    lab = {}
    for _ in range(2):
        pos, out = at, b""
        for it in items:
            if isinstance(it, bytes):
                out += it
                pos += len(it)
            elif it[0] == "L":
                lab[it[1]] = pos
            else:
                out += it[1](pos, lab)
                assert len(out) == pos - at + it[0]
                pos += it[0]
    return out


def tgt(t, lab, pos):
    return lab.get(t, pos) if isinstance(t, str) else t


def B(t):
    return 4, lambda pos, lab: P.b_w(pos, tgt(t, lab, pos))


def BC(cond, t):
    return 4, lambda pos, lab: P.bcc_w(pos, tgt(t, lab, pos), cond)


def datos_a6300(preset: bytes) -> tuple[bytes, bytes, bytes]:
    """Matriz 0x13, matriz 0xf y conjunto 0x1a de la propiedad 0x30001 del preset de Backup de la A6300 (no están en su `av-cam`)."""
    sys.path.insert(0, str(ROOT / "references/pmca"))
    from pmca.backup import BackupFile
    t = {i: bytes(p.data) for i, p in BackupFile(io.BytesIO(preset)).listProperties()}[0x30001]
    return t[0x590:0x590 + 18], t[0x310:0x310 + 18], t[0x360 + 0x18 * (0x1A - 0x18):][:24]


def codigo() -> dict[int, bytes]:
    caso = lambda m: [_hw(0x2100, 0xF04F, 0x09FF, 0x464B, 0x2200 | IDX_SET, 0x2500 | m)]   # movs r1,#0; mov.w sb,#0xff; mov r3,sb; movs r2,#conjunto; movs r5,#matriz
    sw = asm(CODE_SW, [BC(HI, "mayor"), B(SW_TBH), ("L", "mayor"), cmp_w(8, ID_S3 - 1), BC(EQ, "s3"), cmp_w(8, ID_CINE - 1), BC(EQ, "ci"), B(SW_DEFECTO),
                       ("L", "s3"), *caso(IDX_S3), B(SW_EPILOGO), ("L", "ci"), *caso(IDX_CINE), B(SW_EPILOGO)])
    mx = asm(CODE_MX, [_hw(0x290F), BC(LO, "normal"), BC(EQ, "f"), _hw(0x2910), BC(EQ, "s3"),
                       dir32(1, MAT_CINE), B(MX_SIGUE), ("L", "s3"), dir32(1, MAT_S3), B(MX_SIGUE), ("L", "normal"), B(MX_NORMAL), ("L", "f"), B(MX_F)])
    dl = asm(CODE_DL, [_hw(0x2C18), BC(EQ, "m18"), _hw(0x2C00 | IDX_SET), BC(HS, "nuevo"), B(DL_NORMAL), ("L", "m18"), B(DL_M18),
                       ("L", "nuevo"), dir32(4, SET), B(DL_SIGUE)])
    return {CODE_SW: sw, CODE_MX: mx, CODE_DL: dl}


def patches(base: bytes, preset_a6300: bytes) -> list[tuple[int, bytes, str]]:
    """Escrituras (dirección virtual, bytes, descripción). Las descripciones empiezan por «dato» o «gancho» (orden de escritura en pp_curves_patch)."""
    for a, o in ORIG.items():
        assert base[a - BASE:a - BASE + len(o) // 2] == bytes.fromhex(o), hex(a)
    assert not any(base[CAVE - BASE:CAVE + 0x100 - BASE]), "el hueco ya no está a cero"
    assert struct.unpack_from("<I", base, TIPO_LIT - BASE)[0] == 0x4FBED0 and base[TABLA_ORIG - BASE:][:7] == TIPOS[:7]
    m_s3, m_cine, delta = datos_a6300(preset_a6300)
    assert m_s3 == struct.pack("<9h", 1084, -110, 49, -11, 1086, -51, 133, -482, 1373)
    assert m_cine == struct.pack("<9h", 1203, -205, 26, -8, 1083, -51, 132, -393, 1285)
    assert delta[:8] == bytes([0xE4, 8, 0xE4, 8, 0xC0, 0xC0, 0xC0, 0xC0]) and not any(delta[8:])
    cod = codigo()
    assert CODE_SW + len(cod[CODE_SW]) <= CODE_MX and CODE_MX + len(cod[CODE_MX]) <= CODE_DL and CODE_DL + len(cod[CODE_DL]) <= CAVE + 0x100
    return [(TABLA_TIPOS, TIPOS, "dato tabla tipo→id"), (MAT_S3, m_s3, "dato matriz S-Gamut3"), (MAT_CINE, m_cine, "dato matriz S-Gamut3.Cine"),
            (SET, delta, "dato deltas S-Gamut3"),
            (CODE_SW, cod[CODE_SW], "dato código switch"), (CODE_MX, cod[CODE_MX], "dato código matrices"), (CODE_DL, cod[CODE_DL], "dato código deltas"),
            (TIPO_LIT, struct.pack("<I", TABLA_TIPOS - TIPO_PC), "gancho literal tabla de tipos"), (TIPO_CMP, bytes.fromhex("0a28"), "gancho cmp tipo ≤ 10"),
            (MX_GATE, bytes.fromhex("1129"), "gancho cmp matriz ≤ 0x11"), (DL_GATE, bytes.fromhex("1a29"), "gancho cmp conjunto ≤ 0x1a"),
            (MX_SITE, P.b_w(MX_SITE, CODE_MX), "gancho matrices"), (DL_SITE, P.b_w(DL_SITE, CODE_DL), "gancho deltas"),
            (SW_SITE, P.b_w(SW_SITE, CODE_SW), "gancho switch")]
