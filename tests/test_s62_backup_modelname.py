"""S62: la propiedad BK4 `modelName` (0x003e0005) en el preset de fábrica del A6000 3.21.

Comprueba, sin cámara ni firmware ejecutado:
  * el header del fdat real (modelo numérico 0x41030035, versión 3.21);
  * que 0x003e0005 es `modelName` (16 B, attr solo-lectura) con `ILCE-6000`;
  * que `ILCE-6001` (payload del procedimiento reportado) no existe en el firmware,
    y que su longitud coincide con la propiedad.

Requiere `firmware/extracted/fw321/firmware.fdat`; si no está, el test se omite.
"""
import struct
import tarfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FDAT = ROOT / "firmware/extracted/fw321/firmware.fdat"
MEMBER = "0110_backup/SYSMUSASHI-DSLR/DM_UUD3/CX77500_ALLLANG.bin"
MODEL_CODE = 0x41030035
MODEL_NAME_ID = 0x003E0005
MODEL_NAME = b"ILCE-6000" + b"\x00" * 7
SPOOF_NAME = b"ILCE-6001" + b"\x00" * 7

HDR_SIZE = 0x100


def read_fdat_header(f):
    f.seek(0)
    head = f.read(0x40)
    return {
        "magic": head[0:8],
        "major": head[0x21],
        "minor": head[0x20],
        "model": struct.unpack_from("<I", head, 0x24)[0],
        "region": struct.unpack_from("<I", head, 0x28)[0],
        "fw_offset": struct.unpack_from("<I", head, 0x30)[0],
    }


def backup_header(blob):
    (magic, cookie, write_comp, revision, num_sub, num_props,
     data_off, data_size, checksum) = struct.unpack_from("<iii4siiiii", blob, 0)
    assert revision[:2] == b"BK" and revision[3:] == b"\x00"
    return {
        "revision": revision[2],
        "num_sub": num_sub,
        "num_props": num_props,
        "data_off": data_off,
        "data_size": data_size,
        "checksum": checksum,
        "header_size": HDR_SIZE,
    }


def backup_property(blob, pid):
    """Entrada de tabla y datos de una propiedad BK4 (revisiones 2 y 4)."""
    h = backup_header(blob)
    entry_size = 6 if h["revision"] >= 4 else 5
    sub = pid >> 16
    idx = pid & 0xFFFF
    sub_off = h["header_size"] + sub * 6
    num_sub_props, ptr = struct.unpack_from("<hi", blob, sub_off)
    assert idx < num_sub_props, "indice fuera del subsistema"
    row = ptr + idx
    table_off = h["header_size"] + h["num_sub"] * 6
    row_off = table_off + row * entry_size
    attr = struct.unpack_from("<h" if entry_size == 6 else "<b", blob, row_off)[0]
    prop_ptr = struct.unpack_from("<i", blob, row_off + (2 if entry_size == 6 else 1))[0]
    size = prop_ptr >> 24
    off = prop_ptr & 0xFFFFFF
    if size == 0:
        size = struct.unpack_from("<h", blob, off)[0]
        off += 2
    elif size == 0xFF:
        size = struct.unpack_from("<h", blob, off)[0]
        off += 2
    return attr, blob[off:off + size]


@unittest.skipUnless(FDAT.exists(), "firmware A6000 3.21 no disponible")
class ModelNameProperty(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(FDAT, "rb") as f:
            cls.hdr = read_fdat_header(f)
            f.seek(cls.hdr["fw_offset"])
            tf = tarfile.open(fileobj=f, mode="r:")
            for m in tf:
                if m.name == MEMBER:
                    cls.blob = tf.extractfile(m).read()
                    break
            else:
                raise unittest.SkipTest("preset no encontrado en el fdat")

    def test_fdat_header_is_numeric_model_guard(self):
        self.assertEqual(self.hdr["magic"], b"UDTRFIRM")
        self.assertEqual(self.hdr["model"], MODEL_CODE)
        self.assertEqual((self.hdr["major"], self.hdr["minor"]), (3, 0x21))  # 3.21
        self.assertEqual(self.hdr["region"], 0)

    def test_property_id_is_subsystem_3e_index_5(self):
        self.assertEqual(MODEL_NAME_ID >> 16, 0x3E)
        self.assertEqual(MODEL_NAME_ID & 0xFFFF, 5)

    def test_model_name_is_ilce_6000_16_bytes_read_only(self):
        attr, data = backup_property(self.blob, MODEL_NAME_ID)
        self.assertEqual(len(data), 16)
        self.assertEqual(data, MODEL_NAME)
        self.assertEqual(attr & 0x01, 0x01)  # solo lectura (parser PMCA)

    def test_model_code_is_separate_and_protected(self):
        _, code = backup_property(self.blob, 0x00E70000)
        self.assertEqual(code, bytes.fromhex("0000069905"))
        attr, _ = backup_property(self.blob, 0x00E70000)
        self.assertEqual(attr & 0x02, 0x02)

    def test_spoof_payload_has_same_size_and_absent_from_firmware(self):
        self.assertEqual(len(SPOOF_NAME), len(MODEL_NAME))
        self.assertNotEqual(SPOOF_NAME, MODEL_NAME)
        self.assertNotIn(b"ILCE-6001", self.blob)
        self.assertEqual(self.blob.count(b"ILCE-"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
