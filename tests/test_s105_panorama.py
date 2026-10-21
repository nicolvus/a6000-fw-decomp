"""S105 — panoramica/barrido, bracketing e intervalo.

Verifica CONTRA BYTES del `av-cam.bin` (A6000 fw3.21):

  * cada cadena citada existe en `vaddr - 0x43541000` con el texto exacto;
  * los recuentos de los patrones del inventario;
  * cada sitio de referencia cruzada citado resuelve a la cadena esperada mediante el mecanismo
    real del firmware Thumb: `ldr rX,[pc,#imm]` (pool literal) + `add rX,pc`
    (target = pool_value + (dir_add + 4));
  * las direcciones de codigo citadas no son relleno (0x00/0xFF) y empiezan por un prologo Thumb
    valido (push {..,lr}).

Convencion: vaddr = 0x43541000 + offset_de_fichero.
"""
import re
import struct
from pathlib import Path

import pytest

BASE = 0x43541000
ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "analysis" / "rea-independent" / "input" / "av-cam.bin"

DATA = BIN.read_bytes()


# --------------------------------------------------------------------------------------- utilidades
def off(vaddr: int) -> int:
    """offset de fichero de una vaddr."""
    assert BASE <= vaddr < BASE + len(DATA), f"vaddr fuera de rango: {vaddr:#x}"
    return vaddr - BASE


def cstr(vaddr: int) -> str:
    """cadena terminada en NUL que empieza en vaddr."""
    i = off(vaddr)
    j = DATA.find(b"\x00", i)
    assert j >= 0, f"cadena sin NUL en {vaddr:#x}"
    return DATA[i:j].decode("latin1")


def u32(vaddr: int) -> int:
    return struct.unpack_from("<I", DATA, off(vaddr))[0]


def count(pattern: bytes) -> int:
    return len(re.findall(re.escape(pattern), DATA))


def resolve_xref(site: int):
    """Resuelve una referencia PC-relativa del firmware.

    `site` es la direccion de `ldr rX,[pc,#imm]`.  Devuelve la vaddr de la cadena referenciada,
    o None si el patron no aparece.
    """
    hw = struct.unpack_from("<H", DATA, off(site))[0]
    if (hw & 0xF800) == 0x4800:                     # LDR (literal) T1: 01001 Rt imm8
        rt = (hw >> 8) & 0x7
        imm = (hw & 0xFF) << 2
    elif hw in (0xF8DF, 0xF9DF):                    # LDR (literal) T2 (32 bits)
        hw2 = struct.unpack_from("<H", DATA, off(site) + 2)[0]
        rt = (hw2 >> 12) & 0xF
        imm = hw2 & 0xFFF
    else:
        return None
    pool = ((site + 4) & ~3) + imm
    value = u32(pool)
    for addr in range(off(site) + 2, off(site) + 24, 2):
        h = struct.unpack_from("<H", DATA, addr)[0]
        if 0x4478 <= h <= 0x447F and (h - 0x4478) == rt:   # add rX, pc
            return value + (BASE + addr + 4)
    return None


def has_push_prologue(vaddr: int) -> bool:
    """prologo Thumb: push (16 o 32 bits) en los primeros 4 bytes."""
    i = off(vaddr)
    for k in (0, 2):
        hw = struct.unpack_from("<H", DATA, i + k)[0]
        if (hw & 0xFE00) == 0xB400:                       # push {rlist} T1/T2 (16 bits)
            return True
        if hw == 0xE92D and (struct.unpack_from("<H", DATA, i + k + 2)[0] & 0x4000):
            return True                                   # push.w {rlist, lr}
    return False


