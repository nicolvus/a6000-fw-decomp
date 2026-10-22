"""S177 — tests del módulo [CAM_FUNC_MGR] contra los BYTES REALES del firmware.

Cada test comprueba direcciones concretas: si una dirección cambia en el firmware
(o en el mapa de referencias), el test falla.

Método de referencias: regla PIC **estricta** (canónica del repo,
`analysis/s106_imaging_cap/pic_xref_methodology.md`):
    ldr rX,[pc,#imm]  ->  W = literal del pool
    add rX,pc         ->  destino = W + (dirección_del_add + 4)
El par se empareja con el `ldr` más cercano del mismo registro (ventana 4 KB).
"""
import bisect
import json
import struct
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = ROOT / "analysis/rea-independent/input/av-cam.bin"
A7S = (ROOT / "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
CFM_JSON = ROOT / "analysis/s177_cam_func_mgr/cam_func_mgr.json"

B = BIN.read_bytes()
A7 = A7S.read_bytes()
A63 = A6300.read_bytes()

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)


def u16(a, blob=None):
    blob = B if blob is None else blob
    return struct.unpack_from("<H", blob, a - BASE)[0]


def u32(a, blob=None):
    blob = B if blob is None else blob
    return struct.unpack_from("<I", blob, a - BASE)[0]


def cstr(a, blob=None):
    blob = B if blob is None else blob
    o = a - BASE
    e = blob.find(b"\x00", o)
    return blob[o:e].decode("ascii", "replace")


def disasm1(a, blob=None):
    """Desensambla una instrucción Thumb en la dirección `a`."""
    blob = B if blob is None else blob
    code = blob[a - BASE:a - BASE + 4]
    for ins in MD.disasm(code, a):
        return f"{ins.mnemonic} {ins.op_str}".strip()
    return None


def pic_ldr_sites(lo, hi):
    """[(addr, reg, valor_del_pool, pool_addr)] de los `ldr rX,[pc,#imm]`."""
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(B) - 8:
            a += 2
            continue
        h = u16(a)
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = u16(a + 2)
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= len(B) - 4:
            out.append((a, reg, u32(lit), lit))
        a += 2
    return out


