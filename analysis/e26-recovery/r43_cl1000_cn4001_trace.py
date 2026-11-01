"""E26-R43 — verifica, por coordenadas exactas del PDF vectorial (sin rasterizar), a qué pin
de CN4001 (conector Multi externo, página 37 del manual) llega la red global `BOOT_SERIAL_IN`
que sale de la hoja "CLK BOOT" (página 24), y si la red `BOOT_MAIN`/`CL1000` (IC6000 P7,
`MODEREG` bit 0) tiene alguna salida equivalente hacia ese mismo conector.

Método: `pdftotext -bbox` da la posición exacta (puntos PDF) de cada etiqueta de texto;
`pdftocairo -svg` da los trazos vectoriales reales. Para cada fila de interés se comprueba
que existe un segmento horizontal CONTINUO (mismo y, sin desvío) entre la etiqueta de la red
global y el borde de la tabla de pines de CN4001 (x=379.43 en la página 37) — el mismo método
que ya usa `r29_pinout_pixel_trace.py` para CN4906, aplicado aquí a CN4001, que R29 dejó sin
cubrir (usó agrupación por fila, que en esta hoja confunde pin 9 y pin 10 — ver `main()`).

Solo lectura. No toca hardware. Requiere `pdftotext` y `pdftocairo` (poppler-utils).
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "references/manuals/a6000_service_L3.pdf"

PAGE_CLKBOOT = 24
PAGE_CN4001 = 37
TABLE_EDGE_X = 379.43  # borde izquierdo de la columna "pin #" en CN4001 (página 37)


def _require_tools() -> None:
    for tool in ("pdftotext", "pdftocairo"):
        if shutil.which(tool) is None:
            raise RuntimeError(f"falta {tool} (poppler-utils)")


def bbox_words(page: int) -> list[tuple[float, float, float, float, str]]:
    html = subprocess.run(
        ["pdftotext", "-bbox", "-f", str(page), "-l", str(page), str(PDF), "-"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    out = []
    for m in re.finditer(
        r'xMin="([0-9.]+)" yMin="([0-9.]+)" xMax="([0-9.]+)" yMax="([0-9.]+)">([^<]*)',
        html,
    ):
        x0, y0, x1, y1, txt = m.groups()
        if txt.strip():
            out.append((float(x0), float(y0), float(x1), float(y1), txt))
    return out


def svg_segments(page: int, x_range: tuple[float, float], y_range: tuple[float, float]):
    out = ROOT / f"analysis/e26-recovery/_r43_page{page}.svg"
    subprocess.run(
        ["pdftocairo", "-svg", "-f", str(page), "-l", str(page), str(PDF), str(out)],
        check=True,
        capture_output=True,
    )
    data = out.read_text(encoding="utf-8")
    path_re = re.compile(r'<path\s+([^>]*?)d="([^"]+)"([^>]*)/>', re.DOTALL)
    transform_re = re.compile(r'transform="matrix\(([^)]+)\)"')
    X0, X1 = x_range
    Y0, Y1 = y_range
    segs: list[tuple[float, float, float, float]] = []
    for m in path_re.finditer(data):
        attrs = m.group(1) + m.group(3)
        if 'fill="none"' not in attrs or "stroke=" not in attrs:
            continue
        tm = transform_re.search(attrs)
        a, b, c, d, e, f = (
            (float(v) for v in tm.group(1).split(",")) if tm else (1, 0, 0, 1, 0, 0)
        )
        tokens = m.group(2).replace(",", " ").split()
        subpaths: list[list[tuple[float, float]]] = []
        cur: list[tuple[float, float]] | None = None
        cmd = None
        i = 0
        while i < len(tokens):
            t = tokens[i]
            if t in ("M", "L", "C", "Z", "z"):
                cmd = t
                i += 1
                if cmd == "M":
                    if cur:
                        subpaths.append(cur)
                    cur = []
                continue
            if cmd in ("M", "L"):
                x, y = float(tokens[i]), float(tokens[i + 1])
                (cur if cur is not None else []).append((x, y))
                i += 2
            elif cmd == "C":
                i += 6
            else:
                i += 1
        if cur:
            subpaths.append(cur)
        for sp in subpaths:
            abs_pts = [(a * x + c * y + e, b * x + d * y + f) for x, y in sp]
            for j in range(len(abs_pts) - 1):
                x1, y1 = abs_pts[j]
                x2, y2 = abs_pts[j + 1]
                if (X0 <= x1 <= X1 or X0 <= x2 <= X1) and (Y0 <= y1 <= Y1 or Y0 <= y2 <= Y1):
                    segs.append((round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)))
    out.unlink(missing_ok=True)
    return sorted(set(segs))


def pin_rows(words, x0=378, x1=384) -> dict[int, float]:
    return {
        int(txt): (wy0 + wy1) / 2
        for wx0, wy0, wx1, wy1, txt in words
        if x0 <= wx0 <= x1 and re.fullmatch(r"\d+", txt)
    }


def cn4001_label_to_pin(label: str, words37, segs37, pins) -> int | None:
    """Pin de CN4001 al que llega, sin desvío de fila, la etiqueta global izquierda `label`."""
    w = next(w for w in words37 if w[4] == label and w[0] < 240)
    y_label = (w[1] + w[3]) / 2
    # segmento horizontal que toca x=TABLE_EDGE_X a la misma altura que la etiqueta (+-3.5 pt,
    # el desplazamito típico etiqueta/trazo visto en todo el manual)
    # el trazo real viene de fuera de la tabla (x bien a la izquierda de 379.43); las líneas
    # internas de la rejilla de la tabla también tocan x=379.43 pero arrancan justo al lado
    # (x~383) y se confundirían con el cableado real si no se excluyen por longitud
    hits = [
        (x1, y1)
        for x1, y1, x2, y2 in segs37
        if y1 == y2
        and (abs(x1 - TABLE_EDGE_X) < 0.6 or abs(x2 - TABLE_EDGE_X) < 0.6)
        and min(x1, x2) < 370
        and abs(y1 - y_label) < 4.0
    ]
    if not hits:
        return None
    _, wire_y = min(hits, key=lambda h: abs(h[1] - y_label))
    return min(pins.items(), key=lambda kv: abs(kv[1] - wire_y))[0]


def _walk_row(start_y: float, segs24, max_hops: int = 6) -> set[float]:
    """Alturas y alcanzables desde `start_y` siguiendo segmentos horizontales (misma y) y los
    saltos verticales (misma x en ambos extremos) que arrancan de un punto ya alcanzado."""
    ys = {start_y}
    xs_at_y: dict[float, set[float]] = {}
    for x1, y1, x2, y2 in segs24:
        if y1 == y2:
            xs_at_y.setdefault(y1, set()).update({x1, x2})
    for _ in range(max_hops):
        grown = False
        for x1, y1, x2, y2 in segs24:
            if x1 != x2:
                continue  # solo saltos verticales
            for y in (y1, y2):
                other = y2 if y == y1 else y1
                if any(abs(y - ry) < 0.6 for ry in ys) and not any(
                    abs(other - ry) < 0.6 for ry in ys
                ):
                    ys.add(other)
                    grown = True
        if not grown:
            break
    return ys


def clkboot_export_target(ball: str, words24, segs24) -> tuple[float, float, str] | None:
    """Etiqueta global (x>=500) alcanzada por el trazo de la fila del pin `ball` (H21/P7),
    siguiendo los saltos de fila (columnas verticales) que haya. Devuelve (x,y,texto) o None."""
    by = next((y0 + y1) / 2 for x0, y0, x1, y1, txt in words24 if txt == ball and 379 <= x0 <= 384)
    row_candidates = [
        y1
        for x1, y1, x2, y2 in segs24
        if y1 == y2 and 383 <= min(x1, x2) <= 384.5 and abs(y1 - by) < 6
    ]
    if not row_candidates:
        return None
    # cada fila real queda ~3.5pt por debajo de su etiqueta en esta hoja (offset constante,
    # igual para las 6 filas K6..P7); con varias filas a <6pt (están muy apretadas) se toma la
    # MÁS CERCANA, no la primera, para no robarle la fila a la vecina
    wire_y = min(row_candidates, key=lambda y: abs(y - by))
    reachable_ys = _walk_row(wire_y, segs24)
    candidates = [
        (x1, y1, x2, y2)
        for x1, y1, x2, y2 in segs24
        if y1 == y2 and any(abs(y1 - ry) < 0.6 for ry in reachable_ys) and max(x1, x2) >= 500
    ]
    if not candidates:
        return None
    x1, y1, x2, _y2 = max(candidates, key=lambda s: max(s[0], s[2]))
    end_x, end_y = max(x1, x2), y1
    far_words = [w for w in words24 if w[0] >= 500]
    best = min(far_words, key=lambda w: abs((w[1] + w[3]) / 2 - end_y) + abs(w[0] - end_x) * 0.01)
    return (best[0], (best[1] + best[3]) / 2, best[4])


def main() -> None:
    _require_tools()

    words24 = bbox_words(PAGE_CLKBOOT)
    segs24 = svg_segments(PAGE_CLKBOOT, (375, 560), (210, 260))

    print("== Página 24 (CLK BOOT): red global alcanzada por cada fila ==")
    for ball, interno in (("H21", "BOOT_SERIAL_IN (bit1)"), ("P7", "BOOT_MAIN/CL1000 (bit0)")):
        target = clkboot_export_target(ball, words24, segs24)
        print(f"{ball} [{interno}] -> {target[2] if target else None!r} "
              f"(y={target[1]:.2f})" if target else f"{ball} [{interno}] -> None (sin salto trazable)")

    words37 = bbox_words(PAGE_CN4001)
    segs37 = svg_segments(PAGE_CN4001, (150, 440), (625, 700))
    pins = pin_rows(words37)

    print("\n== Página 37 (CN4001 Multi): pin alcanzado por cada etiqueta global ==")
    for label in ("XRESET_REQ", "DEBUG_UART0_RXD", "BOOT_SERIAL_IN", "AD_JACK_IN"):
        pin = cn4001_label_to_pin(label, words37, segs37, pins)
        print(f"{label!r} -> pin {pin}")


if __name__ == "__main__":
    main()
