"""Tests for S121 — `[AIP]` (Audio IP de la cámara).

Tests de **bytes reales**: leen el firmware, resuelven los punteros PIC y comprueban
direcciones, textos y recuentos. Regla estricta: para cada `add rX, pc` se toma el
`ldr rX, [pc, #imm]` más cercano hacia atrás sobre el mismo registro y
destino = valor_del_pool + (dir_add + 4).
"""

import json
import pathlib
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
PREFIX = "[AIP]"

# las 37 cadenas: vaddr -> (texto, sitio PIC)
TRAZAS = {
    0x43CDD844: ("[AIP]SA OpenConfigCb Ack", 0x43926D2C),
    0x43CDD85E: ("[AIP]SA OpenConfigCb Ack Err errCode %x errState %x", 0x43926D4A),
    0x43CDD893: ("[AIP]SA OpenConfigCb Comp", 0x43926D7A),
    0x43CDD8AE: ("[AIP]SA OpenConfigCb Comp Err errCode %x errState %x", 0x43926D98),
    0x43CDD8E4: ("[AIP]SA OpenConfigCb Err", 0x43926DB4),
    0x43CDD8FE: ("[AIP]SA CloseConfigCb Done", 0x43926DF8),
    0x43CDD91A: ("[AIP]SA CloseCallback Err errCode %x errState %x", 0x43926E16),
    0x43CDD94C: ("[AIP]SA CloseCallback Err uniqueId %x ", 0x43926E42),
    0x43CDD9E3: ("[AIP][SA ANR MGR]SetAudioNrType %x", 0x4392732A),
    0x43CDDAB5: ("[AIP]SetFader m_fader.count %x", 0x4355AF04),
    0x43CDE67A: ("[AIP]SaBackUpCtrl::UnREG CB OK", 0x4392A722),
    0x43CDE69A: ("[AIP]SaBackUpCtrl::UnREG CB err %d", 0x4392A73A),
    0x43CDE6BE: ("[AIP]SaBackUpCtrl GetBackUp err bkId %x", 0x4392A7B0),
    0x43CDE77B: ("[AIP]SaBackUpCtrl::CreateBackUpLpsList Err", 0x4392A9CA),
    0x43CDE7A7: ("[AIP]SaBackUpCtrl::Init Sa OK id num = %d", 0x4392AA46),
    0x43CDE7D2: ("[AIP]SaBackUpCtrl::Init Sa err %d", 0x4392AA5C),
    0x43CDE7F5: ("[AIP]SaBackUpCtrl::Init Lps OK id num = %d", 0x4392AA86),
    0x43CDE821: ("[AIP]SaBackUpCtrl::Init Lps err %d", 0x4392AA9C),
    0x43CDE845: ("[AIP]SaBackUpCtrl::REG CB OK", 0x4392AAEC),
    0x43CDE863: ("[AIP]SaBackUpCtrl::REG CB err %d", 0x4392AB04),
    0x43CDE885: ("[AIP]SaBackUpCtrl::WriteShadow2BakcupArea OK id num = %d", 0x4392AB8E),
    0x43CDE8BF: ("[AIP]SaBackUpCtrl::WriteShadow2BackupArea err %d", 0x4392ABA4),
    0x43CDE900: ("[AIP]Sa OpenConfig Cmd %x Func %x", 0x4392AC3A),
    0x43CDE923: ("[AIP]Zma %x Ext %x Mbx %x", 0x4392AC46),
    0x43CDE957: ("[AIP]Sa Close Cmd %x Func %x Unq %x", 0x4392ACBE),
    0x43CDE97C: ("[AIP]SaDriver CloseConfig", 0x4392ACE4),
    0x43CDEA9E: ("[AIP]LPS OpenConfigCb Ack", 0x4392B17C),
    0x43CDEAB9: ("[AIP]LPS OpenConfigCb Ack Err errCode %x errState %x", 0x4392B19A),
    0x43CDEAEF: ("[AIP]Lps OpenConfigCb Comp OK", 0x4392B1CE),
    0x43CDEB0E: ("[AIP]LPS OpenConfigCb Comp ErrCode %x ErrStatus %x", 0x4392B1F8),
    0x43CDEB63: ("[AIP]LPS CloseConfigCb Comp", 0x4392B25E),
    0x43CDEB80: ("[AIP]LPS CloseCallback Err errCode %x errState %x", 0x4392B27C),
    0x43CDEBB3: ("[AIP]LPS CloseCallback Err uniqueId %x ", 0x4392B2A8),
    0x43CDEBDC: ("[AIP]LPS SetMailBox Err", 0x4392B416),
    0x43CDEC04: ("[AIP]LPS GetMailBox Err", 0x4392B4DE),
    0x43CDEC1C: ("[AIP]LPS GetMb Callback TimeOut Err", 0x4392B512),
    0x43CDEC50: ("[AIP]LPS SetLpsSysv Err", 0x4392B6AC),
}


