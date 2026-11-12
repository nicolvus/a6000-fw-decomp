#!/usr/bin/env python3
"""Rasterizador fuera de línea de las listas de la GPU de DMP volcadas con GPUDUMP (G22 §5.18z).

uso: gpu_raster.py DIR_TRABAJO [salida.png]
Lee DIR/gpu.txt (listas y líneas VTX de cada cuadrilátero, escritas por el shim en cada timbre) y las texturas de los volcados
AREADUMP (DIR/area_stream_<base>.bin). Cada lista dibuja una tira de triángulos (0x202 = 0x9000_00NN; 4 = cuadrilátero, 16 = marco de 9 trozos): textura en 0x589 (dirección>>3),
0x586 (ancho<<16 | alto), 0x58f formato (4 = RGBA4444, 8 = A8; mosaico 8×8 en orden de Morton). Vértice de 0x40 B: posición local
(f0, f1), color RGBA (f3–f6), UV (f7, f8) y matriz afín 2×3 a pantalla (f9–f11, f12–f14). Mezcla alfa «sobre» en un lienzo 640×480.
Scissor (redibujado parcial): 0x47 = (2(x0−320), 2(240−y1)), 0x48 = (2(x1−320), 2(240−y0)), s16 cada mitad (medido sobre 60 listas, §5.18z).
shortcut: sin shaders ni combinadores reales; solo tiras de triángulos y los dos formatos medidos.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

W, H = 640, 480


def lee_trabajos(txt: str) -> list[dict]:
    jobs: list[dict] = []
    for ln in txt.splitlines():
        p = ln.split()
        if ln.startswith("JOB"):
            jobs.append({"lista": p[2], "regs": {}, "vtx": []})
        elif ln.startswith("VTX") and jobs:
            jobs[-1]["vtx"].append([float(x) for x in p[2:18]])
        elif jobs and len(p) >= 3 and re.fullmatch(r"[0-9a-f]{4}", p[0]) and int(p[1], 16) >> 12 and 0x202 not in jobs[-1]["regs"]:
            jobs[-1]["regs"][int(p[0], 16)] = int(p[2], 16)  # estado hasta el primer disparo (0x202); después la lista redefine 0x216/0x47…
    return jobs


def tile_index(w: int, h: int) -> np.ndarray:
    """Desplazamiento en píxeles de (y, x) dentro de una textura en mosaico 8×8 de Morton."""
    y, x = np.mgrid[0:h, 0:w]
    m = (x & 1) | (y & 1) << 1 | (x & 2) << 1 | (y & 2) << 2 | (x & 4) << 2 | (y & 4) << 3
    return ((y >> 3) * (w >> 3) + (x >> 3)) * 64 + m


def textura(areas: dict[int, bytes], addr: int, w: int, h: int, fmt: int) -> np.ndarray | None:
    """RGBA en flotantes [0,1], forma (h, w, 4); None si la dirección no está volcada o el formato no se conoce."""
    bpp = {4: 2, 8: 1}.get(fmt)
    base = next((b for b, d in areas.items() if b <= addr and addr + w * h * (bpp or 1) <= b + len(d)), None)
    if bpp is None or base is None:
        return None
    raw = np.frombuffer(areas[base], np.uint8, w * h * bpp, addr - base)
    idx = tile_index(w, h)
    if fmt == 8:
        a = raw[idx].astype(np.float32) / 255
        return np.dstack([np.ones_like(a)] * 3 + [a])
    v = raw.view("<u2")[idx]
    return np.dstack([((v >> s) & 15).astype(np.float32) / 15 for s in (12, 8, 4, 0)])


def scissor(r: dict[int, int]) -> tuple[int, int, int, int]:
    """(x0, y0, x1, y1) en píxeles; pantalla completa si la lista no lo fija."""
    if 0x47 not in r or 0x48 not in r:
        return 0, 0, W, H
    s16 = [(v ^ 0x8000) - 0x8000 for v in (r[0x47] & 0xFFFF, r[0x47] >> 16, r[0x48] & 0xFFFF, r[0x48] >> 16)]
    return 320 + s16[0] // 2, 240 - s16[3] // 2, 320 + s16[2] // 2, 240 - s16[1] // 2


def dibuja(canvas: np.ndarray, vtx: list[list[float]], tex: np.ndarray | None, clip: tuple[int, int, int, int] = (0, 0, W, H)) -> None:
    """Tira de triángulos (0x202 = 0x9000_00NN: 4 = cuadrilátero, 16 = marco de 9 trozos); UV y color interpolados en baricéntricas."""
    v = np.array(vtx)
    sx = v[:, 9] * v[:, 0] + v[:, 10] * v[:, 1] + v[:, 11]
    sy = v[:, 12] * v[:, 0] + v[:, 13] * v[:, 1] + v[:, 14]
    x0, y0 = max(int(np.floor(sx.min())), clip[0], 0), max(int(np.floor(sy.min())), clip[1], 0)
    x1, y1 = min(int(np.ceil(sx.max())), clip[2], W), min(int(np.ceil(sy.max())), clip[3], H)
    if x0 >= x1 or y0 >= y1:
        return
    py, px = np.mgrid[y0:y1, x0:x1] + 0.5
    mask = np.zeros(px.shape, bool)
    att = np.zeros(px.shape + (6,), np.float32)  # u, v, r, g, b, a
    for i in range(len(v) - 2):  # el último triángulo que cubre un píxel manda: sin doble mezcla en las aristas compartidas
        (ax, bx, cx), (ay, by, cy) = sx[i:i + 3], sy[i:i + 3]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            continue
        w0 = ((by - cy) * (px - cx) + (cx - bx) * (py - cy)) / den
        w1 = ((cy - ay) * (px - cx) + (ax - cx) * (py - cy)) / den
        w2 = 1 - w0 - w1
        ins = (w0 >= -1e-6) & (w1 >= -1e-6) & (w2 >= -1e-6)
        k = v[i:i + 3][:, [7, 8, 3, 4, 5, 6]]
        att[ins] = (w0[ins, None] * k[0] + w1[ins, None] * k[1] + w2[ins, None] * k[2])
        mask |= ins
    col = att[..., 2:6]
    if tex is None:
        src = col
    else:
        th, tw = tex.shape[:2]
        u = np.clip((att[..., 0] * tw).astype(int), 0, tw - 1)
        t = np.clip((att[..., 1] * th).astype(int), 0, th - 1)
        src = tex[t, u] * col
    dst = canvas[y0:y1, x0:x1]
    al = src[..., 3:4] * mask[..., None]
    dst[..., :3] = src[..., :3] * al + dst[..., :3] * (1 - al)
    dst[..., 3:4] = al + dst[..., 3:4] * (1 - al)


def main(work: Path, out: Path) -> None:
    areas = {int(m.group(1), 16): f.read_bytes() for f in work.glob("area_stream_*.bin") if (m := re.search(r"_([0-9a-f]+)\.bin$", f.name))}
    canvas = np.zeros((H, W, 4), np.float32)
    for j in lee_trabajos((work / "gpu.txt").read_text()):
        r = j["regs"]
        if r.get(0x202, 0) >> 24 != 0x90 or len(j["vtx"]) != r[0x202] & 0xFFF:
            continue
        w, h = r.get(0x586, 0) >> 16, r.get(0x586, 0) & 0xFFFF
        tex = textura(areas, (r.get(0x589, 0) << 3) & 0xFFFFFFFF, w, h, r.get(0x58F, -1)) if w and h else None
        print(f"{j['lista']} tex {r.get(0x589, 0) << 3 & 0xFFFFFFFF:#x} {w}x{h} fmt {r.get(0x58F)} {'ok' if tex is not None else 'sin datos'}")
        dibuja(canvas, j["vtx"], tex, scissor(r))
    Image.fromarray((canvas[..., :3] * 255).astype(np.uint8)).save(out)
    print(out)


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]) if len(sys.argv) > 2 else Path(sys.argv[1]) / "menu.png")
