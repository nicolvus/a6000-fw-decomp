#!/usr/bin/env python3
"""Parche de gammas de Picture Profile para el núcleo `av-cam.bin` de la A6000 (G18). NO instala nada.

Copia las 7 curvas de vídeo de la A7S fw3.20 (`0x16`, `0x18`–`0x1d`, 0x101a B, `+0x1012` = 4 como las de la A6000) al hueco sin
referencias `0x43faf28c`–`0x43fb8ee0` y, para las gammas que el código de la A6000 ya trata (`0x16`, `0x18`–`0x1b`), escribe sus
punteros de vídeo en la tabla de curvas (`0x44001404`) y las entradas 3–9 de la tabla selector→gamma (`0x43cb56e6`) como en la A7S.
`0x1c`/`0x1d` quedan sin puntero ni selector hasta la fase 4 (necesitan código).
Salidas: `av-cam.pp.bin` (salida 2: imagen) · `pp_ram.sh` + `pp_curvas.bin` (salida 1: las mismas escrituras desde la propia cámara al arrancar, por
`/dev/mem`, física = virtual + 0x40000000, con comprobación previa y relectura) · `manifest.json`.
Uso: pp_curves_patch.py BASE_AVCAM SALIDA_DIR [SELECTOR_DE_PRUEBA] [--color]  (p. ej. 6 = Cine1 forzada, solo CFW de prueba)
"""
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

ROOT = Path(__file__).resolve().parents[2]
A7S = ROOT / "analysis/rea-independent/input/av-cam-a7s.bin"
A6300 = ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
BASE, PHYS, CURVE = 0x43541000, 0x40000000, 0x101A
GAP = (0x43FAF28C, 0x43FB8EE0)
SLOT0, STRIDE = 0x43FAF300, 0x1020
TAB = {"a6000": 0x44001404, "a7s": 0x43FFA290}
SEL = {"a6000": 0x43CB56E6, "a7s": 0x43CAB54D}
# G26: la A6300 trae S-Log3 como gamma 0x1f (curva en el bloque de punteros 0x441bc70c, selector 12 = (0x1f,0x1f), tabla de selectores de la A6300 en 0x43db1e31 (= índice 3)).
# Se instala con el número 0x17: el código de la A6000 lo trata por la rama por defecto (como Movie/Still), sin caso propio (NO verificado en cámara).
TAB_A6300, SLOG3_A6300, SLOG3_AQUI = 0x441BC70C, 0x1F, 0x17
GAMMAS = [0x16, 0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D]
# Fase 4 solo-datos (G25): el código de la A6000 llega a 0x1b, así que las dos curvas de la A7S con código propio (0x1c = S-Log2, 0x1d = ITU709(800%);
# selectores 10 y 11 = VALUEID 0x480 y 0x481) se instalan con los números 0x14 y 0x15, que el código ya trata como el resto de gammas de cine
# (mismos casos del switch y de la rodilla que 0x16 y 0x18–0x1b) y cuya curva de vídeo está vacía en la A6000.
REMAP = {0x1C: 0x14, 0x1D: 0x15}
CON_CODIGO = {0x16, 0x18, 0x19, 0x1A, 0x1B, 0x14, 0x15}
SEL_IDX = range(3, 13)  # 3 → 0x16, 4/5 → Movie/Still forzadas, 6–9 → 0x18–0x1b, 10/11 → 0x14/0x15, 12 → 0x17 (S-Log3, G26)


def u32(d: bytes, a: int) -> int:
    return struct.unpack_from("<I", d, a - BASE)[0]


def patches(base: bytes, a7s: bytes, a6300: bytes | None = None) -> list[tuple[int, bytes, str]]:
    out = []
    for n, g in enumerate(GAMMAS):
        src = bytearray(a7s[u32(a7s, TAB["a7s"] + 8 * g + 4) - BASE:][:CURVE])
        assert src[0x1012] == 7 and src[0x1014] == g, (hex(g), src[0x1012], src[0x1014])  # +0x1014 = número de gamma
        src[0x1012] = 4  # valor de todas las curvas de vídeo de la A6000 (G17 §1)
        ng = REMAP.get(g, g)
        src[0x1014] = ng  # el número de gamma de la propia curva coincide con el que usa el núcleo
        dst = SLOT0 + n * STRIDE
        out.append((dst, bytes(src), f"curva 0x{ng:02x}"))
        out.append((TAB["a6000"] + 8 * ng + 4, struct.pack("<I", dst), f"puntero vídeo 0x{ng:02x}"))
    if a6300 is not None:  # S-Log3 (G26): curva 0x1f de la A6300 → gamma 0x17, selector 12
        src = bytearray(a6300[u32(a6300, TAB_A6300 + 8 * SLOG3_A6300 + 4) - BASE:][:CURVE])
        assert src[0x1012] == 7 and src[0x1014] == SLOG3_A6300, (src[0x1012], src[0x1014])
        src[0x1012], src[0x1014] = 4, SLOG3_AQUI
        dst = SLOT0 + len(GAMMAS) * STRIDE
        out.append((dst, bytes(src), f"curva 0x{SLOG3_AQUI:02x}"))
        out.append((TAB["a6000"] + 8 * SLOG3_AQUI + 4, struct.pack("<I", dst), f"puntero vídeo 0x{SLOG3_AQUI:02x}"))
    for i in SEL_IDX:
        if i == 12:
            if a6300 is not None:
                out.append((SEL["a6000"] + 2 * i, bytes([SLOG3_AQUI, SLOG3_AQUI]), f"selector {i}"))
            continue
        e = a7s[SEL["a7s"] + 2 * i - BASE:][:2]
        out.append((SEL["a6000"] + 2 * i, bytes(REMAP.get(x, x) for x in e), f"selector {i}"))
    return out


