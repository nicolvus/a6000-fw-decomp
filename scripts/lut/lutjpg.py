"""G91 — `.cube` 3D COMPLETO (17³/33³/65³…) aplicado por software a los JPEG, en la cámara.

El ISP solo admite 5×9×9 (G90 §C, geometría fija). Esta es la vía sin ese límite, solo foto:
`userland/lutjpg.c` (libjpeg-turbo estática + musl, binario ARMv7 Cortex-A5 sin NEON) lee el JPEG de
`/android/mnt/sdcard` (FUSE de Sony, POSIX), interpola tetraédricamente cada píxel y escribe otro JPEG
(EXIF y submuestreo conservados; el APP2 MPF se omite). No toca firmware ni `av-cam`.

Compilar: necesita zig (`LUTJPG_ZIG`, por defecto `zig` del PATH o ~/.local/opt/zig-*) y libjpeg-turbo
estática para `arm-linux-musleabihf` (`LUTJPG_JPEG`, por defecto ~/.local/arm-jpeg con include/ y lib/).
`python3 lutjpg.py` = compila en `build/lutjpg/lutjpg` y se comprueba con qemu-arm contra la referencia.
"""
from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).parent / "userland/lutjpg.c"
SALIDA = ROOT / "build/lutjpg/lutjpg"
# Cortex-A5 de la cámara (CPU part 0xc05): VFPv4-D16, sin NEON (/proc/cpuinfo de los volcados)
CPU = "cortex_a5-neon-d32"


def _zig() -> str | None:
    cand = [os.environ.get("LUTJPG_ZIG"), shutil.which("zig"), *sorted(glob.glob(os.path.expanduser("~/.local/opt/zig-*/zig")))]
    return next((c for c in cand if c and Path(c).exists()), None)


def _jpeg() -> Path:
    return Path(os.environ.get("LUTJPG_JPEG", os.path.expanduser("~/.local/arm-jpeg")))


def disponible() -> bool:
    return bool(_zig()) and (_jpeg() / "lib/libjpeg.a").exists() and bool(shutil.which("qemu-arm"))


def compila(destino: Path = SALIDA) -> Path:
    j = _jpeg()
    destino.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([_zig(), "cc", "-target", "arm-linux-musleabihf", f"-mcpu={CPU}", "-O2", "-static", "-s",
                    "-Wall", "-Wextra", "-Werror", f"-I{j / 'include'}", str(SRC), str(j / "lib/libjpeg.a"),
                    "-o", str(destino)], check=True)
    return destino


def ejecuta(cube: Path, ent: Path, sal: Path, q: int = 98, binario: Path = SALIDA) -> subprocess.CompletedProcess:
    return subprocess.run(["qemu-arm", str(binario), "-q", str(q), str(cube), str(ent), str(sal)], capture_output=True, text=True, check=False)


def tetra(tab: np.ndarray, lo, hi, x: np.ndarray) -> np.ndarray:
    """Referencia flotante. tab [n,n,n,3] índice [r,g,b] (cube_a6000.lee_cube); x [...,3] en 0…1."""
    n = tab.shape[0]
    u = np.clip((x - lo) / (hi - lo), 0, 1) * (n - 1)
    i = np.minimum(u.astype(int), n - 2)
    f = u - i
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    v = lambda dr, dg, db: tab[i[..., 0] + dr, i[..., 1] + dg, i[..., 2] + db]
    # 6 tetraedros: orden de las fracciones → vértices intermedios
    casos = [((r >= g) & (g >= b), (1, 0, 0), (1, 1, 0), r, g, b),
             ((r >= g) & (g < b) & (r >= b), (1, 0, 0), (1, 0, 1), r, b, g),
             ((r >= g) & (b > r), (0, 0, 1), (1, 0, 1), b, r, g),
             ((r < g) & (b > g), (0, 0, 1), (0, 1, 1), b, g, r),
             ((r < g) & (b <= g) & (b > r), (0, 1, 0), (0, 1, 1), g, b, r),
             ((r < g) & (b <= r), (0, 1, 0), (1, 1, 0), g, r, b)]
    out = np.zeros(x.shape)
    for m, a1, a2, p, s, t in casos:
        o = (1 - p)[..., None] * v(0, 0, 0) + (p - s)[..., None] * v(*a1) + (s - t)[..., None] * v(*a2) + t[..., None] * v(1, 1, 1)
        out[m] = o[m]
    return out


def main() -> int:
    sys.path.insert(0, str(Path(__file__).parent))
    import tempfile

    import cube_a6000 as C
    from PIL import Image
    if not disponible():
        print("falta zig, libjpeg-turbo ARM o qemu-arm (ver docstring)")
        return 1
    b = compila()
    print(f"{b}: {b.stat().st_size} B")
    jpg = ROOT / "analysis/camera-dumps/20261117-traza-S5/DSC03986.JPG"
    with tempfile.TemporaryDirectory() as d:
        cube, sal = Path(d) / "p.cube", Path(d) / "o.jpg"
        C.escribe_cube(cube, C.lut_pelicula, 65, "pelicula")
        r = ejecuta(cube, jpg, sal, q=100)
        print(r.returncode, r.stderr.strip())
        x = np.asarray(Image.open(jpg).convert("RGB"), float)[::8, ::8] / 255
        y = np.asarray(Image.open(sal).convert("RGB"), float)[::8, ::8] / 255
        ref = tetra(*C.lee_cube(cube), x)
        e = C.de2000(ref.reshape(-1, 3), y.reshape(-1, 3))
        print(f"65³ película, ΔE2000 medio {e.mean():.3f} p95 {np.percentile(e, 95):.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
