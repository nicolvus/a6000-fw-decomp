"""Tests de S148 — el módulo `[DEPTH]` (16 trazas) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware, **recalculan** el índice
de referencias PIC de forma independiente (regla estricta canónica del repo,
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`) y comprueban direcciones,
textos, la tabla de comandos, la clase RTTI, el GID, el consumidor del MakerNote
y el negativo de obturador/sensor/exposición.

Si cambia una dirección, un texto, un enlace o un recuento, el test falla.
"""

import bisect
import json
import pathlib
import struct

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
JSON_PATH = "analysis/s148_depth/depth.json"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = b"[DEPTH]"
MAX_LDR_GAP = 4096

# --- las 16 cadenas con su dirección exacta y su texto exacto ----------------
CADENAS = {
    0x43C249EC: "[DEPTH][INFO]Regist Dummy Receiver 0x %08X",
    0x43C24A17: "[DEPTH][INFO]Rsp: cid = %08X, status = %d, valueDepth = %d",
    0x43C24A52: "[DEPTH][INFO]status = %d, valueDepth = %d",
    0x43C24A7C: "[DEPTH][INFO]usage: notifyOff respGID(as HEX)",
    0x43C24AAA: "[DEPTH][INFO]ret = %08X",
    0x43C24AC2: "[DEPTH][INFO]usage: notifyOn respGID(as HEX)",
    0x43C24AEF: "[DEPTH][INFO]ret = 0x%08X",
    0x43C24B09: "[DEPTH][INFO]usage: Update status(as HEX) valueDepth(as HEX)",
    0x43C24B96: "[DEPTH][INFO]GET %d %d",
    0x43C24BAD: "[DEPTH][INFO]NOTIFY to %08X %d %d",
    0x43C24BCF: "[DEPTH][INFO]UPDATE %d %d",
    0x43C24BE9: "[DEPTH][DEBUG]NOTTIFY_ON %08X",
    0x43C24C07: "[DEPTH][WARN]ERR NOTTIFY_ON %08X %08X",
    0x43C24C2D: "[DEPTH][DEBUG]NOTTIFY_OFF %08X",
    0x43C24C4C: "[DEPTH][WARN]ERR NOTTIFY_OFF %08X %08X",
    0x43C24C73: "[DEPTH][WARN]ERR Invalid Command %08X %08X",
}

# --- sitio de referencia (`add rX,pc`) por cadena -----------------------------
SITIOS = {
    0x43C249EC: [0x435622BA],
    0x43C24A17: [0x435622EC],
    0x43C24A52: [0x43562338, 0x43562444],
    0x43C24A7C: [0x43562366],
    0x43C24AAA: [0x4356239C],
    0x43C24AC2: [0x435623CE],
    0x43C24AEF: [0x43562402],
    0x43C24B09: [0x43562464],
    0x43C24B96: [0x43562652],
    0x43C24BAD: [0x435626B8],
    0x43C24BCF: [0x43541B28],
    0x43C24BE9: [0x4356270C],
    0x43C24C07: [0x4356273E],
    0x43C24C2D: [0x43562764],
    0x43C24C4C: [0x43562786],
    0x43C24C73: [0x435627A6],
}

# --- funciones emisoras (punto de entrada real) -------------------------------
FUNCIONES = {
    0x43541B00: ["UPDATE %d %d"],
    0x4356228C: ["Regist Dummy Receiver"],
    0x435622D4: ["Rsp: cid"],
    0x4356230C: ["status = %d, valueDepth = %d"],
    0x43562354: ["usage: notifyOff", "ret = %08X"],
    0x435623BC: ["usage: notifyOn", "ret = 0x%08X"],
    0x43562424: ["status = %d, valueDepth = %d"],
    0x43562454: ["usage: Update status"],
    0x43562634: ["GET %d %d"],
    0x43562660: ["NOTIFY to"],
    0x435626D4: ["NOTTIFY_ON", "ERR NOTTIFY_ON", "NOTTIFY_OFF", "ERR NOTTIFY_OFF",
                 "ERR Invalid Command"],
}

