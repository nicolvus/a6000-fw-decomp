"""Tests de S139 — el módulo `[ENCSEQCTRL]` (46 trazas) de la A6000 fw3.21.

Todos los tests son de **bytes reales**: leen el firmware, **recalculan** el mapa de
referencias PIC de forma independiente (regla estricta de `scan_pic_refs_strict.py`) y
comprueban direcciones, textos, tablas y guardas concretas. Si cambia una dirección, un
texto, una tabla o un recuento, el test falla.
"""

import bisect
import json
import pathlib
import struct

import pytest

BASE_VADDR = 0x43541000
BIN_PATH = "analysis/rea-independent/input/av-cam.bin"
JSON_PATH = "analysis/s139_encseqctrl/encseqctrl.json"
A7S_BIN = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300_BIN = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
ROOT = pathlib.Path(__file__).resolve().parents[1]
TOKEN = b"[ENCSEQCTRL]"

# --- direcciones que el informe afirma (si alguna cambia, el test falla) ------
CADENAS = {
    0x43C4BCE5: "[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d ",
    0x43C4BD2B: "[ENCSEQCTRL][O/U Crank] Table[%d] fR[0x%x] sR[0x%x]",
    0x43C4BD5F: "[ENCSEQCTRL]OuCrank Config Err: FrameRate = %x,SamplingRate = %x ",
    0x43C4BDA2: "[ENCSEQCTRL][state]0x%x -> 0x%x ",
    0x43C4BDC4: ("[ENCSEQCTRL]Warning, m_beginEncCompTime < refTime, change state "
                 "forcibly"),
    0x43C4BE0E: "[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d,Err = %x ",
    0x43C4BE41: "[ENCSEQCTRL]Func:%s() ,Line:%d, State:0x%x->0x%x ",
    0x43C4BE74: "[ENCSEQCTRL][AVC ENC SEQ CTRL] Chip Mode = %x ",
    0x43C4BEA4: "[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d, State:0x%x->0x%x ",
    0x43C4BEE0: "[ENCSEQCTRL]Invalid syshsCnt File:%s, Func:%s() ,Line:%d ",
    0x43C4BF1B: "[ENCSEQCTRL]WRN: Pin Supply Timing UNKNOWN ",
    0x43C4BF48: ("[ENCSEQCTRL]EXEC TIME = %x PIN SUPPLY TIMING = %x REVISED VFCNUM "
                 "= %d"),
    0x43C4BF8F: ("[ENCSEQCTRL]OU StopInfo(NrmlTerm:%x,OuTerm:%x=((%x+%x)*smpl(%x)),"
                 "Stt:%x,Stp:%x(%x)->%x "),
    0x43C4BFE8: ("[ENCSEQCTRL]abcd[%d] eTime[0x%x] cTime[0x%x] revFA[%d] "
                 "FramePos[%d] revTA[%d] vNum[%d]"),
    0x43C4C040: "[ENCSEQCTRL][Begin][odd] ReviseNum Set to zero [%d]",
    0x43C4C075: "[ENCSEQCTRL][Begin][odd] ReviseNum Set to one  [%d]",
    0x43C4C0AA: "[ENCSEQCTRL][Begin][even] ReviseNum Set to zero [%d]",
    0x43C4C0E0: "[ENCSEQCTRL][Begin][even] ReviseNum Set to one  [%d]",
    0x43C4C116: "[ENCSEQCTRL][Term][odd] ReviseNum Set to one [%d]",
    0x43C4C149: "[ENCSEQCTRL][Term][odd] ReviseNum Set to zero  [%d]",
    0x43C4C17E: "[ENCSEQCTRL][Term][even] ReviseNum Set to one [%d]",
    0x43C4C1B2: "[ENCSEQCTRL][Term][even] ReviseNum Set to zero  [%d]",
    0x43C4C1E8: "[ENCSEQCTRL]HighSpeed Rec is set to zero [%d]",
    0x43C4C217: "[ENCSEQCTRL]MCodec%d changed termEncodeVfc %d->%d",
    0x43C4C24A: ("[ENCSEQCTRL]TermEnc TimeInfo = %x, RefTime(VFC) = %x, "
                 "EnsStopTime(VFC) = %x EnsStopTimeAudio(VFC) = %x "),
    0x43C4C2B3: "[ENCSEQCTRL]CheckSendFirstRefTimer = %x ",
    0x43C4C2DD: "[ENCSEQCTRL]CheckSendFirstRefTimer NOP ",
    0x43C4C306: "[ENCSEQCTRL]%s() [%s] Invalid replyId !!!!",
    0x43C4C332: ("[ENCSEQCTRL]AVSC_CID_MPRNTFY_ENC_SA_CONFIRM_EVENT(msgId:0x%x)::"
                 "mid:0x%x,cid:0x%x,err:%x,cdcId:0x%x,replyId:0x%x"),
    0x43C4C3A3: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_OPEN_COMP ERR = %x ",
    0x43C4C3D8: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_CLOSE_COMP ERR = %x ",
    0x43C4C40E: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_INITIALIZE_MOVIE_COMP ERR = %x ",
    0x43C4C44F: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL_COMP ERR = %x ",
    0x43C4C490: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_ENC_PICTURE_COMP ERR = %x ",
    0x43C4C4CC: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_ENC_FINAL_PICTURE_COMP ERR = %x ",
    0x43C4C50E: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_FINALIZE_COMP ERR = %x ",
    0x43C4C547: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_RELEASE_ES_COMP ERR = %x ",
    0x43C4C582: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_RELEASE_PICTURE_NOTIFY ERR = %x ",
    0x43C4C5C4: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_GET_ES_NOTIFY ERR = %x ",
    0x43C4C5FD: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_SET_MOVIE_QUALITY_INFO_COMP ERR = %x ",
    0x43C4C644: "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_SET_FACE_INFO_COMP ERR = %x ",
    0x43C4C682: "[ENCSEQCTRL]ProcAvcMsg: Err = %x, MsgId = %x ",
    0x43C4C6B1: ("[ENCSEQCTRL]BeginEnc TimeInfo = %x, RefTime(VFC) = %x, "
                 "EnsStartTime(VFC) = %x , EncStartTimeAudio(VFC) = %x "),
    0x43C4C71F: "[ENCSEQCTRL]File:%s, Func:%s() ,Line:%d, Stat ",
    0x43C4C74F: ("[ENCSEQCTRL]wai semaphore error, Err:%d, File:%s, Func:%s() "
                 ",Line:%d "),
    0x43C4C796: ("[ENCSEQCTRL]sig semaphore error, Err:%d, File:%s, Func:%s() "
                 ",Line:%d "),
}

