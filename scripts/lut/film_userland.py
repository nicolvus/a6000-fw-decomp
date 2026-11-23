#!/usr/bin/env python3
"""G97 — userland de las simulaciones de película (`userland/films.c`): datos, menú, compilación, inyección en `viewUnified2.so` y emulación.

`FILAS` define el menú «Film» (filas de ≤ 7 opciones: tope medido de la lista, G36): Off + hasta 6 looks por fila, numerados en ese orden (1…38).
`datos_h(looks.npz)` genera `films_datos.h` (tablas empaquetadas a 21 bits y curvas de 1024 u16); `compila()` deja el binario Thumb independiente de posición
y `patch_vu2()` lo cuelga de `DT_INIT` con el mismo tramo que G89 (`lut_sd_vu2`), entrando en `films_hilo`.
"""
from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(Path(__file__).parent)]
import cfw_ajustes as cfw

SRC = Path(__file__).parent / "userland/films.c"
BK_ID, BK_TAM, MAGIC, OFF_T, TAM_TABLA = 0x150005, 16384, 0x4D4C4946, 0x1000, 1064
ACK_ID = cfw.ID_LIBRES[8]
BASE_COMPILADO = 0x10000

# (etiqueta de la fila, ((id del catálogo, nombre en el menú), …)); ≤ 6 looks por fila (+ Off = 7 opciones)
FILAS = (
    ("Kodak 1", (("kodak_ektachrome_100", "Ektachrome"), ("kodak_ektar_100", "Ektar 100"), ("kodak_gold_200", "Gold 200"),
                 ("kodak_kodachrome_64", "Kodachrome"), ("kodak_portra_160", "Portra 160"), ("kodak_portra_400", "Portra 400"))),
    ("Kodak 2", (("kodak_portra_800", "Portra 800"), ("kodak_portra_800_push1", "Portra800 +1"), ("kodak_portra_800_push2", "Portra800 +2"),
                 ("kodak_ultramax_400", "Ultramax 400"), ("kodak_verita_200d", "Verita 200D"), ("kodak_vision3_200t", "Vision3 200T"))),
    ("Kodak 3", (("kodak_vision3_250d", "Vision3 250D"), ("kodak_vision3_500t", "Vision3 500T"), ("kodak_vision3_50d", "Vision3 50D"))),
    ("Fuji 1", (("fujifilm_c200", "C200"), ("fujifilm_pro_400h", "Pro 400H"), ("fujifilm_provia_100f", "Provia 100F"),
                ("fujifilm_velvia_100", "Velvia 100"), ("fujifilm_xtra_400", "X-Tra 400"), ("fujifilm_eterna_250", "Eterna 250"))),
    ("Fuji 2", (("fujifilm_eterna_250d", "Eterna 250D"), ("fujifilm_eterna_400", "Eterna 400"), ("fujifilm_eterna_500", "Eterna 500"),
                ("fujifilm_eterna_vivid_160", "Eterna V160"), ("fujifilm_eterna_vivid_250d", "Eterna V250D"), ("fujifilm_eterna_vivid_500", "Eterna V500"))),
    ("Fuji 3", (("fujifilm_f64d", "F-64D"), ("fujifilm_reala_500d", "Reala 500D"))),
    ("Fuji Sim 1", (("fuji_sim_astia", "Astia"), ("fuji_sim_classic_chrome", "Classic Chr."), ("fuji_sim_classic_neg", "Classic Neg"),
                    ("fuji_sim_eterna", "Eterna"), ("fuji_sim_eterna_bleach_bypass", "Eterna BB"), ("fuji_sim_pro_neg", "Pro Neg"))),
    ("Fuji Sim 2", (("fuji_sim_provia", "Provia"), ("fuji_sim_reala_ace", "Reala Ace"), ("fuji_sim_velvia", "Velvia"))),
)
CARPETA = "Film"

