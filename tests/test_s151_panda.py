"""Tests de S151 — el módulo `[PANDA]` (10 trazas) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen los tres `av-cam.bin`, **recalculan** el
índice de referencias PIC de forma independiente (regla estricta canónica del repo,
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`) y comprueban direcciones, textos,
prólogos, pools literales, GIDs, la tabla de parámetros de "Panda", el diferencial entre
firmwares y el negativo de obturador.

Si cambia una dirección, un texto, un enlace, un pool o un recuento, el test falla.
"""

import bisect
import json
import pathlib
import struct

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
JSON_PATH = "analysis/s151_panda/panda.json"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = b"[PANDA]"
MAX_LDR_GAP = 4096

# --- las 10 cadenas con su dirección exacta y su texto exacto -----------------
CADENAS = {
    0x43C9A599: "[PANDA]: Panda_SendMessage: Pre1 osal_valloc_msg error!\n",
    0x43C9A5D2: "[PANDA]: Panda_SendMessage: Pre2 osal_valloc_msg error!\n",
    0x43C9A60B: "[PANDA]: Panda_SendMessage: Post1 osal_valloc_msg error!\n",
    0x43C9A645: "[PANDA]: Panda_SendMessage: Post2 osal_valloc_msg error!\n",
    0x43C9A67F: "[PANDA]: Panda_SendMessage: Async osal_valloc_msg error!\n",
    0x43C9A6B9: "[PANDA]: Panda_SendMessage: Pre1 osal_snd_msg error!\n",
    0x43C9A6EF: "[PANDA]: Panda_SendMessage: Pre2 osal_snd_msg error!\n",
    0x43C9A725: "[PANDA]: Panda_SendMessage: Post1 osal_snd_msg error!\n",
    0x43C9A75C: "[PANDA]: Panda_SendMessage: Post2 osal_snd_msg error!\n",
    0x43C9A793: "[PANDA]: Panda_SendMessage: Async osal_snd_msg error!\n",
}

# --- sitio de referencia (`add rX,pc`) por cadena, recalculado del blob --------
SITIOS = {
    0x43C9A599: [0x4370744A, 0x43708066],
    0x43C9A5D2: [0x4370745E, 0x43708138],
    0x43C9A60B: [0x43707470],
    0x43C9A645: [0x43707482, 0x4370829E, 0x43708364],
    0x43C9A67F: [0x43707494, 0x43708550],
    0x43C9A6B9: [0x43708048],
    0x43C9A6EF: [0x4370811A],
    0x43C9A725: [0x43708280],
    0x43C9A75C: [0x43708346],
    0x43C9A793: [0x43708532],
}

# --- funciones emisoras: (inicio real, fin del codigo) -------------------------
FUNCIONES = {
    "F1_init": (0x437073CC, 0x43707628),
    "F4_pre": (0x43707F8C, 0x43708148),
    "F5_post": (0x437081B8, 0x43708374),
    "F6_async": (0x437083E4, 0x43708560),
}
SITIOS_POR_FUNCION = {
    "F1_init": [0x4370744A, 0x4370745E, 0x43707470, 0x43707482, 0x43707494],
    "F4_pre": [0x43708048, 0x43708066, 0x4370811A, 0x43708138],
    "F5_post": [0x43708280, 0x4370829E, 0x43708346, 0x43708364],
    "F6_async": [0x43708532, 0x43708550],
}

# --- logger privado del modulo -------------------------------------------------
REPORTER = 0x43707324
LLAMADAS_REPORTER = [0x4370744C, 0x43707460, 0x43707472, 0x43707484, 0x43707496,
                     0x43708068, 0x4370813E, 0x437082A0, 0x4370836A, 0x43708556]
GID_LOG = 0x008F0139
GID_LENTE = 0x00740017
IDS_COLA = [0x00F900BC, 0x00F90078, 0x00F900D5, 0x00F90191,
            0x00F90184, 0x00F90520, 0x00F90521]
TABLILLA = 0x4401EEE4
TAM_BUFFER = 0x40
TAM_MSG_LOG = 0x9A
ID_LOG_PANDA = 0x16