# Las 12 MSGID con su id numérico (verificado en el `tbh` de ProcAvcMsg)
MSGIDS = {
    0x8101: ("MSGID_AVC_ENC_VIDEO_OPEN_COMP", 0x43C4C3A3, 0x435D8D82),
    0x8102: ("MSGID_AVC_ENC_VIDEO_CLOSE_COMP", 0x43C4C3D8, 0x435D8DF4),
    0x8103: ("MSGID_AVC_ENC_VIDEO_INITIALIZE_MOVIE_COMP", 0x43C4C40E, 0x435D8E16),
    0x8104: ("MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL_COMP", 0x43C4C44F, 0x435D8E38),
    0x8105: ("MSGID_AVC_ENC_VIDEO_ENC_PICTURE_COMP", 0x43C4C490, 0x435D8E5A),
    0x8106: ("MSGID_AVC_ENC_VIDEO_ENC_FINAL_PICTURE_COMP", 0x43C4C4CC, 0x435D8E7C),
    0x8107: ("MSGID_AVC_ENC_VIDEO_FINALIZE_COMP", 0x43C4C50E, 0x435D8E9E),
    0x8108: ("MSGID_AVC_ENC_VIDEO_RELEASE_ES_COMP", 0x43C4C547, 0x435D8EC0),
    0x8109: ("MSGID_AVC_ENC_VIDEO_SET_MOVIE_QUALITY_INFO_COMP", 0x43C4C5FD,
             0x435D8F2C),
    0x810A: ("MSGID_AVC_ENC_VIDEO_SET_FACE_INFO_COMP", 0x43C4C644, 0x435D8F4E),
    0x8111: ("MSGID_AVC_ENC_VIDEO_RELEASE_PICTURE_NOTIFY", 0x43C4C582, 0x435D8EE2),
    0x8112: ("MSGID_AVC_ENC_VIDEO_GET_ES_NOTIFY", 0x43C4C5C4, 0x435D8F04),
}

