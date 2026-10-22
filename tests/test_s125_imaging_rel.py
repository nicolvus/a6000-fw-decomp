"""S125 — los módulos de trazas `[IMAGING_REL]` (31) y `[IMAGING]` (120) de la A6000 fw3.21.

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos, recuentos,
referencias PIC y el diferencial A7S/A6300.  Ningún test es tautológico: si cambia una
dirección, un texto o un contador en el binario, el test falla.

Ver `analysis/s125_imaging_rel/imaging_rel.md`.
"""

import pathlib
import re
import struct

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)

REL_TOKEN = b"[IMAGING_REL]"
IMG_TOKEN = b"[IMAGING]:"
CAP_TOKEN = b"[IMAGING_CAP]:"
MAX_LDR_GAP = 4096          # ventana del esquema PIC (regla estricta canónica)


# --------------------------------------------------------------------- utilidades
def _cstr(data, vaddr, maxlen=400):
    """Cadena terminada en NUL que empieza en `vaddr` (puede contener '\\n')."""
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = data.find(b"\x00", off, off + maxlen)
    assert end > off, f"cadena sin NUL en {hex(vaddr)}"
    return data[off:end].decode("latin1")


def _tokens(data, token):
    """[(vaddr, texto hasta NUL)] de cada aparición de `token`."""
    out = []
    idx = 0
    while True:
        i = data.find(token, idx)
        if i < 0:
            break
        idx = i + 1
        e = data.find(b"\x00", i)
        if e < 0:
            e = len(data)
        out.append((BASE_VADDR + i, data[i:e].decode("latin1")))
    return out


def _string_set(data):
    """Conjunto de cadenas completas del blob (para comparaciones texto a texto)."""
    out = set()
    i = 0
    n = len(data)
    while i < n:
        if 32 <= data[i] < 127:
            e = data.find(b"\x00", i)
            if e < 0:
                e = n
            if e > i:
                out.add(data[i:e].decode("latin1"))
                i = e + 1
                continue
        i += 1
    return out


def _find_string(data, texto):
    """Offset de la cadena **completa** `texto` en el blob (-1 si no existe)."""
    pat = texto.encode("latin1")
    i = data.find(pat)
    while i >= 0:
        if (i == 0 or data[i - 1] == 0) and data[i + len(pat)] == 0:
            return i
        i = data.find(pat, i + 1)
    return -1


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _pic_map(data):
    """Mapa completo de referencias PIC (regla estricta canónica).

    Devuelve {vaddr_destino: [vaddr_sitio_add, ...]} para los destinos que caen en el
    **inicio** de una cadena NUL-terminada imprimible.
    """
    n = len(data)

    # 1) inicios de cadena
    starts = set()
    prev_print = False
    for i in range(n):
        cur = 32 <= data[i] < 127
        if cur and not prev_print:
            starts.add(BASE_VADDR + i)
        prev_print = cur

    # 2) ldr rX,[pc,#imm] y add rX,pc
    ldrs = []
    adds = []
    for a in range(BASE_VADDR, BASE_VADDR + n - 6, 2):
        h = struct.unpack_from("<H", data, a - BASE_VADDR)[0]
        if (h & 0xF800) == 0x4800:
            ldrs.append((a, (h >> 8) & 7, ((a + 4) & ~3) + (h & 0xFF) * 4))
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", data, a + 2 - BASE_VADDR)[0]
            ldrs.append((a, (h2 >> 12) & 0xF,
                         ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, ((h >> 7) & 1) << 3 | (h & 7)))

    by_reg = {}
    for a, reg, pool in ldrs:
        by_reg.setdefault(reg, []).append((a, pool))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}

    out = {}
    for a, reg in adds:
        lst = by_reg.get(reg)
        if not lst:
            continue
        ks = keys[reg]
        lo, hi = 0, len(ks)
        while lo < hi:
            mid = (lo + hi) // 2
            if ks[mid] <= a:
                lo = mid + 1
            else:
                hi = mid
        if lo == 0:
            continue
        la, pool = lst[lo - 1]
        if a - la > MAX_LDR_GAP:
            continue
        if not (BASE_VADDR <= pool <= BASE_VADDR + n - 4):
            continue
        tgt = (struct.unpack_from("<I", data, pool - BASE_VADDR)[0] + (a + 4)) & 0xFFFFFFFF
        if tgt in starts:
            out.setdefault(tgt, []).append(a)
    return {k: sorted(v) for k, v in sorted(out.items())}