# ------------------------------------------------------------------------------------ inventario
# (vaddr, texto exacto de la cadena)
STRINGS = [
    # --- panoramica: ficheros fuente y nombres de etapa --------------------------------------
    (0x43CACF07, "Stage_Panorama.cpp"),
    (0x43CACF3F, "[IMAGING_CAP]: PanoramaSweepStart: err[0x%08x]"),
    (0x43CACF9C, "[IMAGING_CAP]: ApolloSA_Main: err[0x%02x]"),
    (0x43CAD0F4, "Stage_PanoramaCcnrEncode"),
    (0x43CAD10D, "Stage_InitializeSweepAndSpoolBranch"),
    (0x43CAD558, "Stage_RchRcv_Resize_PanoramaGmvCoarse"),
    (0x43CAD57E, "Stage_RchRcv_ResizeFill_PanoramaAutoReview"),
    (0x43CAD72D, "Stage_RchRcv_ResizeFill_PanoramaThm"),
    # --- panoramica: modulo IMAGING (still_cnt_panoramaSweep.cpp) ---------------------------
    (0x43CAB088, "still_cnt_panoramaSweep.cpp"),
    (0x43CAB054, "[IMAGING]: [PanoramaSweepStart] Err: 0x%08x : %s:%d"),
    (0x43CAB0A4, "[IMAGING]: [PanoramaSweepStart] Jpeg Open  err: 0x%08x"),
    (0x43CAB0DB, "[IMAGING]: [PanoramaSweepStart] Jpeg Close  err: 0x%08x"),
    (0x43CAB113, "[IMAGING]: [PanoramaSweepStart] End  err: 0x%08x"),
    (0x43CAB144, "[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x : %s:%d"),
    (0x43CAB176, "[IMAGING]: [PanoramaSweepEnd] Err: 0x%08x, status: 0x%08x"),
    (0x43CAB1B0, "[IMAGING]: [PanoramaSweepEnd] Err! %s:%d"),
    (0x43CAB1D9, "[IMAGING]: [PanoramaSweepEnd] cmp_execStitchPreProcess() Err! %s:%d"),
    (0x43CAB21D, "[IMAGING]: [PanoramaSweepEnd] cmp_checkFillResidual() Err! %s:%d"),
    (0x43CAB25E, "[IMAGING]: [PanoramaSweepEnd] End : 0x%08x"),
    (0x43CAB289, "[IMAGING]: [UpdateSweepCanvas] UnitOpen() Err: 0x%08x : %s:%d"),
    (0x43CAB33A, "[IMAGING]: [UpdateSweepCanvas] seq_brcEncode() Err! %s:%d"),
    (0x43CAB374, "[IMAGING]: [UpdateSweepCanvas] SWEEP_ERROR Err: 0x%08x, ReqID: 0x%04x"),
    (0x43CAB42B, "[IMAGING]: [UpdateSweepCanvas] End  err: 0x%08x"),
    # --- panoramica: stitch / resize / secuencia ---------------------------------------------
    (0x43CC69FA, "still_cnt_panoramaStitch.cpp"),
    (0x43CC69BF, "[IMAGING]: [PanoramaStitch] UnitOpen() Err: 0x%08x : %s:%d"),
    (0x43CC6A47, "[IMAGING]: [PanoramaStitch] seq_initStitch() Err! err: 0x%08x %s:%d"),
    (0x43CC6A8B, "[IMAGING]: [PanoramaStitch] seq_panoramaParallelStitch() Err! err: 0x%08x %s:%d"),
    (0x43CC6ADB, "[IMAGING]: [PanoramaStitch] seq_endStitch() Err! err: 0x%08x %s:%d"),
    (0x43C9E617, "still_seq_panoramaStitch.cpp"),
    (0x43C9E5D0, "[IMAGING]: [seq_panoramaClippingDecode] cmp_decode Err: 0x%%08x : %s:%d".replace("%%", "%")),
    (0x43CCD5C8, "PanoramaStripSequence::StripInfo"),
    (0x43CCD5E9, "PreProcessResult"),
    (0x43CCD5FA, "PreProcessResult::Strip[]"),
    (0x43CC6959, "src/stitch/ddl_stitch.cpp"),
    (0x43CC684D, "src/srotate/ddl_srotate.cpp"),
    (0x43C9E50F, "[IMAGING_CAP]: CameraPanoramaSRotateImage: err[0x%08x]"),
    (0x43CADDC2, "GetImageSizeFromBackup_Panorama"),
    (0x43CAE41B, "ReadBackup_PanoramaJpegStreamSize"),
    (0x43CAE47C, "ReadBackup_PanoramaScnJpegTargetSize"),
    # --- CCNR / Tanzaku ----------------------------------------------------------------------
    (0x43C781AC, "MSG_ID_SDF_CCNR_ENCODE"),
    (0x43C781C3, "MSG_ID_SDF_CCNR_ENCODE_WITH_MODE"),
    (0x43C781E4, "MSG_ID_SDF_PANORAMA_CCNR_ENCODE"),
    (0x43C78289, "MSG_ID_SDF_CCNR_RESIZE"),
    (0x43C7EEFE, "ModuleOnePassCcnrEncode.cpp"),
    (0x43C7E8F1, "ModuleCallbackMgrCcnrEnc.cpp"),
    (0x43C7B926, "ModulePanoramaCcnrEncode.cpp"),
    (0x43C7BABA, "WrapAplCcnrTanzakuStart.cpp"),
    (0x43c7bbc9, "WrapCamTanzakuStart.cpp"),
    (0x43C7B19F, "ExecAplCcnrTanzakuStart"),
    (0x43C7B8CB, "ExecTanzaku"),
    (0x43C7B829, "OpenTanzCalc"),
    (0x43C7B8A9, "OpenTanzInitParam"),
    (0x43C7B69A, "OpenRcAcquire"),
    (0x43C7B7FB, "OpenSrcAcquire"),
    (0x43C7B73C, "GetTanzNoFromDtable"),
    (0x43C7B72E, "WriteToDtable"),
    (0x43C7F07D, "StartTanzaku"),
    (0x43C7F57A, "[SDF][INT_ERROR] ExecTanzaku Err!\n"),
    (0x43C7EF97, "[SDF][CCNR] Timeout! (...going to whole module RETRY)"),
    (0x43C7EF6E, "[SDF][INT_ERROR] [CCNR TimeOut] twai_flg"),
    (0x43C7EF1A, "[SDF][INT_ERROR] [CCNR TimeOut] SetPblAifIibNum"),
    (0x43C7B615, "[SDF][CCNR_ENCODE] jpegOverLimit (...going to ENCODE RETRY)\n"),
    (0x43c7effb, "[SDF][CCNR_ENCODE] SDF_RECMODE_STILL_REC\n"),
    (0x43C7EFCD, "[SDF][CCNR_ENCODE] SDF_RECMODE_OPAL_DUAL_REC\n"),
    (0x43CE29C1, "exec_tanzaku"),
    (0x43CE29CE, "exec_tanzaku_mem2mem"),
    (0x43CE2942, "s_callback_exec_tanzaku %08X"),
    (0x43CBDEF1, "[CAMERA_MAIN_YC]: MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl48_cb_p1 - "
                 "param->ccnr.cc_bl48_cb_p0 == 0"),
    (0x43CBDF54, "[CAMERA_MAIN_YC]: MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl48_cr_p1 - "
                 "param->ccnr.cc_bl48_cr_p0 == 0"),
    (0x43CBDFB7, "[CAMERA_MAIN_YC]: MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl14_cb_p1 - "
                 "param->ccnr.cc_bl14_cb_p0 == 0"),
    (0x43CBE01A, "[CAMERA_MAIN_YC]: MARBLE:\tSTL_PANORAMA\t\tparam->ccnr.cc_bl14_cr_p1 - "
                 "param->ccnr.cc_bl14_cr_p0 == 0"),
    (0x43CBE0E4, "[CAMERA_MAIN_YC]: MARBLE:\tSTL_APOLLO\t\tparam->ccnr.cc_bl48_cb_p1 - "
                 "param->ccnr.cc_bl48_cb_p0 == 0"),
    (0x43CBE2CD, "[CAMERA_MAIN_YC]: MARBLE:\tSTL_CAP\t\tparam->ccnr.cc_bl48_cb_p1 - "
                 "param->ccnr.cc_bl48_cb_p0 == 0"),
    (0x43CBDCE4, "[CAMERA_MAIN_YC]: MARBLE: STL\tSet_marble_tanzaku_param_rc "
                 "main_digitalZoomRatioDenom\t=%x"),
    (0x43CBE4A2, "void Camera::YC::job_YC_Set_marble_tanzaku_param_makernote("
                 "const Camera::CaptureModuleDataAll*, const Camera::APL::APL_MARBLE*)"),
    # --- bracketing --------------------------------------------------------------------------
    (0x43CA79BA, "lc_BracketAF.cpp"),
    (0x43C9B47C, "[IMAGING]: FATAL! %s:%d"),
    # --- intervalo ----------------------------------------------------------------------------
    (0x43CA9F89, "[IMAGING_CAP]: GetCaptureIntervalResource Error! %x"),
    (0x43CAA28B, "[IMAGING_CAP]: CapMgr) osal_stat_sem: CAPTURE_INTERVAL err %d"),
    (0x43CAA2C9, "[IMAGING_CAP]: CapMgr) osal_sig_sem: CAPTURE_INTERVAL err %d"),
    (0x43CAA3D3, "[IMAGING_CAP]: CapMgr) osal_wai_sem: CAPTURE_INTERVAL err %d"),
    (0x43CAA306, "[IMAGING_CAP]: CapMgr) FreeCaptureIntervalResource(): err %d"),
    (0x43CAA343, "[IMAGING_CAP]: CapMgr) osal_alloc_timer: err %x"),
    (0x43CAA373, "[IMAGING_CAP]: CapMgr) osal_set_timer: err %x"),
    (0x43CAA3A1, "[IMAGING_CAP]: CapMgr) SetIntervalTimer(): err %d"),
    (0x43C7A1A5, "[SDF] interval(PTM) %ld\n"),
    (0x43C7A1BE, "[SDF_ERR] interval_ptm over 10[sec]\n"),
    (0x43C7A3C2, "ApiPtmCount.cpp"),
    (0x43C78350, "MSG_ID_SDF_PTM_COUNT"),
    (0x43C7A061, "[SDF] Decode YC Sds handle:%ld, YC Mem handle:%ld\n"),
    (0x43C7A094, "[SDF] Effect PTM: ptm_32.ptm_31_0 : %08x.%08x \n"),
    # --- gestor de captura --------------------------------------------------------------------
    (0x43CA9FBD, "[IMAGING_CAP]: CapMgr) CaptureStart SeqID(0x%08x)"),
    (0x43CAA019, "[IMAGING_CAP]: !!! Can't send Panorama cmd"),
    (0x43CA9FEF, "[IMAGING_CAP]: !!! Can't send DualRec cmd"),
    (0x43CACE6C, "[IMAGING_CAP]: %s: ImageParam_Create Error! SeqId(0x%x) ExpID(%d)"),
    (0x43caceae, "[IMAGING_CAP]: UpdateSweepCanvas: err[0x%08x]"),
    (0x43cacedc, "[IMAGING_CAP]: PanoramaStitch: err[0x%08x]"),
]

