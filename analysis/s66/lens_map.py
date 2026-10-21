"""S62: mapa string -> refs PIC (ldr lit + add pc) -> función contenedora (A6000/A7S).

Uso: lens_map.py A6000|A7S   (imprime refs y funciones para la lista de cadenas clave)
"""
import sys, re, bisect, struct
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B, u32, ins_list  # noqa: E402
from strrefs import scan, func_of  # noqa: E402

# Direcciones absolutas de cadenas clave (A6000). Para A7S se recalculan por búsqueda.
TARGETS_A6000 = {
    0x43c9a09f: "FirmUp Error : CAIF CASND LUPDT_INFO",
    0x43c9a0d7: "FirmUp Error : CAIF CASND LUPDT_DATA",
    0x43c9a144: "FirmUpReq Error : CAIF REQ ERROR",
    0x43c99201: "UUD CallBack : MSGID_GET_VERSION",
    0x43c99234: "UUD CallBack : MSGID_GET_FORCE_FIRMUP",
    0x43c9926c: "UUD CallBack : MSGID_FIRM_UP_REQ",
    0x43c9929f: "UUD CallBack : MSGID_PREPARE_UPDATE",
    0x43c992d5: "UUD CallBack : MSGID_UNPLUG_USB",
    0x43c98eb8: "[L->B]UPDATE_ON",
    0x43c98ed7: "[L->B]UPDATE_ON_NG",
    0x43c98ef9: "[L->B]UPDATE_DATA",
    0x43c98f1a: "[L->B]UPDATE_NG",
    0x43c98aa5: "[B->L]UPDATE_DATA",
    0x43c9986c: "[B->L]UPDATE_ON",
    0x43c9905f: "[BL]PREPARE UPDATE REQ RCV",
    0x43c99089: "[BL]PREPARE UPDATE OK",
    0x43c990ae: "[BL]PREPARE UPDATE NG",
    0x43c990d3: "[BL]PREPARE UPDATE WAIT",
    0x43c99126: "[BL]PREPARE UPDATE TIME_OUT",
    0x43c99151: "[BL]PREPARE UPDATE CHECK OK",
    0x43c9917c: "[BL]PREPARE UPDATE CHECK NG",
    0x43c991a7: "[BL]PREPARE UPDATE CHECK NG LENS_NONE",
    0x43c991dc: "[BL]UPDATE UNPLUG USB",
    0x43c98cbf: "[BL]LENS FIRMERR",
    0x43c98e76: "LensFirmUpdateResult : Illegal Error Code",
    0x43c9a1b9: "LensFirmUpdateResult : Error Code = %d",
    0x43c9a178: "GetLensVersion Error : ERRCD_FIRMUP_UNSUPPORT",
    0x43c98f79: "GetLensVersion Error : ERRCD_FIRM_ERROR",
    0x43c98fb4: "GetLensVersion Error : ERRCD_LENS_UNMOUNT",
    0x43c98ff1: "FirmUpReq Error : ERRCD_FIRMUP_BUSY",
    0x43c99028: "FirmUpReq Error : ERRCD_PARAM_ERROR",
    0x43c98f39: "[BL]UPDATE times %d",
    0x43c98f5c: "[BL]UPDATE %d",
    0x43c98db7: "[L->B]CS_CREDIT",
    0x43c98dfe: "[B->L]CS_CREDIT=%d",
    0x43c981b4: "LIF CREDIT RegistErro Lens doesn't know",
    0x43c9834d: "EclipseDataComState [%d] => [%d]",
    0x43c986b5: "ZPD change EclipseDataComState from STANDBY to START",
    0x43c98754: "Mount_EclipseComInit",
    0x43c98218: "MOUNT_DIVIDED_INFO_1st message",
    0x43c98246: "MOUNT_DIVIDED_INFO_2nd message",
    0x43c99540: "UART_HZ 750:%d 1500%d",
    0x43c99569: "[L->B]UART_HZ NG",
    0x43c9958d: "UART_HS_COMPLETE NO_WAIT",
    0x43c995b9: "UART_HS_COMPLETE",
    0x43c98ac6: "[HS]CS_HIGH",
    0x43c98ae5: "[HS]DATA_HIGH",
    0x43c98b06: "[HS]CS_LOW",
    0x43c98b24: "[HS]COMPLETE",
    0x43c993cd: "CHG FREQ, %d, %d, %d",
    0x43c9a7ca: "BonoboDSP_Send: Data latch failed!",
    0x43c9a7fa: "BonoboDSP_Send:[ch0]Data latch failed!",
    0x43c9a82e: "BonoboDSP_Send:[ch1]Data latch failed!",
    0x43c9a862: "BonoboDSP_Rcv: paritycheck_error!",
    0x43c9a54c: "Ch.0/00..Count, (log CANAL DSP)",
    0x43c9a58e: "LENS_MOUNT (tag log DSP)",
}


def movw_movt_targets(m):
    """Direcciones construidas con pares movw/movt."""
    ins = ins_list(m)
    out = {}
    for k in range(len(ins) - 1):
        a, mn, op = ins[k]
        if mn != "movw":
            continue
        m1 = re.match(r"(r\d+), #(\d+)$", op)
        if not m1:
            continue
        b, mn2, op2 = ins[k + 1]
        if mn2 != "movt" or not op2.startswith(m1.group(1) + ", #"):
            continue
        lo = int(m1.group(2))
        hi = int(op2.split("#")[1])
        addr = (hi << 16) | lo
        out.setdefault(addr, []).append(a)
    return out


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else "A6000"
    d = data(model)
    refs, starts = scan(model)
    mt = movw_movt_targets(model)
    targets = dict(TARGETS_A6000)
    if model != "A6000":
        # recalcular direcciones buscando el prefijo de cada cadena
        import re as _re
        newt = {}
        for addr, name in TARGETS_A6000.items():
            probe = d[addr - B:addr - B + 24]
            i = d.find(probe)
            if i >= 0:
                newt[B + i] = name
        targets = newt
    for addr, name in sorted(targets.items()):
        hits = refs.get(addr, []) + mt.get(addr, [])
        funcs = sorted({func_of(starts, h) for h in hits if func_of(starts, h)})
        print(f"{addr:#010x} {name}")
        for h in sorted(set(hits)):
            print(f"    ref@{h:#x} func~{func_of(starts, h) or 0:#x}")
        if not hits:
            print("    (sin refs PIC/movw locales)")


if __name__ == "__main__":
    main()
