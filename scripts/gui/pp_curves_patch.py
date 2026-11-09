#!/usr/bin/env python3
"""Parche de gammas de Picture Profile para el núcleo `av-cam.bin` de la A6000 (G18). NO instala nada.

Copia las 7 curvas de vídeo de la A7S fw3.20 (`0x16`, `0x18`–`0x1d`, 0x101a B, `+0x1012` = 4 como las de la A6000) al hueco sin
referencias `0x43faf28c`–`0x43fb8ee0` y, para las gammas que el código de la A6000 ya trata (`0x16`, `0x18`–`0x1b`), escribe sus
punteros de vídeo en la tabla de curvas (`0x44001404`) y las entradas 3–9 de la tabla selector→gamma (`0x43cb56e6`) como en la A7S.
`0x1c`/`0x1d` quedan sin puntero ni selector hasta la fase 4 (necesitan código).
Salidas: `av-cam.pp.bin` (salida 2: imagen) · `pp_ram.sh` + `pp_curvas.bin` (salida 1: las mismas escrituras desde la propia cámara al arrancar, por
`/dev/mem`, física = virtual + 0x40000000, con comprobación previa y relectura) · `manifest.json`.
Uso: pp_curves_patch.py BASE_AVCAM SALIDA_DIR [SELECTOR_DE_PRUEBA]  (p. ej. 6 = Cine1 forzada, solo CFW de prueba)
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / "analysis/rea-independent/input/av-cam-a7s.bin"
BASE, PHYS, CURVE = 0x43541000, 0x40000000, 0x101A
GAP = (0x43FAF28C, 0x43FB8EE0)
SLOT0, STRIDE = 0x43FAF300, 0x1020
TAB = {"a6000": 0x44001404, "a7s": 0x43FFA290}
SEL = {"a6000": 0x43CB56E6, "a7s": 0x43CAB54D}
GAMMAS = [0x16, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D]
CON_CODIGO = {0x16, 0x18, 0x19, 0x1A, 0x1B}  # el switch/rodilla de la A6000 llega a 0x1b
SEL_IDX = range(3, 10)  # 3 → 0x16, 4/5 → Movie/Still forzadas, 6–9 → 0x18–0x1b


def u32(d: bytes, a: int) -> int:
    return struct.unpack_from("<I", d, a - BASE)[0]


def patches(base: bytes, a7s: bytes) -> list[tuple[int, bytes, str]]:
    out = []
    for n, g in enumerate(GAMMAS):
        src = bytearray(a7s[u32(a7s, TAB["a7s"] + 8 * g + 4) - BASE:][:CURVE])
        assert src[0x1012] == 7 and src[0x1014] == g, (hex(g), src[0x1012], src[0x1014])  # +0x1014 = número de gamma
        src[0x1012] = 4  # valor de todas las curvas de vídeo de la A6000 (G17 §1)
        dst = SLOT0 + n * STRIDE
        out.append((dst, bytes(src), f"curva 0x{g:02x}"))
        if g in CON_CODIGO:
            out.append((TAB["a6000"] + 8 * g + 4, struct.pack("<I", dst), f"puntero vídeo 0x{g:02x}"))
    for i in SEL_IDX:
        out.append((SEL["a6000"] + 2 * i, a7s[SEL["a7s"] + 2 * i - BASE:][:2], f"selector {i}"))
    return out


def check_base(base: bytes, ps: list[tuple[int, bytes, str]]) -> None:
    assert not any(base[GAP[0] - BASE:GAP[1] - BASE]), "el hueco ya no está a cero"
    assert SLOT0 + len(GAMMAS) * STRIDE <= GAP[1]
    for a, data, what in ps:
        cur = base[a - BASE:a - BASE + len(data)]
        if what.startswith("puntero"):
            assert cur == b"\0" * 4, (what, cur.hex())
        elif what.startswith("selector"):
            assert cur == bytes([0, 0x0A]), (what, cur.hex())


def apply(base: bytes, ps: list[tuple[int, bytes, str]]) -> bytes:
    out = bytearray(base)
    for a, data, _ in ps:
        out[a - BASE:a - BASE + len(data)] = data
    assert len(out) == len(base)
    return bytes(out)


CFG = (0x43EDF684, 0x43ED4D28 + 0x48)  # bloque de ajustes (LIRO) y su copia de trabajo (S64); +0x153 = selector de gamma PP


def camera_files(base: bytes, ps: list[tuple[int, bytes, str]], prueba: int | None) -> tuple[str, bytes]:
    """Script de arranque de la cámara (salida 1) + fichero de datos. Orden: curvas → punteros → selector; antes comprueba
    con md5 que TODOS los sitios tienen los bytes originales de la imagen (si no, no escribe nada)."""
    ps = sorted(ps, key=lambda p: ("curva", "puntero", "selector").index(p[2].split()[0]))
    blob, rows = b"", []
    for a, data, what in ps:
        phys = a + PHYS
        assert phys % 2 == 0 and len(data) % 2 == 0 and len(blob) % 2 == 0
        orig = base[a - BASE:a - BASE + len(data)]
        rows.append((phys, len(data), len(blob), hashlib.md5(orig).hexdigest(), hashlib.md5(data).hexdigest(), what))
        blob += data
    sh = ["#!/bin/sh", "# pp_ram.sh (G18, generado por pp_curves_patch.py): gammas PP en la RAM del núcleo. Lo lanza s_start_android.sh.",
          "D=/usr/bin/pp_curvas.bin", "rd() { dd if=/dev/mem bs=2 skip=$1 count=$2 2>/dev/null | md5sum | cut -c1-32; }  # en medias palabras: $(( )) de ash es de 32 bits",
          "echo \"pp_ram: inicio $(date)\"", "ok=1"]
    for phys, n, off, mo, _, what in rows:
        sh.append(f'[ "$(rd {phys // 2} {n // 2})" = "{mo}" ] || {{ echo "pp_ram: {what} no es el original"; ok=0; }}')
    sh.append('[ $ok = 1 ] || { echo "pp_ram: av-cam distinto, no se escribe nada"; exit 1; }')
    for phys, n, off, _, mn, what in rows:
        sh.append(f"dd if=$D bs=2 skip={off // 2} count={n // 2} 2>/dev/null | dd of=/dev/mem bs=2 seek={phys // 2} 2>/dev/null")
        sh.append(f'[ "$(rd {phys // 2} {n // 2})" = "{mn}" ] || {{ echo "pp_ram: FALLO al escribir {what}"; ok=0; }}')
    sh.append('[ $ok = 1 ] && echo "pp_ram: OK" || { echo "pp_ram: ERROR"; exit 1; }')
    curvas = [r for r in rows if r[5].startswith("curva")]
    check = " ; ".join(f'[ "$(rd {p // 2} {n // 2})" = "{mn}" ] || echo "pp_ram: {w} alterada a los ${{t}} s"' for p, n, _, _, mn, w in curvas)
    sh.append(f"( for t in 60 600 3600; do sleep $t; {check}; echo \"pp_ram: comprobación ${{t}} s hecha\"; done ) &"
              "  # ¿el núcleo pisa el hueco en uso real?")
    if prueba is not None:  # solo para la prueba: fuerza el selector sin UI (CFW de prueba, no el definitivo)
        for c in CFG:
            sh.append(f"( sleep 20; echo -ne '\\{prueba:03o}' | dd of=/dev/mem bs=1 seek={c + 0x153 + PHYS} 2>/dev/null;"
                      f" echo \"pp_ram: prueba selector={prueba} en 0x{c + 0x153 + PHYS:08x}\" ) &")
    return "\n".join(sh) + "\n", blob


def main(base_path: Path, out: Path, prueba: int | None = None) -> dict:
    base, a7s = base_path.read_bytes(), A7S.read_bytes()
    ps = patches(base, a7s)
    check_base(base, ps)
    new = apply(base, ps)
    # autocomprobación: releer como lo haría el núcleo
    for g in CON_CODIGO:
        p = u32(new, TAB["a6000"] + 8 * g + 4)
        c = new[p - BASE:p - BASE + CURVE]
        ref = a7s[u32(a7s, TAB["a7s"] + 8 * g + 4) - BASE:][:CURVE]
        assert c[:0x1012] == ref[:0x1012] and c[0x1013:] == ref[0x1013:] and c[0x1012] == 4
    assert [list(new[SEL["a6000"] + 2 * i - BASE:][:2]) for i in range(12)] == \
        [[0, 10]] * 3 + [[0x16, 0x16], [10, 10], [0, 0], [0x18, 0x18], [0x19, 0x19], [0x1A, 0x1A], [0x1B, 0x1B]] + [[0, 10]] * 2
    diff = sum(a != b for a, b in zip(base, new))
    out.mkdir(parents=True, exist_ok=True)
    (out / "av-cam.pp.bin").write_bytes(new)
    sh, blob = camera_files(base, ps, prueba)
    (out / "pp_ram.sh").write_text(sh)
    (out / "pp_curvas.bin").write_bytes(blob)
    man = {"base_sha256": hashlib.sha256(base).hexdigest(), "pp_sha256": hashlib.sha256(new).hexdigest(), "bytes_distintos": diff,
           "escrituras": [{"virt": hex(a), "fis": hex(a + PHYS), "len": len(d), "que": w} for a, d, w in ps]}
    (out / "manifest.json").write_text(json.dumps(man, indent=1, ensure_ascii=False))
    return man


if __name__ == "__main__":
    m = main(Path(sys.argv[1]), Path(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else None)
    print(m["base_sha256"][:16], "→", m["pp_sha256"][:16], "bytes distintos", m["bytes_distintos"], "escrituras", len(m["escrituras"]))