# estas dos SI aparecen como puntero absoluto: son entradas de la tabla de nombres de comandos
# del SPICA (a diferencia del resto, que solo se referencian de forma PC-relativa)
TABLA_NOMBRES_SPICA = (0x43CE29C1, 0x43CE29CE)

# (sitio de la instruccion 'ldr rX,[pc,#imm]', vaddr de la cadena referenciada)
XREFS = [
    (0x437E6B5E, 0x43CAB054),   # PanoramaSweepStart Err
    (0x437E6D6C, 0x43CAB0A4),   # PanoramaSweepStart Jpeg Open
    (0x437E6D8C, 0x43CAB0DB),   # PanoramaSweepStart Jpeg Close
    (0x437E6DA6, 0x43CAB113),   # PanoramaSweepStart End
    (0x437E6E92, 0x43CAB144),   # PanoramaSweepEnd Err
    (0x437E711C, 0x43CAB1D9),   # cmp_execStitchPreProcess
    (0x437E737A, 0x43CAB21D),   # cmp_checkFillResidual
    (0x437E73FC, 0x43CAB25E),   # PanoramaSweepEnd End
    (0x437E75A0, 0x43CAB289),   # UpdateSweepCanvas UnitOpen
    (0x437E7AD6, 0x43CAB33A),   # seq_brcEncode
    (0x437E7B46, 0x43CAB374),   # SWEEP_ERROR
    (0x437F0980, 0x43CAD10D),   # Stage_InitializeSweepAndSpoolBranch
    (0x437F179C, 0x43CAD0F4),   # Stage_PanoramaCcnrEncode
    (0x437F0B0E, 0x43caceae),   # UpdateSweepCanvas (IMAGING_CAP)
    (0x437F0C98, 0x43cacedc),   # PanoramaStitch (IMAGING_CAP)
    (0x435492B2, 0x43CACF3F),   # PanoramaSweepStart (IMAGING_CAP)
    (0x437DF7AE, 0x43CAA019),   # Can't send Panorama cmd
    (0x43639822, 0x43C781AC),   # MSG_ID_SDF_CCNR_ENCODE
    (0x43639828, 0x43C781C3),   # MSG_ID_SDF_CCNR_ENCODE_WITH_MODE
    (0x4363982E, 0x43C781E4),   # MSG_ID_SDF_PANORAMA_CCNR_ENCODE
    (0x43639882, 0x43C78350),   # MSG_ID_SDF_PTM_COUNT
    (0x43648066, 0x43C7B926),   # ModulePanoramaCcnrEncode.cpp
    (0x4363E0BE, 0x43C79FFE),   # ExecMain
    (0x4363E862, 0x43C7A1A5),   # [SDF] interval(PTM)
    (0x4363E886, 0x43C7A1BE),   # interval_ptm over 10[sec]
    (0x437C7512, 0x43CA79BA),   # lc_BracketAF.cpp
    (0x437E0CF8, 0x43CAA28B),   # osal_stat_sem CAPTURE_INTERVAL
    (0x437E0D1E, 0x43CAA2C9),   # osal_sig_sem CAPTURE_INTERVAL
    (0x437E0EDC, 0x43CAA343),   # osal_alloc_timer
    (0x437E0F0C, 0x43CAA3A1),   # SetIntervalTimer
    (0x437E0FF8, 0x43CAA3D3),   # osal_wai_sem CAPTURE_INTERVAL
    (0x437DF430, 0x43CA9F89),   # GetCaptureIntervalResource
    (0x4389D46E, 0x43CBDEF1),   # MARBLE STL_PANORAMA ccnr
    (0x4389C382, 0x43CBDCE4),   # Set_marble_tanzaku_param_rc
    (0x438BD122, 0x43CC69BF),   # PanoramaStitch UnitOpen
    (0x438F4BE4, 0x43CCD5C8),   # PanoramaStripSequence::StripInfo
    (0x43780F26, 0x43C9E5D0),   # seq_panoramaClippingDecode
]

