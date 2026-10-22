"""Tests de S140 — el módulo `[CAM_UTIL_ADJ]` (22 trazas) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware, **recalculan** el mapa de
referencias PIC de forma independiente (regla estricta canónica del repo,
`analysis/s106_imaging_cap/scan_pic_refs_strict.py`) y comprueban direcciones, textos,
tablas y guardas concretas. Si cambia una dirección, un texto, una tabla o un recuento,
el test falla.
"""

import bisect
import json
import pathlib
import re
import struct

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
JSON_PATH = "analysis/s140_cam_util_adj/cam_util_adj.json"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = b"[CAM_UTIL_ADJ]"

# --- las 22 cadenas con su dirección exacta y su texto exacto ----------------
CADENAS = {
    0x43CCDCEE: "[CAM_UTIL_ADJ]:  -- Table Write",
    0x43CCDD0E: "[CAM_UTIL_ADJ]:  -- :[Size] %08x [Orgdata] %x",
    0x43CCDD3C: "[CAM_UTIL_ADJ]:  -- :[Wdata] %x",
    0x43CCDD5C: "[CAM_UTIL_ADJ]:  -- Table Read",
    0x43CCDD7B: "[CAM_UTIL_ADJ]:  -- :[Size] %08x [Rdata] %x",
    0x43CCDDA7: "[CAM_UTIL_ADJ]:  -- :[Orgdata] %x",
    0x43CCDDC9: "[CAM_UTIL_ADJ]: Senser RAM Access: CMD %x, Block %x",
    0x43CCDDFD: "[CAM_UTIL_ADJ]:   : [Mode]:%x, [ResCode]:%x, [StepNum]:%x",
    0x43CCDE37: "[CAM_UTIL_ADJ]:   : [Adr]:%08x, [BSize]:%08x,[Size]:%08x",
    0x43CCDE70: "[CAM_UTIL_ADJ]:   : [D0]:%04x, [D1]:%04x,[D2]:%04x, [D3]:%04x",
    0x43CCDEAE: "[CAM_UTIL_ADJ]:   : [D4]:%04x, [D5]:%04x,[D6]:%04x, [D7]:%04x",
    0x43CCDEEC: "[CAM_UTIL_ADJ]:   : [Module ID]:%08x, [Offset]:%08x, [Size]:%08x",
    0x43CCDF2D: "[CAM_UTIL_ADJ]: ---cam_adjcmd_handle_cb()---[CmdCode]:%04x",
    0x43CCDF68: "[CAM_UTIL_ADJ]:  For SensRamAcs[DataSize]%x",
    0x43CCDF94: "[CAM_UTIL_ADJ]:  For SensRamAcs[ModuleID]%x [Value]%x",
    0x43CCDFCA: "[CAM_UTIL_ADJ]:  [OriginalCmdCode ]:%04x",
    0x43CCDFF3: "[CAM_UTIL_ADJ]:  [OriginalDataSize]:%04x",
    0x43CCE01C: "[CAM_UTIL_ADJ]:  [OriginalBDataSize]:%04x",
    0x43CCE046: "[CAM_UTIL_ADJ]: ---Finish SENSER Infra Call Back Operation--- :%x",
    0x43CCE088: "[CAM_UTIL_ADJ]:     tsk_cam_adjctrl: begin. [Osal]%d",
    0x43CCE0BD: "[CAM_UTIL_ADJ]:     tsk_cam_adjctrl: rcv failed(%d).",
    0x43CCE0F2: "[CAM_UTIL_ADJ]:     tsk_cam_adjctrl: rcv cmd err(%x).",
}