FUNCIONES = {
    0x435D6AD0: "ExecSeqAllocUserDataArea",
    0x435D6B3C: "ExecSeqSetSeqParam",
    0x435D6BC8: "ExecSeqApllyUserDataGop",
    0x435D6C94: "ExecSeqApplyUserDataPic",
    0x435D6D60: "ExecSeqMuteAudioCapture",
    0x435D6DF8: "ExecSeqSetEncReadPt",
    0x435D6F04: "ExecSeqInitEsApi",
    0x435D7040: "ExecSeqStillEncState",
    0x435D7190: "ExecSeqErrEncReadyState",
    0x435D74F4: "ExecSeqInActChip",
    0x435D7608: "ExecSeqActEnc",
    0x435D79CC: "ExecSeqEncodeState",
    0x435D7B70: "ExecSeqEncReady2StillState",
    0x435D7BF8: "ExecSeqInactiveState",
    0x435D7D60: "ExecSeqStillEnc",
    0x435D7F34: "CalcEncStartStopTimingForSysHS",
    0x435D84CC: "ExecSeqTermEnc",
    0x435D882C: "ProcMCMsg",
    0x435D8A84: "ExecSeqEncReadyState",
    0x435D8C08: "GetReplyId",
    0x435D8D38: "ProcAvcMsg",
    0x435D900E: "ProcMsg",
    0x435D90AC: "ExecSeqBeginEnc",
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
        o = a - BASE_VADDR
        h = struct.unpack("<H", data[o:o + 2])[0]
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


def _bl_targets(data, lo, hi, targets):
    """Llamadores `bl` de 32 bits (decodificación manual del patrón de bits)."""
    tset = set(targets)
    out = []
    for a in range(lo, hi - 4, 2):
        h1 = _u16(data, a)
        if (h1 & 0xF800) != 0xF000:
            continue
        h2 = _u16(data, a + 2)
        if (h2 & 0xD000) not in (0x9000, 0xD000):
            continue
        s = (h1 >> 10) & 1
        j1 = (h2 >> 13) & 1
        j2 = (h2 >> 11) & 1
        i1 = 1 - (j1 ^ s)
        i2 = 1 - (j2 ^ s)
        imm = (s << 24) | (i1 << 23) | (i2 << 22) | ((h1 & 0x3FF) << 12) | ((h2 & 0x7FF) << 1)
        if s:
            imm -= 1 << 25
        if ((a + 4 + imm) & 0xFFFFFFFF) in tset:
            out.append(a)
    return out


# ------------------------------------------------------------------- cadenas
class TestCadenas:
    def test_conteo_y_rango(self):
        data = _data()
        occ = _strings_with(data)
        assert len(occ) == 46
        starts = {s for _, s, _ in occ}
        assert len(starts) == 46, "las 46 apariciones dan 46 cadenas distintas"
        assert min(starts) == 0x43C4BCE5
        assert max(starts) == 0x43C4C796

    def test_textos_concretos(self):
        data = _data()
        for va, texto in CADENAS.items():
            assert _cstr(data, va) == texto, f"texto cambiado en {hex(va)}"

    def test_todas_empiezan_por_el_token(self):
        data = _data()
        for _, s, texto in _strings_with(data):
            assert texto.startswith("[ENCSEQCTRL]")

    def test_bloque_contiguo_y_fichero_intercalado(self):
        """Entre la primera y la última traza sólo hay el nombre del fichero."""
        data = _data()
        lo, hi = 0x43C4BCE5, 0x43C4C796
        otros = []
        i = lo - BASE_VADDR
        while i <= hi - BASE_VADDR:
            j = i
            while j < len(data) and 32 <= data[j] < 127:
                j += 1
            if j - i >= 3:
                txt = data[i:j].decode("latin1")
                if not txt.startswith("[ENCSEQCTRL]"):
                    otros.append((BASE_VADDR + i, txt))
            i = j + 1
        assert otros == [(0x43C4BD0F, "seqCtrl/mcAvcEncSeqCtrl.cpp")]


# ---------------------------------------------------------------- referencias
class TestReferenciasPic:
    def test_todas_referenciadas(self):
        data = _data()
        pic = _pic_index(data)
        starts = {s for _, s, _ in _strings_with(data)}
        sin = [hex(s) for s in sorted(starts) if not pic.get(s)]
        assert sin == [], f"cadenas sin referencia PIC: {sin}"

    def test_recuento_sitios_y_funciones(self):
        data = _data()
        pic = _pic_index(data)
        pro = _prologues(data)
        starts = {s for _, s, _ in _strings_with(data)}
        sitios = 0
        funcs = set()
        for s in starts:
            for site in pic.get(s, []):
                sitios += 1
                funcs.add(_fstart(pro, site))
        assert sitios == 96
        assert len(funcs) == 32
        assert min(funcs) == 0x435D6AD0
        assert max(funcs) == 0x435D90AC

    def test_sitios_recalculados_de_forma_independiente(self):
        """Cada sitio atribuido a una cadena la resuelve de verdad (regla estricta)."""
        data = _data()
        pic = _pic_index(data)
        starts = {s for _, s, _ in _strings_with(data)}
        total = 0
        for s in starts:
            for site in pic.get(s, []):
                total += 1
                h = _u16(data, site)
                assert (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15
                reg = (((h >> 7) & 1) << 3) | (h & 7)
                found = None
                for la in range(site - 2, site - 4096, -2):
                    lh = _u16(data, la)
                    if (lh & 0xF800) == 0x4800 and ((lh >> 8) & 7) == reg:
                        lit = ((la + 4) & ~3) + ((lh & 0xFF) * 4)
                        found = (_u32(data, lit) + (site + 4)) & 0xFFFFFFFF
                        break
                    if (lh & 0xFF7F) == 0xF85F:
                        h2 = _u16(data, la + 2)
                        if (h2 >> 12) == reg:
                            lit = ((la + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
                            found = (_u32(data, lit) + (site + 4)) & 0xFFFFFFFF
                            break
                assert found == s, f"sitio {hex(site)} no resuelve a {hex(s)}"
        assert total == 96

    def test_macro_generica_48_sitios(self):
        data = _data()
        pic = _pic_index(data)
        assert len(pic.get(0x43C4BCE5, [])) == 48

    def test_sin_punteros_absolutos_de_4_bytes(self):
        """Las cadenas no se referencian por puntero absoluto (esquema PIC puro)."""
        data = _data()
        for va in CADENAS:
            pat = struct.pack("<I", va)
            assert pat not in data, f"puntero absoluto a {hex(va)}"


# ------------------------------------------------------------------ funciones
class TestFunciones:
    def test_firmas_rtti_por_funcion(self):
        """Cada función con nombre referencia su firma `__PRETTY_FUNCTION__`."""
        data = _data()
        pic = _pic_index(data)
        pro = _prologues(data)
        for fn, nombre in FUNCIONES.items():
            idx = bisect.bisect_right(pro, fn)
            fin = pro[idx] if idx < len(pro) else fn + 0x1000
            found = set()
            for dest, sites in pic.items():
                for site in sites:
                    if fn <= site < fin:
                        off = dest - BASE_VADDR
                        if not (0 <= off < len(data)):
                            continue
                        end = off
                        while end < len(data) and 32 <= data[end] < 127:
                            end += 1
                        t = data[off:end].decode("latin1")
                        if f"::{nombre}(" in t:
                            found.add(dest)
            assert found, f"{hex(fn)} no referencia la firma de {nombre}"

    def test_json_consistente(self):
        j = _json()
        assert j["token"] == "[ENCSEQCTRL]"
        assert j["totales"]["cadenas"] == 46
        assert j["totales"]["referenciadas"] == 46
        assert j["totales"]["sin_referencia"] == []
        assert j["totales"]["sitios"] == 96
        assert j["totales"]["funciones"] == 32
        assert j["clase"]["vaddr"] == "0x43c4320f"
        assert j["clase"]["fichero"] == "seqCtrl/mcAvcEncSeqCtrl.cpp"
        assert j["clase"]["vaddr_fichero"] == "0x43c4bd0f"
        assert j["id_modulo_log"].startswith("0x0e")

    def test_json_tiene_las_46_cadenas_con_sus_sitios(self):
        j = _json()
        assert len(j["cadenas"]) == 46
        total = sum(len(c["sitios"]) for c in j["cadenas"])
        assert total == 96
        vaddrs = {c["vaddr"] for c in j["cadenas"]}
        assert vaddrs == {hex(v) for v in CADENAS}

    def test_llamadas_de_entrada_del_modulo(self):
        data = _data()
        calls = _bl_targets(data, BASE_VADDR, BASE_VADDR + len(data),
                            [0x435D90AC, 0x435D7D60, 0x435D84CC, 0x435D882C, 0x435D8D38])
        assert 0x435D6188 in calls      # McAvcEncModeReady -> ExecSeqBeginEnc
        assert 0x435D6100 in calls      # McAvcEncModeReady -> ExecSeqStillEnc
        assert 0x435D3D30 in calls      # McAvcEncModeEncErr -> ExecSeqTermEnc
        assert 0x435D9022 in calls      # ProcMsg -> ProcMCMsg
        assert 0x435D9028 in calls      # ProcMsg -> ProcAvcMsg


# ------------------------------------------------------------ estado y msgids
class TestEstadoYMensajes:
    def test_setter_del_estado_en_offset_0x15B84(self):
        data = _data()
        # 0x435d7160: add.w r4,r4,#0x15800 ; 0x435d7166: add.w r4,r4,#0x384
        assert data[0x435D7160 - BASE_VADDR:0x435D7160 - BASE_VADDR + 4] == \
            bytes.fromhex("04f5ac34")
        assert data[0x435D7166 - BASE_VADDR:0x435D7166 - BASE_VADDR + 4] == \
            bytes.fromhex("04f56174")
        # la escritura del estado nuevo: str r5,[r4] en 0x435d7180
        assert data[0x435D7180 - BASE_VADDR:0x435D7180 - BASE_VADDR + 2] == \
            bytes.fromhex("2560")

    def test_setter_del_estado_tiene_17_llamadores(self):
        """14 dentro del módulo + 3 en los accesores inline de otra TU."""
        data = _data()
        calls = _bl_targets(data, BASE_VADDR, BASE_VADDR + len(data), [0x435D715C])
        assert len(calls) == 17
        dentro = [c for c in calls if 0x435D0000 <= c <= 0x435D9600]
        fuera = [c for c in calls if not (0x435D0000 <= c <= 0x435D9600)]
        assert len(dentro) == 14
        assert sorted(fuera) == [0x43A5D2CA, 0x43A5D38C, 0x43A5D3E2]

    def test_getter_del_estado_en_0x43a5d2da(self):
        """El getter lee un u32 en obj+0x15B84 (0x15800 + 0x384)."""
        data = _data()
        assert data[0x43A5D2DA - BASE_VADDR:0x43A5D2DA - BASE_VADDR + 4] == \
            bytes.fromhex("00f5ac30")
        assert data[0x43A5D2DE - BASE_VADDR:0x43A5D2DE - BASE_VADDR + 4] == \
            bytes.fromhex("00f56170")
        assert data[0x43A5D2E2 - BASE_VADDR:0x43A5D2E2 - BASE_VADDR + 2] == \
            bytes.fromhex("0068")

    def test_estado_7_en_enc_ready2_still(self):
        data = _data()
        assert data[0x435D7BB4 - BASE_VADDR:0x435D7BB4 - BASE_VADDR + 2] == \
            bytes.fromhex("0725")   # movs r5,#7
        assert data[0x435D7BE4 - BASE_VADDR:0x435D7BE4 - BASE_VADDR + 4] == \
            bytes.fromhex("fff7bafa")   # bl 0x435d715c

    def test_ventana_de_ids_y_tabla_tbh(self):
        data = _data()
        # mvn r3,#0x8100 (0x6ff40143) en 0x435d8d3a
        assert data[0x435D8D3A - BASE_VADDR:0x435D8D3A - BASE_VADDR + 4] == \
            bytes.fromhex("6ff40143")
        # ldrh r2,[r1,#2] en 0x435d8d3e
        assert data[0x435D8D3E - BASE_VADDR:0x435D8D3E - BASE_VADDR + 2] == \
            bytes.fromhex("4a88")
        # cmp r3,#0x11 en 0x435d8d46
        assert data[0x435D8D46 - BASE_VADDR:0x435D8D46 - BASE_VADDR + 2] == \
            bytes.fromhex("112b")
        # tbh [pc,r3,lsl#1] en 0x435d8d4c
        assert data[0x435D8D4C - BASE_VADDR:0x435D8D4C - BASE_VADDR + 4] == \
            bytes.fromhex("dfe813f0")
        # tabla: 18 halfwords en 0x435d8d50
        expected = [0x0012, 0x004B, 0x005C, 0x006D, 0x007E, 0x008F, 0x00A0, 0x00B1,
                    0x00E7, 0x00F8] + [0x0109] * 6 + [0x00C2, 0x00D3]
        got = [_u16(data, 0x435D8D50 + 2 * i) for i in range(18)]
        assert got == expected

    def test_nombre_de_cada_msgid_en_su_caso(self):
        """Cada id con nombre tiene su rama y su cadena."""
        data = _data()
        base = 0x435D8D50
        for mid, (nombre, cadena, sitio) in MSGIDS.items():
            idx = mid - 0x8101
            hwv = _u16(data, base + 2 * idx)
            destino = base + 2 * hwv
            assert sitio >= destino, f"{hex(mid)} sitio fuera de su rama"
            assert _cstr(data, cadena).endswith(f"{nombre} ERR = %x ")
            # el sitio del nombre debe resolver a su cadena por PIC
            pic = _pic_index(data)
            assert cadena in pic, f"{hex(cadena)} sin referencia"
            assert sitio in pic[cadena], f"{hex(sitio)} no referencia {hex(cadena)}"

    def test_los_6_ids_sin_nombre_caen_en_la_rama_por_defecto(self):
        data = _data()
        base = 0x435D8D50
        for mid in range(0x810B, 0x8111):
            hwv = _u16(data, base + 2 * (mid - 0x8101))
            assert base + 2 * hwv == 0x435D8F62

    def test_log_call_de_procavcmsg_es_0x8101(self):
        """El primer caso del `tbh` es OPEN_COMP (id 0x8101)."""
        data = _data()
        assert _cstr(data, 0x43C4C3A3).startswith(
            "[ENCSEQCTRL]MSGID_AVC_ENC_VIDEO_OPEN_COMP")


# ------------------------------------------------------------------ tabla O/U
class TestTablaOuCrank:
    def test_57_entradas_de_8_bytes(self):
        data = _data()
        # add r1,pc en 0x435d70aa -> literal 0x435d7150
        lit = _u32(data, 0x435D7150)
        assert (lit + 0x435D70AA + 4) & 0xFFFFFFFF == 0x43B93BF4
        # el bucle recorre 0x39 = 57 entradas de 8 B
        assert data[0x435D7116 - BASE_VADDR:0x435D7116 - BASE_VADDR + 2] == \
            bytes.fromhex("0833")   # adds r3,#8
        assert data[0x435D7118 - BASE_VADDR:0x435D7118 - BASE_VADDR + 2] == \
            bytes.fromhex("392c")   # cmp r4,#0x39

    def test_valores_del_campo_frame_rate(self):
        data = _data()
        base = 0x43B93BF4
        f0 = [_u32(data, base + 8 * i) for i in range(57)]
        assert set(f0) == {2, 3, 4, 5, 6, 7, 8, 9, 10}
        assert f0[0] == 4 and f0[11] == 2 and f0[22] == 6
        assert f0[33] == 5 and f0[43] == 3 and f0[53] == 7
        assert f0[54] == 8 and f0[55] == 9 and f0[56] == 10

    def test_bytes_de_sampling_rate(self):
        data = _data()
        base = 0x43B93BF4
        b4 = {data[base + 8 * i + 4 - BASE_VADDR] for i in range(57)}
        assert b4 == {0x3C, 0x32, 0x1E, 0x18, 0x14, 0x10, 0x0C, 0x0A, 0x08, 0x06,
                      0x04, 0x02, 0x01}
        # el byte devuelto (+5) es 1 en las 57 entradas
        assert {data[base + 8 * i + 5 - BASE_VADDR] for i in range(57)} == {1}


# ---------------------------------------------------------- lineas de fuente
class TestLineasDeFuente:
    def test_linea_1510_en_exec_seq_enc_ready2_still(self):
        data = _data()
        # movw r3,#0x5e6 (=1510) en 0x435d7bcc
        assert data[0x435D7BCC - BASE_VADDR:0x435D7BCC - BASE_VADDR + 4] == \
            bytes.fromhex("40f2e653")
        assert 0x5E6 == 1510  # noqa: PLR0133 -- el valor importa, no la comparación

    def test_linea_1052_en_procmsg(self):
        data = _data()
        # movw r3,#0x41c (=1052) en 0x435d9048
        assert data[0x435D9048 - BASE_VADDR:0x435D9048 - BASE_VADDR + 4] == \
            bytes.fromhex("40f21c43")
        assert 0x41C == 1052  # noqa: PLR0133 -- el valor importa, no la comparación

    def test_id_de_modulo_del_log_es_0x0e(self):
        data = _data()
        # 0x435d716e: movs r1,#0x0e
        assert data[0x435D716E - BASE_VADDR:0x435D716E - BASE_VADDR + 2] == \
            bytes.fromhex("0e21")

    def test_las_82_llamadas_al_logger_usan_el_id_0x0e(self):
        """Todas las llamadas a `log` del módulo pasan `r1 = 0x0e`."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "ln", ROOT / "analysis/s139_encseqctrl/line_numbers.py")
        ln = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ln)
        data = _data()
        pro = [p for p in _prologues(data) if 0x435D6AD0 <= p < 0x435D9300]
        pro.append(0x435D9300)
        md = ln.md
        n = 0
        for k in range(len(pro) - 1):
            insns = list(md.disasm(
                data[pro[k] - BASE_VADDR:pro[k + 1] - BASE_VADDR], pro[k]))
            r1 = None
            for ins in insns:
                m, o = ins.mnemonic, ins.op_str
                if m in ("movs", "mov", "movw") and o.startswith("r1,"):
                    try:
                        r1 = int(o.split("#")[1], 0)
                    except (IndexError, ValueError):
                        r1 = ("var", o)
                elif (m.startswith("ldr") or m in ("add", "adds", "sub", "subs",
                                                   "and", "orr", "eor", "mvn")) \
                        and o.startswith("r1,"):
                    r1 = ("var", o)
                if m == "bl":
                    if o.startswith("#0x") and int(o[1:], 16) in ln.LOGGERS:
                        n += 1
                        assert r1 == 0x0E, f"{hex(ins.address)} usa r1={r1}"
                    r1 = None
        assert n == 82


# ------------------------------------------------------------------ negativos
class TestNegativos:
    """El módulo NO menciona obturador, sensor, exposición ni lectura."""

    def test_sin_terminos_de_obturador_o_sensor(self):
        data = _data()
        textos = [t.lower() for _, _, t in _strings_with(data)]
        for term in ("shut", "silent", "electro", "mech", "curtain", "flicker",
                     "sensor", "imager", "expos", "drive", "readout", "bracket",
                     "sweep", "interval", "jpeg", "liveview"):
            hits = [t for t in textos if term in t]
            assert hits == [], f"'{term}' aparece en {hits}"

    def test_still_y_movie_solo_en_modos_del_codificador(self):
        data = _data()
        occ = _strings_with(data)
        still = [hex(s) for _, s, t in occ if "still" in t.lower()]
        movie = [hex(s) for _, s, t in occ if "movie" in t.lower()]
        assert still == ["0x43c4c44f"]
        assert movie == ["0x43c4c40e", "0x43c4c5fd"]

    def test_imaging_cap_no_mentiona_el_codificador_avc(self):
        data = _data()
        i = 0x43C9B000 - BASE_VADDR
        fin = 0x43CD0000 - BASE_VADDR
        st = None
        cur = bytearray()
        hits = []
        while i < fin:
            c = data[i]
            if 32 <= c < 127:
                if st is None:
                    st = i
                cur.append(c)
            else:
                if st is not None:
                    t = cur.decode("latin1")
                    if t.startswith("[IMAGING_CAP]") and (
                            "AVC" in t or "MCodec" in t or "Movie" in t):
                        hits.append(t)
                st = None
                cur = bytearray()
            i += 1
        assert hits == []


# ---------------------------------------------------------------- diferencial
class TestDiferencial:
    def test_a7s_mismo_conteo_y_textos_identicos(self):
        a6 = _data()
        a7 = _data(A7S_BIN)
        t6 = {t for _, _, t in _strings_with(a6)}
        t7 = {t for _, _, t in _strings_with(a7)}
        assert len(t6) == 46 and len(t7) == 46
        assert t6 == t7

    def test_a7s_tabla_tbh_byte_a_byte_identica(self):
        a6 = _data()
        a7 = _data(A7S_BIN)
        t6 = a6[0x435D8D50 - BASE_VADDR:0x435D8D50 - BASE_VADDR + 36]
        t7 = a7[0x435D69E0 - BASE_VADDR:0x435D69E0 - BASE_VADDR + 36]
        assert t6 == t7
        # y el prólogo de ProcAvcMsg
        p6 = a6[0x435D8D38 - BASE_VADDR:0x435D8D38 - BASE_VADDR + 20]
        p7 = a7[0x435D69C8 - BASE_VADDR:0x435D69C8 - BASE_VADDR + 20]
        assert p6 == p7

    def test_a6300_tiene_50_cadenas_y_5_nuevas(self):
        a3 = _data(A6300_BIN)
        occ = _strings_with(a3)
        assert len({s for _, s, _ in occ}) == 50
        a6 = _data()
        t6 = {t for _, _, t in _strings_with(a6)}
        t3 = {t for _, _, t in occ}
        assert len(t6 & t3) == 45
        assert len(t6 - t3) == 1
        assert len(t3 - t6) == 5
        assert "quickRestartVfc" in "\n".join(t3 - t6)
        assert "Audio Buffer Overflow" in "\n".join(t3 - t6)

    def test_diferencial_en_el_json(self):
        j = _json()
        a7 = j["diferencial"]["A7S_fw320"]
        assert a7["ocurrencias_token"] == 46
        assert a7["textos"] == 46
        assert a7["comunes"] == 46
        assert a7["solo_a6000"] == []
        assert a7["solo_modelo"] == []
        a3 = j["diferencial"]["A6300_fw201"]
        assert a3["ocurrencias_token"] == 50
        assert a3["comunes"] == 45
        assert len(a3["solo_modelo"]) == 5
        assert len(a3["solo_a6000"]) == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