def _data():
    with open(ROOT / BIN_PATH, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=300):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _strings(data):
    out = []
    start = 0
    while True:
        i = data.find(PREFIX.encode(), start)
        if i < 0:
            break
        end = i
        while end < len(data) and 32 <= data[end] < 127:
            end += 1
        out.append((BASE_VADDR + i, data[i:end].decode("latin1")))
        start = i + 1
    return out


def _u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE_VADDR)[0]


def _u32(data, vaddr):
    return struct.unpack_from("<I", data, vaddr - BASE_VADDR)[0]


def _pic_target(data, site, maxgap=0x20):
    """Destino PIC de un `add rX,pc` con la regla estricta (ldr mismo registro)."""
    h = _u16(data, site)
    assert (h & 0xFFF8) == 0x4478, f"{hex(site)} no es add rX,pc"
    reg = h & 7
    for gap in range(2, maxgap + 1, 2):
        hh = _u16(data, site - gap)
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == reg:
            pool = ((site - gap + 4) & ~3) + (hh & 0xFF) * 4
            return (_u32(data, pool) + site + 4) & 0xFFFFFFFF
    raise AssertionError(f"sin ldr resoluble para {hex(site)}")


def _bl_target(data, site):
    """Destino de un `bl` Thumb-2 (32 bits) en `site`."""
    h1 = _u16(data, site)
    h2 = _u16(data, site + 2)
    assert (h1 & 0xF800) == 0xF000 and (h2 & 0x8000) == 0x8000, hex(h1)
    s = (h1 >> 10) & 1
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    i1 = (~(j1 ^ s)) & 1
    i2 = (~(j2 ^ s)) & 1
    off = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
    if off & (1 << 24):
        off -= 1 << 25
    return (site + 4 + off) & 0xFFFFFFFF


def _json(name="aip.json"):
    with open(ROOT / "analysis" / "s121_aip" / name, encoding="utf-8") as fh:
        return json.load(fh)


class TestModulo:
    def test_conteo_de_trazas(self):
        assert len(_strings(_data())) == 37

    def test_rango_y_offsets(self):
        data = _data()
        ss = _strings(data)
        assert hex(ss[0][0]) == "0x43cdd844"
        assert hex(ss[-1][0]) == "0x43cdec50"
        assert ss[0][0] - BASE_VADDR == 0x79C844
        assert ss[-1][0] - BASE_VADDR == 0x79DC50

    @pytest.mark.parametrize("vaddr", sorted(TRAZAS))
    def test_texto_en_su_direccion(self, vaddr):
        texto, _ = TRAZAS[vaddr]
        assert _cstr(_data(), vaddr) == texto, hex(vaddr)

    @pytest.mark.parametrize("vaddr", sorted(TRAZAS))
    def test_sitio_pic_resuelve_a_la_cadena(self, vaddr):
        _, site = TRAZAS[vaddr]
        assert _pic_target(_data(), site) == vaddr, hex(site)

    def test_ninguna_cadena_muerta(self):
        data = _data()
        ss = _strings(data)
        assert len({site for _, site in TRAZAS.values()}) == len(ss) == 37

    def test_la_etiqueta_es_aip_en_las_37(self):
        assert all(t.startswith(PREFIX) for _, t in _strings(_data()))


class TestFalsosPositivos:
    """Los dos casos extremos y los dos destinos no-cadena de la kill analysis."""

    def test_falso_positivo_de_0x4355bcb2(self):
        data = _data()
        site = 0x4355BCB2
        assert _pic_target(data, site) == 0x43CEB58B
        assert _cstr(data, 0x43CEB58B).startswith("SA_PARAM_APL_LGR_YRATIO_SET_FIELD!")

    def test_sitio_real_de_reg_cb_err(self):
        assert _pic_target(_data(), 0x4392AB04) == 0x43CDE863

    def test_setfader_si_es_verdadero(self):
        data = _data()
        assert _pic_target(data, 0x4355AF04) == 0x43CDDAB5
        assert _u16(data, 0x4355AEFE) & 0xF800 == 0x4800

    @pytest.mark.parametrize("site,destino", [(0x4392A6F0, 0x43F1C4B4),
                                              (0x4392AF24, 0x43F1C5F4)])
    def test_destino_no_cadena(self, site, destino):
        data = _data()
        assert _pic_target(data, site) == destino
        assert not _cstr(data, destino).isprintable() or len(_cstr(data, destino)) < 3

    def test_cruce_de_familia(self):
        """El `add` de 0x4392a5ac emite [AudioIp]..., no la traza [AIP] Init Sa OK."""
        data = _data()
        tgt = _pic_target(data, 0x4392A5AC)
        assert tgt == 0x43CDE614
        assert _cstr(data, tgt).startswith("[AudioIp]")


