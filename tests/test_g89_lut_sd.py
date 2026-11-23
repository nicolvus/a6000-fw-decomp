"""G89 (LUT-SD-1) — `.cube` leídos de la SD EN la cámara: userland ARM (C compilado, emulado con Fsys/Backup/dlsym simulados), segmento en `viewUnified2.so`,
lectura del blob de Backup en `av-cam` (bytes reales, Unicorn) y build `--sd`. Sin cámara: los contratos de Fsys_*/Backup_* son los leídos del código real (g89 §2)."""
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/lut"), str(ROOT / "scripts/gui")]
import avcam_dinamico as D
import cfw_ajustes
import cube_a6000 as C
import lut_patch as P
import lut_sd_userland as U
import lut_sd_vu2 as V
import numpy as np

DEV_A = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev"
DEV_B = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
VU2 = ROOT / "analysis/camera-extract/usr/lib/viewUnified2.so"
needs_av = pytest.mark.skipif(not C.BIN.is_file(), reason="av-cam.bin ausente")
needs_vu2 = pytest.mark.skipif(not VU2.is_file(), reason="viewUnified2.so ausente")


@pytest.fixture(scope="module")
def compilado():
    return U.compila()


def cubo(tmp_path, n, f=None):
    p = tmp_path / f"c{n}.cube"
    C.escribe_cube(p, f or C.SINT["teal_orange"], n, "t")
    return p.read_text()


def corre(compilado, cam, pasos=(None,)):
    cam.pasos = list(pasos)
    cam = U.emula(cam, *compilado)
    cam.paquetes = [p for p in cam.aperturas if p.endswith(".LUT")]           # G95: cada ranura prueba antes el `.LUT` precalculado (test_g95)
    cam.aperturas = [p for p in cam.aperturas if not p.endswith(".LUT")]
    return cam


# ---------- userland ARM ----------
@pytest.mark.parametrize("n", [17, 32, 33])
def test_arm_igual_a_la_referencia(compilado, tmp_path, n):
    txt = {1: cubo(tmp_path, n)}
    cam = corre(compilado, U.Camara({1: txt[1].encode()}))
    assert cam.backup == U.blob_esperado(txt) and cam.escrituras == 1
    assert list(cam.backup[8:14]) == [1, 0, 0, 0, 0, 0] and cam.aperturas[0] == "E:/LUT/LUT1.cube"
    assert cam.paquetes == [f"E:/LUT/LUT{s}.LUT" for s in range(1, 7)]


def test_arm_64_cubed_igual_a_la_referencia(compilado, tmp_path):
    txt = {6: cubo(tmp_path, 64, C.SINT["pelicula"])}
    cam = corre(compilado, U.Camara({6: txt[6].encode()}))
    assert cam.backup == U.blob_esperado(txt) and cam.backup[13] == 1


def test_seis_ranuras_y_no_validos(compilado, tmp_path):
    txt = {1: cubo(tmp_path, 17), 3: cubo(tmp_path, 17, C.SINT["identidad"]), 4: "LUT_3D_SIZE 4\n0 0 0\n", 5: "LUT_1D_SIZE 8\n0 0 0\n", 6: ""}
    cam = corre(compilado, U.Camara({k: v.encode() for k, v in txt.items()}))
    assert list(cam.backup[8:14]) == [1, 0, 1, 0, 0, 0]            # filas incompletas, 1D y vacío → ranura inválida (el av-cam usa el .dat/fábrica)
    assert cam.backup == U.blob_esperado(txt)
    assert len(cam.aperturas) == 6


def test_sin_tarjeta_no_escribe_y_al_insertar_barre_una_vez(compilado, tmp_path):
    txt = {1: cubo(tmp_path, 17)}
    cam = U.Camara({1: txt[1].encode()}, letra=None)
    inserta = lambda c: setattr(c, "letra", "F")
    corre(compilado, cam, [None, inserta, None, None])
    assert cam.escrituras == 1 and cam.aperturas[0] == "F:/LUT/LUT1.cube"      # la letra sale de Fsys_GetDriveLetter
    assert all(p.startswith("F:") for p in cam.aperturas) and len(cam.aperturas) == 6   # un solo barrido aunque haya varios sondeos


def test_blob_igual_no_reescribe_la_nvram(compilado, tmp_path):
    txt = {2: cubo(tmp_path, 32)}
    cam = corre(compilado, U.Camara({2: txt[2].encode()}, backup=U.blob_esperado(txt)))
    assert cam.escrituras == 0


