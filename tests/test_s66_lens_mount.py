"""S66: subsistema de montura de lente (MOUNT) en av-cam.bin A6000 — verificaciones contra bytes.

Alcance: línea de ingeniería inversa GENERAL de la cámara (montura E-mount), sin relación con la
línea SilentShutter/obturador electrónico. Nada se ejecuta del firmware: solo lectura de bytes.

Hechos verificados aquí:
- Ubicación y orden de los logs del subsistema MOUNT (`[MOUNT_DEBUG]`/`[MOUNT_ERROR]`, `[B->L]`, `[L->B]`).
- Inventario de mensajes cuerpo->lente y lente->cuerpo con la función que los emite/recibe.
- Decodificación del tipo de lente (campo & 3 -> 4.8 V / no registrado / desconocido) y sus códigos.
- Handshake de hardware [HS] (CS_HIGH -> DATA_HIGH -> CS_LOW) sobre primitivas GPIO.
- Secuencia de la tarea principal de montura (0x436e5e3c).
- Diferencias A6000 (fw3.21) vs A7S (fw3.20) en el mismo subsistema.

Informes: docs/capture/s66-lens-mount.md · analysis/s66/lens_power_attach.md
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

MD = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
MD.detail = False
MD.skipdata = True

STR_RE = re.compile(rb"[\x20-\x7e]{4,}")
LIT_RE = re.compile(r"^(r\d+), \[pc, #(0x[0-9a-f]+|\d+)\]$")


def u32(model, a):
    import struct

    return struct.unpack_from("<I", data(model)[a - B:a - B + 4])[0]


def cstr(model, addr):
    """Cadena C terminada en NUL. Se recorta el '\n' final que，很多 logs incluyen."""
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


class MountInventory(unittest.TestCase):
    def test_sha(self):
        self.assertEqual(hashlib.sha256(data("A6000")).hexdigest(), SHA_A6000)

    def test_mount_region_has_expected_inventory(self):
        """646 cadenas en la región MOUNT (0x43c95600-0x43c9ab00) — regresión del inventario."""
        st = strings_in("A6000", 0x43C95600, 0x43C9AB00)
        self.assertEqual(len(st), 646)
        prefixes = ("[MOUNT_", "[B->L]", "[L->B]", "[BL]", "[ADF]")
        self.assertGreater(sum(1 for _, s in st if s.startswith(prefixes)), 150)

    def test_key_log_strings_and_addresses(self):
        """Direcciones exactas de los logs clave (VERIFICADO contra bytes)."""
        expected = {
            0x43C95659: "[MOUNT_ERROR]: [MCS]addCmdDataList data times overflow",
            0x43C9648D: "[MOUNT_DEBUG]: [BL]SYNC SEND SET ID(%d):CB(0x%8x)",
            0x43C96679: "[MOUNT_DEBUG]: [BL]ASYNC SEND ID(%d):CB(0x%8x)",
            0x43C96B93: "[MOUNT_ERROR]: [BL]state:%02Xh, code:%02Xh",
            0x43C96EA2: "[MOUNT_DEBUG]: [B->L]ALPHALENS:%d,%d",
            0x43C97CFF: "[MOUNT_DEBUG]: [BL]LENS_POWER_4.8V",
            0x43C97D22: "[MOUNT_DEBUG]: [BL]LENS_POWER_UNREG",
            0x43C97D46: "[MOUNT_ERROR]: [BL]LENS_TYPE_UNKNOWN",
            0x43C98540: "[MOUNT_DEBUG]: [BL]UART_HZ 750:%d 1500%d",
            0x43C98521: "[MOUNT_DEBUG]: LENS_WEAR_START",
            0x43C987D4: "[MOUNT_DEBUG]: DETACH_START",
            0x43C98660: "[MOUNT_DEBUG]: WAKE_UP_START",
            0x43C98698: "[MOUNT_DEBUG]: POWEROFF_START",
            0x43C9A862: "[LENS_PDR]: BonoboDSP_Rcv: paritycheck_error!",
            0x43C9A09F: "[MOUNT_ERROR]: [BL]FirmUp Error : CAIF CASND LUPDT_INFO",
            0x43C9A0D7: "[MOUNT_ERROR]: [BL]FirmUp Error : CAIF CASND LUPDT_DATA",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr("A6000", addr), text, hex(addr))

    def test_source_file_names_in_logs(self):
        """Los logs revelan los ficheros fuente internos del subsistema."""
        all_str = " ".join(s for _, s in strings_in("A6000", 0x43C95600, 0x43C9AB00))
        self.assertIn("Mount_Controller.cpp", all_str)
        self.assertIn("Mount_DividedInfo.cpp", all_str)

    def test_log_strings_end_with_newline(self):
        """Los formatos de log terminan en '\\n' (detalle de formato del blob)."""
        d = data("A6000")
        off = 0x43C95659 - B
        self.assertTrue(
            d[off:off + 64].startswith(b"[MOUNT_ERROR]: [MCS]addCmdDataList data times overflow\n"))


class CommandDirection(unittest.TestCase):
    """Inventario de mensajes cuerpo->lente y lente->cuerpo."""

    def test_body_to_lens_commands(self):
        """[B->L]: CS_POWER, ATTACH_INFO1/3/4, CS_RESET, TEST_CMD, UPDATE_DATA."""
        expected = {
            0x436E4412: "[MOUNT_DEBUG]: [B->L]CS_POWER",
            0x436E445C: "[MOUNT_DEBUG]: [B->L]ATTACH_INFO1",
            0x436E449E: "[MOUNT_DEBUG]: [B->L]ATTACH_INFO3",
            0x436E44DA: "[MOUNT_DEBUG]: [B->L]ATTACH_INFO4",
            0x436E4572: "[MOUNT_DEBUG]: [B->L]TEST_CMD:%d",
            0x436E4708: "[MOUNT_DEBUG]: [B->L]CS_RESET",
        }
        for instr, text in expected.items():
            found = log_strings_in_func("A6000", instr - 24, instr + 8)
            self.assertIn(text, [s for _, _, s in found], hex(instr))

    def test_lens_to_body_commands(self):
        """[L->B]: CS_POWER, SYSTEM_HZ, CS_RESET(+ERROR), CS_SLEEP, CS_CHECK_CMD, ATTACH_INFO1..4,
        STARTUP_INFO, CS_CREDIT, ALPHA_LENS_INFO."""
        texts = []
        for start, end in ((0x436E4B66, 0x436E4F98), (0x436E4F98, 0x436E540C), (0x436E5C6C, 0x436E5E3C)):
            texts += [s for _, _, s in log_strings_in_func("A6000", start, end)]
        for expected in (
            "[MOUNT_DEBUG]: [L->B]CS_POWER",
            "[MOUNT_DEBUG]: [L->B]SYSTEM_HZ",
            "[MOUNT_DEBUG]: [L->B]CS_RESET",
            "[MOUNT_DEBUG]: [L->B]CS_RESET_ERROR",
            "[MOUNT_DEBUG]: [L->B]CS_SLEEP",
            "[MOUNT_DEBUG]: [L->B]CS_CHECK_CMD",
            "[MOUNT_DEBUG]: [L->B]ATTACH_INFO1",
            "[MOUNT_DEBUG]: [L->B]STARTUP_INFO",
            "[MOUNT_DEBUG]: [L->B]CS_CREDIT",
            "[MOUNT_DEBUG]: [B->L]ALPHA_LENS_INFO:%d",
        ):
            self.assertIn(expected, texts, expected)


class LensTypeDecode(unittest.TestCase):
    """Decodificación del tipo de lente en 0x436e4eb4."""

    def test_power_mode_mask_and_branches(self):
        found = log_strings_in_func("A6000", 0x436E4EB4, 0x436E4F98)
        texts = [s for _, _, s in found]
        self.assertIn("[MOUNT_DEBUG]: [BL]LENS_POWER_4.8V", texts)
        self.assertIn("[MOUNT_DEBUG]: [BL]LENS_POWER_UNREG", texts)
        self.assertIn("[MOUNT_ERROR]: [BL]LENS_TYPE_UNKNOWN", texts)

    def test_instructions_mask_and_error_codes(self):
        d = data("A6000")
        ins = list(MD.disasm(d[0x436E4EB4 - B:0x436E4F98 - B], 0x436E4EB4))
        ops = [(i.address, i.mnemonic, i.op_str) for i in ins if i.mnemonic != ".byte"]
        # `ldrb r6, [r3, #0x22]` + `and r6, r6, #3`  -> campo de modo de alimentacion
        self.assertIn((0x436E4EC0, "ldrb.w", "r6, [r3, #0x22]"), ops)
        self.assertIn((0x436E4EC6, "and", "r6, r6, #3"), ops)
        self.assertIn((0x436E4ECA, "cmp", "r6, #1"), ops)
        self.assertIn((0x436E4F04, "cmp", "r6, #2"), ops)
        # codigos de error: 0xff (tipo desconocido) y 0x0a (lente registrada)
        self.assertIn((0x436E4F5A, "movs", "r3, #0xff"), ops)
        self.assertIn((0x436E4F5E, "str", "r3, [r5, #8]"), ops)
        self.assertIn((0x436E4F6C, "movs", "r3, #0xa"), ops)
        self.assertIn((0x436E4F6E, "str", "r3, [r5, #8]"), ops)

    def test_4v8_log_references_4v8_and_unreg(self):
        """El log de 4.8 V lleva además el valor 0x1000 (4096 mV) en el argumento."""
        d = data("A6000")
        ins = list(MD.disasm(d[0x436E4ED0 - B:0x436E4F00 - B], 0x436E4ED0))
        ops = [(i.mnemonic, i.op_str) for i in ins if i.mnemonic != ".byte"]
        self.assertIn(("mov.w", "r1, #0x1000"), ops)


class HardwareHandshake(unittest.TestCase):
    """Handshake [HS] con líneas CS/DATA: 0x436e4d68."""

    def test_hs_state_machine_and_strings(self):
        # 0x436e48fc: CS_HIGH / DATA_HIGH / CS_LOW (espera de la línea DATA)
        found = log_strings_in_func("A6000", 0x436E48FC, 0x436E4A94)
        texts = [s for _, _, s in found]
        self.assertIn("[MOUNT_DEBUG]: [BL][HS]CS_HIGH", texts)
        self.assertIn("[MOUNT_DEBUG]: [BL][HS]DATA_HIGH", texts)
        self.assertIn("[MOUNT_DEBUG]: [BL][HS]CS_LOW", texts)
        # 0x436e4d68: CS_HIGH / CS_LOW / COMPLETE + timeout de la secuencia de power
        found = log_strings_in_func("A6000", 0x436E4D68, 0x436E4E80)
        texts = [s for _, _, s in found]
        self.assertIn("[MOUNT_DEBUG]: [BL][HS]CS_HIGH", texts)
        self.assertIn("[MOUNT_DEBUG]: [BL][HS]CS_LOW", texts)
        self.assertIn("[MOUNT_DEBUG]: [BL][HS]COMPLETE", texts)
        self.assertIn("[MOUNT_ERROR]: [BL][HS]POWER SEQ TIME OUT", texts)

    def test_hs_uses_gpio_primitives(self):
        d = data("A6000")
        ins = list(MD.disasm(d[0x436E4D68 - B:0x436E4E80 - B], 0x436E4D68))
        calls = [int(i.op_str[1:], 16) for i in ins
                 if i.mnemonic == "bl" and i.op_str.startswith("#")]
        self.assertIn(0x43ADA128, calls)   # CS (set)
        self.assertIn(0x43ADA134, calls)   # DATA (get)
        # el getter acaba en la primitiva gpio_get documentada en S55
        ins2 = list(MD.disasm(d[0x43A1C768 - B:0x43A1C778 - B], 0x43A1C768))
        self.assertTrue(any(i.mnemonic.startswith("b.w") and int(i.op_str[1:], 16) == 0x43B5E2BC
                            for i in ins2))
    def test_hs_states_are_zero_one_three(self):
        d = data("A6000")
        ins = list(MD.disasm(d[0x436E4D68 - B:0x436E4E80 - B], 0x436E4D68))
        ops = [(i.address, i.mnemonic, i.op_str) for i in ins if i.mnemonic != ".byte"]
        self.assertIn((0x436E4D74, "cmp", "r4, #1"), ops)
        self.assertIn((0x436E4D78, "cmp", "r4, #3"), ops)
        self.assertIn((0x436E4D7C, "cmp", "r4, #0"), ops)


class MainMountTask(unittest.TestCase):
    """Tarea principal de montura 0x436e5e3c: secuencia de logs."""

    def test_ordered_log_sequence(self):
        found = log_strings_in_func("A6000", 0x436E5E3C, 0x436E7BF0)
        texts = [s for _, _, s in found]
        self.assertGreaterEqual(len(texts), 60)
        order = [
            "[MOUNT_DEBUG]: LENS_WEAR_START",
            "[MOUNT_DEBUG]: [BL]UART_HZ 750:%d 1500%d",
            "[MOUNT_DEBUG]: [L->B]ATTACH_INFO2",
            "[MOUNT_DEBUG]: LENS_WEAR_END",
            "[MOUNT_DEBUG]: WAKE_UP_START",
            "[MOUNT_DEBUG]: WAKE_UP_END",
            "[MOUNT_DEBUG]: POWEROFF_START",
            "[MOUNT_DEBUG]: POWEROFF_END",
            "[MOUNT_DEBUG]: DETACH_COMP",
            "[MOUNT_DEBUG]: DETACH_START",
            "[MOUNT_DEBUG]: [BL]LOGIC_OFF",
            "[MOUNT_DEBUG]: [BL]LOGIC_ON",
            "[MOUNT_DEBUG]: [B->L]UPDATE_ON",
            "[MOUNT_DEBUG]: [L->B]ALPHA_LENS_INFO:%d",
            "[MOUNT_DEBUG]: [BL]STANDBY",
            "[MOUNT_DEBUG]: PB->WAKEUP->OFF",
        ]
        idx = []
        for o in order:
            self.assertIn(o, texts, o)
            idx.append(texts.index(o))
        self.assertEqual(idx, sorted(idx), "el orden de los logs difiere del esperado")

    def test_function_uses_known_helpers(self):
        d = data("A6000")
        ins = list(MD.disasm(d[0x436E5E3C - B:0x436E7BF0 - B], 0x436E5E3C))
        calls = {int(i.op_str[1:], 16) for i in ins
                 if i.mnemonic == "bl" and i.op_str.startswith("#")}
        # constructores de mensaje: 0x436e41e4 (log+send), 0x436e1254 (SYNC SEND),
        # 0x436e239c (volcado de estado), 0x436e4360 (bloque de envio CS_POWER)
        for helper in (0x436E41E4, 0x436E1254, 0x436E239C, 0x436E4360):
            self.assertIn(helper, calls, hex(helper))


class LensShading(unittest.TestCase):
    """SHD: correccion de sombreado dependiente de la lente."""

    def test_shd_mode_table_from_tbb(self):
        """GetShdMode (0x438ef40e): tabla tbb de 69 drive_mode -> 14 ShdMode distintos."""
        d = data("A6000")
        base = 0x438EF418
        table = d[base - B:base - B + 69]
        self.assertEqual(len(table), 69)
        values = {}
        for mode in range(69):
            tgt = base + 2 * table[mode]
            ins = [i for i in MD.disasm(d[tgt - B:tgt - B + 8], tgt) if i.mnemonic != ".byte"]
            val = None
            for i in ins:
                m = re.match(r"^r0, #(0x[0-9a-f]+|\d+)$", i.op_str)
                if i.mnemonic in ("movs", "mov") and m:
                    val = int(m.group(1), 0)
                    break
            self.assertIsNotNone(val, hex(tgt))
            values[mode] = val
        self.assertEqual(sorted(set(values.values())),
                         [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0xA, 0xB, 0xC, 0xD, 0xF])
        self.assertEqual(values[0], 0x00)
        self.assertEqual(values[2], 0x07)
        self.assertEqual(values[3], 0x03)
        self.assertEqual(values[16], 0x0F)
        self.assertEqual(values[63], 0x0A)

    def test_per_lens_shading_field_names(self):
        """11 valores + 32 ganancias + minimo/efecto por lente (nombres en el blob)."""
        self.assertEqual(cstr("A6000", 0x43CBE9CB), "ss_LensMountShdValue[0]")
        self.assertEqual(cstr("A6000", 0x43CBEABB), "ss_LensMountShdValue[10]")
        self.assertEqual(cstr("A6000", 0x43CBEAD4), "us_LensMountShdGain[0]")
        self.assertEqual(cstr("A6000", 0x43CBEDB2), "us_LensMountShdGain[31]")
        self.assertEqual(cstr("A6000", 0x43CBEE03), "us_ShdGainMin")
        self.assertEqual(cstr("A6000", 0x43CBEE11), "us_LensMountShdEffect")
        self.assertEqual(cstr("A6000", 0x43CBE73B), "uc_SyncLensShdOn")

    def test_shd_functions_and_logs(self):
        found = log_strings_in_func("A6000", 0x438EF40E, 0x438EF4C0)
        self.assertIn("SHD::GetShdMode: unknown drive_mode = 0x%x", [s for _, _, s in found])
        self.assertEqual(cstr("A6000", 0x43CCCE0C),
                         "[CAMERA_MAIN_YC]: SHD::job_LensMountSHD_GainCalc: ShdMode = 0x%x")
        self.assertEqual(cstr("A6000", 0x43CCCF6B),
                         "[CAMERA_MAIN_YC]: SHD:IsTrackBonoboOn: LensShdMode = 0x%x")

    def test_shd_logs_identical_between_models(self):
        """A6000 (fw3.21) y A7S (fw3.20) tienen el MISMO bloque SHD: 217 logs cada uno,
        identicos salvo el prefijo '[CAMERA_MAIN_YC]: ' que solo usa A6000."""
        def shd_set(model):
            out = set()
            for _, s in strings_in(model, 0x43C90000, 0x43D00000):
                if s.startswith("[CAMERA_MAIN_YC]: SHD::"):
                    out.add(s[len("[CAMERA_MAIN_YC]: "):])
                elif s.startswith("SHD::"):
                    out.add(s)
            return out

        a, b = shd_set("A6000"), shd_set("A7S")
        self.assertEqual(len(a), 217)
        self.assertEqual(len(b), 217)
        self.assertEqual(a, b)
        # A6000 usa el prefijo; A7S no
        a6000_pref = sum(1 for _, s in strings_in("A6000", 0x43C90000, 0x43D00000)
                         if s.startswith("[CAMERA_MAIN_YC]: SHD::"))
        a7s_pref = sum(1 for _, s in strings_in("A7S", 0x43C90000, 0x43D00000)
                        if s.startswith("[CAMERA_MAIN_YC]: SHD::"))
        self.assertEqual(a6000_pref, 217)
        self.assertEqual(a7s_pref, 0)


class LensClassAndJobs(unittest.TestCase):
    """Clase Camera::Lens, cargador ODL y barrera de lente."""

    def test_odl_load_uses_async_messages(self):
        """ODL::Load no abre ficheros: usa AsyncSend/AsyncRecieve (0x43721bf6 / 0x43721c20)."""
        d = data("A6000")
        ins = list(MD.disasm(d[0x43721B9C - B:0x43721C80 - B], 0x43721B9C))
        calls = {int(i.op_str[1:], 16) for i in ins
                 if i.mnemonic == "bl" and i.op_str.startswith("#")}
        self.assertIn(0x43AE07C0, calls)   # AsyncSend
        self.assertIn(0x43AE07CE, calls)   # AsyncRecieve
        texts = [s for _, _, s in log_strings_in_func("A6000", 0x43721B9C, 0x43721C80)]
        self.assertIn("[LENS_YC]: %s: AsyncSend error (0x%x)", texts)
        self.assertIn("[LENS_YC]: %s: AsyncRecieve error (0x%x)", texts)

    def test_camera_lens_class_names(self):
        """Los nombres de las funciones de Camera::Lens estan en el blob (traza)."""
        joined = "\n".join(s for _, s in strings_in("A6000", 0x43C99000, 0x43C9C000))
        for name in ("void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)",
                     "Camera::Lens::job_Mount_LoadAberrationDataHndl()",
                     "Camera::Lens::job_Mount_SaveAberrationDataHndl(__uint16_t)",
                     "Camera::Lens::job_Mount_CloseAberrationDataHndl()",
                     "Camera::Lens::SetAberrationDataInfo(__uint16_t)",
                     "Camera::Lens::ODL::ODL_ERR Camera::Lens::ODL::Load(Camera::Lens::ODL::LOAD_ARG*)"):
            self.assertIn(name, joined, name)

    def test_lens_barrier_log(self):
        self.assertEqual(cstr("A6000", 0x43CA7E4A), "[LensBarrier] KikiLog Move")
        found = log_strings_in_func("A6000", 0x437CF490, 0x437CF620)
        self.assertIn("[LensBarrier] KikiLog Move", [s for _, _, s in found])


class WireFrame(unittest.TestCase):
    """Trama en el cable (constructor 0x43b7b276, sub-tarea A)."""

    def _ops(self, start, end):
        d = data("A6000")
        return [(i.address, i.mnemonic, i.op_str) for i in MD.disasm(d[start - B:end - B], start)
                if i.mnemonic != ".byte"]

    def test_header_footer_and_length(self):
        ops = self._ops(0x43B7B276, 0x43B7B2E0)
        self.assertIn((0x43B7B29C, "movs", "r3, #0xf0"), ops)
        self.assertIn((0x43B7B2A2, "strb", "r3, [r0]"), ops)          # cabecera 0xF0 en +0
        self.assertIn((0x43B7B286, "add.w", "r8, r8, #8"), ops)        # longitud = size + 8
        self.assertIn((0x43B7B2A6, "strb.w", "r8, [r0, #1]"), ops)      # longitud LE en +1
        self.assertIn((0x43B7B2B2, "strb.w", "r8, [r0, #2]"), ops)
        self.assertIn((0x43B7B2B8, "strb.w", "sb, [r0, #4]"), ops)      # parametro del emisor en +4
        self.assertIn((0x43B7B2BC, "bfi", "r3, r2, #0, #3"), ops)      # tipo de comunicacion = tipo & 7
        self.assertIn((0x43B7B2CE, "movs", "r3, #0x55"), ops)
        self.assertIn((0x43B7B2D0, "strb", "r3, [r5, #2]"), ops)       # footer 0x55

    def test_checksum_is_sum_over_payload(self):
        ops = self._ops(0x43B7B276, 0x43B7B2E0)
        self.assertIn((0x43B7B2C4, "adds", "r0, #1"), ops)             # checksum sobre buf+1
        self.assertIn((0x43B7B2C6, "adds", "r1, #4"), ops)             # longitud = size + 4
        self.assertIn((0x43B7B2CA, "bl", "#0x43b7b25e"), ops)
        # la funcion de checksum suma bytes y trunca a 16 bits
        ops2 = self._ops(0x43B7B25E, 0x43B7B276)
        self.assertTrue(any(m == "adds" and o.startswith("r0, r") for _, m, o in ops2), ops2)
        self.assertTrue(any(m == "uxth" for _, m, _ in ops2), ops2)


class LensFiles(unittest.TestCase):
    """Ficheros de datos por lente: /lens/VX91xx_lensfile.bin y su tabla en av-cam.bin."""

    LENS_DIR = ("firmware/extracted/fw321/firmware.tar_unpacked/0800_appli/lens")

    def _lensfile(self, name):
        return (ROOT / self.LENS_DIR / name).read_bytes()

    def test_lf_header_layout(self):
        """Cabecera LF: magic, hdr_len=0x10, size-0x10, lens_id; secciones ED/CS/LC."""
        import struct
        for name, lens_id in (("VX9101_lensfile.bin", 0x9101), ("VX9129_lensfile.bin", 0x9129)):
            b = self._lensfile(name)
            self.assertEqual(b[0:2], b"LF")
            self.assertEqual(struct.unpack_from("<H", b, 2)[0], 0x10)
            self.assertEqual(struct.unpack_from("<I", b, 4)[0], len(b) - 0x10)
            self.assertEqual(struct.unpack_from("<H", b, 12)[0], lens_id)
            # secciones ED / CS / LC
            self.assertEqual(b[16:18], b"ED")
            self.assertEqual(struct.unpack_from("<H", b, 18)[0], 8)
            # la ultima seccion es LC con 12 B de payload
            off = 16
            magics = []
            while off + 8 <= len(b) - 4:
                magic = b[off:off + 2]
                if magic not in (b"ED", b"CS", b"LC"):
                    break
                magics.append(magic)
                hdr = struct.unpack_from("<H", b, off + 2)[0]
                plen = struct.unpack_from("<I", b, off + 4)[0]
                if magic == b"LC":
                    self.assertEqual(plen, 12)
                off += hdr + plen
            self.assertEqual(magics, [b"ED", b"CS", b"LC"])

    def test_a6000_and_a6300_lens_files_are_identical(self):
        """Los 18 ficheros de A6000 y A6300 son byte a byte iguales."""
        import hashlib
        a6300 = (ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0800_appli/lens")
        names = sorted(p.name for p in (ROOT / self.LENS_DIR).glob("VX*_lensfile.bin"))
        self.assertEqual(len(names), 18)
        for n in names:
            other = a6300 / n
            self.assertTrue(other.exists(), n)
            self.assertEqual(hashlib.sha256((ROOT / self.LENS_DIR / n).read_bytes()).hexdigest(),
                             hashlib.sha256(other.read_bytes()).hexdigest(), n)

    def test_name_table_layout_in_avcam(self):
        """Tabla de nombres: base 0x43C22BF2, 18 slots x 0x42, [u16 key][ruta]."""
        import struct
        d = data("A6000")
        base = 0x43C22BF2
        names = []
        for i in range(18):
            slot = base + i * 0x42
            off = slot - B
            key = struct.unpack_from("<H", d, off)[0]
            raw = d[off + 2:off + 0x42]
            path = raw.split(b"\x00")[0].decode("ascii")
            names.append((key, path))
        self.assertEqual(names[0][1], "/lens/VX9101_lensfile.bin")
        self.assertEqual(names[-1][1], "/lens/VX9129_lensfile.bin")
        self.assertEqual(len(names), 18)
        keys = [k for k, _ in names]
        self.assertEqual(keys, sorted(keys))
        self.assertEqual(keys[0], 0x8011)

    def test_a7s_has_no_lens_files(self):
        """La A7S 3.20 no tiene el subsistema de ficheros de lente."""
        joined = "\n".join(s for _, s in strings_in("A7S", 0x43C90000, 0x43D00000))
        self.assertNotIn("/lens/", joined)
        self.assertNotIn("lensfile", joined)
        self.assertNotIn("VX9", joined)


class A7SComparison(unittest.TestCase):
    """A7S (fw3.20) tiene el mismo subsistema pero con un esquema de logs más pobre."""

    def test_a7s_has_mount_sources_and_bonobo(self):
        texts = [s for _, s in strings_in("A7S", 0x43C90000, 0x43D00000)]
        joined = "\n".join(texts)
        self.assertIn("Mount_Controller.cpp", joined)
        self.assertIn("Mount_DividedInfo.cpp", joined)
        self.assertIn("BonoboDSP_Send: Data latch failed!", joined)
        self.assertIn("BonoboDSP_Rcv: paritycheck_error!", joined)

    def test_a7s_lacks_a6000_only_logs(self):
        joined = "\n".join(s for _, s in strings_in("A7S", 0x43C90000, 0x43D00000))
        for absent in ("[MOUNT_DEBUG]", "[MOUNT_ERROR]", "[B->L]", "LENS_WEAR_START",
                       "DETACH_START", "ALPHA_LENS_INFO", "LENS_POWER_4.8V",
                       "LENS_POWER_UNREG", "CS_CREDIT", "LENS_SLEEP MODE", "UART_HZ 750"):
            self.assertNotIn(absent, joined, absent)

    def test_a7s_keeps_core_messages(self):
        joined = "\n".join(s for _, s in strings_in("A7S", 0x43C90000, 0x43D00000))
        for present in ("LENS_TYPE_UNKNOWN", "LENS FIRMERR", "UART_HZ NG", "LensPowerState",
                        "[L->B]", "PREPARE UPDATE"):
            self.assertIn(present, joined, present)


if __name__ == "__main__":
    unittest.main()
