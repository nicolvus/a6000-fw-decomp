"""Tests de S144 — el módulo `[CAM_UTIL_SENS]` (21 trazas) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware, **recalculan** el mapa de
referencias PIC de forma independiente (regla estricta canónica del repo,
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`) y comprueban direcciones, textos,
llamantes, punteros absolutos, ids OSAL y el negativo de obturador/iris/ISO.
Si cambia una dirección, un texto, un enlace o un recuento, el test falla.
"""

import bisect
import json
import pathlib
import re
import struct

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
JSON_PATH = "analysis/s144_cam_util_sens/cam_util_sens.json"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = b"[CAM_UTIL_SENS]"

# --- las 21 cadenas con su dirección exacta y su texto exacto ----------------
CADENAS = {
    0x43CCE1EA: "[CAM_UTIL_SENS]: CB for BKID change [BKID]:%x [Size]:%x",
    0x43CCE222: "[CAM_UTIL_SENS]:                    [SWFLG]:%x",
    0x43CCE251: "[CAM_UTIL_SENS]:                    [MODEFLG]:%x",
    0x43CCE322: "[CAM_UTIL_SENS]:   Debug IM ASync Open start",
    0x43CCE34F: "[CAM_UTIL_SENS]: [FileNum]%04x [Adr]%x [Size]%x",
    0x43CCE37F: "[CAM_UTIL_SENS]: [Flg]%04x [MountSTAT]%04x [FsysMode]%04x",
    0x43CCE3B9: "[CAM_UTIL_SENS]:   Debug IM ASync Open OSAL MEM ALLOC Error : %x",
    0x43CCE3FA: "[CAM_UTIL_SENS]: >>[FILE_NUM]%x [ADR]%x [SIZE]%x",
    0x43CCE42B: "[CAM_UTIL_SENS]: >>[STAT]%x [FSYSMODE]",
    0x43CCE452: "[CAM_UTIL_SENS]:   Debug IM ASync Open end [ErrInfo]%x [Flg]%x",
    0x43CCE491: "[CAM_UTIL_SENS]:   Debug IM Sync Open start",
    0x43CCE4BD: "[CAM_UTIL_SENS]:  Debug IM Sync Open OSAL MEM ALLOC Error : %x",
    0x43CCE4FC: "[CAM_UTIL_SENS]:   >> [SndMsgErrInfo]%x",
    0x43CCE524: "[CAM_UTIL_SENS]:   >> [RcvMsgErr]%x",
    0x43CCE548: "[CAM_UTIL_SENS]:   >> Recieve UnKnown Msg [CID]%x",
    0x43CCE57A: "[CAM_UTIL_SENS]:   Debug IM Sync Open end[Flg]%x",
    0x43CCE5AB: "[CAM_UTIL_SENS]: SET FILE NUM Func",
    0x43CCE5CE: "[CAM_UTIL_SENS]: [FileNum]%02x [Adr]%x [Size]%x",
    0x43CCE5FE: "[CAM_UTIL_SENS]:   SET FILE NUM Func OSAL MEM ALLOC Error : %x",
    0x43CCE63D: "[CAM_UTIL_SENS]: UTIL MS Mgr) Call CB [Flg]%x",
    0x43CCE66B: "[CAM_UTIL_SENS]: UTIL MS Mgr) ## CALL BACK NULL Error!!! ##[Flg]%x",
}

