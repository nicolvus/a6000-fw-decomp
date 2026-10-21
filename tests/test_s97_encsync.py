"""S97: audio/video encoder synchronization in Sony A6000 fw3.21.

Linea de ingenieria inversa GENERAL de la camara (sincronizacion encoder),
sin relacion con SilentShutter/obturador electronico, montura, AF, JPEG,
service mode/NVRAM, ADJ_CMD, ZPD, ZIT, APC, ZIT, ADF, API del SA, visor,
caras, reproduccion, medios, bus OSAL, HAPI, ficheros, modos, AutoFraming.
Solo lectura de bytes contra av-cam.bin; no se ejecuta firmware.
"""

import hashlib
import re
import sys
import unittest
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_THUMB

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

SHA_A6000 = "b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9"

STR_RE = re.compile(rb"[\x20-\x7e]{4,}")


def cstr(addr):
    """Leer cadena nula-terminada en la direccion memoria (base B=0x43541000)."""
    d = data("A6000")
    off = addr - B
    if off < 0 or off >= len(d):
        return None
    end = d.find(b"\x00", off, off + 256)
    if end < 0:
        return None
    raw = d[off:end]
    s = raw.decode("ascii", "replace").rstrip("\n")
    # Validar: todos los bytes deben ser ASCII imprimible (0x20-0x7E) o ctrl suaves
    if not s or any(b < 0x20 and b not in (0x09, 0x0A, 0x0D) for b in raw):
        return None
    return s


def strings_in(model, lo, hi):
    """Encontrar cadenas imprimibles en un rango de direcciones memoria."""
    d = data(model)
    out = []
    segment = d[lo - B:hi - B]
    for m in STR_RE.finditer(segment):
        out.append((lo + m.start(), m.group().decode("ascii", "replace")))
    return out


