#!/usr/bin/env python3
"""G97 — userland de las simulaciones de película (`userland/films.c`): datos, menú, compilación, inyección en `viewUnified2.so` y emulación.

`FILAS` define el menú «Film Simulation»: una fila por marca (Kodak, Fujifilm, Fujifilm Sim) con Off + todos sus looks, numerados en ese orden (1…38).
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

# (etiqueta de la fila, ((id del catálogo, nombre en el menú), …)): una fila por marca con todos sus estilos (G102: la lista vertical no tiene tope de 7,
# medido en el arnés; antes «Kodak 1/2/3»…). Numeración de los looks = este orden (1…38).
FILAS = (
    ("Kodak", (("kodak_ektachrome_100", "Ektachrome"), ("kodak_ektar_100", "Ektar 100"), ("kodak_gold_200", "Gold 200"),
               ("kodak_kodachrome_64", "Kodachrome"), ("kodak_portra_160", "Portra 160"), ("kodak_portra_400", "Portra 400"),
               ("kodak_portra_800", "Portra 800"), ("kodak_portra_800_push1", "Portra800 +1"), ("kodak_portra_800_push2", "Portra800 +2"),
               ("kodak_ultramax_400", "Ultramax 400"), ("kodak_verita_200d", "Verita 200D"), ("kodak_vision3_200t", "Vision3 200T"),
               ("kodak_vision3_250d", "Vision3 250D"), ("kodak_vision3_500t", "Vision3 500T"), ("kodak_vision3_50d", "Vision3 50D"))),
    ("Fujifilm", (("fujifilm_c200", "C200"), ("fujifilm_pro_400h", "Pro 400H"), ("fujifilm_provia_100f", "Provia 100F"),
                  ("fujifilm_velvia_100", "Velvia 100"), ("fujifilm_xtra_400", "X-Tra 400"), ("fujifilm_eterna_250", "Eterna 250"),
                  ("fujifilm_eterna_250d", "Eterna 250D"), ("fujifilm_eterna_400", "Eterna 400"), ("fujifilm_eterna_500", "Eterna 500"),
                  ("fujifilm_eterna_vivid_160", "Eterna V160"), ("fujifilm_eterna_vivid_250d", "Eterna V250D"), ("fujifilm_eterna_vivid_500", "Eterna V500"),
                  ("fujifilm_f64d", "F-64D"), ("fujifilm_reala_500d", "Reala 500D"))),
    ("Fujifilm Sim", (("fuji_sim_astia", "Astia"), ("fuji_sim_classic_chrome", "Classic Chr."), ("fuji_sim_classic_neg", "Classic Neg"),
                      ("fuji_sim_eterna", "Eterna"), ("fuji_sim_eterna_bleach_bypass", "Eterna BB"), ("fuji_sim_pro_neg", "Pro Neg"),
                      ("fuji_sim_provia", "Provia"), ("fuji_sim_reala_ace", "Reala Ace"), ("fuji_sim_velvia", "Velvia"))),
)
CARPETA = "Film Simulation"

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
OFF_REC = 0x1800                                 # blob: copia de los ajustes del usuario (`struct copia` de films.c), la escribe la GUI
COPIA_TAM = 44
# G110: WRAPPER_* de vu2 (verificado en sus tablas): balance 1 = AWB, 0xc = temperatura de color; DRO 0 Off, 1 Auto, k + 1 = nivel k.
WB_AWB, WB_KELVIN, K_AWB = 1, 0xC, 5500


def receta_gui(nombre: str) -> list[int]:
    """Receta de RecipeLab en los parámetros de los setters de la GUI: modo WB, K, A-B, G-M, código de estilo, contraste, saturación, nitidez, DRO.
    (EV no: es de la exposición, queda libre.)"""
    est, sat, con, nit, wb, k, ab, gm, _ev, dro = RECIPELAB[nombre]
    kel = wb == 14
    return [WB_KELVIN if kel else WB_AWB, k if kel else K_AWB, ab, gm, est, con, sat, nit, 0 if dro == 0 else 1 if dro == 6 else dro + 1]


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


def datos_h(npz: Path, pids: dict | None = None, pp_pids: tuple[int, int, int] = (0, 1, 0)) -> str:
    """Cabecera C con las tablas (21 bits, orden lógico como el blob de G89) y las curvas en el orden de `orden()`.
    `pids` = {id de ajuste: ProcessId real de la build} (por defecto el de `ajustes()`); `pp_pids` = (pid del selector PP, primer pid PP, último pid PP), 0 sin PP."""
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
    pids = pids or {x.id: x.pid for x in a}
    return "\n".join([
        f"#define NLOOKS {len(ids)}", f"#define NFILAS {len(a)}", f"#define ACK_ID {ACK_ID:#x}u",
        "static const u32 FILA_ID[NFILAS] = {" + ",".join(f"{x.backup:#x}u" for x in a) + "};",
        "static const i32 FILA_PID[NFILAS] = {" + ",".join(str(pids[x.id]) for x in a) + "};",
        "static const i32 FILA_BASE[NFILAS] = {" + ",".join(map(str, [*bases(), 0])) + "};",
        "static const i32 FILA_N[NFILAS] = {" + ",".join(str(len(x.opciones)) for x in a) + "};",
        "static const u8 LOOK_USA_T[NLOOKS] = {" + ",".join(map(str, usa)) + "};",
        f"#define OFF_REC {OFF_REC:#x}",
        f"#define PID_PP_SEL {pp_pids[0]}", f"#define PID_PP_PRIMERO {pp_pids[1]}", f"#define PID_PP_ULTIMO {pp_pids[2]}",
        "static const i16 RECETA_GUI[NLOOKS][9] = {" + ",".join("{" + ",".join(map(str, receta_gui(RECETA_DE[i]))) + "}" for i in ids) + "};",
        "static const u8 LOOK_LUT[NLOOKS][1064] = {" + ",".join("{" + hx(t) + "}" for t in luts) + "};",
        "static const u16 LOOK_T[NLOOKS][1024] = {" + ",".join("{" + ",".join(map(str, c.tolist())) + "}" for c in curvas) + "};", ""])


# G110: funciones de viewUnified2.so (3.21) que usan los ganchos de la GUI (Thumb con bit 0; PLT ARM sin él). Verificadas en el gestor con símbolos
# `cmn_view_processDataMgr.so` (vtable de CmnViewProcessDataMgr) y en los wrappers exportados de vu2 (docs/gui/g111-film-receta-gui-iconos.md).
VU2 = {"V_GETVALUE": 0x1B475B, "V_SETVALUE": 0x1B460F, "V_SET_CONT": 0x1B4613, "V_GRIS_CONT": 0x1B469B,
       "V_WB_CTOR": 0x1BF1B1, "V_WB_GET": 0x1BF1D5, "V_WB_SET": 0x1BFB61, "V_CS_CTOR": 0x1C0C55, "V_CS_SET": 0x1C0E35,
       "V_DRO_CTOR": 0x191759, "V_DRO_GET": 0x191999, "V_DRO_CONV": 0x19177D,
       "P_DLOPEN": 0xE8D20, "P_DLSYM": 0xE72E4, "P_MALLOC": 0xE9398, "P_FREE": 0xE8204}
SITIO_SET, SITIO_GRIS = (0x1B460E, bytes.fromhex("98b500af")), (0x1B4696, bytes.fromhex("80b500af"))


def compila(npz: Path, base: int = BASE_COMPILADO, gris_sigue: int | None = None, pids: dict | None = None,
            pp_pids: tuple[int, int, int] = (0, 1, 0)) -> tuple[bytes, dict[str, int]]:
    """C + datos → (binario plano Thumb, {símbolo: desplazamiento}). Enlazado en `base` (la VA real del segmento en vu2: las llamadas a `VU2` son relativas al PC).
    `gris_sigue`: destino de `films_tramo_gris` si no decide (por defecto el prólogo original replicado en `films_orig_gris`)."""
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "films_datos.h").write_text(datos_h(npz, pids, pp_pids))
        o, e, b = f"{d}/f.o", f"{d}/f.elf", f"{d}/f.bin"
        subprocess.run(["clang", "--target=thumbv7a-none-eabi", "-mthumb", "-mfloat-abi=soft", "-Os", "-ffreestanding", "-fno-builtin", "-fno-stack-protector", "-fropi",
                        "-fno-exceptions", "-fno-asynchronous-unwind-tables", "-nostdlib", "-Wall", "-Wextra", "-Werror", "-I", d, "-c", str(SRC), "-o", o], check=True)
        sym = [f"--defsym={k}={v:#x}" for k, v in VU2.items()]
        sym.append(f"--defsym=V_GRIS_SIGUE={gris_sigue:#x}" if gris_sigue else "--defsym=V_GRIS_SIGUE=films_orig_gris")
        subprocess.run(["ld.lld", "-m", "armelf", "--omagic", f"-Ttext={base:#x}", f"--entry={base:#x}", *sym, "-o", e, o], check=True)
        subprocess.run(["llvm-objcopy", "-O", "binary", e, b], check=True)
        nm = subprocess.run(["llvm-nm", e], check=True, capture_output=True, text=True).stdout
        sim = {p[2]: int(p[0], 16) - base for p in (ln.split() for ln in nm.splitlines()) if len(p) == 3 and p[1] in "TtRr"}
        return Path(b).read_bytes(), sim


def _bw(origen: int, destino: int) -> bytes:
    import cfw_ajustes
    return cfw_ajustes.ensamblar(f"b.w #{destino:#x}", origen)


def _destino_bw(d: bytes, va: int) -> int | None:
    """Destino de un `b.w` Thumb en `va` (None si no lo es)."""
    from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
    i = next(Cs(CS_ARCH_ARM, CS_MODE_THUMB).disasm(d[va:va + 4], va), None)
    return int(i.op_str.lstrip("#"), 16) if i and i.mnemonic in ("b.w", "b") and i.size == 4 else None


def patch_vu2(vu2: bytes, npz: Path, pids: dict | None = None, pp_pids: tuple[int, int, int] = (0, 1, 0)) -> bytes:
    """Hilo por DT_INIT (G97) + G110: ganchos de setValue (receta) e isGrayedOut (grises) en el gestor de procesos de vu2."""
    import lut_sd_vu2
    va = lut_sd_vu2.va_blob(vu2)
    s_set, s_gris = SITIO_SET[0], SITIO_GRIS[0]
    assert vu2[s_set:s_set + 4] == SITIO_SET[1], "setValue de vu2 no es el esperado"
    sigue = None if vu2[s_gris:s_gris + 4] == SITIO_GRIS[1] else _destino_bw(vu2, s_gris)
    assert vu2[s_gris:s_gris + 4] == SITIO_GRIS[1] or sigue, "isGrayedOut de vu2 no es el esperado"
    blob, sim = compila(npz, va, sigue | 1 if sigue else None, pids, pp_pids)
    out = bytearray(lut_sd_vu2.patch(vu2, (blob, sim), entrada="films_hilo"))
    out[s_set:s_set + 4] = _bw(s_set, va + sim["films_tramo_set"])
    out[s_gris:s_gris + 4] = _bw(s_gris, va + sim["films_tramo_gris"])
    return bytes(out)


def blob_esperado(look: int, npz: Path, guardado: bytes | None = None) -> bytes:
    """Blob que debe dejar el hilo para el look `look` (0 = Off); `guardado` = copia del usuario que la GUI dejó en el blob (se conserva)."""
    import avcam_dinamico as D
    import cube_a6000 as C
    b = bytearray(BK_TAM)
    struct.pack_into("<I", b, 0, MAGIC)
    b[4], b[5], b[6] = 1, look, len(orden())
    if guardado is not None:
        b[OFF_REC:OFF_REC + len(guardado)] = guardado
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
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_SP,
    )
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
