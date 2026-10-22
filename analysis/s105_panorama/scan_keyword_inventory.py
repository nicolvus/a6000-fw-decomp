#!/usr/bin/env python3
"""S105 — extracción reproducible de los datos del informe.

Genera `keyword_inventory.json` a partir de los bytes de
`analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21) y
el blob de la A7S en firmware/extracted/a7s-fw320/ (A7S fw3.20).

Convención de direcciones: vaddr = 0x43541000 + file_offset (en AMBOS blobs).

El script AUTOVALIDA: cada cadena curada se comprueba contra los bytes del blob
y el script aborta si alguna dirección no contiene el texto esperado.

Uso:
    .venv/bin/python analysis/s105_panorama/scan_final.py
"""
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "keyword_inventory.json"
BASE = 0x43541000
BLOBS = {
    "A6000": ROOT / "analysis/rea-independent/input/av-cam.bin",
    "A7S": ROOT / ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
                     "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"),
}
PAT = re.compile(rb"[\x20-\x7e]{4,}")

# ---------------------------------------------------------------- palabras clave
SETS = {
    "panorama": ["panorama", "Panorama", "PANORAMA"],
    "sweep":    ["sweep", "Sweep", "SWEEP"],
    "stitch":   ["stitch", "Stitch", "STITCH"],
    "interval": ["interval", "Interval", "INTERVAL"],
    "bracket":  ["Bracket", "bracket", "BRACKET"],
}
MOD_PREFIXES = ("[IMAGING]: ", "[IMAGING_CAP]: ", "[CAMERA_MAIN_YC]: ",
                "[CAMERA_MAIN_TC]: ", "[CAMERA_IS][MOUNT]: [Error] ")

