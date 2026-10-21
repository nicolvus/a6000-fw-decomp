"""S71 — Subsistema de deteccion de caras y objetos (FC/FRC) de la A6000 fw3.21.

Anclas verificadas contra los bytes del av-cam.bin (A6000 fw3.21 y A7S fw3.20).
Ver analysis/s71_frc/frc_subsystem.md

Este archivo sustituye al borrador del subagente (que usaba direcciones en espacio de
ficheros, nombres de bufer inexistentes y un diferencial A7S incorrecto).
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
    end = d.find(b"\x00", off, off + 200)
    return d[off:end].decode("ascii", "replace").rstrip("\n")


def fc_files(model="A6000"):
    """Mapa fichero FC/... -> direccion de su cadena."""
    d = data(model)
    out = {}
    for m in STR_RE.finditer(d):
        s = m.group().decode("ascii", "replace")
        if s.startswith("FC/") and (".c" in s or ".cpp" in s):
            out.setdefault(s, B + m.start())
    return out


def strings_with(prefix, model="A6000"):
    d = data(model)
    return sorted(B + m.start() for m in STR_RE.finditer(d) if m.group().startswith(prefix.encode()))


def strings_containing(frag, model="A6000"):
    d = data(model)
    return sorted(B + m.start() for m in STR_RE.finditer(d) if frag.encode() in m.group())


class FcInventory(unittest.TestCase):
    def test_file_set_identical_in_both_models(self):
        """CORRECCION: los 99 ficheros FC/... son los mismos en A6000 fw3.21 y A7S fw3.20."""
        a6, a7 = fc_files("A6000"), fc_files("A7S")
        self.assertEqual(len(a6), 99)
        self.assertEqual(len(a7), 99)
        self.assertEqual(set(a6), set(a7))

    def test_key_file_addresses(self):
        a6 = fc_files("A6000")
        expected = {
            "FC/Alg/fc_alg_frc.cpp": 0x43CF052F,
            "FC/Alg/fc_alg_smoothing.cpp": 0x43CF0412,
            "FC/Alg/fc_alg_remove_overlap.cpp": 0x43CF042E,
            "FC/Alg/fc_alg_target_selecting.cpp": 0x43CF044F,
            "FC/Alg/fc_alg_tracking.cpp": 0x43CF0472,
            "FC/Alg/fc_alg_pre_fdt.cpp": 0x43CF048D,
            "FC/Alg/fc_alg_blink.cpp": 0x43CF071F,
            "FC/Alg/fc_alg_exif_face_data.cpp": 0x43CF0737,
            "FC/Alg/fc_alg_exif_makernote.cpp": 0x43CF0758,
            "FC/Seq/fc_data_frc.cpp": 0x43CF0518,
            "FC/Seq/fc_seq_mon_object.cpp": 0x43CF0563,
            "FC/Seq/fc_seq_vae.cpp": 0x43CF06A4,
            "FC/Seq/fc_seq_oneshot.cpp": 0x43CF0705,
            "FC/Seq/fc_seq_touch.cpp": 0x43CF082F,
            "FC/Seq/fc_seq_prc.cpp": 0x43CF088A,
            "FC/Drv/fc_drv_fat.cpp": 0x43CF04E6,
            "FC/Drv/fc_drv_iro.cpp": 0x43CF059E,
            "FC/Drv/fc_drv_vae.cpp": 0x43CF06D1,
            "FC/Drv/fc_drv_prc.cpp": 0x43CF08A0,
            "FC/Drv/fc_drv_bt.cpp": 0x43CF603A,
            "FC/Drv/fc_drv_edt.cpp": 0x43CF6FD9,
            "FC/Drv/fc_drv_iro2g.cpp": 0x43CF7044,
            "FC/Seq/fc_seq_pmv.cpp": 0x43CF697B,
            "FC/Feature/fc_feature_mon_face.cpp": 0x43CF04A7,
            "FC/Feature/fc_feature_mon_object.cpp": 0x43CF0618,
            "FC/Feature/fc_feature_capture.cpp": 0x43CF0779,
            "FC/Feature/fc_feature_retouch.cpp": 0x43CF079B,
            "FC/Feature/fc_feature_panorama.cpp": 0x43CF07BD,
            "FC/Feature/fc_feature_develop.cpp": 0x43CF07E0,
            "FC/Feature/fc_feature_panorama_face_meta.cpp": 0x43CF0802,
            "FC/Feature/fc_feature_touch_for_scanaf.cpp": 0x43CF085F,
            "FC/Feature/fc_feature_prc_retouch.cpp": 0x43CF08B6,
            "FC/Feature/fc_feature_base_setting.cpp": 0x43CF08DC,
            "FC/SaFuncDrv/recog_sa_drv.cpp": 0x43CF0545,
            "FC/SaFuncDrv/fc_sa_frc2_drv.cpp": 0x43CF0A5C,
            "FC/SaFuncDrv/fc_sa_frc2_mmu.cpp": 0x43CF0BF1,
            "FC/Misc/fc_detect_cb_handler.cpp": 0x43CF0903,
            "FC/Misc/fc_prc_request_controller.cpp": 0x43CF0924,
            "FC/Misc/fc_scalara_detect_cb_handler.cpp": 0x43CF0A33,
        }
        for name, addr in expected.items():
            self.assertEqual(a6.get(name), addr, name)

    def test_a7s_addresses_of_key_files(self):
        a7 = fc_files("A7S")
        self.assertEqual(a7.get("FC/Drv/fc_drv_iro2g.cpp"), 0x43CE9972)
        self.assertEqual(a7.get("FC/Feature/fc_feature_panorama_face_meta.cpp"), 0x43CE5963)
        self.assertEqual(a7.get("FC/Alg/fc_alg_frc.cpp"), 0x43CE5690)


class SaBridge(unittest.TestCase):
    def test_resource_acquisition_on_both_cores(self):
        self.assertIn("Core2 user[0]", cstr(0x43CF094A))
        self.assertIn("Core3 user[1]", cstr(0x43CF0981))
        self.assertIn("RES_SA_FOR_FRC2", cstr(0x43CF09B8))

    def test_real_buffer_names(self):
        """CORRECCION: los buferes reales son s_sa_temp_icon_mem y s_sa_param_mem."""
        self.assertEqual(cstr(0x43CF0BD8), "s_sa_temp_icon_mem.Alloc")
        self.assertEqual(cstr(0x43CF0B64), "s_sa_temp_icon_mem.Free")
        self.assertEqual(cstr(0x43CF0BC3), "s_sa_param_mem.Alloc")
        self.assertEqual(cstr(0x43CF0B7C), "s_sa_param_mem.Free")
        self.assertIn("s_mmu_memhundle Free Error", cstr(0x43CF0B90))
        # los nombres del borrador no existen
        for model in ("A6000", "A7S"):
            d = data(model)
            self.assertEqual(d.find(b"s_temp_icon_mem"), -1)
            self.assertEqual(d.find(b"s_param_mem\x00"), -1)

    def test_mmu_and_calc_cycle(self):
        self.assertIn("MakeMmu - SA_MMU_NUM_MEM_ERR", cstr(0x43CF0C11))
        self.assertIn("MakeMmu - MakeExtentError", cstr(0x43CF0CF9))
        self.assertEqual(cstr(0x43CF0AAF), "FC MMU param open error %d")
        self.assertIn("ddl_saCalcCancel", cstr(0x43CF0AFB))
        self.assertIn("int_fact=NOT_FINISH", cstr(0x43CF0AD4))
        self.assertEqual(cstr(0x43CF0B39), "alloc size:%d, expected:%d")
        self.assertEqual(cstr(0x43CF0B54), "SA result: NULL")
        self.assertIn("error_status (cancel)", cstr(0x43CF0A7C))

    def test_face_icon_handles(self):
        self.assertEqual(cstr(0x43CF0D6C), "FRC: Init FaceIcon")
        self.assertEqual(cstr(0x43CF0D7F), "FRC: Update FaceIcon :%d")
        self.assertEqual(cstr(0x43CF0D98), "FaceIconInfo::Free() handle:%d")
        self.assertEqual(cstr(0x43CF0DB8), "FaceIconInfo::Alloc() handle:%d")

    def test_same_strings_in_a7s(self):
        """Las mismas cadenas existen en la A7S (direcciones distintas)."""
        self.assertEqual(cstr(0x43CE5ECD, "A7S"), "FRC: Init FaceIcon")
        self.assertEqual(cstr(0x43CE5F19, "A7S"), "FaceIconInfo::Alloc() handle:%d")
        self.assertEqual(cstr(0x43CE5C9A, "A7S"), "alloc size:%d, expected:%d")


class TrackingDetectors(unittest.TestCase):
    def test_detector_prefixes_exist(self):
        for prefix in ("[TRK]: [DETSA]", "[TRK]: [EDTSA]", "[TRK]: [IRO2G]",
                       "[TRK]: [PMV]", "[TRK]: [STK]", "[TRK]: [BT]"):
            self.assertGreaterEqual(len(strings_with(prefix)), 3, prefix)

    def test_stk_is_saliency_and_similarity(self):
        """STK: saliencia y similitud (toque/color) segun sus propios callbacks."""
        joined = "\n".join(cstr(a) for a in strings_with("[TRK]: [STK]"))
        self.assertIn("Saliency CB", joined)
        self.assertIn("TouchSimilarity CB", joined)
        self.assertIn("ColorSimilarity CB", joined)

    def test_pmv_is_motion_vector_tracking(self):
        joined = "\n".join(cstr(a) for a in strings_with("[TRK]: [PMV]"))
        self.assertIn("Affine_err_thresh", joined)
        self.assertIn("Vector_thresh", joined)
        self.assertIn("Motion_frame_num", joined)

    def test_bt_detects_objects_with_fg_bg(self):
        joined = "\n".join(cstr(a) for a in strings_with("[TRK]: [BT]"))
        self.assertIn("fg_area", joined)
        self.assertIn("bg_area", joined)
        self.assertIn("bayes_map_level", joined)
        self.assertIn("big_obj_size_thres", joined)

    def test_edt_is_eye_detection(self):
        joined = "\n".join(cstr(a) for a in strings_with("EyeDetection"))
        self.assertGreaterEqual(len(joined), 1)
        self.assertIn("idt_edt_start", "\n".join(cstr(a) for a in strings_containing("idt_edt_start")))

    def test_face_module_states(self):
        joined = "\n".join(cstr(a) for a in strings_with("[FACE]"))
        for frag in ("[FACE]: [INIT]", "[FACE]: [MON]", "[FACE]: [IMME]",
                     "[FACE]: [ATTR]", "[FACE]: [STOP]", "SA Return Error",
                     "FDT Int Error"):
            self.assertIn(frag, joined, frag)


class FrcAlgorithm(unittest.TestCase):
    def test_recognition_ranking(self):
        joined = "\n".join(cstr(a) for a in strings_with("FRC algo"))
        self.assertIn("recognized ID", joined)
        self.assertIn("swap ID", joined)
        self.assertIn("record_rank", joined)

    def test_priority_rules(self):
        joined = "\n".join(cstr(a) for a in strings_with("FRC error."))
        self.assertIn("CREATE_ICON & PRIORITY_RECOGNIZED", joined)
        self.assertIn("RECOGNIZE & PRIORITY_SELECTED", joined)

    def test_blink_detection(self):
        self.assertIn("blink", "\n".join(cstr(a) for a in strings_containing("blink, unblink")))
        self.assertIn("FC/Alg/fc_alg_blink.cpp", fc_files("A6000"))

    def test_pre_fdt_scene_modes(self):
        joined = "\n".join(cstr(a) for a in strings_with("PreFdt On:"))
        for frag in ("African", "Scene", "Bunri", "Hist1", "Light_backlight_Hist"):
            self.assertIn(frag, joined, frag)

    def test_face_object_tracking_handover(self):
        joined = "\n".join(cstr(a) for a in strings_containing("ObjTracking"))
        self.assertIn("Face -> ObjTracking", joined)
        self.assertIn("ObjTracking->FaceTracking", joined)

    def test_makernote_of_faces(self):
        self.assertIn("FC MakerNote address",
                      "\n".join(cstr(a) for a in strings_containing("FC MakerNote")))
        self.assertIn("Exif Add", "\n".join(cstr(a) for a in strings_containing("Exif Add")))


if __name__ == "__main__":
    unittest.main()
