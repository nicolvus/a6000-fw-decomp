"""G68 — efecto de «DR Prioridad» sobre una foto de referencia con el ISP emulado (g23): exposición −1/−2 EV (el sensor recibe 2^-n; k = 1/2^n) frente a la misma
escena con la ganancia global de recuperación de sombras (aproximación del DRO: k = 1 → como disparada). NO modela el DRO real (g23 §4.2, sin algoritmo estático).
uso: demo_isp.py ARW SALIDA.png"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "scripts/gui/isp"), str(ROOT / "scripts/gui")]
import compara_real as C
import modelo as M


def main(arw: Path, out: Path) -> None:
    lin, _, meta = C.lee_arw(arw)
    t = M.Tablas()
    p = {"gamma": 5}
    k0 = 1.0
    filas = []
    for etiqueta, ev, k in (("Off (k=1)", 0, k0), ("Debil -1 EV, sin recuperar", 1, k0 / 2), ("Fuerte -2 EV, sin recuperar", 2, k0 / 4)):
        img = M.aplica(lin, p, t, True, k, True)
        filas.append((etiqueta, np.clip(img, 0, 1)))
        print(f"{etiqueta}: altas luces >=0.98 = {100 * (img >= 0.98).mean():.2f} %  sombras <0.05 = {100 * (img < 0.05).mean():.1f} %  media {img.mean():.3f}")
    print("meta", {k: v for k, v in meta.items() if k in ("dro", "creative_style")}, "saturado en RAW >=0.98:", f"{100 * (lin >= 0.98).mean():.3f} %")
    w = 640
    tiras = []
    for _, im in filas:
        a = Image.fromarray((im * 255).astype(np.uint8))
        tiras.append(a.resize((w, int(a.height * w / a.width)), Image.BOX))
    h = max(x.height for x in tiras)
    lienzo = Image.new("RGB", (w * len(tiras), h))
    for i, x in enumerate(tiras):
        lienzo.paste(x, (i * w, 0))
    lienzo.save(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