# --------------------------------------------------- cadenas curadas (autovalidadas)
# (vaddr, texto esperado, modo)
KEY_STRINGS = [
    # --- panorámica: ruta SDF / módulos -------------------------------
    (0x43c781e4, "MSG_ID_SDF_PANORAMA_CCNR_ENCODE", "panorama"),
    (0x43c79fd2, "ApiPanoramaCcnrEncode.cpp", "panorama"),
    (0x43c7a007, "21ApiPanoramaCcnrEncode", "panorama"),
    (0x43c7b926, "ModulePanoramaCcnrEncode.cpp", "panorama"),
    (0x43c7b957, "24ModulePanoramaCcnrEncode", "panorama"),
    (0x43c7b8eb, "MakeDevelopResizeTable", "panorama"),
    (0x43cacf07, "Stage_Panorama.cpp", "panorama"),
    (0x43cad0f4, "Stage_PanoramaCcnrEncode", "panorama"),
    (0x43cad558, "Stage_RchRcv_Resize_PanoramaGmvCoarse", "panorama"),
    (0x43cad57e, "Stage_RchRcv_ResizeFill_PanoramaAutoReview", "panorama"),
    (0x43cad72d, "Stage_RchRcv_ResizeFill_PanoramaThm", "panorama"),
    (0x43cc7a2a, "[IMAGING_CAP]: [Panorama][DEBUG]CAPTURE_START", "panorama"),
    (0x43caa019, "[IMAGING_CAP]: !!! Can't send Panorama cmd", "panorama"),
    (0x43ca13ff, "REQ_PANORAMA_EE", "panorama"),
    (0x43ca1603, "REPLY_PANORAMA_EE", "panorama"),
    (0x43cae41b, "ReadBackup_PanoramaJpegStreamSize", "panorama"),
    (0x43cae47c, "ReadBackup_PanoramaScnJpegTargetSize", "panorama"),
    (0x43caddc2, "GetImageSizeFromBackup_Panorama", "panorama"),
    (0x43cade26, "CaptureUtilityImageSize.cpp", "panorama"),
    (0x43cb6b8b, "[CAMERA_MAIN_TC]: APL_PANORAMA_INFO %d %d %d %d 0x%X 0x%X %d 0x%X 0x%X 0x%X 0x%X", "panorama"),
    (0x43cbdf03, "MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl48_cb_p1 - param->ccnr.cc_bl48_cb_p0 == 0", "panorama"),
    (0x43cbdf66, "MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl48_cr_p1 - param->ccnr.cc_bl48_cr_p0 == 0", "panorama"),
    (0x43cbdfc9, "MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl14_cb_p1 - param->ccnr.cc_bl14_cb_p0 == 0", "panorama"),
    (0x43cbe02c, "MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl14_cr_p1 - param->ccnr.cc_bl14_cr_p0 == 0", "panorama"),
    (0x43cbe08f, "MARBLE:\tSTL_PANORAMA\t\tparam->marble_y.yy_emodu_p1 - param->marble_y.yy_emodu_p0 == 0", "panorama"),
    (0x43cace1e, "[IMAGING_CAP]: NotifyStitchProgress: ERR", "panorama"),
    (0x43cace47, "[IMAGING_CAP]: NotifyStitchComp: ERR", "panorama"),
    (0x43cacedc, "[IMAGING_CAP]: PanoramaStitch: err[0x%08x]", "panorama"),
    (0x43cad054, "[IMAGING_CAP]: ExecutePanoramaTC1ST: PanoraamApollo Err", "panorama"),
    (0x43cad08c, "[IMAGING_CAP]: ExecutePanoramaTC2ND: PanoramaApollo Err", "panorama"),
    (0x43c9a3a7, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB (%x)", "panorama"),
    (0x43c9a3e3, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyroCB - checkData", "panorama"),
    (0x43c9a426, "[CAMERA_IS][MOUNT]: [Error] IS_LensMountPanoramaGyro (%x)", "panorama"),
    # --- panorámica: motor de costura (stitch) -------------------------
    (0x43c9e617, "still_seq_panoramaStitch.cpp", "stitch"),
    (0x43cc69fa, "still_cnt_panoramaStitch.cpp", "stitch"),
    (0x43c9e50f, "[IMAGING_CAP]: CameraPanoramaSRotateImage: err[0x%08x]", "stitch"),
    (0x43c9e573, "[IMAGING]: [seqStitchCallBack] ercd: 0x%08x", "stitch"),
    (0x43c9e5d0, "[IMAGING]: [seq_panoramaClippingDecode] cmp_decode Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e634, "[IMAGING]: [seq_panoramaResize] effectImage Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e674, "[IMAGING]: [seq_panoramaResize][OK] effectImage OK : %s:%d", "stitch"),
    (0x43c9e6af, "[IMAGING]: [seq_panoramaParallelStitch] getJPGListI Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e6f7, "[IMAGING]: [seq_panoramaParallelStitch] setStitchImageObjectInfo Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e74c, "[IMAGING]: [seq_panoramaParallelStitch] DecodeControl Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e796, "[IMAGING]: [seq_panoramaParallelStitch] SRotateControl Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e7e1, "[IMAGING]: [seq_panoramaParallelStitch] StitchControl Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e82b, "[IMAGING]: [seq_panoramaParallelStitch] wai_flg Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e86f, "[IMAGING]: [seq_panoramaParallelStitch] clr_flg Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e8b3, "[IMAGING]: [seq_panoramaParallelStitch] Decode Interrupt Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e900, "[IMAGING]: [seq_panoramaParallelStitch] SRotate Interrupt Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9ebb4, "[IMAGING]: [seq_panoramaParallelStitch] Stitch Interrupt Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9ec01, "[IMAGING]: [seq_panoramaParallelStitch][OK] StitchProc ALL OK : %s:%d", "stitch"),
    (0x43c9ec47, "[IMAGING]: [seq_panoramaParallelStitch] cmp_getBackStitchParam Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9ec9a, "[IMAGING]: [panoramaSRotateLeftStitchImage][Debug] End  err: 0x%08x", "stitch"),
    (0x43c9ecde, "[IMAGING]: [seq_panoramaParallelStitch][OK] SRotateLeftProc OK : %s:%d", "stitch"),
    (0x43c9ed25, "[IMAGING]: [seq_makePanoramaMakerNoteData] Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e94e, "[IMAGING]: [StitchInterrupt] Stitch Interrupt Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e990, "[IMAGING]: [StitchInterrupt] csl_RingBuff_getDataNum Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9e9d9, "[IMAGING]: [StitchInterrupt] csl_RingBuff_getInputImage Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9ea25, "[IMAGING]: [StitchInterrupt] ringBuffDataHeader == NULL Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9ea71, "[IMAGING]: [StitchInterrupt] csl_RingBuff_endReadImage Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9eabc, "[IMAGING]: [StitchInterrupt] clr_flg Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9eaf5, "[IMAGING]: [StitchInterrupt] cmp_stopStitch Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9eb35, "[IMAGING]: [StitchInterrupt] wai_flg Err: 0x%08x : %s:%d", "stitch"),
    (0x43c9eb6e, "[IMAGING]: [StitchInterrupt] Stop Stitch (Cancel) Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc68eb, "[IMAGING]: [ddls_stitch_set_flg] ercd: 0x%08x", "stitch"),
    (0x43cc6919, "[IMAGING]: [ddls_stitch_sa_start_cb] SA DRV Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc6959, "src/stitch/ddl_stitch.cpp", "stitch"),
    (0x43cc6973, "[IMAGING]: [ddls_stitch_sa_start_cb][Debug NG] CallBack Addr = NULL: 0x%08x", "stitch"),
    (0x43cc69bf, "[IMAGING]: [PanoramaStitch] UnitOpen() Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc6a17, "[IMAGING]: [PanoramaStitch] Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc6a47, "[IMAGING]: [PanoramaStitch] seq_initStitch() Err! err: 0x%08x %s:%d", "stitch"),
    (0x43cc6a8b, "[IMAGING]: [PanoramaStitch] seq_panoramaParallelStitch() Err! err: 0x%08x %s:%d", "stitch"),
    (0x43cc6adb, "[IMAGING]: [PanoramaStitch] seq_endStitch() Err! err: 0x%08x %s:%d", "stitch"),
    (0x43cc6b1e, "[IMAGING]: [PanoramaStitch] UnitClose() Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc6b5a, "[IMAGING]: [PanoramaStitch] End  err: 0x%08x", "stitch"),
    (0x43cc6b87, "[IMAGING]: [PanoramaResize] UnitOpen() Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc6bc2, "[IMAGING]: [PanoramaResize] seq_panoramaResize() Err! err: 0x%08x %s:%d", "stitch"),
    (0x43cc6c0a, "[IMAGING]: [PanoramaResize] seq_makePanoramaMakerNoteData() Err! err: 0x%08x %s:%d", "stitch"),
    (0x43cc6c5d, "[IMAGING]: [PanoramaResize] UnitClose() Err: 0x%08x : %s:%d", "stitch"),
    (0x43cc6c99, "[IMAGING]: [PanoramaResize] End  err: 0x%08x", "stitch"),
    # --- barrido (sweep) -----------------------------------------------
    (0x43cab054, "[IMAGING]: [PanoramaSweepStart] Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab088, "still_cnt_panoramaSweep.cpp", "sweep"),
    (0x43cab0a4, "[IMAGING]: [PanoramaSweepStart] Jpeg Open  err: 0x%08x", "sweep"),
    (0x43cab0db, "[IMAGING]: [PanoramaSweepStart] Jpeg Close  err: 0x%08x", "sweep"),
    (0x43cab113, "[IMAGING]: [PanoramaSweepStart] End  err: 0x%08x", "sweep"),
    (0x43cab144, "[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab176, "[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x, status: 0x%08x", "sweep"),
    (0x43cab1b0, "[IMAGING]: [PanoramaSweepEnd] Err! %s:%d", "sweep"),
    (0x43cab1d9, "[IMAGING]: [PanoramaSweepEnd] cmp_execStitchPreProcess() Err! %s:%d", "sweep"),
    (0x43cab21d, "[IMAGING]: [PanoramaSweepEnd] cmp_checkFillResidual() Err! %s:%d", "sweep"),
    (0x43cab25e, "[IMAGING]: [PanoramaSweepEnd] End : 0x%08x", "sweep"),
    (0x43cab289, "[IMAGING]: [UpdateSweepCanvas] UnitOpen() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab2c7, "[IMAGING]: [UpdateSweepCanvas] Err: 0x%08x, status: 0x%08x ReqID: 0x%04x", "sweep"),
    (0x43cab310, "[IMAGING]: [UpdateSweepCanvas] Err! %s:%d", "sweep"),
    (0x43cab33a, "[IMAGING]: [UpdateSweepCanvas] seq_brcEncode() Err! %s:%d", "sweep"),
    (0x43cab374, "[IMAGING]: [UpdateSweepCanvas] SWEEP_ERROR Err: 0x%08x, ReqID: 0x%04x", "sweep"),
    (0x43cab3ba, "[IMAGING]: [UpdateSweepCanvas] SWEEP_ERROR! %s:%d", "sweep"),
    (0x43cab3ec, "[IMAGING]: [UpdateSweepCanvas] UnitClose() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab42b, "[IMAGING]: [UpdateSweepCanvas] End  err: 0x%08x", "sweep"),
    (0x43cab45b, "[IMAGING]: [PanoramaResizeEncode][JpegSweepInfo] UnitOpen() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab4ab, "[IMAGING]: [PanoramaResizeEncode][YuvDecodeWorkInfo] UnitOpen() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab4ff, "[IMAGING]: [PanoramaResizeEncode][JpegResizeEncodeInfo] UnitOpen() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab556, "[IMAGING]: [PanoramaResizeEncode] Err Mode: 0x%08x : %s:%d", "sweep"),
    (0x43cab591, "[IMAGING]: [PanoramaResizeEncode] Err Dir: 0x%08x : %s:%d", "sweep"),
    (0x43cab5cb, "[IMAGING]: [PanoramaResizeEncode] Err seq_bigImageResizeEncode(): 0x%08x : %s:%d", "sweep"),
    (0x43cab61c, "[IMAGING]: [PanoramaResizeEncode][JpegSweepInfo] UnitClose() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab66d, "[IMAGING]: [PanoramaResizeEncode][YuvDecodeWorkInfo] UnitClose() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab6c2, "[IMAGING]: [PanoramaResizeEncode][JpegResizeEncodeInfo] UnitClose() Err: 0x%08x : %s:%d", "sweep"),
    (0x43cab71a, "[IMAGING]: [PanoramaResizeEncode] End  err: 0x%08x", "sweep"),
    (0x43cad10d, "Stage_InitializeSweepAndSpoolBranch", "sweep"),
    (0x43cacdd2, "[IMAGING_CAP]: NotifySweepProgress: ERR", "sweep"),
    (0x43cacdfa, "[IMAGING_CAP]: NotifySweepComp: ERR", "sweep"),
    (0x43caceae, "[IMAGING_CAP]: UpdateSweepCanvas: err[0x%08x]", "sweep"),
    (0x43cacf3f, "[IMAGING_CAP]: PanoramaSweepStart: err[0x%08x]", "sweep"),
    (0x43cade8c, "[IMAGING_CAP]: %s Invalid SWEEP_DIRECTION", "sweep"),
    (0x43cadeb6, "[IMAGING_CAP]: %s Invalid SWEEP_LENGTH", "sweep"),
    (0x43cbc27c, "[CAMERA_MAIN_YC]: HD_SWEEP_HOLD  =%x", "sweep"),
    # --- bracketing ----------------------------------------------------
    (0x43ca79ba, "lc_BracketAF.cpp", "bracket"),
    (0x43ca54c8, "[CAMERA_MAIN_CC]: ExtractCaptureData()       [CapMode:%d] [ExposureID:%d] [ContID:%d] [FrameID:%d]", "bracket"),
    (0x43ca552b, "[CAMERA_MAIN_CC]: CaptureInit()              [CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d]", "bracket"),
    (0x43ca55a9, "[CAMERA_MAIN_CC]: SetReadImageParam()        [CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d]", "bracket"),
    (0x43ca5627, "[CAMERA_MAIN_CC]: SetNRParam()               [CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d]", "bracket"),
    (0x43ca56a5, "[CAMERA_MAIN_CC]: SetOPDParam()              [CapMode:%d] [ExposureID:%d] [ContID:%d] [BDROSeq:%d]", "bracket"),
    (0x43cc8c32, "[IMAGING_CAP]: ExposureTimerStart!(first)", "bracket"),
    (0x43cc8c5c, "[IMAGING_CAP]: ExposureTimerEnd!", "bracket"),
    (0x43ccdb75, "uc_DrvMode", "bracket"),
    (0x43ca7bc4, "N6Camera2LC18CPafStateSelfTimerE", "interval"),
    # --- intervalo -----------------------------------------------------
    (0x43cb4c60, "SB_INTERVAL", "interval"),
    (0x43c7a1a5, "[SDF] interval(PTM) %ld", "interval"),
    (0x43c7a1be, "[SDF_ERR] interval_ptm over 10[sec]", "interval"),
    (0x43ca9f89, "[IMAGING_CAP]: GetCaptureIntervalResource Error! %x", "interval"),
    (0x43caa28b, "[IMAGING_CAP]: CapMgr) osal_stat_sem: CAPTURE_INTERVAL err %d", "interval"),
    (0x43caa2c9, "[IMAGING_CAP]: CapMgr) osal_sig_sem: CAPTURE_INTERVAL err %d", "interval"),
    (0x43caa306, "[IMAGING_CAP]: CapMgr) FreeCaptureIntervalResource(): err %d", "interval"),
    (0x43caa3a1, "[IMAGING_CAP]: CapMgr) SetIntervalTimer(): err %d", "interval"),
    (0x43caa3d3, "[IMAGING_CAP]: CapMgr) osal_wai_sem: CAPTURE_INTERVAL err %d", "interval"),
]

# --------------------------------------------------------------- tablas/estructuras
# (vaddr, bytes hex, descripción)
TABLES = [
    # tbb de SWEEP_DIRECTION en GetImageSizeFromBackup_Panorama (A6000)
    (0x437f6f38, "11111313", "tbb SWEEP_DIRECTION: 4 entradas (0,1)->idx0; (2,3)->idx1"),
    # tbb de SWEEP_LENGTH (A6000)
    (0x437f6f68, "02041517", "tbb SWEEP_LENGTH: 4 entradas -> idx 2,3,0,1"),
    # mismos tbb en la A7S fw3.20
    (0x438271da, "08080a0a", "A7S: tbb SWEEP_DIRECTION (idéntico mapeo)"),
    (0x438271f8, "02040c0e", "A7S: tbb SWEEP_LENGTH (idéntico mapeo)"),
    # límite de 10 s del intervalo SDF (constante 0x000DBBA0 = 900000 PTM)
    (0x4363e93c, "a0bb0d00", "A6000: límite intervalo SDF = 900000 PTM (10 s)"),
    (0x4365a668, "a0bb0d00", "A7S: mismo límite 900000 PTM"),
    # escala Q12 de la Cubic Table
    (0x438f3e08, "00008045", "A6000: float 4096.0 (escala Q12 de la Cubic Table)"),
    # escala de la Div Table
    (0x438f3e0c, "00008048", "A6000: float 262144.0 (divisor de la Div Table)"),
    # factor 10000 del temporizador de intervalo
    (0x437e0e9a, "42f21072", "A6000: movw r2,#0x2710 (10000) -> periodo = 10000 * campo"),
]


def blob(which):
    return BLOBS[which].read_bytes()


def cstr(data, vaddr):
    o = vaddr - BASE
    return data[o:o + 200].split(b"\x00")[0].decode("latin-1")


def all_strings(which):
    data = blob(which)
    return [(m.start() + BASE, m.start(), m.group(0).decode("latin-1"))
            for m in PAT.finditer(data)]


def norm(t):
    for p in MOD_PREFIXES:
        if t.startswith(p):
            t = t[len(p):]
    return re.sub(r"\s*:\s*%s:%d$", "", t)


def main():
    errs = []
    a_data, b_data = blob("A6000"), blob("A7S")
    strings_out = {"A6000": [], "A7S": []}
    for vaddr, expected, mode in KEY_STRINGS:
        got = cstr(a_data, vaddr)
        if not got.startswith(expected):
            errs.append(f"A6000 0x{vaddr:08x}: esperado {expected!r}, obtido {got!r}")
        strings_out["A6000"].append({"vaddr": f"0x{vaddr:08x}", "off": f"0x{vaddr - BASE:08x}",
                                     "mode": mode, "text": expected})
    if errs:
        print("FALLO de autovalidación:", *errs, sep="\n  ")
        sys.exit(1)

    tables_out = []
    for vaddr, hexs, desc in TABLES:
        which = "A7S" if "A7S" in desc else "A6000"
        data = a_data if which == "A6000" else b_data
        o = vaddr - BASE
        got = data[o:o + len(hexs) // 2].hex()
        if got != hexs:
            errs.append(f"{which} 0x{vaddr:08x}: esperado {hexs}, obtenido {got}")
        tables_out.append({"vaddr": f"0x{vaddr:08x}", "blob": which, "bytes": hexs, "desc": desc})
    if errs:
        print("FALLO de autovalidación:", *errs, sep="\n  ")
        sys.exit(1)

    A, B = all_strings("A6000"), all_strings("A7S")
    res = {
        "milestone": "S105",
        "title": "Panorámica, barrido (sweep), bracketing y disparo por intervalo en la A6000",
        "binary": {
            "A6000": {"path": str(BLOBS["A6000"].relative_to(ROOT)),
                      "size_bytes": len(a_data), "fw": "3.21"},
            "A7S": {"path": str(BLOBS["A7S"].relative_to(ROOT)),
                    "size_bytes": len(b_data), "fw": "3.20"},
        },
        "convention": "vaddr = 0x43541000 + file_offset (igual en A6000 y A7S)",
        "method": {
            "type": "estatico, solo lectura de bytes (sin ejecutar firmware, sin camara, sin flasheo)",
            "string_xref": "las cadenas se referencian con 'ldr rX,[pc,#imm]' (pool literal) + "
                           "'add rX,pc' (0x4478+Rd): target = pool_value + (dir_add + 4). "
                           "Verificado byte a byte (p.ej. 0x438ef492 -> '[CAMERA_MAIN_YC]: SHD::GetShdMode: unknown drive_mode = 0x%x' 0x43ccca56).",
            "scripts": ["analysis/s105_panorama/scan_strings.py",
                        "analysis/s105_panorama/scan_kw.py",
                        "analysis/s105_panorama/scan_xref.py",
                        "analysis/s105_panorama/scan_diff.py",
                        "analysis/s105_panorama/scan_keyword_inventory.py"],
        },
        "counts": {},
        "strings": strings_out,
        "tables": tables_out,
        "notes": [],
    }

    for name, keys in SETS.items():
        sa = [(v, o, t) for (v, o, t) in A if any(k in t for k in keys)]
        sb = [(v, o, t) for (v, o, t) in B if any(k in t for k in keys)]
        na = {norm(t): (v, o, t) for v, o, t in sa}
        nb = {norm(t): (v, o, t) for v, o, t in sb}
        res["counts"][name] = {
            "A6000_ocurrencias": len(sa), "A6000_distintas": len(na),
            "A7S_ocurrencias": len(sb), "A7S_distintas": len(nb),
            "comunes_normalizados": len(set(na) & set(nb)),
            "solo_A6000": [{"vaddr": f"0x{na[k][0]:08x}", "off": f"0x{na[k][1]:08x}",
                            "text": na[k][2]} for k in sorted(set(na) - set(nb))],
            "solo_A7S": [{"vaddr": f"0x{nb[k][0]:08x}", "off": f"0x{nb[k][1]:08x}",
                          "text": nb[k][2]} for k in sorted(set(nb) - set(na))],
        }
    res["counts"]["total_ocurrencias_palabras_clave"] = {
        "A6000": sum(res["counts"][k]["A6000_ocurrencias"] for k in SETS),
        "A7S": sum(res["counts"][k]["A7S_ocurrencias"] for k in SETS)}

    # ---- resultado negativo destacado: "Bracket" sólo aparece una vez ----
    res["counts"]["bracket_en_bytes_brutos"] = {
        "A6000_ocurrencias_de_la_subcadena_Bracket": a_data.count(b"Bracket"),
        "A7S_ocurrencias_de_la_subcadena_Bracket": b_data.count(b"Bracket"),
        "A6000_ocurrencias_de_la_subcadena_bracket": a_data.count(b"bracket"),
        "A7S_ocurrencias_de_la_subcadena_bracket": b_data.count(b"bracket"),
    }
    res["notes"] = [
        "El unico 'Bracket' del firmware A6000 es 'lc_BracketAF.cpp' (0x43ca79ba): el bracketing NO se "
        "implementa con ese nombre en av-cam.bin; vive en el userland (libScalarDaemon.so / libObj.so) "
        "y llega a la camara como drive_mode / ContID / BDROSeq.",
        "El barrido (sweep) se valida con dos tablas tbb identicas en A6000 fw3.21 y A7S fw3.20: "
        "SWEEP_DIRECTION (0..3) y SWEEP_LENGTH (0..3) -> indice de 8 entradas (2 direcciones x 4 longitudes).",
        "El limite superior del intervalo (10 s) esta implementado con la constante 0x000DBBA0 = 900000 PTM, "
        "identica en A6000 (0x4363e93c) y A7S (0x4365a668).",
        "El motor de costura (stitch) se ejecuta en el SA (acelerador Scalar) con 4 argumentos de mailbox: "
        "STITCH_ARG (0x3C B), Cubic Table (0x44 B), Div Table (0x400 B) y STITCH_STRIP_INFO (16 B por franja).",
        "Los 4 'stage' de panoramic y el barrido comparten el modulo CAMERA_MAIN_CC/IMAGING; la ruta de "
        "codificacion pasa por el SDF con MSG_ID_SDF_PANORAMA_CCNR_ENCODE.",
    ]
    OUT.write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in res["counts"].items()
                      if not isinstance(v, dict) or "ocurrencias" not in v}, indent=2))
    print("->", OUT)


if __name__ == "__main__":
    main()
