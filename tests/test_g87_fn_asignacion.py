"""G86-B — «LUT» elegible en las 12 ranuras Fn (listas de CautionConfig + tabla opción→valor de viewUnified2), mapeo opción→valor→nodo y build del CFW de objetivos (offline)."""
from __future__ import annotations

import contextlib
import re
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/lut"), str(ROOT / "tests")]
import add_menu_entry as A
import build_fn_lut
import fn_lut_menu as F
import test_g86_fn_lut as T
import uxc_strings

LIB, DEV_A, DEV_B = T.LIB, T.DEV_A, T.DEV_B
needs = T.needs
TABLA_1 = [1, 2, 0xA, 5, 6, 0xC, 3, 4, 7, 8, 9, 0x12, 0xB, 0xF, 0xD, 0x10, 0xE, 0x13, 0x16, 0x15, 0x14, 0x17, 0x18, 0x19, 0x2A, 0x2B, 0x2D, 0x2F, 0x20, 0x21, 0x22, 0x2C, 0x2E, 0x25, 0x29, 0, 0x11]
TABLA_N = [0x11, *TABLA_1[:-1]]
ID_LUT = {1: 0x24, **{n: 0 for n in range(2, 13)}}      # 0xf de la opción LUT por ranura = id de ShootMode (no está en la lista del A6000); su valor guardado pasa de 0x11 a 0x26


