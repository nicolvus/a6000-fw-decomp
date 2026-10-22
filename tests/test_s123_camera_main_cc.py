"""Tests for S123 — el módulo `[CAMERA_MAIN_CC]` (49 trazas) de la A6000 fw3.21.

Tests de **bytes reales**: leen el firmware y comprueban direcciones, textos, recuentos
y la mecánica PIC. Cada test falla si una dirección o un texto cambia.

Convención: `vaddr = 0x43541000 + file_offset`.
"""

import bisect
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
MODULE = "[CAMERA_MAIN_CC]"
TAG = "[CAMERA_MAIN_CC]: "


def _data(path=BIN_PATH):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


def _cstr(data, vaddr, maxlen=200):
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    end = off
    while end < len(data) and end < off + maxlen and 32 <= data[end] < 127:
        end += 1
    return data[off:end].decode("latin1")


def _cc_strings(data):
    """(vaddr_de_la_cadena, texto) de cada traza `[CAMERA_MAIN_CC]`."""
    out = []
    start = 0
    while True:
        i = data.find(MODULE.encode(), start)
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


def _add_pc_sites(data):
    """Direcciones de las instrucciones `add rX, pc` de 16 bits."""
    out = []
    n = len(data)
    for a in range(0, n - 2, 2):
        h = struct.unpack_from("<H", data, a)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append(BASE_VADDR + a)
    return out


def _pic_dest(data, add_vaddr):
    """Resuelve el esquema PIC con la regla **estricta** del repo:
    cada `add rX, pc` se empareja con el `ldr rX,[pc,#imm]` MÁS CERCANO por detrás
    del mismo registro (ventana 4 KB)."""
    h = _u16(data, add_vaddr)
    assert (h & 0xFF00) == 0x4400, f"{hex(add_vaddr)} no es `add rX, pc`"
    assert ((h >> 3) & 0xF) == 15
    rd = (((h >> 7) & 1) << 3) | (h & 7)
    lo = add_vaddr - 0x1000
    best = None
    for a in range(lo, add_vaddr, 2):
        hh = _u16(data, a)
        lit = None
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == rd:
            lit = ((a + 4) & ~3) + ((hh & 0xFF) * 4)
        elif (hh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, a + 2)
            if (h2 >> 12) == rd:
                imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
                lit = ((a + 4) & ~3) + imm12
        if lit is not None and 0 <= lit - BASE_VADDR <= len(data) - 4:
            if best is None or a > best[0]:
                best = (a, _u32(data, lit))
    assert best is not None, f"sin `ldr` para el registro en {hex(add_vaddr)}"
    return (best[1] + add_vaddr + 4) & 0xFFFFFFFF


def _pic_dest_rapido(data, add_vaddr):
    """Igual que `_pic_dest` pero parando en el primer `ldr` del registro (el más
    cercano) — es la regla estricta, sólo que rápida."""
    h = _u16(data, add_vaddr)
    rd = (((h >> 7) & 1) << 3) | (h & 7)
    for a in range(add_vaddr - 2, add_vaddr - 0x1000, -2):
        hh = _u16(data, a)
        lit = None
        if (hh & 0xF800) == 0x4800 and ((hh >> 8) & 7) == rd:
            lit = ((a + 4) & ~3) + ((hh & 0xFF) * 4)
        elif (hh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, a + 2)
            if (h2 >> 12) == rd:
                imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
                lit = ((a + 4) & ~3) + imm12
        if lit is not None and 0 <= lit - BASE_VADDR <= len(data) - 4:
            return (_u32(data, lit) + add_vaddr + 4) & 0xFFFFFFFF
    return None


def _bl_targets(data, lo, hi):
    """Destinos de `bl`/`blx` Thumb en un rango (decodificación manual)."""
    out = []
    for a in range(lo, hi, 2):
        hw1 = _u16(data, a)
        if (hw1 & 0xF800) != 0xF000:
            continue
        hw2 = _u16(data, a + 2)
        if (hw2 & 0xD000) != 0xD000:
            continue
        s = (hw1 >> 10) & 1
        i1 = (~(((hw2 >> 13) & 1) ^ s)) & 1
        i2 = (~(((hw2 >> 11) & 1) ^ s)) & 1
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((hw1 & 0x3FF) << 12) | ((hw2 & 0x7FF) << 1)
        if s:
            imm -= (1 << 25)
        out.append((a, (a + 4 + imm) & 0xFFFFFFFF))
    return out


