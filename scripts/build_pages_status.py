"""Build the public, documentation-only milestone index for GitHub Pages."""

from __future__ import annotations

import json
import re
import shutil
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "site" / "status.json"
DETAIL = ROOT / "analysis" / "s178_census" / "census_detalle.json"
PROGRESS = ROOT / "analysis" / "s178_census" / "census.md"
REPO = "https://github.com/nicolvus/a6000-fw-decomp/blob/main/"
SESSION = re.compile(r"(?:^|/)s(\d{1,3})(?:[-_/]|\.md$)", re.IGNORECASE)
HEADING = re.compile(r"^#\s+(.+)$", re.MULTILINE)


def title(path: Path) -> str:
    match = HEADING.search(path.read_text(encoding="utf-8", errors="replace")[:3000])
    return match.group(1).strip() if match else path.stem.replace("-", " ")


COLORS = {"hito": "#2ea043", "sub": "#9be9a8", "todo": "#30363d", "cancel": "#d29922", "ok": "#2ea043"}
COLS = 62


def groups(data: dict) -> list[tuple[str, str, list[tuple[str, str]]]]:
    """(title, summary, [(css class, tooltip)]) for each grid of the board."""
    detail = json.loads(DETAIL.read_text(encoding="utf-8"))
    kind = {"hito": "hito", "sub-etiqueta": "sub", "pendiente": "todo"}
    modules = [
        (f"m-{kind[v['estado']]}", f"{k}: {v['estado']}" + (f" S{', S'.join(v['hitos'])}" if v["hitos"] else ""))
        for k, v in sorted(detail.items(), key=lambda kv: (kv[1]["estado"] != "hito", kv[1]["estado"] != "sub-etiqueta", kv[0]))
    ]
    done = {int(x["id"][1:]) for x in data["sessions"]}
    sessions = [
        ("s-ok", f"S{n}: documentada") if n in done else
        ("s-cancel", f"S{n}: cancelada") if n == 67 else ("s-todo", f"S{n}: sin informe propio")
        for n in range(1, data["latest_number"] + 1)
    ]
    tests = [("t-todo", f"P{n}: sin ejecutar") for n in range(1, data["physical_tests"]["total"] + 1)]
    cov = data["module_coverage"]
    return [
        (f"Módulos de la fw 3.21*: {cov['percent']}% ({cov['covered']}/{cov['total']})", "modules", modules),
        (f"Sesiones documentadas: {len(done)}/{data['latest_number']}", "sessions", sessions),
        (f"Pruebas físicas: {data['physical_tests']['done']}/{data['physical_tests']['total']}", "tests", tests),
    ]


FILL = {"m-hito": COLORS["hito"], "m-sub": COLORS["sub"], "m-todo": COLORS["todo"], "s-ok": COLORS["ok"],
        "s-cancel": COLORS["cancel"], "s-todo": COLORS["todo"], "t-todo": COLORS["todo"]}


def render_svg(grids) -> str:
    out, y = [], 0
    for title, _, cells in grids:
        out.append(f'<text x="4" y="{y + 21}" font-family="sans-serif" font-size="16" fill="#fff">{escape(title)}</text>')
        for i, (cls, tip) in enumerate(cells):
            x, row = 1 + (i % COLS) * 16, y + 31 + (i // COLS) * 16
            out.append(f'<rect x="{x}" y="{row}" width="14" height="14" rx="2" fill="{FILL[cls]}"><title>{escape(tip)}</title></rect>')
        y += 31 + -(-len(cells) // COLS) * 16 + 14
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 {y}" width="1000" height="{y}">'
            f'<rect width="1000" height="{y}" fill="#0d1117"/>\n' + "\n".join(out) + "\n</svg>\n")


def render_html(grids, data: dict) -> str:
    cov, src = data["module_coverage"], data["module_coverage"]["source"]
    body = "".join(
        f'<h2>{escape(t)}</h2><div class="grid">' + "".join(f'<span class="cell {c}" title="{escape(tip)}"></span>' for c, tip in cells) + "</div>"
        for t, _, cells in grids
    )
    css = " ".join(f".{c}{{background:{f}}}" for c, f in FILL.items())
    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sony A6000 FW RE — progreso</title>
<style>body{{font-family:sans-serif;max-width:1000px;margin:auto;padding:16px;background:#0d1117;color:#c9d1d9}}
a{{color:#58a6ff}}h2{{font-size:1.1rem;margin:20px 0 8px;color:#fff}}
.grid{{display:grid;grid-template-columns:repeat({COLS},1fr);gap:2px}}
.cell{{aspect-ratio:1;border-radius:2px}} {css}
@media(max-width:600px){{.grid{{grid-template-columns:repeat(31,1fr)}}}}
table{{border-collapse:collapse}}th,td{{border:1px solid #30363d;padding:2px 8px}}td+td,th+th{{text-align:right}}
.legend span{{display:inline-block;width:12px;height:12px;border-radius:2px;margin:0 4px 0 12px}}</style></head><body>
<h1>Progreso</h1>
<p class="legend"><span class="m-hito"></span>módulo con hito<span class="m-sub"></span>sub-etiqueta cubierta<span class="m-todo"></span>pendiente / sin informe / sin ejecutar<span class="s-cancel"></span>cancelada</p>
{body}
<table><tr><th>Etiquetas de módulo</th><th>N</th></tr>
<tr><td>Cubiertas</td><td>{cov['covered']}</td></tr><tr><td>Pendientes reales</td><td>{cov['pending']}</td></tr>
<tr><td>Total</td><td>{cov['total']}</td></tr></table>
<p>*Censo <a href="{src}">S178</a>; pasa el ratón por un cuadrado para ver su etiqueta. Generado por
<a href="https://github.com/nicolvus/a6000-fw-decomp/blob/main/scripts/build_pages_status.py">scripts/build_pages_status.py</a>
a partir de los informes versionados. Datos crudos: <a href="../status.json">status.json</a>.</p>
</body></html>
"""


def main() -> None:
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
    if int(covered) + int(pending.group(1)) != int(total):
        raise ValueError("El censo S178 no suma cobertura y pendientes")

    data = {
        "generated_from": "Documentos versionados en docs/capture/ y analysis/",
        "latest": sessions[0]["id"] if sessions else None,
        "documented_count": len(sessions),
        "latest_number": int(sessions[0]["id"][1:]),
        "sessions": sessions,
        "module_coverage": {
            "covered": int(covered), "total": int(total),
            "pending": int(pending.group(1)), "percent": percent,
            "source": REPO + "analysis/s178_census/census.md",
        },
        "exceptions": {
            "S67": {
                "label": "Cancelada; el tema de AF se asignó a S63.",
                "source": REPO + "docs/capture/linea-general-re.md",
            }
        },
        "physical_tests": {"done": 0, "total": 8, "source": REPO + "docs/capture/physical-test-plan.md"},
        "decision": {"label": "No parchear: evidencia insuficiente", "source": REPO + "docs/capture/s51-decision.md"},
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "site" / "progress").mkdir(exist_ok=True)
    grids = groups(data)
    src_dir = ROOT / "docs" / "progress"
    (src_dir / "progress.svg").write_text(render_svg(grids), encoding="utf-8")
    (src_dir / "index.html").write_text(render_html(grids, data), encoding="utf-8")
    for name in ("index.html", "progress.svg"):
        shutil.copyfile(src_dir / name, ROOT / "site" / "progress" / name)
    print(f"{len(sessions)} sesiones documentadas; última {data['latest']}; salida {OUTPUT}")


if __name__ == "__main__":
    main()