def test_extraer_y_reinsertar_con_fichero_nuevo(compilado, tmp_path):
    a, b = cubo(tmp_path, 17), cubo(tmp_path, 17, C.SINT["pelicula"])
    cam = U.Camara({1: a.encode()})
    quita = lambda c: setattr(c, "letra", None)
    pon_b = lambda c: (setattr(c, "letra", "E"), c.ficheros.update({1: b.encode()}))
    corre(compilado, cam, [None, quita, pon_b, None])
    assert cam.escrituras == 2 and cam.backup == U.blob_esperado({1: b})


def test_formatos_numericos_y_dominio(compilado):
    t = "TITLE \"x\"\nDOMAIN_MIN -0.5 0 0\nDOMAIN_MAX 1.5 1 1\nLUT_3D_SIZE 2\n" + "".join(f"{a:.2e} {b} {c}\n" for a in (0.0, 1e-05) for b in (0, 1) for c in (0.25, 1.0))
    cam = corre(compilado, U.Camara({1: t.encode()}))
    assert U.referencia(t) is not None and cam.backup == U.blob_esperado({1: t})


def test_error_de_ΔE_frente_al_cube_exacto(compilado, tmp_path):
    """El muestreo directo en el nodo es más burdo que el ajuste por mínimos cuadrados del PC pero útil: ΔE2000 contra el .cube exacto, medido en el ARM emulado."""
    txt = cubo(tmp_path, 33)
    cam = corre(compilado, U.Camara({1: txt.encode()}))
    bits = int.from_bytes(cam.backup[16:16 + U.TAM_TABLA], "little")
    q = np.zeros((405, 3), np.int8)
    for i in range(405):
        w = bits >> (21 * i) & 0x1FFFFF
        q[i] = [((v & 127) ^ 64) - 64 for v in (w >> 14, w >> 7 & 127, w & 127)]
    p = tmp_path / "c.cube"
    p.write_text(txt)
    tab, lo, hi = C.lee_cube(p)
    x = np.random.default_rng(3).random((5000, 3))
    de = C.de2000(C.aplica_cube(tab, lo, hi, x), C.aplica_lut3d(q, x))
    print(f"ΔE2000 medio {de.mean():.2f} p95 {np.percentile(de, 95):.2f}")
    assert de.mean() < 1.5 and np.percentile(de, 95) < 5


# ---------- viewUnified2.so ----------
@needs_vu2
def test_vu2_segmento_dt_init_y_arranque_del_hilo(compilado):
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R2,
        UC_ARM_REG_R3,
        UC_ARM_REG_SP,
    )
    d = VU2.read_bytes()
    out = V.patch(d, compilado)
    segs = V.A._segments(out)
    nuevo = segs[-1]
    assert nuevo[0] == 1 and nuevo[6] == 5 and nuevo[2] > max(s[2] + s[5] for s in segs[:-1] if s[0] == 1)       # LOAD R+X nuevo, sin solaparse
    _, dyn = V.A._dynamic(out, segs)
    init = dict(dyn)[12]
    assert init == nuevo[2] | 1 and dict(V.A._dynamic(d, V.A._segments(d))[1])[12] == V.INIT_ORIG
    base_vu2 = 0x10000000
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(base_vu2, 0x600000)
    mu.mem_map(0x70000000, 0x10000)
    seg = out[nuevo[1]:nuevo[1] + 0x80]
    mu.mem_write(base_vu2 + nuevo[2], seg)
    visto = {}
    pthread = 0x70000100

    def hook(mu, a, s, _):
        rel = a - base_vu2
        if rel == V.INIT_ORIG - 1:
            visto["init"] = True
        elif rel == V.DLSYM_PLT:
            visto["dlsym_arg"] = mu.mem_read(mu.reg_read(UC_ARM_REG_R0 + 1), 15)
            mu.reg_write(UC_ARM_REG_R0, pthread | 1)
        elif a == pthread:
            visto["hilo"] = mu.reg_read(UC_ARM_REG_R2)
            visto["arg"] = mu.reg_read(UC_ARM_REG_R3)
            mu.reg_write(UC_ARM_REG_R0, 0)
        else:
            return
        mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR))
    mu.hook_add(UC_HOOK_CODE, hook)
    mu.reg_write(UC_ARM_REG_SP, 0x70008000)
    mu.reg_write(UC_ARM_REG_LR, 0x70000300 | 1)
    mu.emu_start((base_vu2 + init) | 1, 0x70000300, count=200)
    assert visto["init"] and bytes(visto["dlsym_arg"]) == b"pthread_create\0"
    assert visto["hilo"] == base_vu2 + nuevo[2] + V.STUB_TAM + compilado[1]["lutsd_hilo"] + 1       # lutsd_hilo (Thumb)
    assert visto["arg"] == base_vu2 + V.DLSYM_PLT                                                     # su argumento = dlsym@plt de la propia biblioteca
    assert out[64:0x43b964] == d[64:0x43b964]                                                          # ni un byte del segmento de código original cambia (solo la cabecera ELF y DT_INIT)


