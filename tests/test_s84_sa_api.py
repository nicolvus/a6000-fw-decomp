"""S84 — El API del motor de imagen (SA): catalogo de sa_func_* con firmas C++.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s84_sa_api/sa_api_catalogue.md
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis" / "s58"))
from tdis import data, B  # noqa: E402

STR_RE = re.compile(rb"[\x09\x20-\x7e]{4,}")


def cstr(addr, model="A6000"):
    d = data(model)
    off = addr - B
    end = d.find(b"\x00", off, off + 250)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def sa_strings(model="A6000"):
    d = data(model)
    return [m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
            if b"sa_func_" in m.group()]


def imaging_cap_calls(model="A6000"):
    """Cadenas de traza que invocan sa_func_* (con prefijo [IMAGING_CAP] en A6000)."""
    d = data(model)
    return "\n".join(m.group().decode("ascii", "replace") for m in STR_RE.finditer(d)
                     if b"sa_func_" in m.group() and b"Camera::SaFuncDrv" not in m.group())


class SaApi(unittest.TestCase):
    def test_counts(self):
        # 92 cadenas contienen 'sa_func_' (65 de ellas con 30+ caracteres, que son las
        # firmas/trazas largas); el recuento depende del filtro, se fija el de referencia.
        self.assertEqual(len(sa_strings("A6000")), 92)
        self.assertEqual(len(sa_strings("A7S")), 109)

    def test_common_signature_shape(self):
        """Firma comun: (unit_num u8, func_code u16, X_START_PARAM*) -> SA_FUNCDRV_ERR."""
        s = cstr(0x43CEC7F5)
        self.assertTrue(s.startswith("Camera::SaFuncDrv::SA_FUNCDRV_ERR Camera::SaFuncDrv::sa_func_BFNR_release("))
        self.assertIn("__uint8_t, __uint16_t, Camera::SaFuncDrv::BFNR_START_PARAM*)", s)

    def test_signatures_with_context(self):
        self.assertIn("sa_func_BFNR_init(Camera::SaFuncDrv::SaFuncDrvCmn*, "
                      "Camera::SaFuncDrv::BFNR_START_PARAM*, Camera::SaFuncDrv::BFNR_PARAM*, __uint16_t)",
                      cstr(0x43CEC98B))
        self.assertIn("sa_func_KKNR_exit(Camera::SaFuncDrv::SaFuncDrvCmn*, "
                      "Camera::SaFuncDrv::KKNR_START_PARAM*)", cstr(0x43CEE27B))

    def test_golfshot_two_overloads(self):
        self.assertIn("sa_func_GOLFSHOT_start(__uint8_t, __uint16_t, "
                      "Camera::SaFuncDrv::SSP_START_PARAM*, Camera::SaFuncDrv::SSP_START_MBX*, __uint8_t*)",
                      cstr(0x43CEDC91))
        self.assertIn("sa_func_GOLFSHOT_start(__uint8_t, __uint16_t, "
                      "Camera::SaFuncDrv::BGEST_START_PARAM*, Camera::SaFuncDrv::SA_MBX_0123*, __uint8_t*)",
                      cstr(0x43CEDFF6))
        self.assertIn("sa_func_GOLFSHOT_release", cstr(0x43CEDF67))

    def test_other_signatures(self):
        for addr, frag in {
            0x43CED65E: "sa_func_CONTP_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::CONTP_START_PARAM*)",
            0x43CED8AC: "sa_func_DECOMP_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::DECOMP_START_PARAM*)",
            0x43CEE1F4: "sa_func_KKNR_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::KKNR_START_PARAM*)",
            0x43CEE4CA: "sa_func_NFLASH_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::NFLASH_START_PARAM*)",
            0x43CEE7EC: "sa_func_PreDCV_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::PRE_DCV_START_PARAM*)",
            0x43CEE878: "sa_func_SFTFCS_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::SFTFCS_START_PARAM*)",
            0x43CEEAA0: "sa_func_SFTFCS_preinit(__uint16_t)",
            0x43CEEEA8: "sa_func_TBOX_release(__uint8_t, __uint16_t, Camera::SaFuncDrv::TBOX_START_PARAM*)",
        }.items():
            self.assertIn(frag, cstr(addr), hex(addr))

    def test_error_codes(self):
        d = data("A6000")
        txt = d.decode("latin-1")
        for code in ("SA_FUNCDRV_E_OSAL", "SA_FUNCDRV_E_RSLTCODE", "SA_FUNCDRV_E_ERRCODE"):
            self.assertIn(code, txt, code)

    def test_imaging_cap_calls(self):
        calls = imaging_cap_calls("A6000")
        for frag in ("sa_func_NFLASH_start error", "sa_func_DUALREC_BAYER_start",
                     "sa_func_BFNR_acquire()", "sa_func_BOKS_acquire err",
                     "sa_func_CONTP_acquire error", "sa_func_DECOMP_acquire()",
                     "sa_func_PreDCV_start error", "sa_func_KKNR_acquire error",
                     "sa_func_LFNR_acquire error", "sa_func_SPICA_acquire error",
                     "sa_func_STAR_acquire error", "sa_func_TBOX_start error",
                     "sa_func_YKNR_acquire error"):
            self.assertIn(frag, calls, frag)

    def test_spica_three_phases(self):
        calls = imaging_cap_calls("A6000")
        for frag in ("sa_func_SPICA_PRE_release", "sa_func_SPICA_MAPPING_release",
                     "sa_func_SPICA_POST_release"):
            self.assertIn(frag, calls, frag)

    def test_differential_motionshot_and_nlap(self):
        """La A7S usa NLAP y sa_func_MOTIONSHOT_*; en la A6000 fw3.21 no existen (0 ocurrencias)."""
        a7 = imaging_cap_calls("A7S")
        a6 = imaging_cap_calls("A6000")
        for frag in ("sa_func_MOTIONSHOT_acquire error", "sa_func_MOTIONSHOT_start error",
                     "sa_func_NLAP_acquire error", "sa_func_NLAP_start error",
                     "sa_func_NLAP_release error"):
            self.assertIn(frag, a7, frag)
            self.assertNotIn(frag, a6, frag)
        # NLAP desaparece COMPLETAMENTE en la A6000 (tambien el driver)
        d6, d7 = data("A6000"), data("A7S")
        self.assertEqual(d6.find(b"NLAP"), -1)
        self.assertGreater(d7.find(b"NLAP"), -1)
        # ... y lo que queda en la A6000 es MOTIONSHOTVIDEO (modulo SFRS), otra cosa
        self.assertEqual(d6.find(b"sa_func_MOTIONSHOT"), -1)
        self.assertGreater(d6.find(b"MOTIONSHOTVIDEO"), -1)
        self.assertIn("[YC][NLAP]", "\n".join(sa_strings("A7S") + [cstr(0x43CBBF71, "A7S")]))

    def test_sftfcs_lowercase_in_capture_path(self):
        """La A6000 llama 'sa_func_sftfcs_start' (minusculas) desde IMAGING_CAP."""
        self.assertIn("sa_func_sftfcs_start error", imaging_cap_calls("A6000"))
        d = data("A6000")
        txt = d.decode("latin-1")
        self.assertIn("sftfcs_start_mbx.cha_mbx0", txt)
        self.assertIn("sftfcs_start_mbx.cha_mbx2", txt)
        self.assertEqual(cstr(0x43CC93C2),
                         "[IMAGING_CAP]: %s: sa_func_sftfcs_start error (%d)")

    def test_nflash_is_the_flash_driver(self):
        """Los parametros de NFLASH son de flash: flash_add/amb_add/int_add/rc_line_ofs."""
        d = data("A6000")
        txt = d.decode("latin-1")
        for frag in ("flash_add", "amb_add", "int_add", "rc_line_ofs"):
            self.assertIn(frag, txt, frag)


if __name__ == "__main__":
    unittest.main()