# --- base textual de "Panda" ---------------------------------------------------
PARAM_PANDA = {
    "uc_PandaADErrorOpen": (0x43C99267, 0x43FEBE04, 0x43E0A482),
    "uc_PandaADErrorClose": (0x43C9927B, 0x43FEBE14, 0x43E84C84),
}
NOMBRE_LENS_INIT = 0x43C9AE4E      # 'void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)'
NOMBRE_ODL = 0x43C9AF18            # 'Camera::Lens::ODL::ODL_ERR'
LENS_MOUNT_MOD = 0x43C9A58E       # 'LENS_MOUNT'

# --- equivalencias con los otros firmwares -------------------------------------
EQUIV = {
    "F1_init": {"a6000": 0x437073CC, "a7s": 0x43729910, "a6300": 0x437648D0},
    "F4_pre": {"a6000": 0x43707F88, "a7s": 0x4372A456},
    "F5_post": {"a6000": 0x437081B8, "a7s": 0x4372A6B8},
    "F6_async": {"a6000": 0x437083E4, "a7s": 0x4372A888},
}

# --- vocabulario prohibido (obturador / sensor / exposicion / tiempo) -----------
PROHIBIDO = ("shut", "shutter", "silent", "electro", "mech", "sensor", "imager",
             "expos", "readout", "bracket", "sweep", "interval", "timer", "fps")


# --------------------------------------------------------------- utilidades
_DATA_CACHE = {}


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
    while end < len(data) and end < off + maxlen and (
            32 <= data[end] < 127 or data[end] in (9, 10)):
        end += 1
    return data[off:end].decode("latin1")