# G99 — receta nativa por look: valores de RecipeLab 1.13.1 (`Recipes.java`, voxivoid; mismas codificaciones que `Params.writes`).
# (estilo 1…14, sat, con, nitidez, modo WB (1 = AWB, 14 = K), kelvin, A-B, G-M, EV en 1/3, DRO (0 Off, 1…5 Lv, 6 Auto)).
RECIPELAB = {
    "Kodak Ektachrome E100": (7, 3, 1, 0, 1, 0, -1, 0, -1, 6), "Kodak Ektar 100": (1, 3, 1, 1, 1, 0, 0, 0, -1, 6),
    "Kodak Gold 200": (1, 2, 1, 0, 1, 0, 3, 1, 1, 6), "Kodachrome 64": (8, 3, 2, 1, 1, 0, -1, 0, -1, 6),
    "Kodak Portra 160": (4, -3, -2, 0, 1, 0, 1, -1, 2, 6), "Kodak Portra 400": (4, -1, -1, 0, 1, 0, 3, 1, 2, 6),
    "Kodak Portra 800": (4, -2, -2, 0, 1, 0, 1, 1, 1, 6), "Kodak Ultra Max 400": (1, 0, 0, 0, 1, 0, 0, 1, 1, 6),
    "Kodak Vision3 500T (daylight)": (3, -1, 0, 0, 14, 3200, 0, 0, 1, 3), "Kodak Vision 200T (Asteroid City)": (3, -2, -3, 0, 14, 5000, 2, 3, 1, 3),
    "Cinestill 50D (Blue Velvet)": (1, -2, -1, 0, 14, 5500, -1, -1, 0, 6), "Classic Cinema": (1, 0, -1, 0, 14, 6000, 2, 0, 0, 3),
    "Fuji C200": (1, 0, 0, 0, 1, 0, -1, 1, 0, 6), "Fuji Pro 400H": (9, -2, -2, 0, 1, 0, -1, 1, 2, 6),
    "Fuji Superia 400": (1, 1, 1, 0, 1, 0, 1, 1, 1, 6), "Provia": (1, 1, 0, 0, 1, 0, 0, 0, 0, 6), "Velvia": (2, 3, 2, 0, 1, 0, 0, 0, 0, 6),
    "Astia": (4, 0, -1, 0, 1, 0, 1, 0, 1, 6), "Classic Chrome": (1, -1, 2, 0, 1, 0, 3, 1, -1, 6),
    "Classic Negative": (1, -3, 3, 1, 1, 0, -1, 1, 0, 6), "Reala Ace": (1, 0, 1, 0, 1, 0, 0, 0, 0, 6),
    "Pro Neg Std": (4, -2, -1, 0, 1, 0, 0, 0, 0, 6), "Eterna": (3, -3, -2, -1, 1, 0, 0, 0, -1, 3),
    "Eterna Bleach Bypass": (3, -3, 3, 0, 1, 0, 0, 0, -1, 0),
}
# Look del catálogo → receta de RecipeLab de la misma película (o la de cine más cercana si RecipeLab no la tiene).
RECETA_DE = {
    "kodak_ektachrome_100": "Kodak Ektachrome E100", "kodak_ektar_100": "Kodak Ektar 100", "kodak_gold_200": "Kodak Gold 200",
    "kodak_kodachrome_64": "Kodachrome 64", "kodak_portra_160": "Kodak Portra 160", "kodak_portra_400": "Kodak Portra 400",
    "kodak_portra_800": "Kodak Portra 800", "kodak_portra_800_push1": "Kodak Portra 800", "kodak_portra_800_push2": "Kodak Portra 800",
    "kodak_ultramax_400": "Kodak Ultra Max 400", "kodak_verita_200d": "Classic Cinema", "kodak_vision3_200t": "Kodak Vision 200T (Asteroid City)",
    "kodak_vision3_250d": "Classic Cinema", "kodak_vision3_500t": "Kodak Vision3 500T (daylight)", "kodak_vision3_50d": "Cinestill 50D (Blue Velvet)",
    "fujifilm_c200": "Fuji C200", "fujifilm_pro_400h": "Fuji Pro 400H", "fujifilm_provia_100f": "Provia", "fujifilm_velvia_100": "Velvia",
    "fujifilm_xtra_400": "Fuji Superia 400", "fujifilm_eterna_250": "Eterna", "fujifilm_eterna_250d": "Eterna", "fujifilm_eterna_400": "Eterna",
    "fujifilm_eterna_500": "Eterna", "fujifilm_eterna_vivid_160": "Classic Cinema", "fujifilm_eterna_vivid_250d": "Classic Cinema",
    "fujifilm_eterna_vivid_500": "Classic Cinema", "fujifilm_f64d": "Classic Cinema", "fujifilm_reala_500d": "Reala Ace",
    "fuji_sim_astia": "Astia", "fuji_sim_classic_chrome": "Classic Chrome", "fuji_sim_classic_neg": "Classic Negative", "fuji_sim_eterna": "Eterna",
    "fuji_sim_eterna_bleach_bypass": "Eterna Bleach Bypass", "fuji_sim_pro_neg": "Pro Neg Std", "fuji_sim_provia": "Provia",
    "fuji_sim_reala_ace": "Reala Ace", "fuji_sim_velvia": "Velvia",
}
# Ids de Backup que toca una receta (RecipeLab `Params.ROW_ID` + ranuras dobles de `writes`): estilo, sat, con, nitidez, modo WB, kelvin, A-B (+AWB, +K),
# G-M (+AWB, +K), EV (+copia), DRO (+nivel). El hilo guarda su valor al salir de Off y lo devuelve al volver a Off.
REC_ID = (0x1070175, 0x1070187, 0x1070178, 0x107018A, 0x1070019, 0x1070018, 0x1070017, 0x107067F, 0x1070683,
          0x1070016, 0x107067E, 0x1070682, 0x10700B8, 0x1070C7F, 0x1070104, 0x1070775)