# --- tabla de comandos (12 B: {nombre, nombre, handler}) ----------------------
TABLA_A6000 = 0x43FD7C30
TABLA_A7S = 0x43FD9914
TABLA_A6300 = 0x4419920C
COMANDOS = ["update", "getLiro", "getMsg", "notifyOn", "notifyOff", "enableDummyRecv"]
HANDLERS_A6000 = [0x43562454, 0x43562424, 0x4356230C, 0x435623BC, 0x43562354, 0x4356228C]
HANDLERS_A7S = [0x43A20010, 0x43A1FFEA, 0x435600B8, 0x43560120, 0x435600E4, 0x43560074]
HANDLERS_A6300 = [0x43AC9378, 0x43AC9352, 0x4355A7CC, 0x4355A834, 0x4355A7F8, 0x4355A788]

# --- clase, RTTI, vtable, nombre de registro ---------------------------------
NOMBRE_CLASE = 0x43C24B85          # '14DepthGaugeMain'
NOMBRE_REGISTRO = 0x43C24B46       # 'depth'
TYPE_INFO = 0x43FD7C84             # {vptr, nombre}
VTABLE = 0x43FB8F50                # {offset-to-top, type_info, f1, f2}
SINGLETON = 0x43E131E8
GID = 0x018B04DC
TABLA_SERVICIOS = 0x4401EEE4

# --- consumidor verificado (MakerNote) ---------------------------------------
MK_FILE_STR = 0x43CC56DC           # 'CS_ExifMakerNote.cpp'
CONSUMIDOR = 0x438B900A            # bl -> getMsg
TAG_RACIONAL = 0x438B9090          # movw r1,#0x5001
TAG_ESTADO = 0x438B90B0            # movw r1,#0x5002
RACION_MUL = 0x438B90A0            # movs r2,#0x0A
RACION_DEN = 0x438B90A4            # movw r2,#0x3E8
CALLER_ACCY = [0x43564DC0, 0x43564ED2]

# --- vocabulario prohibido (obturador / sensor / exposición / enfoque) --------
PROHIBIDO = ("shut", "shutter", "silent", "electro", "mech", "sensor", "exposure",
             "readout", "focus", "af", "dist", "iso", "aperture", "iris", "zpd",
             "imager", "drv", "drive")

