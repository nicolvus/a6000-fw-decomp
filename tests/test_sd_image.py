import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "gui" / "harness"))
import sd_image  # noqa: E402


def mdir(img: Path, ruta: str) -> str:
    return subprocess.run(["mdir", "-i", str(img), f"::{ruta}"], capture_output=True, text=True, env={"MTOOLS_SKIP_CHECK": "1", "PATH": "/usr/bin"}).stdout


def test_imagen_fat32_con_estructura_a6000(tmp_path):
    raiz = tmp_path / "sd"
    (raiz / "DCIM" / "100MSDCF").mkdir(parents=True)
    (raiz / "DCIM" / "100MSDCF" / "DSC00001.JPG").write_bytes(b"\xff\xd8x" * 1000)
    cab = tmp_path / "sd.head"
    sect = sd_image.construye(raiz, cab, 1.0)
    assert sect == (1 << 30) // 512
    datos = cab.read_bytes()
    assert 0 < len(datos) < 64 << 20  # solo la cabeza: FAT, directorios y la foto
    assert datos[0x52:0x5a] == b"FAT32   " and datos[510:512] == b"\x55\xaa"  # FAT32 sin MBR
    assert datos[0x47:0x52].strip() == sd_image.ETIQUETA.encode()
    img = tmp_path / "cab.img"
    img.write_bytes(datos)
    for c in ("DCIM", "PRIVATE", "PRIVATE/M4ROOT/CLIP"):
        assert "Directory" in mdir(img, c) or "Volume" in mdir(img, c), c
    assert "DSC00001" in mdir(img, "DCIM/100MSDCF")
