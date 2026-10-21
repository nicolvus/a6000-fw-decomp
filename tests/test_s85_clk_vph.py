"""S85 — CLK_CTRL (control de reloj) y VPH_API (API del procesado de video del visor).

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s85_clk_vph/clk_ctrl_vph_api.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x09\x20-\x7e]{6,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 200)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def module_strings(mod, model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if m.group().startswith(f"[{mod}]".encode())]


class ClkCtrl(unittest.TestCase):
    def test_only_in_fw321(self):
        """CLK_CTRL no existe en la A7S fw3.20: es nuevo en la fw3.21."""
        self.assertEqual(len(module_strings("CLK_CTRL", "A6000")), 66)
        self.assertEqual(len(module_strings("CLK_CTRL", "A7S")), 0)

    def test_ddl_api(self):
        joined = "\n".join(module_strings("CLK_CTRL"))
        for f in ("ddl_clkctrl_get_clk_chg_enable", "ddl_clkctrl_unlock_sync_signal",
                  "ddl_clkctrl_lock_sync_signal", "ddl_clkctrl_set_sysv_delay_changing",
                  "ddl_clkctrl_set_sysv_delay", "ddl_clkctrl_set_sync_signal",
                  "ddl_clkctrl_set_sync_initial_signal", "ddl_clkctrl_set_sysv_initial_delay",
                  "ddl_clkctrl_close_dly", "ddl_clkctrl_open_dly",
                  "ddl_clkctrl_close_clk", "ddl_clkctrl_open_clk"):
            self.assertIn(f, joined, f)

    def test_state_machine(self):
        self.assertIn("State:STATE_INIT1(InitDelay)", cstr(0x43C3A534))
        self.assertIn("State:STATE_NORMAL(InitSignal)", cstr(0x43C3A55D))
        self.assertIn("State:STATE_LOCK", cstr(0x43C3A588))
        self.assertIn("STATE_CHANGE_CLK", cstr(0x43C3A6E9))
        self.assertIn("STATE_CHANGE_CLK_LOCKING", cstr(0x43C3A768))
        self.assertIn("Tsk ClkCtrl Initial", cstr(0x43C3A5FF))

    def test_subsystem_bookkeeping(self):
        self.assertIn("open subsytem", cstr(0x43C3A91A))
        self.assertIn("close subsytem", cstr(0x43C3A97E))
        self.assertIn("already opened", cstr(0x43C3A93D))
        self.assertIn("lock_sync_signal subsystem", cstr(0x43C3A5A5))
        self.assertIn("unlock_sync_signal subsystem", cstr(0x43C3A5D1))

    def test_clock_and_delay_changes(self):
        self.assertIn("CHANGE_CLK dly", cstr(0x43C3A71B))
        self.assertIn("ClkChgExec at", cstr(0x43C3A811))
        self.assertIn("DelayChgExec at", cstr(0x43C3A8C3))
        self.assertIn("m_vfc.main=0x%0x, m_vfc.sub=0x%0x", cstr(0x43C3AC2F))

    def test_master_slave_and_vph_link(self):
        self.assertIn("Receive Message from Master", cstr(0x43C3ABD0))
        self.assertIn("Send Message to Slave", cstr(0x43C3AC86))
        self.assertIn("Send HTP at", cstr(0x43C3AAE7))
        self.assertIn("vph stat:%d,mode:%d", cstr(0x43C3AA69))


class VphApi(unittest.TestCase):
    def test_only_in_fw321(self):
        self.assertEqual(len(module_strings("VPH_API", "A6000")), 106)
        self.assertEqual(len(module_strings("VPH_API", "A7S")), 0)

    def test_command_vocabulary(self):
        expected = {
            0x43CE32E7: "[VPH_API]<mode>",
            0x43CE32F7: "[VPH_API]<line_out>o/f:%d",
            0x43CE3311: "[VPH_API]<panel_out>o/f:%d",
            0x43CE332C: "[VPH_API]<update_yuv>s:%d",
            0x43CE3346: "[VPH_API]<mix_mode>",
            0x43CE335A: "[VPH_API]<osd_on>",
            0x43CE3382: "[VPH_API]<osdarea>",
            0x43CE33AF: "[VPH_API]<faceframe_on>",
            0x43CE33E3: "[VPH_API]<timecode_on>",
            0x43CE3415: "[VPH_API]<yuv_mute>o/f:%d,s:%d",
            0x43CE344E: "[VPH_API]<chroma_mute>",
            0x43CE3465: "[VPH_API]<line_closedcaption>",
            0x43CE3483: "[VPH_API]<line_macrovision>",
            0x43CE349F: "[VPH_API]<line_vbidwss>",
            0x43CE34D2: "[VPH_API]<panel_brightness>",
            0x43CE34EE: "[VPH_API]<panel_cabc>",
            0x43CE3504: "[VPH_API]<panel_depth>",
            0x43CE354C: "[VPH_API]<pictureeffect>",
            0x43CE357F: "[VPH_API]<zebra>",
            0x43CE3590: "[VPH_API]<peaking>",
            0x43CE35B7: "[VPH_API]<histogram>",
            0x43CE35CC: "[VPH_API]<testpattern>",
            0x43CE3688: "[VPH_API]<parallax_adjust>",
            0x43CE36A3: "[VPH_API]<set_extblackframe>",
            0x43CE36C0: "[VPH_API]<set_color_temperature>",
            0x43CE3728: "[VPH_API]<set_panel_osd_luminance>",
            0x43CE3C84: "[VPH_API]<dualpanel_out>o/f:%d",
            0x43CE3CE4: "[VPH_API]<force_out>",
        }
        for addr, text in expected.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_sub_channel_twins(self):
        """Cada comando tiene su gemelo _sub (los dos canales: linea y panel)."""
        for addr, text in {
            0x43CE37D2: "[VPH_API]<update_yuv_sub>s:%d",
            0x43CE39BC: "[VPH_API]<panel_brightness_sub>",
            0x43CE3A85: "[VPH_API]<zebra_sub>",
            0x43CE3C1F: "[VPH_API]<set_panel_osd_luminance_sub>",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))
        joined = "\n".join(module_strings("VPH_API"))
        self.assertEqual(joined.count("_sub>"), joined.count("_sub>"))
        self.assertIn("<faceframe_on_sub>", joined)

    def test_status_outputs(self):
        for addr, text in {
            0x43CE3CF9: "[VPH_API]>hw_status<",
            0x43CE3D0E: "[VPH_API]>mode_status<",
            0x43CE3D3C: "[VPH_API]>histogram_result<",
            0x43CE3D58: "[VPH_API]>yuv_delay<",
            0x43CE3D6D: "[VPH_API]>osdmix_size_panel<",
            0x43CE3DA6: "[VPH_API]>black_frame<",
            0x43CE3DE4: "[VPH_API]>shutter_mute<",
        }.items():
            self.assertEqual(cstr(addr), text, hex(addr))

    def test_faceframe_links_to_face_detection(self):
        """El visor dibuja el marco de cara: puente con el subsistema FC (S71)."""
        joined = "\n".join(module_strings("VPH_API"))
        self.assertIn("<faceframe_on>", joined)
        self.assertIn("<update_faceframe>", joined)
        self.assertIn("<faceframe_color>", joined)


if __name__ == "__main__":
    unittest.main()
