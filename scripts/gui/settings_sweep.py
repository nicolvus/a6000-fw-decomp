#!/usr/bin/env python3
"""Barrido de los ajustes de menú (nodos raíz de `CautionConfig.so`) de A6000 fw3.21 y A6300 fw2.01 y su diferencia (G13). Solo lee.

Por raíz `cmnViewSettingNodeRoot<X>`: ProcessId (`0xe`), etiqueta inglesa, número de opciones (listas `<X>…` con `0xf`) y
estado: «oculta» = ninguna `viewUnified*.so` del mismo firmware la importa (la UI no puede llegar a ella); «dudosa» = importada pero
la raíz no tiene `0xb = 2` (SilentShutter, oculta en la A6000, pero también FnFunction/CustomFunction, que sí se ven); «activa» = el resto.
shortcut: importar el nodo no prueba que una página visible para este modelo lo contenga; la verdad final es la cámara.
Uso: settings_sweep.py [SALIDA.json]   → resumen por stdout
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import setting_nodes
import uxc_strings

ROOT = Path(__file__).resolve().parents[2]
FW = {"a6000": ROOT / "firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked",
      "a6300": ROOT / "firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked"}
NODE = "cmnViewSettingNodeRoot"


def _syms(lib: Path, flag: str) -> list[str]:
    out = subprocess.run(["nm", "-D", flag, str(lib)], capture_output=True, text=True, check=True).stdout
    return [ln.split()[-1] for ln in out.splitlines()]


def sweep(usr: Path) -> dict[str, dict]:
    lib = usr / "lib/CautionConfig.so"
    _, _, texts = uxc_strings.parse((usr / "share/app/string_english.uxc").read_bytes())
    lists = {n: {p: v for p, _, v in props} for n, props in setting_nodes.property_lists(lib, ".*")}
    ui = {s[len(NODE):] for v in (usr / "lib").glob("viewUnified*.so") for s in _syms(v, "--undefined-only") if s.startswith(NODE)}
    out = {}
    for name in (s[len(NODE):] for s in _syms(lib, "--defined-only") if s.startswith(NODE)):
        key = name if name in lists else name + "Root"
        root = lists.get(key, {})
        base = key.removesuffix("Root")
        opts = [n for n in lists if n.startswith(base) and n not in (name, key) and 0xF in lists[n] and 0xE not in lists[n]]
        label = root.get(0)
        out[name] = {"pid": root.get(0xE), "texto": texts.get(label & 0xFFFF, "") if label else "", "opciones": len(opts),
                     "estado": "oculta" if name not in ui else "activa" if root.get(0xB) == 2 else "dudosa"}
    return out


def main(dest: Path | None) -> dict:
    a, b = (sweep(FW[k]) for k in ("a6000", "a6300"))
    assert a["CustomFrontCurtainShutter"]["estado"] == "activa" and a["SilentShutter"]["estado"] == "dudosa", "heurística rota"
    assert a["AfIlluminator"]["estado"] == "oculta" and a["StillAFIlluminator"]["estado"] == "activa", "heurística rota"
    res = {"a6000": a, "a6300": b,
           "solo_a6300": sorted(set(b) - set(a)), "solo_a6000": sorted(set(a) - set(b)),
           "no_activas_a6000": sorted(n for n, r in a.items() if r["estado"] != "activa"),
           "no_activas_a6000_activas_a6300": sorted(n for n, r in a.items() if r["estado"] != "activa" and b.get(n, {}).get("estado") == "activa"),
           "comunes_con_mas_opciones_en_a6300": sorted(n for n in set(a) & set(b) if b[n]["opciones"] > a[n]["opciones"]),
           "pid_igual_en_comunes": sum(a[n]["pid"] == b[n]["pid"] for n in set(a) & set(b)), "comunes": len(set(a) & set(b))}
    if dest:
        dest.write_text(json.dumps(res, indent=1, ensure_ascii=False))
    return res


if __name__ == "__main__":
    r = main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    for k in ("a6000", "a6300"):
        print(k, "raíces", len(r[k]), {e: sum(x["estado"] == e for x in r[k].values()) for e in ("activa", "dudosa", "oculta")})
    for k in ("solo_a6300", "solo_a6000", "no_activas_a6000", "no_activas_a6000_activas_a6300", "comunes_con_mas_opciones_en_a6300"):
        print(k, len(r[k]))
    print("ProcessId igual en comunes:", r["pid_igual_en_comunes"], "/", r["comunes"])
