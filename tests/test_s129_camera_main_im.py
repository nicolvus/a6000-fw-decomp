"""Tests de S129 — `[CAMERA_MAIN_IM]` en la fw3.21 de la A6000 (bytes reales).

Todo se recalcula desde `av-cam.bin` (vaddr = 0x43541000 + offset): las cadenas en su
dirección, los sitios de la regla PIC estricta, los prólogos de las 10 funciones, la tabla
del despachador y las relaciones con S115/S124.
"""

import json
import pathlib
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[CAMERA_MAIN_IM]: "
HERE = ROOT / "analysis" / "s129_camera_main_im"


def _bytes(path):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def data():
    return _bytes(BIN)


@pytest.fixture(scope="module")
def inv():
    with open(HERE / "camera_main_im.json", encoding="utf-8") as fh:
        return json.load(fh)


@pytest.fixture(scope="module")
def pic():
    with open(ROOT / "analysis" / "s106_imaging_cap" / "pic_refs_strict_global.json",
              encoding="utf-8") as fh:
        return json.load(fh)


def u16(d, v):
    return struct.unpack_from("<H", d, v - BASE)[0]


def u32(d, v):
    return struct.unpack_from("<I", d, v - BASE)[0]


def cstr(d, v):
    o = v - BASE
    e = d.index(b"\x00", o)
    return d[o:e]


def bl_target(d, v):
    """Destino de un `bl` Thumb-2 en `v` (None si no lo es)."""
    h1, h2 = u16(d, v), u16(d, v + 2)
    if (h1 & 0xF800) != 0xF000 or (h2 & 0xD000) != 0xD000:
        return None
    s = ((h1 & 0x7FF) << 12) | ((h2 & 0x7FF) << 1)
    if s & 0x400000:
        s -= 0x800000
    return (v + 4 + s) & 0xFFFFFFFF


def find_strings(d):
    out, start = [], 0
    while True:
        i = d.find(PREFIX, start)
        if i < 0:
            return out
        e = d.index(b"\x00", i)
        out.append((BASE + i, d[i:e].decode("latin1")))
        start = i + 1


def add_pc(d, site):
    """(registro, destino) si `site` es un `add rX, pc` de 16 bits."""
    h = u16(d, site)
    if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
        return None
    return (((h >> 7) & 1) << 3) | (h & 7), site


def prev_ldr(d, site, reg, gap=0x1000):
    """`ldr` (16 o 32 bits) más cercano por detrás para `reg`; devuelve su literal."""
    for a in range(site - 2, max(site - gap, 0), -2):
        if a < BASE:
            break
        h = u16(d, a)
        if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == (reg & 7):
            return ((a + 4) & ~3) + (h & 0xFF) * 4
        if (h & 0xFF7F) == 0xF85F:
            h2 = u16(d, a + 2)
            if ((h2 >> 12) & 0xF) == (reg & 0xF):
                return ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
    return None


def push_lr_offset(d, entry, span=12):
    """Offset del primer `push {...lr}` en [entry, entry+span), o None."""
    for k in range(0, span, 2):
        h = u16(d, entry + k)
        if (h & 0xFF00) == 0xB500 and (h & 0x100):
            return k
        if h == 0xE92D and (u16(d, entry + k + 2) & 0x4000):
            return k
    return None


class TestCadenas:
    def test_42_cadenas_con_prefijo(self, data, inv):
        found = find_strings(data)
        assert len(found) == 42
        assert inv["counts"]["strings"] == 42
        # 40 del bloque + 2 sueltas de ZitDdcDriver
        assert len([v for v, _ in found if 0x43CA6B32 <= v <= 0x43CA71E7]) == 40
        assert {v for v, _ in found} & {0x43CB5FC1, 0x43CB5FFA} == {0x43CB5FC1, 0x43CB5FFA}

    def test_cada_vaddr_contiene_su_texto(self, data, inv):
        for s in inv["strings"]:
            v = int(s["vaddr"], 16)
            assert cstr(data, v).decode("latin1") == s["text"], hex(v)
            assert s["text"].startswith("[CAMERA_MAIN_IM]: ")

    def test_inventario_sin_duplicados_salvo_la_doble_referencia(self, inv):
        vaddrs = [s["vaddr"] for s in inv["strings"]]
        assert len(vaddrs) == 43 and len(set(vaddrs)) == 42
        assert [v for v in vaddrs if vaddrs.count(v) > 1] == ["0x43ca70f6", "0x43ca70f6"]

    def test_no_hay_prefijo_en_a7s_ni_a6300(self):
        for path in (A7S, A6300):
            d = _bytes(path)
            assert d.find(b"[CAMERA_MAIN_IM]") < 0, path