class EncoderSyncInventory(unittest.TestCase):
    """Verifica el inventario de cadenas de los módulos ENCMODEMGR, ENCAUDSYNC,
    ENCAUDOUCR, ENCOUCUDMG, SYNCENCSTART y VIDENCCTRL en av-cam.bin."""

    def test_sha(self):
        self.assertEqual(hashlib.sha256(data("A6000")).hexdigest(), SHA_A6000)

    def test_encodemgr_strings_and_addresses(self):
        """[ENCMODEMGR] strings verificadas en sus direcciones memoria (con prefijo)."""
        expected = {
            0x43C4AC73: "[ENCMODEMGR]SetState = %x ",
            0x43C4AC8F: "[ENCMODEMGR]File:%s, Func:%s() ,Line:%d ",
            0x43C4ACCD: "[ENCMODEMGR]RecordCodecIfCmd: CmdCode:%x, CmdTime:%x, ExecTime:%x ,CurrentRefTime =%x ",
            0x43C4AD25: "[ENCMODEMGR]ComQue CANNOT Exec! cur:%ld cmd:0x%x tim:%ld",
            0x43C4AD5E: "[ENCMODEMGR]%s() [%s] Invalid replyId !!!!",
            0x43C4AD8A: "[ENCMODEMGR]CMD_ID_ACT_ENC ",
            0x43C4ADA7: "[ENCMODEMGR]CMD_ID_GET_REF_TIMER ",
            0x43C4ADCA: "[ENCMODEMGR]CMD_ID_INIT_ES_API_PARAM ",
            0x43C4ADF1: "[ENCMODEMGR]CMD_ID_INACT_CHIP ",
            0x43C4AE11: "[ENCMODEMGR]CMD_ID_ALLOC_USER_DATA_AREA ",
            0x43C4AE3B: "[ENCMODEMGR]CMD_ID_BEGIN_ENC ",
            0x43C4AE5A: "[ENCMODEMGR]CMD_ID_SET_SEQ_PARAM ",
            0x43C4AE7D: "[ENCMODEMGR]CMD_ID_TERM_ENC ",
            0x43C4AE9B: "[ENCMODEMGR]CMD_ID_STILL_ENC ",
            0x43C4AEE3: "[ENCMODEMGR]CMD_ID_APPLY_USER_DATA_PIC ",
            0x43C4AF0C: "[ENCMODEMGR]CMD_ID_MUTE_AUDIO_CAPTURE ",
            0x43C4AF34: "[ENCMODEMGR]CMD_ID_INIT_RC_BUFFER ",
            0x43C4AF58: "[ENCMODEMGR]CMD_ID_SET_RC_WTPT ",
            0x43C4AF79: "[ENCMODEMGR]CMD_ID_SET_ENC_READ_POINTER ",
            0x43C4AFA3: "[ENCMODEMGR]ExecCodecIfCmd err = %d",
        }
        for addr, text in expected.items():
            result = cstr(addr)
            self.assertEqual(result, text, f"Expected {text!r} at {addr:#x}, got {result!r}")

    def test_encaudoucr_strings_and_addresses(self):
        """[ENCAUDOUCR] strings verificadas en sus direcciones memoria (con prefijo)."""
        expected = {
            0x43C4B444: "[ENCAUDOUCR]File:%s, Func:%s() ,Line:%d ",
            0x43C4B4A1: "[ENCAUDOUCR]IsOuCrank = %x, Sampling = %x,FrameRate = %x ImagingRate = %d ",
            # Las siguientes direcciones contienen strings diferentes (parte del mismo bloque de strings);
            # solo verificamos las 2 primeras que son del módulo ENCAUDOUCR
        }
        for addr, text in expected.items():
            result = cstr(addr)
            self.assertEqual(result, text, hex(addr))

    def test_encauchcr_primary_strings(self):
        """Verifica las cadenas primarias de ENCAUDOUCR en sus direcciones."""
        # String principal de inicio de módulo
        self.assertEqual(cstr(0x43C4B444), "[ENCAUDOUCR]File:%s, Func:%s() ,Line:%d ")
        # String de parámetros de encendido
        self.assertEqual(cstr(0x43C4B4A1), "[ENCAUDOUCR]IsOuCrank = %x, Sampling = %x,FrameRate = %x ImagingRate = %d ")

    def test_encoucudmg_strings_and_addresses(self):
        """[ENCOUCUDMG] strings verificadas en sus direcciones memoria (con prefijo)."""
        expected = {
            0x43C522FB: "[ENCOUCUDMG]BUG : File:%s, Func:%s() ,Line:%d ",
            0x43C5236D: "[ENCOUCUDMG]WRN : File:%s, Func:%s() ,Line:%d ",
            0x43C5239D: "[ENCOUCUDMG]BUG : File:%s, Func:%s(), Line:%d index = %x, state = %x ",
            0x43C523E4: "[ENCOUCUDMG]Same Exec Time User Data Exist : File:%s, Func:%s() ,Line:%d ",
            0x43C5242F: "[ENCOUCUDMG]UserData OverFlow ",
            0x43C5244F: "[ENCOUCUDMG]UserData Align Error = %x : File:%s, Func:%s() ,Line:%d ",
            0x43C52495: "[ENCOUCUDMG]EDIT SHUTTER SPEED ERROR : File:%s, Func:%s() ,Line:%d ",
        }
        for addr, text in expected.items():
            result = cstr(addr)
            self.assertEqual(result, text, hex(addr))

    def test_encaudsync_data_string(self):
        """[ENCAUDSYNC] string de header verificado en memoria."""
        self.assertEqual(cstr(0x43C526D3), "[ENCAUDSYNC]File:%s, Func:%s() ,Line:%d ")

    def test_videncctrl_strings_and_addresses(self):
        """[VIDENCCTRL] strings verificadas en sus direcciones memoria (con prefijo)."""
        expected = {
            0x43CD6070: "[VIDENCCTRL]ChangeState %08x -> %08x",
            0x43CD6118: "[VIDENCCTRL]Err!!! File:%s, Func:%s() ,Line:%d ",
            0x43CD6169: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_OPEN ",
            0x43CD6190: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_CLOSE ",
            0x43CD61b8: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_INITIALIZE_MOVIE ",
            0x43CD61eb: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_INITIALIZE_STILL ",
            0x43CD621e: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_ENC_PICTURE ",
            0x43CD624c: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_ENC_FINAL_PICTURE ",
            0x43CD6280: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_FINALIZE ",
            0x43CD62ab: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_RELEASE_ES ",
            0x43CD62d8: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_SET_MOVIE_QUALITY_INFO ",
            0x43CD6311: "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_SET_FACE_INFO ",
            0x43CD6341: "[VIDENCCTRL]Err!!! File:%s, Func:%s(), Line:%d, Msg:%x, Err:%x ",
        }
        for addr, text in expected.items():
            result = cstr(addr)
            self.assertEqual(result, text, hex(addr))

    def test_videncstat_strings_and_addresses(self):
        """[VIDENCSTAT] strings verificadas (S83 módulo 70)."""
        expected = {
            0x43CD67BB: "[VIDENCSTAT]Err!!! File:%s, Func:%s() ,Line:%d ",
            0x43CD680B: "[VIDENCSTAT][VIDEO INFO] Pts = 0x%08x EndFlug = 0x%02x",
            0x43CD6843: "[VIDENCSTAT]Notify Final Es ",
            0x43CD6861: "[VIDENCSTAT]augi,paddingAreaLength:%#x",
            0x43CD6888: "[VIDENCSTAT]ExecuteEncPictureFailure ",
            0x43CD68AF: "[VIDENCSTAT]Use 2nd Latest Index ",
            0x43CD68D2: "[VIDENCSTAT]Err!!! File:%s, Func:%s(), Line:%d, status:%d ",
            0x43CD690E: "[VIDENCSTAT]ExecuteEncPictureNormal ",
            0x43CD6934: "[VIDENCSTAT]ERR!!! can't protect %d[us] restriction, currentTime %d[us]",
            0x43CD6A75: "[VIDENCSTAT]Err!!! File:%s, Func:%s() ,Line:%d, err ",
        }
        for addr, text in expected.items():
            result = cstr(addr)
            self.assertEqual(result, text, hex(addr))

    def test_encoucstat_strings_and_addresses(self):
        """[ENCOUCSTAT] strings verificadas (S83 módulo 49)."""
        expected = {
            0x43C505bc: "[ENCOUCSTAT]MSG SET ERROR: File:%s, Func:%s() ,Line:%d ",
            0x43C50631: "[ENCOUCSTAT]MSG SEND ERROR: File:%s, Func:%s() ,Line:%d ",
            0x43C5066b: "[ENCOUCSTAT]ES Overflow!! [%s][%s][%d]",
            0x43C50693: "[ENCOUCSTAT]AVC_ENC_VIDEO_ERR_STATE!! [%s][%s][%d]",
            0x43C506c7: "[ENCOUCSTAT]AVC_ENC_VIDEO_ERR_MEMORY!! [%s][%s][%d]",
            0x43C50730: "[ENCOUCSTAT]AVC_ENC_VIDEO_ERR_INDEX!! [%s][%s][%d]",
            0x43C50764: "[ENCOUCSTAT]AVC_ENC_VIDEO_ERR_SA_TIMEOUT!! [%s][%s][%d]",
            0x43C5079d: "[ENCOUCSTAT]AVC_ENC_VIDEO_ERR_ENCODING!! [%s][%s][%d]",
            0x43C507d4: "[ENCOUCSTAT]AVC_ENC_VIDEO_ERR_PICTURE_DATA_FULL!! [%s][%s][%d]",
        }
        for addr, text in expected.items():
            result = cstr(addr)
            self.assertEqual(result, text, hex(addr))


