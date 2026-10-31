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
# P1–P24: inventario de physical-test-review-2026-10-26.md (P22–P24 añadidos ese día).
PLANS = 24
SESSION = re.compile(r"(?:^|/)s(\d{1,3})(?:[-_/]|\.md$)", re.IGNORECASE)
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def title(path: Path) -> str:
    match = HEADING.search(path.read_text(encoding="utf-8", errors="replace")[:3000])
    return match.group(1).strip() if match else path.stem.replace("-", " ")


COLORS = {"hito": "#2ea043", "sub": "#9be9a8", "todo": "#30363d", "cancel": "#d29922", "ok": "#2ea043"}
COLS = 62
CATALOG = ROOT / "docs" / "capture" / "linea-general-re.md"
TOP = 30
FILL = {"m-hito": COLORS["hito"], "m-sub": COLORS["sub"], "m-todo": COLORS["todo"], "s-ok": COLORS["ok"],
        "s-cancel": COLORS["cancel"], "s-todo": COLORS["todo"], "t-todo": COLORS["todo"], "t-ok": COLORS["ok"],
        "m-rejected": "#6e7681"}
KIND = {"hito": "m-hito", "sub-etiqueta": "m-sub", "pendiente": "m-todo", "no-modulo": "m-rejected"}


def topics() -> dict[str, str]:
    """Session number -> topic name, read from the milestone catalogue."""
    out = {}
    for line in CATALOG.read_text(encoding="utf-8").splitlines():
        row = re.match(r"\| (S\d+(?:/S\d+)?) \| ([^|]+) \|", line)
        if row:
            for num in re.findall(r"\d+", row.group(1)):
                out[num] = row.group(2).strip()
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


def tip(label: str, info: dict, names: dict[str, str]) -> str:
    name = " / ".join(dict.fromkeys(names.get(h, "") for h in info["hitos"] if names.get(h)))
    extra = f" S{', S'.join(info['hitos'])}" if info["hitos"] else ""
    return f"{label}: {info['estado']}{extra}" + (f" — {name}" if name else "")


