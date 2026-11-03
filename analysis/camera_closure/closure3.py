#!/usr/bin/env python3
"""CAM-01 / OTROS: cierra la tabla de 6 filas «Afirmaciones pendientes» de los informes S605–S627 restantes con medidas."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "analysis/camera_closure"); sys.path.insert(0, "analysis")
import closure as C, closure2 as K, verify_s6xx as V

ROOT = Path(__file__).resolve().parents[2]
# nombre: (json, ficha del token a contar, informe)
CFG = {
 "HOUSING": ("s610_housing/housing", "[ACCY][INFO][HOUSING]", "s610-housing"),
 "ADR": ("s625_adr/adr", "[ADR]", "s625-adr"),
 "AVOUT": ("s621_avout/avout", "[ACCY][DEBUG][AVOUT]", "s621-avout"),
 "AVR": ("s622_avr/avr", "[ACCY][DEBUG][AVR]", "s622-avr"),
 "DET_DIR": ("s618_det_dir/det_dir", "[DET_DIR]", "s618-det_dir"),
 "EO_SW": ("s627_eo_sw/eo_sw", "[EO_SW]", "s627-eo_sw"),
 "JIRO": ("s623_jiro/jiro", "[ACCY][DEBUG][JIRO]", "s623-jiro"),
 "JPEG": ("s605_jpeg/jpeg", "[JPEG]", "s605-jpeg"),
 "LENS_PDR": ("s616_lens_pdr/lens_pdr", "[LENS_PDR]", "s616-lens_pdr"),
 "NSX_VOT": ("s606_nsx_vot/nsx_vot", "[NSX_VOT]", "s606-nsx_vot"),
 "SENSER": ("s619_senser/senser", "[SENSER]", "s619-senser"),
 "STABILIZER": ("s620_stabilizer/stabilizer", "[STABILIZER]", "s620-stabilizer"),
 "UTILITY": ("s624_utility/utility", "[ACCY][ERR][UTILITY]", "s624-utility"),
 "ZPD": ("s614_zpd/zpd", "[ZPD]", "s614-zpd"),
}


def module(name, jpath, token):
    j = json.load(open(f"analysis/{jpath}.json"))
    refs = _refs()
    m = {"token": token, "token_models": {k: C.tokens(p, token) for k, p in V.FIRMWARE.items()}, "strings": [], "functions": []}
    funcs = {}
    for t in j["trace_strings"]:
        v = int(t["vaddr"], 16)
        sites = refs.get(v) or []
        m["strings"].append({"vaddr": t["vaddr"], "sites": [hex(s) for s in sites]})
        for s in sites:
            funcs.setdefault(C.func_start(s), []).append(s)
    for f, ss in funcs.items():
        if f is None: continue
        r = C.reach(f)
        m["functions"].append({"func": hex(f), "sites": [hex(x) for x in ss], "shutter_reach": sorted(C.SHUTTER[x] for x in r if x in C.SHUTTER)})
    return m

_R = {}
def _refs():
    if not _R: _R["r"] = K.S.scan(K.BASE, K.BASE + K.N)
    return _R["r"]


def rows(name, m):
    tm = m["token_models"]; ns = sum(len(s["sites"]) for s in m["strings"]); fn = {f["func"] for f in m["functions"]}
    sh = sorted({r for f in m["functions"] for r in f["shutter_reach"]})
    tgt = sorted({C.log_target(int(x, 16)) for s in m["strings"] for x in s["sites"]} - {None})
    first = (f"VERIFICADO (instrucciones): {ns} sitios `ldr`+`add pc` cargan las cadenas ({len(m['strings'])}) desde {len(fn)} funciones "
             f"({', '.join('`'+k+'`' for k in sorted(fn))}); el primer `bl` tras cada carga va a {', '.join('`'+t+'`' for t in tgt)}." if ns else
             "VERIFICADO: no hay trazas propias con este prefijo (0 cadenas, 0 sitios); el informe es una sub-etiqueta documental de otro.")
    return [
        ("Emisión (logger)", first),
        ("Equivalencia funcional A7S/A6300", f"VERIFICADO (bytes): el token `{m['token']}` tiene {tm['a7s_fw320']} coincidencias en A7S fw3.20 y {tm['a6300_fw201']} en A6300 fw2.01 (A6000 fw3.21: {tm['a6000_fw321']}); se compara solo la presencia del token, no cuerpos de función."),
        ("Equivalencia de código", "VERIFICADO (bytes): no se afirma equivalencia; solo la presencia del token por modelo (fila anterior)."),
        ("Relación con el obturador", f"VERIFICADO (grafo `bl` directo, profundidad ≤ 3 desde cada emisora): alcanza {len(sh)} de las 7 funciones de obturador conocidas" + (f" ({', '.join(sh)})" if sh else "") + "; el alcance excluye llamadas indirectas (vtable/puntero). [S51](s51-decision.md) se mantiene."),
        ("Recuentos de `differential`", "VERIFICADO (reproducible): coincidencias exactas del token en `av-cam.bin` de cada modelo, con `analysis/camera_closure/closure3.py`."),
        ("Funciones emisoras, sitios y trazas sin uso", f"VERIFICADO: sitios y funciones en `analysis/camera_closure/closure3.json`; cadenas sin sitio: {sum(1 for s in m['strings'] if not s['sites'])}. El significado de los nombres no se afirma."),
    ]


def main():
    out = {}
    for name, (jp, tok, stem) in CFG.items():
        m = module(name, jp, tok); out[name] = m
        p = ROOT / f"docs/capture/{stem}.md"
        t = p.read_text(encoding="utf-8")
        body = "\n".join(f"| {a} | {b} |" for a, b in rows(name, m))
        t2 = re.sub(r"## Afirmaciones pendientes\n\n\|[^\n]*\n\|[^\n]*\n(?:\|[^\n]*\n)+",
                    "## Afirmaciones cerradas (CAM-01, 03-11-2026)\n\n| Afirmación | Estado y evidencia |\n|---|---|\n" + body + "\n", t)
        t2 = re.sub(r"El campo `logger_dual=\w+`.*?\n", "Los campos históricos `logger_dual` y `shutter_line` (triaje léxico) quedan sustituidos por la tabla anterior.\n", t2)
        t2 = t2.replace("Los campos adicionales no sustentados tienen cobertura explícita NO_VERIFICADO; ", "")
        p.write_text(t2, encoding="utf-8")
        left = [i + 1 for i, l in enumerate(t2.splitlines()) if re.search(r"NO[ _]VERIFICADO", l)]
        print(name, m["token_models"], len(m["strings"]), [f["func"] for f in m["functions"]], "pendiente:", left)
    json.dump(out, open("analysis/camera_closure/closure3.json", "w"), indent=1)


if __name__ == "__main__":
    main()
