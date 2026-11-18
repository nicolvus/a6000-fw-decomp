"""E2E-2 (G75 T47): el overlay local con todos los parches sueltos se construye con los generadores existentes y trae las entradas de menú y los binarios parcheados."""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts/gui/avcam"), str(ROOT / "scripts"), str(ROOT / "references/pmca")]
import build_overlay_objetivos as O

pytestmark = pytest.mark.skipif(not (O.DEV_A.exists() and O.DEV_B.exists() and O.BASE_TAR.exists()), reason="sin firmware extraído")


@pytest.fixture(scope="module")
def overlay(tmp_path_factory):
    import pp_menu_spec as M
    antes = (dict(M.SETTINGS), list(M.PIDS), M.TREE)   # cfw_ajustes.construir muta la spec global
    dest = tmp_path_factory.mktemp("ov") / "pkg"
    O.main(dest)
    yield dest
    M.SETTINGS.clear(); M.SETTINGS.update(antes[0]); M.PIDS[:] = antes[1]; M.TREE = antes[2]


def test_ficheros_de_usr_parcheados(overlay):
    usr = overlay / "cam/usr"
    for rel in ("lib/libObj.so", "lib/CautionConfig.so", "lib/viewUnified2.so"):
        assert (usr / rel).read_bytes() != (O.USR / rel).read_bytes(), rel
    assert len((usr / "lib/libObj.so").read_bytes()) >= len((O.USR / "lib/libObj.so").read_bytes())


def test_entradas_de_menu_cfw(overlay):
    txt = (overlay / "cam/usr/share/app/string_english.uxc").read_bytes()
    assert b"CFW" in txt
    for a in O.cfw_ajustes.AJUSTES:
        assert a.label.encode() in txt, a.label
        for t, _ in a.opciones:
            assert t.encode() in txt, (a.label, t)


def test_avcam_junto_al_overlay_es_cargable_y_distinto_del_de_fabrica(overlay):
    import avcam_fuente
    av = avcam_fuente.avcam_de(Path(str(overlay) + ".nflasha3"))
    stock = (ROOT / "analysis/rea-independent/input/av-cam.bin").read_bytes()
    assert len(av) == len(stock) and av != stock
    for modulo in (O.bulb_timer_patch, O.jpeg_hook_patch):   # cuevas de G55/G65 con el código escrito
        assert any(av[modulo.CAVE - 0x43541000:modulo.CAVE - 0x43541000 + 8])


def test_cada_parche_de_libobj_y_cautionconfig_conserva_sus_bytes_en_el_conjunto(overlay):
    """El encadenado no pisa a nadie: los bytes que cambia cada parche solo sobre Sony son los mismos en el fichero final."""
    usr = overlay / "cam/usr"
    for rel, parches in (("lib/libObj.so", O.LIBOBJ), ("lib/CautionConfig.so", O.CAUTION)):
        final = (usr / rel).read_bytes()
        if rel.endswith("libObj.so"):                      # libObj no cambia de tamaño con ningún parche
            base = (O.USR / rel).read_bytes()
            for p in parches:
                solo = p(base)
                dif = [i for i, (a, b) in enumerate(zip(base, solo, strict=False)) if a != b]
                assert dif and all(final[i] == solo[i] for i in dif), p.__module__
        else:
            assert len(final) >= len((O.USR / rel).read_bytes())


def test_cueva_sq_y_drp_funcionan_sobre_el_libobj_del_conjunto(overlay):
    sys.path.insert(0, str(ROOT / "tests"))
    import test_g76_sq_libobj as T
    img = (overlay / "cam/usr/lib/libObj.so").read_bytes()
    ev, est, _ = T._emula(img, {O.cfw_ajustes.POR_ID["sq"].backup: 1})
    assert [e[3] for e in ev if e[0] == "p"] == [0x206, 0x3E2, 1, 0, 1]
    assert est["llego"][:4] == (0x111, 0x222, 0x333, 0x444)
    msgs = O.drp_patch.emular(img, {O.cfw_ajustes.POR_ID["dr_prior"].backup: 2})["msgs"]
    assert msgs and msgs[0][2] == O.drp_patch.DRO_LV5
