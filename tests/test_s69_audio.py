"""S69: subsistema de audio (AUDIO) en av-cam.bin A6000 — verificaciones contra bytes.

Linea de ingenieria inversa GENERAL de la camara (audio), sin relacion con la linea
SilentShutter/obturador electronico. Nada se ejecuta del firmware: solo lectura de bytes.

Hechos verificados aqui:
- Inventario de cadenas de audio (ADF/AudioIp/Abb/RecLevel/Wind/MAGIC/SA) en direcciones exactas.
- Codecs de audio en contenedor de video (XAVCS_LPCM/MP4_LPCM/AAC).
- Campos de depuracion (targetAudioFormat/audioChannelNum/audioMuteRec).
- Funciones que emiten logs clave (audio_ip_init, wind_stage, reclevel).
- Diferencias A6000 (fw3.21) vs A7S (fw3.20): codec externo.
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


class AudioInventory(unittest.TestCase):
    def test_sha(self):
        self.assertEqual(hashlib.sha256(data("A6000")).hexdigest(), SHA_A6000)

    def test_audio_region_has_expected_inventory(self):
        st = strings_in("A6000", 0x43C26400, 0x43CDF100)
        self.assertGreater(len(st), 100)

    def test_key_log_strings_and_addresses(self):
        expected = {
            0x43C26411: "[ADF][INIT]AUDIOIP INIT COMP",
            0x43C264FA: "[ADF]AUDIO_IP_CONFIG_TYPE_VGS",
            0x43C26DC1: "[ADF][ADJ]AdfSenserCtrl::SetParamSetMicMode err %x",
            0x43C26DF4: "[ADF][ADJ]AdfSenserCtrl::SetParamSetRecLevel err %x",
            0x43C26E91: "[ADF][ADJ]AdfSenserCtrl::SetParamSetRecLevelMode err %x",
            0x43C28D29: "[ADF][adf]ProcBuffMgrWrAudioPin::StartNew1Comp err1",
            0x43C5C68E: "targetAudioFormat           = %#x",
            0x43C5C6B1: "audioChannelNum             = %#x",
            0x43C5CA62: "audioMuteRec                = %#x",
            0x43C6909D: "audioCodecType AUDIO_CODEC_TYPE_XAVCS_LPCM",
            0x43C690C8: "audioCodecType AUDIO_CODEC_TYPE_MP4_LPCM",
            0x43C690F1: "audioCodecType AUDIO_CODEC_TYPE_AAC",
            0x43CDDAD4: "Abb::SetMicConfig Err mode %x",
            0x43CDDB5E: "[AudioIp]AbbBackUpCtrl ChangeBackUp START err %x",
            0x43CDDD49: "AbbMicSensAdjustCtrl::SetStatus %x",
            0x43CDDDF3: "15AbbRecLevelCtrl",
            0x43CDDEA7: "WindStage:%d, MagDataRsv:%d",
            0x43CDDEC4: "MAGIC SetNwnr",
            0x43CDDED3: "New WNR ON",
            0x43CDDEDF: "New WNR OFF",
            0x43CDDEEC: "MAGIC SetPremiumCloserVoice",
            0x43CDDF09: "PremiumCloserVoice ON",
            0x43CDDF20: "PremiumCloserVoice OFF",
            0x43CDDF38: "MAGIC SetMyvoiceCanceling",
            0x43CDDF53: "MyvoiceCanceling ON",
            0x43CDDF68: "MyvoiceCanceling OFF",
            0x43CDDF7E: "MAGIC SetiVoice",
            0x43CDDF8F: "iVoice ON",
            0x43CDDF9A: "iVoice OFF",
            0x43CDDFA6: "RecLevel SetRecLevel",
            0x43CDE0D3: "[RecLevel]SetRecLevel [volume]",
            0x43CDDFBC: "Sa SaChangeBackup",
            0x43CDD82E: "9AudioIpIf",
            0x43CDD844: "[AIP]SA OpenConfigCb Ack",
            0x43CDE8F1: "12SaDriverBase",
            0x43CDF0E5: "13SaDriverDummy",
            0x43CDF0F5: "[AUDIOIP]DUMMY EXE ",
            0x43CDEF06: "8AbbSysnd",
            0x43CDEF10: "ABB SYSND InitComp cnt:%d",
            0x43CDDAF3: "3Abb",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr("A6000", addr), text, hex(addr))


class AudioFunctions(unittest.TestCase):
    def test_audio_ip_init_function(self):
        d = data("A6000")
        ins = list(MD.disasm(d[0x4356725C - B:0x43567290 - B], 0x4356725C))
        ops = [(i.address, i.mnemonic, i.op_str) for i in ins if i.mnemonic != ".byte"]
        self.assertIn((0x43567260, "ldr", "r0, [pc, #0x2c]"), ops)
        self.assertIn((0x43567264, "bl", "#0x435ab880"), ops)
        found = log_strings_in_func("A6000", 0x4356725C, 0x43567290)
        self.assertIn("[ADF][INIT]AUDIOIP INIT COMP", [s for _, _, s in found])

    def test_wind_stage_function(self):
        found = log_strings_in_func("A6000", 0x43929DB4, 0x43929DE6)
        self.assertIn("WindStage:%d, MagDataRsv:%d", [s for _, _, s in found])

    def test_reclevel_function(self):
        found = log_strings_in_func("A6000", 0x43929FA4, 0x43929FCE)
        self.assertIn("RecLevel SetRecLevel", [s for _, _, s in found])


class A7SComparison(unittest.TestCase):
    def test_a7s_has_external_codec_subsystem(self):
        joined_a6000 = "\n".join(s for _, s in strings_in("A6000", 0x43C20000, 0x43D00000))
        joined_a7s = "\n".join(s for _, s in strings_in("A7S", 0x43C20000, 0x43D00000))
        self.assertNotIn("15AbbExtCodecCtrl", joined_a6000)
        self.assertIn("15AbbExtCodecCtrl", joined_a7s)
        self.assertNotIn("ConvChSsau2AudioIpCh", joined_a6000)
        self.assertIn("ConvChSsau2AudioIpCh", joined_a7s)

    def test_a7s_external_codec_addresses(self):
        self.assertEqual(cstr("A7S", 0x43CD582E), "15AbbExtCodecCtrl")
        # find the ConvCh string address
        hits = [a for a, s in strings_in("A7S", 0x43C20000, 0x43D00000)
                if "ConvChSsau2AudioIpCh" in s]
        self.assertTrue(len(hits) > 0)

    def test_audio_rec_strings_parity(self):
        def rec_set(model):
            out = set()
            for _, s in strings_in(model, 0x43C20000, 0x43D00000):
                if any(k in s for k in ("RecLevel", "Wind", "Mic", "AudioIp", "Abb")):
                    out.add(s)
            return out
        a, b = rec_set("A6000"), rec_set("A7S")
        # parity: at least 200 shared
        self.assertGreater(len(a & b), 200)


if __name__ == "__main__":
    unittest.main()