# funciones citadas: (vaddr, nombre)
FUNCTIONS = [
    (0x437DF646, "CaptureManager::CaptureStart"),
    (0x437F0838, "Stage_InitializeSweepAndSpoolBranch"),
    (0x43549020, "Stage_Panorama::PanoramaSweepStart"),
    (0x437F10D4, "Stage_Panorama::ApolloSA_Main"),
    (0x437E6B3C, "PanoramaSweepStart"),
    (0x437E6E78, "PanoramaSweepEnd"),
    (0x437E751C, "UpdateSweepCanvas"),
    (0x437F0A58, "UpdateSweepCanvas (IMAGING_CAP)"),
    (0x437F0B58, "PanoramaStitch (IMAGING_CAP)"),
    (0x438BCEF8, "PanoramaStitch (IMAGING)"),
    (0x43780EB4, "seq_panoramaClippingDecode"),
    (0x437F1414, "Stage_PanoramaCcnrEncode"),
    (0x4363DE9C, "ApiPanoramaCcnrEncode::ExecMain"),
    (0x4364801C, "ModulePanoramaCcnrEncode"),
    (0x4364D214, "WrapAplCcnrTanzakuStart"),
    (0x4364D4A8, "WrapCamTanzakuStart"),
    (0x436433A8, "ExecAplCcnrTanzakuStart"),
    (0x438F4BCC, "PanoramaStripSequence::StripInfo"),
    (0x437C74B6, "lc_BracketAF::f1"),
    (0x437C7554, "lc_BracketAF::f2"),
    (0x437DF338, "CaptureManager::GetCaptureIntervalResource"),
    (0x437E0CE8, "CaptureManager::IntervalSemaphore"),
    (0x437E0D5A, "CaptureManager::FreeCaptureIntervalResource"),
    (0x437E0E1C, "CaptureManager::SetIntervalTimer"),
    (0x437E0FC0, "CaptureManager::WaitIntervalSem"),
    (0x4363E7AC, "SDF::CheckPtmInterval"),
    (0x4363EC80, "ApiPtmCount::WaitImcResponse"),
    (0x4389D180, "MARBLE::STL_PANORAMA"),
    (0x4389C378, "MARBLE::Set_marble_tanzaku_param_rc"),
    (0x4365E424, "ModuleOnePassCcnrEncode::StartTanzaku"),
    (0x437F42B8, "Stage_RchRcv_Resize_PanoramaGmvCoarse"),
    (0x437F4378, "Stage_RchRcv_ResizeFill_PanoramaAutoReview"),
    (0x437F40C4, "Stage_RchRcv_ResizeFill_PanoramaThm"),
    (0x437F6F24, "GetImageSizeFromBackup_Panorama"),
    (0x437F8248, "ReadBackup_PanoramaJpegStreamSize"),
    (0x437F85B8, "ReadBackup_PanoramaScnJpegTargetSize"),
    (0x437802DE, "CameraPanoramaSRotateImage"),
]

