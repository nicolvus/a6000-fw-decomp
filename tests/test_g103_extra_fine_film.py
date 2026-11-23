"""G103 — «Extra fine» (G39) en el CFW Film + PP (3.92): comprobación teórica de punta a punta sin cámara.
Menú/Fn (ficheros `/usr` reales de `build_cfw_film.build_files`, en un directorio temporal: no construye el paquete), `libObj` y núcleo (av-cam en la LIRO VM)."""
import io
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts/gui"), str(ROOT / "scripts"), str(ROOT / "references/fwtool"), str(ROOT / "tests")]
import quality_exfine_patch as Q

LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib"
AVCAM_338 = ROOT / "analysis/e25-27/artifacts-338/av-cam.integrated.bin"
B = 0x43541000
# camino de la calidad JPEG en av-cam (G75 T19): ConvertQualityForBKID y lector de BKID, manejador de 0x4036, tabla de BKID por calidad, tabla de órdenes
CAMINO_AVCAM = ((0x437F8204, 0x437F8320), (0x4380394C, 0x43803A50), (0x43FFAC44, 0x43FFACA4), (0x43FFF564, 0x43FFF964))
NODOS_DEFAULT = ["RAW", "RAW_JPEG", "ExtraFine", "Fine", "Standard"]
pytestmark = pytest.mark.skipif(not (LIB / "CautionConfig.so").is_file(), reason="fw321 extraído no disponible")


@pytest.fixture(scope="module")
def usr(tmp_path_factory) -> Path:
    """`/usr` parcheado del 3.92 (`build_files(pp=True)`) en un subproceso: la especificación del menú es global."""
    out = tmp_path_factory.mktemp("f392")
    code = f"import sys; sys.path.insert(0, 'scripts/gui'); import build_cfw_film as F; F.build_files(__import__('pathlib').Path({str(out)!r}), F.LOOKS, pp=True)"
    subprocess.run([sys.executable, "-c", code], cwd=ROOT, check=True, capture_output=True)
    return out / "files/lib"


def _elf(d: bytes):
    """(GOT, {offset: símbolo de su reubicación}, {símbolo: (va, tamaño)}, lector por va)."""
    from elftools.elf.elffile import ELFFile
    from elftools.elf.relocation import RelocationSection
    e = ELFFile(io.BytesIO(d))
    got = next(t.entry.d_ptr for t in e.get_section_by_name(".dynamic").iter_tags() if t.entry.d_tag == "DT_PLTGOT")  # type: ignore[union-attr]
    rel = {r["r_offset"]: e.get_section(s["sh_link"]).get_symbol(r["r_info_sym"]).name  # type: ignore[attr-defined]
           for s in e.iter_sections() if isinstance(s, RelocationSection) for r in s.iter_relocations() if r["r_info_sym"]}
    syms = {s.name: (s["st_value"], s["st_size"]) for s in e.get_section_by_name(".dynsym").iter_symbols()}  # type: ignore[union-attr]
    segs = [(g["p_vaddr"], g["p_offset"], g["p_filesz"]) for g in e.iter_segments() if g["p_type"] == "PT_LOAD"]
    rd = lambda va, n=4: next(d[o + va - v:o + va - v + n] for v, o, sz in segs if v <= va < v + sz)
    return got, rel, syms, rd