NO_TOCA = 999
OFF_REC = 0x1800                                 # blob: [OFF_REC] = 1 si hay ajustes del usuario guardados, después un byte por REC_ID


def receta_bytes(nombre: str) -> list[int]:
    """Valor de cada REC_ID para una receta (codificación de `Params.writes`; NO_TOCA = no se escribe)."""
    est, sat, con, nit, wb, k, ab, gm, ev, dro = RECIPELAB[nombre]
    kel = wb == 14
    dro_main = 0 if dro == 0 else 1 if dro == 6 else dro + 1
    return [est, sat, con, nit, wb, k // 100 if kel else NO_TOCA, ab, NO_TOCA if kel else ab, ab if kel else NO_TOCA,
            -gm, NO_TOCA if kel else -gm, -gm if kel else NO_TOCA, ev, ev, dro_main, dro + 1 if 1 <= dro <= 5 else 1]


def orden() -> list[str]:
    """Ids del catálogo en el orden de los números de look (1…N)."""
    return [i for _, looks in FILAS for i, _ in looks]


def ajustes() -> list[cfw.Ajuste]:
    """Una fila del menú = un ajuste CFW de 1 B (ids libres de g56; el ACK usa el siguiente)."""
    assert len(FILAS) <= 8
    return [cfw.Ajuste(f"film{k + 1}", et, cfw.ID_LIBRES[k], (("Off", 0),) + tuple((n, j + 1) for j, (_, n) in enumerate(looks)), cfw.PID_PRIMERO + k)
            for k, (et, looks) in enumerate(FILAS)]


def ajuste_todas() -> cfw.Ajuste:
    """G100: lista única Off + los 38 (no entra en las páginas del menú, cuyo tope es 7; va al menú Fn, cuya franja horizontal desplaza). Id libre 9 de g56."""
    return cfw.Ajuste("film_todas", CARPETA, cfw.ID_LIBRES[9], (("Off", 0),) + tuple((n, k) for k, n in enumerate((n for _, looks in FILAS for _, n in looks), 1)),
                      cfw.PID_PRIMERO + len(FILAS))


def bases() -> list[int]:
    b, out = 0, []
    for _, looks in FILAS:
        out.append(b)
        b += len(looks)
    return out