class TestSitiosPic:
    def test_43_sitios_estrictos(self, inv, pic):
        total = 0
        for s in {x["vaddr"] for x in inv["strings"]}:
            total += len(pic.get(s, []))
        assert total == 43
        assert inv["counts"]["sites"] == 43
        assert inv["counts"]["unreferenced"] == 0

    def test_cada_sitio_es_add_pc_y_apunta_a_su_cadena(self, data, inv, pic):
        for v in {x["vaddr"] for x in inv["strings"]}:
            for site in pic[v]:
                got = add_pc(data, site)
                assert got is not None, hex(site)
                reg, _ = got
                lit = prev_ldr(data, site, reg)
                assert lit is not None, hex(site)
                assert (u32(data, lit) + site + 4) & 0xFFFFFFFF == int(v, 16), hex(site)

    def test_doble_referencia_de_imstartmovthermal(self, inv, pic):
        sites = pic["0x43ca70f6"]
        assert sites == [0x437B90FE, 0x437B9268]
        usados = [int(s["site"], 16) for s in inv["strings"] if s["vaddr"] == "0x43ca70f6"]
        assert sorted(usados) == sites


class TestFunciones:
    def test_diez_entradas_y_sus_sitios(self, inv):
        fns = {f["entry"]: f for f in inv["functions"]}
        assert len(fns) == 10
        assert {k: f["n_sites"] for k, f in fns.items()} == {
            "0x43547362": 3, "0x437b8774": 22, "0x437b8e1c": 1, "0x437b8ed4": 3,
            "0x437b8fb0": 3, "0x437b9064": 3, "0x437b915c": 2, "0x437b91e8": 3,
            "0x437b93c0": 1, "0x4386bbec": 2,
        }
        assert sum(f["n_sites"] for f in fns.values()) == 43

    def test_atribucion_por_entrada_mas_cercana(self, inv):
        entradas = sorted(int(f["entry"], 16) for f in inv["functions"])
        for f in inv["functions"]:
            for site in map(lambda x: int(x, 16), f["sites"]):
                cerca = max(e for e in entradas if e <= site)
                assert cerca == int(f["entry"], 16), hex(site)

    def test_prologos_reales(self, data, inv):
        # 6 funciones llevan preámbulo (ldr/contexto) antes del push: entrada real.
        con_preambulo = {"0x437b8ed4", "0x437b8fb0", "0x437b9064",
                         "0x437b915c", "0x437b91e8", "0x4386bbec"}
        for f in inv["functions"]:
            off = push_lr_offset(data, int(f["entry"], 16))
            assert off is not None, f["entry"]
            if f["entry"] in con_preambulo:
                assert off > 0, f["entry"]

    def test_chequeo_termico_no_tiene_llamadas_ni_punteros(self, data):
        # 0x437b8774: 22 sitios pero 0 bl y 0 punteros de 32 bits en toda la imagen.
        assert not [a for a in range(BASE, BASE + len(data) - 4, 2)
                    if bl_target(data, a) == 0x437B8774]
        ptrs = [a for a in range(0, len(data) - 3, 4)
                if struct.unpack_from("<I", data, a)[0] in (0x437B8774, 0x437B8775)]
        assert ptrs == []


class TestDespachador:
    def test_id_de_16_bits_y_tabla_de_24(self, data, inv):
        assert u16(data, 0x437B8390) & 0xF800 == 0x8800        # ldrh r6,[r3,#0x10]
        assert ((u16(data, 0x437B8390) >> 6) & 0x1F) * 2 == 0x10
        assert u16(data, 0x437B83AA) & 0xF800 == 0x2800        # cmp r2,#0x18
        assert u16(data, 0x437B83AA) & 0xFF == 0x18
        w = u32(data, 0x437B8478)                              # pool del ldr de 0x437b8392
        assert w + 0x437B8398 == 0x43BEFC32
        assert inv["dispatch"]["table"] == "0x43befc32"

    def test_los_24_pares_id_codigo(self, data, inv):
        ent = inv["dispatch"]["entries"]
        assert len(ent) == 24 and inv["dispatch"]["n_entries"] == 24
        for i, e in enumerate(ent):
            ident, code = struct.unpack_from("<HH", data, 0x43BEFC32 - BASE + 4 * i)
            assert ident == int(e["id"], 16), i
            assert code == int(e["code"], 16), i
            assert code == ident & 0xFF, i                       # código = byte bajo del id

    def test_defecto_y_despacho(self, data, inv):
        assert u16(data, 0x437B8404) == 0xF44F                 # mov.w r3,#0xa00
        assert u16(data, 0x437B8406) == 0x6320
        assert (u16(data, 0x437B8454), u16(data, 0x437B8456)) == (0xF5B2, 0x6F2C)
        # ^ cmp.w r2,#0xac0 (capstone); el inmediato va repartido en el par
        assert bl_target(data, 0x437B843E) == 0x437B9064
        assert bl_target(data, 0x437B8444) == 0x437B915C
        assert bl_target(data, 0x437B844C) == 0x437B8E1C
        assert inv["dispatch"]["function"] == "0x437b8384"