def test_calidad_del_392_usa_la_lista_default_con_extra_fine(usr):
    pytest.importorskip("elftools")
    orig, nuevo = (LIB / "CautionConfig.so").read_bytes(), (usr / "CautionConfig.so").read_bytes()
    got, rel, syms, rd = _elf(nuevo)
    lits = struct.unpack_from("<II", nuevo, Q.LIT_T)
    assert [rel[got + x] for x in lits] == ["cmnViewSettingNodesStlImageQualityDefault", "cmnViewSettingNodesNumOfStlImageQualityDefault"]
    va = syms["cmnViewSettingNodesStlImageQualityDefault"][0]
    n = struct.unpack("<I", rd(syms["cmnViewSettingNodesNumOfStlImageQualityDefault"][0]))[0]
    assert [rel[va + 4 * i] for i in range(n)] == [f"cmnViewSettingNodeStlImageQuality{k}" for k in NODOS_DEFAULT]
    p, sz = syms["cmnViewSettingPropertyListStlImageQualityExtraFine"]
    props = {a: v for a, _, v in struct.iter_unpack("<III", rd(p, sz)[:sz // 12 * 12])}
    assert (props[0xF], props[0x10]) == (2, 2)          # id de proceso 2 → WRAPPER_IMAGE_QUALITY 3 = JPG_QUALITY_EXFINE (G39 §1)
    a, b = syms["_ZN33CmnViewSettingNodeStlImageQuality11_getSubNodeEv"][0] & ~1, Q.LIT_N + 4
    assert [i for i in range(a, b) if orig[i] != nuevo[i]] == [Q.LIT_T, Q.LIT_T + 1, Q.LIT_N, Q.LIT_N + 1]   # nada más del CFW toca _getSubNode


def test_menu_fn_y_rueda_comparten_el_nodo_de_calidad(usr):
    """Una sola clase `CmnViewSettingNodeStlImageQuality` y un solo nodo raíz, importado por el menú (vu2), el menú Fn (vu4) y vu7: el parche cubre las tres listas."""
    pytest.importorskip("elftools")
    _, _, syms, _ = _elf((usr / "CautionConfig.so").read_bytes())
    assert [k for k in syms if k.startswith("_ZN") and "getSubNode" in k and "ImageQuality" in k] == ["_ZN33CmnViewSettingNodeStlImageQuality11_getSubNodeEv"]
    for so in ("viewUnified2", "viewUnified4", "viewUnified7"):
        s = _elf((usr / f"{so}.so").read_bytes())[2]
        assert s["cmnViewSettingNodeRootStlImageQuality"][0] == 0, so      # importado (UND)


def test_libobj_del_392_no_toca_la_orden_de_calidad(usr):
    """Diferencias de `libObj` = solo PP (validador, CamMsgConv, eco PP) y eco de Silent; ninguna junto al constructor de `0x4036` (movw #0x4036 en 0x97f49c)."""
    o, n = (LIB / "libObj.so").read_bytes(), (usr / "libObj.so").read_bytes()
    assert o[0x97F49C:0x97F49F] == bytes.fromhex("44f236")
    assert not [i for i in range(0x97F000, 0x980000) if o[i] != n[i]]


@pytest.fixture(scope="module")
def nucleo(tmp_path_factory) -> tuple[Path, bytes]:
    if not AVCAM_338.is_file():
        pytest.skip("av-cam del 3.38 ausente")
    pytest.importorskip("keystone")
    import build_cfw_film
    from g22 import patch_tristate as P
    tri = P.apply_bytes(AVCAM_338.read_bytes())[0]
    f = tmp_path_factory.mktemp("nucleo") / "av-cam.392.bin"
    f.write_bytes(build_cfw_film.bionz_pp(tri))
    return f, tri


def test_nucleo_del_392_no_toca_el_camino_de_calidad(nucleo):
    f, tri = nucleo
    c = f.read_bytes()
    for lo, hi in CAMINO_AVCAM:
        assert tri[lo - B:hi - B] == c[lo - B:hi - B], hex(lo)


@pytest.mark.parametrize(("valor", "nombre"), [(2, "Extrafina"), (1, "Fina")])
def test_av_cam_del_392_acepta_extra_fine(nucleo, monkeypatch, valor, nombre):
    """La orden real del menú (`0x4036`, byte 10 = 2, medida en el arnés en G75 T19) sobre el av-cam del 3.92 en la LIRO VM: la guarda y contesta `0xf000`."""
    import test_avcam_ee_start as T  # añade scripts/gui/avcam al path
    L = pytest.importorskip("liro_vm")
    monkeypatch.setattr(L, "AVCAM", nucleo[0])
    T.test_av_cam_acepta_la_calidad_jpeg_de_la_orden_0x4036(valor, nombre)