def pic_add_sites(lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        if o < 0 or o > len(B) - 4:
            a += 2
            continue
        h = u16(a)
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            out.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    return out


def strict_dest(site):
    """Destino de un `add rX,pc` según la regla estricta, o None."""
    by_reg = {}
    for a, reg, w, lit in pic_ldr_sites(site - 4096, site + 16):
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    h = u16(site)
    if not ((h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15):
        return None
    reg = (((h >> 7) & 1) << 3) | (h & 7)
    v = by_reg.get(reg)
    if not v:
        return None
    ks = [x[0] for x in v]
    i = bisect.bisect_left(ks, site) - 1
    if i < 0:
        return None
    la, w, lit = v[i]
    if site - la > 4096:
        return None
    return (w + site + 4) & 0xFFFFFFFF


_STRICT_CACHE = {}


def strict_map(blob=None):
    """Mapa {sitio_add: destino} de toda la imagen con la regla estricta (cacheado)."""
    key = id(blob) if blob is not None else 0
    if key in _STRICT_CACHE:
        return _STRICT_CACHE[key]
    blob = B if blob is None else blob
    ldrs = []
    a = BASE
    while a < BASE + len(blob):
        o = a - BASE
        if o < 0 or o > len(blob) - 8:
            a += 2
            continue
        h = struct.unpack_from("<H", blob, o)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:
            h2 = struct.unpack_from("<H", blob, o + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None and 0 <= lit - BASE <= len(blob) - 4:
            ldrs.append((a, reg, struct.unpack_from("<I", blob, lit - BASE)[0], lit))
        a += 2
    by_reg = {}
    for a, reg, w, lit in ldrs:
        by_reg.setdefault(reg, []).append((a, w, lit))
    for v in by_reg.values():
        v.sort()
    keys = {r: [x[0] for x in v] for r, v in by_reg.items()}
    out = {}
    a = BASE
    while a < BASE + len(blob):
        o = a - BASE
        if o < 0 or o > len(blob) - 4:
            a += 2
            continue
        h = struct.unpack_from("<H", blob, o)[0]
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            reg = (((h >> 7) & 1) << 3) | (h & 7)
            v = by_reg.get(reg)
            if v:
                ks = keys[reg]
                i = bisect.bisect_left(ks, a) - 1
                if i >= 0:
                    la, w, lit = v[i]
                    if a - la <= 4096:
                        out[a] = (w + a + 4) & 0xFFFFFFFF
        a += 2
    _STRICT_CACHE[key] = out
    return out


# ---------------------------------------------------------------------------
# Las 43 trazas [CAM_FUNC_MGR]: (vaddr, texto exacto)
# ---------------------------------------------------------------------------
PREFIX = "[CAM_FUNC_MGR]: "
STRINGS = [
    (0x43ca12af, "[CAM_FUNC_MGR]: CAPCON WARNING! FILE:%s LINE=%d func:%s param=%x %x %x"),
    (0x43ca12f6, "[CAM_FUNC_MGR]: SyncProcMargin[usec] HS0:%u HS1:%u HS2:%u "
                 "HS3@CPU2:%u HS3@CPU0(IDT):%u HS3@CPU3(RCH):%u VDDrive:%u VDPost:%u"),
    (0x43caefe8, "[CAM_FUNC_MGR]: ERROR !!! osal_err:0x%04x %s : %d"),
    (0x43caf036, "[CAM_FUNC_MGR]: SetCapMode:Invalid CapMode[0x%x: %d: %d: %d: %d]"),
    (0x43caf077, "[CAM_FUNC_MGR]: receive[%d,%d] before comp[%d,%d] (QUEUEING)"),
    (0x43caf0b4, "[CAM_FUNC_MGR]: receive[%d,%d] before comp[%d,%d] (FAILED)"),
    (0x43caf136, "[CAM_FUNC_MGR]: ERROR !!! osalErr:0x%04x %s : %d"),
    (0x43caf17d, "[CAM_FUNC_MGR]: ERROR !!! LSI_NUM_TYPE:0x%04x %s : %d"),
    (0x43caf1b3, "[CAM_FUNC_MGR]: UNKNOWN EID !!! type:[0x%02x] %s : %d"),
    (0x43caf1e9, "[CAM_FUNC_MGR]: ERROR !!! type:[0x%02x] %s : %d"),
    (0x43caf219, "[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf26f, "[CAM_FUNC_MGR]: [LRB]APP Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf2bd, "[CAM_FUNC_MGR]: [LRB]APP_CMP Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf30f, "[CAM_FUNC_MGR]: [LRB]REQ_VSYNC_CUST_SND Snd type_id:0x%02x "
                 "from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x"),
    (0x43caf37e, "[CAM_FUNC_MGR]: [LRB]VSYNC_CUST Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x vsync_type:0x%02x"),
    (0x43caf3e5, "[CAM_FUNC_MGR]: [LRB]VSYNC_CUST_CMP Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x vsync_type:0x%02x"),
    (0x43caf450, "[CAM_FUNC_MGR]: [LRB]REQ_V2ND_SND Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf4a7, "[CAM_FUNC_MGR]: [LRB]V2ND Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf4f6, "[CAM_FUNC_MGR]: [LRB]V2ND_CMP Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf549, "[CAM_FUNC_MGR]: [LRB]REQ_FSPSUM_SND Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf5a2, "[CAM_FUNC_MGR]: [LRB]FSPSUM Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf5f3, "[CAM_FUNC_MGR]: [LRB]FSPSUM_CMP Snd type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf648, "[CAM_FUNC_MGR]: ERROR !!! LRBridge SndV2ndLatchCmp. %s : %d"),
    (0x43caf684, "[CAM_FUNC_MGR]: ERROR !!! LRBridge SndApp2Cmp. %s : %d"),
    (0x43caf6bb, "[CAM_FUNC_MGR]: [LRB]REQ_APP_SND Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf711, "[CAM_FUNC_MGR]: [LRB]APP Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf75f, "[CAM_FUNC_MGR]: [LRB]APP_CMP Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf7b1, "[CAM_FUNC_MGR]: [LRB]REQ_VSYNC_CUST_SND Rsv type_id:0x%02x "
                 "from_lsi:0x%02x req_seq_id:0x%02x vsync_type:0x%02x"),
    (0x43caf820, "[CAM_FUNC_MGR]: [LRB]VSYNC_CUST Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x vsync_type:0x%02x"),
    (0x43caf887, "[CAM_FUNC_MGR]: [LRB]VSYNC_CUST_CMP Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x vsync_type:0x%02x"),
    (0x43caf8f2, "[CAM_FUNC_MGR]: [LRB]REQ_V2ND_SND Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf949, "[CAM_FUNC_MGR]: [LRB]V2ND Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf998, "[CAM_FUNC_MGR]: [LRB]V2ND_CMP Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43caf9eb, "[CAM_FUNC_MGR]: [LRB]REQ_FSPSUM_SND Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43cafa44, "[CAM_FUNC_MGR]: [LRB]FSPSUM Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43cafa95, "[CAM_FUNC_MGR]: [LRB]FSPSUM_CMP Rsv type_id:0x%02x from_lsi:0x%02x "
                 "req_seq_id:0x%02x"),
    (0x43cb009b, "[CAM_FUNC_MGR]: Unexpected ExpFocusTransition : message [%x] timing [%d]"),
    (0x43cb010a, "[CAM_FUNC_MGR]: Unexpected SleepTransition : message [%x] timing [%d]"),
    (0x43cb0150, "[CAM_FUNC_MGR]: unknown message in Imager Sleep Process: %x"),
    (0x43cb027c, "[CAM_FUNC_MGR]: #### Execute unretract command!!"),
    (0x43cb02ad, "[CAM_FUNC_MGR]: IsNeedScanAf (%d)"),
    (0x43cb02cf, "[CAM_FUNC_MGR]: IsNeedAe     (%d)"),
    (0x43cb02f1, "[CAM_FUNC_MGR]: Pseudo AF Stop %d"),
]

# Los 57 sitios de emisión (regla PIC estricta): sitio -> dirección de la cadena
SITES = {
    0x43787bc4: 0x43ca12af, 0x43787c48: 0x43ca12f6,
    0x43801ac6: 0x43caefe8, 0x43801b1e: 0x43caefe8,
    0x43801d02: 0x43caefe8, 0x43801d58: 0x43caefe8,
    0x43803edc: 0x43caf036, 0x43803ff0: 0x43caf077, 0x4380401e: 0x43caf0b4,
    0x438056d2: 0x43caf136, 0x43805736: 0x43caf17d,
    0x4380579c: 0x43caf136, 0x438057c8: 0x43caf136, 0x43805820: 0x43caf136,
    0x43805890: 0x43caefe8, 0x438058e8: 0x43caefe8,
    0x43805a6c: 0x43caf1b3, 0x43805ab2: 0x43caf1e9,
    0x43805ed6: 0x43caf219, 0x43805f0a: 0x43caf26f, 0x43805f40: 0x43caf2bd,
    0x43805f7a: 0x43caf30f, 0x43805fb8: 0x43caf37e, 0x43805ff6: 0x43caf3e5,
    0x4380602e: 0x43caf450, 0x43806064: 0x43caf4a7, 0x4380609a: 0x43caf4f6,
    0x438060d0: 0x43caf549, 0x43806106: 0x43caf5a2, 0x4380613c: 0x43caf5f3,
    0x438061e6: 0x43caefe8, 0x4380623e: 0x43caefe8,
    0x43806422: 0x43caefe8, 0x4380647a: 0x43caefe8,
    0x438064ea: 0x43caefe8, 0x43806542: 0x43caefe8,
    0x438065ce: 0x43caf648, 0x4380663a: 0x43caf648, 0x438066a6: 0x43caf684,
    0x43806702: 0x43caf6bb, 0x43806736: 0x43caf711, 0x4380676c: 0x43caf75f,
    0x438067a6: 0x43caf7b1, 0x438067e4: 0x43caf820, 0x43806822: 0x43caf887,
    0x4380685a: 0x43caf8f2, 0x43806890: 0x43caf949, 0x438068c6: 0x43caf998,
    0x438068fc: 0x43caf9eb, 0x43806932: 0x43cafa44, 0x43806968: 0x43cafa95,
    0x4380953c: 0x43cb009b, 0x438096c0: 0x43cb010a, 0x438097c6: 0x43cb0150,
    0x43809c86: 0x43cb027c, 0x43809d20: 0x43cb02ad, 0x43809d42: 0x43cb02cf,
}

# RTTI: nombre de clase -> dirección de la cadena (las 18 de Camera::Function)
RTTI = {
    0x43cafc36: "N6Camera8Function18ExecStateTransBaseE",
    0x43cafc5d: "N6Camera8Function16CapconEventQueueE",
    0x43cafc82: "N6Camera8Function15EventDispatcherE",
    0x43cafccd: "N6Camera8Function12EventHandlerE",
    0x43cafcee: "N6Camera8Function11ExecHandlerE",
    0x43cafd0e: "N6Camera8Function15ExecModeHandlerE",
    0x43cafdd8: "N6Camera8Function18ExecReleaseHandlerE",
    0x43cafdff: "N6Camera8Function10HandleInfoE",
    0x43cb001c: "N6Camera8Function12ReplyHandlerE",
    0x43cb003d: "N6Camera8Function11SendChannelE",
    0x43cb00e4: "N6Camera8Function17ExecExpFocusTransE",
    0x43cb018c: "N6Camera8Function14ExecSleepTransE",
    0x43cb021d: "N6Camera8Function7CamMainE",
    0x43cb0313: "N6Camera8Function7CamUserE",
    0x43cb03a6: "N6Camera8Function16CameraBackGroundE",
    0x43cb03cb: "N6Camera8Function4FaceE",
    0x43cb03f4: "N6Camera8Function7ReleaseE",
    0x43ccabb4: "N6Camera8Function15ExecHandlerBaseE",
}

# Ficheros fuente del subsistema: dirección -> texto
FILES = {
    0x43ca124e: "api/capcon_api_cam.cpp",
    0x43caeef6: "Function/FunctionMessage.cpp",
    0x43caf01a: "Function/FunctionNotify.cpp",
    0x43caf0ef: "Function/FunctionSetParam.cpp",
    0x43caf167: "Function/LRBridge.cpp",
    0x43cafca6: "EventDispatcher.cpp",
    0x43cafd3f: "ExecModeHandler.cpp",
    0x43cafda7: "ExecReleaseHandler.cpp",
    0x43cafed5: "RawDevHandler.cpp",
    0x43cb000b: "ReplyHandler.cpp",
    0x43cb005d: "SendChannel.cpp",
    0x43cb0072: "api/capcon_api_businessif.cpp",
    0x43cb01c3: "tsk/tsk_capcon_sequence.cpp",
    0x43cb01f3: "tsk/tsk_rawdev_sequence.cpp",
    0x43cb0268: "wrapper/CamMain.cpp",
    0x43cb032e: "wrapper/CamUser.cpp",
    0x43cb0389: "wrapper/CameraBackGround.cpp",
    0x43cb03e3: "wrapper/Face.cpp",
}

# Tabla de funciones: base, paso y (nombre, id) de las 65 entradas
TABLE_BASE = 0x43ff17b8
TABLE_STRIDE = 12
TABLE = [
    (0x0, "UNKNOWN"), (0x1, "REQ_MOVIE"), (0x2, "REQ_MOVIE_REC"), (0x3, "REQ_STILL_EE"),
    (0x4, "REQ_PB"), (0x5, "REQ_HOLD"), (0x6, "REQ_HS_EE"), (0x7, "REQ_HS_PLAY"),
    (0x8, "REQ_PANORAMA_EE"), (0x9, "REQ_POWER_OFF"), (0xa, "REQ_CUSTOM_WB"),
    (0xb, "REQ_GOLF_EE"), (0xc, "REQ_GOLF_SOUND_DET_END"), (0xd, "REQ_GOLF_PLAY"),
    (0x8101, "REQ_TOUCH_SCAN"), (0x11, "REQ_TOUCH_NOSCAN"), (0xe, "REQ_DUALREC_DEV"),
    (0x8100, "REQ_MOVIE_EO"), (0xf, "REQ_BB_OUT"), (0x8000, "REQ_CLEANING"),
    (0x10, "RAW_CONT_CAP_CANCEL"), (0x16, "REQ_AUTO_BB"), (0x17, "REQ_SHS_EE"),
    (0x18, "REQ_SHS_REC"), (0x19, "REQ_FELOCK_ON"), (0x8102, "REQ_FELOCK_OFF"),
    (0x12, "REQ_PREVIEW_MODE"), (0x13, "REQ_EXP_FOCUSED_ON"),
    (0x15, "REQ_EXP_FOCUSED_OFF"), (0x100, "REQ_BKF_AF"), (0x101, "REQ_CAPTURE_START"),
    (0x102, "REQ_CAPTURE_END"), (0x103, "REQ_AF_START"), (0x8301, "REQ_AF_STOP"),
    (0x8302, "REQ_AE_START"), (0x104, "REQ_AE_STOP"), (0x300, "REQ_AF_CHANGE"),
    (0x301, "REPLY_MOVIE"), (0x302, "REPLY_MOVIE_REC"), (0x303, "REPLY_STILL_EE"),
    (0x304, "REPLY_PB"), (0x305, "REPLY_HOLD"), (0x306, "REPLY_HS_EE"),
    (0x307, "REPLY_HS_PLAY"), (0x308, "REPLY_PANORAMA_EE"), (0x309, "REPLY_POWER_OFF"),
    (0x30a, "REPLY_CUSTOM_WB"), (0x30b, "REPLY_GOLF_EE"),
    (0x30c, "REPLY_GOLF_SOUND_DET_END"), (0x30e, "REPLY_GOLF_PLAY"),
    (0x310, "REPLY_PRELIGHT"), (0x311, "REPLY_SCANAF"), (0x312, "REPLY_S1"),
    (0x313, "REPLY_TOUCH_SCAN_1"), (0x314, "REPLY_TOUCH_SCAN_2"),
    (0x316, "REPLY_TOUCH_SCAN_3"), (0x319, "REPLY_DUALREC_DEV"),
    (0x31e, "REPLY_MOVIE_EO"), (0x326, "REPLY_AUTO_BB"), (0x327, "REPLY_SHS_EE"),
    (0x328, "REPLY_SHS_REC"), (0xfff, "REPLY_FE_LOCK"), (0x329, "REPLY_ERR"),
    (0xf00, "REPLY_FACE_DET_OFF"), (0x10, "MSG_NONE"),
]

# Los 12 type_id del LRB: (dirección de la comparación, valor esperado)
LRB_TYPE_IDS = [
    (0x43805ef6, 1, "APP"), (0x43805f2a, 2, "APP_CMP"),
    (0x4380601a, 3, "REQ_V2ND_SND"), (0x4380604e, 4, "V2ND"),
    (0x43806084, 5, "V2ND_CMP"), (0x43805f60, 6, "REQ_VSYNC_CUST_SND"),
    (0x43805f9e, 7, "VSYNC_CUST"), (0x43805fdc, 8, "VSYNC_CUST_CMP"),
    (0x438060ba, 9, "REQ_FSPSUM_SND"), (0x438060f0, 10, "FSPSUM"),
    (0x43806126, 11, "FSPSUM_CMP"),
]

# Traza nueva: id de módulo 3 y nivel 0xd, fijados justo antes de cada llamada
LOG_MODULE_ID = 3
LOG_LEVEL = 13


def imm_of(txt):
    """Inmediato decimal de una instrucción (el último `#N`)."""
    part = txt.rsplit("#", 1)[-1].split(",")[0].split("]")[0].strip()
    return int(part, 0)


class TestS177Strings(unittest.TestCase):
    def test_43_cadenas_en_su_direccion(self):
        self.assertEqual(len(STRINGS), 43)
        for addr, txt in STRINGS:
            with self.subTest(addr=hex(addr)):
                self.assertEqual(cstr(addr), txt)

    def test_rango_de_las_cadenas(self):
        self.assertEqual(min(a for a, _ in STRINGS), 0x43ca12af)
        self.assertEqual(max(a for a, _ in STRINGS), 0x43cb02f1)

    def test_prefijo_de_16_bytes_y_gemelo_en_mas16(self):
        """Las 43 cadenas tienen el literal ORIGINAL 16 bytes más allá."""
        self.assertEqual(len(PREFIX), 16)
        for addr, txt in STRINGS:
            with self.subTest(addr=hex(addr)):
                self.assertTrue(txt.startswith(PREFIX))
                self.assertEqual(cstr(addr + 16), txt[len(PREFIX):])

    def test_numero_de_ocurrencias_del_token(self):
        self.assertEqual(B.count(b"[CAM_FUNC_MGR]"), 43)
        self.assertEqual(A7.count(b"[CAM_FUNC_MGR]"), 0)
        self.assertEqual(A63.count(b"[CAM_FUNC_MGR]"), 0)

    def test_nucleos_presentes_en_las_otras_fw(self):
        for addr, txt in STRINGS:
            core = txt[len(PREFIX):]
            with self.subTest(addr=hex(addr)):
                self.assertEqual(A7.count(core.encode()), 1)
        # en el A6300 falta sólo la cadena muerta
        faltan = [a for a, t in STRINGS
                  if A63.count(t[len(PREFIX):].encode()) != 1]
        self.assertEqual(faltan, [0x43cb02f1])

    def test_cadena_muerta_sin_referencias(self):
        """`Pseudo AF Stop %d` (0x43cb02f1): 0 refs PIC y 0 punteros absolutos."""
        addr = 0x43cb02f1
        self.assertEqual(cstr(addr), "[CAM_FUNC_MGR]: Pseudo AF Stop %d")
        for site, dest in strict_map().items():
            if dest == addr:
                self.fail(f"referencia PIC inesperada en {site:#x}")
        pat = struct.pack("<I", addr)
        self.assertEqual(B.count(pat), 0)

    def test_negativo_para_la_linea_del_obturador(self):
        for term in ("shutter", "silent", "curtain", "electro", "mech", "expos",
                     "iso", "apert", "sensor", "shut", "svd", "shd", "spl"):
            for addr, txt in STRINGS:
                with self.subTest(term=term, addr=hex(addr)):
                    self.assertNotIn(term, txt.lower())


class TestS177Sites(unittest.TestCase):
    def test_57_sitios_resuelven_a_su_cadena(self):
        self.assertEqual(len(SITES), 57)
        for site, sva in SITES.items():
            with self.subTest(site=hex(site)):
                self.assertEqual(strict_dest(site), sva)

    def test_los_sitios_cubren_las_42_cadenas_vivas(self):
        cubiertas = set(SITES.values())
        vivas = {a for a, _ in STRINGS if a != 0x43cb02f1}
        self.assertEqual(cubiertas, vivas)

    def test_no_hay_mas_sitios_que_los_declarados(self):
        """Recuento independiente: cada `add rX,pc` que apunta a una cadena
        [CAM_FUNC_MGR] debe estar en la lista de sitios."""
        declarados = set(SITES)
        vistos = set()
        for site, dest in strict_map().items():
            if isinstance(dest, int) and cstr(dest).startswith("[CAM_FUNC_MGR]"):
                vistos.add(site)
        self.assertEqual(vistos, declarados)


class TestS177LogDuo(unittest.TestCase):
    """La fw3.21 duplica la traza: nueva (módulo 3) + antigua (intacta)."""

    def test_ejemplo_canonico_del_LRB(self):
        # 0x43805ed6: traza nueva (prefijo) ...
        self.assertEqual(strict_dest(0x43805ed6), 0x43caf219)
        self.assertEqual(disasm1(0x43805ed8), "bl #0x43805604")
        # ... y traza antigua 16 bytes más allá, con la función de log clásica
        self.assertEqual(strict_dest(0x43805ee0), 0x43caf229)
        self.assertEqual(disasm1(0x43805ee6), "bl #0x43902718")

    def test_id_de_modulo_3_y_nivel_13_en_los_sitios(self):
        for site in (0x43805ed6, 0x438056d2, 0x43806702, 0x43803ff0, 0x43809d20):
            with self.subTest(site=hex(site)):
                ventana = []
                code = B[site - 48 - BASE:site + 16 - BASE]
                for ins in MD.disasm(code, site - 48):
                    ventana.append(f"{ins.mnemonic} {ins.op_str}".strip())
                self.assertTrue(any(t.startswith("movs r0, #3") for t in ventana), ventana)
                self.assertTrue(any(t.startswith("movs r1, #0xd") for t in ventana), ventana)

    def test_fichero_y_linea_en_la_traza_nueva(self):
        self.assertEqual(cstr(0x43caf167), "Function/LRBridge.cpp")
        self.assertEqual(strict_dest(0x438061ea), 0x43caf167)
        self.assertIn("0x7de", disasm1(0x438061ec))

    def test_la_traza_antigua_no_cambia_en_las_otras_fw(self):
        """En la A7S y el A6300 sólo existe la traza antigua (sin prefijo)."""
        self.assertEqual(strict_map(A7)[0x437ac63e], 0x43ca7108)
        self.assertEqual(disasm1(0x437ac642, A7), "bl #0x438f7114")
        self.assertEqual(strict_map(A63)[0x437f621e], 0x43dacf4f)
        self.assertEqual(disasm1(0x437f6222, A63), "bl #0x43986518")
        # y el texto en las otras fw es el MISMO sin el prefijo
        self.assertEqual(cstr(0x43ca7108, A7),
                         "[LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x "
                         "req_seq_id:0x%02x")
        self.assertEqual(cstr(0x43dacf4f, A63),
                         "[LRB]REQ_APP_SND Snd type_id:0x%02x from_lsi:0x%02x "
                         "req_seq_id:0x%02x")

    def test_log_antiguo_de_la_A6000(self):
        self.assertEqual(disasm1(0x43805ee6), "bl #0x43902718")
        self.assertEqual(cstr(0x43902718 - 0x43902718 + 0x43ca3c34),
                         "ERROR !!! osal_err:0x%04x %s : %d")


class TestS177RttiAndFiles(unittest.TestCase):
    def test_18_clases_rtti_en_su_direccion(self):
        self.assertEqual(len(RTTI), 18)
        for addr, nombre in RTTI.items():
            with self.subTest(addr=hex(addr)):
                self.assertEqual(cstr(addr), nombre)

    def test_las_18_clases_existen_en_las_tres_fw(self):
        for nombre in RTTI.values():
            with self.subTest(nombre=nombre):
                self.assertEqual(B.count(nombre.encode()), 1)
                self.assertEqual(A7.count(nombre.encode()), 1)
                self.assertEqual(A63.count(nombre.encode()), 1)

    def test_ficheros_fuente_en_su_direccion(self):
        for addr, nombre in FILES.items():
            with self.subTest(addr=hex(addr)):
                self.assertEqual(cstr(addr), nombre)

    def test_referencia_pic_al_fichero_LRBridge(self):
        self.assertEqual(strict_dest(0x438056d6), 0x43caf167)
        self.assertEqual(strict_dest(0x438061ea), 0x43caf167)
        self.assertEqual(strict_dest(0x438066a8), 0x43caf167)


class TestS177FunctionTable(unittest.TestCase):
    def test_tabla_de_65_entradas(self):
        self.assertEqual(len(TABLE), 65)
        for k, (idv, nombre) in enumerate(TABLE):
            slot = TABLE_BASE + TABLE_STRIDE * k
            with self.subTest(k=k):
                self.assertEqual(cstr(u32(slot + 4)), nombre)
                self.assertEqual(u32(slot + 8), idv)

    def test_tabla_identica_en_la_A7S(self):
        base7 = 0x43ff65d4
        for k, (idv, nombre) in enumerate(TABLE):
            slot = base7 + TABLE_STRIDE * k
            with self.subTest(k=k):
                self.assertEqual(cstr(u32(slot + 4, A7), A7), nombre)
        # ids idénticos salvo el último (MSG_NONE), artefacto de disposición
        for k, (idv, _n) in enumerate(TABLE[:-1]):
            slot = base7 + TABLE_STRIDE * k
            self.assertEqual(u32(slot + 8, A7), idv)

    def test_la_tabla_no_existe_en_el_A6300(self):
        self.assertEqual(A63.count(b"REPLY_"), 0)
        self.assertEqual(A63.count(b"MSG_NONE"), 0)
        self.assertEqual(A63.count(b"RAW_CONT_CAP_CANCEL"), 0)
        self.assertEqual(A63.count(b"FUNC <= "), 0)
        self.assertEqual(B.count(b"FUNC <= "), 4)
        self.assertEqual(A7.count(b"FUNC <= "), 4)

    def test_origenes_de_la_tabla(self):
        """`origin` se escribe en runtime: USER 26, BG 3, REL 7, CAM 27, ??? 2."""
        for addr, txt in ((0x43ca1373, "FUNC <= USER"), (0x43ca1380, "FUNC <= BG  "),
                          (0x43ca138d, "FUNC <= REL "), (0x43ca139a, "FUNC <= CAM "),
                          (0x43ca13a7, "???         ")):
            with self.subTest(addr=hex(addr)):
                self.assertEqual(cstr(addr), txt)
        # el init escribe el origin de MSG_NONE (offset +0x2f8) y de UNKNOWN (+4)
        self.assertEqual(disasm1(0x43787e86), "str.w r2, [r3, #0x2f8]")
        self.assertEqual(disasm1(0x43787e8e), "str r2, [r3, #4]")


class TestS177LrbAndDispatcher(unittest.TestCase):
    def test_12_type_id_del_LRB(self):
        for addr, valor, _nombre in LRB_TYPE_IDS:
            with self.subTest(addr=hex(addr)):
                txt = disasm1(addr)
                self.assertIsNotNone(txt)
                self.assertTrue(txt.startswith("cmp "), txt)
                self.assertEqual(imm_of(txt), valor)

    def test_type_id_0_de_REQ_APP_SND(self):
        self.assertEqual(disasm1(0x43805ec2), "cbnz r3, #0x43805eea")

    def test_despachador_con_tbb_de_49_casos(self):
        self.assertIn("sub.w r2, r3, #0x3000", disasm1(0x4380599a))
        self.assertIn("cmp r2, #0x30", disasm1(0x4380599e))
        self.assertEqual(disasm1(0x438059a2), "tbb [pc, r2]")
        base = (0x438059a2 + 4) & ~3
        self.assertEqual(base, 0x438059a4)
        # 49 entradas de 2 bytes: idx 47 -> rama VSYNC_CUST Snd del LRB,
        # idx 25 -> rama *Rsv* del LRB
        def case_target(i):
            off = struct.unpack_from("<H", B, base + 2 * i - BASE)[0]
            return base + 2 * off
        self.assertEqual(case_target(47), 0x43805fb0)
        self.assertEqual(case_target(25), 0x43805a36)
        # la tabla no puede extenderse más allá del último caso
        self.assertEqual(imm_of(disasm1(0x4380599e)), 0x30)

    def test_marcas_de_temporizacion_LR(self):
        for addr, txt in ((0x43cafaea, "LR REQAPP Start"), (0x43cafafa, "LR REQAPP End"),
                          (0x43cafb08, "LR APP Start"), (0x43cafb15, "LR APP End"),
                          (0x43cafc00, "LR FSP Start"), (0x43cafc28, "LR FSPCMP End")):
            with self.subTest(addr=hex(addr)):
                self.assertEqual(cstr(addr), txt)

    def test_SetCapMode_valida_el_modo(self):
        self.assertEqual(strict_dest(0x43803edc), 0x43caf036)
        self.assertIn("cmp r1, #0x1d", disasm1(0x43803e98))


class TestS177Json(unittest.TestCase):
    """El JSON del hito debe ser coherente con los bytes."""

    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CFM_JSON.read_text())

    def test_contadores(self):
        c = self.data["contadores"]
        self.assertEqual(c["n_cadenas_A6000"], 43)
        self.assertEqual(c["n_ocurrencias_token_A7S"], 0)
        self.assertEqual(c["n_ocurrencias_token_A6300"], 0)
        self.assertEqual(c["n_sitios_pic_regla_estricta"], 57)
        self.assertEqual(c["n_funciones_emisoras"], 25)
        self.assertEqual(c["n_cadenas_muertas"], 1)
        self.assertEqual(c["cadenas_muertas"], ["0x43cb02f1"])
        self.assertEqual(c["n_pares_pic_verificados_a_mano"], 57)
        self.assertEqual(c["n_pares_pic_sin_reuso_registro"], 57)
        self.assertEqual(c["n_con_gemelo_exacto_en_mas16"], 43)
        self.assertEqual(c["n_nucleos_en_A7S"], 43)
        self.assertEqual(c["n_nucleos_en_A6300"], 42)
        self.assertEqual(c["n_clases_rtti_Camera_Function"], 18)
        self.assertEqual(c["n_entradas_tabla_funciones"], 65)

    def test_las_43_cadenas_del_json(self):
        self.assertEqual(len(self.data["cadenas"]), 43)
        for c in self.data["cadenas"]:
            with self.subTest(vaddr=c["vaddr"]):
                self.assertEqual(cstr(int(c["vaddr"], 16)), c["texto"])

    def test_las_25_funciones_con_su_fichero(self):
        self.assertEqual(len(self.data["funciones"]), 25)
        for f in self.data["funciones"]:
            with self.subTest(func=f["func"]):
                self.assertIsNotNone(f["fichero_fuente"])
                self.assertEqual(sum(1 for _ in f["sitios"]), f["n_sitios"])


if __name__ == "__main__":
    unittest.main()
