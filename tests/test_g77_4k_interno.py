"""G77 — 4K interno: el codificador MP4/XAVC S de av-cam 3.21 no tiene configuración 3840×2160; sí hay piezas 4K comunes (decodificación, redimensionado, EE)."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
AVCAM = ROOT / "analysis/rea-independent/input/av-cam.bin"
SABIN = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/sabin"


@pytest.mark.skipif(not AVCAM.exists(), reason="av-cam.bin no disponible")
def test_codificador_sin_3840x2160():
    d = AVCAM.read_bytes()
    tam = {m.group(1).decode() for m in re.finditer(rb"\[EXCDCENCMP\]\[(\d+x\d+) +\d+[ipP]\]\[ActEnc\]", d)}
    assert tam == {"1920x1080", "1440x1080", "1280x720", "640x480", "800x480"}
    assert b"ExCodecDecMp4::ActDecXAvcSMp4_30p_3840_2160" in d          # 4K solo en decodificación
    assert b"vfx_4k_movie_prm_gen" in d and b"4K EE PIN" in d


@pytest.mark.skipif(not SABIN.exists(), reason="extracción no disponible")
def test_filtros_de_redimensionado_4k_en_usr():
    assert all((SABIN / f"spica_musashi_mov_4k_{c}_tap_step{n}.bin").exists() for c in "yc" for n in (1, 2))
