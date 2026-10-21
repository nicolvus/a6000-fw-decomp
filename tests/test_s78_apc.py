"""S78 — El espacio de parametros apc_* del motor de imagen YC (A6000 fw3.21).

Anclas verificadas contra los bytes del av-cam.bin.
Ver analysis/s78_apc/yc_apc_params.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x20-\x7e]{4,}")
PARAM_RE = re.compile(r"apc_([a-z0-9]+)\.([a-z0-9_]+)")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 160)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def all_params(model="A6000"):
    """Mapa parametro -> direccion de su cadena, en todo el blob."""
    d = data(model)
    out = {}
    for m in STR_RE.finditer(d):
        s = m.group().decode("ascii", "replace")
        for mm in PARAM_RE.finditer(s):
            key = f"apc_{mm.group(1)}.{mm.group(2)}"
            out.setdefault(key, B + m.start())
    return out


class ApcParameters(unittest.TestCase):
    def test_total_and_modules(self):
        p = all_params()
        self.assertEqual(len(p), 50)
        mods = {}
        for k in p:
            mods.setdefault(k.split(".")[0], 0)
            mods[k.split(".")[0]] += 1
        self.assertEqual(mods, {
            "apc_lpf": 2, "apc_mask": 6, "apc_yld": 9, "apc_acm": 4,
            "apc_zoukou": 18, "apc_coring": 8, "apc_gain": 3,
        })

    def test_key_parameter_addresses(self):
        p = all_params()
        expected = {
            "apc_lpf.vaplpf": 0x43CC44CB, "apc_lpf.haplpf": 0x43CC44F6,
            "apc_mask.vmaskgain": 0x43CC4521, "apc_mask.hmasksel_l": 0x43CC45F9,
            "apc_yld.yld_base_gain": 0x43CC46D5, "apc_yld.yld_sofst_h": 0x43CC4825,
            "apc_acm.acmpm_th_en": 0x43CC485D, "apc_acm.acmpp": 0x43CC48E8,
            "apc_zoukou.size_adj": 0x43CC4916, "apc_zoukou.cgain_hs": 0x43CC4B6E,
            "apc_zoukou.egain_slope_hs": 0x43CC4D12,
            "apc_coring.vcoring_p0": 0x43CC4DCC, "apc_coring.hcoring_aplk": 0x43CC4F54,
            "apc_gain.apgain": 0x43CC4F8C, "apc_gain.hapgain": 0x43CC4FE4,
        }
        for name, addr in expected.items():
            self.assertEqual(p.get(name), addr, name)

    def test_log_format_strings_embed_the_parameter_name(self):
        """Cada parametro se registra con su nombre embebido en la cadena de formato."""
        expected = {
            0x43CC44B4: "[CAMERA_MAIN_YC]: YAP:\tapc_lpf.vaplpf\t=%x",
            0x43CC450A: "[CAMERA_MAIN_YC]: YAP:\t    apc_mask.vmaskgain   \t=%x",
            0x43CC464E: "[CAMERA_MAIN_YC]: YAP:\t    apc_yld.yld_vlpf       \t=%x",
            0x43CC4846: "[CAMERA_MAIN_YC]: YAP:\tapc_acm.acmpm_th_en\t=%x",
            0x43CC48FF: "[CAMERA_MAIN_YC]: YAP:\t    apc_zoukou.size_adj        \t=%x",
            0x43CC4DB5: "[CAMERA_MAIN_YC]: YAP:\t    apc_coring.vcoring_p0   \t=%x",
            0x43CC4F75: "[CAMERA_MAIN_YC]: YAP:\tapc_gain.apgain\t\t=%x",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_job_signature_strings(self):
        self.assertTrue(cstr(0x43CC40DF).startswith(
            "void Camera::YC::job_apc_gain_stl(short unsigned int"))
        self.assertTrue(cstr(0x43CC513D).startswith(
            "void Camera::YC::job_apc_coring_stl(short unsigned int"))

    def test_context_parameters(self):
        """ISO, efecto de imagen y secuencia BDRO condicionan el calculo."""
        self.assertEqual(cstr(0x43CC4D37),
                         "[CAMERA_MAIN_YC]: %s: bdro_sequence error = 0x%x")
        self.assertEqual(cstr(0x43CC4D68), "[CAMERA_MAIN_YC]: YAP:aus_X_ISO =%x")
        self.assertEqual(cstr(0x43CC4D8C), "[CAMERA_MAIN_YC]: YAP:picture_effect =%x")
        self.assertIn("job_apc_main_stl main_digitalZoomRatioDenom=%x", cstr(0x43CC4FF9))
        self.assertIn("job_apc_main_mov digitalZoomRatioDenom=%x", cstr(0x43CC50FB))

    def test_agc_sync_context(self):
        self.assertEqual(cstr(0x43CC4428),
                         "[CAMERA_MAIN_YC]: YAP::job_YC_CalcParam (SYNC): AgcContStdBase = 0x%x")
        self.assertEqual(cstr(0x43CC446E),
                         "[CAMERA_MAIN_YC]: YAP::job_YC_CalcParam (SYNC): AgcContBlend   = 0x%x")


if __name__ == "__main__":
    unittest.main()