# --- sitio de referencia (add rX,pc) por cadena ------------------------------
SITIOS = {
    0x43CCDCEE: 0x439007F8,
    0x43CCDD0E: 0x4390080E,
    0x43CCDD3C: 0x43900824,
    0x43CCDD5C: 0x43900864,
    0x43CCDD7B: 0x43900878,
    0x43CCDDA7: 0x4390088E,
    0x43CCDDC9: 0x43900A6A,
    0x43CCDDFD: 0x43900A84,
    0x43CCDE37: 0x43900A9E,
    0x43CCDE70: 0x43900ABC,
    0x43CCDEAE: 0x43900AE2,
    0x43CCDEEC: 0x43900AF0,
    0x43CCDF2D: 0x43900B04,
    0x43CCDF68: 0x43900B14,
    0x43CCDF94: 0x43900B26,
    0x43CCDFCA: 0x43900B3C,
    0x43CCDFF3: 0x43900B4E,
    0x43CCE01C: 0x43900B60,
    0x43CCE046: 0x43900BC6,
    0x43CCE088: 0x43900C5E,
    0x43CCE0BD: 0x43900C86,
    0x43CCE0F2: 0x43900D0A,
}

# --- funciones y su reparto de trazas ---------------------------------------
FUNCIONES = {
    0x439007B0: ("Table Write / Table Read", 6),
    0x43900A24: ("cam_adjcmd_handle_cb()", 13),
    0x43900C44: ("tsk_cam_adjctrl", 3),
}

# --- tabla de despacho (8 B por entrada: campo0 + puntero a función) ---------
DESPACHO = {
    0x440121F8: (0x00000000, 0x43B2A0B9),
    0x44012200: (0x00000001, 0x439007B1),
    0x44012208: (0x00000002, 0x43B2A0B9),
}