@needs_vu2
def test_vu2_se_compone_con_pid_space_sin_pisar_relocaciones(compilado):
    import pid_space
    d = pid_space.patch(VU2.read_bytes(), [])
    out = V.patch(d, compilado)
    assert len(V.A._segments(out)) == len(V.A._segments(d)) + 1
    assert dict(V.A._dynamic(out, V.A._segments(out))[1])[0x11] == dict(V.A._dynamic(d, V.A._segments(d))[1])[0x11]      # DT_REL (de pid_space) intacto


# ---------- av-cam: lectura del blob de Backup (bytes reales) ----------
def _hw_esperado(tabla21: bytes, img: bytes) -> bytes:
    perm = struct.unpack_from("<405H", img, D.PERM - D.BASE)
    bits = int.from_bytes(tabla21, "little")
    out = bytearray(0x654)
    for i in range(405):
        w = bits >> (21 * i) & 0x1FFFFF
        struct.pack_into("<I", out, 4 * perm[i], (w >> 14) << 16 | (w >> 7 & 127) << 8 | (w & 127))
    return bytes(out)


def corre_avcam(img, k, opcion, blob, orig=0x11223344, malloc_falla_en=None):
    from unicorn import UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB, Uc
    from unicorn.arm_const import (
        UC_ARM_REG_LR,
        UC_ARM_REG_PC,
        UC_ARM_REG_R0,
        UC_ARM_REG_R1,
        UC_ARM_REG_R3,
        UC_ARM_REG_R5,
        UC_ARM_REG_SP,
    )
    mu = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    mu.mem_map(P.BASE & ~0xFFF, ((len(img) + (P.BASE & 0xFFF)) + 0x200000) & ~0xFFF)
    mu.mem_write(P.BASE, img)
    stack, obj, end, heap = 0x10000000, 0x20000000, 0x30000000, 0x31000000
    for a, s in ((stack - 0x10000, 0x20000), (obj, 0x1000), (end, 0x1000), (heap, 0x100000)):
        mu.map = mu.mem_map(a, s)
    mu.mem_write(obj + 0xC4, struct.pack("<I", orig))
    est = {"brk": heap, "mallocs": [], "lecturas": []}

    def hook(mu, a, s, _):
        if a == D.MALLOC & ~1:
            n = mu.reg_read(UC_ARM_REG_R0)
            est["mallocs"].append(n)
            r = 0 if malloc_falla_en == len(est["mallocs"]) else est["brk"]
            est["brk"] += (n + 15) & ~15
            mu.reg_write(UC_ARM_REG_R0, r)
        elif a == cfw_ajustes.BACKUP_READ:
            i = mu.reg_read(UC_ARM_REG_R0)
            est["lecturas"].append(i)
            if i == P.AJ.backup:
                mu.mem_write(mu.reg_read(UC_ARM_REG_R1), bytes([opcion]))
            else:
                assert i == D.BK_ID
                mu.mem_write(mu.reg_read(UC_ARM_REG_R1), blob)
            mu.reg_write(UC_ARM_REG_R0, 0)
        else:
            return
        mu.reg_write(UC_ARM_REG_PC, mu.reg_read(UC_ARM_REG_LR) | 1)
    mu.hook_add(UC_HOOK_CODE, hook, begin=0x435613B0, end=0x435613B1)
    mu.hook_add(UC_HOOK_CODE, hook, begin=D.MALLOC & ~1, end=(D.MALLOC & ~1) + 1)
    mu.reg_write(UC_ARM_REG_SP, stack)
    mu.reg_write(UC_ARM_REG_R5, obj)
    mu.reg_write(UC_ARM_REG_LR, end | 1)
    mu.emu_start(P.entradas(True)[0] | 1, end, count=500000)
    r3 = mu.reg_read(UC_ARM_REG_R3)
    return r3, (bytes(mu.mem_read(r3, 0x654)) if r3 != orig else None), est


@needs_av
def test_avcam_usa_la_ranura_del_blob_y_cae_al_dat_o_a_fabrica(tmp_path):
    img = C.BIN.read_bytes()
    p = P.apply_bytes(img, None, True)
    txt = {1: cubo(tmp_path, 17), 4: cubo(tmp_path, 33, C.SINT["pelicula"]), 6: cubo(tmp_path, 17, C.SINT["identidad"])}
    blob = U.blob_esperado(txt)
    for k, valida in ((1, True), (2, False), (3, False), (4, True), (5, False), (6, True)):
        r, hw, _ = corre_avcam(p, k, k, blob)
        if valida:
            assert hw == _hw_esperado(blob[16 + (k - 1) * U.TAM_TABLA:16 + k * U.TAM_TABLA], p), k
        elif k <= 3:                                                                          # ranura sin fichero: la tabla del .dat (looks de fábrica del CFW)
            assert hw == _hw_esperado(p[D.LUT_TABLAS - D.BASE + (k - 1) * D.LUT_BYTES:][:D.LUT_BYTES], p), k
        else:
            assert hw is None and r == 0x11223344, k                                           # sin tabla: el puntero de fábrica