class TestRelaciones:
    def test_temperatura_del_imager_s115(self, data, inv):
        assert bl_target(data, 0x437B877A) == 0x436D6118
        assert bl_target(data, 0x437B8780) == 0x436D648C
        assert u16(data, 0x437B8796) == 0xED9D                 # vldr s14,[sp,#0x34]
        assert u32(data, 0x437B8A0C) == 0x42C80000             # 100.0f
        assert inv["relation_s115"]["vtable_slot"] == "0x6c"
        assert inv["relation_s115"]["imager_ctx_getter"] == "0x436d6118"

    def test_campos_de_modo_y_estructura_s124(self, data, inv):
        for site, imm in ((0x437B87F6, 6), (0x437B87FE, 4)):
            h = u16(data, site)
            assert h & 0xF800 == 0x7800, hex(site)             # ldrb
            assert (h >> 6) & 0x1F == imm, hex(site)
            assert (h >> 3) & 7 == 4, hex(site)                # [r4,#imm]
        r = inv["relation_s124"]
        assert r["thermal_reads"] == ["0x437b87f6 ldrb r3,[r4,#6]",
                                      "0x437b87fe ldrb r5,[r4,#4]"]
        assert r["same_struct"] == "NO VERIFICADO"

    def test_intervalos_de_100ms(self, data):
        for site, pool in ((0x437B8F3E, 0x437B8F78), (0x437B90E0, 0x437B9118),
                           (0x437B9248, 0x437B92B4)):
            assert u16(data, site) & 0xF800 == 0x4800, hex(site)
            lit = ((site + 4) & ~3) + (u16(data, site) & 0xFF) * 4
            assert lit == pool
            assert u32(data, pool) == 0x186A0, hex(site)       # campo u16 x 100000

    def test_logger_y_predicado(self, data, inv):
        assert u16(data, 0x437B85AC) == 0xB408                 # push {r3}
        assert u16(data, 0x437B8494) == 0x7B1B                 # ldrb r3,[r3,#0xc]
        assert u16(data, 0x437B8496) == 0x4218                 # tst r0,r3
        assert inv["support"]["logger_private"] == "0x437b85ac"


class TestNegativos:
    def test_sin_campos_del_obturador(self, inv):
        textos = [s["text"] for s in inv["strings"]]
        for token in ("svd", "shd", "spl", "sint", "gs:", "epdsel"):
            assert not [t for t in textos if token in t], token
        shut = [t for t in textos if "shut" in t]
        assert len(shut) == 2 and all("shutdownTh" in t for t in shut)

    def test_diferencial_34_y_33(self, inv, data):
        d = json.loads((HERE / "diff.json").read_text(encoding="utf-8"))
        assert d["a6000_strings"] == 42
        assert d["a7s_interior_exact"] == 34 and d["a6300_interior_exact"] == 33
        assert inv["diff"]["a7s_interior_exact"] == 34
        assert inv["diff"]["a6300_interior_exact"] == 33
        # recuento recalculado desde los textos interiores del inventario
        inner = {s["interior"] for s in inv["strings"]}
        for path, n in ((A7S, 34), (A6300, 33)):
            pool = {x.decode("latin1") for x in _bytes(path).split(b"\x00") if len(x) > 3}
            assert len(inner & pool) == n, path

    def test_fichero_fuente_no_thermal(self, data):
        assert data.find(b"Thermal.cpp") < 0
        for cpp in (b"CS_imaging.cpp", b"SyncYCOut.cpp", b"lc_PreReadAF.cpp"):
            assert data.find(cpp) > 0, cpp
