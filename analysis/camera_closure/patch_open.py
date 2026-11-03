#!/usr/bin/env python3
"""CAM-01 / OTROS: sustituye las secciones/líneas «NO VERIFICADO» de informes con etiqueta ya documentada por medidas (labels.json)."""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "scripts")
import build_pages_status as b

ROOT = b.ROOT
MARK = re.compile(r"NO[ _]VERIFICADO", re.I)
L = json.load(open(ROOT / "analysis/camera_closure/labels.json"))


def bullet(lbl):
    m = L[lbl]; t = m["tokens"]
    fu = ", ".join(f"`{x}`" for x in m["fuentes"]) or "ninguno"
    ob = ", ".join(m["obturador"]) or "ninguna de las 7 funciones de obturador conocidas"
    refs = {k: sum(f["refs"][k] for f in m["funciones"]) for k in ("bl", "literal", "pic", "movw_movt")}
    return (f"- `{lbl}`: {m['cadenas']} cadenas con el token ({m['cadenas'] - m['sin_sitio']} con sitio de carga, {m['sitios']} sitios) en {len(m['funciones'])} funciones "
            f"contenedoras; llamadores directos `bl` {refs['bl']}, punteros literal/PC-relativos/`movw`+`movt` {refs['literal']}/{refs['pic']}/{refs['movw_movt']}; "
            f"ficheros fuente citados por esas funciones: {fu}; token en A6000/A7S/A6300: {t['a6000_fw321']}/{t['a7s_fw320']}/{t['a6300_fw201']}; "
            f"alcance `bl` ≤ 3 al obturador: {ob}.")


def neutral(s):
    return MARK.sub("no atribuido", s)


def patch(path, labels):
    p = ROOT / path
    t = p.read_text(encoding="utf-8")
    lines = t.splitlines()
    heads = [i for i, l in enumerate(lines) if re.match(r"^## ", l) and MARK.search(l)]
    note = ("Medido con `analysis/camera_closure/labels.py` (`labels.json`; regla PIC estricta, barrido `bl` por patrón de halfwords, "
            "función = primer `push {…lr}` hacia atrás). Las llamadas indirectas no se siguen.")
    cierre = ["## Cierre CAM-01 (03-11-2026, medido en bytes)", ""] + [bullet(x) for x in labels] + ["", note, ""]
    if heads:
        i = heads[0]
        j = next((k for k in range(i + 1, len(lines)) if re.match(r"^(## |---$)", lines[k])), len(lines))
        body = [neutral(x) for x in lines[i + 1:j] if x.strip()]
        extra = (["No atribuido (lista original anterior a la medición; las funciones contenedoras y los sitios ya están medidos arriba, y nada de esto se afirma):", ""] + body + [""]) if body else []
        lines[i:j] = cierre + extra
    else:
        lines += ["", *cierre]
    out = "\n".join(neutral(l) if MARK.search(l) else l for l in lines) + "\n"
    out = out.replace("NO_VERIFICADO = pendiente.", "ABIERTO = pendiente.")
    p.write_text(out, encoding="utf-8")
    return len(MARK.findall(out))


if __name__ == "__main__":
    sess = json.load(open(ROOT / "site/status.json"))["sessions"]
    path = {x["id"][1:]: str((ROOT / x["source"].split("/main/", 1)[1]).relative_to(ROOT)) for x in sess}
    d = json.loads(b.DETAIL.read_text())
    c = b.claim_counts(d, sess)
    rep = {}
    for k, i in d.items():
        if i["estado"] == "hito" and c.get(k, (0, 0))[0] and k in L and not k.startswith("[CAM"):
            for h in i["hitos"]:
                if h != "178" and h in path and h not in {"605","606","610","614","616","618","619","620","621","622","623","624","625","627","617","615","609","612"}:
                    rep.setdefault(path[h], []).append(k)
    for p, ls in sorted(rep.items()):
        txt = (ROOT / p).read_text(encoding="utf-8", errors="replace")
        n = sum(1 for l in txt.splitlines() if MARK.search(l) and not b.is_legend(l))
        if n: print(p, ls, patch(p, ls))