class Lib:
    """Lectura mínima de un ELF .so: símbolos, relocaciones y palabras por VA."""

    def __init__(self, d: bytes):
        self.d, self.segs = d, A._segments(d)
        _, dyn = A._dynamic(d, self.segs)
        self.t = {a: b for a, b in dyn if a}
        ro = A._off(self.segs, self.t[0x11])
        self.rel = {}
        for i in range(0, self.t[0x12], 8):
            o, inf = struct.unpack_from("<II", d, ro + i)
            self.rel[o] = inf
        sym, st = A._off(self.segs, self.t[6]), A._off(self.segs, self.t[5])
        self.sym = {}
        for i in range((st - sym) // 16):
            no, v, sz = struct.unpack_from("<III", d, sym + 16 * i)
            self.sym[d[st + no:d.index(b"\0", st + no)].decode()] = (i, v, sz)
        self.names = {i: n for n, (i, _, _) in self.sym.items()}

    def u(self, va, n=1):
        return struct.unpack_from(f"<{n}I", self.d, A._off(self.segs, va))

    def lista(self, n: int):
        """(entradas, cuenta) de `cmnViewSettingNodesCustomFunction{n}Type08` tal como la ve el cargador: GOT → matriz."""
        i, _, _ = self.sym[f"cmnViewSettingNodesCustomFunction{n}Type08"]
        got = [o for o, inf in self.rel.items() if inf >> 8 == i and inf & 0xFF == 21]
        if got:                                              # sin parchear: GLOB_DAT contra el símbolo
            arr = self.sym[f"cmnViewSettingNodesCustomFunction{n}Type08"][1]
        else:                                                # parcheado: RELATIVE sobre la palabra del GOT
            got = [o for o, inf in self.rel.items() if inf == 23 and self._gotword(o, n)]
            assert len(got) == 1, got
            arr = self.u(got[0])[0]
        cnt = self.u(self.sym[f"cmnViewSettingNodesNumOfCustomFunction{n}Type08"][1])[0]
        out = []
        for k in range(cnt):
            inf = self.rel.get(arr + 4 * k)
            out.append(("sym", self.names[inf >> 8]) if inf and inf & 0xFF == 2 else ("rel", self.u(arr + 4 * k)[0]))
        return out, cnt

    def _gotword(self, o, n):
        # GOT de CautionConfig: la entrada que antes era GLOB_DAT del símbolo; se reconoce porque su offset coincide con el original
        return o == ORIG_GOT[n]


ORIG_GOT: dict[int, int] = {}


@contextlib.contextmanager
def _spec_intacta():
    """La spec global del menú (`pp_menu_spec`, `build_pp_menu`) se reescribe en el sitio al configurar: se restaura entera, incluida la lista de páginas de TREE."""
    import build_pp_menu
    import pp_menu_spec as M
    snap = (dict(M.SETTINGS), list(M.PIDS), list(M.TREE[2]), list(build_pp_menu.EXTRA_TREES), list(build_pp_menu.FN_TREES), build_pp_menu.configurar, M.TREE)
    try:
        yield
    finally:
        M.SETTINGS.clear()
        M.SETTINGS.update(snap[0])
        M.PIDS[:] = snap[1]
        M.TREE = snap[6]
        M.TREE[2][:] = snap[2]
        build_pp_menu.EXTRA_TREES[:] = snap[3]
        build_pp_menu.FN_TREES[:] = snap[4]
        build_pp_menu.configurar = snap[5]



@pytest.fixture(scope="module")
def orig_lib():
    lib = Lib((LIB / "CautionConfig.so").read_bytes())
    for n in range(1, 13):
        i = lib.sym[f"cmnViewSettingNodesCustomFunction{n}Type08"][0]
        ORIG_GOT[n] = next(o for o, inf in lib.rel.items() if inf >> 8 == i and inf & 0xFF == 21)
    return lib


@pytest.fixture(scope="module")
def construido(tmp_path_factory):
    d = tmp_path_factory.mktemp("fnlut87")
    with _spec_intacta():
        build_fn_lut.main(DEV_A, DEV_B, d)
    return d


@needs
def test_las_12_listas_type08_tienen_la_opcion_lut_antes_de_notset(construido, orig_lib):
    nuevo = Lib((construido / "lib/CautionConfig.so").read_bytes())
    en = uxc_strings.parse((construido / "share/app/string_english.uxc").read_bytes())[2]
    for n in range(1, 13):
        antes, c0 = orig_lib.lista(n)
        despues, c1 = nuevo.lista(n)
        assert c0 == 26 and c1 == 27 and len(despues) == 27
        assert despues[:25] == antes[:25] and despues[26] == antes[25] and antes[25][1].endswith("NotSet")
        kind, nodo = despues[25]
        assert kind == "rel"
        _, _, nk, props = nuevo.u(nodo, 4)
        assert nk == 0
        lst, ntri = nuevo.u(props, 2)
        tri = {a: (b, c) for a, b, c in (nuevo.u(lst + 12 * i, 3) for i in range(ntri))}
        assert (tri[0xB][1], tri[0xC][1], tri[0xF][1], tri[0x10][1]) == (0, 2, ID_LUT[n], ID_LUT[n])
        assert en[tri[0][1] & 0xFFFF] == "LUT" and en[tri[6][1] & 0xFFFF] != "LUT"          # nombre y ayuda
        assert nuevo.u(nodo)[0] == nuevo.sym["_ZTV18CmnViewSettingNode"][1] + 8


@needs
def test_el_resto_de_listas_y_cuentas_no_cambian(construido, orig_lib):
    nuevo = Lib((construido / "lib/CautionConfig.so").read_bytes())
    for n in range(1, 13):
        for t in ("Default", "Type01", "Type02", "Type03", "Type04", "Type05", "Type06", "Type07"):
            for pre in ("cmnViewSettingNodesCustomFunction", "cmnViewSettingNodesNumOfCustomFunction"):
                nm = f"{pre}{n}{t}"
                _, v0, sz = orig_lib.sym[nm]
                assert nuevo.sym[nm][1:] == (v0, sz)
                assert nuevo.u(v0, sz // 4) == orig_lib.u(v0, sz // 4)


@needs
def test_tablas_opcion_valor_de_vu2_asignan_0x26_a_shootmode(construido):
    orig = (LIB / "viewUnified2.so").read_bytes()
    nuevo = (construido / "lib/viewUnified2.so").read_bytes()
    pat = lambda t: b"".join(struct.pack("<I", x) for x in t)
    assert (orig.count(pat(TABLA_N)), orig.count(pat(TABLA_1))) == (11, 1)
    assert (nuevo.count(pat(TABLA_N)), nuevo.count(pat(TABLA_1))) == (0, 0)
    assert (nuevo.count(pat([F.VALOR_LUT, *TABLA_N[1:]])), nuevo.count(pat([*TABLA_1[:-1], F.VALOR_LUT]))) == (11, 1)


@needs
def test_valor_guardado_de_la_opcion_lut_llega_al_hijo_39(construido):
    """Cadena completa por ranura: id 0xf del nodo LUT → entrada de la tabla de vu2 (ranura 1: tabla propia con ids directos; 2…12: ids +1) → valor 0x26 → despachador de vu4 → SRNum 0x27."""
    vu2 = (construido / "lib/viewUnified2.so").read_bytes()
    vu4 = (construido / "lib/viewUnified4.so").read_bytes()
    caution = Lib((construido / "lib/CautionConfig.so").read_bytes())
    pat = lambda t: b"".join(struct.pack("<I", x) for x in t)
    t1 = struct.unpack_from("<37I", vu2, vu2.index(pat([*TABLA_1[:-1], F.VALOR_LUT])))
    tn = struct.unpack_from("<37I", vu2, vu2.index(pat([F.VALOR_LUT, *TABLA_N[1:]])))
    for n in range(1, 13):
        nodo = caution.lista(n)[0][25][1]
        o = caution.u(caution.u(nodo + 12)[0], 2)[0]                     # props → lista de tripletas
        tri = {a: v for a, _, v in (caution.u(o + 12 * i, 3) for i in range(6))}
        valor = (t1 if n == 1 else tn)[tri[0xF]]
        assert valor == F.VALOR_LUT and T._srnum(vu4, valor) == F.SRNUM_LUT == 0x27


@needs
def test_mapeo_opcion_valor_nodo_coincide_por_nombre_en_todas_las_opciones():
    """FN-LUT-4: valor guardado = tabla[0xf] (ranura 1: ids directos; 2…12: ids +1); el hijo de la raíz Fn al que lleva ese valor se llama como la opción (las 36 que existen en vu4)."""
    vu4 = (LIB / "viewUnified4.so").read_bytes()
    cau = Lib((LIB / "CautionConfig.so").read_bytes())
    vl = Lib(vu4)
    kids = [vl.names[vl.rel[F.TABLA_VA + 4 * i] >> 8].replace("cmnViewSettingNodeRoot", "") for i in range(38)]
    esperado = {"ExposureComp": "ExposureCompensation", "SmileFaceDetect": "FaceDetect_SmileShutter", "PortraitFraming": "PortraitIFraming", "ImageSize": "StillImageSize",
                "AspectRatio": "StlImageAspectRatio", "Quality": "StlImageQuality", "RecordingMedia": "MemoryCardRecordingMedia", "SteadyShot": "StillSteadyShot",
                "AudioRecordingLevel": "MovieAudioRecordingLevel", "GridLine": "CustomGridLine", "PeakingLevel": "CustomPeakingLevel", "PeakingColor": "CustomPeakingColor",
                "SteadyShotonly": "SteadyShot", "AudioRecordingLevelDisplay": "MovieAudioRecordingLevelDisplay", "SoftSkinEffect": "SoftSkin", "DROAutoHDR": "DRO_Auto_HDR",
                "FlashCompensation": "FlashComp", "ISO": "ISOSensitivity", "MemoryRecall": "MemoryRecallFn", "ShootMode": "ShootingMode"}
    comprobadas = 0
    for n, tabla in ((1, TABLA_1), (2, TABLA_N), (12, TABLA_N)):
        _, base, tam = cau.sym[f"cmnViewSettingNodesCustomFunction{n}Default"]
        for k in range(tam // 4):
            suf = re.sub(r"^cmnViewSettingNodeCustomFunction\d+(CustomFunction\d+)?", "", cau.names[cau.rel[base + 4 * k] >> 8])
            pl = cau.sym[f"cmnViewSettingPropertyListFnFunctionCustomFunction{n}{suf}"]
            v = cau.u(pl[1], pl[2] // 4)
            idopt = next(v[3 * j + 2] for j in range(pl[2] // 12) if v[3 * j] == 0xF)
            if suf == "NotSet":
                continue
            sr = T._srnum(vu4, tabla[idopt])
            if sr is None or not 1 <= sr <= 38:
                continue                                                 # valores con bloque condicional (Subexposuremodes, FocusArea): se omiten
            assert kids[sr - 1] == esperado.get(suf, suf), (n, suf, idopt, hex(tabla[idopt]), sr)
            comprobadas += 1
    assert comprobadas >= 3 * 30, comprobadas


def test_build_cfw_objetivos_encadena_la_opcion_lut_en_fn():
    import build_cfw_objetivos as O
    import build_pp_menu
    with _spec_intacta():
        O._configurar_con_cfw()
        assert build_pp_menu.FN_TREES == ["lut"]


@needs
def test_build_files_del_cfw_objetivos_incluye_vu4_parcheado(tmp_path, orig_lib):
    """Solo el paquete de ficheros de /usr (sin nflasha15 ni paquete): el manifiesto lleva viewUnified4.so, CautionConfig y viewUnified2 con la opción LUT."""
    import json

    import build_cfw_objetivos as O
    import build_pp_menu
    with _spec_intacta():
        O._cuevas_fuera_del_bloque_0()
        build_pp_menu.configurar = O._configurar_con_cfw
        files = O.C.build_files(tmp_path)
        O.aplicar_objetivos(files)
    man = json.loads((files / "MANIFEST.json").read_text())
    assert "lib/viewUnified4.so" in man["parcheados"]
    assert man["parcheados"]["lib/viewUnified4.so"] != man["originales"]["lib/viewUnified4.so"]
    vu4 = (files / "lib/viewUnified4.so").read_bytes()
    assert T._srnum(vu4, F.VALOR_LUT) == F.SRNUM_LUT
    assert Lib((files / "lib/CautionConfig.so").read_bytes()).lista(1)[1] == 27
