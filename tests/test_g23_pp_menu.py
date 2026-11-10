"""G23: menú completo de Picture Profile — árbol de nodos de datos y descriptores (offline, sobre los .so de Sony)."""
from __future__ import annotations

import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/gui"))
import add_menu_entry as A
import build_pp_menu as B
import pp_descriptors as D
import pp_menu_spec as M

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
needs = pytest.mark.skipif(not (LIB / "CautionConfig.so").is_file(), reason="biblioteca de Sony ausente")


def test_spec_coherente():
    assert len(M.SETTINGS) == len(M.PIDS) == len(set(M.PIDS))
    assert M.SETTINGS["gamma"].clave == 0x214 and M.SETTINGS["sel"].clave == 0x274 and M.SETTINGS["saturation"].clave == 0x26C
    assert [M.SETTINGS[f"cd_{c}"].clave for c in "rgbcmy"] == [0x254, 0x258, 0x25C, 0x260, 0x264, 0x268]
    assert len({(s.clave, s.evento) for s in M.SETTINGS.values()}) == len(M.SETTINGS)    # ninguna (clave, evento) repetida
    

@needs
def test_arbol_y_descriptores(tmp_path):
    txt = B.textos()
    ids = {t: 0xE000 + i for i, t in enumerate(txt)}
    new, delta = B.patch_caution((LIB / "CautionConfig.so").read_bytes(), ids)
    p = tmp_path / "c.so"
    p.write_bytes(new)
    syms = {f[3]: int(f[0], 16) for f in (l.split() for l in subprocess.run(["nm", "-D", str(p)], capture_output=True, text=True).stdout.splitlines()) if len(f) == 3 for f in [[f[0], "", "", f[2]]]}
    segs = A._segments(new)
    rd = lambda va, n=1: struct.unpack_from(f"<{n}I", new, A._off(segs, va))
    roots, cnt = [], {"carpeta": 0, "pagina": 0, "opcion": 0}

    def walk(n):
        kids, c = rd(n + 4, 2)
        lst, pc = rd(rd(n + 12)[0], 2)
        pr = {t[0]: t[2] for t in (rd(lst + 12 * i, 3) for i in range(pc))}
        if 0xE in pr:
            roots.append((pr[0xE], c))
        elif pr.get(0xC) == 3:
            cnt["carpeta"] += 1
        elif pr.get(0xC) == 1:
            cnt["opcion"] += 1
            return
        else:
            cnt["pagina"] += 1
        for k in rd(kids, c):
            walk(k)

    walk(syms["cmnViewSettingNodeRootAelWShutter"] + delta)
    assert len(roots) == len(M.SETTINGS) and cnt == {"carpeta": 9, "pagina": 10, "opcion": sum(len(s.opciones) for s in M.SETTINGS.values())}
    assert dict(roots) == {M.PIDS[i]: len(s.opciones) for i, s in enumerate(M.SETTINGS.values())}

    ajustes = [D.Ajuste(M.PIDS_PRESTADOS[i], s.clave, tuple(v for _, v in s.opciones)) for i, s in enumerate(M.SETTINGS.values())]
    pm = D.patch((LIB / "cmn_view_processDataMgr.so").read_bytes(), ajustes)
    ps = A._segments(pm)
    prd = lambda va, n=1: struct.unpack_from(f"<{n}I", pm, A._off(ps, va))
    for a in ajustes:
        desc = prd(prd(D.TABLA_D + 4 * a.pid)[0], D.DESC_PALABRAS)
        m = prd(desc[6], D.MODEL_PALABRAS)
        assert desc[7] == 1 and desc[5] >> 8 & 0xFF == len(a.valores) and m[2:4] == (a.evento, 0x49)
        assert prd(m[4])[0] == a.clave and prd(m[5])[0] == a.clave + 2
        assert tuple(struct.unpack("<i", struct.pack("<I", x))[0] for x in prd(m[7], len(a.valores))) == a.valores


@needs
def test_parche_libobj_saturacion_solo_cambia_seis_bytes():
    import patch_libobj_pp as P

    old = (LIB / "libObj.so").read_bytes()
    new = P.patch(old)
    diff = [i for i in range(len(old)) if old[i] != new[i]]
    assert len(new) == len(old) and 0 < len(diff) <= 6 and A._off(A._segments(old), P.VA) <= diff[0]
    assert new[A._off(A._segments(old), P.VA):][:6] == P.NUEVO


def test_copy_usa_evento_41_y_clave_del_selector():
    s = M.SETTINGS["copy"]
    assert (s.evento, s.clave, [v for _, v in s.opciones]) == (0x41, 0x274, list(range(9)))


def test_sin_copy_reset_el_menu_no_usa_los_eventos_41_42():
    """G27: la `libObj` sin `patch_actions` rechaza 0x41/0x42; el menú por defecto no debe ofrecerlos (subproceso: muta la spec)."""
    code = ("import sys; sys.path.insert(0, 'scripts/gui'); import build_pp_menu as B, pp_menu_spec as M; B.sin_acciones(); "
            "assert {s.evento for s in M.SETTINGS.values()} == {0x40} and 'Copy' not in B.textos() and 'Reset' not in B.textos(); "
            "assert M.TREE[2][0][:2] == ['sel', 'gamma']")
    assert subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=False).returncode == 0


def test_color_mode_level_clave_1_rango_del_validador():
    """G27: Color Mode Level = clave K(1), opciones 1…8 (lo que acepta el caso 1 de `pvt_ChangePictureProfileParamApp2Obj`), en la página de Color Mode."""
    s = M.SETTINGS["color_level"]
    assert (s.clave, s.evento, [v for _, v in s.opciones]) == (0x1FC, 0x40, list(range(1, 9)))
    assert M.PIDS[list(M.SETTINGS).index("color_level")] == 0xE9 + 33 and len(set(M.PIDS)) == len(M.PIDS) and min(M.PIDS) >= 0xE9
    assert M.TREE[2][1][:3] == ["color_mode", "color_level", "saturation"]
    if not (LIB / "libObj.so").is_file():
        return
    sys.path.insert(0, str(ROOT / "tests"))
    from test_g25_gamma_libobj import APP2OBJ_FN, call
    d = (LIB / "libObj.so").read_bytes()
    assert [v for v in range(-20, 21) if call(d, APP2OBJ_FN, 1, v)[0] == 1] == list(range(1, 9))
