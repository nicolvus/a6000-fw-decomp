"""CFW de objetivos (3.82): el BIONZ cambia solo fuera del bloque TPZL 0 de `nflasha3` (R55) y todo el menú cabe en el espacio de pids."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts"), str(ROOT / "references/fwtool"), str(ROOT / "references/pmca")]
import build_cfw_objetivos as B
import pid_space
from e25_27 import build, fatimg, tarball, tpzl

BLOQUE, INICIO_AVCAM = 0x10000, 0x9A00   # 64 KiB por bloque; av-cam empieza en 0x9a00 de la partición (0x600 del fichero = 0x9c00)


def test_pids_caben_en_el_espacio_ampliado():
    try:
        B._configurar_con_cfw(gam=True, col=True, acc=True)
        assert max(B.M.PIDS) <= pid_space.PID_MAX and len(B.M.PIDS) == len(B.M.SETTINGS)
    finally:
        B.build_pp_menu.EXTRA_TREES.clear()


def test_bionz_no_toca_el_bloque_0():
    base = {e.name: e.data for e in tarball.parse((ROOT / "analysis/gui/g22/base-380.tar").read_bytes())[0]}
    bz = fatimg.Fat16.parse(tpzl.TpzlImage.parse(base[build.NFLASHA3]).decompressed()).read(build.AVCAM_NAME)
    nuevo = B.bionz_objetivos(bz)
    assert len(nuevo) == len(bz) and nuevo != bz
    assert not [i for i, (a, b) in enumerate(zip(bz, nuevo)) if a != b and i < BLOQUE - 0x9C00 + 0x600]
