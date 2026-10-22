"""Tests de S136 — el módulo `[ACCY]` (accesorios) del firmware A6000 fw3.21.

Todos los tests son **de bytes reales**: leen `av-cam.bin` (A6000 fw3.21) y, para el
diferencial, la A7S fw3.20 y la A6300 fw2.01. Cada aserción fija una **dirección
concreta**, de modo que cualquier cambio de direcciones, textos o instrucciones
rompe el test.

La regla de referencias a cadenas es la **estricta** canónica
(`analysis/s106_imaging_cap/scan_pic_refs_strict.py`): cada `add rX, pc` se empareja
con el `ldr rX, [pc, #imm]` más cercano por detrás del mismo registro.
"""

import json
import pathlib
import re
import struct

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = (
    "firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
A6300 = (
    "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
    "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
)
PREFIX = b"[ACCY]"
ACCY_CODE_LO, ACCY_CODE_HI = 0x43562A08, 0x43567060
MAX_LDR_GAP = 4096
U16S = struct.Struct("<H")
U32S = struct.Struct("<I")


def _data(path=BIN):
    with open(ROOT / path, "rb") as fh:
        return fh.read()


DATA = _data()


def _u16(addr, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - 2, f"vaddr {hex(addr)} fuera del binario"
    return U16S.unpack_from(data, off)[0]


def _u32(addr, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - 4, f"vaddr {hex(addr)} fuera del binario"
    return U32S.unpack_from(data, off)[0]


def _bytes(addr, n, data=None):
    data = DATA if data is None else data
    off = addr - BASE
    assert 0 <= off <= len(data) - n, f"vaddr {hex(addr)} fuera del binario"
    return data[off:off + n]


def _cstr(addr, data=None, maxlen=600):
    data = DATA if data is None else data
    off = addr - BASE
    end = off
    while end < len(data) and end < off + maxlen and data[end] != 0:
        end += 1
    return data[off:end].decode("latin1")


def _accy_strings(data=None):
    """[(vaddr, texto)] de todas las cadenas que empiezan por `[ACCY]`."""
    data = DATA if data is None else data
    out = []
    for m in re.finditer(re.escape(PREFIX), data):
        i = m.start()
        e = data.find(b"\x00", i)
        out.append((BASE + i, data[i:e].decode("latin1")))
    return out


def _strict_pic(lo, hi, data=None):
    """Regla estricta: `add rX,pc` emparejado con el `ldr rX,[pc,#imm]` más cercano.

    Devuelve {destino_vaddr: [sitios_add]}.
    """
    data = DATA if data is None else data
    n = len(data)
    ldrs = []          # (addr, reg, valor_pool)
    adds = []          # (addr, reg)
    a = lo
    while a < hi:
        off = a - BASE
        if off < 0 or off > n - 8:
            a += 2
            continue
        h = U16S.unpack_from(data, off)[0]
        reg = lit = None
        if (h & 0xF800) == 0x4800:              # ldr rT, [pc, #imm5*4]
            reg = (h >> 8) & 7
            lit = ((a + 4) & ~3) + ((h & 0xFF) * 4)
        elif (h & 0xFF7F) == 0xF85F:            # ldr.w rT, [pc, #imm12]
            h2 = U16S.unpack_from(data, off + 2)[0]
            reg = (h2 >> 12) & 0xF
            lit = ((a + 4) & ~3) + ((((h2 >> 8) & 0xF) << 8) | (h2 & 0xFF))
        if reg is not None:
            o2 = lit - BASE
            if 0 <= o2 <= n - 4:
                ldrs.append((a, reg, U32S.unpack_from(data, o2)[0]))
        if (h & 0xFF00) == 0x4400 and ((h >> 3) & 0xF) == 15:
            adds.append((a, (((h >> 7) & 1) << 3) | (h & 7)))
        a += 2
    by_reg = {}
    for a_, r, w in ldrs:
        by_reg.setdefault(r, []).append((a_, w))
    out = {}
    for a_, r in adds:
        v = by_reg.get(r)
        if not v:
            continue
        la, w = max((x for x in v if x[0] <= a_), key=lambda x: x[0], default=(None, 0))
        if la is None or a_ - la > MAX_LDR_GAP:
            continue
        tgt = (w + (a_ + 4)) & 0xFFFFFFFF
        out.setdefault(tgt, []).append(a_)
    return out


def _prologues(lo, hi, data=None):
    """Inicios de función Thumb: `push {...,lr}`."""
    data = DATA if data is None else data
    out = []
    a = lo
    while a < hi:
        off = a - BASE
        h = U16S.unpack_from(data, off)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
        elif h == 0xE92D and (U16S.unpack_from(data, off + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def _summary():
    with open(ROOT / "analysis" / "s136_accy" / "accy.json", encoding="utf-8") as fh:
        return json.load(fh)


# --------------------------------------------------------------------------
# 1. Las 106 cadenas, con su dirección exacta
# --------------------------------------------------------------------------

EXPECTED_STRINGS = {
    0x43C24CAC: "[ACCY][INFO][HW]:AD=%d, ID=%d",
    0x43C24CCA: "[ACCY][DEBUG][Main] NotifyAttachedUart(%08X)",
    0x43C24CF7: "[ACCY][DEBUG][Main] NotifyAttached(%d)",
    0x43C24D1E: "[ACCY][DEBUG][Main] NotifyDetached",
    0x43C24D41: "[ACCY][INFO][MAIN] NotifyUartCommand[%c%c%c...]",
    0x43C24D71: "[ACCY][ERR][MAIN]:%d:Uart Send Err",
    0x43C24D94: "[ACCY][INFO][MAIN] NotifyUartResponse[%c%c%c...]",
    0x43C24DC5: "[ACCY][INFO][Main] NotifyApi (%02X)",
    0x43C24DE9: "[ACCY][ERR][MAIN]:%d:Uart Send Err:%08X",
    0x43C24E11: "[ACCY][DEBUG][Main] NotifyUartLoopBackTest (%c%c%c%c%c)",
    0x43C24E49: "[ACCY][DEBUG][Main] NotifyUartLoopBackReply (%c%c%c%c%c)",
    0x43C24E82: "[ACCY][DEBUG][Main] Resume Sus-Attached %d, %03X",
    0x43C24EB3: "[ACCY][DEBUG][Main] Suspend Sus-Attached %d, %03X",
    0x43C24EE5: "[ACCY][DEBUG][Main] **** UMMAIN START ****",
    0x43C24F10: "[ACCY][ERR][SENSER] unknown block %04X",
    0x43C24F37: "[ACCY][DEBUG][SENSER] Cmd %04X, S1 %02X",
    0x43C24F5F: "[ACCY][ERR][SENSER] unknown command %04X",
    0x43C24F88: "[ACCY][INFO][UART]:%d:RECIVE DATA %s",
    0x43C24FAD: "[ACCY][INFO][UART]:%d:AccyUartOpen Ch:%d",
    0x43C24FD6: "[ACCY][WARN][UART]:%d:CH:%d UART Open Err:%02X",
    0x43C25005: "[ACCY][WARN][UART]:%d:CH:%d UART Set Func Err:%02X",
    0x43C25038: "[ACCY][WARN][UART]:%d:CH:%d UART Rx Start Err:%02X",
    0x43C2506B: "[ACCY][WARN][UART]:%d:CH:%d UART Tx Start Err:%02X",
    0x43C2509E: "[ACCY][INFO][UART]:%d:AccyUartClose Ch:%d",
    0x43C250C8: "[ACCY][WARN][UART]:%d:CH:%d UART Tx Stop Err:%02X",
    0x43C250FA: "[ACCY][WARN][UART]:%d:CH:%d UART Rx Stop Err:%02X",
    0x43C2512C: "[ACCY][WARN][UART]:%d:AccyUartSend UART FULL",
    0x43C25159: "[ACCY][ERR][UART]:%d:AccyUartSend Size = %d",
    0x43C25185: "[ACCY][INFO][UART]:%d:SEND DATA %s",
    0x43C251A8: "[ACCY][ERR][UART]:%d:IntAccyUartErr = %d",
    0x43C251D1: "[ACCY][ERR][UTILITY]:%d:ConvNum8ToAscii num = %08X",
    0x43C25204: "[ACCY][ERR][UTILITY]:%d:ConvAsciiToNum8 ascii:%08X",
    0x43C25237: "[ACCY][DEBUG][FACTORY]:%d:HELLO Attached",
    0x43C25260: "[ACCY][DEBUG][FACTORY]:%d:AvOut Attached",
    0x43C25289: "[ACCY][DEBUG][FACTORY]:%d:JIRO1.5 Attached",
    0x43C252B4: "[ACCY][DEBUG][FACTORY]:%d:LANC-AVR Attached",
    0x43C252E0: "[ACCY][DEBUG][FACTORY]:%d:UNSUPPORTED(%d) Attached",
    0x43C25313: "[ACCY][DEBUG][FACTORY]:%d:Remote Attached",
    0x43C2533D: "[ACCY][DEBUG][FACTORY]:%d:WaterHousing Attached",
    0x43C25380: "[ACCY][INFO][HOUSING]:%d:NotifyAttached",
    0x43C253A8: "[ACCY][INFO][HOUSING]:%d:NotifyContinuousAttached",
    0x43C253DA: "[ACCY][INFO][HOUSING]:%d:RestoreInfo...Savedata:%02X %02X",
    0x43C25414: "[ACCY][INFO][HOUSING]:%d:NotifyDetached",
    0x43C2543C: "[ACCY][INFO][HOUSING]:%d:NotifyUartTimedOut... %d",
    0x43C2549E: "[ACCY][DEBUG][AVOUT] NotifyDetached(%d)",
    0x43C254C6: "[ACCY][DEBUG][AVOUT] NotifyAttached(%d)",
    0x43C25502: "[ACCY][DEBUG][AVR] NotifyDetached(%d)",
    0x43C25528: "[ACCY][DEBUG][AVR] NotifyAttached(%d)",
    0x43C25560: "[ACCY][ERR][BASE]:%d:NotifyInput...valloc err:%08X",
    0x43C25593: "[ACCY][DEBUG][BASE]:%d:NotifyInput...KeyCode:%08X, State:%d, INFO:%d",
    0x43C255D8: "[ACCY][ERR][BASE]:%d:NotifyInput...Send_Msg end err:%08X",
    0x43C25611: "[ACCY][ERR][BASE]:%d:NotifyInput...Send_Msg free err:%08X",
    0x43C2564B: "[ACCY][ERR][BASE]:%d:NotifyDial...valloc err:%08X",
    0x43C2567D: "[ACCY][DEBUG][BASE]:%d:NotifyDial...KeyCode:%08X, State:%d, INFO:%d",
    0x43C256C1: "[ACCY][ERR][BASE]:%d:NotifyDial...Send_Msg end err:%08X",
    0x43C2570D: "[ACCY][INFO][HELLO]:%d:RetrySendCmd...retry_up:%d",
    0x43C2573F: "[ACCY][ERR][HELLO]%d:Retry SendCmd Buffer Err",
    0x43C2576D: "[ACCY][INFO][HELLO]:%d:State Change To %d",
    0x43C25797: "[ACCY][INFO][HELLO]:%d:NotifyDetached...State:%d",
    0x43C257C8: "[ACCY][INFO][HELLO]:%d:SendCmd...CMD:%c%c%c%c%c Retry:%d",
    0x43C25801: "[ACCY][ERR][HELLO]:%d:SendCmd Buffer Busy Request CMD:%S",
    0x43C2583A: "[ACCY][INFO][HELLO]:%d:NotifyUartTimedOut...RetryCount:%d",
    0x43C25874: "[ACCY][ERR][HELLO]:%d:HELLO Command Not Execution",
    0x43C258A6: "[ACCY][WARN][HELLO]:%d:EventTimeout AISATSU Retryout Count:%d",
    0x43C258E4: "[ACCY][INFO][HELLO]:%d:NotifyUartResponse...State:%02X "
                 "Date:[%02X %02X %02X %02X %02X %02X %02X]",
    0x43C25945: "[ACCY][DEBUG][HELLO]:%d:NotifyUartResponse AISATSU Complete...State:%d",
    0x43C2598C: "[ACCY][INFO][HELLO]:CateId = %08X",
    0x43C259AE: "[ACCY][INFO][HELLO]:%d:NotifyUartResponse...Unmatch State:%d",
    0x43C259EB: "[ACCY][WARN][HELLO]:%d:NotifyUartResponse...Unmatch Response:%02X",
    0x43C25A2D: "[ACCY][WARN][HELLO]:%d:NotifyUartResponse...Unmatch Not Support "
                 "Category:%02X",
    0x43C25A7B: "[ACCY][INFO][HELLO]:%d:NotifyAttached...State:%d",
    0x43C25AAC: "[ACCY][DEBUG][JIRO] NotifyDetached(%d)",
    0x43C25AD3: "[ACCY][DEBUG][JIRO] NotifyAttached(%d)",
    0x43C25B20: "[ACCY][DEBUG][NULL] NotifyAttached(%d)",
    0x43C25B47: "[ACCY][INFO][REMOTE]:%d:NotifyUartCommand...UART CMD:%C%C%C%C%C%C "
                 "[%02X %02X %02X %02X %02X %02X]",
    0x43C25BA9: "[ACCY][WARN][REMOTE]:%d:RecvCmd Unknown Category:%02X",
    0x43C25BDF: "[ACCY][WARN][REMOTE]:%d:EventKey Catwgory:%02X ,Data1:%02X, Data2:%02X",
    0x43C25C26: "[ACCY][INFO][REMOTE]:%d:RetrySendCmd...retry_up:%d",
    0x43C25C59: "[ACCY][ERR][REMOTE]:%d:RetrySendCmd Buffer err",
    0x43C25C88: "[ACCY][INFO][REMOTE]:%d:SaveInfo...GF:%d SS:%d Freeze:%d Photo:%d "
                 "Zoom:%d Tally:%d",
    0x43C25CDB: "[ACCY][DEBUG][REMOTE]:%d:Zoom State Change To %d Speed:%d",
    0x43C25D15: "[ACCY][INFO][REMOTE]:%d:RestoreInfo...Savedata:%02X %02X",
    0x43C25D4E: "[ACCY][INFO][REMOTE]:%d:ExecUartCommand",
    0x43C25D76: "[ACCY][INFO][REMOTE]:%d:To Input KEY:%08X STATE:%08X INFO:%08X",
    0x43C25DB5: "[ACCY][INFO][REMOTE]:%d:SendCmd...CMD:%S retry:%d",
    0x43C25DE7: "[ACCY][ERR][REMOTE]:%d:SendCmd Buffer Busy Request CMD:%S",
    0x43C25E21: "[ACCY][INFO][REMOTE]:%d:TallyControlCmd...retry:%d",
    0x43C25E54: "[ACCY][INFO][REMOTE]:%d:CallForTransaction...Wait Tally Light Response  "
                 "NextState:%d",
    0x43C25EA9: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Command:%02X State:%02X "
                 "CntlState:%d",
    0x43C25EF9: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Buffer Busy CntlState:%d",
    0x43C25F3D: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Tally Light State:%d  "
                 "NextState:%d",
    0x43C25F8B: "[ACCY][INFO][REMOTE]:%d:NotifyApiRequest...Not Support Command:%02X "
                 "or State:%02X",
    0x43C25FDD: "[ACCY][INFO][REMOTE]:%d:AccyCmdClr",
    0x43C26000: "[ACCY][INFO][REMOTE]:%d:RemoteClose...Spinal:%02X  GF:%02X  SS:%02X  "
                 "Freeze:%02X  Photo:%02X  Zoom:%02X",
    0x43C26068: "[ACCY][INFO][REMOTE]:%d:GUIDE FRAME OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C260B0: "[ACCY][INFO][REMOTE]:%d:START STOP OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C260F7: "[ACCY][INFO][REMOTE]:%d:PHOTO FREEZE OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C26140: "[ACCY][INFO][REMOTE]:%d:PHOTO REC OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C26186: "[ACCY][INFO][REMOTE]:%d:ZOOM OFF  KEY:%08X STATE:%08X  INFO:%08X",
    0x43C261C7: "[ACCY][INFO][REMOTE]:%d:NotifyDetached",
    0x43C261EE: "[ACCY][INFO][REMOTE]:%d:NotifyUartTimedOut...RetryCount:%d",
    0x43C26229: "[ACCY][ERR][REMOTE]:%d:TimeoutNotify...Command Not Execution",
    0x43C26266: "[ACCY][DEBUG][REMOTE]:%d:EventTimeout Tally Light TIMEOUT",
    0x43C262A0: "[ACCY][INFO][REMOTE]:%d:NotifyUartResponse...Set Tally Light:%02X",
    0x43C262E2: "[ACCY][DEBUG][REMOTE]:%d:Set Tally Light:%02X State:%d",
    0x43C26319: "[ACCY][INFO][REMOTE]:%d:NotifyAttached",
}


def test_hay_106_cadenas_acc_y():
    assert len(_accy_strings()) == 106
    assert len(EXPECTED_STRINGS) == 106


def test_cada_cadena_acc_y_esta_en_su_direccion():
    got = dict(_accy_strings())
    assert got == EXPECTED_STRINGS


def test_rango_y_bloque_contiguo():
    addrs = sorted(EXPECTED_STRINGS)
    assert addrs[0] == 0x43C24CAC
    assert addrs[-1] == 0x43C26319
    # el bloque es contiguo en .rodata: entre la primera cadena y el final del
    # ultimo nombre de clase solo hay las 9 clases RTTI intercaladas y nada mas
    others = []
    cur = addrs[0] - BASE
    end = 0x43C26340 + len("18AccyUmDeviceRemote") + 1 - BASE
    while cur < end:
        e = DATA.find(b"\x00", cur)
        if e < 0:
            break
        chunk = DATA[cur:e]
        if chunk and not chunk.startswith(b"[ACCY]"):
            others.append((BASE + cur, chunk.decode("latin1")))
        cur = e + 1
    assert [n for _, n in others] == [
        "16AccyUmDeviceBase",
        "24AccyUmDeviceWaterHousing",
        "18AccyUmKeyStatusMgr",
        "17AccyUmDeviceAvOut",
        "15AccyUmDeviceAvr",
        "17AccyUmDeviceHello",
        "16AccyUmDeviceJiro",
        "16AccyUmDeviceNull",
        "18AccyUmDeviceRemote",
    ]


def test_referencia_pic_por_sitio_verificada_a_mano():
    """Tres sitios decodificados a mano: ldr + add -> destino exacto."""
    # 0x43562a8a `ldr r3,[pc,#0x54]` ; 0x43562a8c `add r3,pc`
    assert _u16(0x43562A8A) == 0x4B15
    assert _u16(0x43562A8C) == 0x447B
    assert _u32(0x43562AE0) == 0x006C221C
    assert (0x006C221C + 0x43562A8C + 4) == 0x43C24CAC

    # 0x43566be4 `ldr r3,[pc,#0x148]` ; 0x43566be8 `add r3,pc` -> START STOP OFF
    assert _u16(0x43566BE4) == 0x4B52
    assert _u16(0x43566BE8) == 0x447B
    pool = ((0x43566BE4 + 4) & ~3) + 0x148
    assert pool == 0x43566D30
    assert (_u32(0x43566D30) + 0x43566BE8 + 4) == 0x43C260B0

    # 0x43565834 `ldr r3,[pc,#0x94]` ; 0x4356583c `add r3,pc` -> NotifyInput valloc
    assert _u16(0x43565834) == 0x4B25
    assert _u16(0x4356583C) == 0x447B
    assert (_u32(0x435658CC) + 0x4356583C + 4) == 0x43C25560


def test_regla_estricta_resuelve_111_sitios_en_61_funciones():
    pic = _strict_pic(ACCY_CODE_LO, ACCY_CODE_HI)
    accy = {d: v for d, v in pic.items()
            if d in EXPECTED_STRINGS}
    n_sites = sum(len(v) for v in accy.values())
    assert n_sites == 111
    assert len(accy) == 106          # las 106 cadenas referenciadas
    assert all(accy.values())        # ninguna sin referencia
    # los sitios caen dentro de la región ACCY
    for d, sites in accy.items():
        for s in sites:
            assert ACCY_CODE_LO <= s < ACCY_CODE_HI
    # 61 funciones emisoras (prólogo push{...,lr} más cercano hacia atrás)
    pro = _prologues(ACCY_CODE_LO, ACCY_CODE_HI)
    funcs = set()
    for sites in accy.values():
        for s in sites:
            cand = [p for p in pro if p <= s]
            funcs.add(cand[-1])
    assert len(funcs) == 61
    for f in funcs:
        assert f in [0x43562A08, 0x43562DB0, 0x43562E22, 0x43562E54, 0x43562EA4,
                     0x43562F34, 0x43562F90, 0x43563004, 0x435630AC, 0x43563138,
                     0x43563174, 0x435631D2, 0x43563310, 0x43563360, 0x435638EE,
                     0x43563A94, 0x43563BF8, 0x43563DE8, 0x43563EF4, 0x43564024,
                     0x435641B6, 0x435641EC, 0x435646A4, 0x435647C0, 0x43564AB4,
                     0x43564C0C, 0x43564CA4, 0x43564D98, 0x43565188, 0x43565508,
                     0x4356554C, 0x43565680, 0x435656D4, 0x43565814, 0x435658DC,
                     0x43565B14, 0x43565B84, 0x43565BA4, 0x43565BE0, 0x43565CE4,
                     0x43565D90, 0x43565EB8, 0x43565FD0, 0x43566018, 0x43566150,
                     0x43566290, 0x435663B8, 0x435664D0, 0x43566558, 0x43566580,
                     0x435665F8, 0x435668B4, 0x4356692C, 0x43566998, 0x43566A54,
                     0x43566B2C, 0x43566B54, 0x43566D44, 0x43566D8C, 0x43566E5C,
                     0x43566EC0]


def test_sub_bloques():
    got = {}
    for vaddr, txt in _accy_strings():
        m = re.match(r"\[ACCY\]\[[A-Z]+\]\[([A-Za-z0-9_]+)\]", txt)
        assert m, txt
        got.setdefault(m.group(1), []).append(vaddr)
    expected = {"HW": 1, "Main": 9, "MAIN": 4, "SENSER": 3, "UART": 13,
                "UTILITY": 2, "FACTORY": 7, "HOUSING": 5, "AVOUT": 2, "AVR": 2,
                "BASE": 7, "HELLO": 16, "JIRO": 2, "NULL": 1, "REMOTE": 32}
    assert {k: len(v) for k, v in got.items()} == expected
    assert sum(expected.values()) == 106


def test_rtti_jerarquia_de_clases():
    """Tabla de typeinfo: AccyUmDeviceBase + 7 derivadas y AccyUmKeyStatusMgr suelta."""
    assert _u32(0x43FD7C8C) == 0x43FD04F8      # vtable __class_type_info
    assert _u32(0x43FD7C90) == 0x43C2536D      # nombre AccyUmDeviceBase
    # AccyUmDeviceWaterHousing (__si_class_type_info, base AccyUmDeviceBase)
    assert _u32(0x43FD7D6C) == 0x43FD03D8
    assert _u32(0x43FD7D70) == 0x43C2546E
    assert _u32(0x43FD7D74) == 0x43FD7C8C
    # AccyUmKeyStatusMgr: typeinfo simple, SIN clase base
    assert _u32(0x43FD7D78) == 0x43FD04F8
    assert _u32(0x43FD7D7C) == 0x43C25489
    # derivadas con base AccyUmDeviceBase
    for ti, name in ((0x43FD7D80, 0x43C254EE), (0x43FD7D8C, 0x43C2554E),
                      (0x43FD7D98, 0x43C256F9), (0x43FD7DA4, 0x43C25AFA),
                      (0x43FD7DB0, 0x43C25B0D), (0x43FD7DBC, 0x43C26340)):
        assert _u32(ti) == 0x43FD03D8
        assert _u32(ti + 4) == name
        assert _u32(ti + 8) == 0x43FD7C8C
    # los nombres llevan delante la longitud en ASCII
    assert _cstr(0x43C2536D) == "16AccyUmDeviceBase"
    assert _cstr(0x43C2546E) == "24AccyUmDeviceWaterHousing"
    assert _cstr(0x43C25489) == "18AccyUmKeyStatusMgr"
    assert _cstr(0x43C254EE) == "17AccyUmDeviceAvOut"
    assert _cstr(0x43C2554E) == "15AccyUmDeviceAvr"
    assert _cstr(0x43C256F9) == "17AccyUmDeviceHello"
    assert _cstr(0x43C25AFA) == "16AccyUmDeviceJiro"
    assert _cstr(0x43C25B0D) == "16AccyUmDeviceNull"
    assert _cstr(0x43C26340) == "18AccyUmDeviceRemote"


def test_taxonomia_de_accesorios_en_la_fabrica():
    """ID de accesorio -> nombre, leido de los `cmp` de la fabrica 0x435646a4."""
    # r4 == 4 -> HELLO Attached ; r4 == 0 -> AvOut ; r4 == 1 -> JIRO1.5 ;
    # r4 == 5 -> LANC-AVR ; resto -> UNSUPPORTED(%d)
    assert _u16(0x435646BA) == 0x2C04          # cmp r4, #4
    assert _u16(0x43564712) == 0x2C01          # cmp r4, #1
    assert _u16(0x43564740) == 0x2C05          # cmp r4, #5
    assert _u16(0x43564788) == 0x2C00          # cmp r4, #0
    # bitmask de la segunda fabrica: 0x80 -> Remote, 0x40 -> WaterHousing
    assert _u16(0x435647F6) == 0xF016          # ands r4, r6, #0x80
    assert (_u16(0x435647F8) & 0xFF) == 0x80
    assert _u16(0x43564820) == 0xF016          # tst.w r6, #0x40
    assert (_u16(0x43564822) & 0xFF) == 0x40


def test_codigos_de_tecla_del_mando_remoto():
    """Pool literal de 0x43566b54: los 5 codigos de tecla enviados por NotifyInput."""
    assert _u32(0x43566CF8) == 0x0A000009      # GUIDE FRAME OFF
    assert _u32(0x43566CFC) == 0x0A00000D      # START STOP OFF
    assert _u32(0x43566D04) == 0x0A000008      # PHOTO FREEZE OFF
    assert _u32(0x43566D0C) == 0x0A00000C      # PHOTO REC OFF
    assert _u32(0x43566D14) == 0x0A000011      # ZOOM OFF
    # y las trazas correspondientes
    assert _cstr(0x43C26068).endswith("GUIDE FRAME OFF  KEY:%08X STATE:%08X  INFO:%08X")
    assert _cstr(0x43C260B0).endswith("START STOP OFF  KEY:%08X STATE:%08X  INFO:%08X")
    assert _cstr(0x43C260F7).endswith("PHOTO FREEZE OFF  KEY:%08X STATE:%08X  INFO:%08X")
    assert _cstr(0x43C26140).endswith("PHOTO REC OFF  KEY:%08X STATE:%08X  INFO:%08X")
    assert _cstr(0x43C26186).endswith("ZOOM OFF  KEY:%08X STATE:%08X  INFO:%08X")


def test_estructura_del_mensaje_de_entrada():
    """NotifyInput (0x43565814) escribe KeyCode/ID/State/INFO y envia por OSAL."""
    assert _bytes(0x4356584C, 2) == bytes.fromhex("5860")  # str r0, [r3, #4]
    assert _bytes(0x43565850, 2) == bytes.fromhex("1e60")  # str r6, [r3]
    assert _bytes(0x43565852, 2) == bytes.fromhex("9d60")  # str r5, [r3, #8]
    assert _bytes(0x43565854, 2) == bytes.fromhex("df60")  # str r7, [r3, #0xc]
    # primer argumento de osal_snd_msg (0x4356120c) en NotifyInput
    assert _u32(0x435658BC) == 0x007A0020
    # GID emisor del modulo: escrito en [msg-4] en 0x43562270
    assert _u32(0x43562284) == 0x008F0139


def test_el_codigo_acc_y_no_referencia_cadenas_del_obturador():
    """Negativo verificado: la region ACCY solo referencia 'Valloc error!' fuera de [ACCY]."""
    pic = _strict_pic(ACCY_CODE_LO, ACCY_CODE_HI)
    externos = []
    for dest in pic:
        if dest in EXPECTED_STRINGS:
            continue
        off = dest - BASE
        if not (0 <= off < len(DATA)):
            continue
        # solo cuentan los destinos que son realmente inicio de cadena imprimible
        if off > 0 and DATA[off - 1] == 0 and DATA[off] != 0:
            raw = DATA[off:DATA.find(b"\x00", off)]
            if all(32 <= c < 127 for c in raw):
                externos.append((dest, raw.decode("latin1")))
    assert externos == [(0x43C24C9E, "Valloc error!")]


def test_ninguna_traza_acc_y_habla_del_obturador():
    keywords = ("shut", "silen", "electro", "mech", "curtain", "mirror", "imager",
                "sensor", "readout", "bracket", "sweep", "interval", "flash", "lens",
                "mount", "batt")
    for vaddr, txt in _accy_strings():
        low = txt.lower()
        for kw in keywords:
            assert kw not in low, f"{hex(vaddr)} menciona {kw}"


def test_diferencial_el_token_no_existe_en_a7s_ni_en_a6300():
    for path in (A7S, A6300):
        d = _data(path)
        assert d.count(b"[ACCY]") == 0
        assert d.count(b"UMMAIN") == 0
        assert d.count(b"AccyUart") == 0
        assert d.count(b"NotifyAttached") == 0
        assert d.count(b"START STOP") == 0
        assert d.count(b"Tally") == 0


def test_diferencial_las_clases_acc_y_si_existen_en_a7s_y_a6300():
    """Las MISMAS clases AccyUm* existen en los otros dos firmwares."""
    for path, block, base in ((A7S, 0x43C25A23, 0x43C25A4A),
                              (A6300, 0x43D0C9A2, 0x43D0C9C9)):
        d = _data(path)
        for name in ("16AccyUmDeviceBase", "24AccyUmDeviceWaterHousing",
                     "18AccyUmKeyStatusMgr", "17AccyUmDeviceAvOut", "15AccyUmDeviceAvr",
                     "17AccyUmDeviceHello", "16AccyUmDeviceJiro", "16AccyUmDeviceNull",
                     "18AccyUmDeviceRemote"):
            assert d.count(name.encode()) == 1, (path, name)
        # ... y la A7S/A6300 anaden las clases AccyMi* que la A6000 no tiene
        assert d.count(b"16AccyMiDeviceBase") == 1
        assert d.count(b"17AccyMiDeviceLight") == 1
        assert _cstr(block, d) == "16AccyMiDeviceBase"
        assert _cstr(base, d) == "16AccyUmDeviceBase"
    assert DATA.count(b"AccyMi") == 0


def test_ninguna_traza_acc_y_existe_textualmente_en_los_otros_dos():
    for path in (A7S, A6300):
        d = _data(path)
        for vaddr, txt in _accy_strings():
            assert txt.encode("latin1") not in d, (path, hex(vaddr))


def test_json_del_hito_consistente_con_los_bytes():
    s = _summary()
    assert s["counters"]["n_strings"] == 106
    assert s["counters"]["n_sites"] == 111
    assert s["counters"]["n_functions"] == 61
    assert s["counters"]["n_subblocks"] == 15
    assert s["counters"]["token_in_a7s"] == 0
    assert s["counters"]["token_in_a6300"] == 0
    assert s["string_range"] == ["0x43c24cac", "0x43c26319"]
    assert s["xref_rule"].startswith("estricta")
    # cada cadena del JSON debe existir en el binario en su direccion
    for e in s["strings"]:
        assert _cstr(int(e["vaddr"], 16)) == e["text"]