COUNTS = {
    b"Panorama": 67,
    b"Sweep": 26,
    b"Bracket": 1,
    b"Interval": 10,
    b"INTERVAL": 4,
    b"PTM": 59,
    b"Ccnr": 14,
    b"CCNR": 10,
    b"Tanzaku": 27,
    b"still_cnt_panoramaSweep.cpp": 1,
    b"still_cnt_panoramaStitch.cpp": 1,
    b"still_seq_panoramaStitch.cpp": 1,
    b"lc_BracketAF.cpp": 1,
    b"ModulePanoramaCcnrEncode.cpp": 1,
    b"ApiPanoramaCcnrEncode.cpp": 1,
    b"WrapAplCcnrTanzakuStart.cpp": 1,
    b"WrapCamTanzakuStart.cpp": 1,
    b"ModuleOnePassCcnrEncode.cpp": 1,
    b"ApiPtmCount.cpp": 1,
    b"ddl_stitch.cpp": 1,
    b"ddl_srotate.cpp": 1,
    b"MSG_ID_SDF_PANORAMA_CCNR_ENCODE": 1,
    b"MSG_ID_SDF_CCNR_ENCODE": 2,
    b"MSG_ID_SDF_PTM_COUNT": 1,
    b"Stage_PanoramaCcnrEncode": 1,
    b"Stage_InitializeSweepAndSpoolBranch": 1,
    b"PanoramaStripSequence": 2,
    b"exec_tanzaku": 3,
    b"PreProcessResult": 2,
}

