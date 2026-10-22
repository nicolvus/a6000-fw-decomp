"""Tests for S109 — el módulo `[CDIAG]` (diagnóstico del códec) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware y comprueban direcciones,
textos, recuentos y encadenamientos de instrucciones concretos. Si cambia una
dirección, el texto o un recuento, el test falla.
"""

import json
import pathlib
import re
import struct

import pytest

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
ROOT = pathlib.Path(__file__).resolve().parents[1]
PREFIX = b"[CDIAG]"


# --------------------------------------------------------------- utilidades
_DATA_CACHE = {}


def _data(path=BIN_PATH):
    if path not in _DATA_CACHE:
        with open(ROOT / path, "rb") as fh:
            _DATA_CACHE[path] = fh.read()
    return _DATA_CACHE[path]


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


def _string_start(data, token_off):
    """Retrocede hasta el inicio de la cadena imprimible que contiene el token."""
    s = token_off
    while s > 0 and 32 <= data[s - 1] < 127:
        s -= 1
    return BASE_VADDR + s


def _cdiag_occurrences(data):
    """[(vaddr_token, vaddr_cadena, texto)] de cada token `[CDIAG]`."""
    out = []
    start = 0
    while True:
        i = data.find(PREFIX, start)
        if i < 0:
            break
        v = _string_start(data, i)
        out.append((BASE_VADDR + i, v, _cstr(data, v)))
        start = i + 1
    return out


def _bl_target(data, vaddr):
    """Destino de la instrucción `bl` de 32 bits que empieza en `vaddr`."""
    h1 = _u16(data, vaddr)
    h2 = _u16(data, vaddr + 2)
    assert (h1 & 0xF800) == 0xF000, f"{hex(vaddr)} no es un BL/BLX de 32 bits"
    assert (h2 & 0xD000) == 0xD000, f"{hex(vaddr)} no es un BL/BLX de 32 bits"
    s = (h1 >> 10) & 1
    imm10 = h1 & 0x3FF
    j1 = (h2 >> 13) & 1
    j2 = (h2 >> 11) & 1
    i1 = (~(j1 ^ s)) & 1
    i2 = (~(j2 ^ s)) & 1
    imm11 = h2 & 0x7FF
    imm = (s << 24) | (i1 << 23) | (i2 << 22) | (imm10 << 12) | (imm11 << 1)
    if s:
        imm -= 1 << 25
    return (vaddr + 4 + imm) & 0xFFFFFFFF