def datos_h(npz: Path) -> str:
    """Cabecera C con las tablas (21 bits, orden lógico como el blob de G89) y las curvas en el orden de `orden()`."""
    import avcam_dinamico as D
    import cube_a6000 as C
    z = np.load(npz)
    pos = {str(i): k for k, i in enumerate(z["ids"])}
    img = C.BIN.read_bytes()
    perm = list(struct.unpack_from("<405H", img, D.PERM - D.BASE))
    ids = orden()
    faltan = [i for i in ids if i not in pos]
    assert not faltan, faltan
    luts = [D.empaqueta_21(C.empaqueta_hw(z["q"][pos[i]], img), perm) for i in ids]
    curvas = [z["T"][pos[i]].astype("<u2") for i in ids]
    usa = [int(str(z["curva"][pos[i]]) != "sin_T") for i in ids]
    hx = lambda b: ",".join(f"0x{x:02x}" for x in b)
    a = [*ajustes(), ajuste_todas()]                # la lista única va la última: base 0, Off + 38
    return "\n".join([
        f"#define NLOOKS {len(ids)}", f"#define NFILAS {len(a)}", f"#define ACK_ID {ACK_ID:#x}u",
        "static const u32 FILA_ID[NFILAS] = {" + ",".join(f"{x.backup:#x}u" for x in a) + "};",
        "static const i32 FILA_BASE[NFILAS] = {" + ",".join(map(str, [*bases(), 0])) + "};",
        "static const i32 FILA_N[NFILAS] = {" + ",".join(str(len(x.opciones)) for x in a) + "};",
        "static const u8 LOOK_USA_T[NLOOKS] = {" + ",".join(map(str, usa)) + "};",
        f"#define NREC {len(REC_ID)}", f"#define NO_TOCA {NO_TOCA}", f"#define OFF_REC {OFF_REC:#x}",
        "static const u32 REC_ID[NREC] = {" + ",".join(f"{x:#x}u" for x in REC_ID) + "};",
        "static const i16 RECETA[NLOOKS][NREC] = {" + ",".join("{" + ",".join(map(str, receta_bytes(RECETA_DE[i]))) + "}" for i in ids) + "};",
        "static const u8 LOOK_LUT[NLOOKS][1064] = {" + ",".join("{" + hx(t) + "}" for t in luts) + "};",
        "static const u16 LOOK_T[NLOOKS][1024] = {" + ",".join("{" + ",".join(map(str, c.tolist())) + "}" for c in curvas) + "};", ""])


def compila(npz: Path) -> tuple[bytes, dict[str, int]]:
    """C + datos → (binario plano Thumb independiente de posición, {símbolo: desplazamiento})."""
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "films_datos.h").write_text(datos_h(npz))
        o, e, b = f"{d}/f.o", f"{d}/f.elf", f"{d}/f.bin"
        subprocess.run(["clang", "--target=thumbv7a-none-eabi", "-mthumb", "-mfloat-abi=soft", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fropi",
                        "-fno-exceptions", "-fno-asynchronous-unwind-tables", "-nostdlib", "-Wall", "-Wextra", "-Werror", "-I", d, "-c", str(SRC), "-o", o], check=True)
        subprocess.run(["ld.lld", "-m", "armelf", "--omagic", f"-Ttext={BASE_COMPILADO:#x}", f"--entry={BASE_COMPILADO:#x}", "-o", e, o], check=True)
        subprocess.run(["llvm-objcopy", "-O", "binary", e, b], check=True)
        nm = subprocess.run(["llvm-nm", e], check=True, capture_output=True, text=True).stdout
        sim = {p[2]: int(p[0], 16) - BASE_COMPILADO for p in (ln.split() for ln in nm.splitlines()) if len(p) == 3 and p[1] in "TtRr"}
        return Path(b).read_bytes(), sim


def patch_vu2(vu2: bytes, compilado: tuple[bytes, dict[str, int]]) -> bytes:
    import lut_sd_vu2
    return lut_sd_vu2.patch(vu2, compilado, entrada="films_hilo")