STRING_IDS = [f"{v:#x}" for v, _ in STRINGS]
XREF_IDS = [f"{s:#x}" for s, _ in XREFS]
FUNC_IDS = [f"{v:#x}" for v, _ in FUNCTIONS]
COUNT_IDS = [p.decode("latin1") for p in COUNTS]


# ----------------------------------------------------------------------------------------- tests
def test_binario_y_convencion_de_direcciones():
    assert BIN.exists(), BIN
    assert len(DATA) == 11_427_236
    for vaddr, _ in STRINGS:
        assert BASE <= vaddr < BASE + len(DATA)


@pytest.mark.parametrize("vaddr,text", STRINGS, ids=STRING_IDS)
def test_cadena_exacta_en_vaddr_menos_base(vaddr, text):
    """cada cadena citada existe en `vaddr - 0x43541000` con el texto exacto."""
    assert cstr(vaddr) == text, f"{vaddr:#x}: {cstr(vaddr)!r} != {text!r}"


@pytest.mark.parametrize("vaddr,text", STRINGS, ids=STRING_IDS)
def test_offset_de_fichero_de_cada_cadena(vaddr, text):
    """offset_de_fichero == vaddr - 0x43541000, y los bytes son los de la cadena."""
    i = off(vaddr)
    assert DATA[i:i + len(text)] == text.encode("latin1")
    assert DATA[i + len(text)] == 0