# --- sitio de referencia (add rX,pc) por cadena ------------------------------
SITIOS = {
    0x43CCE1EA: [0x4390130E],
    0x43CCE222: [0x43901326],
    0x43CCE251: [0x4390133A],
    0x43CCE322: [0x43901D7C],
    0x43CCE34F: [0x43901D90, 0x43901F18],
    0x43CCE37F: [0x43901DB0, 0x43901F36, 0x439021C0],
    0x43CCE3B9: [0x43901E06],
    0x43CCE3FA: [0x43901E48, 0x43902030, 0x43902264, 0x43902498],
    0x43CCE42B: [0x43901E6A, 0x4390204E, 0x43902286, 0x439024C6],
    0x43CCE452: [0x43901ECA],
    0x43CCE491: [0x43901F04],
    0x43CCE4BD: [0x43901F8C, 0x43902450],
    0x43CCE4FC: [0x43902094, 0x439022C6, 0x4390250C],
    0x43CCE524: [0x439020B6, 0x439022E8, 0x4390252E],
    0x43CCE548: [0x439020E0, 0x43902312, 0x43902558],
    0x43CCE57A: [0x43902118, 0x4390234A, 0x43902590],
    0x43CCE5AB: [0x43902180],
    0x43CCE5CE: [0x43902198],
    0x43CCE5FE: [0x4390220E],
    0x43CCE63D: [0x439023D8],
    0x43CCE66B: [0x439023F0],
}

# --- funciones del modulo y su reparto de sitios -----------------------------
FUNCIONES = {
    0x439012D0: ("CB for BKID change", 3),
    0x43901D50: ("Debug IM ASync Open", 17),
    0x43902168: ("SET FILE NUM Func", 10),
    0x439023B8: ("UTIL MS Mgr) Call CB", 2),
    0x43902418: ("Debug IM Sync Open", 7),
}

# --- llamantes verificados (bl) de cada funcion ------------------------------
LLAMANTES = {
    0x439012D0: [],
    0x43901D50: [0x4376BF92, 0x43783136, 0x437EE214, 0x4387375C, 0x43873B5C,
                 0x43873B96, 0x43873BEC, 0x43873C0C, 0x43873C3A, 0x4387883C,
                 0x4387888A, 0x438B834A, 0x439F7BDA, 0x439F7C7C, 0x439F7D4E,
                 0x439F7E34, 0x43B723B8],
    0x43902168: [0x43782644, 0x43782650, 0x43782904, 0x4382CEA2],
    0x439023B8: [0x43900C9C],
    0x43902418: [0x437894DC],
}

# --- puntero absoluto del callback de BKID ----------------------------------
CB_BKID_PTR = 0x44022D84
CB_BKID_VALUE = 0x439012D1        # Thumb: 0x439012d0 | 1

# --- ids OSAL compartidos con [CAM_UTIL_ADJ] --------------------------------
OSAL_LOG_ID = 0x008F0139
OSAL_CMD_ID = 0x008F013A
OSAL_LOG_POOLS = [0x439007AC, 0x439011D4, 0x43901C00]     # ADJ + 2 copias SENS
OSAL_CMD_POOLS = [0x439009BC, 0x43901C94]                 # ADJ + SENS

# --- globales verificados del modulo ----------------------------------------
GLOBALES = {
    0x43901CD2: 0x43F062C8,     # bloque de parametros / plantilla de 12 B
    0x43900FFA: 0x43FA29F0,     # byte 'MountSTAT'/'STAT'
    0x43901D7E: 0x43FA2D23,     # byte 'Flg'
    0x439023BE: 0x43FA2D23,     # el mismo byte 'Flg' (lo pone a 0 'UTIL MS Mgr) Call CB')
    0x439023C4: 0x43F062D4,     # puntero al callback del gestor MS
    0x43901D5E: 0x4401EEE4,     # tabla de objetos global
    0x439012E4: 0x4401EEE4,     # idem (CB de BKID)
}

# --- texto de las trazas de los llamantes (atribucion de modulo) ------------
CADENAS_LLAMANTES = {
    0x43C9D45C: "[CAMERA_MAIN_LC]: MS_Writer: disable addr! memmapID: %d",
    0x43C9F2DD: "[IMAGING_CAP]: MemAreaMSDebug) Exec MS Dump: filename FILE%04x, addr 0x%08x, size 0x%08x",
    0x43C9EECE: "[IMAGING_CAP]: <SACC_Debug> Capture_MemOpen() error",
    0x43C9F336: "[IMAGING_CAP]: ## Error : cam_util_debug_file_write(%d) %s : %d",
    0x43CC56AF: "[CAMERA_MAIN_YC]: [Error] WiriteMsDebug = %x",
}