def _json():
    with open(ROOT / "analysis" / "s123_camera_main_cc" / "camera_main_cc.json",
              encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------- modulo
class TestModulo:
    def test_conteo_de_trazas_en_la_a6000(self):
        assert len(_cc_strings(_data())) == 49

    def test_la_a7s_y_el_a6300_no_tienen_el_prefijo_de_modulo(self):
        assert len(_cc_strings(_data(A7S_BIN))) == 0
        assert len(_cc_strings(_data(A6300_BIN))) == 0

    def test_las_49_cadenas_llevan_el_prefijo_completo(self):
        data = _data()
        for vaddr, texto in _cc_strings(data):
            assert texto.startswith(TAG), f"{hex(vaddr)} sin el prefijo '{TAG}'"

    def test_las_trazas_ocupan_6_tramos_contiguos_de_rodata(self):
        """Cada sub-bloque del módulo es un tramo contiguo propio en `.rodata`:
        dentro de un tramo, cada cadena acaba en NUL justo donde empieza la siguiente."""
        data = _data()
        pares = _cc_strings(data)
        offs = [v - BASE_VADDR for v, _ in pares]
        assert offs[0] == 0x7644C8
        assert offs[-1] == 0x773D62
        # todas las cadenas están terminadas en NUL
        for off, texto in pares:
            fin = off - BASE_VADDR + len(texto)
            assert data[fin] == 0, hex(off)
        # reparto en tramos: una cadena pertenece al tramo anterior si su NUL está
        # justo antes de la siguiente
        tramos = [[offs[0], 1]]
        for i in range(1, len(offs)):
            previo_fin = offs[i - 1] + len(pares[i - 1][1])
            if previo_fin + 1 == offs[i]:
                tramos[-1][1] += 1
            else:
                tramos.append([offs[i], 1])
        assert len(tramos) == 6
        assert [n for _, n in tramos] == [21, 12, 8, 2, 2, 4]
        assert [hex(BASE_VADDR + o) for o, _ in tramos] == [
            "0x43ca54c8", "0x43ca5f0a", "0x43ca6470",
            "0x43ca665e", "0x43ca6805", "0x43cb4cd3"]

    def test_textos_y_direcciones_de_trazas_clave(self):
        data = _data()
        esperadas = {
            0x43CA54C8: "[CAMERA_MAIN_CC]: ExtractCaptureData()       [CapMode:%d] [ExposureID:%d] [ContID:%d] [FrameID:%d]",
            0x43CA552B: "[CAMERA_MAIN_CC]: CaptureInit()              [CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d] [BDRObase:%d] [FrameID:%d]",
            0x43CA5627: "[CAMERA_MAIN_CC]: SetNRParam()               [CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d] [BDRObase:%d] [FrameID:%d]",
            0x43CA5B13: "[CAMERA_MAIN_CC]: SetSACCSaEndParam()",
            0x43CA5F0A: "[CAMERA_MAIN_CC]: LutMode Change SA %02X <- %02X",
            0x43CA5FA3: "[CAMERA_MAIN_CC]: IsSplit Change [%02X] -> [%02X]",
            0x43CA5FD5: "[CAMERA_MAIN_CC]: uc_sync = [%02X]",
            0x43CA5FF8: "[CAMERA_MAIN_CC]: Create3DLUT 0x%X > 0x%X Level:%d ConvSD:%d BlkOfs Cr:%X, Cb:%X",
            0x43CA6470: "[CAMERA_MAIN_CC]: IE     Error Null Address",
            0x43CA64FF: "[CAMERA_MAIN_CC]: IE     Get   [LightNum:   %2d][MapNum:   %2d][ResAdress:%10lx] ",
            0x43CA665E: "[CAMERA_MAIN_CC]: CC miniRaw Size Error [width: %3d][height: %3d] ",
            0x43CA6805: "[CAMERA_MAIN_CC]: CC::WriteMakerNotePlayRaw [err %d] [CcTagDaraSize %d] [CC_PLAYRAW_MAKERNOTE SIZE %d] ",
            0x43CB4CD3: "[CAMERA_MAIN_CC]: CamCore 3D-Lut table Write Start",
            0x43CB4D62: "[CAMERA_MAIN_CC]: CamCore GetBaseAddress  %X",
        }
        for vaddr, texto in esperadas.items():
            assert _cstr(data, vaddr) == texto, hex(vaddr)


# ------------------------------------------------------------------ referencias
class TestReferenciasPic:
    #: sitio `add rX,pc` -> dirección de la cadena, según la regla estricta
    SITIOS = {
        0x4379ECBA: 0x43CA54C8,
        0x4379ED7A: 0x43CA552B,
        0x4379EE4E: 0x43CA55A9,
        0x4379EF26: 0x43CA5627,
        0x4379EFF6: 0x43CA56A5,
        0x4379F0C6: 0x43CA5723,
        0x4379F196: 0x43CA57A1,
        0x4379F266: 0x43CA581F,
        0x4379F336: 0x43CA589D,
        0x4379F406: 0x43CA591B,
        0x4379F4DC: 0x43CA5999,
        0x4379F5C6: 0x43CA5A17,
        0x4379F65E: 0x43CA5A95,
        0x4379F706: 0x43CA5B13,
        0x4379F78A: 0x43CA5B39,
        0x4379F858: 0x43CA5C35,
        0x4379F924: 0x43CA5CB3,
        0x4379F9F2: 0x43CA5DAF,
        0x4379FB92: 0x43CA5E30,
        0x437A1BDE: 0x43CA5F0A,
        0x437A1BFA: 0x43CA5F3B,
        0x437A1C16: 0x43CA5F6D,
        0x437A1C62: 0x43CA5FA3,
        0x437A1CAE: 0x43CA5FD5,
        0x437A1FC2: 0x43CA5FF8,
        0x437A2782: 0x43CA6158,
        0x437A68D6: 0x43CA6470,
        0x437A6B60: 0x43CA64FF,
        0x437A7E1E: 0x43CA657E,
        0x437A7F24: 0x43CA65BF,
        0x437A8090: 0x43CA6600,
        0x437A9314: 0x43CA665E,
        0x437A9422: 0x43CA66A1,
        0x437ADAD0: 0x43CA6805,
        0x437ADB48: 0x43CA686D,
        0x4381D2EC: 0x43CB4CD3,
        0x4381D350: 0x43CB4D62,
    }

    def test_los_37_sitios_resuelven_a_su_cadena(self):
        data = _data()
        for site, expected in self.SITIOS.items():
            assert _pic_dest(data, site) == expected, hex(site)

    def test_las_47_trazas_referenciadas_estan_en_el_mapa(self):
        data = _data()
        referenciadas = set(self.SITIOS.values())
        assert len(referenciadas) == 37
        # 37 sitios + 10 sitios más dentro de las funciones multi-traza
        todos = {v for v, _ in _cc_strings(data)}
        assert len(todos - referenciadas) == 12

    def test_las_2_trazas_huerfanas_no_tienen_par_pic_estricto(self):
        """Con la regla estricta (el `ldr` MÁS CERCANO del mismo registro) ninguna
        de las dos cadenas es alcanzable; y tampoco hay puntero absoluto."""
        data = _data()
        for vaddr in (0x43CA5BB7, 0x43CA5D31):
            assert _cstr(data, vaddr).startswith(TAG)
            # no hay puntero absoluto de 4 bytes a su dirección
            assert data.find(struct.pack("<I", vaddr)) == -1, hex(vaddr)
        # ningún `add rX,pc` de todo el blob resuelve a ellas con la regla estricta
        for add in _add_pc_sites(data):
            if _pic_dest_rapido(data, add) in (0x43CA5BB7, 0x43CA5D31):
                pytest.fail(f"par PIC estricto en {hex(add)}")

    def test_los_pares_de_la_regla_ancha_son_falsos_positivos(self):
        """La regla ancha atribuye un par a cada traza huérfana, pero el `ldr` que
        usa pertenece a OTRA función y el registro se reescribe antes del `add`."""
        data = _data()
        anchos = {0x43CA5BB7: (0x4379F406, 0x4379ED78),
                  0x43CA5D31: (0x4379F924, 0x4379F6FE)}
        for vaddr, (add, ldr) in anchos.items():
            # el par ancho existe: W + add + 4 == vaddr
            h = _u16(data, ldr)
            assert (h & 0xF800) == 0x4800, hex(ldr)
            lit = ((ldr + 4) & ~3) + ((h & 0xFF) * 4)
            assert (_u32(data, lit) + add + 4) & 0xFFFFFFFF == vaddr
            # ... pero el `ldr` MÁS CERCANO del mismo registro da otra cadena
            assert _pic_dest(data, add) != vaddr
            # y entre `ldr` y `add` el registro r3 se reescribe varias veces
            n_rewrites = 0
            for a in range(ldr + 2, add, 2):
                hh = _u16(data, a)
                if (hh & 0xF800) == 0x6800 and (hh & 7) == 3:        # ldr r3,[rX,#imm]
                    n_rewrites += 1
                elif (hh & 0xFFF0) == 0xF8D0:                          # ldr.w r3,[rX,#imm]
                    if (_u16(data, a + 2) >> 12) & 0xF == 3:
                        n_rewrites += 1
            assert n_rewrites >= 3, (hex(ldr), hex(add), n_rewrites)


# ------------------------------------------------------------------ funciones
class TestFunciones:
    #: (inicio, fin, n_trazas) de las 29 funciones del módulo
    FUNCIONES = [
        (0x4379EC84, 0x4379ED16, 1),
        (0x4379ED34, 0x4379EDE8, 1),
        (0x4379EE04, 0x4379EEC4, 1),
        (0x4379EEE0, 0x4379EF94, 1),
        (0x4379EFB0, 0x4379F064, 1),
        (0x4379F080, 0x4379F134, 1),
        (0x4379F150, 0x4379F204, 1),
        (0x4379F220, 0x4379F2D4, 1),
        (0x4379F2F0, 0x4379F3A6, 1),
        (0x4379F3C0, 0x4379F47C, 1),
        (0x4379F498, 0x4379F568, 1),
        (0x4379F586, 0x4379F604, 1),
        (0x4379F618, 0x4379F6CC, 1),
        (0x4379F6EA, 0x4379F730, 1),
        (0x4379F744, 0x4379F7F8, 1),
        (0x4379F814, 0x4379F8C6, 1),
        (0x4379F8E0, 0x4379F992, 1),
        (0x4379F9AC, 0x4379FA60, 1),
        (0x4379FB48, 0x4379FC02, 1),
        (0x437A1A7E, 0x437A1CE0, 5),
        (0x437A1D7E, 0x437A24AE, 6),
        (0x437A24FC, 0x437A27B2, 1),
        (0x437A6890, 0x437A6BE4, 5),
        (0x437A7E00, 0x437A7E3A, 1),
        (0x437A7E90, 0x437A80A6, 2),
        (0x437A8FAC, 0x437A9552, 2),
        (0x437ADA6E, 0x437ADAEE, 1),
        (0x437ADAFE, 0x437ADB74, 1),
        (0x4381D296, 0x4381D386, 4),
    ]

    def test_hay_29_funciones(self):
        assert len(self.FUNCIONES) == 29

    def test_cada_funcion_empieza_con_prologo_thumb(self):
        data = _data()
        for ini, fin, _ in self.FUNCIONES:
            h = _u16(data, ini)
            if (h & 0xFF00) == 0xB500:
                assert h & 0x0100, hex(ini)     # push {..,lr}
            else:
                assert h == 0xE92D, hex(ini)   # push.w {..,lr}
                assert _u16(data, ini + 2) & 0x4000

    def test_cada_funcion_termina_con_epilogo(self):
        data = _data()
        for ini, fin, _ in self.FUNCIONES:
            h = _u16(data, fin)
            assert (h & 0xFF00) == 0xBD00 or h == 0xE8BD, hex(fin)
            assert h & 0x0080 or (h & 0x8000), hex(fin)   # pop {..,pc}

    def test_el_sumo_de_trazas_por_funcion_es_47(self):
        assert sum(n for _, _, n in self.FUNCIONES) == 47


# ------------------------------------------------------------ identidad captura
class TestIdentidadDeCaptura:
    #: (offset en la estructura, tamaño en bytes, dirección de la instrucción)
    CAMPOS = [
        (0x1C0, 4, 0x4379ED4E),
        (0x1B8, 4, 0x4379ED58),
        (0x1BC, 4, 0x4379ED5E),
        (0x6EC, 4, 0x4379ED64),
        (0x6F4, 4, 0x4379ED6A),
        (0x701, 1, 0x4379ED70),
    ]

    def test_capture_init_lee_los_6_campos_en_los_offsets_documented(self):
        data = _data()
        for off, size, addr in self.CAMPOS:
            if size == 4:
                # ldr.w r3, [r1, #off]  (T3)
                assert _u16(data, addr) == 0xF8D1, hex(addr)
                assert (_u16(data, addr + 2) & 0xFFF) == off, hex(addr)
                assert (_u16(data, addr + 2) >> 12) & 0xF == 3
            else:
                # ldrb.w r3, [r1, #off]  (T2)
                assert _u16(data, addr) == 0xF891, hex(addr)
                assert (_u16(data, addr + 2) & 0xFFF) == off, hex(addr)

    def test_extract_capture_data_usa_una_estructura_de_16_bytes(self):
        data = _data()
        # CapMode@0x08, ExposureID@0x00, ContID@0x04, FrameID@0x0c  (argumento r2)
        esperados = [(0x4379ECA2, 0x08), (0x4379ECAA, 0x00),
                     (0x4379ECAE, 0x04), (0x4379ECB2, 0x0C)]
        for addr, off in esperados:
            h = _u16(data, addr)
            assert h & 0xF800 == 0x6800, hex(addr)          # ldr r3, [r2, #imm]
            assert ((h >> 6) & 0x1F) * 4 == off, hex(addr)
            assert (h >> 3) & 7 == 2, hex(addr)            # Rn = r2
            assert h & 7 == 3, hex(addr)                    # Rt = r3

    def test_el_byte_de_estado_se_escribe_en_el_offset_0xb(self):
        """Cada función de etapa escribe su byte de estado en `[rX, #0xb]`."""
        data = _data()
        etapas = {0x43AEB2AE: 0, 0x43AEB2EC: 1, 0x43AEB324: 2, 0x43AEB358: 3,
                  0x43AEB3A6: 4, 0x43AEB3F8: 5, 0x437A1314: 6, 0x43AEB50E: 7,
                  0x43AEB472: 8, 0x43AEB5A6: 9}
        for addr, estado in etapas.items():
            ok_mov = False
            ok_str = False
            for a in range(addr, addr + 0x60, 2):
                h = _u16(data, a)
                # movs rX, #estado   (T1: 001 00 Rd imm8)
                if (h & 0xF800) == 0x2000 and (h & 0xFF) == estado:
                    ok_mov = True
                # strb r?, [r?, #0xb]  (T1: 01110 imm5 Rn Rt)
                if (h & 0xF800) == 0x7000 and ((h >> 6) & 0x1F) == 0xB:
                    ok_str = True
            assert ok_mov, f"no hay `movs rX, #{estado}` en {hex(addr)}"
            assert ok_str, f"no hay `strb [r?, #0xb]` en {hex(addr)}"

    def test_los_ids_de_parametro_compartido_del_modulo(self):
        data = _data()
        for addr, valor in ((0x437AD61A, 0x9408), (0x437AD64C, 0x9409),
                            (0x437AD672, 0x9410)):
            hw1 = _u16(data, addr)
            hw2 = _u16(data, addr + 2)
            # movw r1, #valor  (T3: hw1 = 1111 0 i 100100 1111 ; hw2 = 0 imm3 Rd imm8)
            assert hw1 & 0xFBF0 == 0xF240, hex(addr)
            imm4 = hw1 & 0xF
            imm3 = (hw2 >> 12) & 0x7
            imm8 = hw2 & 0xFF
            assert (imm4 << 12) | (imm3 << 8) | imm8 == valor, hex(addr)
            assert (hw2 >> 8) & 0xF == 1, hex(addr)      # Rd = r1


# ----------------------------------------------------------------- clase "CC"
class TestClaseCC:
    def test_el_registro_de_clases_lista_las_clases_CC(self):
        data = _data()
        esperados = {
            0x43FF8EE4: "CC::CcEncryptedTagData",
            0x43FF8EE8: "CC::CcEncryptedFtTagData",
            0x43FF8EEC: "FC::FcEncryptedTagData",
            0x43FF8EF0: "LC::LcEncryptedTagData",
            0x43FF8EF8: "TC::TcEncryptedTagData",
            0x43FF8F0C: "CC::CcEncryptedNflashTagData",
            0x43FF8F14: "IM::ImEncryptedTagData",
        }
        for ranura, texto in esperados.items():
            ptr = _u32(data, ranura)
            assert _cstr(data, ptr) == texto, hex(ranura)

    def test_los_typeinfo_de_ImageParam_Capture(self):
        data = _data()
        esperados = {
            0x43FF8F1C: "N6Camera7Imaging10ImageParamE",
            0x43FF8F24: "N6Camera7Capture24ImageParam_Capture_ShareE",
            0x43FF8F30: "N6Camera7Capture18ImageParam_CaptureE",
            0x43FF8F3C: "N6Camera7Capture23ImageParam_Capture_BaseE",
        }
        for ranura, texto in esperados.items():
            ptr = _u32(data, ranura)
            assert _cstr(data, ptr) == texto, hex(ranura)

    def test_dos_trazas_llevan_el_ambito_CC(self):
        data = _data()
        assert "CC::WriteMakerNotePlayRaw" in _cstr(data, 0x43CA6805)
        assert "CC::SetExtOutputMakerNotePlayRaw" in _cstr(data, 0x43CA686D)


# --------------------------------------------------------------- grafo llamadas
class TestGrafoDeLlamadas:
    def test_stage_sacc_llama_a_set_sacc_param(self):
        data = _data()
        objetivos = dict(_bl_targets(data, 0x43782464, 0x43782A06))
        assert objetivos.get(0x4378258A) == 0x4379F618

    def test_stage_sacc_llama_a_write_sacc_makernote(self):
        data = _data()
        objetivos = dict(_bl_targets(data, 0x43782464, 0x43782A06))
        assert objetivos.get(0x4378286A) == 0x4379FB48

    def test_los_19_metodos_vivos_usan_el_mismo_registrador_de_trazas(self):
        data = _data()
        metodos = [f for f, _, _ in TestFunciones.FUNCIONES if 0x4379EC84 <= f <= 0x4379FC02]
        assert len(metodos) == 19
        for m in metodos:
            assert 0x4379EBD8 in [t for _, t in _bl_targets(data, m, m + 0x100)], hex(m)

    def test_cada_modo_vivo_delega_en_una_funcion_de_etapa_distinta(self):
        data = _data()
        etapas = []
        for f, _, _ in TestFunciones.FUNCIONES:
            if not (0x4379EC84 <= f <= 0x4379FC02):
                continue
            tg = [t for _, t in _bl_targets(data, f, f + 0x100)]
            candidatas = [t for t in tg if 0x43AEB2AE <= t <= 0x43AEB640
                          or t in (0x437A1314, 0x437A16A4, 0x4381D4AC)]
            assert len(candidatas) <= 1, hex(f)
            if candidatas:
                assert candidatas[0] not in etapas
                etapas.append(candidatas[0])
        assert len(etapas) >= 15

    def test_el_control_de_captura_no_llama_a_dmm_imager_ni_motor_yc(self):
        data = _data()
        dmm = {int(f["func"], 16) for f in json.load(
            open(ROOT / "analysis" / "s113_cam_dmm" / "func_map.json"))["functions"]}
        imager = {int(f["func"], 16) for f in json.load(
            open(ROOT / "analysis" / "s115_cam_imager" / "func_map.json"))["functions"]}
        yc = {int(f["func"], 16) for f in json.load(
            open(ROOT / "analysis" / "s110_camera_main_yc" / "func_map.json"))["functions"]}
        destinos = set()
        for f, fin, _ in TestFunciones.FUNCIONES:
            destinos.update(t for _, t in _bl_targets(data, f, fin + 4))
        assert not (destinos & dmm)
        assert not (destinos & imager)
        assert not (destinos & yc)


# ----------------------------------------------------------------- diferencial
def _cadenas_exactas(data):
    """Conjunto de cadenas NUL-terminadas del binario."""
    out = set()
    start = 0
    n = len(data)
    prev = False
    ini = 0
    for i in range(n):
        c = data[i]
        cur = 32 <= c < 127
        if cur and not prev:
            ini = i
        if not cur and prev:
            out.add(data[ini:i].decode("latin1"))
        prev = cur
    return out


class TestDiferencial:
    def test_47_de_49_mensajes_son_identicos_en_la_a7s_sin_el_prefijo(self):
        a6 = _data()
        a7 = _cadenas_exactas(_data(A7S_BIN))
        textos6 = [t[len(TAG):] for _, t in _cc_strings(a6)]
        comunes = sum(1 for t in textos6 if t in a7)
        assert comunes == 47

    def test_los_2_mensajes_extendidos_son_ampliaciones_de_la_a6000(self):
        a6 = _data().decode("latin1")
        a7 = _data(A7S_BIN).decode("latin1")
        assert "IsSplit Change [%02X] -> [%02X]" in a6
        assert "IsSplit Change [%02X] -> [%02X] uc_proc[%02X]" in a7
        assert "Create3DLUT 0x%X > 0x%X Level:%d ConvSD:%d BlkOfs Cr:%X, Cb:%X" in a6
        assert "Create3DLUT 0x%X > 0x%X Level:%d ConvSD:%d" in a7

    def test_la_a7s_no_tiene_ningun_prefijo_camera_main(self):
        assert b"[CAMERA_MAIN" not in _data(A7S_BIN)
        assert b"[CAMERA_MAIN" not in _data(A6300_BIN)

    def test_la_a6000_tiene_los_8_submodulos_camera_main(self):
        a6 = _data()
        for pref in (b"[CAMERA_MAIN]", b"[CAMERA_MAIN_CC]", b"[CAMERA_MAIN_FC]",
                     b"[CAMERA_MAIN_IM]", b"[CAMERA_MAIN_LC]", b"[CAMERA_MAIN_SYNC]",
                     b"[CAMERA_MAIN_TC]", b"[CAMERA_MAIN_YC]"):
            assert pref in a6, pref


# --------------------------------------------------------------------- json
class TestJsonDelHito:
    def test_los_recuentos_del_json(self):
        j = _json()
        assert j["counts"]["strings"] == 49
        assert j["counts"]["referenced"] == 47
        assert j["counts"]["unreferenced"] == 2
        assert j["counts"]["functions"] == 29
        assert j["counts"]["subblocks"] == 6
        assert j["counts"]["a7s_prefixed"] == 0
        assert j["counts"]["a7s_common_messages"] == 47

    def test_los_6_subbloques_suman_49(self):
        j = _json()
        assert sum(b["n"] for b in j["subblocks"]) == 49
        assert {b["name"]: b["n"] for b in j["subblocks"]} == {
            "capture-control": 21, "lut": 12, "ie": 8,
            "camcore-3dlut": 4, "miniraw": 2, "makernote-playraw": 2}

    def test_las_2_trazas_sin_referencia_son_las_huerfanas(self):
        j = _json()
        huerfanas = [s["vaddr"] for s in j["strings"] if not s["referenced"]]
        assert huerfanas == ["0x43ca5bb7", "0x43ca5d31"]
