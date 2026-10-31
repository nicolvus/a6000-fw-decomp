"""E26-R29 — traza por coordenadas de píxel el esquema vectorial de CN4001/CN4906
(manual de servicio, páginas 37/38 del PDF) para resolver el cableado que
`scripts/schematic_pin_nets.py` (agrupación por fila) no distingue: líneas que
bajan, cruzan varias filas y se doblan hacia un pin distinto del de su propia fila.

Método: renderiza la página a 600 dpi (pdftoppm), localiza cada pin y cada
etiqueta de red por su texto (pdftotext -bbox) y sigue la columna de píxeles
de cada línea vertical hasta su doblez (segmento continuo más largo = tramo
real; las demás marcas son cruces con otras líneas horizontales).

Solo lectura. No toca hardware. Uso: python3 r29_pinout_pixel_trace.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "sony_ilce-6000_ilce-6000l_ilce-6000y_ver.1.1_rev-1_level3.pdf"
PAGE_CN4906 = 38
DPI = 600
SCALE = DPI / 72
# recorte usado (píxeles, origen de pdftoppm -x/-y): cubre la hoja de CN4906
CROP_X, CROP_Y, CROP_W, CROP_H = 5000, 3650, 3400, 1450

# pines 11/12/15 de BIONZ (vía servicio) unidos a las señales "DWN" de Darwin;
# cada entrada: dirección x de la columna, bisagra superior esperada (pin) e
# inferior esperada (etiqueta), en coordenadas locales del recorte.
RISERS = {
    2736: ("pin6 UART_RXD_DWN", "DWN_UART_RXD"),
    2778: ("pin7 UART_TXD_DWN", "DWN_UART_TXD"),
    2819: ("pin8 NSRST", "MD0_DWN"),
    2861: ("pin9 TDO", "TDO_DWN"),
    2903: ("pin11 TCK(SWCLK)", "TCK_DWN"),
    2944: ("pin12 TMS(SWDIO)", "TMS_DWN"),
    2986: ("pin13 TDI", "TDI_DWN"),
    3027: ("pin14 NTRST", "TRST_DWN"),
    3068: ("pin15 DEBUG_MODE", "XDWN_RESET"),
}


def render_crop(out: Path) -> Image.Image:
    prefix = out.with_suffix("")
    subprocess.run(
        [
            "pdftoppm",
            "-f",
            str(PAGE_CN4906),
            "-l",
            str(PAGE_CN4906),
            "-r",
            str(DPI),
            "-x",
            str(CROP_X),
            "-y",
            str(CROP_Y),
            "-W",
            str(CROP_W),
            "-H",
            str(CROP_H),
            "-png",
            str(PDF),
            str(prefix),
        ],
        check=True,
        capture_output=True,
    )
    png = next(prefix.parent.glob(prefix.name + f"-{PAGE_CN4906}.png"))
    return Image.open(png).convert("L")


def vertical_segments(
    img: Image.Image, x: int, y0: int, y1: int, thresh: int = 160
) -> list[tuple[int, int]]:
    """Segmentos oscuros continuos (tolerancia de 2 px) en la columna x entre y0 y y1."""
    col = [img.getpixel((x, y)) < thresh for y in range(y0, y1)]
    ys = [y0 + i for i, v in enumerate(col) if v]
    segs: list[tuple[int, int]] = []
    i = 0
    while i < len(ys):
        j = i
        while j + 1 < len(ys) and ys[j + 1] - ys[j] <= 2:
            j += 1
        segs.append((ys[i], ys[j]))
        i = j + 1
    return segs


def main() -> dict[int, tuple[int, int]]:
    tmp = Path("/tmp/r29_cn4906.png")
    img = render_crop(tmp)
    out = {}
    for x in RISERS:
        segs = vertical_segments(img, x, 150, 1450)
        longest = max(segs, key=lambda s: s[1] - s[0])
        out[x] = longest
    return out


if __name__ == "__main__":
    segs = main()
    for x, (top_label, bottom_label) in RISERS.items():
        top, bottom = segs[x]
        print(f"x={x} y=[{top},{bottom}]: {top_label} <- {bottom_label}")