# --- vocabulario prohibido (obturador / iris / ISO) -------------------------
PROHIBIDO = ("shut", "shutter", "iris", "aperture", "iso", "exposure", "silent",
             "elec", "efcs", "fps", "frame")

# --------------------------------------------------------------- utilidades
_DATA_CACHE = {}
_PIC_CACHE = {}


def _data(path=BIN_PATH):
    if path not in _DATA_CACHE:
        with open(ROOT / path, "rb") as fh:
            _DATA_CACHE[path] = fh.read()
    return _DATA_CACHE[path]


def _json():
    with open(ROOT / JSON_PATH) as fh:
        return json.load(fh)


def _u16(data, vaddr):
    off = vaddr - BASE_VADDR
    assert 0 <= off <= len(data) - 2, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack("<H", data[off:off + 2])[0]


def _u32(data, vaddr):
    off = vaddr - BASE_VADDR
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(vaddr)} fuera del binario"
    return struct.unpack("<I", data[off:off + 4])[0]


def _cstr(data, vaddr, maxlen=300):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _strings_with(data, token=TOKEN):
    """[(vaddr_token, vaddr_cadena, texto)] de cada token."""
    out = []
    start = 0
    while True:
        i = data.find(token, start)
        if i < 0:
            break
        s = i
        while s > 0 and 32 <= data[s - 1] < 127:
            s -= 1
        out.append((BASE_VADDR + i, BASE_VADDR + s, _cstr(data, BASE_VADDR + s)))
        start = i + 1
    return out