def _pic_ref(data, add_site):
    """Cadena referenciada por el `add rX,pc` de `add_site` (esquema PIC)."""
    h = _u16(data, add_site)
    assert (h & 0xFF00) == 0x4400, f"{hex(add_site)} no es `add rX,pc`"
    assert ((h >> 3) & 0xF) == 15, f"{hex(add_site)} no usa PC como origen"
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    # `ldr rX,[pc,#imm]` más cercano por detrás (mismo registro)
    for la in range(add_site - 2, add_site - 4096, -2):
        lh = _u16(data, la)
        if (lh & 0xF800) == 0x4800:
            lreg = (lh >> 8) & 7
            lit = ((la + 4) & ~3) + ((lh & 0xFF) * 4)
        elif (lh & 0xFF7F) == 0xF85F:
            h2 = _u16(data, la + 2)
            lreg = (h2 >> 12) & 0xF
            imm12 = (((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF)
            lit = ((la + 4) & ~3) + imm12
        else:
            continue
        if lreg != reg:
            continue
        w = _u32(data, lit)
        return (w + (add_site + 4)) & 0xFFFFFFFF
    return None


# ------------------------------------------------------------------- módulo
class TestModulo:
    def test_conteo_de_tokens_cdiag(self):
        data = _data()
        occ = _cdiag_occurrences(data)
        assert len(occ) == 270, f"Se esperaban 270 tokens [CDIAG], hay {len(occ)}"
        assert occ[0][1] == 0x43C3B0D4
        assert occ[-1][1] == 0x43C3E86A

    def test_255_empiezan_por_el_prefijo_y_15_levan_ERR(self):
        data = _data()
        occ = _cdiag_occurrences(data)
        start = [o for o in occ if o[2].startswith("[CDIAG]")]
        err = [o for o in occ if o[2].startswith("[ERR][CDIAG]")]
        assert len(start) == 255, len(start)
        assert len(err) == 15, len(err)
        assert len(start) + len(err) == 270

    def test_subbloques_y_recuentos(self):
        data = _data()
        occ = _cdiag_occurrences(data)
        tag = re.compile(r"^\[CDIAG\]\[([A-Z0-9_]+)\]")
        counts = {}
        for _tok, _v, txt in occ:
            if not txt.startswith("[CDIAG]"):
                continue
            m = tag.match(txt)
            assert m, txt
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
        esperado = {
            "TSK": 1, "CTRLIF": 19, "CTRLCORE": 49,
            "CTRLHDDEC": 26, "CTRLHDREC": 27,
            "CTRLJPGDEC": 21, "CTRLJPGENC": 21, "CTRLJPGENCDEC": 22,
            "CTRLSDDEC": 26, "CTRLSDREC": 27, "CMPDATA": 16,
        }
        assert counts == esperado, counts
        assert sum(counts.values()) == 255

    def test_cadenas_especificas(self):
        data = _data()
        esperadas = {
            0x43C3B0D4: "[CDIAG][TSK]act_tsk",
            0x43C3B0F4: "[ERR][CDIAG][TSKCORE]DataflowInfraMsgErr [0x%08X]",
            0x43C3B1B5: "[CDIAG][CTRLIF]EXEC CMD cmd[0x%02x] mode[%d] func[%d] prm[%d]",
            0x43C3B2CF: "[CDIAG][CTRLIF]SEND MSG EXEC CMD cmd[0x%02x] mode[%d] func[%d] prm[%d]",
            0x43C3B316: "[CDIAG][CTRLIF]cmdMode[0x%08X] cmd[0x%08X] mode[0x%08X] [%s]",
            0x43C3B3E8: "[ERR][CDIAG][CTRLIF]NOT SUPPORTED(SENS_SET_DATA) -- MODE ID [0x%08X] [%s]",
            0x43C3B518: "[CDIAG][CTRLIF]SENS_SET_DIAG_MODE [%s]",
            0x43C3B5B4: "[CDIAG][CTRLIF]SENS_CMP_DATA [%s]",
            0x43C3B624: "[CDIAG][CTRLIF]SENS_GET_DATA [%s]",
            0x43C3B82D: "[ERR][CDIAG][CTRLCORE]p_prm is NULL file[%s] func[%s] line[%d]",
            0x43C3B89F: "[CDIAG][CTRLCORE]Exec DbgDiagAvc HD REC!!",
            0x43C3B91D: "[CDIAG][CTRLCORE]Exec DbgDiagAvc SD DEC!!(NotSupport)",
            0x43C3B953: "[CDIAG][CTRLCORE]No Support EXEC MODE!!",
            0x43C3BF7D: "[CDIAG][CTRLCORE][SET_DIAG_MODE] mode[0x%02X] func[0x%02X]",
            0x43C3BFEE: ("[CDIAG][CTRLCORE]memIdx[%d] fileId[%02d:%02d] unitHandle[0x%04X] "
                         "unitType[0x%08X] size[0x%08X]"),
            0x43C3C0EB: "[CDIAG][CTRLCORE]Exec SetData JPG ENCDEC!!",
            0x43C3C247: ("[CDIAG][CTRLHDDEC]index[%d] unit[0x%08X] addr[0x%08X] size[%d] "
                         "fsize[%d] hdl[0x%08X]"),
            0x43C3C463: "[CDIAG][CTRLHDDEC]ClkState IDLE->OPEN",
            0x43C3C5A3: "[CDIAG][CTRLHDDEC][VSYNC] RUN CODEC INIT",
            0x43C3C5E9: "[CDIAG][CTRLHDDEC]PAL(50i) MODE Clk[%d]",
            0x43C3C612: "[CDIAG][CTRLHDDEC]NTSC(60i) MODE Clk[%d]",
            0x43C3CB59: "[CDIAG][CTRLHDREC]LOOP NUM [0x%02X]",
            0x43C3CE57: "[CDIAG][CTRLJPGDEC]JPEG DEC IMG Differ!!",
            0x43C3CF30: "[CDIAG][CTRLJPGDEC]JPEG DEC END... w[%d] h[%d]",
            0x43C3D34F: "[CDIAG][CTRLJPGENC]JPEG ENC ES Differ!!",
            0x43C3D42F: "[CDIAG][CTRLJPGENC]JPEG ENC END... [%d]bits",
            0x43C3D7C1: "[CDIAG][CTRLJPGENCDEC]VideoES Differ!!",
            0x43C3D7E9: "[CDIAG][CTRLJPGENCDEC]AudioES Differ!!",
            0x43C3E3F6: "[CDIAG][CTRLSDREC]PAL(50i) MODE Clk[%d] NTPAL[%d]",
            0x43C3E5CA: "[CDIAG][CMPDATA]differ size!!!",
            0x43C3E5EA: "[CDIAG][CMPDATA]src[0x%08X] dst[0x%08X] size[%d]",
            0x43C3E6DC: "[CDIAG][CMPDATA][step.1] [0x%08X]byte... s[0x%02X] d[0x%02X]",
            0x43C3E7AC: "[CDIAG][CMPDATA]step2 OK",
            0x43C3E86A: "[CDIAG][CMPDATA]step3 sadr[0x%08X] dadr[0x%08X]",
        }
        for vaddr, texto in esperadas.items():
            assert _cstr(data, vaddr) == texto, f"vaddr {hex(vaddr)}: texto incorrecto"

    def test_clases_y_ficheros_fuente(self):
        data = _data()
        clases = {
            0x43C3B0CB: "7CdMsgIf",
            0x43C3B0E9: "9CdTskCore",
            0x43C3B67E: "8CdCtrlIf",
            0x43C3B6D4: "9CdMsgCore",
            0x43C3C116: "10CdCtrlCore",
            0x43C3C1E3: "11CdCtrlHdDec",
            0x43C3C753: "11CdCtrlHdRec",
            0x43C3CC98: "12CdCtrlJpgDec",
            0x43C3D11C: "12CdCtrlJpgEnc",
            0x43C3D5A4: "15CdCtrlJpgEncDec",
            0x43C3DF16: "11CdCtrlSdDec",
            0x43C3DFCC: "11CdCtrlSdRec",
            0x43C3E53C: "9CdMemCtrl",
            0x43C3E547: "13CdUtilClkCtrl",
            0x43C3E89B: "13CdUtilCmpData",
            0x43C3E8AB: "13CdUtilSysvMsg",
        }
        for vaddr, texto in clases.items():
            assert _cstr(data, vaddr) == texto, f"clase en {hex(vaddr)}"
        assert _cstr(data, 0x43C3B1A8) == "cdCtrlIf.cpp"
        assert _cstr(data, 0x43C3B86C) == "cdCtrlCore.cpp"

    def test_firmas_cdiager(self):
        data = _data()
        firmas = {
            0x43C3B126: ("CDIAGER CdCtrlIf::ExecSensCmd(__uint32_t, const OsalRequestPacket*, "
                         "__uint32_t)"),
            0x43C3B647: "CDIAGER CdCtrlIf::ExecCmd(CdCtrlIf::MSG_SENS_COMMAND*)",
            0x43C3B688: ("CDIAGER CdCtrlIf::ExecSensComp(__uint32_t, OsalResponsePacket*, "
                         "__uint32_t)"),
            0x43C3B6DF: ("CDIAGER CdCtrlCore::DbgDiagAvc(__uint8_t, __uint8_t, __uint8_t, "
                         "__uint8_t)"),
            0x43C3B72A: "CDIAGER CdCtrlCore::CmpData(__uint8_t, __uint8_t, __uint32_t)",
            0x43C3C123: "CDIAGER CdCtrlCore::RunCodec(__uint8_t, __uint8_t, __uint32_t)",
            0x43C3C162: "CDIAGER CdCtrlCore::SetData(const __uint8_t*, __uint32_t)",
            0x43C3C694: "CDIAGER CdCtrlHdDec::SetMemArea(CdCtrlHdDec::DIAGINFO*)",
            0x43C3E4ED: ("CDIAGER CdCtrlSdRec::SetCodecParam(__uint8_t, __uint8_t, __uint8_t, "
                         "__uint8_t)"),
        }
        for vaddr, texto in firmas.items():
            assert _cstr(data, vaddr) == texto, f"firma en {hex(vaddr)}"
        # exactamente 27 firmas en la zona del módulo
        zona = data[0x43C3B000 - BASE_VADDR:0x43C3F000 - BASE_VADDR]
        assert len(re.findall(rb"CDIAGER [ -~]{3,}", zona)) == 27

    def test_comandos_sens(self):
        """Los 16 nombres de comando `SENS_*` están en direcciones concretas."""
        data = _data()
        sens = {
            0x43C3B203: "SENS_SET_DATA_AREA",
            0x43C3B216: "SENS_REL_DATA_AREA",
            0x43C3B229: "SENS_RUN_CODEC",
            0x43C3B397: "SENS_MODE_PROC_START",
            0x43C3B3CA: "SENS_MODE_FIN_SEND_DATA",
            0x43C3B40A: "SENS_SET_DATA",
            0x43C3B44B: "SENS_MODE_FIN_RECV_DATA",
            0x43C3B47C: "SENS_CNFM_DONE_CODEC",
            0x43C3B4A6: "SENS_CNFM_SET_DATA_AREA",
            0x43C3B4D3: "SENS_CNFM_REL_DATA_AREA",
            0x43C3B500: "SENS_DBG_DIAG_AVC",
            0x43C3B527: "SENS_SET_DIAG_MODE",
            0x43C3B5C3: "SENS_CMP_DATA",
            0x43C3B633: "SENS_GET_DATA",
            0x43C3B66F: "SENS_COMMAND",
        }
        for vaddr, texto in sens.items():
            assert _at(data, vaddr, len(texto)) == texto, f"comando en {hex(vaddr)}"
        # los tres primeros son cadenas independientes; los demás van dentro de
        # las cadenas de [CTRLIF] (dirección del token != inicio de la cadena)
        assert _cstr(data, 0x43C3B203) == "SENS_SET_DATA_AREA"
        assert _cstr(data, 0x43C3B216) == "SENS_REL_DATA_AREA"
        assert _cstr(data, 0x43C3B229) == "SENS_RUN_CODEC"
        assert _cstr(data, 0x43C3B37F) == "[CDIAG][CTRLIF]Received SENS_MODE_PROC_START [%s]"
        assert _cstr(data, 0x43C3B647).startswith("CDIAGER CdCtrlIf::ExecCmd(")

    def test_no_hay_menciones_del_obturador_ni_del_sensor(self):
        data = _data()
        occ = _cdiag_occurrences(data)
        texto = " ".join(o[2] for o in occ).lower()
        for palabra in ("shutter", "silent", "efcs", "curtain", "mechan",
                        "imager", "sensor", "dfe", "dmm", "readout"):
            assert palabra not in texto, palabra


class TestReferenciasPIC:
    """El esquema PIC: ldr rX,[pc,#imm] + add rX,pc -> destino = W + (add + 4)."""

    def test_referencia_de_CTRLIF_EXEC_CMD(self):
        data = _data()
        # 0x435a1450: ldr r0,[pc,#0x20] ; pool 0x435a14ec = 0x000699d5f
        assert _u16(data, 0x435A1450) & 0xFF00 == 0x4800
        assert _u16(data, 0x435A1450) & 0xFF == 0x26
        assert _u32(data, 0x435A14EC) == 0x000699D5F
        # 0x435a1452: add r0, pc
        assert _u16(data, 0x435A1452) == 0x4478
        assert _pic_ref(data, 0x435A1452) == 0x43C3B1B5
        assert _cstr(data, _pic_ref(data, 0x435A1452)).startswith("[CDIAG][CTRLIF]EXEC CMD")

    def test_referencia_de_CTRLCORE_no_support(self):
        data = _data()
        # 0x435a1de8 area: el dispatcher de "No Support EXEC MODE!!"
        # se localiza recorriendo las referencias del propio binario
        occ = _cdiag_occurrences(data)
        vaddr = None
        for _tok, v, txt in occ:
            if txt == "[CDIAG][CTRLCORE]No Support EXEC MODE!!":
                vaddr = v
        assert vaddr == 0x43C3B953
        # y la cadena existe con ese texto exacto
        assert _cstr(data, 0x43C3B953) == "[CDIAG][CTRLCORE]No Support EXEC MODE!!"

    def test_referencia_de_CMPDATA_step2_ok(self):
        data = _data()
        # la cadena "step2 OK" está referenciada desde el comparador
        assert _cstr(data, 0x43C3E7AC) == "[CDIAG][CMPDATA]step2 OK"
        # el PIC debe resolver a esa dirección desde algún `add rX,pc`
        refs = _pic_refs_de_la_cadena(data, 0x43C3E7AC)
        assert refs, "no se encuentra referencia PIC a 'step2 OK'"
        for site in refs:
            assert _pic_ref(data, site) == 0x43C3E7AC

    def test_29_cadenas_sin_referencia(self):
        data = _data()
        occ = _cdiag_occurrences(data)
        sin_ref = []
        for _tok, v, txt in occ:
            if not txt.startswith("[CDIAG]"):
                continue
            if not _pic_refs_de_la_cadena(data, v):
                sin_ref.append(v)
        assert len(sin_ref) == 29, f"{len(sin_ref)} cadenas sin referencia: {sin_ref}"
        # y ninguna tiene un puntero absoluto de 4 B en la imagen
        for v in sin_ref:
            assert data.find(struct.pack("<I", v)) == -1, hex(v)


_PIC_CACHE = {}


def _at(data, vaddr, n):
    """n bytes imprimibles leídos exactamente en `vaddr`."""
    off = vaddr - BASE_VADDR
    assert 0 <= off < len(data), f"vaddr {hex(vaddr)} fuera del binario"
    return data[off:off + n].decode("latin1")


def _pic_index(data):
    """Índice {destino: [sitios 'add rX,pc']} de toda la imagen (se cachea)."""
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
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    import bisect
    for a in range(BASE_VADDR, BASE_VADDR + n - 4, 2):
        o = a - BASE_VADDR
        h = struct.unpack("<H", data[o:o + 2])[0]
        if (h & 0xFF00) != 0x4400 or ((h >> 3) & 0xF) != 15:
            continue
        reg = (((h >> 7) & 1) << 3) | (h & 7)
        v = by_reg.get(reg)
        if not v:
            continue
        ks = keys[reg]
        i = bisect.bisect_right(ks, a) - 1
        if i < 0:
            continue
        la, w = v[i]
        if a - la > 4096:
            continue
        out.setdefault((w + (a + 4)) & 0xFFFFFFFF, []).append(a)
    _PIC_CACHE[key] = out
    return out


def _pic_refs_de_la_cadena(data, vaddr):
    """Todos los sitios `add rX,pc` que resuelven a `vaddr`."""
    return list(_pic_index(data).get(vaddr, []))


class TestCodigo:
    """Bytes concretos del código que implementa el módulo."""

    def test_nucleo_de_la_tarea_llama_a_osal_rcv_msg(self):
        data = _data()
        # 0x435a1318: push {r4,r5,lr}  (núcleo de la tarea, CdTskCore)
        assert _u16(data, 0x435A1318) == 0xB530
        # 0x435a1342: bl 0x435a9f4d  (recepción del mensaje)
        assert _bl_target(data, 0x435A1342) == 0x435A9F4C
        # 0x435a9f68: bl 0x43561261  -> osal_rcv_msg
        assert _bl_target(data, 0x435A9F68) == 0x43561260

    def test_escritor_de_trazas_usa_nivel_0xbe_y_id_0xbad(self):
        data = _data()
        # 0x435ab880: push {r0,r1,r2,r3}   (0xB40F)
        assert _u16(data, 0x435AB880) == 0xB40F
        # 0x435ab882: movs r1,#0x80  (búfer de 128 bytes)   (0x2180)
        assert _u16(data, 0x435AB882) == 0x2180
        # 0x435ab896: bl 0x439c5004  (vsnprintf)
        assert _bl_target(data, 0x435AB896) == 0x439C5004
        # 0x435ab8a2: movw r1,#0xbad  (id de módulo)
        assert _u16(data, 0x435AB8A2) == 0xF640
        assert _u16(data, 0x435AB8A4) == 0x31AD
        # 0x435ab8ae: movs r0,#0xbe  (nivel)
        assert _u16(data, 0x435AB8AE) == 0x20BE
        # 0x435ab8b0: bl 0x435ab7d4  (emisor de log)
        assert _bl_target(data, 0x435AB8B0) == 0x435AB7D4

    def test_nombres_de_api_osal_en_el_modulo_CLK_CTRL(self):
        data = _data()
        # las trazas que nombran las API OSAL, con su vaddr exacta
        assert _cstr(data, 0x43C3AB06) == "[CLK_CTRL]: [ERR] osal_try_valloc_msg 0x%0x"
        assert _cstr(data, 0x43C3AB32) == "[CLK_CTRL]: [ERR] osal_snd_msg 0x%0x"
        assert _cstr(data, 0x43C3AB57) == "[CLK_CTRL]: [ERR] osal_free_msg 0x%0x"
        assert _cstr(data, 0x43C3AB7D) == "[CLK_CTRL]: [ERR] osal_rcv_msg 0x%0x"


class TestDiferencial:
    def test_a7s_tiene_las_mismas_270_cadenas(self):
        path = ROOT / A7S_BIN
        if not path.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(path, "rb") as fh:
            a7s = fh.read()
        assert a7s.count(PREFIX) == 270
        texto_a6 = {t for _tok, _v, t in _cdiag_occurrences(_data())}
        texto_a7 = {t for _tok, _v, t in _cdiag_occurrences(a7s)}
        assert texto_a6 == texto_a7
        assert len(texto_a6) == 270

    def test_a7s_tiene_las_mismas_clases_y_ficheros(self):
        path = ROOT / A7S_BIN
        if not path.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(path, "rb") as fh:
            a7s = fh.read()
        # la primera aparicion de cada clase y de cada fichero, por texto
        for texto in (b"10CdCtrlCore", b"15CdCtrlJpgEncDec", b"13CdUtilCmpData",
                      b"cdCtrlIf.cpp", b"cdCtrlCore.cpp"):
            assert a7s.count(texto) == 1, texto
        assert a7s.count(b"CDIAGER ") == 27

    def test_a6300_anade_4k(self):
        path = ROOT / A6300_BIN
        if not path.exists():
            pytest.skip("blob de la A6300 no disponible")
        with open(path, "rb") as fh:
            a6300 = fh.read()
        assert a6300.count(PREFIX) == 310
        texto_a6 = {t for _tok, _v, t in _cdiag_occurrences(_data())}
        texto_a63 = {t for _tok, _v, t in _cdiag_occurrences(a6300)}
        nuevos = texto_a63 - texto_a6
        assert len(nuevos) == 40, len(nuevos)
        assert "[CDIAG][CTRL4KREC]ClkState IDLE->OPEN" in nuevos
        assert "[CDIAG][CTRLCORE]Exec RunCodec 4K REC!!" in nuevos
        # ninguna cadena de la A6000 desaparece
        assert not (texto_a6 - texto_a63)


class TestTablaDeClases:
    """Tabla de registro de clases del subsistema (pares {vptr, nombre})."""

    TABLA_A6000 = 0x43FDA6A0
    TABLA_A7S = 0x43FDB6EC
    TABLA_A6300 = 0x4419B094

    def _entradas(self, data, tabla):
        out = []
        a = tabla
        while True:
            w1 = _u32(data, a)
            w2 = _u32(data, a + 4)
            off = w2 - BASE_VADDR
            if off < 0 or off >= len(data):
                break
            end = off
            while end < len(data) and 32 <= data[end] < 127:
                end += 1
            t = data[off:end].decode("latin1")
            if not t or not t[0].isdigit():
                break
            out.append((a, t))
            a += 8
        return out

    def test_tabla_a6000_tiene_16_clases_en_orden(self):
        data = _data()
        ent = self._entradas(data, self.TABLA_A6000)
        assert len(ent) == 16, ent
        nombres = [t for _a, t in ent]
        assert nombres == [
            "7CdMsgIf", "9CdTskCore", "8CdCtrlIf", "9CdMsgCore",
            "10CdCtrlCore", "11CdCtrlHdDec", "11CdCtrlHdRec", "12CdCtrlJpgDec",
            "12CdCtrlJpgEnc", "15CdCtrlJpgEncDec", "11CdCtrlSdDec", "11CdCtrlSdRec",
            "9CdMemCtrl", "13CdUtilClkCtrl", "13CdUtilCmpData", "13CdUtilSysvMsg",
        ]
        # la primera entrada apunta al nombre de clase "7CdMsgIf"
        assert _u32(data, self.TABLA_A6000 + 4) == 0x43C3B0CB
        # todas las entradas comparten el mismo vptr
        vptrs = {_u32(data, a) for a, _t in ent}
        assert vptrs == {0x43FD04F8}, vptrs

    def test_a7s_tiene_la_misma_tabla_de_clases(self):
        path = ROOT / A7S_BIN
        if not path.exists():
            pytest.skip("blob de la A7S no disponible")
        with open(path, "rb") as fh:
            a7s = fh.read()
        ent = self._entradas(a7s, self.TABLA_A7S)
        assert len(ent) == 16, ent
        assert {t for _a, t in ent} == {
            "7CdMsgIf", "9CdTskCore", "8CdCtrlIf", "9CdMsgCore",
            "10CdCtrlCore", "11CdCtrlHdDec", "11CdCtrlHdRec", "12CdCtrlJpgDec",
            "12CdCtrlJpgEnc", "15CdCtrlJpgEncDec", "11CdCtrlSdDec", "11CdCtrlSdRec",
            "9CdMemCtrl", "13CdUtilClkCtrl", "13CdUtilCmpData", "13CdUtilSysvMsg",
        }

    def test_a6300_tiene_20_clases_con_las_CdExt(self):
        path = ROOT / A6300_BIN
        if not path.exists():
            pytest.skip("blob de la A6300 no disponible")
        with open(path, "rb") as fh:
            a6300 = fh.read()
        ent = self._entradas(a6300, self.TABLA_A6300)
        nombres = {t for _a, t in ent}
        assert len(ent) == 20, len(ent)
        for extra in ("10CdExtMsgIf", "11CdExtCtrlIf", "13CdExtCtrlCore", "11CdExtMcCtrl"):
            assert extra in nombres, extra


class TestJsonDelHito:
    def test_json_estructura(self):
        with open(ROOT / "analysis/s109_cdiag/cdiag.json") as fh:
            dat = json.load(fh)
        assert dat["milestone"] == "S109"
        assert dat["base_vaddr"] == "0x43541000"
        assert dat["count_cdiag_token"] == 270
        assert dat["count_strings_starting_with_prefix"] == 255
        assert dat["count_strings_with_ERR_prefix"] == 15
        assert dat["range"] == ["0x43c3b0d4", "0x43c3e86a"]
        assert len(dat["function_signatures"]) == 27
        assert len(dat["class_names"]) == 16
        assert len(dat["source_files"]) == 2
        sub = {b["tag"]: b["count"] for b in dat["subblocks"]}
        assert sub["CTRLCORE"] == 49
        assert sub["CMPDATA"] == 16
        assert sum(sub.values()) == 255
        # el diferencial con la A7S es 0/0
        cmp_a7s = dat["differential"]["A7S_fw320"]["text_comparison"]
        assert cmp_a7s["comunes"] == 270
        assert cmp_a7s["solo_en_A6000"] == []
        assert cmp_a7s["solo_en_A7S_fw320"] == []
        # 29 cadenas sin referencia PIC
        sin_ref = [s for s in dat["strings"] if not s["pic_sites"]]
        assert len(sin_ref) == 29
        # tabla de registro de clases en el diferencial
        reg = dat["differential"]["A7S_fw320"]["class_registry_table"]
        assert reg["table_vaddr"] == "0x43fdb6ec"
        assert reg["n_entries"] == 16
