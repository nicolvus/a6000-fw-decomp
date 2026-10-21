"""S68: gestion de batería, alimentación y carga (NP-FW50) en av-cam.bin A6000 — verificaciones contra bytes.

Alcance: línea de ingeniería inversa GENERAL de la cámara (energía/batería), independiente de la
línea SilentShutter/obturador electrónico. Nada se ejecuta del firmware: solo lectura de bytes.

Hechos verificados aquí:
- Cadenas exactas de batería/nivel en direcciones exactas (Set UPM Battery Level, BatteryInfo,
  IRLight/VideoLight Battery Info, ACV_BATT_Snd, BATT_*_Snd, Box_Temperature_Snd).
- Funciones: 0x4378f364 (Set UPM Battery Level lee 8 bytes del dispositivo), 0x437b7d6c
  (BatteryInfo OSAL_ERROR), 0x437cf1f0 (IRLight), 0x437d0768 (VideoLight), 0x4385fff0 (CamStrbCharge).
- Nombres de variables de carga/flash en 0x43ccd8aa..0x43ccdc92 (uc_ChargeCommand, uc_ChargeStatus,
  uc_ChargeEnable, uc_ChargeForceOff, uc_ChargeRequest, uc_ChargeStopRequest, b_SBChargeReq, ...).
- Power save del imager y SubLVDS, espera de reducción de voltaje de lente, cancelación de captura
  por power-off.
- Cadenas AUSENTES (NP-FW, FW50, USB power, AutoPowerOff, PowerMgr, Energy, Drain, libbackup).
- Comparativa A6000 fw3.21 vs A7S fw3.20 (BatteryInfo y ACV_BATT_Snd solo en A6000).

Informes: analysis/s68_power/battery_power.md · analysis/s68_power/battery_power.json
"""
import hashlib
import re
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB, Cs

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

SHA_A6000 = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"
SHA_A7S = "b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e"

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
MD.skipdata = True

STR_RE = re.compile(rb"[\x20-\x7e]{4,}")
LIT_RE = re.compile(r"^(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$")


def u32(model, a):
    import struct

    return struct.unpack_from("<I", data(model)[a - B:a - B + 4])[0]


def cstr(model, addr):
    """Cadena C terminada en NUL."""
    d = data(model)
    off = addr - B
    if off < 0 or off >= len(d):
        return None
    end = d.find(b"\x00", off, off + 256)
    if end < 0:
        return None
    s = d[off:end]
    if not s or any(b < 0x20 and b not in (0x09, 0x0A, 0x0D) or b > 0x7E for b in s):
        return None
    return s.decode("ascii").rstrip("\n")


def strings_in(model, lo, hi):
    d = data(model)
    out = []
    for m in STR_RE.finditer(d[lo - B:hi - B]):
        out.append((lo + m.start(), m.group().decode("ascii", "replace")))
    return out


def log_strings_in_func(model, start, end):
    """Cadenas referenciadas por el patrón PIC (ldr [pc,#imm] + add pc) dentro del rango."""
    d = data(model)
    pending = {}
    found = []
    for i in MD.disasm(d[start - B:end - B], start):
        if i.mnemonic == ".byte":
            continue
        m = LIT_RE.match(i.op_str)
        if i.mnemonic.startswith("ldr") and m:
            la = ((i.address + 4) & ~3) + int(m.group(2), 0)
            pending[m.group(1)] = la
            continue
        if i.mnemonic == "add" and i.op_str.endswith(", pc"):
            reg = i.op_str.split(",")[0]
            la = pending.pop(reg, None)
            if la is None:
                continue
            tgt = (u32(model, la) + (i.address + 4)) & 0xFFFFFFFF
            s = cstr(model, tgt)
            if s is not None:
                found.append((i.address, tgt, s))
    return found


class ShaAndModel(unittest.TestCase):
    def test_sha_a6000(self):
        self.assertEqual(hashlib.sha256(data("A6000")).hexdigest(), SHA_A6000)

    def test_sha_a7s(self):
        self.assertEqual(hashlib.sha256(data("A7S")).hexdigest(), SHA_A7S)


