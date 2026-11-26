"""Build the public, documentation-only milestone index for GitHub Pages."""

from __future__ import annotations

import json
import re
import shutil
import sys
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DETAIL = ROOT / "analysis" / "s178_census" / "census_detalle.json"
PROGRESS = ROOT / "analysis" / "s178_census" / "census.md"
REGISTRY = ROOT / "docs" / "capture" / "registro-pruebas-camara.md"
REPO = "https://github.com/nicolvus/a6000-fw-decomp/blob/main/"
WIKI = "https://github.com/nicolvus/a6000-fw-decomp/wiki/"
# P1–P24: inventario de physical-test-review-2026-10-26.md (P22–P24 añadidos ese día).
PLANS = 24
SESSION = re.compile(r"(?:^|/)s(\d{1,3})(?:[-_/]|\.md$)", re.IGNORECASE)
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def title(path: Path) -> str:
    match = HEADING.search(path.read_text(encoding="utf-8", errors="replace")[:3000])
    return match.group(1).strip().replace("`", "") if match else path.stem.replace("-", " ")


COLORS = {"hito": "#2ea043", "sub": "#9be9a8", "todo": "#30363d", "cancel": "#d29922", "ok": "#2ea043"}
COLS = 62
CATALOG = ROOT / "docs" / "capture" / "linea-general-re.md"
JOINT = {74: "S74 — ADJ_CMD (informe conjunto S73/S74)", 516: "S516 — `[PNL]` (informe conjunto S515/S516/S628–S630)",
         628: "S628 — `[FILE_NUM]` (informe conjunto S515/S516/S628–S630)", 629: "S629 — `[FSYSMODE]` (informe conjunto S515/S516/S628–S630)",
         630: "S630 — `[RING_DIAL]` (informe conjunto S515/S516/S628–S630)"}
FILL = {"m-hito": COLORS["hito"], "m-sub": COLORS["sub"], "m-todo": COLORS["todo"], "s-ok": COLORS["ok"],
        "s-cancel": COLORS["cancel"], "s-todo": COLORS["todo"], "t-todo": COLORS["todo"], "t-ok": COLORS["ok"],
        "m-rejected": "#6e7681", "m-ver": "#1f6feb"}
KIND = {"hito": "m-hito", "sub-etiqueta": "m-sub", "pendiente": "m-todo", "no-modulo": "m-rejected"}


def topics(sessions: list[dict] | None = None) -> dict[str, str]:
    """Session number -> topic name: the milestone catalogue, else the session report's own title."""
    out = {}
    for item in sessions or []:
        out[item["id"][1:]] = re.sub(r"^S\d+\s*[—-]\s*(el módulo\s*)?", "", item["title"]).replace("`", "")
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        row = re.match(r"\| (S\d+(?:/S\d+)?) \| ([^|]+) \|", line)
        if row:
            for num in re.findall(r"\d+", row.group(1)):
                out[num] = row.group(2).strip().replace("`", "")
    return out