@pytest.mark.parametrize("site,target", XREFS, ids=XREF_IDS)
def test_xref_pc_relativo_resuelve_a_la_cadena(site, target):
    """`ldr rX,[pc,#imm]` + `add rX,pc` resuelve exactamente a la cadena citada."""
    got = resolve_xref(site)
    assert got == target, f"xref {site:#x} -> {got!r}, esperado {target:#x}"
    assert cstr(target)


@pytest.mark.parametrize("pattern,n", sorted(COUNTS.items()), ids=COUNT_IDS)
def test_recuentos_del_inventario(pattern, n):
    assert count(pattern) == n, f"{pattern!r}: {count(pattern)} != {n}"


@pytest.mark.parametrize("vaddr,name", FUNCTIONS, ids=FUNC_IDS)
def test_direccion_de_codigo_no_es_relleno(vaddr, name):
    """las direcciones de codigo citadas no son relleno 0x00/0xFF y tienen prologo Thumb."""
    i = off(vaddr)
    blob = DATA[i:i + 8]
    assert len(blob) == 8
    assert blob != b"\x00" * 8 and blob != b"\xff" * 8
    assert not all(b in (0x00, 0xFF) for b in blob), f"{name} {vaddr:#x} parece relleno"
    assert has_push_prologue(vaddr), f"{name} {vaddr:#x} no empieza por push: {blob.hex(' ')}"


def test_peticiones_de_modo_en_el_gestor_de_captura():
    """`movw r0,#0x301f` (panorama) y `movw r0,#0x3005` (DualRec) en CaptureStart."""
    assert DATA[off(0x437DF7A2):off(0x437DF7A2) + 4] == bytes.fromhex("43f21f00")
    assert DATA[off(0x437DF6DE):off(0x437DF6DE) + 4] == bytes.fromhex("43f20500")


def test_periodo_del_intervalo_10000_por_N():
    """`movw r2,#0x2710` (10000) y `mul r2,r2,sb` en SetIntervalTimer."""
    assert DATA[off(0x437E0E9A):off(0x437E0E9A) + 4] == bytes.fromhex("42f21072")
    assert DATA[off(0x437E0EA8):off(0x437E0EA8) + 4] == bytes.fromhex("02fb09f2")


def test_limite_del_intervalo_ptm_es_900000():
    """literal pool 0x4363E93C = 900000 (limite de 64 bits del control de intervalo PTM)."""
    assert u32(0x4363E93C) == 900_000


def test_bracket_una_sola_ocurrencia_y_es_el_fichero():
    """el unico 'Bracket' del binario es 'lc_BracketAF.cpp' (no hay bracketing de exposicion)."""
    hits = [m.start() for m in re.finditer(b"Bracket", DATA)]
    assert len(hits) == 1
    assert DATA[hits[0] - 3:hits[0] + 13] == b"lc_BracketAF.cpp"
    assert (BASE + hits[0] - 3) == 0x43CA79BA
    assert count(b"BRACKET") == 0
    assert count(b"bracket") == 0
    assert count(b"ExposureBracketing") == 0


def test_las_cadenas_se_referencian_de_forma_pc_relativa():
    """salvo la tabla de nombres del SPICA, ninguna cadena citada aparece como puntero absoluto."""
    for vaddr, text in STRINGS:
        if vaddr in TABLA_NOMBRES_SPICA:
            continue
        assert DATA.find(struct.pack("<I", vaddr)) == -1, f"{vaddr:#x} aparece como puntero absoluto"


def test_tabla_de_nombres_de_comandos_del_spica():
    """'exec_tanzaku' / 'exec_tanzaku_mem2mem' SI son punteros absolutos (tabla de comandos)."""
    for vaddr in TABLA_NOMBRES_SPICA:
        assert DATA.find(struct.pack("<I", vaddr)) != -1
        assert cstr(vaddr)


def test_informe_y_json_existen():
    informe = ROOT / "analysis" / "s105_panorama" / "panorama_bracket_interval.md"
    datos = ROOT / "analysis" / "s105_panorama" / "panorama_bracket_interval.json"
    resumen = ROOT / "docs" / "capture" / "s105-panorama-bracket-interval.md"
    assert informe.exists() and informe.stat().st_size > 4000
    assert datos.exists() and datos.stat().st_size > 1000
    assert resumen.exists() and resumen.stat().st_size > 800