def blob_esperado(look: int, npz: Path, guardado: bytes | None = None) -> bytes:
    """Blob que debe dejar el hilo para el look `look` (0 = Off); `guardado` = ajustes del usuario guardados (por defecto ceros si hay look)."""
    import avcam_dinamico as D
    import cube_a6000 as C
    b = bytearray(BK_TAM)
    struct.pack_into("<I", b, 0, MAGIC)
    b[4], b[5], b[6], b[10] = 1, look, len(orden()), look
    if look or guardado is not None:
        b[OFF_REC] = 1
        b[OFF_REC + 1:OFF_REC + 1 + len(REC_ID)] = guardado or bytes(len(REC_ID))
    if look:
        z = np.load(npz)
        k = [str(i) for i in z["ids"]].index(orden()[look - 1])
        img = C.BIN.read_bytes()
        b[16:16 + TAM_TABLA] = D.empaqueta_21(C.empaqueta_hw(z["q"][k], img), list(struct.unpack_from("<405H", img, D.PERM - D.BASE)))
        b[8] = 1
        if str(z["curva"][k]) != "sin_T":
            b[OFF_T:OFF_T + 2048] = z["T"][k].astype("<u2").tobytes()
            b[9] = 1
    return bytes(b)


# ---------- emulación (Unicorn) ----------
@dataclass
class Backup:
    ids: dict = field(default_factory=dict)       # id → bytes
    escrituras: list = field(default_factory=list)
    pierde: int = 0                               # nº de escrituras del blob que se pierden (Backup que aún no las ha asentado)

    def lee(self, i: int) -> bytes:
        return self.ids.get(i, bytes(BK_TAM if i == BK_ID else 8))


def emula(bk: Backup, compilado, pasos: list, entrada: str = "films_hilo", max_instr: int = 2_000_000_000) -> Backup:
    """Ejecuta el hilo: `pasos` = un evento por cada `usleep` (callable(bk) o None); al agotarse se detiene."""
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP
    blob, sim = compilado
    code, stubs, heap, stack = 0x10000000, 0x20000000, 0x30000000, 0x40000000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for a, s in ((code, (len(blob) + 0xFFFF) & ~0xFFFF), (stubs, 0x1000), (heap, 0x100000), (stack, 0x20000)):
        mu.mem_map(a, s)
    mu.mem_write(code, blob)
    nombres = ["dlsym", "dlopen", "malloc", "usleep", "Backup_read", "Backup_write"]
    dir_ = {n: stubs + 0x10 * i for i, n in enumerate(nombres)}
    inv = {a: n for n, a in dir_.items()}
    brk = [heap]
    pasos = list(pasos)

    def cstr(a):
        out = bytearray()
        while (c := mu.mem_read(a + len(out), 1)[0]):
            out.append(c)
        return out.decode()

    def hook(mu, addr, size, _):
        n = inv.get(addr)
        if n is None:
            return
        r = lambda k: mu.reg_read(UC_ARM_REG_R0 + k)
        ret = 0
        if n == "dlsym":
            ret = dir_.get(cstr(r(1)), -1) | 1 if cstr(r(1)) in dir_ else 0
        elif n == "dlopen":
            ret = 1 if cstr(r(0)) == "libbackup.so" else 0
        elif n == "malloc":
            ret, brk[0] = brk[0], brk[0] + ((r(0) + 15) & ~15)
        elif n == "usleep":
            if not pasos:
                mu.emu_stop()
            elif (ev := pasos.pop(0)):
                ev(bk)
        elif n == "Backup_read":
            d = bk.lee(r(0))
            mu.mem_write(r(1), d)
        elif n == "Backup_write":
            i = r(1)
            assert r(0) == i >> 16
            bk.escrituras.append(i)
            if i == BK_ID and bk.pierde > 0:
                bk.pierde -= 1
            else:
                bk.ids[i] = bytes(mu.mem_read(r(2), BK_TAM if i == BK_ID else 8))
        mu.reg_write(UC_ARM_REG_R0, ret & 0xFFFFFFFF)
        mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR) | 1)

    mu.hook_add(UC_HOOK_CODE, hook, begin=stubs, end=stubs + 0x100)
    mu.reg_write(UC_ARM_REG_SP, stack + 0x20000 - 16)
    mu.reg_write(UC_ARM_REG_LR, stubs + 0xF00)
    mu.reg_write(UC_ARM_REG_R0, dir_["dlsym"] | 1)
    mu.emu_start((code + sim[entrada]) | 1, stubs + 0xF00, count=max_instr)
    return bk
