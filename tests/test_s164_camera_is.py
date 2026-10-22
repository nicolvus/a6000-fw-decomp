"""Tests for S164 — el módulo `[CAMERA_IS]` (17 trazas) de la A6000 fw3.21.

Tests de **bytes reales**: cada comprobación decodifica el binario en la dirección exacta,
de modo que si cambia una dirección, una cadena o una instrucción, el test falla.
Referencia canónica: analysis/s164_camera_is/camera_is.md y camera_is.json.
"""

import json
import pathlib
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
REFS = "analysis/s106_imaging_cap/pic_refs_strict_global.json"

U16S = struct.Struct("<H")
U32S = struct.Struct("<I")

# Las 17 cadenas del modulo: (vaddr, texto exacto, tal y como esta en el binario)
STRINGS = [
    (0x43C98DA6, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB (%x)"),
    (0x43C98DDE, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountExpStartCB - checkData"),
    (0x43C98E1D, "[CAMERA_IS][DIST]: ERR:MakeDistCorPrm prm=null\n"),
    (0x43C98E4D, "[CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=null\n"),
    (0x43C98E80, "[CAMERA_IS][DIST]: ERR:CnvPosInvDistCorr prm=inv1 (%d, %d)\n"),
    (0x43C98EBC, "[CAMERA_IS][DIST]: WRN:CnvPosInvDistCorr prm=inv2 (%d, %d) \n"),
    (0x43C98EF9, "[CAMERA_IS][DIST]: ERR:MakeDistRawAppliTag prm=null\n"),
    (0x43C9A1F3, "[CAMERA_IS][AS]: [STABILIZER][AS][osal_reg_sync_msg_queue_cb] %x"),
    (0x43C9A234, "[CAMERA_IS][AS]: [STABILIZER][AS][upm_get_hcrn_ura] %x"),
    (0x43C9A26B, "[CAMERA_IS][AS]: [STABILIZER][AS][osal_unreg_sync_msg_queue_cb] %x"),
    (0x43C9A2B2, "[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzPower error!"),
    (0x43C9A2EB, "[CAMERA_IS][EIS]: error:0x%02x rcct_SetStblzGridH error!"),
    (0x43C9A324, "[CAMERA_IS][EIS]: GyroAD[p],GyroAD[y], %d, %d"),
    (0x43C9A352, "[CAMERA_IS][EIS]: %x, %d, %d"),
    (0x43C9A3A7, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB (%x)"),
    (0x43C9A3E3, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB - checkData"),
    (0x43C9A426, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyro (%x)"),
]

# textos interiores "distintivos" (los genericos como "%x, %d, %d" no sirven)
INNER_DISTINCTIVE = [
    b"IS_LensMountExpStartCB",
    b"IS_LensMountPanoramaGyroCB",
    b"IS_LensMountPanoramaGyro",
    b"MakeDistCorPrm",
    b"CnvPosInvDistCorr",
    b"MakeDistRawAppliTag",
    b"upm_get_hcrn_ura",
    b"osal_reg_sync_msg_queue_cb",
    b"osal_unreg_sync_msg_queue_cb",
    b"GyroAD[p],GyroAD[y]",
]

# mapa funcion -> cadenas (13 funciones emisoras)
FUNC_STRINGS = {
    0x436EA2D0: [0x43C98DA6, 0x43C98DDE],
    0x436EA470: [0x43C98E1D],
    0x436EA50C: [0x43C98E4D, 0x43C98E80, 0x43C98EBC],
    0x436EA65C: [0x43C98EF9],
    0x436FECBE: [0x43C9A1F3],
    0x436FEE80: [0x43C9A234],
    0x436FFAB4: [0x43C9A26B],
    0x43702DAC: [0x43C9A2B2, 0x43C9A2EB],
    0x437046A4: [0x43C9A324, 0x43C9A352],
    0x43704D90: [0x43C9A2B2],
    0x43705D64: [0x43C9A3A7, 0x43C9A3E3],
    0x43705DD0: [0x43C9A426],
    0x4371E4CC: [0x43C9A234],
}

# pares PIC verificados a mano: (ldr, add, cadena destino)
PIC_PAIRS = [
    (0x436EA2DC, 0x436EA2E6, 0x43C98DA6),
    (0x436EA48A, 0x436EA492, 0x43C98E1D),
    (0x436FED70, 0x436FED7A, 0x43C9A1F3),
    (0x43702DF8, 0x43702E02, 0x43C9A2B2),
    (0x43702E12, 0x43702E1C, 0x43C9A2EB),
    (0x437047F8, 0x43704802, 0x43C9A324),
    (0x43705D70, 0x43705D7A, 0x43C9A3A7),
    (0x43705DAE, 0x43705DB6, 0x43C9A3E3),
]


def _data(path=BIN):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


DATA = _data()
DATA7 = _data(A7S)
DATA6 = _data(A6300)


def _u16(addr, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - 2, f"vaddr {hex(addr)} fuera del binario"
    return U16S.unpack_from(data, off)[0]


def _u32(addr, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(addr)} fuera del binario"
    return U32S.unpack_from(data, off)[0]


def _cstr(addr, data=None, maxlen=600):
    data = DATA if data is None else data
    off = addr - BASE
    end = off
    while end < len(data) and end < off + maxlen and data[end] != 0:
        end += 1
    return data[off:end].decode("latin1")


def _pic_dest(ldr, add):
    """Resuelve un par `ldr rX,[pc,#imm]` + `add rX,pc` -> direccion destino."""
    h = _u16(ldr)
    if (h & 0xF800) == 0x4800:                       # ldr 16 bits
        lit = ((ldr + 4) & ~3) + (h & 0xFF) * 4
    else:                                            # ldr.w 32 bits
        h2 = _u16(ldr + 2)
        assert (h & 0xFF7F) == 0xF85F, f"ldr inesperado {hex(h)} en {hex(ldr)}"
        imm = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
        lit = ((ldr + 4) & ~3) + imm
    w = _u32(lit)
    return (w + (add + 4)) & 0xFFFFFFFF


# --------------------------------------------------------------------------------------
# 1) las 17 cadenas, en su direccion exacta
# --------------------------------------------------------------------------------------

def test_hay_exactamente_17_cadenas_con_el_token():
    assert DATA.count(b"[CAMERA_IS]") == 17
    assert DATA7.count(b"[CAMERA_IS]") == 0
    assert DATA6.count(b"[CAMERA_IS]") == 0


def test_las_17_cadenas_estan_en_su_direccion_exacta():
    for addr, text in STRINGS:
        assert _cstr(addr) == text, f"cadena inesperada en {hex(addr)}"


def test_los_textos_interiores_distintivos_no_existen_en_la_a7s_ni_en_la_a6300():
    for token in INNER_DISTINCTIVE:
        assert DATA.count(token) > 0, f"{token!r} deberia estar en la A6000"
        assert DATA7.count(token) == 0, f"{token!r} presente en la A7S"
        assert DATA6.count(token) == 0, f"{token!r} presente en el A6300"
    # ninguna de las 17 cadenas completas aparece en los otros dos firmwares
    for _, text in STRINGS:
        assert text.encode("latin1") not in DATA7
        assert text.encode("latin1") not in DATA6


# --------------------------------------------------------------------------------------
# 2) referencias PIC: la regla estricta y la verificacion manual
# --------------------------------------------------------------------------------------

def test_mapa_pic_estricto_referencia_las_17_cadenas():
    with open(ROOT / REFS) as fh:
        refs = json.load(fh)
    for addr, _ in STRINGS:
        key = hex(addr)
        assert key in refs, f"la cadena {hex(addr)} no tiene referencia PIC"
        assert refs[key], f"la cadena {hex(addr)} tiene una lista de sitios vacia"


def test_los_13_sitios_de_la_regla_estricta_coinciden_con_los_verificados_a_mano():
    with open(ROOT / REFS) as fh:
        refs = json.load(fh)
    esperado = {
        0x43C98DA6: [0x436EA2E6],
        0x43C98DDE: [0x436EA312],
        0x43C98E1D: [0x436EA492],
        0x43C98E4D: [0x436EA53C],
        0x43C98E80: [0x436EA576],
        0x43C98EBC: [0x436EA600],
        0x43C98EF9: [0x436EA670],
        0x43C9A1F3: [0x436FED7A, 0x436FED9C],
        0x43C9A234: [0x436FF098, 0x4371E738],
        0x43C9A26B: [0x436FFACE, 0x436FFAEC],
        0x43C9A2B2: [0x43702E02, 0x43704DB0],
        0x43C9A2EB: [0x43702E1C],
        0x43C9A324: [0x43704802],
        0x43C9A352: [0x43704C02],
        0x43C9A3A7: [0x43705D7A],
        0x43C9A3E3: [0x43705DB6],
        0x43C9A426: [0x43705E28],
    }
    for addr, sites in esperado.items():
        assert sorted(refs[hex(addr)]) == sites, f"sitios distintos para {hex(addr)}"
    assert sum(len(v) for v in esperado.values()) == 21


def test_verificacion_manual_de_los_pares_pic():
    for ldr, add, dest in PIC_PAIRS:
        assert _pic_dest(ldr, add) == dest, (
            f"el par {hex(ldr)}/{hex(add)} apunta a {hex(_pic_dest(ldr, add))}, "
            f"se esperaba {hex(dest)}")
        assert "[CAMERA_IS]" in _cstr(dest)


# --------------------------------------------------------------------------------------
# 3) las 13 funciones emisoras: prologo, traza y llamada al logger
# --------------------------------------------------------------------------------------

def test_las_13_funciones_emisoras_empiezan_con_push_lr():
    for func in FUNC_STRINGS:
        h = _u16(func)
        # push {...,lr} de 16 bits (0xB4xx/0xB5xx) o push.w de 32 bits (0xE92D)
        ok16 = (h & 0xFF00) in (0xB400, 0xB500)
        ok32 = (h & 0xFFFF) == 0xE92D
        assert ok16 or ok32, f"la funcion {hex(func)} no empieza con push: {hex(h)}"


def test_las_13_funciones_coinciden_con_el_mapa_del_informe():
    js = json.loads((ROOT / "analysis/s164_camera_is/camera_is.json").read_text())
    mapa = {f["vaddr"]: set(f["strings"]) for f in js["functions"]}
    assert len(mapa) == 13
    for func, strs in FUNC_STRINGS.items():
        assert func in mapa, f"falta la funcion {hex(func)} en camera_is.json"
        assert mapa[func] == set(strs), f"mapa distinto en {hex(func)}"


def test_cada_cadena_del_informe_tiene_una_funcion_correcta():
    js = json.loads((ROOT / "analysis/s164_camera_is/camera_is.json").read_text())
    for s in js["strings"]:
        addr = s["vaddr"]
        assert s["text"] == dict(STRINGS)[addr]
        assert s["n_refs"] >= 1
        assert set(s["functions"]) <= set(FUNC_STRINGS)


# --------------------------------------------------------------------------------------
# 4) la categoria de log por sub-capa (r1) y los envoltorios
# --------------------------------------------------------------------------------------

def test_categoria_de_log_por_subcapa():
    # r1 = valor inmediato cargado justo antes del `add rX,pc` del sitio de emision
    esperado = {
        "DIST": (1, [0x436EA492, 0x436EA53C, 0x436EA576, 0x436EA670]),
        "EIS": (2, [0x43702E02, 0x43702E1C, 0x43704802]),
        "AS": (4, [0x436FED7A, 0x436FF098, 0x436FFACE]),
        "MOUNT": (6, [0x436EA2E6, 0x43705D7A]),
    }
    for sub, (cat, sites) in esperado.items():
        for site in sites:
            # busca hacia atras el `movs r1,#cat` (0x21xx)
            found = False
            for back in range(2, 34, 2):
                h = _u16(site - back)
                if (h & 0xFF00) == 0x2100 and (h & 0xFF) == cat:
                    found = True
                    break
            assert found, f"sub-capa {sub}: no hay movs r1,#{cat} cerca de {hex(site)}"


def test_envoltorios_de_traza_por_subcapa():
    # cada sitio de emision va seguido de un `bl` a un envoltorio conocido
    envoltorios = {0x436EA224, 0x436EA3C4, 0x436FEBC4,
                   0x437026AC, 0x437041DC, 0x43705CB8, 0x4371E39C}
    js = json.loads((ROOT / "analysis/s164_camera_is/camera_is.json").read_text())
    n = 0
    for s in js["strings"]:
        for site_hex, info in s["log_wrapper"].items():
            w = info["wrapper"]
            if w is None:
                continue          # 0x43705DB6 hace cola con `b.w`, no `bl`
            assert int(w, 16) in envoltorios, f"envoltorio desconocido {w}"
            n += 1
    assert n >= 16


# --------------------------------------------------------------------------------------
# 5) lo que escribe: RC de estabilizacion, globales y fichero por lente
# --------------------------------------------------------------------------------------

def test_las_funciones_rc_de_estabilizacion_son_las_nombradas():
    # rcct_SetStblzPower: la cadena esta referenciada dentro de la funcion 0x439417c8
    assert _cstr(0x43CE190C) == "rcct_SetStblzPower"
    assert 0x439417EE in json.loads((ROOT / REFS).read_text())[hex(0x43CE190C)]
    # rcct_SetStblzGridH
    assert _cstr(0x43CE186A) == "rcct_SetStblzGridH"
    assert 0x4394183A in json.loads((ROOT / REFS).read_text())[hex(0x43CE186A)]
    # el modulo llama a esas dos funciones
    assert _bl_target(0x43702DF2) == 0x439417C8
    assert _bl_target(0x43702E0C) == 0x43941814
    assert _bl_target(0x43704DA0) == 0x439417C8


def test_el_fichero_is_por_lente_y_su_contador():
    assert _cstr(0x43C9A535) == "/mnt/FILE_IS_%04x.dat"
    assert _cstr(0x43C9A54B).startswith("\nCh.0/00,01,02,03,04,05,06,07,Ch.1/00")
    # el contador u16 global esta en 0x43f65d3c (verificado a mano con el par PIC)
    assert _pic_dest(0x43707166, 0x4370716A) == 0x43F65D3C
    # el mismo fichero existe en la A7S y en el A6300
    assert b"/mnt/FILE_IS_%04x.dat" in DATA7
    assert b"/mnt/FILE_IS_%04x.dat" in DATA6


def test_los_globales_de_la_capa_dist():
    # 0x43f61884 / 0x43f61886: centro y coeficiente de correccion de distorsion
    assert _pic_dest(0x436EA4C6, 0x436EA4CC) == 0x43F61884
    assert _pic_dest(0x436EA58A, 0x436EA58C) == 0x43F61884


def test_el_servicio_de_la_montura_se_llama_lens_mount():
    assert _cstr(0x43C9A39C) == "LENS_MOUNT"
    assert _cstr(0x43C9A58E) == "LENS_MOUNT"
    assert _pic_dest(0x43707278, 0x4370727A) == 0x43C9A58E


# --------------------------------------------------------------------------------------
# 6) diferencial y negativo verificado para la linea del obturador
# --------------------------------------------------------------------------------------

def test_diferencial_con_la_a7s_y_el_a6300():
    for token in (b"GyroAD", b"IS_LensMountExpStartCB", b"IS_LensMountPanoramaGyro",
                  b"MakeDistCorPrm", b"CnvPosInvDistCorr", b"MakeDistRawAppliTag",
                  b"upm_get_hcrn_ura", b"[STABILIZER]"):
        assert DATA.count(token) > 0, f"{token!r} deberia estar en la A6000"
        assert DATA7.count(token) == 0, f"{token!r} no deberia estar en la A7S"
        assert DATA6.count(token) == 0, f"{token!r} no deberia estar en el A6300"
    # la infraestructura RC si es comun a los tres
    for token in (b"rcct_SetStblzPower", b"rcct_SetStblzGridH",
                  b"WrapRcctSetStblzPower.cpp", b"EIS_RC1V_SetPower", b"LENS_MOUNT"):
        assert DATA.count(token) > 0
        assert DATA7.count(token) > 0
        assert DATA6.count(token) > 0


def test_negativo_verificado_para_la_linea_del_obturador():
    # ninguna de las 17 trazas menciona obturador / lectura / rolling
    for _, text in STRINGS:
        bajo = text.lower()
        for palabra in ("shut", "silen", "rolling", "readout", "read out"):
            assert palabra not in bajo, f"{text!r} menciona {palabra!r}"
    # y en toda la imagen de la A6000 fw3.21 no hay ni "rolling" ni "readout"
    assert DATA.count(b"rolling") == 0
    assert DATA.count(b"readout") == 0
    assert DATA7.count(b"rolling") == 0
    assert DATA7.count(b"readout") == 0
    # el A6300 si tiene el concepto de rolling shutter (fuera de [CAMERA_IS])
    assert DATA6.count(b"position num in rolling is strange %d") == 1


def test_el_api_de_tiempo_de_estabilizacion_solo_existe_en_el_a6300():
    assert b"GetImagerStabilizationTime" not in DATA
    assert b"GetImagerStabilizationTime" not in DATA7
    assert DATA6.count(b"GetImagerStabilizationTime") == 1


def _bl_target(addr):
    """Devuelve el destino de un `bl` de 32 bits (Thumb)."""
    h = _u16(addr)
    h2 = _u16(addr + 2)
    assert (h & 0xF800) == 0xF000 and (h2 & 0xD000) == 0xD000, "no es un bl de 32 bits"
    s = (h >> 10) & 1
    imm10 = h & 0x3FF
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    imm11 = h2 & 0x7FF
    i1 = (~(j1 ^ s)) & 1
    i2 = (~(j2 ^ s)) & 1
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        imm -= (1 << 25)
    return (addr + 4 + imm) & 0xFFFFFFFF