@needs_av
def test_avcam_off_blob_invalido_y_sin_memoria_no_cambian_la_ruta(tmp_path):
    img = C.BIN.read_bytes()
    p = P.apply_bytes(img, None, True)
    blob = U.blob_esperado({1: cubo(tmp_path, 17)})
    assert corre_avcam(p, 1, 0, blob)[0] == 0x11223344                                        # Off = fábrica, sin leer el Backup del blob
    assert D.BK_ID not in corre_avcam(p, 1, 0, blob)[2]["lecturas"]
    malo = bytes(U.BK_TAM)                                                                    # Backup vacío (sin SD nunca): .dat para 1…3, fábrica para 4…6
    assert corre_avcam(p, 2, 2, malo)[1] == _hw_esperado(p[D.LUT_TABLAS - D.BASE + D.LUT_BYTES:][:D.LUT_BYTES], p)
    assert corre_avcam(p, 5, 5, malo)[0] == 0x11223344
    sin_mem = corre_avcam(p, 1, 1, blob, malloc_falla_en=2)                                   # falla la reserva de 16 KB: tabla 1 del .dat
    assert sin_mem[1] == _hw_esperado(p[D.LUT_TABLAS - D.BASE:][:D.LUT_BYTES], p)
    est = corre_avcam(p, 1, 1, blob)[2]
    assert est["mallocs"] == [0x654, U.BK_TAM]                                               # una reserva de cada, ninguna por llamada posterior


@needs_av
def test_sin_modo_sd_el_parche_es_el_de_siempre():
    img = C.BIN.read_bytes()
    assert P.apply_bytes(img, None, False) == P.apply_bytes(img) and P.apply_bytes(img) != P.apply_bytes(img, None, True)


# ---------- build ----------
@pytest.mark.skipif(not (DEV_A / "nflasha15_unpacked_unpacked/lib/viewUnified4.so").is_file() or not DEV_B.is_dir(), reason="firmware de Sony ausente")
def test_build_sd_emite_userland_y_siete_opciones(tmp_path, compilado):
    import build_fn_lut
    d = build_fn_lut.main(DEV_A, DEV_B, tmp_path, sd=True)
    vu2 = (d / "lib/viewUnified2.so").read_bytes()
    segs = V.A._segments(vu2)
    assert segs[-1][0] == 1 and compilado[0][:16] in vu2                                       # el blob ARM compilado va dentro
    txt = (d / "share/app/string_english.uxc").read_bytes()
    assert all(f"LUT {i}".encode() in txt or f"LUT {i}".encode("utf-16-le") in txt for i in range(1, 7))
    assert not build_pp_menu_sd()                                                              # el flag no queda activado tras el build


def build_pp_menu_sd():
    import build_pp_menu
    return build_pp_menu.SD_USERLAND


@pytest.mark.skipif(not (DEV_A / "nflasha15_unpacked_unpacked/lib/viewUnified4.so").is_file() or not DEV_B.is_dir(), reason="firmware de Sony ausente")
def test_build_files_del_cfw_objetivos_con_sd_lut(tmp_path):
    """El CFW de objetivos con `sd_lut_cubes` lleva el userland en viewUnified2.so y 7 opciones en «LUT» (solo ficheros; no construye CFW)."""
    sys.path.insert(0, str(ROOT / "tests"))
    import build_cfw_objetivos as O
    import build_pp_menu
    from test_g87_fn_asignacion import _spec_intacta
    with _spec_intacta():
        O._cuevas_fuera_del_bloque_0()
        build_pp_menu.configurar = O._configurar_con_cfw
        P.MODO_SD = build_pp_menu.SD_USERLAND = True
        try:
            files = O.C.build_files(tmp_path)
        finally:
            P.MODO_SD = build_pp_menu.SD_USERLAND = False
    vu2 = (files / "lib/viewUnified2.so").read_bytes()
    assert V.A._segments(vu2)[-1][0] == 1 and b"pthread_create\0" in vu2
    assert b"LUT 6" in (files / "share/app/string_english.uxc").read_bytes() or "LUT 6".encode("utf-16-le") in (files / "share/app/string_english.uxc").read_bytes()