def _pic_refs(data, lo, hi):
    """Regla estricta: cada `add rX,pc` con el `ldr rX,[pc,#imm]` mas cercano."""
    ldrs = []
    for a in range(lo, hi, 2):
        o = a - BASE_VADDR
        if o < 0 or o > len(data) - 8:
            continue
        h = _u16(data, a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = _u16(data, a + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE_VADDR
            if 0 <= o2 <= len(data) - 4:
                ldrs.append((a, reg, lit, _u32(data, lit)))
    by = {}
    for a, reg, lit, w in ldrs:
        by.setdefault(reg, []).append((a, lit, w))
    for v in by.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by.items()}
    out = []
    for a in range(lo, hi, 2):
        o = a - BASE_VADDR
        if o < 0 or o > len(data) - 4:
            continue
        h = _u16(data, a)
        if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by.get(reg, [])
        if not v:
            continue
        i = bisect.bisect_right(keys[reg], a) - 1
        if i < 0:
            continue
        la, lit, w = v[i]
        if a - la > MAX_LDR_GAP:
            continue
        tgt = (w + a + 4) & 0xFFFFFFFF
        out.append((a, tgt))
    return out


def _branch_targets(data, objetivo):
    """Todos los destinos de rama del blob que caen en `objetivo`."""
    n = len(data)
    out = []
    for o in range(0, n - 4, 2):
        h1 = _u16(data, BASE_VADDR + o)
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = _u16(data, BASE_VADDR + o + 2)
        s = (h1 >> 10) & 1
        if (h2 & 0xD000) == 0xD000:          # BL
            imm10 = h1 & 0x3FF
            i1 = 1 - (((h2 >> 13) & 1) ^ s)
            i2 = 1 - (((h2 >> 11) & 1) ^ s)
            imm11 = h2 & 0x7FF
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
            if s:
                imm -= (1 << 25)
            if (BASE_VADDR + o + 4 + imm) & 0xFFFFFFFF == objetivo:
                out.append(BASE_VADDR + o)
        elif (h2 & 0xD000) == 0x9000:        # B.w
            imm10 = h1 & 0x3FF
            i1 = 1 - (((h2 >> 13) & 1) ^ s)
            i2 = 1 - (((h2 >> 11) & 1) ^ s)
            imm11 = h2 & 0x7FF
            imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
            if s:
                imm -= (1 << 25)
            if (BASE_VADDR + o + 4 + imm) & 0xFFFFFFFF == objetivo:
                out.append(BASE_VADDR + o)
    return out


# ------------------------------------------------------------------- tests
def test_las_10_cadenas_estan_en_su_direccion_exacta():
    data = _data()
    assert len(CADENAS) == 10
    for vaddr, texto in CADENAS.items():
        assert _cstr(data, vaddr) == texto, hex(vaddr)


def test_el_bloque_es_contiguo_y_en_ese_orden():
    data = _data()
    vaddrs = sorted(CADENAS)
    for a, b in zip(vaddrs, vaddrs[1:]):
        assert a + len(CADENAS[a]) + 1 == b, (hex(a), hex(b))


def test_el_token_no_aparece_antes_ni_despues():
    data = _data()
    assert data.count(TOKEN) == 10
    posiciones = set()
    i = 0
    while True:
        i = data.find(TOKEN, i)
        if i < 0:
            break
        posiciones.add(BASE_VADDR + i)
        i += 1
    # el token esta dentro de las 10 cadenas declaradas y solo en ellas
    esperados = set()
    for vaddr, texto in CADENAS.items():
        esperados.add(vaddr + texto.index("[PANDA]"))
    assert posiciones == esperados


def test_referencias_pic_recalculadas_coinciden():
    data = _data()
    refs = _pic_refs(data, 0x43706000, 0x43709000)
    calculadas = {}
    for sitio, tgt in refs:
        if tgt in CADENAS:
            calculadas.setdefault(tgt, []).append(sitio)
    assert {hex(k): [hex(x) for x in sorted(v)] for k, v in calculadas.items()} == \
           {hex(k): [hex(x) for x in v] for k, v in SITIOS.items()}
    assert len(calculadas) == 10                     # ninguna cadena muerta
    assert sum(len(v) for v in calculadas.values()) == 15


def test_cada_sitio_pertenece_a_su_funcion_declarada():
    for nombre, sitios in SITIOS_POR_FUNCION.items():
        a0, a1 = FUNCIONES[nombre]
        for s in sitios:
            assert a0 <= s < a1, (nombre, hex(s))
    total = sum(len(v) for v in SITIOS_POR_FUNCION.values())
    assert total == 15
    assert sum(len(v) for v in SITIOS.values()) == 15


def test_prologos_de_las_cuatro_funciones_emisoras():
    data = _data()
    # F1: push.w {r4,r5,r6,r7,r8,lr}
    assert data[0x437073CC - BASE_VADDR:0x437073CC - BASE_VADDR + 4] == \
        bytes.fromhex("2de9f041")
    # F4/F5/F6: shrink-wrapping -> ldr rX,[pc] seguido de push.w
    for inicio, push in ((0x43707F8E, "2de9f047"), (0x437081BA, "2de9f041"),
                         (0x437083E6, "2de9f041")):
        assert data[inicio - BASE_VADDR:inicio - BASE_VADDR + 4] == \
            bytes.fromhex(push), hex(inicio)
    # F4/F5/F6 empiezan dos bytes antes con un `ldr rX,[pc]`
    for inicio in (0x43707F8C, 0x437081B8, 0x437083E4):
        h = _u16(data, inicio)
        assert (h & 0xFF00) == 0x4B00 or (h & 0xFF00) == 0x5B00, hex(inicio)


def test_reporter_usa_el_gid_de_log_y_el_tamano_de_mensaje():
    data = _data()
    off = REPORTER - BASE_VADDR
    assert data[off:off + 4] == bytes.fromhex("08b49a22")     # push {r3}; movs r2,#0x9a
    assert (_u16(data, 0x43707326) & 0xFF) == TAM_MSG_LOG
    assert _u32(data, 0x437073C4) == GID_LOG
    assert (_u16(data, 0x4370734E) & 0xFF) == ID_LOG_PANDA
    # llamada a osal_try_valloc_msg (0x435612d0) en 0x4370733c
    assert _bl_destino(data, 0x4370733C) == 0x435612D0
    # vsnprintf (0x439c5004) en 0x43707388 y osal_snd_msg (0x4356120c) en 0x437073b4
    assert _bl_destino(data, 0x43707388) == 0x439C5004
    assert _bl_destino(data, 0x437073B4) == 0x4356120C


def _bl_destino(data, addr):
    """Destino de una instruccion BL de 32 bits en `addr`."""
    h1 = _u16(data, addr)
    h2 = _u16(data, addr + 2)
    assert (h1 & 0xF800) == 0xF000, hex(addr)
    assert (h2 & 0xD000) == 0xD000, hex(addr)
    s = (h1 >> 10) & 1
    i1 = 1 - (((h2 >> 13) & 1) ^ s)
    i2 = 1 - (((h2 >> 11) & 1) ^ s)
    imm = ((s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12)
           | ((h2 & 0x7FF) << 1))
    if s:
        imm -= (1 << 25)
    return (addr + 4 + imm) & 0xFFFFFFFF


def test_el_reporter_solo_lo_llama_el_modulo_panda():
    data = _data()
    assert sorted(_branch_targets(data, REPORTER)) == sorted(LLAMADAS_REPORTER)
    rangos = list(FUNCIONES.values())
    for s in LLAMADAS_REPORTER:
        assert any(a0 <= s < a1 for a0, a1 in rangos), hex(s)


def test_los_buffers_se_reservan_con_el_gid_de_lente_y_0x40_bytes():
    data = _data()
    assert _u32(data, 0x43707644) == GID_LENTE
    assert _u32(data, 0x43708148) == GID_LENTE
    assert _u32(data, 0x43708374) == GID_LENTE
    assert _u32(data, 0x43708560) == GID_LENTE
    # el envio usa el thunk OSAL 0x43561228 con el mismo GID
    assert _bl_destino(data, 0x43708038) == 0x43561228
    assert _bl_destino(data, 0x43708270) == 0x43561228
    assert _bl_destino(data, 0x43708522) == 0x43561228
    # tamano 0x40 en las 5 reservas
    assert (_u16(data, 0x437075BA) & 0xFF) == TAM_BUFFER


def test_las_siete_colas_osal_se_abren_con_los_siete_ids():
    data = _data()
    pool = [0x43707628 + 4 * i for i in range(7)]
    assert [_u32(data, p) for p in pool] == IDS_COLA
    # las 5 reservas de buffer usan el envoltorio [CAM_UTIL]
    assert _bl_destino(data, 0x437075C0) == 0x4390406C
    assert _bl_destino(data, 0x43708054) == 0x4390406C


def _add_pc_destino(data, addr):
    """Destino de un `add rX,pc` en `addr` (regla estricta: ldr mas cercano del mismo reg)."""
    h = _u16(data, addr)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(addr)
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    best = None
    for a in range(addr - 2, max(BASE_VADDR, addr - MAX_LDR_GAP), -2):
        h1 = _u16(data, a)
        lit = None
        r = None
        if (h1 & 0xF800) == 0x4800:
            r = (h1 >> 8) & 7
            lit = ((a + 4) & ~3) + ((h1 & 0xFF) * 4)
        elif (h1 & 0xFF7F) == 0xF85F:
            h2 = _u16(data, a + 2)
            r = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if r == reg and lit is not None:
            best = (a, lit)
            break
    assert best is not None, hex(addr)
    a, lit = best
    return (_u32(data, lit) + addr + 4) & 0xFFFFFFFF


def test_la_tabla_global_de_slots_es_la_del_firmware():
    data = _data()
    # `add r4,pc` -> 0x4401eee4 en las cuatro funciones emisoras
    assert _add_pc_destino(data, 0x437073DA) == TABLILLA
    assert _add_pc_destino(data, 0x43707F98) == TABLILLA
    assert _add_pc_destino(data, 0x437081C4) == TABLILLA
    assert _add_pc_destino(data, 0x437083F0) == TABLILLA


def test_el_inicializador_es_camera_lens_initialize():
    data = _data()
    assert _cstr(data, NOMBRE_LENS_INIT) == \
        "void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)"
    assert _bl_destino(data, 0x4372163E) == FUNCIONES["F1_init"][0]
    # el envoltorio de clase ODL existe
    assert _cstr(data, NOMBRE_ODL).startswith("Camera::Lens::ODL::")


def test_lens_mount_es_un_modulo_registrado_y_panda_no():
    data = _data()
    assert _cstr(data, LENS_MOUNT_MOD) == "LENS_MOUNT"
    assert data.count(b"\x00PANDA\x00") == 0
    # el nombre del modulo se compara en 0x4370727a (ldr r1,[pc,#0x18])
    assert _u32(data, 0x43707294) == 0x00593310
    assert (LENS_MOUNT_MOD - (0x4370727A + 4)) & 0xFFFFFFFF == 0x00593310


def test_base_textual_de_panda_solo_las_dos_esperadas():
    data = _data()
    for nombre, (vaddr, ptr_tabla, variable) in PARAM_PANDA.items():
        assert _cstr(data, vaddr) == nombre
        assert _u32(data, ptr_tabla) == vaddr
        # la tabla es de pares {direccion_variable, nombre} de 16 B
        assert _u32(data, ptr_tabla - 4) == variable
    # ninguna otra aparicion de "Panda" en el blob:
    # 10 trazas x ("[PANDA]" + "Panda_SendMessage") + 2 nombres de parametro
    total = data.count(b"Panda") + data.count(b"PANDA") + data.count(b"panda")
    esperado = 2 * sum(t.count("Panda") for t in CADENAS.values()) + \
        sum(t.count("Panda") for t in PARAM_PANDA)
    assert total == esperado, (total, esperado)


def test_los_parametros_panda_existen_en_los_tres_firmwares():
    for path in (BIN_PATH, A7S_BIN, A6300_BIN):
        data = _data(path)
        assert data.count(b"uc_PandaADErrorOpen") == 1, path
        assert data.count(b"uc_PandaADErrorClose") == 1, path


def test_diferencial_del_token_y_de_los_textos_internos():
    for path, esperado_token, esperado_internos in (
            (BIN_PATH, 10, 10), (A7S_BIN, 0, 0), (A6300_BIN, 0, 0)):
        data = _data(path)
        assert data.count(TOKEN) == esperado_token, path
        for texto in CADENAS.values():
            nucleo = texto.split(": ", 1)[1].rstrip("\n").encode("latin1")
            assert (nucleo in data) is (esperado_internos == 10), (path, nucleo)


def test_el_codigo_panda_existe_en_los_tres_firmwares():
    """Los 7 ids de cola aparecen 1 vez en cada blob, en el pool de la funcion equivalente."""
    for path in (BIN_PATH, A7S_BIN, A6300_BIN):
        data = _data(path)
        for v in IDS_COLA:
            assert data.count(struct.pack("<I", v)) == 1, (path, hex(v))


def test_equivalencia_de_F1_init_entre_firmwares():
    """Mismo prologo y mismo pool de colas en A6000 / A7S / A6300."""
    for nombre, dirs in EQUIV["F1_init"].items():
        path = {"a6000": BIN_PATH, "a7s": A7S_BIN, "a6300": A6300_BIN}[nombre]
        data = _data(path)
        inicio = dirs
        # la funcion equivalente arranca con push.w {r4-r8,lr} seguido del ldr del id
        assert data[inicio - BASE_VADDR:inicio - BASE_VADDR + 4] == \
            bytes.fromhex("2de9f041"), (nombre, hex(inicio))
        h = _u16(data, inicio + 4)
        assert (h & 0xFF00) == 0x4800, (nombre, hex(inicio + 4))
        # el pool correspondiente contiene el primer id de cola
        pool = ((inicio + 4 + 4) & ~3) + ((h & 0xFF) * 4)
        assert _u32(data, pool) == IDS_COLA[0], (nombre, hex(pool))


def test_el_reporter_es_nuevo_en_la_fw321():
    """El prologo 'push {r3}; movs r2,#0x9a' (familia de loggers) no existe en A7S/A6300."""
    pat = bytes.fromhex("08b49a22")
    assert _data(BIN_PATH).count(pat) == 43
    assert _data(A7S_BIN).count(pat) == 0
    assert _data(A6300_BIN).count(pat) == 0
    # y el logger PANDA pertenece a esa familia
    data = _data(BIN_PATH)
    assert data[REPORTER - BASE_VADDR:REPORTER - BASE_VADDR + 4] == pat


def test_las_funciones_equivalentes_en_a7s_no_tienen_trazas_panda():
    data = _data(A7S_BIN)
    for nombre in ("F1_init", "F4_pre", "F5_post", "F6_async"):
        a = EQUIV[nombre]["a7s"]
        assert data[a - BASE_VADDR:a - BASE_VADDR + 200].count(TOKEN) == 0, nombre


def test_negativo_de_obturador_en_las_10_trazas():
    for texto in CADENAS.values():
        bajo = texto.lower()
        for palabra in PROHIBIDO:
            assert palabra not in bajo, (palabra, texto)


def test_el_codigo_panda_no_referencia_ficheros_fuente():
    data = _data()
    refs = _pic_refs(data, 0x43707324, 0x43708560)
    for _, tgt in refs:
        texto = _cstr(data, tgt)
        assert ".cpp" not in texto, texto
        assert ".h" not in texto, texto


def test_destinos_de_llamada_del_codigo_panda():
    """Exhaustivo: el codigo PANDA solo llama a thunks OSAL, a sus propios helpers,
    al envoltorio [CAM_UTIL] y a la biblioteca C. Nada de captura ni de imager."""
    import capstone
    data = _data()
    md = capstone.Cs(capstone.CS_ARCH_ARM, capstone.CS_MODE_THUMB)
    md.detail = True
    lo, hi = 0x43707324, 0x43708560
    destinos = {}
    for ins in md.disasm(data[lo - BASE_VADDR:hi - BASE_VADDR], lo):
        if ins.mnemonic in ("bl", "blx"):
            destinos[ins.op_str] = destinos.get(ins.op_str, 0) + 1
    esperados = {
        "#0x43560cc8": 1, "#0x4356120c": 1, "#0x43561228": 5, "#0x43561244": 1,
        "#0x435612d0": 1, "#0x435612ec": 6, "#0x43561508": 7,
        "#0x43707324": 7, "#0x43707d44": 1, "#0x43707ec8": 1,
        "#0x4390406c": 10, "#0x439c5004": 1, "#0x439c5a04": 1,
        "#0x43ada9fc": 1, "#0x43adaa00": 1, "#0x43b5e2a4": 1,
        "r4": 1,                      # una llamada indirecta (blx r4)
    }
    assert destinos == esperados, destinos
    # ninguna llamada entra en zonas de captura / imager /_REL / ACCY / CDIAG
    zonas = {"REL": (0x4379D114, 0x4379E600), "RelQueue": (0x4381C30C, 0x4381D150),
             "ACCY": (0x43562A08, 0x43566F20), "CDIAG": (0x435A127A, 0x435A50B6)}
    for t in destinos:
        if not t.startswith("#0x"):
            continue
        a = int(t[1:], 16)
        for n, (zlo, zhi) in zonas.items():
            assert not (zlo <= a <= zhi), (n, t)


def test_el_codigo_panda_no_referencia_cadenas_de_imager_ni_de_captura():
    data = _data()
    refs = _pic_refs(data, 0x43707324, 0x43708560)
    for _, tgt in refs:
        texto = _cstr(data, tgt)
        for token in ("[CAM_IMAGER]", "[IMAGING]", "[IMAGING_CAP]", "[CAMERA_MAIN]",
                      "shutter", "shut"):
            assert token not in texto, (token, texto)


def test_el_json_es_consistente_con_los_bytes():
    doc = _json()
    assert doc["hito"] == "S151"
    cadenas = {c["vaddr"]: c["texto"] for c in doc["cadenas"]}
    assert cadenas == CADENAS
    refs = doc["referencias"]
    assert len(refs) == 10
    assert sum(len(v) for v in refs.values()) == 15
    assert doc["ids_osal"]["gid_log"] == GID_LOG
    assert doc["ids_osal"]["gid_mensajes_lente"] == GID_LENTE
    assert doc["ids_osal"]["colas_abiertas"] == IDS_COLA
    dif = doc["diferencial"]
    assert dif["a6000_fw321"]["ocurrencias_token"] == 10
    assert dif["a7s_fw320"]["ocurrencias_token"] == 0
    assert dif["a6300_fw201"]["ocurrencias_token"] == 0
    assert dif["a6000_fw321"]["textos_internos_presentes"] == 10
    assert dif["a7s_fw320"]["textos_internos_presentes"] == 0
    assert dif["a6300_fw201"]["textos_internos_presentes"] == 0


def test_el_json_refleja_las_funciones_emisoras_declaradas():
    doc = _json()
    for nombre, (a0, a1) in FUNCIONES.items():
        assert doc["funciones_emisoras"][nombre]["inicio"] == a0
        assert doc["funciones_emisoras"][nombre]["fin"] == a1
    assert doc["helper_reporter"]["vaddr"] == REPORTER
    assert sorted(doc["llamadas_al_reporter"]) == sorted(LLAMADAS_REPORTER)
    assert doc["base_textual_panda"]["cadena_independiente_PANDA"] == 0
    assert doc["base_textual_panda"]["clases_rtti_panda"] == 0
    assert doc["base_textual_panda"]["ficheros_panda"] == 0