class BatteryStringsExact(unittest.TestCase):
    """Cadenas exactas de batería/nivel en direcciones exactas (VERIFICADO contra bytes)."""

    def test_battery_level_and_info_strings(self):
        expected = {
            0x43CA2DFD: "[CAMERA_MAIN_SYNC]: Set UPM Battery Level [state] %d [Error] %d",
            0x43CA6A3C: "[CAMERA_MAIN_FC]: OSAL_ERROR: BatteryInfo",
            0x43CA6A5A: "BatteryInfo",
            0x43CA7E2E: "[IRLight] Battery Info : %d",
            0x43CA7F1D: "[VideoLight] Battery Info : %d",
            0x43C8F83B: "ACV Error Voltage",
            0x43C8F95E: "ACV_BATT_Snd",
            0x43C8F96B: "BATT_AUTH_Snd",
            0x43C8F979: "BATT_STATE1_Snd",
            0x43C8F989: "BATT_STATE2_Snd",
            0x43C8F999: "BATT_STATE3_Snd",
            0x43C8F9A9: "BATT_TYPE1_Snd",
            0x43C8F9B8: "BATT_TYPE2_Snd",
            0x43C8F9FC: "Box_Temperature_Snd",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr("A6000", addr), text, hex(addr))

    def test_flash_charge_strings(self):
        """SB_CHARGE / CamStrbChargeOn/Off: subsistema de flash, NO de batería principal."""
        expected = {
            0x43CB4C23: "SB_CHARGE",
            0x43CB4CAC: "WAIT_MEM_CHG",
            0x43CB58B3: "EV CamStrbChargeOn",
            0x43CB58C6: "EV CamStrbChargeOff",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr("A6000", addr), text, hex(addr))

    def test_power_save_strings(self):
        expected = {
            0x43C90F07: "[CAMCORE]: MonPowersave[%d] is already Enabled !",
            0x43C9469C: "[CAM_IMAGER]: ImagerCommon::MacroPowerSaveOnRequest Unknown index number",
            0x43C94729: "[CAM_IMAGER]: ImagerCommon::MacroPowerOffRequest Unknown index number",
            0x43C95466: "[CAM_IMAGER]: SubLVDS PowerSaveOn: SUBLCNTL_DFE1 does not exist on Regulus.",
            0x43C954ED: "[CAM_IMAGER]: SubLVDS PowerSaveOff: SUBLCNTL_DFE1 does not exist on Regulus.",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr("A6000", addr), text, hex(addr))

    def test_lens_and_capture_power_strings(self):
        self.assertEqual(
            cstr("A6000", 0x43CC7AA4),
            "[IMAGING_CAP]: Warning! Wait E-MountLens ReduceVoltage Wait(%d ms)",
        )
        self.assertEqual(
            cstr("A6000", 0x43CA9D85),
            "[IMAGING_CAP]: CapMgr)CaptureCancel_PowerOffDetect() offFactor=%d",
        )


class ChargeVariableNames(unittest.TestCase):
    """Bloque de nombres de variables de carga/flash en 0x43ccd8aa..0x43ccdc92."""

    def test_charge_variable_names_at_exact_addresses(self):
        expected = {
            0x43CCD8AB: "us_RechargeIntervalCnt",  # el bloque empieza con un '#' en 0x43CCD8AA
            0x43CCD8C2: "uc_ChargeCommand",
            0x43CCD8D3: "us_ChargeCnt",
            0x43CCD8E0: "uc_ChargeOnCnt",
            0x43CCD8EF: "uc_ChargeStatus",
            0x43CCD8FF: "uc_AcvOn",
            0x43CCD908: "uc_UnregVolltage",
            0x43CCD919: "uc_CapacitorStatus",
            0x43CCD92C: "uc_PwmStatus",
            0x43CCD939: "uc_ChargeEnable",
            0x43CCD949: "us_ActivePwmDutySlope",
            0x43CCD95F: "uc_GetInfoOK",
            0x43CCD96C: "uc_ChargeForceOff",
            0x43CCDA49: "uc_ChargeRequest",
            0x43CCDA5A: "uc_ChargeStopRequest",
            0x43CCDC63: "b_GpflLogicPowerOn",
            0x43CCDC76: "b_SBChargeReq",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr("A6000", addr), text, hex(addr))

    def test_charge_variables_are_contiguous_name_block(self):
        """Los nombres forman un bloque contiguo terminado en NUL entre 0x43ccd8aa y 0x43ccdc92."""
        d = data("A6000")
        start = 0x43CCD8AA - B
        end = 0x43CCDC92 - B
        block = d[start:end]
        self.assertIn(b"uc_ChargeCommand", block)
        self.assertIn(b"uc_ChargeStatus", block)
        self.assertIn(b"b_SBChargeReq", block)
        # el bloque termina justo antes del siguiente string de log
        self.assertEqual(block[-1], 0)


