"""G69 — efecto de «Color Chrome / Film» sobre una foto de referencia con el ISP emulado (g23): suma las filas de `color_chrome_patch.FILAS` a Saturación y Color Depth.
El ISP modela Color Depth con pesos por tono APROX (`PASO_DEPTH`, sin calibrar contra la cámara): sirve para ver la dirección del efecto, no la magnitud real.
uso: demo_isp.py ARW SALIDA.png"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts/gui/isp"), str(ROOT / "scripts/gui"), str(ROOT / "scripts/g69")]
import color_chrome_patch as C
import compara_real as R
import modelo as M

NOMBRES = ("Off", "Débil", "Fuerte", "Clásico", "Vivo", "Suave")
CLAVES = ("cd_r", "cd_y", "cd_g", "cd_c", "cd_b", "cd_m")          # orden del paquete 0x2a…0x2f


def parametros(fila) -> dict:
    return {"gamma": 5, "saturation": fila[0], **{c: v for c, v in zip(CLAVES, fila[1:])}}


def main(arw: Path, out: Path) -> None:
    lin, _, _ = R.lee_arw(arw)
    t = M.Tablas()
    w, tiras = 480, []
    for n, fila in zip(NOMBRES, C.FILAS):
        img = np.clip(M.aplica(lin, parametros(fila), t, True, 1.0, True), 0, 1)
        hsv = np.array(Image.fromarray((img * 255).astype(np.uint8)).convert("HSV"), float) / 255
        print(f"{n}: saturación media {hsv[..., 1].mean():.3f}  valor medio {hsv[..., 2].mean():.3f}  luma {img.mean():.3f}")
        a = Image.fromarray((img * 255).astype(np.uint8))
        tiras.append(a.resize((w, int(a.height * w / a.width)), Image.BOX))
    h = max(x.height for x in tiras)
    lienzo = Image.new("RGB", (w * 3, h * 2))
    for i, x in enumerate(tiras):
        lienzo.paste(x, ((i % 3) * w, (i // 3) * h))
    lienzo.save(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