def _pic_target(data, add_site):
    """Destino materializado por el `add rX, pc` de `add_site` (esquema PIC).

    Empareja con el `ldr rX,[pc,#imm]` MÁS CERCANO por detrás (regla estricta canónica).
    """
    h = _u16(data, add_site)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(add_site)
    rd = ((h >> 7) & 1) << 3 | (h & 7)
    for k in range(1, 2049):
        la = add_site - 2 * k
        if la < BASE_VADDR:
            break
        hh = _u16(data, la)
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == rd:
            pool = ((la + 4) & ~3) + (hh & 0xFF) * 4
            return (_u32(data, pool) + (add_site + 4)) & 0xFFFFFFFF
        if (hh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, la + 2)
            if (h2 >> 12) == rd:
                pool = ((la + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
                return (_u32(data, pool) + (add_site + 4)) & 0xFFFFFFFF
    raise AssertionError(f"no hay ldr pc que preceda a {hex(add_site)}")


# ------------------------------------------------------------------------ fixtures
@pytest.fixture(scope="module")
def data():
    return (ROOT / BIN_PATH).read_bytes()


@pytest.fixture(scope="module")
def pic(data):
    return _pic_map(data)


@pytest.fixture(scope="module")
def a7s():
    p = ROOT / A7S_BIN
    if not p.exists():
        pytest.skip("blob de la A7S no disponible")
    return p.read_bytes()


@pytest.fixture(scope="module")
def pic_a7s(a7s):
    return _pic_map(a7s)


@pytest.fixture(scope="module")
def a6300():
    p = ROOT / A6300_BIN
    if not p.exists():
        pytest.skip("blob del A6300 no disponible")
    return p.read_bytes()


# ------------------------------------------------------------------- [IMAGING_REL]
class TestImagingRel:
    def test_31_ocurrencias_del_token(self, data):
        assert data.count(REL_TOKEN) == 31

    def test_31_textos_distintos(self, data):
        toks = _tokens(data, REL_TOKEN)
        assert len(toks) == 31
        assert len({t for _, t in toks}) == 31

    def test_rango_del_modulo(self, data):
        toks = _tokens(data, REL_TOKEN)
        assert toks[0][0] == 0x43C9C520
        assert toks[-1][0] == 0x43CB4BC4
        assert toks[0][1] == "[IMAGING_REL]: Spinal) osal_free_timer: err %x"
        assert toks[-1][1] == "[IMAGING_REL]: NoMprCap InnerRp Clear!!"

    def test_todas_llevan_prefijo_y_espacio(self, data):
        for vaddr, text in _tokens(data, REL_TOKEN):
            assert text.startswith("[IMAGING_REL]: "), (hex(vaddr), text)

    def test_textos_fijos_en_direcciones_fijas(self, data):
        esperados = {
            0x43CA3887: "[IMAGING_REL]: (%d,%d,%d)",
            0x43CA5319: "[IMAGING_REL]: RelKey) %02d: %02d",
            0x43CA533B: "[IMAGING_REL]: it is a strange trig in IsNeedForceS1ON : %d",
            0x43CA5377: "[IMAGING_REL]: remote capture cancel due to camuser's release lock",
            0x43CA53BA: "[IMAGING_REL]: Unknown REL_EVT (%02X)",
            0x43CA53E0: "[IMAGING_REL]: RelMgr) <ExecMsg> CLEAR_INNER_RP_CAPID_IDX %d",
            0x43CA541D: "[IMAGING_REL]: RelMgr) <ExecMsg> CLEAR_INNER_RP %d",
            0x43CA5450: "[IMAGING_REL]: RelMgr) Invalid RelLock Factor %08x",
            0x43CAFD53: "[IMAGING_REL]: NotifyEEStartEnable (%08X)",
            0x43CB4549: "[IMAGING_REL]: CapIdTblMgr) Initialize irp(%x), cidx(%x), "
                        "rp(%x), wp(%x), wpd(%x), dm(%x)",
            0x43CB47AA: "[IMAGING_REL]: CapIdTblMgr) GetCaptureID           "
                        "irp(%x), cidx(%x), rp(%x), wp(%x), wpd(%x), dm(%x)",
            0x43CB48D2: "[IMAGING_REL]: RelQueue) err. queue is empty (PopBack)",
            0x43CB4909: "[IMAGING_REL]: RelQueue) err. queue is empty (PopFront)",
            0x43CB4941: "[IMAGING_REL]: RelQueue) err. queue is full (PushFront)",
            0x43CB4979: "[IMAGING_REL]: RelQueue) err. queue is full (PushBack)",
            0x43CB49B0: "[IMAGING_REL]: CapIdTblMgrIf) StartAccess Cmp To %08X",
            0x43CB4A1E: "[IMAGING_REL]: CapIdTblMgrIf) Init End",
            0x43CB4B21: "[IMAGING_REL]: CapIdTblMgrIf) pop queue StartAccess From %08X",
            0x43CB4B80: "[IMAGING_REL]: RelLock) You may forget to hold down the LOCK key...",
            0x43CB4BC4: "[IMAGING_REL]: NoMprCap InnerRp Clear!!",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_rel_equivale_a_release_por_los_nombres_rtti(self, data):
        """`REL` está expandido en el firmware: la clase C++ es `Camera::ReleaseLock`."""
        rtti = {
            0x43CA5483: "N6Camera11ReleaseLock9RelLockS1E",
            0x43CA54A4: "N6Camera11ReleaseLock11RelLockBaseE",
            0x43CB4B5F: "N6Camera11ReleaseLock9RelLockS2E",
            0x43CB4810: "N6Camera11ReleaseLock9RingQueueINS0_7Wrapper10msg_headerELi10EEE",
            0x43CB4889: "N6Camera11ReleaseLock9RingQueueIjLi10EEE",
            0x43CB4851: "N6Camera11ReleaseLock5QueueINS0_7Wrapper10msg_headerEEE",
            0x43CB48B2: "N6Camera11ReleaseLock5QueueIjEE",
        }
        for vaddr, nombre in rtti.items():
            assert _cstr(data, vaddr) == nombre, hex(vaddr)

    def test_el_fichero_fuente_es_spinal_cpp(self, data):
        assert _cstr(data, 0x43C9C54F) == "Spinal.cpp"
        assert _pic_target(data, 0x4372A9B6) == 0x43C9C54F
        assert _pic_target(data, 0x4372AA04) == 0x43C9C54F

    def test_referencias_pic_de_las_trazas_clave(self, data):
        """Comprobación a mano de los sitios PIC de cinco trazas del módulo."""
        assert _pic_target(data, 0x4379D14A) == 0x43CA5319      # RelKey) %02d: %02d
        assert _pic_target(data, 0x43792A64) == 0x43CA3887      # (%d,%d,%d)
        assert _pic_target(data, 0x4381C356) == 0x43CB4549      # CapIdTblMgr) Initialize
        assert _pic_target(data, 0x4379E186) == 0x43CA53BA      # Unknown REL_EVT (%02X)
        assert _pic_target(data, 0x4381D13E) == 0x43CB4BC4      # NoMprCap InnerRp Clear!!

    def test_la_cadena_spinal_esta_muerta(self, pic):
        """`0x43c9c520` no tiene ninguna referencia PIC en todo el binario."""
        assert pic.get(0x43C9C520, []) == []

    def test_despachador_rel_evt_tabla_de_salto(self, data):
        """`0x4379d83a` es el despachador de `REL_EVT`: ids 0x01..0x27 con `tbh`."""
        assert _u16(data, 0x4379D83E) == 0x1E5A        # subs r2, r3, #1
        assert _u16(data, 0x4379D84C) == 0x2A26        # cmp r2, #0x26
        h = _u16(data, 0x4379D852)
        assert (h & 0xFF00) == 0xE800                  # tbh [pc, r2, lsl #1]

    def test_relqueue_emite_cada_error_en_dos_sitios(self, pic):
        """Cada mensaje de `RelQueue)` tiene dos sitios PIC (Pop/Push x Front/Back)."""
        esperados = {
            0x43CB48D2: [0x4381C950, 0x4381CAA4],
            0x43CB4909: [0x4381C9A0, 0x4381CAF0],
            0x43CB4941: [0x4381C9F8, 0x4381CB44],
            0x43CB4979: [0x4381CA50, 0x4381CB94],
        }
        for vaddr, sitios in esperados.items():
            assert pic.get(vaddr, []) == sitios, hex(vaddr)

    def test_capidtblmgrif_emite_las_ocho_trazas_en_una_funcion(self, pic):
        esperados = {
            0x43CB49B0: 0x4381CCCE, 0x43CB49E6: 0x4381CD3E, 0x43CB4A1E: 0x4381CD7E,
            0x43CB4A45: 0x4381CDB6, 0x43CB4A7C: 0x4381CDEA, 0x43CB4AB3: 0x4381CE2A,
            0x43CB4AEA: 0x4381CE5E, 0x43CB4B21: 0x4381CEAA,
        }
        for vaddr, sitio in esperados.items():
            assert pic.get(vaddr, []) == [sitio], hex(vaddr)

    def test_30_de_31_cadenas_referenciadas(self, pic):
        """Solo la cadena muerta de `Spinal)` queda sin referencia."""
        sin_ref = [v for v, _ in _tokens(open(ROOT / BIN_PATH, "rb").read(), REL_TOKEN)
                   if not pic.get(v, [])]
        assert sin_ref == [0x43C9C520]


# ----------------------------------------------------------------------- [IMAGING]
class TestImaging:
    def test_120_ocurrencias_del_prefijo(self, data):
        assert data.count(IMG_TOKEN) == 120

    def test_120_textos_distintos(self, data):
        toks = _tokens(data, IMG_TOKEN)
        assert len(toks) == 120
        assert len({t for _, t in toks}) == 120

    def test_rango_del_modulo(self, data):
        toks = _tokens(data, IMG_TOKEN)
        assert toks[0][0] == 0x43C9B47C
        assert toks[-1][0] == 0x43CC6C99
        assert toks[0][1] == "[IMAGING]: FATAL! %s:%d"
        assert toks[-1][1] == "[IMAGING]: [PanoramaResize] End  err: 0x%08x"

    def test_las_120_cadenas_empiezan_en_el_token(self, data):
        """El token `[IMAGING]:` no aparece anidado dentro de otra cadena."""
        for vaddr, text in _tokens(data, IMG_TOKEN):
            assert data[vaddr - BASE_VADDR - 1] == 0x00, hex(vaddr)
            assert text.startswith("[IMAGING]: "), (hex(vaddr), text)

    def test_la_cadena_con_nl_esta_contada(self, data):
        """`[IMAGING]: %s:%d \n` contiene un 0x0A: no se pierde al escanear."""
        assert data.count(b"[IMAGING]: %s:%d \n") == 1
        assert _cstr(data, 0x43CABAFB) == "[IMAGING]: %s:%d \n"

    def test_textos_fijos_en_direcciones_fijas(self, data):
        esperados = {
            0x43C9B47C: "[IMAGING]: FATAL! %s:%d",
            0x43C9E546: "[IMAGING]: [seqSRotateCallBack] ercd: 0x%08x",
            0x43C9E573: "[IMAGING]: [seqStitchCallBack] ercd: 0x%08x",
            0x43C9E59F: "[IMAGING]: [seqClippingDecCallback] ercd: 0x%08x",
            0x43C9E5D0: "[IMAGING]: [seq_panoramaClippingDecode] cmp_decode Err: "
                        "0x%08x : %s:%d",
            0x43C9EC01: "[IMAGING]: [seq_panoramaParallelStitch][OK] StitchProc ALL OK : %s:%d",
            0x43C9F6D9: "[IMAGING]: FATAL! %s:%d [0x%x]",
            0x43CAAFA1: "[IMAGING]: [cmp_fill] Err: 0x%08x : %s:%d",
            0x43CAB054: "[IMAGING]: [PanoramaSweepStart] Err: 0x%08x : %s:%d",
            0x43CAB144: "[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x : %s:%d",
            0x43CAB176: "[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x, status: 0x%08x",
            0x43CAB1B0: "[IMAGING]: [PanoramaSweepEnd] Err! %s:%d",
            0x43CAB1D9: "[IMAGING]: [PanoramaSweepEnd] cmp_execStitchPreProcess() Err! %s:%d",
            0x43CAB21D: "[IMAGING]: [PanoramaSweepEnd] cmp_checkFillResidual() Err! %s:%d",
            0x43CAB74D: "[IMAGING]: [allocOutputArea] Size over!: data[0x%08x] "
                        "ram[0x%08x]: %s:%d",
            0x43CAC052: "[IMAGING]: [Jpeg Close Callback] ercd: 0x%08x",
            0x43CC680C: "[IMAGING]: [ddls_srotate_sa_start_cb] SA DRV Err: 0x%08x : %s:%d",
            0x43CC69BF: "[IMAGING]: [PanoramaStitch] UnitOpen() Err: 0x%08x : %s:%d",
            0x43CC6B87: "[IMAGING]: [PanoramaResize] UnitOpen() Err: 0x%08x : %s:%d",
            0x43CC6C99: "[IMAGING]: [PanoramaResize] End  err: 0x%08x",
        }
        for vaddr, texto in esperados.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_el_modulo_no_se_solapa_con_imaging_cap(self, data):
        """Las 697 trazas de `[IMAGING_CAP]:` (S106) y las 120 de `[IMAGING]:` son disjuntas."""
        assert data.count(CAP_TOKEN) == 697
        cap = {v for v, _ in _tokens(data, CAP_TOKEN)}
        img = {v for v, _ in _tokens(data, IMG_TOKEN)}
        assert cap & img == set()

    def test_fatal_generico_tiene_443_sitios(self, pic):
        """`[IMAGING]: FATAL! %s:%d` es el macro `FATAL!` de todo el subsistema de captura."""
        sitios = pic.get(0x43C9B47C, [])
        assert len(sitios) == 443
        assert sitios[0] == 0x43549056
        assert 0x437E6B6A not in sitios          # ese sitio es de PanoramaSweepStart

    def test_referencias_pic_de_las_trazas_de_panorama(self, data):
        assert _pic_target(data, 0x437E6B6A) == 0x43CAB054      # PanoramaSweepStart Err
        assert _pic_target(data, 0x437E7090) == 0x43CAB176      # PanoramaSweepEnd Err: status
        assert _pic_target(data, 0x437E7124) == 0x43CAB1D9      # cmp_execStitchPreProcess
        assert _pic_target(data, 0x437E737E) == 0x43CAB21D      # cmp_checkFillResidual
        assert _pic_target(data, 0x43781E3C) == 0x43C9EC01      # StitchProc ALL OK
        assert _pic_target(data, 0x437804B8) == 0x43C9E546      # seqSRotateCallBack

    def test_82_cadenas_referenciadas_y_38_muertas(self, data, pic):
        referenciadas = [v for v, _ in _tokens(data, IMG_TOKEN) if pic.get(v, [])]
        muertas = [v for v, _ in _tokens(data, IMG_TOKEN) if not pic.get(v, [])]
        assert len(referenciadas) == 82
        assert len(muertas) == 38
        assert min(muertas) == 0x43C9E634
        assert max(muertas) == 0x43CC6C99

    def test_las_38_muertas_ya_lo_estaban_en_la_a7s(self, data, a7s, pic, pic_a7s):
        """Las 38 cadenas de `[IMAGING]` sin referencia ya estaban muertas en la A7S fw3.20."""
        muertas = [v for v, _ in _tokens(data, IMG_TOKEN) if not pic.get(v, [])]
        assert len(muertas) == 38
        for v in muertas:
            texto = _cstr(data, v)[len("[IMAGING]: "):]
            off = _find_string(a7s, texto)
            assert off >= 0, (hex(v), texto)          # el texto existe en la A7S
            assert pic_a7s.get(BASE_VADDR + off, []) == [], (hex(v), texto)

    def test_codigo_de_las_trazas_nuevas_de_la_fw321(self, pic):
        for vaddr, esperado in ((0x43CAB176, 9), (0x43CAB1B0, 8),
                                (0x43CAB1D9, 1), (0x43CAB21D, 1), (0x43C9EC01, 1)):
            assert len(pic.get(vaddr, [])) == esperado, hex(vaddr)


# ------------------------------------------------------------------- diferencial
class TestDiferencial:
    def test_la_a7s_no_etiqueta_nada(self, a7s):
        assert a7s.count(b"[IMAGING") == 0
        assert a7s.count(b"[IMAGING_REL]") == 0
        assert a7s.count(b"[IMAGING]:") == 0

    def test_el_a6300_no_etiqueta_nada(self, a6300):
        assert a6300.count(b"[IMAGING") == 0
        assert a6300.count(b"[IMAGING_REL]") == 0

    def test_115_de_120_imaging_existen_sin_prefijo_en_la_a7s(self, data, a7s):
        cadenas7 = _string_set(a7s)
        toks = _tokens(data, IMG_TOKEN)
        comunes = [t for _, t in toks if t[len("[IMAGING]: "):] in cadenas7]
        assert len(comunes) == 115

    def test_las_5_nuevas_de_la_fw321_no_existen_en_la_a7s(self, data, a7s):
        cadenas7 = _string_set(a7s)
        nuevas = {
            "[PanoramaSweepEnd] Err: 0x%08x, status: 0x%08x",
            "[PanoramaSweepEnd] Err! %s:%d",
            "[PanoramaSweepEnd] cmp_execStitchPreProcess() Err! %s:%d",
            "[PanoramaSweepEnd] cmp_checkFillResidual() Err! %s:%d",
            "[seq_panoramaParallelStitch][OK] StitchProc ALL OK : %s:%d",
        }
        for texto in nuevas:
            assert texto not in cadenas7, texto

    def test_30_de_31_imaging_rel_existen_sin_prefijo_en_la_a7s(self, data, a7s):
        cadenas7 = _string_set(a7s)
        toks = _tokens(data, REL_TOKEN)
        comunes = [t for _, t in toks if t[len("[IMAGING_REL]: "):] in cadenas7]
        assert len(comunes) == 30
        assert "[IMAGING_REL]: (%d,%d,%d)" not in comunes

    def test_22_de_31_imaging_rel_existen_en_el_a6300(self, data, a6300):
        cadenas = _string_set(a6300)
        toks = _tokens(data, REL_TOKEN)
        comunes = [t for _, t in toks if t[len("[IMAGING_REL]: "):] in cadenas]
        assert len(comunes) == 22

    def test_mensajes_propios_del_a6300(self, a6300):
        assert a6300.count(b"CapIdTblMgr) SetMprInitEnd irp(%x)") == 1
        assert a6300.count(b"CapIdTblMgrIf) Unknown massage") == 1

    def test_el_a6300_tiene_la_clase_release_lock(self, a6300):
        assert a6300.count(b"N6Camera11ReleaseLock9RelLockS2E") == 1

    def test_el_a6300_no_tiene_la_traza_de_la_tecla(self, a6300):
        assert a6300.count(b"RelKey) %02d: %02d") == 0


# ------------------------------------------------------------- contexto y relación
class TestContexto:
    def test_camcore_no_usa_estas_etiquetas(self, data):
        """`[IMAGING_REL]`/`[IMAGING]` no aparecen dentro de `[IMAGING_CAP]` ni al revés."""
        for vaddr, text in _tokens(data, CAP_TOKEN):
            assert "[IMAGING]" not in text and "[IMAGING_REL]" not in text, hex(vaddr)

    def test_rel_evty_lock_conviven(self, data):
        """Las piezas de release que S61 ya conocía están en este módulo."""
        assert _cstr(data, 0x43CA387E) == "VD_Pre S"
        assert _cstr(data, 0x43CA3C74) == "EV SendSpinalON:LIROSeq"
        assert _cstr(data, 0x43C9C54F) == "Spinal.cpp"

    def test_ficheros_fuente_de_la_zona_de_panorama(self, data):
        assert _cstr(data, 0x43CACF07) == "Stage_Panorama.cpp"
        assert _cstr(data, 0x43CC6964) == "ddl_stitch.cpp"
        assert data.count(b"src/srotate/ddl_srotate.cpp") == 1
        assert data.count(b"still_cnt_panoramaSweep.cpp") == 1
        assert data.count(b"still_seq_panoramaStitch.cpp") == 1
        assert data.count(b"still_cnt_panoramaStitch.cpp") == 1

    def test_el_motor_de_secciones_solo_emite_el_fatal_generico(self, pic):
        """Los 17 manejadores de S114 no emiten ningún mensaje específico de `[IMAGING]`."""
        manejadores = [0x437EABFC, 0x437EB144, 0x437EA8CC, 0x437EB24C, 0x437E9D78,
                       0x437EA178, 0x437EAA5C, 0x437EA034, 0x437EAF38, 0x437EA410,
                       0x437EAD4C, 0x437EAB64, 0x437E9A70, 0x437EA724, 0x437E9BE8,
                       0x437EB470, 0x437EA2BC]
        assert len(manejadores) == 17
        # ninguna cadena de `[IMAGING]` específica está referenciada desde 0x437e9a70..0x437eb470
        especificas = [0x43C9E546, 0x43C9E573, 0x43C9E59F, 0x43C9E5D0, 0x43C9EC01,
                        0x43CAB054, 0x43CAB144, 0x43CAB176, 0x43CAB1B0, 0x43CAB1D9,
                        0x43CAB21D, 0x43CAC052, 0x43CC69BF, 0x43CC6C99]
        for v in especificas:
            for sitio in pic.get(v, []):
                assert not (0x437E9A70 <= sitio < 0x437EB500), (hex(v), hex(sitio))