class BatteryFunctions(unittest.TestCase):
    """Instrucciones clave de las funciones de batería (VERIFICADO contra instrucciones)."""

    def _ops(self, start, end):
        d = data("A6000")
        return [(i.address, i.mnemonic, i.op_str) for i in MD.disasm(d[start - B:end - B], start)
                if i.mnemonic != ".byte"]

    def test_set_upm_battery_level_reads_8_bytes(self):
        """0x4378f364: ldm.w r5,{r0,r1} lee 8 bytes de obj+5; error path movs r0,#4."""
        ops = self._ops(0x4378F364, 0x4378F3E0)
        self.assertIn((0x4378F37C, "ldm.w", "r5, {r0, r1}"), ops)
        self.assertIn((0x4378F3A8, "movs", "r0, #4"), ops)
        self.assertIn((0x4378F3AE, "ldrsb.w", "r2, [r5, #5]"), ops)

    def test_batteryinfo_osal_error(self):
        """0x437b7d6c: compara resultado con 2, lee obj[0x49c], logea OSAL_ERROR: BatteryInfo."""
        ops = self._ops(0x437B7D6C, 0x437B7E10)
        self.assertIn((0x437B7D74, "cmp", "r0, #2"), ops)
        self.assertIn((0x437B7D7A, "ldr", "r3, [r5]"), ops)
        self.assertIn((0x437B7D7C, "ldrb.w", "r5, [r3, #0x49c]"), ops)

    def test_irlight_battery_info_fields(self):
        """0x437cf1f0: lee flags de r1 offsets 0x1a, 0x22, 0x7, 0xf."""
        ops = self._ops(0x437CF1F0, 0x437CF31E)
        self.assertIn((0x437CF1F8, "ldrb", "r3, [r1, #0x1a]"), ops)
        self.assertIn((0x437CF1FE, "ldrb.w", "r2, [r1, #0x22]"), ops)
        self.assertIn((0x437CF20C, "ldrb", "r2, [r1, #7]"), ops)
        self.assertIn((0x437CF212, "ldrb", "r2, [r1, #8]"), ops)
        self.assertIn((0x437CF220, "ldrb", "r3, [r1, #0xf]"), ops)

    def test_videolight_battery_info_threshold_770(self):
        """0x437d0768: umbral 0x302 = 770 y lógica de contadores de recarga."""
        ops = self._ops(0x437D0768, 0x437D0826)
        self.assertIn((0x437D07C2, "movw", "r3, #0x302"), ops)
        self.assertIn((0x437D07C6, "cmp", "r0, r3"), ops)
        self.assertIn((0x437D07D2, "ldrh", "r7, [r4, #2]"), ops)


class FlashChargeFunction(unittest.TestCase):
    """0x4385fff0 CamStrbChargeOn/Off emite eventos de carga de flash."""

    def test_cam_strb_charge_emits_events(self):
        d = data("A6000")
        ins = list(MD.disasm(d[0x4385FFF0 - B:0x43860600 - B], 0x4385FFF0))
        calls = [int(i.op_str[1:], 16) for i in ins if i.mnemonic == "bl" and i.op_str.startswith("#")]
        # strings de evento cargados por literal dentro de la función
        found = [s for _, _, s in log_strings_in_func("A6000", 0x4385FFF0, 0x43860600)]
        self.assertIn("EV CamStrbChargeOn", found)
        self.assertIn("EV CamStrbChargeOff", found)


