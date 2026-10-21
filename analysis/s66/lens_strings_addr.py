"""S62: direcciones verificadas por búsqueda de bytes de las cadenas clave (A6000 y A7S)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "s58"))
from tdis import data, B  # noqa: E402

# Textos EXACTOS (comprobar con .find en el blob; dirección = B + offset).
STRINGS = [
    # --- ruta de actualización de firmware de lente ---
    "[MOUNT_ERROR]: [BL]FirmUp Error : CAIF CASND LUPDT_INFO",
    "[MOUNT_ERROR]: [BL]FirmUp Error : CAIF CASND LUPDT_DATA",
    "[MOUNT_ERROR]: [BL]FirmUpReq Error : CAIF REQ ERROR",
    "[MOUNT_ERROR]: [BL]GetLensVersion Error : ERRCD_FIRMUP_UNSUPPORT",
    "[MOUNT_ERROR]: [BL]GetLensVersion Error : ERRCD_FIRM_ERROR",
    "[MOUNT_ERROR]: [BL]GetLensVersion Error : ERRCD_LENS_UNMOUNT",
    "[MOUNT_ERROR]: [BL]FirmUpReq Error : ERRCD_FIRMUP_BUSY",
    "[MOUNT_ERROR]: [BL]FirmUpReq Error : ERRCD_PARAM_ERROR",
    "[MOUNT_ERROR]: [BL]LensFirmUpdateResult : Error Code = %d",
    "[MOUNT_ERROR]: [BL]LensFirmUpdateResult : Illegal Error Code = %d",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE REQ RCV",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE OK",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE NG",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE WAIT",
    "[MOUNT_ERROR]: [BL]PREPARE UPDATE TIME_OUT",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE CHECK OK",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE CHECK NG",
    "[MOUNT_DEBUG]: [BL]PREPARE UPDATE CHECK NG LENS_NONE",
    "[MOUNT_DEBUG]: [BL]UPDATE UNPLUG USB",
    "[MOUNT_DEBUG]: [L->B]UPDATE_ON",
    "[MOUNT_DEBUG]: [L->B]UPDATE_ON_NG",
    "[MOUNT_DEBUG]: [L->B]UPDATE_DATA",
    "[MOUNT_DEBUG]: [L->B]UPDATE_NG",
    "[MOUNT_DEBUG]: [B->L]UPDATE_DATA",
    "[MOUNT_DEBUG]: [B->L]UPDATE_ON",
    "[MOUNT_DEBUG]: [BL]UPDATE times %d",
    "[MOUNT_DEBUG]: [BL]UPDATE %d",
    "[MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_VERSION",
    "[MOUNT_INFO]: [BL]UUD CallBack : MSGID_GET_FORCE_FIRMUP",
    "[MOUNT_INFO]: [BL]UUD CallBack : MSGID_FIRM_UP_REQ",
    "[MOUNT_INFO]: [BL]UUD CallBack : MSGID_PREPARE_UPDATE",
    "[MOUNT_INFO]: [BL]UUD CallBack : MSGID_UNPLUG_USB",
    "[MOUNT_ERROR]: [BL]UUD CallBack : meg_id illegal : meg_id=%d",
    "[MOUNT_ERROR]: [BL]LENS FIRMERR",
    # --- crédito / estado ---
    "[MOUNT_DEBUG]: [L->B]CS_CREDIT",
    "[MOUNT_DEBUG]: [B->L]CS_CREDIT=%d",
    "[MOUNT_DEBUG]: [BL ERR]LIF CREDIT RegistErro Lens doesn't know = %d",
    "[MOUNT_INFO]: [BL]LIF Command Change : 0x%X >>> 0x%X",
    # --- Eclipse / DividedInfo (comunicación con la lente) ---
    "[MOUNT_DEBUG]: [BL]EclipseDataComState [%d] => [%d]",
    "[MOUNT_DEBUG]: [BL]ZPD change EclipseDataComState from STANDBY to START",
    "[MOUNT_DEBUG]: [BL]EclipseDataComState [%d] => [%d] in Mount_InitializeEclipseComState",
    "[MOUNT_DEBUG]: Mount_EclipseComInit Mount_DividedInfo.cpp line %d",
    "[MOUNT_DEBUG]: MOUNT_DIVIDED_INFO_1st message",
    "[MOUNT_DEBUG]: MOUNT_DIVIDED_INFO_2nd message %d",
    "[MOUNT_ERROR]: [BL]ECLIPSE_COM_STATE is INIT in VSYNC at Mount_DividedInfo.cpp %d",
    # --- bus serie / handshake ---
    "[MOUNT_DEBUG]: [BL]UART_HZ 750:%d 1500%d",
    "[MOUNT_ERROR]: [BL][L->B]UART_HZ NG",
    "[MOUNT_DEBUG]: [BL]UART_HS_COMPLETE NO_WAIT",
    "[MOUNT_DEBUG]: [BL]UART_HS_COMPLETE",
    "[MOUNT_DEBUG]: [BL][HS]CS_HIGH",
    "[MOUNT_DEBUG]: [BL][HS]DATA_HIGH",
    "[MOUNT_DEBUG]: [BL][HS]CS_LOW",
    "[MOUNT_DEBUG]: [BL][HS]COMPLETE",
    "[MOUNT_DEBUG]: [BL]CHG FREQ, %d, %d, %d",
    "[MOUNT_ERROR]: [BL]FREQ Now:%d, Send:%d",
    "[MOUNT_DEBUG]: [BL]WAIT CHGFREQ1",
    "[MOUNT_DEBUG]: [BL]WAIT CHGFREQ2",
    "[MOUNT_DEBUG]: [BL]WAIT NEXTVD",
    "[MOUNT_DEBUG]: [BL]SYSTEM_HZ:%d",
    # --- BonoboDSP ---
    "[LENS_PDR]: BonoboDSP_Send: Data latch failed!",
    "[LENS_PDR]: BonoboDSP_Send:[ch0]Data latch failed!",
    "[LENS_PDR]: BonoboDSP_Send:[ch1]Data latch failed!",
    "[LENS_PDR]: BonoboDSP_Rcv: paritycheck_error!",
    "Ch.0/00,01,02,03,04,05,06,07,Ch.1/00,01,02,03,04,05,06,07,Count,",
]


def find_all(d, s):
    b = s.encode()
    out, i = [], d.find(b)
    while i >= 0:
        out.append(B + i)
        i = d.find(b, i + 1)
    return out


def table(model="A6000"):
    d = data(model)
    res = []
    for s in STRINGS:
        res.append((s, find_all(d, s)))
    return res


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "A6000"
    for s, hits in table(model):
        print(f"{','.join(hex(h) for h in hits) or '-':28s} {s}")
