"""G22-B — arnés de la UI: formato de `bk.tbl` (gen_bk.py ↔ `bk_find` del shim) y compilación de `sonyshim.c`."""
from __future__ import annotations

import os
import shutil
import struct
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts/gui/harness"
NVRAM = ROOT / "analysis/camera-dumps/20261105-volcado-total-nvram/backup_flash.bin"
CAM_LIB = ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha7_unpacked_unpacked/lib"
WORK = Path(os.environ.get("A6000_HARNESS_WORK", ROOT / "analysis/gui/g22/harness"))


def bk_find(tbl: bytes, wanted: int) -> bytes | None:
    """Mismo recorrido que `bk_find()` en sonyshim.c: registros {id u32, len u32, datos rellenados a 4}."""
    o = 0
    while o + 8 <= len(tbl):
        i, n = struct.unpack_from("<II", tbl, o)
        if i == wanted:
            return tbl[o + 8:o + 8 + n]
        o += 8 + ((n + 3) & ~3)
    return None


def bk_u32(tbl: bytes, wanted: int) -> int:
    d = bk_find(tbl, wanted)
    assert d is not None and len(d) == 4, hex(wanted)
    return struct.unpack("<I", d)[0]


@pytest.mark.skipif(not NVRAM.exists(), reason="volcado NVRAM no disponible")
def test_gen_bk_sirve_la_zona_mwf(tmp_path: Path) -> None:
    out = tmp_path / "bk.tbl"
    subprocess.run([sys.executable, str(HARNESS / "gen_bk.py"), str(NVRAM), str(out)], check=True)
    tbl = out.read_bytes()
    # Valores que libObj pide al servicio 0x3e014d al arrancar (G22-B avance 5): base física y tamaño de la zona fija MWF.
    assert bk_u32(tbl, 0xFA0028) == 0x82DF9000
    assert bk_u32(tbl, 0xFA005D) == 0x7C000
    assert bk_find(tbl, 0xFFFFFFFF) is None


@pytest.mark.skipif(not (shutil.which("clang") and CAM_LIB.exists() and (WORK / "sysroot/usr/include/arm-linux-gnueabihf").is_dir()),
                    reason="clang, rootfs de la cámara o sysroot Debian (setup.sh) no disponibles")
def test_shim_compila_y_exporta_los_ganchos(tmp_path: Path) -> None:
    so = tmp_path / "sonyshim.so"
    subprocess.run(["sh", str(HARNESS / "shim/build.sh"), str(WORK / "sysroot"), str(CAM_LIB), str(so)], check=True)
    syms = subprocess.run(["readelf", "--dyn-syms", "-W", str(so)], capture_output=True, text=True, check=True).stdout
    for hook in ("open", "open64", "ioctl", "mmap", "fopen", "dlopen", "pthread_cond_wait", "munmap", "abort"):
        assert f" {hook}\n" in syms or f" {hook}@" in syms, hook