class AbsentStrings(unittest.TestCase):
    """Cadenas que NO deben existir en av-cam.bin A6000 (gestión detallada de batería NP-FW50)."""

    def test_absent_battery_pack_strings(self):
        d = data("A6000")
        joined = "\n".join(s for _, s in strings_in("A6000", 0x43C80000, 0x43CD0000))
        for absent in ("NP-FW", "NPFW", "FW50", "USB power", "AutoPowerOff", "PowerProfile",
                       "PowerMgr", "Energy", "Drain", "libbackup"):
            self.assertNotIn(absent, joined, absent)


class A7SComparison(unittest.TestCase):
    """A7S fw3.20 comparativa: misma carga de flash y BATT_*_Snd; falta BatteryInfo y ACV_BATT_Snd."""

    def test_a7s_has_upm_battery_level(self):
        """En la A7S la cadena NO lleva el prefijo '[CAMERA_MAIN_SYNC]: ' (la A6000 si)."""
        self.assertEqual(cstr("A7S", 0x43CA8A94), "Set UPM Battery Level [state] %d [Error] %d")
        self.assertEqual(cstr("A6000", 0x43CA2DFD),
                         "[CAMERA_MAIN_SYNC]: Set UPM Battery Level [state] %d [Error] %d")

    def test_a7s_has_batt_snd_strings(self):
        for addr in (0x43C983F6, 0x43C98403, 0x43C98411, 0x43C98421, 0x43C98431,
                     0x43C98441, 0x43C98450):
            self.assertIsNotNone(cstr("A7S", addr))

    def test_a7s_has_flash_charge_variables(self):
        """A7S tiene las mismas variables de carga (otra base)."""
        for addr, text in ((0x43CC7663, "uc_ChargeCommand"), (0x43CC7690, "uc_ChargeStatus"),
                           (0x43CC76DA, "uc_ChargeEnable"), (0x43CC770D, "uc_ChargeForceOff"),
                           (0x43CC77EA, "uc_ChargeRequest"), (0x43CC77FB, "uc_ChargeStopRequest"),
                           (0x43CC7A17, "b_SBChargeReq")):
            self.assertEqual(cstr("A7S", addr), text, hex(addr))

    def test_a7s_lacks_batteryinfo_but_keeps_acv(self):
        """CORRECCION (21-10-2026): la A7S NO tiene 'BatteryInfo' ni los 'Battery Info' de las
        luces, pero SI tiene 'ACV_BATT_Snd' (0x43c983f6) y 'ACV Error Voltage' (0x43c982d3)."""
        joined = "\n".join(s for _, s in strings_in("A7S", 0x43C80000, 0x43CD0000))
        self.assertNotIn("BatteryInfo", joined)
        self.assertNotIn("[IRLight] Battery Info", joined)
        self.assertNotIn("[VideoLight] Battery Info", joined)
        self.assertIn("ACV_BATT_Snd", joined)
        self.assertIn("ACV Error Voltage", joined)

    def test_a6000_adds_batteryinfo_to_the_shared_acv_block(self):
        """La A6000 anade 'BatteryInfo' y los 'Battery Info' de IRLight/VideoLight; el bloque ACV
        (ACV_BATT_Snd / ACV Error Voltage) es comun a las dos (correccion: no es exclusive)."""
        a6000 = "\n".join(s for _, s in strings_in("A6000", 0x43C80000, 0x43CD0000))
        a7s = "\n".join(s for _, s in strings_in("A7S", 0x43C80000, 0x43CD0000))
        self.assertIn("BatteryInfo", a6000)
        self.assertIn("ACV_BATT_Snd", a6000)
        self.assertIn("ACV Error Voltage", a6000)
        self.assertNotIn("BatteryInfo", a7s)
        self.assertIn("ACV_BATT_Snd", a7s)
        self.assertIn("ACV Error Voltage", a7s)


if __name__ == "__main__":
    unittest.main()
