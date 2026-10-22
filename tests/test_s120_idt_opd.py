"""S120 — `[IDT_OPD]`: la segunda instancia del módulo IDT (mapas de imagen).

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos, recuentos y
layouts concretos.  Ningún test es tautológico: si cambia una dirección, un texto o un
contador en el binario, el test falla.

Ver `analysis/s120_idt_opd/idt_opd.md`.
"""

import json
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
PREFIX = b"[IDT_OPD]"

# Rango de código donde vive el módulo IDT (contiene los 725 sitios de referencia).
IDT_CODE = (0x439D0000, 0x43A09000)


@pytest.fixture(scope="module")
def data():
    return (ROOT / BIN_PATH).read_bytes()


@pytest.fixture(scope="module")
def a7s():
    p = ROOT / A7S_BIN
    if not p.exists():
        pytest.skip("blob de la A7S no disponible")
    return p.read_bytes()


@pytest.fixture(scope="module")
def a6300():
    p = ROOT / A6300_BIN
    if not p.exists():
        pytest.skip("blob de la A6300 no disponible")
    return p.read_bytes()


def _cstr(data, vaddr, maxlen=300):
    """Cadena terminada en NUL en `vaddr` (puede contener '\\n')."""
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = data.find(b"\x00", off, off + maxlen)
    assert end > off, f"cadena sin NUL en {hex(vaddr)}"
    return data[off:end].decode("latin1")


def _tokens(data, prefix):
    """(vaddr, texto hasta NUL) de cada aparición del prefijo."""
    out = []
    idx = 0
    while True:
        i = data.find(prefix, idx)
        if i < 0:
            break
        idx = i + 1
        e = data.find(b"\x00", i)
        if e < 0:
            e = len(data)
        out.append((BASE_VADDR + i, data[i:e].decode("latin1")))
    return out


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _ldr_imm(data, site):
    """Decodifica `ldr/ldrh/ldrb rX, [rY, #imm]` (T1 de Thumb) -> (offset, rn, rd)."""
    h = _u16(data, site)
    if (h & 0xF800) == 0x6800:        # ldr  (palabra)
        return ((h >> 6) & 0x1F) * 4, (h >> 3) & 7, h & 7
    if (h & 0xF800) == 0x8800:        # ldrh (media palabra)
        return ((h >> 6) & 0x1F) * 2, (h >> 3) & 7, h & 7
    if (h & 0xF800) == 0x7800:        # ldrb (byte)
        return (h >> 6) & 0x1F, (h >> 3) & 7, h & 7
    raise AssertionError(f"{hex(site)} no es ldr/ldrh/ldrb de 16 bits: {h:#06x}")


def _ldr_imm32(data, site):
    """Decodifica `ldrh.w rX, [rY, #imm]` (T3 de Thumb-2) -> (offset, rn, rt)."""
    h1 = _u16(data, site)
    h2 = _u16(data, site + 2)
    assert (h1 & 0xFFF0) == 0xF8B0, f"{hex(site)} no es ldrh.w T3: {h1:#06x}"
    u = 1 if (h1 & 0x80) else -1
    return (h2 & 0xFFF) * u, h1 & 0xF, (h2 >> 12) & 0xF


def _pic_target(data, add_site):
    """Destino materializado por el `add rX, pc` de `add_site` (esquema PIC)."""
    h = _u16(data, add_site)
    assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15, hex(add_site)
    rd = ((h >> 7) & 1) << 3 | (h & 7)
    for k in range(1, 10):
        la = add_site - 2 * k
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