def _pic_index(data):
    """{destino: [sitios `add rX,pc`]} de toda la imagen (recálculo independiente).

    Regla **estricta** (canónica del repo): cada `add rX,pc` se empareja con el
    `ldr rX,[pc,#imm]` más cercano por detrás, ventana de 4 KB.
    """
    key = id(data)
    if key in _PIC_CACHE:
        return _PIC_CACHE[key]
    n = len(data)
    ldrs = []
    for a in range(BASE_VADDR, BASE_VADDR + n - 8, 2):
        o = a - BASE_VADDR
        h = struct.unpack("<H", data[o:o + 2])[0]
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack("<H", data[o + 2:o + 4])[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        else:
            continue
        o2 = lit - BASE_VADDR
        if 0 <= o2 <= n - 4:
            ldrs.append((a, reg, struct.unpack("<I", data[o2:o2 + 4])[0]))
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    keys = {}
    for reg, v in by_reg.items():
        v.sort()
        keys[reg] = [x[0] for x in v]
    out = {}
    for a in range(BASE_VADDR, BASE_VADDR + n - 4, 2):
        h = struct.unpack("<H", data[a - BASE_VADDR:a - BASE_VADDR + 2])[0]
        if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        out.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    _PIC_CACHE[key] = out
    return out


def _bl_target(data, site):
    """Destino de un `bl` (16 o 32 bits) en `site`; None si no es un `bl`."""
    h1 = _u16(data, site)
    if (h1 & 0xF800) == 0xE000:                    # BL de 16 bits
        imm = h1 & 0x7FF
        if imm & 0x400:
            imm -= 0x800
        return (site + 4 + (imm << 1)) & 0xFFFFFFFF
    if (h1 & 0xF800) == 0xF000:                    # Thumb-2
        h2 = _u16(data, site + 2)
        S = (h1 >> 10) & 1
        if (h2 & 0xC000) == 0xC000 and (h2 & 0x1000):
            imm10 = h1 & 0x3FF
            J1 = (h2 >> 13) & 1
            J2 = (h2 >> 11) & 1
            imm11 = h2 & 0x7FF
            I1 = 1 - (J1 ^ S)
            I2 = 1 - (J2 ^ S)
            imm = ((S << 24) | (I1 << 23) | (I2 << 22) | (imm10 << 12) | (imm11 << 1))
            if imm & (1 << 24):
                imm -= 1 << 25
            return (site + 4 + imm) & 0xFFFFFFFF
    return None


# ------------------------------------------------------------------- tests
def test_hay_exactamente_21_cadenas_con_esas_direcciones():
    data = _data()
    got = {va: txt for _, va, txt in _strings_with(data)}
    assert got == CADENAS


def test_el_bloque_de_texto_del_modulo_solo_tiene_un_hueco():
    """Entre las 21 cadenas solo se intercalan 3 cadenas `[CAM_UTIL]` conocidas."""
    data = _data()
    intercaladas = [
        (0x43CCE282, "[CAM_UTIL]: EvtDrvnTsk) Send Err tid:%d->%d, func:%08x, arg:%x, %x"),
        (0x43CCE2C5, "[CAM_UTIL]: EvtDrvnTsk) Send Err Print Max..."),
        (0x43CCE2F3, "[CAM_UTIL]: Task tid:%d, func:%08x, arg:%x, %x"),
    ]
    for va, txt in intercaladas:
        assert _cstr(data, va) == txt, hex(va)
    addrs = sorted(CADENAS)
    huecos = []
    for a, b in zip(addrs, addrs[1:]):
        off_a = a - BASE_VADDR + len(CADENAS[a])
        off_b = b - BASE_VADDR
        hueco = data[off_a:off_b]
        if hueco != b"\x00":
            huecos.append((a, b, off_a, off_b))
    # exactamente un hueco: el de las 3 cadenas [CAM_UTIL]
    assert len(huecos) == 1, huecos
    a, b, off_a, off_b = huecos[0]
    assert (a, b) == (0x43CCE251, 0x43CCE322)
    assert off_a + 1 == 0x43CCE282 - BASE_VADDR   # off_a es el NUL terminador
    assert off_b == 0x43CCE322 - BASE_VADDR
    # y las tres cadenas intercaladas caben exactamente en el hueco
    fin = intercaladas[-1][0] - BASE_VADDR + len(intercaladas[-1][1]) + 1
    assert fin == off_b


def test_recalculo_pic_estricto_coincide_con_los_sitios_publicados():
    data = _data()
    pic = _pic_index(data)
    for cadena, sitios in SITIOS.items():
        assert sorted(pic.get(cadena, [])) == sorted(sitios), cadena


def test_aritmetica_pic_a_mano_de_un_sitio_por_cadena():
    """destino = pool + (direccion_del_add + 4), re-hecho byte a byte."""
    data = _data()
    for cadena, sitios in SITIOS.items():
        for site in sitios:
            add_h = _u16(data, site)
            assert (add_h & 0xFF00) == 0x4400 and ((add_h >> 3) & 0xF) == 15, hex(site)
            reg = (((add_h >> 7) & 1) << 3) | (add_h & 7)
            # ldr del mismo registro mas cercano por detras (ventana 4 KB)
            ldr = None
            for a in range(site - 2, site - 4098, -2):
                h = _u16(data, a)
                if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
                    ldr = a
                    break
            assert ldr is not None, hex(site)
            lh = _u16(data, ldr)
            lit = ((ldr + 4) & ~3) + ((lh & 0xFF) * 4)
            pool = _u32(data, lit)
            assert (pool + site + 4) & 0xFFFFFFFF == cadena, (hex(site), hex(cadena))


def test_los_sitios_caen_en_las_5_funciones_publicadas():
    data = _data()
    json_doc = _json()
    publicado = {f["func"]: f["n_sitios"] for f in json_doc["funciones"]}
    assert publicado == {hex(k): v[1] for k, v in FUNCIONES.items()}
    # los sitios deben estar dentro del rango [func, func_fin] del JSON
    for f in json_doc["funciones"]:
        lo = int(f["func"], 16)
        hi = int(f["vaddr_fin_estimado"], 16)
        for t in f["trazas"]:
            assert lo <= int(t["site"], 16) < hi, t


def test_38_sitios_de_referencia_en_total():
    data = _data()
    total = sum(len(v) for v in SITIOS.values())
    assert total == 39
    assert len(CADENAS) == 21


def test_llamantes_bl_de_las_5_funciones():
    data = _data()
    for func, sitios in LLAMANTES.items():
        for site in sitios:
            assert _bl_target(data, site) == func, (hex(site), hex(func))


def test_el_cb_de_bkid_no_se_llama_directamente_pero_se_registra():
    data = _data()
    assert _u32(data, CB_BKID_PTR) == CB_BKID_VALUE
    # y no hay ningun `bl` a 0x439012d0 en toda la imagen
    n = len(data)
    for a in range(BASE_VADDR, BASE_VADDR + n - 4, 2):
        h = struct.unpack("<H", data[a - BASE_VADDR:a - BASE_VADDR + 2])[0]
        if (h & 0xF800) == 0xE000 or ((h & 0xF800) == 0xF000 and (h & 0x0800)):
            tgt = _bl_target(data, a)
            assert tgt != 0x439012D0, hex(a)


def test_tsk_cam_adjctrl_llama_a_util_ms_mgr_call_cb():
    """El puente ADJ -> SENS: 0x43900c9c -> 0x439023b8."""
    data = _data()
    assert _bl_target(data, 0x43900C9C) == 0x439023B8


def test_el_cb_de_bkid_monta_y_desmonta_el_servicio_ms():
    """0x439012fa -> 0x43900e30 (Mount) y 0x43901302 -> 0x43900f18 (UnMount)."""
    data = _data()
    assert _bl_target(data, 0x439012FA) == 0x43900E30
    assert _bl_target(data, 0x43901302) == 0x43900F18


def test_ids_osal_compartidos_con_cam_util_adj():
    data = _data()
    for pool in OSAL_LOG_POOLS:
        assert _u32(data, pool) == OSAL_LOG_ID, hex(pool)
    for pool in OSAL_CMD_POOLS:
        assert _u32(data, pool) == OSAL_CMD_ID, hex(pool)


def test_id_de_modulo_0xb5_en_las_trazas_de_los_dos_hermanos():
    """`movs r0,#0xb5` en los dos log de ADJ y de SENS."""
    data = _data()
    for site in (0x43900A8C, 0x43901D82, 0x439023D0):
        h = _u16(data, site)
        assert (h & 0xF800) == 0x2000 and (h & 0xFF) == 0xB5, hex(site)


def test_globales_del_modulo():
    data = _data()
    for add, base in GLOBALES.items():
        h = _u16(data, add)
        assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(add)
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        ldr = None
        for a in range(add - 2, add - 4098, -2):
            lh = _u16(data, a)
            if (lh & 0xF800) == 0x4800 and ((lh >> 8) & 7) == reg:
                ldr = a
                break
        assert ldr is not None, hex(add)
        lh = _u16(data, ldr)
        lit = ((ldr + 4) & ~3) + ((lh & 0xFF) * 4)
        pool = _u32(data, lit)
        assert (pool + add + 4) & 0xFFFFFFFF == base, (hex(add), hex(base))


def test_prologos_de_las_5_funciones():
    """Cada funcion empieza por un push de registros (Thumb)."""
    data = _data()
    for func in FUNCIONES:
        h = _u16(data, func)
        h2 = _u16(data, func + 2)
        if h == 0xE92D:                       # push.w
            assert h2 & 0x4000, hex(func)     # bit 14 -> incluye LR
        else:
            assert (h & 0xFF00) == 0xB500, hex(func)


def test_diferencial_el_token_no_existe_en_a7s_ni_en_a6300():
    assert _data(A7S_BIN).count(TOKEN) == 0
    assert _data(A6300_BIN).count(TOKEN) == 0
    assert _data().count(TOKEN) == 21


def test_diferencial_los_interiores_no_existen_en_los_otros_firmwares():
    a7s = set(m.group()[:-1].decode("latin1")
              for m in re.finditer(rb"[ -~]{4,300}\x00", _data(A7S_BIN)))
    a6300 = set(m.group()[:-1].decode("latin1")
                for m in re.finditer(rb"[ -~]{4,300}\x00", _data(A6300_BIN)))
    for va, txt in CADENAS.items():
        interior = txt.replace("[CAM_UTIL_SENS]:", "").strip()
        assert interior not in a7s, va
        assert interior not in a6300, va


def test_diferencial_la_funcionalidad_si_existe_en_los_otros_dos():
    """`cam_util_debug_file_write` y `MemAreaMSDebug` estan en los tres."""
    for path, n_min in ((BIN_PATH, 3), (A7S_BIN, 2), (A6300_BIN, 2)):
        d = _data(path)
        assert d.count(b"cam_util_debug_file_write") == n_min, path
        assert d.count(b"MemAreaMSDebug") >= 4, path


def test_negativo_el_modulo_no_habla_de_obturador_iris_ni_iso():
    data = _data()
    for va, txt in CADENAS.items():
        low = txt.lower()
        for word in PROHIBIDO:
            assert word not in low, (hex(va), word)


def test_negativo_tampoco_en_las_cadenas_de_la_banda_del_modulo():
    """Cadenas referenciadas por el codigo de 0x43901000-0x43902610 (47 destinos)."""
    data = _data()
    j = _json()
    banda = j["cadenas_referenciadas_en_banda"]
    assert len(banda) == 47
    textos = {b["text"] for b in banda}
    assert len(textos) >= 25
    for txt in textos:
        low = txt.lower()
        for word in PROHIBIDO:
            assert word not in low, (txt, word)
    # y el recuento independiente desde los bytes
    pic = _pic_index(data)
    n = sum(1 for dest, sites in pic.items()
            if any(0x43901000 <= s < 0x43902610 for s in sites))
    assert n == 47


def test_json_del_hito_es_consistente():
    j = _json()
    assert j["milestone"] == "S144"
    assert j["modulo"] == "[CAM_UTIL_SENS]"
    assert j["contadores"]["cadenas"] == 21
    assert j["contadores"]["sitios"] == 39
    assert j["contadores"]["funciones"] == 5
    assert j["contadores"]["cadenas_con_referencia"] == 21
    assert j["negativo_obturador_iris_iso"] == {}
    assert j["diferencial"]["n_cadenas_a7s"] == 0
    assert j["diferencial"]["n_cadenas_a6300"] == 0
    assert j["diferencial"]["interiores_presentes_a7s"] == 0
    assert j["diferencial"]["interiores_presentes_a6300"] == 0


def test_cadenas_de_los_llamantes_existen_con_su_texto():
    data = _data()
    for va, txt in CADENAS_LLAMANTES.items():
        assert _cstr(data, va) == txt, hex(va)


def test_sin_ficheros_fuente_atribuibles_en_la_banda_del_modulo():
    """No hay ningun nombre .cpp/.h referenciado desde 0x43900000-0x43910000."""
    data = _data()
    pic = _pic_index(data)
    nombres = re.compile(rb"[A-Za-z0-9_./\\-]{3,60}\.(?:cpp|c|h|hpp)\x00")
    for m in nombres.finditer(data):
        s = m.start()
        if not (s == 0 or 32 <= data[s - 1] < 127):
            continue
        va = BASE_VADDR + s
        for site in pic.get(va, []):
            assert not (0x43900000 <= site < 0x43910000), (hex(va), hex(site))
