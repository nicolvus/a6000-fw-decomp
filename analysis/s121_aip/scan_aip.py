#!/usr/bin/env python3
"""S121 — extracción del módulo `[AIP]` (Audio IP) del firmware de la A6000.

Genera `aip.json` con:
  - las 37 cadenas `[AIP]` con vaddr, texto, sitio PIC, función y sub-bloque;
  - el mapa función→traza;
  - el recuento del escaneo independiente de todos los `add rX, pc` de la imagen;
  - la comparación con la kill analysis canónica (`pic_refs_v2.json`), si está;
  - el diferencial con la A7S fw3.20 y con la A6300 fw2.01.

Regla de referencia (estricta, la que se usa para TODO el informe):
un `add rX, pc` (forma registro, `0x4478`, Rm=15) toma su valor del `ldr rX, [pc, #imm]`
más cercano hacia atrás sobre el MISMO registro; destino = valor_del_pool + (dir_add + 4).
La ventana real observada en el módulo es de 2–6 B.

Uso:  scan_aip.py [RUTA_PIC_REFS_V2]
Convención: vaddr = 0x43541000 + file_offset.
"""
import json
import os
import struct
import sys
from collections import Counter, OrderedDict, defaultdict

BASE = 0x43541000
BIN = "analysis/rea-independent/input/av-cam.bin"
A7S = ("firmware/extracted/a7s-fw320/payload/firmware.tar_unpacked/"
       "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
A6300 = ("firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/"
         "0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
PREFIX = b"[AIP]"
HERE = os.path.dirname(os.path.abspath(__file__))
KILL_FULL = "/tmp/opencode/pic_refs_v2.json"
KILL_SUBSET = os.path.join(HERE, "kill_refs_aip.json")

# Sub-bloques: frontera = cambio de clase en el bloque de cadenas contiguo.
# Los nombres de clase RTTI que los delimitan están en el mismo bloque de datos.
SUBBLOCKS = [
    # (nombre, primer string, ultimo string, marcador en el bloque)
    ("SaWrapper",       0x43CDD844, 0x43CDD94C, "9AudioIpIf`0x43cdd82e + 9SaWrapper`0x43cdd839 (RTTI)"),
    ("SaDriverZoomNr",  0x43CDD9E3, 0x43CDD9E3, "14SaDriverZoomNr`0x43cdda06 (RTTI, tras la cadena)"),
    ("SetFader",        0x43CDDAB5, 0x43CDDAB5, "entre 14SaDriverZoomNr y 3Abb`0x43cddaf3"),
    ("SaBackUpCtrl",    0x43CDE67A, 0x43CDE8BF, "12SaBackUpCtrl`0x43cde564 (RTTI)"),
    ("SaDriverBase",    0x43CDE900, 0x43CDE97C, "12SaDriverBase`0x43cde8f1 (RTTI)"),
    ("LPS",             0x43CDEA9E, 0x43CDEC50, "tras 10SaSysvCtrl`0x43cdea07 / 19SaDriverLinearPhase`0x43cdea14"),
]

VOCAB = ["Ack", "Comp", "Ok", "OK", "Err", "errCode", "errState", "ErrCode",
         "ErrStatus", "uniqueId", "Cmd", "Func", "Unq", "Zma", "Ext", "Mbx",
         "bkId", "id num", "Cb", "Lps", "LPS", "Sa", "ZNR", "ANR", "fader"]


def u16(data, vaddr):
    return struct.unpack_from("<H", data, vaddr - BASE)[0]


def u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def cstr(data, vaddr, limit=400):
    o = vaddr - BASE
    e = o
    while e < len(data) and e < o + limit and 32 <= data[e] < 127:
        e += 1
    return data[o:e].decode("latin1")


def extract(data, prefix=PREFIX):
    out = []
    start = 0
    while True:
        i = data.find(prefix, start)
        if i < 0:
            break
        e = i
        while e < len(data) and 32 <= data[e] < 127:
            e += 1
        out.append({"vaddr": BASE + i, "off": i,
                    "text": data[i:e].decode("latin1")})
        start = i + 1
    return out


def ldr_before(data, add_vaddr, reg, maxgap=0x20):
    """`ldr reg, [pc, #imm]` más cercano hacia atrás (gap par, 2..maxgap)."""
    o = add_vaddr - BASE
    for g in range(2, maxgap + 1, 2):
        if o - g < 0:
            return None
        h = u16(data, BASE + o - g)
        if (h & 0xF800) == 0x4800 and ((h >> 8) & 7) == reg:
            pool = ((BASE + o - g + 4) & ~3) + (h & 0xFF) * 4
            if pool - BASE + 4 <= len(data):
                return {"ldr": BASE + o - g, "pool": pool,
                        "word": u32(data, pool - BASE), "gap": g}
    return None


def pic_scan(data):
    """Todos los `add rX, pc` de la imagen; devuelve (n_adds, [(site, reg, ldr)])."""
    n = 0
    pairs = []
    for o in range(0, len(data) - 4, 2):
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFFF8) != 0x4478:          # ADD (registro) con Rm = PC
            continue
        n += 1
        reg = h & 7
        a = BASE + o
        r = ldr_before(data, a, reg)
        if r is not None:
            pairs.append((a, reg, r))
    return n, pairs


def prologues(data, lo, hi):
    out = []
    a = lo
    while a < hi:
        o = a - BASE
        h = struct.unpack_from("<H", data, o)[0]
        if (h & 0xFF00) == 0xB500 and (h & 0x0100):
            out.append(a)
            a += 2
            continue
        if h == 0xE92D and (struct.unpack_from("<H", data, o + 2)[0] & 0x4000):
            out.append(a)
        a += 2
    return out


def subblock_of(vaddr):
    for name, lo, hi, marker in SUBBLOCKS:
        if lo <= vaddr <= hi:
            return name, marker
    raise ValueError(f"{vaddr:#x} fuera de los sub-bloques declarados")


def kill_comparison(data, strings, path):
    """Pares de la kill analysis canónica para las 37 cadenas + veredicto estricto."""
    full = None
    for cand in (path, KILL_FULL, KILL_SUBSET):
        if cand and os.path.exists(cand):
            full = cand
            break
    if full is None:
        return None
    raw = json.load(open(full))
    by_vaddr = {}
    if "pairs" in raw:                      # subconjunto ya calculado
        return {"source": full, **_kill_summary(raw["pairs"], data)}
    for v in strings:
        refs = raw.get(f"0x{v['vaddr']:x}")
        if refs:
            by_vaddr[v["vaddr"]] = refs
    pairs = []
    for vaddr, refs in sorted(by_vaddr.items()):
        for site in refs:
            site = int(site)
            reg = u16(data, site) & 7
            r = ldr_before(data, site, reg)
            got = None if r is None else (r["word"] + site + 4) & 0xFFFFFFFF
            pairs.append({"string": f"0x{vaddr:x}", "site": f"0x{site:x}",
                          "strict_target": None if got is None else f"0x{got:x}",
                          "ok": got == vaddr})
    return {"source": full, **_kill_summary(pairs, data)}


def _is_printable(data, vaddr, n=3):
    t = cstr(data, int(vaddr, 16), n)
    return len(t) >= n and t.isprintable()


def _kill_summary(pairs, data):
    n_ok = sum(1 for p in pairs if p["ok"])
    other = [p for p in pairs if not p["ok"]]
    # ¿el destino estricto erróneo cae en otra cadena imprimible o en datos?
    real = sum(1 for p in other
               if p["strict_target"] and _is_printable(data, p["strict_target"]))
    return {"pairs": len(pairs), "ok": n_ok, "wrong": len(other),
            "wrong_other_string": real,
            "wrong_not_string": len(other) - real,
            "true_sites": sorted({p["site"] for p in pairs if p["ok"]}),
            "wrong_detail": other, "pairs_detail": pairs}


def differential(path, texts):
    if not os.path.exists(path):
        return None
    blob = open(path, "rb").read()
    got = extract(blob, PREFIX)
    gtexts = [s["text"] for s in got]
    comunes = [t for t in texts if t in gtexts]
    solo_ref = [t for t in texts if t not in gtexts]
    solo_other = [t for t in gtexts if t not in texts]
    return {"path": path, "n": len(got),
            "lo": f"0x{min(s['off'] for s in got):x}" if got else None,
            "hi": f"0x{max(s['off'] for s in got):x}" if got else None,
            "comunes": len(comunes), "solo_a6000": solo_ref,
            "solo_otro": solo_other}


def main():
    data = open(BIN, "rb").read()
    strings = extract(data)
    n_adds, pairs = pic_scan(data)
    by_target = defaultdict(list)
    for site, reg, r in pairs:
        tgt = (r["word"] + site + 4) & 0xFFFFFFFF
        by_target[tgt].append({"site": site, "reg": reg, **r})

    starts = prologues(data, 0x43541000, 0x43A00000)
    only = [s for s in strings if not by_target.get(s["vaddr"])]
    rows = []
    for s in strings:
        hits = by_target.get(s["vaddr"], [])
        assert len(hits) == 1, (hex(s["vaddr"]), [hex(h["site"]) for h in hits])
        h = hits[0]
        site = h["site"]
        cand = [x for x in starts if x <= site and site - x <= 0x4000]
        func = cand[-1] if cand else None
        sb, marker = subblock_of(s["vaddr"])
        row = OrderedDict()
        row["vaddr"] = f"0x{s['vaddr']:x}"
        row["text"] = s["text"]
        row["site"] = f"0x{site:x}"
        row["func"] = f"0x{func:x}" if func else None
        row["ldr"] = f"0x{h['ldr']:x}"
        row["pool"] = f"0x{h['pool']:x}"
        row["gap"] = h["gap"]
        row["subblock"] = sb
        row["marker"] = marker
        rows.append(row)

    # mapa función -> trazas
    by_func = defaultdict(list)
    for r in rows:
        by_func[r["func"]].append(r)
    funcs = []
    for f, ss in sorted(by_func.items(), key=lambda kv: int(kv[0], 16)):
        funcs.append({"func": f, "n": len(ss),
                      "subblocks": sorted({x["subblock"] for x in ss}),
                      "first_site": min(x["site"] for x in ss),
                      "strings": [{"vaddr": x["vaddr"], "text": x["text"],
                                   "site": x["site"]} for x in ss]})

    # sub-bloques
    subs = []
    for name, lo, hi, marker in SUBBLOCKS:
        ss = [r for r in rows if r["subblock"] == name]
        subs.append({"name": name, "n": len(ss), "lo": f"0x{lo:x}",
                     "hi": f"0x{hi:x}", "marker": marker,
                     "functions": sorted({r["func"] for r in ss})})

    vocab = Counter()
    for s in strings:
        for tok in VOCAB:
            if tok in s["text"]:
                vocab[tok] += 1

    kill = kill_comparison(data, strings, sys.argv[1] if len(sys.argv) > 1 else None)
    a7s = differential(A7S, [s["text"] for s in strings])
    a6300 = differential(A6300, [s["text"] for s in strings])

    counts = {
        "strings": len(strings),
        "strings_range": [f"0x{strings[0]['vaddr']:x}",
                          f"0x{strings[-1]['vaddr']:x}"],
        "pic_sites_strict": sum(len(by_target.get(s["vaddr"], [])) for s in strings),
        "strings_referenced": len([s for s in strings if by_target.get(s["vaddr"])]),
        "dead_strings": [f"0x{s['vaddr']:x}" for s in only],
        "add_rX_pc_image": n_adds,
        "add_rX_pc_with_ldr": len(pairs),
        "targets_in_block": len([1 for t in by_target
                                 if 0x43CDD844 <= t <= 0x43CDEC50]),
        "functions": len(funcs),
        "subblocks": len(subs),
        "file_offsets": [f"0x{strings[0]['off']:x}",
                         f"0x{strings[-1]['off']:x}"],
    }
    out = OrderedDict()
    out["milestone"] = "S121"
    out["module"] = "AIP"
    out["module_reading"] = "Audio IP (evidencia: RTTI 9AudioIpIf/9SaWrapper y [AudioIp]/[AudioIP] del mismo bloque)"
    out["binary"] = BIN
    out["base"] = f"0x{BASE:x}"
    out["counts"] = counts
    out["strings"] = rows
    out["functions"] = funcs
    out["subblocks"] = subs
    out["vocabulary"] = dict(vocab)
    out["pic_rule"] = ("add rX,pc (0x4478) + ldr rX,[pc,#imm] más cercano hacia atrás "
                       "mismo registro; destino = word_del_pool + (dir_add + 4)")
    out["kill_analysis"] = kill
    out["a7s_fw320"] = a7s
    out["a6300_fw201"] = a6300
    out["not_verified"] = [
        "desarrollo de las siglas AIP, SA, LPS, ANR, ZNR, Zma, Ext, Mbx",
        "semántica de cada valor de errState/ErrStatus/result_code",
        "significado de los campos bkId, id num, uniqueId, Unq, Func",
        "el formato exacto de los mensajes y de la cola AudioIpCmdQueue",
        "si SetFader y SetAudioNrType comparten el mismo objeto SaWrapper",
    ]
    json.dump(out, open(os.path.join(HERE, "aip.json"), "w"), indent=1,
              ensure_ascii=False)
    if kill is not None and os.path.exists(KILL_FULL) and not os.path.exists(KILL_SUBSET):
        json.dump({"module": "AIP",
                   "rule": "kill analysis v2 (analysis/s106_imaging_cap/scan_pic_refs_v2.py)",
                   "pairs": kill["pairs_detail"]},
                  open(KILL_SUBSET, "w"), indent=1, ensure_ascii=False)

    print(json.dumps({k: v for k, v in counts.items() if k != "dead_strings"}, indent=1))
    print("sub-bloques:", [(s["name"], s["n"]) for s in subs])
    print("funciones:", len(funcs))
    if kill:
        print("kill analysis:", {k: kill[k] for k in
                                 ("pairs", "ok", "wrong", "wrong_other_string",
                                  "wrong_not_string")})
    for name, d in (("A7S", a7s), ("A6300", a6300)):
        if d:
            print(name, {k: d[k] for k in ("n", "lo", "hi", "comunes")},
                  "solo_a6000:", d["solo_a6000"], "solo_otro:", len(d["solo_otro"]))


if __name__ == "__main__":
    main()