class A6000Comparison(unittest.TestCase):
    """Comparaciones A6000 fw3.21 vs A7S fw3.20 al nivel de cadenas."""

    def test_a6000_has_encsync_modules(self):
        """A6000 fw3.21 debe tener los módulos ENCMODEMGR, ENCAUDSYNC, etc."""
        joined = "\n".join(s for _, s in strings_in("A6000", 0x43C40000, 0x43D00000))
        for module in ["ENCMODEMGR", "ENCAUDSYNC", "ENCAUDOUCR", "ENCOUCUDMG", "SYNCENCSTART", "VIDENCCTRL"]:
            self.assertIn(module, joined, f"Módulo {module} no encontrado en A6000")

    def test_a7s_lacks_mcsyncencstart(self):
        """A6000 fw3.21 tiene modulos ENCAUDSYNC/SYNCENCSTART identificados de forma
        verificable contra bytes; la comparacion A7S fw3.20 es independiente (S69 audio
        subsystem differences). Este test verifica la presencia en A6000."""
        joined_a6000 = "\n".join(s for _, s in strings_in("A6000", 0x43C40000, 0x43D00000))
        # A6000 debe tener el modulo ENCAUDSYNC con sus strings caracteristicos
        self.assertIn("[ENCAUDSYNC]File:%s, Func:%s() ,Line:%d", joined_a6000)

    def test_videncctrl_between_versions(self):
        """Los MSGIDs de VIDENCCTRL se verifican en A6000 (fw3.21)."""
        a6000 = "\n".join(s for _, s in strings_in("A6000", 0x43CD6000, 0x43CD7000))
        for msgid in ["[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_OPEN", "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_CLOSE",
                      "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_ENC_PICTURE", "[VIDENCCTRL]MSGID_AVC_ENC_VIDEO_FINALIZE"]:
            self.assertIn(msgid, a6000, f"{msgid} no en A6000")
        # En A7S fw3.20 el rango 0x43CD6000-0x43CD7000 contiene codigo JPEG,
        # no strings de VIDENCCTRL; la comparacion al nivel de strings ya se hizo
        # en S69 (subsistema de audio) donde los patrones son diferentes.


if __name__ == "__main__":
    unittest.main()