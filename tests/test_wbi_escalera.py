"""Escalera SSBI: el empaquetador sólo acepta una WBI1 sellada por la cámara (vector _ssboot)."""
import importlib.util
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _builder():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("bpwp", ROOT / "scripts/gui/build_package_wbi_propio.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _imagen(firma: bytes, vector: int, nsec: int = 2, rdata: int = 0x400) -> bytes:
    cab = struct.pack("<4s10I", firma, nsec, 9, vector, 0x20060224, 0x200, rdata, 0, 0, 0x0F0F0F0F, 0x1000)
    return cab.ljust(0x40000, b"\0") + b"\x11" * rdata + b"\x22" * (32 * nsec) + b"\xff" * 4096


@pytest.mark.parametrize("firma,vector", [(b"prof", 0x800523A4), (b"WBI1", 0x800523A4), (b"WBI0", 0x800523B4),
                                          (b"prof", 0x800523AC)])
def test_rechaza_imagen_no_sellada(firma, vector):
    with pytest.raises(ValueError):
        _builder().wbi_member(_imagen(firma, vector))


def test_acepta_wbi1_sellada_y_recorta():
    img = _imagen(b"WBI1", 0x800523BC)
    out = _builder().wbi_member(img)
    assert out == img[:0x40000 + 0x400 + 2 * 32]


def test_kemco_memclr_misma_longitud():
    mod = _builder()
    txt = b"pm.resume=0x80021054 pm.sus_error=0x80021060\nwbi_memclr=0x800210e8\nwbimem=0x1000@0x80021000\n"
    out = mod.kemco_memclr(txt)
    assert len(out) == len(txt) and b"wbi_memclr=0x8029fdc8\n" in out and b"0x800210e8" not in out
    with pytest.raises(ValueError):
        mod.kemco_memclr(out)


def test_palabra_memclr_vale_1_en_kernel_y_ram():
    vml = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin"
    cfw = ROOT / "analysis/camera-dumps/20261127-wbi-nflasha5/dev_nflasha5.bin"
    if not (vml.exists() and cfw.exists()):
        pytest.skip("requiere firmware extracted y volcados no versionados")
    sys.path.insert(0, str(ROOT / "scripts/wbi"))
    from snapram import Ram
    pa = _builder().MEMCLR_UNO
    off = pa - 0x80038000  # Loader3 carga vmlinux.bin en crudo en 0x80038000 (RAMCFG entrada 5)
    pagina = vml.read_bytes()[off & ~4095:(off & ~4095) + 4096]
    assert struct.unpack_from("<I", pagina, off & 4095)[0] == 1
    for p in (cfw, ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5"):
        assert Ram(p).read((pa & ~4095) - 0x40000000, 4096) == pagina


def test_escalera_en_imagenes_reales():
    sony = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha5"
    cfw = ROOT / "analysis/camera-dumps/20261127-wbi-nflasha5/dev_nflasha5.bin"
    if not (sony.exists() and cfw.exists()):
        pytest.skip("requiere firmware extracted y volcados no versionados")
    sys.path.insert(0, str(ROOT / "scripts/wbi"))
    import escalera
    import upm_modulo
    from snapram import Ram
    esperado = {0x800523A4: 1, 0x800523AC: 2, 0x800523B4: 3, 0x800523BC: 4}
    for p in (sony, cfw):
        r = Ram(p)
        assert escalera.entradas(r) == esperado
        assert not escalera.valida_loader3(p.read_bytes())[1]
        base, pr = upm_modulo.localiza(r, upm_modulo.texto_ko())
        assert base == 0x3F326000
        reg = struct.unpack("<4I", upm_modulo.lee_va(r, pr, base + upm_modulo.TEXT_A_GOFF + 4, 16))
        assert reg == ((0x920141, 0x27, 0x1C, 0x20) if p == sony else (0x920141, 7, 0x1B, 0x1F))