def check_base(base: bytes, ps: list[tuple[int, bytes, str]]) -> None:
    assert not any(base[GAP[0] - BASE:GAP[1] - BASE]), "el hueco ya no está a cero"
    assert SLOT0 + (len(GAMMAS) + 1) * STRIDE <= GAP[1]
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
    ps = sorted(ps, key=lambda p: ("curva", "puntero", "selector", "dato", "gancho").index(p[2].split()[0]))   # datos antes que ganchos de código (G27)
    blob, rows = b"", []
    for a, data, what in ps:
        phys = a + PHYS
        assert phys % 2 == 0 and len(data) % 2 == 0 and len(blob) % 2 == 0
        orig = base[a - BASE:a - BASE + len(data)]
        rows.append((phys, len(data), len(blob), hashlib.md5(orig).hexdigest(), hashlib.md5(data).hexdigest(), what))
        blob += data
    sh = ["#!/bin/sh", "# pp_ram.sh (G18, generado por pp_curves_patch.py): gammas PP en la RAM del núcleo. Lo lanza s_start_android.sh.",
          # G27: el busybox de la cámara trae md5sum y cut como applets, pero sin enlaces en el PATH (3.60: «md5sum: not found» y no escribió nada)
          "md5sum() { /bin/busybox md5sum \"$@\"; }; cut() { /bin/busybox cut \"$@\"; }",
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


def main(base_path: Path, out: Path, prueba: int | None = None, color: bool = False) -> dict:
    base, a7s = base_path.read_bytes(), A7S.read_bytes()
    ps = patches(base, a7s, A6300.read_bytes() if A6300.is_file() else None)
    if color:  # G27: S-Gamut3 / S-Gamut3.Cine (código + datos en el hueco, tras las curvas)
        import pp_color_patch
        ps += pp_color_patch.patches(base, pp_color_patch.PRESET_A6300.read_bytes())
    check_base(base, ps)
    new = apply(base, ps)
    # autocomprobación: releer como lo haría el núcleo
    for g in CON_CODIGO | ({SLOG3_AQUI} if A6300.is_file() else set()):
        p = u32(new, TAB["a6000"] + 8 * g + 4)
        c = new[p - BASE:p - BASE + CURVE]
        og = next((k for k, v in REMAP.items() if v == g), g)  # gamma de la A7S de la que viene la curva
        a_ref, t_ref = (a7s, TAB["a7s"]) if g != SLOG3_AQUI else (A6300.read_bytes(), TAB_A6300)
        og = SLOG3_A6300 if g == SLOG3_AQUI else og
        ref = a_ref[u32(a_ref, t_ref + 8 * og + 4) - BASE:][:CURVE]
        assert c[:0x1012] == ref[:0x1012] and c[0x1013] == ref[0x1013] and c[0x1015:] == ref[0x1015:] and c[0x1012] == 4 and c[0x1014] == g
    assert [list(new[SEL["a6000"] + 2 * i - BASE:][:2]) for i in range(13)] == \
        [[0, 10]] * 3 + [[0x16, 0x16], [10, 10], [0, 0], [0x18, 0x18], [0x19, 0x19], [0x1A, 0x1A], [0x1B, 0x1B], [0x14, 0x14], [0x15, 0x15],
                         [0x17, 0x17] if A6300.is_file() else [0, 10]]
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
    pos = [x for x in sys.argv[1:] if not x.startswith("--")]
    m = main(Path(pos[0]), Path(pos[1]), int(pos[2]) if len(pos) > 2 else None, "--color" in sys.argv)
    print(m["base_sha256"][:16], "→", m["pp_sha256"][:16], "bytes distintos", m["bytes_distintos"], "escrituras", len(m["escrituras"]))