def _json():
    with open(ROOT / "analysis" / "s120_idt_opd" / "idt_opd.json", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------- módulo
class TestModulo:
    def test_274_ocurrencias_del_prefijo(self, data):
        assert data.count(PREFIX) == 274

    def test_274_textos_distintos(self, data):
        toks = _tokens(data, PREFIX)
        assert len(toks) == 274
        assert len({t for _, t in toks}) == 274

    def test_rango_de_la_tabla(self, data):
        toks = _tokens(data, PREFIX)
        assert toks[0][0] == 0x43CF11F9
        assert toks[-1][0] == 0x43CF57F1
        assert toks[0][1] == "[IDT_OPD]: SEND MESSAGE alloc ERROR"
        assert toks[-1][1] == "[IDT_OPD]: MovieDepthRate illegal"

    def test_el_rango_es_contiguo(self, data):
        """Entre el primer y el último token `[IDT_OPD]` no hay otros módulos."""
        toks = _tokens(data, PREFIX)
        lo, hi = toks[0][0], toks[-1][0]
        otros = re.findall(rb"\[([A-Za-z0-9_]{2,20})\]", data[lo - BASE_VADDR:hi - BASE_VADDR])
        otros = {o.decode() for o in otros}
        assert otros == {"IDT", "IDT_OPD"}, otros

    def test_cada_tiene_gemelo_idt_contiguo(self, data):
        """Las 274 trazas OPD van seguidas, byte a byte, de su gemelo `[IDT]`."""
        checked = 0
        for vaddr, text in _tokens(data, PREFIX):
            core = text[len("[IDT_OPD]"):]
            twin = vaddr + len(text) + 1
            assert _cstr(data, twin) == "[IDT]" + core, hex(vaddr)
            checked += 1
        assert checked == 274

    def test_una_traza_no_empieza_en_el_token(self, data):
        """`0x43cf274a` es el token dentro de una cadena precedida por una tabla de offsets."""
        assert _cstr(data, 0x43CF274A) == "[IDT_OPD]: CCinitParam addr null"
        tabla = data[0x43CF273F - BASE_VADDR:0x43CF274A - BASE_VADDR]
        assert tabla == bytes((0x04, 0x08, 0x0C, 0x10, 0x15, 0x1B,
                               0x20, 0x24, 0x28, 0x2C, 0x30))


# ------------------------------------------------------------------ textos clave
class TestTextosClave:
    ESPERADOS = {
        0x43CF1DC3: "[IDT_OPD]: ie_miniraw.adrs Err:%X",
        0x43CF1E03: "[IDT_OPD]: backImgData.adrs Err:%X",
        0x43CF1E45: "[IDT_OPD]: imgmap.adrs Err:%X",
        0x43CF1E7D: "[IDT_OPD]: ie_out.adrs Err:%X",
        0x43CF1EB5: "[IDT_OPD]: refmap.adrs Err:%X",
        0x43CF1EED: "[IDT_OPD]: tar_num Err:%d",
        0x43CF1F1D: "[IDT_OPD]: isSpectRef Err:%d",
        0x43CF1F53: "[IDT_OPD]: isMapOut Err:%d",
        0x43CF20C3: "[IDT_OPD]: ie_offset Err:%d",
        0x43CF20F7: "[IDT_OPD]: ie_imgwidth Err:%d",
        0x43CF212F: "[IDT_OPD]: ie_imgheight Err:%d",
        0x43CF2169: "[IDT_OPD]: ie_imgaddnum Err:%d",
        0x43CF21A3: "[IDT_OPD]: ie_aspect Err:%d",
        0x43CF23AF: "[IDT_OPD]: lc_miniraw.adrs Err:%X",
        0x43CF23EF: "[IDT_OPD]: lc_out.adrs Err:%X",
        0x43CF2427: "[IDT_OPD]: lc_offset Err:%d",
        0x43CF2BB6: "[IDT_OPD]: miniraw.adrs Err:%X",
        0x43CF2BF0: "[IDT_OPD]: shade_map.adrs Err:%X",
        0x43CF2C2E: "[IDT_OPD]: 4cmap.adrs Err:%X",
        0x43CF2C64: "[IDT_OPD]: histmap.adrs Err:%X",
        0x43CF2C9E: "[IDT_OPD]: summap.adrs Err:%X",
        0x43CF2CD6: "[IDT_OPD]: out_opd_cc.adrs Err:%X",
        0x43CF2D16: "[IDT_OPD]: out_opd_ec.adrs Err:%X",
        0x43CF2D84: "[IDT_OPD]: imgwidth Err:%d",
        0x43CF3EC8: "[IDT_OPD]: VATR Error det:%x gle:%x",
        0x43CF40E0: "[IDT_OPD]: miniRAW Addr  : %08x",
        0x43CF4545: "[IDT_OPD]: 4cmap:%X",
        0x43CF4569: "[IDT_OPD]: hmap:%X",
        0x43CF458B: "[IDT_OPD]: smap:%X",
        0x43CF45AD: "[IDT_OPD]: ccout:%X",
        0x43CF45D1: "[IDT_OPD]: ecout:%X",
        0x43CF45F5: "[IDT_OPD]: shade:%X",
        0x43CF4619: "[IDT_OPD]: input:%X",
        0x43CF463D: "[IDT_OPD]: msain0:%X",
        0x43CF4663: "[IDT_OPD]: msain1:%X",
        0x43CF4689: "[IDT_OPD]: msaout:%X",
        0x43CF46AF: "[IDT_OPD]: ieout:%X",
        0x43CF46D3: "[IDT_OPD]: p_img_map:%X",
        0x43CF46FF: "[IDT_OPD]: p_backImgData:%X",
        0x43CF4733: "[IDT_OPD]: ie_in:%X",
        0x43CF4757: "[IDT_OPD]: mapRC_in:%X",
        0x43CF4781: "[IDT_OPD]: lc_out:%X",
        0x43CF47A7: "[IDT_OPD]: lc_in:%X",
        0x43CF47CB: "[IDT_OPD]: refmap:%X",
    }

    @pytest.mark.parametrize("vaddr,texto", sorted(ESPERADOS.items()))
    def test_texto_en_su_direccion(self, data, vaddr, texto):
        assert _cstr(data, vaddr) == texto, hex(vaddr)

    def test_los_18_punteros_del_volcado(self, data):
        """`0x439f85d4` vuelca 18 punteros con estos nombres, en este orden."""
        esperado = ["4cmap", "hmap", "smap", "ccout", "ecout", "shade", "input",
                    "msain0", "msain1", "msaout", "ieout", "p_img_map",
                    "p_backImgData", "ie_in", "mapRC_in", "lc_out", "lc_in", "refmap"]
        vaddr = 0x43CF4545
        for nombre in esperado:
            texto = _cstr(data, vaddr)
            assert texto == f"[IDT_OPD]: {nombre}:%X", hex(vaddr)
            # el gemelo [IDT] va justo detrás
            gem = _cstr(data, vaddr + len(texto) + 1)
            assert gem == f"[IDT]: {nombre}:%X", hex(vaddr)
            vaddr += len(texto) + 1 + len(gem) + 1


# ------------------------------------------------------------------ estructuras
class TestEstructuraIE:
    """Bloque IE (IE_CCinit) validado en 0x439e80c8: los offsets salen de los bytes."""

    # (instrucción, offset, base, nombre del campo según la traza que lo nombra)
    CAMPOS = [
        (0x439E80CE, 0x54, 0, "ie_miniraw"),
        (0x439E80D4, 0x78, 0, "backImgData"),
        (0x439E80D8, 0x74, 0, "imgmap"),
        (0x439E80DC, 0x70, 0, "ie_out"),
        (0x439E80E0, 0x10, 0, "refmap"),
        (0x439E81BE, 0x0C, 4, "isSpectRef"),
        (0x439E81C4, 0x0D, 4, "isMapOut"),
    ]

    @pytest.mark.parametrize("site,offset,base,nombre", CAMPOS)
    def test_offsets_del_bloque_ie(self, data, site, offset, base, nombre):
        """`ldr rX, [rB, #offset]` en el sitio indicado (rB = r0 o r4, que copia r0)."""
        off, rn, _rd = _ldr_imm(data, site)
        assert off == offset, f"{nombre}: offset real 0x{off:x} != 0x{offset:x}"
        assert rn == base, f"{nombre}: base r{rn} != r{base}"
        # r4 = r0 (`mov r4, r0` = 0x4604 en 0x439e80ca)
        assert data[0x439E80CA - BASE_VADDR:0x439E80CC - BASE_VADDR] == bytes((0x04, 0x46))

    def test_tar_num_es_u16_en_el_offset_0(self, data):
        off, rn, _rd = _ldr_imm(data, 0x439E8188)
        assert off == 0 and rn == 4        # ldrh r3, [r4]
        assert _u16(data, 0x439E818A) & 0x00FF == 0x0F   # cmp r3, #0xf

    def test_ie_offset_ies_campos_de_16_bits(self, data):
        """`ie_imgwidth/height/addnum/aspect` se leen con ldrh.w (0x5c/0x5e/0x60/0x62)."""
        for site, offset in ((0x439E8448, 0x5C), (0x439E8394, 0x5E),
                             (0x439E847C, 0x60), (0x439E84B2, 0x62)):
            off, rn, _rt = _ldr_imm32(data, site)
            assert off == offset, hex(site)
            assert rn == 4, hex(site)

    def test_ie_offset_es_de_32_bits(self, data):
        off, rn, _rd = _ldr_imm(data, 0x439E8356)
        assert off == 0x58 and rn == 4

    def test_los_ganos_r_g_b_son_de_16_bits(self, data):
        """r/g/b val.high|low en 0x16, 0x18, 0x1c, 0x1e, 0x22, 0x24."""
        for site, offset in ((0x439E8218, 0x16), (0x439E821A, 0x18),
                             (0x439E8270, 0x1C), (0x439E8272, 0x1E),
                             (0x439E82C8, 0x22), (0x439E82CA, 0x24)):
            off, rn, _rd = _ldr_imm(data, site)
            assert off == offset, hex(site)
            assert rn == 4, hex(site)


class TestEstructuraMAP:
    """Bloque MAP validado en 0x439ee7e8 (offsets leídos de los bytes)."""

    CAMPOS = [
        (0x439EE7F0, 0x0C, "miniraw"),
        (0x439EE7F6, 0x38, "shade_map"),
        (0x439EE7FA, 0x3C, "4cmap"),
        (0x439EE7FE, 0x40, "histmap"),
        (0x439EE802, 0x44, "summap"),
        (0x439EE806, 0x48, "out_opd_cc"),
        (0x439EE80A, 0x4C, "out_opd_ec"),
    ]

    @pytest.mark.parametrize("site,offset,nombre", CAMPOS)
    def test_offsets_del_bloque_map(self, data, site, offset, nombre):
        off, rn, _rd = _ldr_imm(data, site)
        assert off == offset, f"{nombre}: offset real 0x{off:x} != 0x{offset:x}"
        assert rn == 0, f"{nombre}: base r{rn} != r0"

    def test_geometria_16_bits(self, data):
        """Geometría del bloque MAP: imgwidth/height/addnum/aspect y x/y sel/span."""
        for site, offset in ((0x439EE90C, 0x14), (0x439EE910, 0x16),
                             (0x439EEA22, 0x18), (0x439EEA52, 0x1A),
                             (0x439EEAFC, 0x2A), (0x439EEB56, 0x2C),
                             (0x439EEB02, 0x2E), (0x439EEC1E, 0x30)):
            off, rn, _rd = _ldr_imm(data, site)
            assert off == offset, hex(site)
            assert rn == 4, hex(site)


class TestVolcadoPunteros:
    """`0x439f85d4`: los punteros salen de bloques globales concretos."""

    def test_bases_globales(self, data):
        """El volcado parte de 0x43f41b30, 0x43f41cbc, 0x43f418a8 y 4 globales sueltos."""
        for site, esperado in ((0x439F85DE, 0x43F41B30), (0x439F869A, 0x43F41BBC),
                               (0x439F86BA, 0x43F41EF0), (0x439F86DA, 0x43F41AD8),
                               (0x439F86FA, 0x43F41CBC), (0x439F876E, 0x43F41F14),
                               (0x439F878E, 0x43F418A8), (0x439F87CA, 0x43F4189C)):
            assert _pic_target(data, site) == esperado, hex(site)

    def test_offsets_de_los_campos(self, data):
        """`ldr r3, [r4, #off]` con r4 = 0x43f41b30 y los offsets del bloque MAP."""
        for site, offset in ((0x439F85E0, 0x3C), (0x439F85F6, 0x40), (0x439F8612, 0x44),
                             (0x439F862E, 0x48), (0x439F864A, 0x4C), (0x439F8666, 0x38),
                             (0x439F8682, 0x54), (0x439F8702, 0x28), (0x439F871E, 0x2C),
                             (0x439F873A, 0x30), (0x439F8756, 0x38), (0x439F8796, 0x28),
                             (0x439F87B2, 0x30)):
            off, rn, _rd = _ldr_imm(data, site)
            assert off == offset, hex(site)
            assert rn == 4, hex(site)


class TestCodigo:
    """El código del módulo y su decodificación PIC."""

    def test_pic_verificado_a_mano(self, data):
        """`ldr r3,[pc,#0x210]` @0x439f85e4 + `add r3,pc` @0x439f85e6 -> 0x43cf4545."""
        h = _u16(data, 0x439F85E4)
        assert (h & 0xF800) == 0x4800
        assert ((h >> 8) & 7) == 3            # r3
        assert (h & 0xFF) * 4 == 0x210
        pool = ((0x439F85E4 + 4) & ~3) + 0x210
        assert pool == 0x439F87F8
        w = _u32(data, pool)
        assert w == 0x002FBF5B
        assert (w + 0x439F85E6 + 4) & 0xFFFFFFFF == 0x43CF4545
        assert _cstr(data, 0x43CF4545) == "[IDT_OPD]: 4cmap:%X"

    def test_entre_ldr_y_add_no_se_reescribe_el_registro(self, data):
        """Nada entre el `ldr r3` y el `add r3,pc` (bytes 0x439f85e4..0x439f85e6)."""
        assert data[0x439F85E4 - BASE_VADDR:0x439F85E6 - BASE_VADDR] == bytes(
            (0x84, 0x4B))

    def test_la_misma_funcion_emite_los_dos_prefijos(self, data):
        """`0x439f85d4` referencia '[IDT_OPD]: 4cmap:%X' y '[IDT]: 4cmap:%X'."""
        assert _cstr(data, 0x43CF4545) == "[IDT_OPD]: 4cmap:%X"
        assert _cstr(data, 0x43CF4559) == "[IDT]: 4cmap:%X"
        # el `add r3,pc` (0x439f85e6) y el `add r0,pc` (0x439f85f0) están en la misma función
        assert 0x439F85E6 < 0x439F85F0 < 0x439F9000

    def test_canales_de_salida(self, data):
        """El emisor de mensaje estructurado (0x9a bytes) y el printf de consola."""
        # 0x439f80b8: `movs r2, #0x9a` (tamaño del registro de mensaje)
        assert _u16(data, 0x439F80D2) & 0xFF == 0x9A
        # 0x439e80fa: `movs r0, #6` / `movs r1, #2` (módulo y comando)
        assert _u16(data, 0x439E80FA) & 0xFF == 6
        assert _u16(data, 0x439E80FC) & 0xFF == 2


# ------------------------------------------------------------------ referencias
class TestReferencias:
    def test_las_3_trazas_sin_referencia(self, data):
        """Comprobado con el barrido PIC (canónico y kill corregido): las mismas 3."""
        import sys
        sys.path.insert(0, str(ROOT / "analysis" / "s120_idt_opd"))
        import scan_idt_code_pic as SC
        from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs
        starts = SC.string_starts(data, 0x0, 0xFFFFFFFF)
        toks = {f"0x{v:x}" for v, _ in _tokens(data, PREFIX)}
        for detail in (False, True):
            md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
            md.detail = detail
            res = SC.scan(data, IDT_CODE[0], IDT_CODE[1], starts, md)
            con = {f"0x{k:x}" for k in res}
            assert len(con & toks) == 271, f"detail={detail}"
            sin = sorted(toks - con)
            assert sin == ["0x43cf150f", "0x43cf1557", "0x43cf274a"], sin

    def test_los_textos_de_las_3_muertas(self, data):
        assert _cstr(data, 0x43CF150F) == "[IDT_OPD]: Can't use sync release CB!"
        assert _cstr(data, 0x43CF1557) == "[IDT_OPD]: No time for 2imager"
        assert _cstr(data, 0x43CF274A) == "[IDT_OPD]: CCinitParam addr null"


# ------------------------------------------------------------------ relaciones
class TestRelacionesConOtrosModulos:
    def test_imaging_cap_dispara_el_kick_fopd(self, data):
        assert _cstr(data, 0x43CADD2D) == "[IMAGING_CAP]: StartRdraw_Prelight: KickFOPD error"
        assert _cstr(data, 0x43CADD60) == "[IMAGING_CAP]: StartRdraw_Read: KickFOPD error"
        assert _cstr(data, 0x43CADD8F) == "[IMAGING_CAP]: StartRdraw_AfterCap: KickFOPD error"

    def test_syncresmgr_gestiona_el_recurso_idt_opd(self, data):
        assert _cstr(data, 0x43C9C2FC) == (
            "[CAMERA_MAIN_SYNC]: SyncResMgr::Get: IDT_OPD_TOP_Sync_OPDAcquire error!")
        assert _cstr(data, 0x43CB0F3E) == "[CAMERA_MAIN_SYNC]: SyncResMgr::Get IDT_OPD failure"

    def test_tabla_de_recursos(self, data):
        """RESOURCE_IDT_OPD / IDT_VOT / IDT_TOP / IMAGER, en ese orden."""
        i = data.find(b"RESOURCE_IDT_OPD")
        assert BASE_VADDR + i == 0x43C9C461
        ventana = data[i - 0x60:i + 0x60].decode("latin1")
        assert "RESOURCE_IDT_OPD" in ventana
        assert "RESOURCE_IDT_VOT" in ventana
        assert "RESOURCE_IDT_TOP" in ventana
        assert "RESOURCE_IMAGER" in ventana

    def test_el_idt_corre_en_hs3_cpu0(self, data):
        assert "HS3@CPU0(IDT)" in _cstr(data, 0x43CA12F6)

    def test_lc_consume_el_miniraw(self, data):
        assert _cstr(data, 0x43C9C8BA) == (
            "[CAMERA_MAIN_LC]: [LC] Movie DM AF cannot get miniRAW Stored memhandle")

    def test_camcore_libera_el_vatr(self, data):
        assert "SplitEEController: Memory Close Error!(VATR)" in _cstr(data, 0x43C90982)

    def test_el_imager_no_nombra_el_idt(self, data):
        """Ningún módulo `[CAM_IMAGER]` menciona IDT/OPD."""
        for m in re.finditer(rb"\[CAM_IMAGER\][ -~]*", data):
            texto = m.group().decode("latin1")
            assert "IDT" not in texto and "OPD" not in texto

    def test_los_nombres_de_los_mapas_solo_existen_en_el_bloque_idt(self, data):
        """`4cmap`, `shade_map`, `summap`, `histmap`… solo aparecen en la tabla del módulo."""
        for nombre in (b"4cmap", b"shade_map", b"summap", b"histmap", b"backImgData",
                       b"p_img_map", b"msain0", b"msaout", b"ie_out", b"imgmap"):
            for m in re.finditer(re.escape(nombre), data):
                v = BASE_VADDR + m.start()
                assert 0x43CF11F9 <= v <= 0x43CF5810, (nombre, hex(v))


# ------------------------------------------------------------------ diferencial
class TestDiferencial:
    def test_a7s_no_tiene_el_prefijo_opd(self, a7s):
        assert a7s.count(PREFIX) == 0
        assert a7s.count(b"[IDT]") == 306

    def test_a6300_no_tiene_el_prefijo_opd(self, a6300):
        assert a6300.count(PREFIX) == 0
        assert a6300.count(b"[IDT]") == 382

    def test_a7s_tiene_el_recurso_idt_opd(self, a7s):
        i = a7s.find(b"RESOURCE_IDT_OPD")
        assert i > 0
        assert i == 0x761B67, hex(i)
        ventana = a7s[i - 0x60:i + 0x60].decode("latin1")
        for otro in ("RESOURCE_IDT_VOT", "RESOURCE_IDT_TOP", "RESOURCE_IMAGER"):
            assert otro in ventana

    def test_a7s_tiene_los_comandos_idt_opd_top(self, a7s):
        assert b"IDT_OPD_TOP_Sync_OPDAcquire" in a7s
        assert b"IDT_OPD_TOP_Sync_SetFOPD" in a7s

    def test_270_mensajes_comunes_texto_a_texto(self, data, a7s):
        """Comparación exacta (no por subcadena) de los 274 mensajes con la A7S."""
        comunes = 0
        for _, texto in _tokens(data, PREFIX):
            core = texto[len("[IDT_OPD]"):]
            if core in {t[len("[IDT]"):] for _, t in _tokens(a7s, b"[IDT]")}:
                comunes += 1
        assert comunes == 270

    def test_4_mensajes_solo_en_la_a6000(self, data, a7s):
        a7s_cores = {t[len("[IDT]"):] for _, t in _tokens(a7s, b"[IDT]")}
        solo = [t[len("[IDT_OPD]"):] for _, t in _tokens(data, PREFIX)
                if t[len("[IDT_OPD]"):] not in a7s_cores]
        assert solo == [
            ": det:xs:%d xe:%d ys:%d ye:%d ",
            ": Sync rate %d -> %d use:%d mode:%d %d %d",
            ": test %d %d %d %d %d %d %d %d %d %d",
            ": test2 %d %d %d %d %d %d %d %d",
        ]

    def test_36_mensajes_solo_en_la_a7s(self, data, a7s):
        a6_cores = {t[len("[IDT_OPD]"):] for _, t in _tokens(data, PREFIX)}
        solo = {t[len("[IDT]"):] for _, t in _tokens(a7s, b"[IDT]")} - a6_cores
        assert len(solo) == 36
        for frag in (": PBL SET_FUNC ERROR. R0.", ": PBL AIF_START ERROR. W2.",
                     ": KICK FOPD %d %d", ": calc_miniraw cycle err %d %d"):
            assert frag in solo, frag


# ------------------------------------------------------------------ json
class TestJsonEntregable:
    def test_contadores_del_json(self):
        j = _json()
        c = j["counts"]
        assert c["trazas_idt_opd"] == 274
        assert c["tokens_idt_opd_en_el_binario"] == 274
        assert c["funciones"] == 165
        assert c["cadenas_con_referencia"] == 271
        assert c["cadenas_sin_referencia"] == 3
        assert c["gemelos_idt_contiguos"] == 274
        assert c["sub_bloques"] == 25
        assert c["a7s_traces_idt_opd"] == 0
        assert c["a7s_traces_idt"] == 306
        assert c["a7s_comunes_texto"] == 270
        assert c["a6300_traces_idt_opd"] == 0
        assert c["a6300_traces_idt"] == 382

    def test_las_274_trazas_del_json_coinciden_con_los_bytes(self, data):
        j = _json()
        assert len(j["strings"]) == 274
        for s in j["strings"]:
            v = int(s["vaddr"], 16)
            assert _cstr(data, v) == s["text"], s["vaddr"]

    def test_los_subbloques_cubren_las_274_trazas(self):
        j = _json()
        total = sum(b["n"] for b in j["subblocks"])
        assert total == 274
        assert len(j["subblocks"]) == 25
        for b in j["subblocks"]:
            assert b["n"] > 0

    def test_estructuras_publicadas(self):
        j = _json()
        ie = {c["campo"]: c["offset"] for c in j["estructuras"]["IE"]["campos"]}
        assert ie["ie_miniraw (adrs)"] == "0x54"
        assert ie["ie_imgwidth"] == "0x5c"
        assert ie["backImgData (adrs)"] == "0x78"
        mp = {c["campo"]: c["offset"] for c in j["estructuras"]["MAP"]["campos"]}
        assert mp["4cmap (adrs)"] == "0x3c"
        assert mp["histmap (adrs)"] == "0x40"
        assert mp["summap (adrs)"] == "0x44"
        assert mp["out_opd_cc (adrs)"] == "0x48"
