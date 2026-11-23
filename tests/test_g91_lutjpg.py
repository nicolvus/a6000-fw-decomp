"""G91 — `.cube` completo aplicado por software al JPEG (binario ARM real bajo qemu-arm)."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lut"))
import cube_a6000 as C
import lutjpg as J

JPG = ROOT / "analysis/camera-dumps/20261117-traza-S5/DSC03986.JPG"
pytestmark = pytest.mark.skipif(not J.disponible(), reason="falta zig / libjpeg-turbo ARM / qemu-arm")


@pytest.fixture(scope="module")
def binario(tmp_path_factory):
    return J.compila(tmp_path_factory.mktemp("b") / "lutjpg")


@pytest.fixture(scope="module")
def recorte(tmp_path_factory):
    d = tmp_path_factory.mktemp("j")
    im = Image.open(JPG)
    exif = im.info["exif"]
    im = im.convert("RGB").crop((2000, 1500, 2480, 1820))
    im.save(d / "c444.jpg", quality=100, subsampling=0, exif=exif)
    im.save(d / "c422.jpg", quality=95, subsampling=1, exif=exif)
    return d


def _rgb(p):
    return np.asarray(Image.open(p).convert("RGB"), float)


@pytest.mark.parametrize("n,f", [(65, C.lut_pelicula), (33, C.lut_teal_orange), (2, lambda x: 1 - x)])
def test_exacto_frente_a_referencia(binario, recorte, tmp_path, n, f):
    """La salida = referencia tetraédrica exacta redondeada y recodificada igual (q100 4:4:4): solo difiere el JPEG."""
    cube = tmp_path / "l.cube"
    C.escribe_cube(cube, f, n, "t")
    r = J.ejecuta(cube, recorte / "c444.jpg", tmp_path / "o.jpg", q=100, binario=binario)
    assert r.returncode == 0, r.stderr
    ref = J.tetra(*C.lee_cube(cube), _rgb(recorte / "c444.jpg") / 255)
    Image.fromarray(np.round(ref * 255).astype(np.uint8)).save(tmp_path / "r.jpg", quality=100, subsampling=0)
    d = np.abs(_rgb(tmp_path / "o.jpg") - _rgb(tmp_path / "r.jpg"))
    # empates de redondeo Q16 frente a float cambian 1 nivel y la DCT lo extiende a su bloque
    assert d.mean() < 0.03 and (d <= 2).mean() > 0.9995


def test_dominio_y_tetra_es_exacto_en_nodos():
    """DOMAIN_MAX = 2 comprime la entrada a la mitad; en los nodos la interpolación devuelve el nodo."""
    n = 9
    tab = np.random.default_rng(1).random((n, n, n, 3))
    g = np.linspace(0, 1, n)
    x = np.stack(np.meshgrid(g, g, g, indexing="ij"), -1)
    assert np.allclose(J.tetra(tab, 0, 1, x), tab)
    assert np.allclose(J.tetra(tab, np.zeros(3), np.full(3, 2.0), x), J.tetra(tab, 0, 1, x / 2))


def test_domain_en_el_binario(binario, recorte, tmp_path):
    cube = tmp_path / "d.cube"
    C.escribe_cube(cube, C.lut_pelicula, 17, "d")
    cube.write_text(cube.read_text().replace("LUT_3D_SIZE 17\n", "LUT_3D_SIZE 17\nDOMAIN_MIN 0 0 0\nDOMAIN_MAX 2 2 2\n"))
    assert J.ejecuta(cube, recorte / "c444.jpg", tmp_path / "o.jpg", q=100, binario=binario).returncode == 0
    ref = J.tetra(*C.lee_cube(cube), _rgb(recorte / "c444.jpg") / 255)
    assert np.abs(_rgb(tmp_path / "o.jpg") - ref * 255).mean() < 1.0


def test_conserva_exif_submuestreo_y_quita_mpf(binario, tmp_path):
    """JPEG real de la cámara (6000×4000, 4:2:2, EXIF + MPF): tamaño, EXIF y 4:2:2 se conservan; sin MPF ni JFIF."""
    cube = tmp_path / "i.cube"
    C.escribe_cube(cube, lambda x: x, 17, "i")
    r = J.ejecuta(cube, JPG, tmp_path / "o.jpg", binario=binario)
    assert r.returncode == 0, r.stderr
    a, b = Image.open(JPG), Image.open(tmp_path / "o.jpg")
    assert b.size == a.size and b.info["exif"] == a.info["exif"] and b.layer == a.layer
    assert "mp" not in b.info and "jfif" not in b.info


@pytest.mark.parametrize("contenido,rc", [("LUT_1D_SIZE 2\n0 0 0\n1 1 1\n", 3), ("LUT_3D_SIZE 2\n0 0 0\n", 3), ("", 3)])
def test_cube_invalido_no_escribe(binario, recorte, tmp_path, contenido, rc):
    cube = tmp_path / "m.cube"
    cube.write_text(contenido)
    assert J.ejecuta(cube, recorte / "c444.jpg", tmp_path / "o.jpg", binario=binario).returncode == rc
    assert not (tmp_path / "o.jpg").exists()


def test_jpeg_corrupto_borra_salida_y_misma_ruta(binario, recorte, tmp_path):
    cube = tmp_path / "i.cube"
    C.escribe_cube(cube, lambda x: x, 2, "i")
    malo = tmp_path / "malo.jpg"
    malo.write_bytes((recorte / "c444.jpg").read_bytes()[:4000])
    r = J.ejecuta(cube, malo, tmp_path / "o.jpg", binario=binario)
    assert r.returncode != 0 or Image.open(tmp_path / "o.jpg").size        # libjpeg avisa (truncado) sin abortar
    malo.write_bytes(b"\xff\xd8no es jpeg")
    assert J.ejecuta(cube, malo, tmp_path / "o2.jpg", binario=binario).returncode == 5
    assert not (tmp_path / "o2.jpg").exists()
    assert J.ejecuta(cube, malo, malo, binario=binario).returncode == 2


def test_binario_es_arm_estatico_sin_neon(binario):
    out = subprocess.run(["readelf", "-hlA", str(binario)], capture_output=True, text=True, check=True).stdout
    assert "ARM" in out and "INTERP" not in out and "NEON" not in out.split("Attribute Section")[-1]


def test_de2000_pares_de_sharma(monkeypatch):
    """Regresión: ΔC usaba C2 en vez de C2' (idénticos daban ΔE ≠ 0). Pares de Sharma, Wu y Dalal (2005)."""
    monkeypatch.setattr(C, "a_lab", lambda x: np.asarray(x, float))
    pares = [((50, 2.6772, -79.7751), (50, 0, -82.7485), 2.0425), ((50, 0, 0), (50, -1, 2), 2.3669),
             ((50, 2.5, 0), (73, 25, -18), 27.1492), ((2.0776, 0.0795, -1.135), (0.9033, -0.0636, -0.5514), 0.9082)]
    a, b, e = (np.array(v, float) for v in zip(*pares))
    assert np.allclose(C.de2000(a, b), e, atol=1e-4)
    assert np.allclose(C.de2000(a, a), 0)
