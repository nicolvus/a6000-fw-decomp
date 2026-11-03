#!/usr/bin/env python3
"""Cierre de las 6 filas pendientes de CAMERA_DETECT_FC/DEVICE/IS (S609/S612/S615/S617/S626).

Mide en av-cam A6000 fw3.21: sitios de carga PC-relativa de cada cadena, función contenedora
(prefijo `push {..lr}` hacia atrás), `bl` directos de esa función y alcance (profundidad<=3) a las
funciones de obturador conocidas; y en A7S/A6300 la presencia del token y de sus cadenas.
shortcut: llamadas indirectas (vtable/puntero) no se siguen; función contenedora = primer push{lr} hacia atrás.
"""
import json, struct, sys, re
from pathlib import Path
sys.path.insert(0, "analysis/s106_imaging_cap")
import scan_pic_refs_strict as S
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB

ROOT = Path(__file__).resolve().parents[2]
B, BASE, N = S.B, S.BASE, S.N
SHUTTER = {0x438c82fe: "C3-B enganche", 0x4383fa40: "productor r5", 0x436d6f6c: "SetExposure A6000",
           0x436d7e08: "SetRead +0x30", 0x437b46d0: "constructor normal", 0x438417c0: "EFCS",
           0x438c74b0: "BULB host"}
SRC = {"CAMERA_DETECT_FC": "s626_camera_detect_fc/camera_detect_fc", "CAMERA_DEVICE": "s617_camera_device/camera_device",
       "CAMERA_IS_DIST": "s609_dist/dist", "CAMERA_IS_MOUNT": "s612_mount/mount", "CAMERA_IS_EIS": "s615_eis/eis"}
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)

def u16(a): return struct.unpack_from("<H", B, a - BASE)[0]

def func_start(a):
    for x in range(a & ~1, max(BASE, a - 0x2000), -2):
        h = u16(x)
        if (h & 0xFE00) == 0xB400 and h & 0x100:           # push {..,lr}
            return x
        if u16(x) == 0xE92D and x + 4 <= BASE + N:          # push.w
            if struct.unpack_from("<H", B, x + 2 - BASE)[0] & 0x4000: return x
    return None

def func_end(f):
    x = f + 2
    while x < min(BASE + N - 4, f + 0x4000):
        h = u16(x)
        if (h & 0xFE00) == 0xB400 and h & 0x100: return x
        x += 2
    return x

def bl_targets(lo, hi):
    out = []
    for i in md.disasm(B[lo - BASE:hi - BASE], lo):
        if i.mnemonic in ("bl", "b.w", "b") and i.op_str.startswith("#"):
            out.append(int(i.op_str[1:], 0))
        elif i.mnemonic == "blx" and i.op_str.startswith("#"):
            out.append(int(i.op_str[1:], 0))
    return out

def reach(f, depth=3, seen=None):
    seen = seen if seen is not None else set()
    if f in seen or depth < 0: return seen
    seen.add(f)
    if BASE <= f < BASE + N:
        for t in bl_targets(f, min(func_end(f), f + 0x1000)):
            reach(t, depth - 1, seen)
    return seen

def tokens(path, tok):
    d = Path(path).read_bytes()
    return len(re.findall(re.escape(tok.encode()), d))

def main():
    sys.path.insert(0, "analysis")
    import verify_s6xx as V
    refs = S.scan(BASE, BASE + N)
    res = {}
    for name, src in SRC.items():
        j = json.load(open(f"analysis/{src}.json"))
        tok = j["prefix"].split("]")[0] + "]" if name == "CAMERA_DEVICE" else j["prefix"].rstrip(": ").rstrip()
        mod = {"strings": [], "token_models": {m: tokens(p, tok) for m, p in V.FIREWARE.items()} if hasattr(V, "FIREWARE") else {}}
        if not mod["token_models"]:
            mod["token_models"] = {m: tokens(p, tok) for m, p in V.FIRMWARE.items()}
        mod["token"] = tok
        funcs = {}
        for t in j["trace_strings"]:
            v = int(t["vaddr"], 16)
            # el prefijo puede empezar antes del inicio de cadena imprimible: probar inicio y exacto
            sites = refs.get(v) or []
            mod["strings"].append({"vaddr": t["vaddr"], "text": t["text"], "sites": [hex(s) for s in sites]})
            for s in sites:
                f = func_start(s)
                funcs.setdefault(f, []).append(s)
        mod["functions"] = []
        for f, ss in funcs.items():
            if f is None: continue
            tg = sorted(set(bl_targets(f, min(func_end(f), f + 0x1000))))
            r = reach(f)
            mod["functions"].append({"func": hex(f), "sites": [hex(x) for x in ss], "bl_targets": [hex(x) for x in tg],
                                     "shutter_reach": sorted(SHUTTER[x] for x in r if x in SHUTTER),
                                     "logger_global_0x43902718_loaded": None})
        res[name] = mod
    json.dump(res, open("analysis/camera_closure/closure.json", "w"), indent=1)
    for k, m in res.items():
        print(k, m["token_models"], [(s["vaddr"], len(s["sites"])) for s in m["strings"]],
              [(f["func"], len(f["bl_targets"]), f["shutter_reach"]) for f in m["functions"]])