class TestEstructura:
    def test_16_funciones(self):
        j = _json()
        assert j["counts"]["functions"] == 16
        assert len(j["functions"]) == 16
        assert sum(f["n"] for f in j["functions"]) == 37

    def test_mapa_funcion_traza(self):
        j = _json()
        m = {f["func"]: f["n"] for f in j["functions"]}
        assert m["0x43926d1c"] == 5
        assert m["0x43926de8"] == 3
        assert m["0x4392aa00"] == 6
        assert m["0x4392b16c"] == 4
        assert m["0x4355ae98"] == 1

    def test_6_subbloques(self):
        j = _json()
        assert j["counts"]["subblocks"] == 6
        por = {s["name"]: s["n"] for s in j["subblocks"]}
        assert por == {"SaWrapper": 8, "SaDriverZoomNr": 1, "SetFader": 1,
                       "SaBackUpCtrl": 12, "SaDriverBase": 4, "LPS": 11}

    def test_contadores_del_escaneo(self):
        j = _json()
        assert j["counts"]["pic_sites_strict"] == 37
        assert j["counts"]["strings_referenced"] == 37
        assert j["counts"]["dead_strings"] == []
        assert j["counts"]["add_rX_pc_image"] == 95599
        assert j["counts"]["add_rX_pc_with_ldr"] == 88158
        assert j["counts"]["targets_in_block"] == 123

    def test_clases_rti_en_el_bloque(self):
        data = _data()
        for s in ("9AudioIpIf", "9SaWrapper", "14SaDriverZoomNr",
                  "12SaBackUpCtrl", "12SaDriverBase", "10SaSysvCtrl",
                  "19SaDriverLinearPhase", "15AudioIpCmdQueue"):
            assert s.encode() in data, s


class TestBackup:
    def test_tabla_de_350_entradas_en_0x43bd1964(self):
        data = _data()
        base = 0x43BD1964
        n = 350
        ids = [_u32(data, base + 12 * i) for i in range(n)]
        assert ids == [0x10C0000 + i for i in range(n)]
        # layout {id u32, offset u32, size u32}: las 12 B siguientes existen y son u32
        assert all(_u32(data, base + 12 * i + 8) > 0 for i in range(n))

    def test_tamano_del_volcado_de_sombra(self):
        """0x4392ab76 hace `mov.w r0,#0x10c` y llama a 0x43561458 con ese tamaño."""
        data = _data()
        h = _u16(data, 0x4392AB76)
        assert (h & 0xFF00) == 0xB500, hex(h)   # prólogo Thumb con push
        assert data[0x4392AB78 - BASE_VADDR:0x4392AB7C - BASE_VADDR] == bytes.fromhex("4ff48670")
        assert _bl_target(data, 0x4392AB82) == 0x43561458


class TestMetodologia:
    def test_kill_analysis_60_37_23(self):
        j = _json()
        k = j["kill_analysis"]
        assert (k["pairs"], k["ok"], k["wrong"]) == (60, 37, 23)
        assert k["wrong_other_string"] + k["wrong_not_string"] == 23
        assert (k["wrong_other_string"], k["wrong_not_string"]) == (21, 2)

    def test_subconjunto_congelado(self):
        j = _json("kill_refs_aip.json")
        assert len(j["pairs"]) == 60
        assert sum(1 for p in j["pairs"] if p["ok"]) == 37


class TestDiferencial:
    def test_a7s_37_identicas(self):
        ruta = ROOT / A7S_BIN
        if not ruta.exists():
            pytest.skip("blob de la A7S no disponible")
        a7s = ruta.read_bytes()
        textos = [t for _, t in _strings(a7s)]
        a6000 = [t for _, t in _strings(_data())]
        assert len(textos) == 37
        # mismo conjunto (el orden difiere: en la A7S el bloque LPS va antes)
        assert sorted(textos) == sorted(a6000)

    def test_a6300_63_con_las_37_de_la_a6000(self):
        ruta = ROOT / A6300_BIN
        if not ruta.exists():
            pytest.skip("blob de la A6300 no disponible")
        a6300 = ruta.read_bytes()
        textos = [t for _, t in _strings(a6300)]
        assert len(textos) == 63
        for _, t in _strings(_data()):
            assert t in textos, t
        extra = [t for t in textos if t not in dict(_strings(_data())).values()]
        assert len(extra) == 26
        assert sum(1 for t in extra if t.startswith("[AIP][ZNR_EE]")) == 25
        assert extra.count("[AIP][ZNR]SetInstanceNumberExec Err %d") == 1


class TestRelaciones:
    def test_no_se_confunde_con_camera_sa(self):
        """Ninguna traza [AIP] menciona la API del acelerador escalar."""
        textos = [t for _, t in _strings(_data())]
        assert not any("sa_func_" in t for t in textos)

    def test_el_adf_es_el_cliente(self):
        data = _data()
        assert _cstr(data, 0x43C26411) == "[ADF][INIT]AUDIOIP INIT COMP"
        for s in (b"AUDIO_IP_CONFIG_TYPE_VGS", b"AUDIO_IP_CONFIG_TYPE_BANDI",
                  b"LinearPhaseSetAip0Print", b"LinearPhaseGetSa0Print",
                  b"LinearPhaseSetSaPrint"):
            assert s in data, s