# --- tabla de codigos "Sens:*" (cmd u32, size u32, str_ptr u32) --------------
SENS_CLAVES = {
    0x04020180: (12, "Sens:AdjCmd CAIF"),
    0x01000181: (2, "Sens:Invalid block"),
    0x01000182: (2, "Sens:Invalid code"),
    0x01000183: (4, "Sens:Invalid offset"),
    0x01000184: (4, "Sens:Invalid size"),
    0x01000185: (4, "Sens:Read only"),
    0x01000186: (4, "Sens:Write only"),
    0x01000187: (0, "Sens:no buf"),
    0x04000188: (1, "Sens:RAM Write"),
    0x04020189: (1, "Sens:RAM Read"),
    0x0400018A: (12, "Sens:AdjCmd DwnCamera"),
    0x0100018B: (0, "Sens:System error"),
    0x0400018C: (12, "Sens:DwnCamera Done"),
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


def _prologues(data):
    out = []
    a = BASE_VADDR
    n = len(data)
    while a < BASE_VADDR + n - 4:
        h = _u16(data, a)
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D:
            h2 = _u16(data, a + 2)
            if h2 & 0x4000:
                out.append(a)
        a += 2
    return out


def _fstart(prologues, site):
    i = bisect.bisect_right(prologues, site) - 1
    return prologues[i] if i >= 0 else None


def _bl_targets(data, lo, hi):
    """Destinos de las instrucciones `bl`/`blx` de 32 bits en [lo, hi)."""
    out = []
    a = lo
    while a < hi - 4:
        h1 = _u16(data, a)
        if (h1 & 0xF800) != 0xF000:
            a += 2
            continue
        h2 = _u16(data, a + 2)
        if (h2 & 0xD000) not in (0x9000, 0xD000):
            a += 2
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = ((s << 24) | (i1 << 23) | (i2 << 22) |
               ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
        if s:
            imm -= 1 << 25
        out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
        a += 4
    return out


def _sens_table(path):
    """[(cmd, size, texto)] de la tabla {cmd,size,str_ptr} de codigos "Sens:*"."""
    d = _data(path)
    anchor = d.find(b"Sens:AdjCmd CAIF")
    assert anchor >= 0, f"no se encuentra 'Sens:AdjCmd CAIF' en {path}"
    idx = d.find(struct.pack("<II", 0x04020180, 0x0C))
    assert idx >= 0, f"no se encuentra la entrada 0x04020180 en {path}"
    delta = struct.unpack_from("<I", d, idx + 8)[0] - anchor
    start = idx
    while start >= 12:
        cmd, size, _ptr = struct.unpack_from("<III", d, start - 12)
        if not (0x04000000 <= cmd <= 0x0402FFFF or 0x01000000 <= cmd <= 0x0102FFFF):
            break
        start -= 12
    rows = []
    o = start
    while True:
        cmd, size, ptr = struct.unpack_from("<III", d, o)
        if not (0x04000000 <= cmd <= 0x0402FFFF or 0x01000000 <= cmd <= 0x0102FFFF):
            break
        so = ptr - delta
        end = so
        while end < len(d) and 32 <= d[end] < 127:
            end += 1
        rows.append((cmd, size, d[so:end].decode("latin1")))
        o += 12
    return rows


# ------------------------------------------------------------------- cadenas
class TestCadenas:
    def test_conteo_y_rango(self):
        data = _data()
        occ = _strings_with(data)
        assert len(occ) == 22
        starts = {s for _, s, _ in occ}
        assert len(starts) == 22, "las 22 apariciones dan 22 cadenas distintas"
        assert min(starts) == 0x43CCDCEE
        assert max(starts) == 0x43CCE0F2

    def test_textos_concretos(self):
        data = _data()
        for va, texto in CADENAS.items():
            assert _cstr(data, va) == texto, f"texto cambiado en {hex(va)}"

    def test_todas_empiezan_por_el_token(self):
        data = _data()
        for _, s, texto in _strings_with(data):
            assert texto.startswith("[CAM_UTIL_ADJ]")

    def test_bloque_contiguo_sin_otras_cadenas(self):
        """Entre la primera y la última traza no hay ninguna otra cadena."""
        data = _data()
        lo, hi = 0x43CCDCEE - BASE_VADDR, 0x43CCE0F2 - BASE_VADDR
        otros = []
        i = lo
        while i <= hi:
            j = i
            while j < len(data) and 32 <= data[j] < 127:
                j += 1
            if j - i >= 3:
                txt = data[i:j].decode("latin1")
                if not txt.startswith("[CAM_UTIL_ADJ]"):
                    otros.append((BASE_VADDR + i, txt))
            i = j + 1
        assert otros == []


# ---------------------------------------------------------------- referencias
class TestReferenciasPic:
    def test_todas_referenciadas_y_una_sola_vez(self):
        data = _data()
        pic = _pic_index(data)
        for va in CADENAS:
            sites = pic.get(va, [])
            assert len(sites) == 1, f"{hex(va)} referenciada {len(sites)} veces"
            assert sites[0] == SITIOS[va], (
                f"{hex(va)}: sitio {hex(sites[0])} != {hex(SITIOS[va])}")

    def test_aritmetica_ldr_add_verificada_a_mano(self):
        """destino = pool + (direccion_del_add + 4), recalculado byte a mano."""
        data = _data()
        for va, site in SITIOS.items():
            # el `add rX,pc` esta en `site`; se busca hacia atras el `ldr rX,[pc,#imm]`
            # mas cercano con el MISMO registro (regla estricta), dentro de 4 KB.
            add_h = _u16(data, site)
            assert (add_h & 0xFF00) == 0x4400 and ((add_h >> 3) & 0xF) == 15
            reg = (((add_h >> 7) & 1) << 3) | (add_h & 7)
            found = None
            for ldr in range(site - 2, site - 2 - 32, -2):
                h = _u16(data, ldr)
                if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
                    lit = ((ldr + 4) & ~3) + ((h & 0xFF) * 4)
                    found = (ldr, _u32(data, lit))
                    break
                if (h & 0xFF7F) == 0xF85F:
                    h2 = _u16(data, ldr + 2)
                    if (h2 >> 12) & 0xF == reg:
                        lit = ((ldr + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
                        found = (ldr, _u32(data, lit))
                        break
            assert found is not None, f"sin ldr r{reg} antes de {hex(site)}"
            ldr, pool = found
            dest = (pool + (site + 4)) & 0xFFFFFFFF
            assert dest == va, f"sitio {hex(site)} apunta a {hex(dest)} != {hex(va)}"

    def test_sitios_dentro_de_las_tres_funciones(self):
        data = _data()
        pro = _prologues(data)
        for va, site in SITIOS.items():
            f = _fstart(pro, site)
            assert f in FUNCIONES, f"{hex(site)} cae en {hex(f)}"


# ------------------------------------------------------------------ funciones
class TestFunciones:
    def test_prologos_y_entradas(self):
        data = _data()
        # 0x439007b0 : push.w {r4,r5,r6,r7,r8,lr}
        assert _u16(data, 0x439007B0) == 0xE92D
        assert _u16(data, 0x439007B2) & 0x4000
        # 0x43900a24 : push.w {r0..r8,lr}
        assert _u16(data, 0x43900A24) == 0xE92D
        assert _u16(data, 0x43900A26) & 0x4000
        # 0x43900c44 : push {r4,r5,r6,r7,lr}
        assert _u16(data, 0x43900C44) == 0xB5F0

    def test_reparto_de_trazas_por_funcion(self):
        data = _data()
        pic = _pic_index(data)
        pro = _prologues(data)
        counts = {}
        for va in CADENAS:
            f = _fstart(pro, pic[va][0])
            counts[f] = counts.get(f, 0) + 1
        assert counts == {f: n for f, (_n, n) in FUNCIONES.items()}, counts

    def test_llamadas_sin_apis_de_obturador_iris_iso(self):
        """Ninguna de las 3 funciones llama a una API de obturador/iris/ISO."""
        data = _data()
        rangos = [(0x439007B0, 0x439008B0), (0x43900A24, 0x43900BE0),
                  (0x43900C44, 0x43900D30)]
        permitidos = {
            0x43900728, 0x4390092C, 0x439009C8, 0x439009F0, 0x43900C1C,
            0x439023B8, 0x439008CC, 0x43561260, 0x435612EC, 0x43B2A0CE,
            0x43B2A0B2, 0x439C5320, 0x439C5A04,
        }
        for lo, hi in rangos:
            for _site, tgt in _bl_targets(data, lo, hi):
                assert tgt in permitidos, (
                    f"llamada inesperada a {hex(tgt)} en [{hex(lo)},{hex(hi)})")

    def test_vocabulario_sin_obturador_iris_iso_wb(self):
        """Ninguna traza del modulo (ni de sus 3 funciones) nombra shutter/iris/ISO/WB."""
        data = _data()
        for va, texto in CADENAS.items():
            bajo = texto.lower()
            for palabra in ("shutter", "iris", "iso", "wb", "whitebal",
                            "exposure", "aperture", "speed"):
                assert palabra not in bajo, f"{hex(va)} menciona {palabra}"


# ------------------------------------------------------------------- despacho
class TestDespacho:
    def test_entradas_de_la_tabla(self):
        data = _data()
        for va, (w0, w1) in DESPACHO.items():
            assert _u32(data, va) == w0, f"campo0 en {hex(va)}"
            assert _u32(data, va + 4) == w1, f"puntero en {hex(va)}"

    def test_indice_1_apunta_a_la_funcion_de_tabla(self):
        data = _data()
        assert (_u32(data, 0x44012204) & ~1) == 0x439007B0

    def test_indices_0_y_2_apuntan_al_stub(self):
        data = _data()
        assert (_u32(data, 0x440121FC) & ~1) == 0x43B2A0B8
        assert (_u32(data, 0x4401220C) & ~1) == 0x43B2A0B8

    def test_el_puntero_del_callback_esta_registrado(self):
        data = _data()
        assert _u32(data, 0x4401F7A4) == 0x43900A25

    def test_pic_de_la_tabla_de_despacho(self):
        """El `ldr`/`add` de 0x43900b98 computa 0x440121f8."""
        data = _data()
        ldr = 0x43900B98
        h = _u16(data, ldr)
        assert (h & 0xF800) == 0x4800
        lit = ((ldr + 4) & ~3) + ((h & 0xFF) * 4)
        pool = _u32(data, lit)
        assert (pool + (0x43900B9A + 4)) & 0xFFFFFFFF == 0x440121F8


# --------------------------------------------------------------- tabla "Sens"
class TestTablaSens:
    def test_a6000_entradas_clave(self):
        rows = {c: (s, t) for c, s, t in _sens_table(BIN_PATH)}
        for cmd, (size, txt) in SENS_CLAVES.items():
            assert cmd in rows, f"falta el cmd {hex(cmd)}"
            assert rows[cmd] == (size, txt), f"cmd {hex(cmd)}: {rows[cmd]}"

    def test_a6000_tiene_51_entradas(self):
        rows = _sens_table(BIN_PATH)
        assert len(rows) == 51
        assert rows[0][0] == 0x0400015D
        assert rows[-1][0] == 0x0400018F

    def test_mismos_cmd_y_size_en_los_tres_firmwares(self):
        a = [(c, s) for c, s, _t in _sens_table(BIN_PATH)]
        b = [(c, s) for c, s, _t in _sens_table(A7S_BIN)]
        c = [(c, s) for c, s, _t in _sens_table(A6300_BIN)]
        assert a == b, "A6000 y A7S difieren en la tabla Sens"
        assert a == c, "A6000 y A6300 difieren en la tabla Sens"

    def test_textos_identicos_en_los_tres_firmwares(self):
        a = dict((c, t) for c, _s, t in _sens_table(BIN_PATH))
        b = dict((c, t) for c, _s, t in _sens_table(A7S_BIN))
        c = dict((c, t) for c, _s, t in _sens_table(A6300_BIN))
        for cmd in SENS_CLAVES:
            assert a[cmd] == b[cmd] == c[cmd], f"texto distinto en {hex(cmd)}"

    def test_unica_diferencia_de_texto_en_la_tabla(self):
        a = dict((c, t) for c, _s, t in _sens_table(BIN_PATH))
        b = dict((c, t) for c, _s, t in _sens_table(A7S_BIN))
        c = dict((c, t) for c, _s, t in _sens_table(A6300_BIN))
        dif_a7s = {k: (a[k], b[k]) for k in a if a[k] != b[k]}
        dif_a6300 = {k: (a[k], c[k]) for k in a if a[k] != c[k]}
        assert dif_a7s == {0x04000167: ("Reserved", "POFF return")}, dif_a7s
        assert dif_a6300 == {0x04000167: ("Reserved", "POFF return")}, dif_a6300

    def test_27_cadenas_sens_en_los_tres(self):
        for path in (BIN_PATH, A7S_BIN, A6300_BIN):
            d = _data(path)
            ss = [m.group()[:-1].decode("latin1")
                  for m in re.finditer(rb"Sens:[ -~]{0,60}\x00", d)]
            assert len(ss) == 27, f"{path}: {len(ss)} cadenas Sens:*"


# ------------------------------------------------------------------ diferencial
class TestDiferencial:
    def test_token_ausente_en_a7s_y_a6300(self):
        assert _data(A7S_BIN).count(TOKEN) == 0
        assert _data(A6300_BIN).count(TOKEN) == 0
        assert _data(BIN_PATH).count(TOKEN) == 22

    def test_interiores_ausentes_en_a7s_y_a6300(self):
        def texts(path):
            d = _data(path)
            return set(m.group()[:-1].decode("latin1")
                       for m in re.finditer(rb"[ -~]{4,300}\x00", d))
        interiores = [t.replace("[CAM_UTIL_ADJ]:", "").strip()
                      for t in CADENAS.values()]
        assert len(interiores) == 22
        for path in (A7S_BIN, A6300_BIN):
            ts = texts(path)
            assert not [x for x in interiores if x in ts], path

    def test_marcadores_auxiliares_ausentes_en_los_otros(self):
        for pat in (b"tsk_cam_adjctrl", b"cam_adjcmd_handle_cb", b"SensRamAcs",
                    b"Senser RAM Access", b"-- Table Write", b"-- Table Read",
                    b"OriginalCmdCode", b"OriginalDataSize", b"OriginalBDataSize",
                    b"[CAM_UTIL]", b"[CAM_UTIL_SENS]", b"[CAMERA_ADJ]"):
            assert _data(BIN_PATH).count(pat) > 0, f"{pat} no esta en la A6000"
            assert _data(A7S_BIN).count(pat) == 0, f"{pat} aparece en A7S"
            assert _data(A6300_BIN).count(pat) == 0, f"{pat} aparece en A6300"


# ------------------------------------------------------------------- relaciones
class TestRelaciones:
    def test_tsk_cam_adjctrl_llama_al_gestor_de_cam_util_sens(self):
        data = _data()
        tgts = [t for _s, t in _bl_targets(data, 0x43900C44, 0x43900D30)]
        assert 0x439023B8 in tgts, "tsk_cam_adjctrl no llama a [CAM_UTIL_SENS]"
        assert _cstr(data, 0x43CCE63D) == \
            "[CAM_UTIL_SENS]: UTIL MS Mgr) Call CB [Flg]%x"

    def test_el_indice_de_despacho_es_r5(self):
        """El indice de la tabla de despacho se toma de r5 (semivariable +0x1e)."""
        data = _data()
        assert _u16(data, 0x43900B8C) == 0x2D02, "cmp r5,#2"
        assert _u16(data, 0x43900B90) == 0x2D01, "cmp r5,#1"
        assert _u16(data, 0x43900B86) == 0x2B01, "cmp r3,#1 (r7-0xfe en {0,1})"

    def test_el_log_recibe_los_argumentos_de_sens_ram_access(self):
        """Traza 7: 'CMD %x, Block %x' <- u16@+0x1a y u16@+0x18."""
        data = _data()
        assert _u16(data, 0x43900A5E) == 0x8B43, "ldrh r3,[r0,#0x1a]"
        assert _u16(data, 0x43900A62) == 0x8B03, "ldrh r3,[r0,#0x18]"

    def test_el_stub_de_no_soportado_devuelve_respuesta_vacia(self):
        """0x43b2a0b8 pone {8,7,cmd,0,0} en la estructura de respuesta."""
        data = _data()
        assert _u16(data, 0x43B2A0B8) == 0x8842, "ldrh r2,[r0,#2]"
        assert _u16(data, 0x43B2A0BC) == 0x2108, "movs r1,#8"
        assert _u16(data, 0x43B2A0C0) == 0x3907, "subs r1,#7"


# ----------------------------------------------------------------------- json
class TestJson:
    def test_json_consistente_con_los_bytes(self):
        data = _data()
        j = _json()
        assert j["milestone"] == "S140"
        assert j["modulo"] == "[CAM_UTIL_ADJ]"
        assert j["contadores"]["cadenas"] == 22
        assert j["contadores"]["cadenas_con_referencia"] == 22
        assert j["contadores"]["sitios"] == 22
        assert j["contadores"]["funciones"] == 3
        assert {int(c["vaddr"], 16): c["text"] for c in j["cadenas"]} == CADENAS
        assert {int(c["vaddr"], 16) for c in j["cadenas"]} == set(CADENAS)
        assert {int(f["func"], 16): f["n_trazas"] for f in j["funciones"]} == {
            f: n for f, (_x, n) in FUNCIONES.items()}
        for c in j["cadenas"]:
            assert c["n_sites"] == 1
            assert int(c["sites"][0]["site"], 16) == SITIOS[int(c["vaddr"], 16)]
            assert c["sites"][0]["verificado_a_mano"] is True
        assert {int(d["vaddr"], 16): d for d in j["tabla_despacho"]}.keys() == \
            set(DESPACHO)