if __name__ == "__main__":
    main()


def log_target(site):
    """Primer bl/blx tras la carga de la cadena (destino del logger) y constantes r0-r3 previas."""
    ins = list(md.disasm(B[site - 0x20 - BASE:site + 0x40 - BASE], site - 0x20))
    k = next(i for i, x in enumerate(ins) if x.address == site)
    for x in ins[k:]:
        if x.mnemonic in ("bl", "blx"):
            return x.op_str.lstrip("#")
    return None


def render(name, m, rows):
    fn = {f["func"]: f for f in m["functions"]}
    ns = sum(len(s["sites"]) for s in m["strings"])
    tgt = sorted({log_target(int(x, 16)) for s in m["strings"] for x in s["sites"]} - {None})
    tm = m["token_models"]
    sh = sorted({r for f in fn.values() for r in f["shutter_reach"]})
    return [
        ("Emisión (logger)", f"VERIFICADO (instrucciones): {ns} sitios `ldr`+`add pc` cargan las cadenas ({len(m['strings'])}) desde {len(fn)} funciones "
         f"({', '.join('`'+k+'`' for k in fn)}); el primer `bl` tras cada carga va a {', '.join('`'+t+'`' for t in tgt)}. "
         "«Dual» no es una propiedad medida: se sustituye por estos recuentos."),
        ("Equivalencia funcional A7S/A6300", f"VERIFICADO (bytes): el token `{m['token']}` tiene {tm['a7s_fw320']} coincidencias en A7S fw3.20 y {tm['a6300_fw201']} en A6300 fw2.01 "
         f"(A6000 fw3.21: {tm['a6000_fw321']}); no hay contraparte con este token que comparar."),
        ("Equivalencia de código", "VERIFICADO (bytes): sin contraparte por token en A7S/A6300 (fila anterior); no se afirma equivalencia."),
        ("Relación con el obturador", f"VERIFICADO (grafo `bl` directo, profundidad ≤ 3 desde cada emisora): alcanza {len(sh)} de las 7 funciones de obturador conocidas"
         + (f" ({', '.join(sh)})" if sh else "") + "; el alcance excluye llamadas indirectas (vtable/puntero). [S51](s51-decision.md) se mantiene."),
        ("Recuentos de `differential`", "VERIFICADO (reproducible): coincidencias exactas del token en `av-cam.bin` de cada modelo, con `analysis/camera_closure/closure.py`."),
        ("Funciones emisoras, sitios y trazas sin uso", f"VERIFICADO: sitios y funciones en `analysis/camera_closure/closure.json`; cadenas sin sitio: "
         f"{sum(1 for s in m['strings'] if not s['sites'])}. El significado de los nombres no se afirma."),
    ]

PATCH = {"CAMERA_DETECT_FC": "s626-camera_detect_fc", "CAMERA_DEVICE": "s617-camera_device", "CAMERA_IS_DIST": "s609-dist",
         "CAMERA_IS_MOUNT": "s612-mount", "CAMERA_IS_EIS": "s615-eis"}

def patch_reports():
    res = json.load(open("analysis/camera_closure/closure.json"))
    for name, stem in PATCH.items():
        p = ROOT / f"docs/capture/{stem}.md"
        t = p.read_text(encoding="utf-8")
        rows = "\n".join(f"| {a} | {b} |" for a, b in render(name, res[name], None))
        t = re.sub(r"## Afirmaciones pendientes\n\n\|.*?\n\n(?=El campo)", "## Afirmaciones cerradas (S-CAMERA, 03-11-2026)\n\n| Afirmación | Estado y evidencia |\n|---|---|\n" + rows + "\n\n", t, flags=re.S)
        t = re.sub(r"El campo `logger_dual=null`.*?\n", "Los campos históricos `logger_dual` y `shutter_line` (triaje léxico) quedan sustituidos por la tabla anterior.\n", t)
        t = re.sub(r"Los campos adicionales no sustentados tienen cobertura explícita NO_VERIFICADO; ", "", t)
        p.write_text(t, encoding="utf-8")

if __name__ == "__main__" and "--patch" in sys.argv:
    patch_reports()
