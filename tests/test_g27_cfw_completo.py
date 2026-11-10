"""G27: piezas del CFW completo (build_cfw_completo): el gancho de arranque y el nodo de Silent reproducen el 3.59 de G22."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import build_cfw_hooks as H

USR = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"
F359 = ROOT / "analysis/gui/g22/files-359"
needs = pytest.mark.skipif(not (USR.is_dir() and F359.is_dir()), reason="faltan el firmware o el paquete 3.59")


@needs
def test_gancho_de_pp_ram_es_el_del_359():
    assert H.con_gancho_ram((USR / "bin/s_start_android.sh").read_text()) == (F359 / "bin/s_start_android.sh").read_text()
    with pytest.raises(AssertionError):
        H.con_gancho_ram((F359 / "bin/s_start_android.sh").read_text())      # no se aplica dos veces


@needs
def test_nodo_silent_con_pid_0x12_reproduce_el_359(tmp_path):
    import build_silent_menu_test as S
    dev_b = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev"
    if not dev_b.is_dir():
        pytest.skip("falta la A6300")
    S.main(USR.parent, dev_b, tmp_path, pid_silent=0x12)
    assert (tmp_path / "lib/CautionConfig.so").read_bytes() == (F359 / "lib/CautionConfig.so").read_bytes()
    assert (tmp_path / "lib/viewUnified2.so").read_bytes() == (F359 / "lib/viewUnified2.so").read_bytes()


def test_add_menu_entry_varias_entradas_suma_cuentas():
    import add_menu_entry as A
    vu = USR / "lib/viewUnified2.so"
    if not vu.is_file():
        pytest.skip("falta viewUnified2.so")
    import struct
    d = A.patch(vu.read_bytes(), [0xEB0, 0x1234])
    assert [struct.unpack_from("<H", d, m)[0] & 0xFF for _, _, m, _, _, _ in A.PAGES] == [c + 2 for _, c, *_ in A.PAGES]
    assert A.patch(vu.read_bytes(), 0xEB0) == A.patch(vu.read_bytes(), [0xEB0])