def families(detail: dict) -> list[tuple[str, list[tuple[str, dict]]]]:
    """Group labels by prefix; families of fewer than 3 labels go to 'OTROS'."""
    by: dict[str, list[tuple[str, dict]]] = {}
    for label, info in detail.items():
        by.setdefault(label.strip("[]").split("_")[0], []).append((label, info))
    big = {k: v for k, v in by.items() if len(v) >= 3}
    loose = [x for k, v in by.items() if k not in big for x in v]
    rows = sorted(big.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    return [(k, sorted(v)) for k, v in rows] + ([("OTROS", sorted(loose))] if loose else [])


OPEN_CLAIM = re.compile(r"NO[ _]VERIFICADO", re.IGNORECASE)
DONE_CLAIM = re.compile(r"(?<!NO )(?<!NO_)\bVERIFICADO(?:_ESTATICO)?\b")


# Leyenda que define las etiquetas de estado (p. ej. «Etiquetas: V = … · N = no verificado»); no es una afirmación.
# Mantener igual en review_reports.py, build_pending_claims.py y build_pages_status.py.
LEGEND = re.compile(r"^\s*(?:Etiquetas?|Leyenda|Convención|Estados?)\b.*[=:]", re.IGNORECASE)


def is_legend(line: str) -> bool:
    return bool(LEGEND.search(line)) and line.count("=") >= 2


def claim_counts(detail: dict, sessions: list[dict]) -> dict[str, tuple[int, int]]:
    """Label -> (NO_VERIFICADO, VERIFICADO) mentions in its report(s); sub-labels follow their parent.

    shortcut: counts text mentions, not distinct claims (a table row and its prose count twice);
    refine per claim if the ratio is used for decisions.
    """
    path = {x["id"][1:]: ROOT / x["source"].split("/main/", 1)[1] for x in sessions}
    counts: dict[str, tuple[int, int]] = {}
    for label, info in detail.items():
        reports = {path.get(h) for h in info["hitos"] if h != "178"}
        if info["estado"] == "hito" and reports and all(r and r.exists() for r in reports):
            texts = ["\n".join(x for x in r.read_text(encoding="utf-8", errors="replace").splitlines() if not is_legend(x))
                     for r in reports]
            counts[label] = (sum(len(OPEN_CLAIM.findall(t)) for t in texts), sum(len(DONE_CLAIM.findall(t)) for t in texts))
    for _ in range(3):  # sub-labels may hang from other sub-labels
        for label, info in detail.items():
            if info["estado"] == "sub-etiqueta" and info["sub_de"] and label not in counts \
                    and info["sub_de"][0] in counts and all(p in counts for p in info["sub_de"]):
                counts[label] = counts[info["sub_de"][0]]
    return counts


def closed_labels(detail: dict, sessions: list[dict]) -> set[str]:
    """Covered labels whose report(s) carry no NO_VERIFICADO mention (even a negated one counts as open)."""
    return {k for k, (o, _) in claim_counts(detail, sessions).items() if o == 0}


def real_progress(detail: dict, sessions: list[dict]) -> dict:
    """Weighted index: each covered label contributes VERIFICADO/(VERIFICADO+NO_VERIFICADO); uncovered ones 0."""
    counts = claim_counts(detail, sessions)
    index = sum(v / (o + v) if o + v else 1 for o, v in counts.values()) / len(detail)
    return {"index": f"{100 * index:.2f}", "by_label": {k: {"open": o, "verified": v} for k, (o, v) in sorted(counts.items())}}


def hitos(info: dict) -> list[str]:
    """Sessions with their own report; S178 is the census itself, not a report on the label."""
    return [h for h in info["hitos"] if h != "178"]


def tip(label: str, info: dict, names: dict[str, str]) -> str:
    name = " / ".join(dict.fromkeys(names[h] for h in hitos(info) if h in names))
    extra = f" S{', S'.join(hitos(info))}" if hitos(info) else ""
    return f"{label}: {info['estado']}{extra}" + (f" — {name}" if name else "")


def groups(data: dict) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """(title, summary, [(css class, tooltip)]) for each grid of the board."""
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    names = topics(data["sessions"])
    modules = [(KIND[i["estado"]], tip(k, i, names)) for _, fam in families(detail) for k, i in fam]
    done = {int(x["id"][1:]) for x in data["sessions"]}
    sessions = [
        ("s-ok", f"S{n}: documentada") if n in done else
        ("s-cancel", f"S{n}: cancelada") if n == 67 else ("s-todo", f"S{n}: número sin informe (numeración paralela)")
        for n in range(1, data["latest_number"] + 1)
    ]
    run = set(data["physical_tests"]["executed"])
    tests = [("t-ok", f"P{n}: con prueba registrada") if n in run else ("t-todo", f"P{n}: sin prueba registrada")
             for n in range(1, data["physical_tests"]["total"] + 1)]
    cov = data["module_coverage"]
    return [
        (f"Cobertura documental de etiquetas*: {cov['percent']}% ({cov['covered']}/{cov['total']})", "modules", modules),
        (f"Sesiones S con informe: {len(done)} (numeradas hasta S{data['latest_number']}; los números salieron de trabajo en paralelo, un hueco no es una sesión pendiente) y {data['phase_reports']} informes de fase E", "sessions", sessions),
        (f"Pruebas físicas: {data['physical_tests']['done']}/{data['physical_tests']['total']}", "tests", tests),
    ]


def render_svg(grids) -> str:
    out, y = [], 0
    for title, _, cells in grids:
        out.append(f'<text x="4" y="{y + 21}" font-family="sans-serif" font-size="16" fill="#fff">{escape(title)}</text>')
        for i, (cls, tooltip) in enumerate(cells):
            x, row = 1 + (i % COLS) * 16, y + 31 + (i // COLS) * 16
            out.append(f'<rect x="{x}" y="{row}" width="14" height="14" rx="2" fill="{FILL[cls]}"><title>{escape(tooltip)}</title></rect>')
        y += 31 + -(-len(cells) // COLS) * 16 + 14
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {y}" width="1000" height="{y}">'
            f'<rect width="1000" height="{y}" fill="#0d1117"/>\n' + "\n".join(out) + "\n</svg>\n")


def render_html(grids, data: dict) -> str:
    cov = data["module_coverage"]
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    names = topics(data["sessions"])

    def squares(cells) -> str:
        return "".join(f'<span class="cell {c}" role="img" aria-label="{escape(t)}" title="{escape(t)}"></span>' for c, t in cells)

    closed = closed_labels(detail, data["sessions"])
    fam_rows = ""
    for fam, items in families(detail):
        n = sum(i["estado"] in {"hito", "sub-etiqueta"} for _, i in items)
        v = sum(k in closed for k, _ in items)
        cells = [("m-ver" if k in closed else KIND[i["estado"]], tip(k, i, names)) for k, i in items]
        fam_rows += (f'<tr><td>{escape(fam)}</td><td class="sq">{squares(cells)}</td>'
                     f"<td>{n}</td><td>{v}</td><td>{len(items)}</td><td>{round(100 * n / len(items))}%</td></tr>")

    rp = data["real_progress"]
    other = "".join(f"<h2>{escape(t)}</h2><div class='grid'>{squares(c)}</div>" for t, _, c in grids[2:])
    css = " ".join(f".{c}{{background:{f}}}" for c, f in FILL.items())
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sony A6000 FW RE — progreso</title>
<style>body{{font-family:sans-serif;max-width:1000px;margin:auto;padding:16px;background:#0d1117;color:#c9d1d9}}
a{{color:#58a6ff}}.hito{{border:1px solid #2ea043;background:#12261a;padding:8px 12px;border-radius:6px}}h2{{font-size:1.1rem;margin:24px 0 8px;color:#fff}}
.grid{{display:grid;grid-template-columns:repeat({COLS},1fr);gap:2px}}
.cell{{aspect-ratio:1;border-radius:2px;display:inline-block;width:11px;height:11px;margin:1px}} .grid .cell{{width:auto;height:auto;margin:0}} {css}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #30363d;padding:2px 8px;text-align:left}}
td:nth-child(n+3):not(:last-child),td:last-child,th:nth-child(n+3){{text-align:right}}.sq{{line-height:0;width:60%}}
.legend span{{display:inline-block;width:12px;height:12px;border-radius:2px;margin:0 4px 0 12px}}
@media(max-width:600px){{.grid{{grid-template-columns:repeat(31,1fr)}}}}</style></head><body>
<h1>Progreso</h1>
<p class="hito"><b>Obturador electrónico funcionando desde el 3.30</b> (envío en línea de <code>pkt[0x0e]</code> + compuerta de Darwin) y Silent calibrado en el firmware desde el 3.77. El 3.23 (Darwin tipo 0 + B1a, 2 bytes) fue el primer hito: la cámara disparó sin mover el obturador mecánico el 27-10-2026. Guía de réplica: <a href="{WIKI}">Wiki CFW Sony a6000</a>.</p>
<h2>Estado actual (25-11-2026)</h2>
<table><tr><th>Pieza</th><th>Estado</th><th>Detalle</th></tr>
<tr><td>Obturador electrónico</td><td><b>Funciona</b></td><td>Desde el 3.30; exposición calibrada en el 3.35 y Silent nivelado de 1/1250 a 1/50 desde el 3.77 (<a href="{REPO}docs/capture/e26-r54-paquete-330-envio-pkt0e.md">R54</a>, <a href="{REPO}docs/capture/e26-r87-disparo-remoto-y-recalibracion.md">R87</a>).</td></tr>
<tr><td>EFCS</td><td><b>Negro desde 1/1000</b></td><td>≈1,27 ms perdidos, también con firmware de Sony: causa física, no de firmware (<a href="{REPO}docs/capture/e26-r74-conclusion-final-efcs-negro.md">R74</a>, <a href="{REPO}docs/capture/e26-r83-informe-final-efcs-negro.md">R83</a>).</td></tr>
<tr><td>Serie 3.93</td><td>Una build por función</td><td>Silent + Film Simulation, Picture Profile, Extra Fine o ISO por separado; <code>iso</code> deja la cámara en bucle de arranque (<a href="{REPO}docs/gui/g105-builds-por-funcion.md">G105</a>).</td></tr>
<tr><td>Serie 4.0x</td><td>Bisección del vídeo</td><td>4.01 y 4.02 instaladas; 4.03 y 4.04 construidas y auditadas, sin instalar.</td></tr>
<tr><td>Vídeo (FILM-PB-1)</td><td><b>Abierto</b></td><td>Los clips se ven en el PC y la cámara no los reproduce; causa probable: el selector PAL/NTSC frente a la cadencia, ajuste no expuesto en el menú (<a href="{REPO}reports/film-pb-1-causa-sistema-tv-20261127.md">informe</a>).</td></tr>
<tr><td>Recuperación física (SWD)</td><td><b>Cerrada (03-11-2026)</b></td><td>Se fuerza un registro de CPU y el actualizador de fábrica instala por USB sin escribir NAND (<a href="{REPO}docs/capture/e26-r49-cierre-recuperacion-326.md">R49</a>, <a href="{WIKI}15-Recuperacion-SWD-experimental">wiki 15</a>). Sin recuperación independiente del firmware de Darwin.</td></tr>
<tr><td>Paquetes .dat</td><td>No se publican</td><td>Se construyen desde el 3.21 oficial con los scripts del repositorio (<a href="{WIKI}4-Construir-los-paquetes">wiki 4</a>).</td></tr>
</table>
<h2>Qué falta</h2>
<table><tr><th>Área</th><th>Pendiente</th><th>Bloqueo</th></tr>
<tr><td>Cobertura de etiquetas</td><td>Todas las etiquetas documentadas (372/372); documentada no implica decodificada.</td><td>Trabajo de análisis</td></tr>
<tr><td>Vídeo en el CFW</td><td>FILM-PB-1: los clips grabados no se reproducen en la cámara; falta el paso físico que separa selector PAL/NTSC, arranque en frío y catálogo.</td><td>Acceso a la cámara</td></tr>
<tr><td>Darwin por actualización oficial</td><td>E23: puerta Silent y parcheo de <code>0640_darwin</code> (CRC-32 único control); F6: sin ruta demostrada (decisión S51).</td><td>Abierto</td></tr>
<tr><td>Interfaz (GUI)</td><td>G2–G8: formatos <code>.uxc/.uxb/.xdb</code>, menús, texto y fuentes, entrada, ajustes y modificación reversible de la UI.</td><td>Abierto</td></tr>
<tr><td>Cadena sensor / obturador</td><td>E6 (Darwin fuera de <code>av-cam</code>), E9/D5 (registros IMX210/IMX235), E11 (segunda cortina), E13 (servicio ODL), F8 (valores solo en ejecución).</td><td>Hojas de datos, volcado de Darwin o prueba física</td></tr></table>
<p>Detalle y criterios de cierre: <a href="{REPO}docs/PENDIENTES.md">PENDIENTES.md</a>.</p>
<h2>Avance real: {rp['index']}%</h2>
<p>Índice ponderado sobre {cov['total']} etiquetas: cada etiqueta cubierta aporta <code>VERIFICADO / (VERIFICADO + NO_VERIFICADO)</code> según su informe. Cobertura documental: mide documentación, no código descompilado ni funciones comprobadas en cámara.</p>
<h2>Etiquetas por familia: {cov['percent']}% documentadas ({cov['covered']}/{cov['total']}), {cov['verified_percent']}% sin pendientes ({cov['verified']}/{cov['total']})</h2>
<p class="legend"><span class="m-ver"></span>documentada y sin pendientes<span class="m-hito"></span>módulo con hito, con pendientes<span class="m-sub"></span>sub-etiqueta cubierta, con pendientes<span class="m-todo"></span>pendiente / sin informe / sin ejecutar<span class="m-rejected"></span>fragmento descartado<span class="s-cancel"></span>cancelada</p>
<table><tr><th>Familia</th><th>Etiquetas</th><th>Con hito</th><th>Sin pendientes</th><th>Total</th><th>% doc.</th></tr>{fam_rows}</table>
{other}
<p>Pruebas en cámara: {data['physical_tests']['done']}/{data['physical_tests']['total']} planes con prueba (<a href="{data['physical_tests']['source']}">registro</a>). Censo <a href="{cov['source']}">S178</a>; pasa el ratón por un cuadrado para ver su etiqueta. Generado por <code>scripts/build_pages_status.py</code>; datos en <a href="../status.json">status.json</a>.</p>
</body></html>
"""


def physical_tests() -> dict:
    """Pruebas en cámara del registro: planes P con alguna prueba y número de registros T."""
    rows = [line.split("|") for line in REGISTRY.read_text(encoding="utf-8").splitlines() if re.match(r"^\| T\d{3}", line)]
    plans = {int(n) for row in rows for n in re.findall(r"\bP(\d{1,2})\b", row[3]) if 1 <= int(n) <= PLANS}
    return {
        "done": len(plans), "total": PLANS, "executed": sorted(plans), "registered": len(rows), "last": rows[-1][1].strip(),
        "source": REPO + "docs/capture/registro-pruebas-camara.md",
    }


def main(out: Path = ROOT) -> None:
    """Escribe `site/` y `docs/progress/` bajo `out` (por defecto la raíz del repositorio)."""
    # The catalogue points to a representative document, not to a claim of completion.
    candidates: dict[int, tuple[int, Path]] = {}
    for folder, priority in (("docs/capture", 0), ("analysis", 1)):
        for path in sorted((ROOT / folder).rglob("*.md")):
            relative = path.relative_to(ROOT)
            match = SESSION.search(relative.as_posix())
            if not match:
                continue
            number = int(match.group(1))
            if not 1 <= number <= 999:
                continue
            score = priority + (2 if "conclusion" not in path.stem and "report" not in path.stem else 0)
            score += bool(re.match(r"s\d+-s\d+", path.stem, re.IGNORECASE))  # un informe de rango pierde frente al propio
            if number not in candidates or (score, len(relative.parts)) < (
                candidates[number][0], len(candidates[number][1].parts)
            ):
                candidates[number] = (score, relative)

    # S73/S74 share a report; S67 was cancelled in the general RE catalogue.
    candidates[74] = candidates[73]
    # S515/S516 and S628–S630 share one report (the loop above only sees its first number).
    for number in (516, 628, 629, 630):
        candidates[number] = (0, Path("docs/capture/s515-s516-s628-s630-modulos.md"))

    sessions = [
        {
            "id": f"S{number}",
            "title": JOINT.get(number) or title(ROOT / path),
            "source": REPO + path.as_posix(),
        }
        for number, (_, path) in sorted(candidates.items(), reverse=True)
    ]
    census = PROGRESS.read_text(encoding="utf-8")
    coverage = re.search(r"\*\*(\d+)/(\d+)\*\* = \*\*([\d.,]+) %\*\*", census)
    pending = re.search(r"\| \*\*pendientes reales\*\* \| \*\*(\d+)\*\*", census)
    if not coverage or not pending:
        raise ValueError("No se pudo leer la cobertura de S178")
    covered, total, percent = coverage.groups()
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    excluded = sum(i["estado"] == "no-modulo" for i in detail.values())
    closed = closed_labels(detail, sessions)
    if int(covered) + int(pending.group(1)) + excluded != int(total):
        raise ValueError("El censo S178 no suma cobertura, pendientes y descartadas")

    data: dict = {
        "generated_from": "Documentos versionados en docs/capture/ y analysis/",
        "latest": sessions[0]["id"] if sessions else None,
        "documented_count": len(sessions),
        "latest_number": int(sessions[0]["id"][1:]),
        "sessions": sessions,
        "module_coverage": {
            "covered": int(covered), "total": int(total),
            "pending": int(pending.group(1)), "excluded": excluded, "percent": percent,
            "verified": len(closed), "verified_percent": f"{100 * len(closed) / int(total):.2f}",
            "source": REPO + "analysis/s178_census/census.md",
        },
        "real_progress": real_progress(detail, sessions),
        "exceptions": {
            "S67": {
                "label": "Cancelada; el tema de AF se asignó a S63.",
                "source": REPO + "docs/capture/linea-general-re.md",
            }
        },
        "physical_tests": physical_tests(),
        # Since E21 the work is numbered by phase (E21–E26 and their sub-reports), not by S session.
        "phase_reports": len(list((ROOT / "docs" / "capture").glob("e[0-9]*.md"))),
        "decision": {"label": "S51 (estático): A=NO, B=NO, C=NO", "source": REPO + "docs/capture/s51-decision.md"},
    }
    site = out / "site"
    output = site / "status.json"
    site.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (site / "progress").mkdir(exist_ok=True)
    grids = groups(data)
    src_dir = out / "docs" / "progress"
    src_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "index.html").write_text(render_html(grids, data), encoding="utf-8")
    (site / "progress" / "progress.svg").write_text(render_svg(grids), encoding="utf-8")  # solo en Pages, no versionado
    shutil.copyfile(src_dir / "index.html", site / "progress" / "index.html")
    # Shields "endpoint" JSON: README badges read these from Pages, so they follow every deploy.
    cov, tests = data["module_coverage"], data["physical_tests"]
    for name, label, msg, color in (
        ("modulos", "etiquetas documentadas", f"{cov['percent']}% ({cov['covered']}/{cov['total']}) · sin pendientes {cov['verified']}", "yellow"),
        ("sesiones", "sesiones", f"S {len(sessions)} · E {data['phase_reports']}", "blue"),
        ("pruebas", "planes con prueba", f"{tests['done']}/{tests['total']}", "green"),
    ):
        badge = {"schemaVersion": 1, "label": label, "message": msg, "color": color}
        (site / f"badge-{name}.json").write_text(json.dumps(badge, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(sessions)} sesiones documentadas; última {data['latest']}; salida {output}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