def groups(data: dict) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """(title, summary, [(css class, tooltip)]) for each grid of the board."""
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    names = topics()
    modules = [(KIND[i["estado"]], tip(k, i, names)) for _, fam in families(detail) for k, i in fam]
    done = {int(x["id"][1:]) for x in data["sessions"]}
    sessions = [
        ("s-ok", f"S{n}: documentada") if n in done else
        ("s-cancel", f"S{n}: cancelada") if n == 67 else ("s-todo", f"S{n}: sin informe propio")
        for n in range(1, data["latest_number"] + 1)
    ]
    run = set(data["physical_tests"]["executed"])
    tests = [("t-ok", f"P{n}: con prueba registrada") if n in run else ("t-todo", f"P{n}: sin prueba registrada")
             for n in range(1, data["physical_tests"]["total"] + 1)]
    cov = data["module_coverage"]
    return [
        (f"Cobertura documental de etiquetas*: {cov['percent']}% ({cov['covered']}/{cov['total']})", "modules", modules),
        (f"Sesiones S documentadas: {len(done)}/{data['latest_number']} (más {data['phase_reports']} informes de fase E)", "sessions", sessions),
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
    names = topics()
    link = {s["id"]: s["source"] for s in data["sessions"]}

    def squares(cells) -> str:
        return "".join(f'<span class="cell {c}" title="{escape(t)}"></span>' for c, t in cells)

    fam_rows = ""
    for fam, items in families(detail):
        n = sum(i["estado"] in {"hito", "sub-etiqueta"} for _, i in items)
        cells = [(KIND[i["estado"]], tip(k, i, names)) for k, i in items]
        fam_rows += (f'<tr><td>{escape(fam)}</td><td class="sq">{squares(cells)}</td>'
                     f"<td>{n}</td><td>{len(items)}</td><td>{round(100 * n / len(items))}%</td></tr>")

    pend = sorted(((k, i) for k, i in detail.items() if i["estado"] == "pendiente"),
                  key=lambda kv: (-kv[1]["cadenas_referenciadas"], -kv[1]["apariciones_token"], kv[0]))[:TOP]
    prio = "".join(
        f'<tr class="prio"><td>{n}</td><td>{escape(k)}</td><td>{i["cadenas_referenciadas"]}</td>'
        f'<td>{i["apariciones_token"]}</td><td>{"solo A6000" if i["solo_a6000"] else "también A7S/A6300"}</td></tr>'
        for n, (k, i) in enumerate(pend, 1)
    )
    done_rows = "".join(
        f"<tr><td>{escape(k)}</td><td>{escape(' / '.join(dict.fromkeys(names[h] for h in i['hitos'] if h in names)))}</td><td>"
        + ", ".join(f'<a href="{link[f"S{h}"]}">S{h}</a>' if f"S{h}" in link else f"S{h}" for h in i["hitos"])
        + "</td></tr>"
        for k, i in sorted(detail.items()) if i["estado"] == "hito"
    )
    other = "".join(f"<h2>{escape(t)}</h2><div class='grid'>{squares(c)}</div>" for t, _, c in grids[1:])
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
<p class="hito"><b>Hito (27-10-2026): la A6000 disparó en silencio</b> con el firmware modificado 3.23 (Darwin tipo 0 + B1a, 2 bytes), según confirmó el usuario. <b>Estado actual:</b> tras instalar el 3.25 integrado la cámara no arranca (testimonio del usuario); la recuperación se investiga offline (E26). <a href="{REPO}README.md">README</a> · <a href="{REPO}docs/capture/e26-recovery.md">E26</a>.</p>
<p class="legend"><span class="m-hito"></span>módulo con hito<span class="m-sub"></span>sub-etiqueta cubierta<span class="m-todo"></span>pendiente / sin informe / sin ejecutar<span class="m-rejected"></span>fragmento descartado<span class="s-cancel"></span>cancelada</p>
<p>{cov['pending']} etiquetas pendientes; {cov['excluded']} fragmentos descartados como módulos. Descartar no aumenta cobertura.</p>
<p>Cobertura documental de etiquetas: no mide código descompilado ni funciones verificadas.
<a href="{REPO}docs/capture/repo-audit-2026-10-24.md">Auditoría y pendientes vigentes</a>.
Pruebas en cámara: {data['physical_tests']['registered']} registros (hasta {data['physical_tests']['last']}, con backup NVRAM previo);
planes P1–P24 con prueba registrada: {data['physical_tests']['done']}/{data['physical_tests']['total']}.
<a href="{data['physical_tests']['source']}">Registro de pruebas</a>.</p>
<h2>Etiquetas por familia — {cov['percent']}% ({cov['covered']}/{cov['total']})*</h2>
<table><tr><th>Familia</th><th>Etiquetas</th><th>Cubiertas</th><th>Total</th><th>%</th></tr>{fam_rows}</table>
<h2>Etiquetas pendientes (top {TOP} por cadenas referenciadas)</h2>
<p>Orden documental por cadenas con referencias candidatas; no demuestra volumen de código,
prioridad técnica ni relación con el obturador. La cola técnica está en la auditoría.</p>
<table><tr><th>#</th><th>Etiqueta</th><th>Cadenas</th><th>Apariciones</th><th>Presencia</th></tr>{prio}</table>
<h2>Etiquetas con informe propio</h2>
<table><tr><th>Etiqueta</th><th>Nombre</th><th>Hitos</th></tr>{done_rows}</table>
{other}
<p>*Censo <a href="{cov['source']}">S178</a>; pasa el ratón por un cuadrado para ver su etiqueta. Nombres tomados del
<a href="https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/linea-general-re.md">catálogo de hitos</a>;
las pendientes aún no tienen nombre funcional. Generado por
<a href="https://github.com/nicolvus/a6000-fw-decomp/blob/main/scripts/build_pages_status.py">scripts/build_pages_status.py</a>.
Datos crudos: <a href="../status.json">status.json</a>.</p>
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
            if number not in candidates or (score, len(relative.parts)) < (
                candidates[number][0], len(candidates[number][1].parts)
            ):
                candidates[number] = (score, relative)

    # S73/S74 share a report; S67 was cancelled in the general RE catalogue.
    candidates[74] = candidates[73]

    sessions = [
        {
            "id": f"S{number}",
            "title": "S74 — ADJ_CMD (informe conjunto S73/S74)" if number == 74 else title(ROOT / path),
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
            "source": REPO + "analysis/s178_census/census.md",
        },
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
        ("modulos", "módulos", f"{cov['percent']}% ({cov['covered']}/{cov['total']})", "yellow"),
        ("sesiones", "sesiones", f"S {len(sessions)}/{data['latest_number']} · E {data['phase_reports']}", "blue"),
        ("pruebas", "planes con prueba", f"{tests['done']}/{tests['total']}", "green"),
    ):
        badge = {"schemaVersion": 1, "label": label, "message": msg, "color": color}
        (site / f"badge-{name}.json").write_text(json.dumps(badge, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(sessions)} sesiones documentadas; última {data['latest']}; salida {output}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
