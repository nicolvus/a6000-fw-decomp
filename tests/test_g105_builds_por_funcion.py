"""G105 — una build por función sobre la base Silent (`build_cfw_film --funciones`): cada función toca solo sus ficheros y el núcleo solo suma sus capas.
Genera los `/usr` en subprocesos (la especificación del menú es global); no construye paquetes."""
import hashlib
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts"), str(ROOT / "scripts/lut")]
LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
pytestmark = pytest.mark.skipif(not (LIB / "CautionConfig.so").is_file(), reason="fw321 extraído no disponible")
VARIANTES = {"base": "", "film": "film", "pp": "pp", "exfine": "exfine", "iso": "iso"}


@pytest.fixture(scope="module")
def usr(tmp_path_factory) -> dict[str, dict[str, str]]:
    """{variante: {fichero: sha256}} del `/usr` de cada variante."""
    res = {}
    for v, f in VARIANTES.items():
        out = tmp_path_factory.mktemp(v)
        code = ("import sys, pathlib; sys.path.insert(0, 'scripts/gui'); import build_cfw_film as F; "
                f"F.build_files(pathlib.Path({str(out)!r}), F.LOOKS, funciones={{x for x in {f!r}.split(',') if x}})")
        subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True, capture_output=True)
        files = out / "files"
        res[v] = {str(p.relative_to(files)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files.rglob("*") if p.is_file() and p.suffix in (".so", ".uxc")}
    return res


def test_base_solo_silent(usr):
    assert {p for p in usr["base"] if not p.startswith("share/app/string_")} == {"lib/CautionConfig.so", "lib/libObj.so", "lib/viewUnified2.so"}


def test_exfine_solo_cambia_cautionconfig(usr):
    distintos = {p for p in usr["base"] | usr["exfine"] if usr["base"].get(p) != usr["exfine"].get(p)}
    assert distintos == {"lib/CautionConfig.so"}


def test_iso_no_toca_menu_ni_film(usr):
    assert usr["iso"]["lib/CautionConfig.so"] == usr["base"]["lib/CautionConfig.so"]
    assert "lib/viewUnified7.so" not in usr["iso"] and "share/app/image_cmn_169.uxc" in usr["iso"]


def test_film_y_pp_sin_iso_ni_otro(usr):
    for v in ("film", "pp"):
        assert "share/app/image_cmn_169.uxc" not in usr[v]
    assert usr["film"]["lib/libObj.so"] == usr["base"]["lib/libObj.so"]      # Film no toca libObj; PP sí (eco PP)
    assert usr["pp"]["lib/libObj.so"] != usr["base"]["lib/libObj.so"]


def test_nucleo_por_capas():
    """`bionz_de` aplica exactamente las capas pedidas (sobre bytes sintéticos con las funciones de parche sustituidas)."""
    import build_cfw_film as F
    capas = []
    orig = (F.build_base_pp.bionz_cfw, F.patch_silent_r5.apply_bytes, F.film_patch.apply_bytes, F.iso_avcam_patch.apply_bytes)
    try:
        F.build_base_pp.bionz_cfw = lambda d: capas.append("pp") or d
        F.patch_silent_r5.apply_bytes = lambda d: capas.append("silent") or d
        F.film_patch.apply_bytes = lambda d: capas.append("film") or d
        F.iso_avcam_patch.apply_bytes = lambda d: capas.append("iso") or d
        for fun, esperado in ((set(), ["silent"]), ({"film"}, ["silent", "film"]), ({"pp"}, ["pp"]), ({"iso"}, ["silent", "iso"]),
                              ({"exfine"}, ["silent"]), (F.POR_DEFECTO | {"pp"}, ["pp", "film", "iso"])):
            capas.clear()
            F.bionz_de(fun)(b"")
            assert capas == esperado, fun
    finally:
        F.build_base_pp.bionz_cfw, F.patch_silent_r5.apply_bytes, F.film_patch.apply_bytes, F.iso_avcam_patch.apply_bytes = orig