# --- destinos de llamada permitidos desde el modulo ---------------------------
LLAMADAS_PERMITIDAS = {
    0x4356120C, 0x43561228, 0x43561244, 0x4356127C, 0x435612D0, 0x435612EC,
    0x43561324, 0x435621E0, 0x435624C8, 0x43562578, 0x43562590, 0x435625DC,
    0x43562634, 0x43562660, 0x439B4244, 0x439C0958, 0x439C5004, 0x439C5A04,
    0x43A3AC8C, 0x43A3AC98, 0x43A3ACAA, 0x43A3ACCA, 0x43A3AF86, 0x43A3AF9A,
}

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
    adds = []
    for a in range(BASE_VADDR, BASE_VADDR + n - 8, 2):
        off = a - BASE_VADDR
        h = struct.unpack("<H", data[off:off + 2])[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack("<H", data[off + 2:off + 4])[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE_VADDR
            if 0 <= o2 <= n - 4:
                ldrs.append((a, reg, struct.unpack("<I", data[o2:o2 + 4])[0]))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 0
    by_reg = {}
    for a, reg, w in ldrs:
        by_reg.setdefault(reg, []).append((a, w))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    for a, reg in adds:
        v = by_reg.get(reg)
        if not v:
            continue
        i = bisect.bisect_left(keys[reg], a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        out.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    _PIC_CACHE[key] = out
    return out


def _prologues(data):
    out = []
    n = len(data)
    for a in range(BASE_VADDR, BASE_VADDR + n - 4, 2):
        off = a - BASE_VADDR
        h = struct.unpack("<H", data[off:off + 2])[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (struct.unpack("<H", data[off + 2:off + 4])[0] & 0x4000):
            out.append(a)
    return out


def _cmd_table(data, addr):
    """[(nombre, handler)] de la tabla de 12 B; se detiene en el terminador."""
    out = []
    for i in range(16):
        a = addr + 12 * i
        n1 = _u32(data, a)
        n2 = _u32(data, a + 4)
        h = _u32(data, a + 8)
        if n1 == 0 and n2 == 0 and h == 0:
            break
        out.append((_cstr(data, n1), h & ~1))
    return out


# ============================================================== tests
def test_hay_16_tokas_depth():
    data = _data()
    assert data.count(TOKEN) == 16
    toks = _strings_with(data)
    assert len(toks) == 16


def test_textos_exactos_en_sus_direcciones():
    data = _data()
    for addr, text in CADENAS.items():
        assert _cstr(data, addr) == text, hex(addr)


def test_rango_y_orden_de_las_trazas():
    data = _data()
    addrs = sorted(CADENAS)
    assert addrs[0] == 0x43C249EC
    assert addrs[-1] == 0x43C24C73
    # el bloque es contiguo: entre la primera y la última sólo hay las 16
    found = [a for a, _t, _x in _strings_with(data)]
    assert found == addrs


def test_niveles_de_log():
    data = _data()
    joined = "\n".join(CADENAS.values())
    assert joined.count("[INFO]") == 11
    assert joined.count("[DEBUG]") == 2
    assert joined.count("[WARN]") == 3


def test_sitios_pic_calculados_de_forma_independiente():
    data = _data()
    pic = _pic_index(data)
    for addr, sites in SITIOS.items():
        assert sorted(set(pic.get(addr, []))) == sorted(sites), hex(addr)


def test_numero_total_de_sitios_y_de_funciones():
    data = _data()
    pic = _pic_index(data)
    total = sum(len(v) for a, v in pic.items() if a in CADENAS)
    assert total == 17
    assert len(SITIOS) == 16
    # 11 funciones emisoras distintas
    assert len(FUNCIONES) == 11


def test_cada_sitio_pic_esta_verificado_a_mano():
    """Para cada sitio: `add rX,pc` + `ldr` del pool -> destino == la cadena."""
    data = _data()
    for addr, sites in SITIOS.items():
        for site in sites:
            h = _u16(data, site)
            assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(site)
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            # el `ldr` emparejado es el más cercano por detrás del mismo registro
            best = None
            for la in range(max(BASE_VADDR, site - MAX_LDR_GAP), site, 2):
                h2 = _u16(data, la)
                r = lit = None
                if (h2 & 0xF800) == 0x4800:
                    r = (h2 >> 8) & 7
                    lit = ((la + 4) & ~3) + ((h2 & 0xFF) * 4)
                elif (h2 & 0xFF7F) == 0xF85F:
                    h3 = _u16(data, la + 2)
                    r = (h3 >> 12) & 0xF
                    lit = ((la + 4) & ~3) + ((((h3 >> 8) & 0xF) << 8) | (h3 & 0xFF))
                if r != reg:
                    continue
                if best is None or la > best[0]:
                    best = (la, lit)
            assert best is not None, hex(site)
            la, lit = best
            w = _u32(data, lit)
            assert (w + site + 4) & 0xFFFFFFFF == addr, hex(site)


def test_no_hay_punteros_absolutos_a_las_trazas():
    data = _data()
    for addr in CADENAS:
        pat = struct.pack("<I", addr)
        assert data.count(pat) == 0, hex(addr)


def test_ninguna_traza_muerta():
    data = _data()
    pic = _pic_index(data)
    for addr in CADENAS:
        assert addr in pic, hex(addr)


def test_tabla_de_comandos_de_la_a6000():
    data = _data()
    tab = _cmd_table(data, TABLA_A6000)
    assert [n for n, _h in tab] == COMANDOS
    assert [h for _n, h in tab] == HANDLERS_A6000
    # terminador {0,0,0} justo detras
    assert _u32(data, TABLA_A6000 + 72) == 0
    assert _u32(data, TABLA_A6000 + 76) == 0
    assert _u32(data, TABLA_A6000 + 80) == 0


def test_tabla_de_comandos_identica_en_a7s_y_a6300():
    for path, addr, handlers in ((A7S_BIN, TABLA_A7S, HANDLERS_A7S),
                                  (A6300_BIN, TABLA_A6300, HANDLERS_A6300)):
        data = _data(path)
        tab = _cmd_table(data, addr)
        assert [n for n, _h in tab] == COMANDOS, path
        assert [h for _n, h in tab] == handlers, path


def test_nombre_de_registro_del_modulo():
    data = _data()
    assert _cstr(data, NOMBRE_REGISTRO) == "depth"
    # el `add r0,pc` de 0x4356249A resuelve a ese nombre
    pic = _pic_index(data)
    assert 0x4356249A in pic.get(NOMBRE_REGISTRO, [])
    # y el `add r1,pc` de 0x4356249C resuelve a la tabla de comandos
    assert 0x4356249C in pic.get(TABLA_A6000, [])


def test_clase_rtti_y_vtable():
    data = _data()
    assert _cstr(data, NOMBRE_CLASE) == "14DepthGaugeMain"
    assert _u32(data, TYPE_INFO) == 0x43FD04F8
    assert _u32(data, TYPE_INFO + 4) == NOMBRE_CLASE
    assert _u32(data, VTABLE) == 0
    assert _u32(data, VTABLE + 4) == TYPE_INFO
    assert _u32(data, VTABLE + 8) == 0x435624B1     # constructor (Thumb)
    assert _u32(data, VTABLE + 12) == 0x43A3ACD1


def test_gid_del_subsistema_en_los_tres_firmwares():
    pat = struct.pack("<I", GID)
    for path in (BIN_PATH, A7S_BIN, A6300_BIN):
        assert _data(path).count(pat) == 6, path


def test_clamp_de_valuedepth_a_4000():
    data = _data()
    # cmp.w r3,#0xFA0  ->  bytes b3 f5 7a 6f
    assert data[0x43541B04 - BASE_VADDR:0x43541B04 - BASE_VADDR + 4] == bytes.fromhex("b3f57a6f")


def test_ids_de_notificacion_1_2_3():
    data = _data()
    # 0x435626DC cmp r7,#2 (bytes 02 2f) ; 0x435626E0 cmp r7,#3 ; 0x435626E4 cmp r7,#1
    assert data[0x435626DC - BASE_VADDR:0x435626DC - BASE_VADDR + 2] == bytes.fromhex("022f")
    assert data[0x435626E0 - BASE_VADDR:0x435626E0 - BASE_VADDR + 2] == bytes.fromhex("032f")
    assert data[0x435626E4 - BASE_VADDR:0x435626E4 - BASE_VADDR + 2] == bytes.fromhex("012f")


def test_umbral_de_argumentos_de_los_handlers():
    data = _data()
    # notifyOff / notifyOn exigen 2 tokens (cmp r0,#2); update exige 3 (cmp r0,#3)
    assert data[0x43562354 - BASE_VADDR:0x43562354 - BASE_VADDR + 2] == bytes.fromhex("0228")
    assert data[0x435623BC - BASE_VADDR:0x435623BC - BASE_VADDR + 2] == bytes.fromhex("0228")
    assert data[0x43562454 - BASE_VADDR:0x43562454 - BASE_VADDR + 2] == bytes.fromhex("0328")


def _bl_target(data, site):
    """Destino de un `bl` (16 o 32 bits) desensamblado con capstone."""
    import capstone
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = False
    for ins in md.disasm(data[site - BASE_VADDR:site - BASE_VADDR + 4], site):
        if ins.mnemonic in ("bl", "blx"):
            return int(ins.op_str[1:], 0)
    return None


def test_consumidor_makernote_usa_getmsg():
    data = _data()
    assert _cstr(data, MK_FILE_STR) == "CS_ExifMakerNote.cpp"
    # bl -> 0x43A3AC98 (API getMsg) en 0x438B900A
    assert _bl_target(data, CONSUMIDOR) == 0x43A3AC98


def test_tags_exif_5001_y_5002():
    data = _data()
    # movw r1,#0x5001 -> 45 f2 01 01 ; movw r1,#0x5002 -> 45 f2 02 01
    assert data[TAG_RACIONAL - BASE_VADDR:TAG_RACIONAL - BASE_VADDR + 4] == bytes.fromhex("45f20101")
    assert data[TAG_ESTADO - BASE_VADDR:TAG_ESTADO - BASE_VADDR + 4] == bytes.fromhex("45f20201")
    # el racional es (valueDepth*10 : 1000)
    assert data[RACION_MUL - BASE_VADDR:RACION_MUL - BASE_VADDR + 2] == bytes.fromhex("0a22")
    assert data[RACION_DEN - BASE_VADDR:RACION_DEN - BASE_VADDR + 4] == bytes.fromhex("4ff47a72")


def test_accy_llama_a_la_api_update():
    data = _data()
    for site in CALLER_ACCY:
        assert _bl_target(data, site) == 0x43A3ACAA, hex(site)


def test_el_modulo_no_sale_de_si_mismo():
    """Todos los `bl` del módulo apuntan a la lista permitida."""
    import capstone
    data = _data()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = False
    regions = [(0x4356228C, 0x435627B0), (0x43541B00, 0x43541BA2),
               (0x43A3AC8C, 0x43A3ACC6), (0x4356248C, 0x435624A6),
               (0x43562578, 0x43562590)]
    seen = set()
    for lo, hi in regions:
        for ins in md.disasm(data[lo - BASE_VADDR:hi - BASE_VADDR], lo):
            if ins.mnemonic in ("bl", "blx") and ins.op_str.startswith("#"):
                seen.add(int(ins.op_str[1:], 0) & ~1)
    assert seen, "no se ha encontrado ninguna llamada"
    fuera = seen - LLAMADAS_PERMITIDAS
    assert not fuera, sorted(hex(x) for x in fuera)


def test_negativo_obturador_sensor_exposicion():
    data = _data()
    for addr, text in CADENAS.items():
        low = text.lower()
        for w in PROHIBIDO:
            assert w not in low, (hex(addr), w)


def test_diferencial_sin_trazas_depth():
    for path in (A7S_BIN, A6300_BIN):
        data = _data(path)
        assert data.count(TOKEN) == 0, path
        assert b"valueDepth" not in data, path
        assert b"14DepthGaugeMain" in data, path    # el modulo SI existe
        assert data.count(b"14DepthGaugeMain") == 1, path


def test_diferencial_textos_interiores_ausentes():
    for path in (A7S_BIN, A6300_BIN):
        data = _data(path)
        for _addr, text in CADENAS.items():
            core = text.split("]", 2)[-1]
            assert core.encode() not in data, (path, core)


def test_json_consistente_con_los_bytes():
    js = _json()
    assert js["modulo"] == "[DEPTH]"
    assert js["contadores"]["n_cadenas"] == 16
    assert js["contadores"]["n_sitios_pic"] == 17
    assert js["contadores"]["n_funcs_emisoras"] == 11
    assert js["contadores"]["n_muertas"] == 0
    assert js["contadores"]["rango"] == ["0x43c249ec", "0x43c24c73"]
    assert js["datos_verificados"]["gid"] == "0x018B04DC"
    assert js["tabla_comandos"]["a6000"] == "0x43fd7c30"
    for s in js["cadenas"]:
        addr = int(s["addr"], 16)
        assert addr in CADENAS
        assert s["text"] == CADENAS[addr]
        assert s["n_sites"] == len(SITIOS[addr])
    assert js["diferencial"]["a7s_fw320"]["n_cadenas_depth"] == 0
    assert js["diferencial"]["a6300_fw201"]["n_cadenas_depth"] == 0
    assert js["diferencial"]["a7s_fw320"]["clase_depthgauge_main"] == 1
    assert js["diferencial"]["a6300_fw201"]["clase_depthgauge_main"] == 1
