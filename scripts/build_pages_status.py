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
CATALOG = ROOT / "docs" / "capture" / "linea-general-re.md"
TOP = 30
FILL = {"m-hito": COLORS["hito"], "m-sub": COLORS["sub"], "m-todo": COLORS["todo"], "s-ok": COLORS["ok"],
        "s-cancel": COLORS["cancel"], "s-todo": COLORS["todo"], "t-todo": COLORS["todo"]}
KIND = {"hito": "m-hito", "sub-etiqueta": "m-sub", "pendiente": "m-todo"}


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
    tests = [("t-todo", f"P{n}: sin ejecutar") for n in range(1, data["physical_tests"]["total"] + 1)]
    cov = data["module_coverage"]
    return [
        (f"Módulos de la fw 3.21*: {cov['percent']}% ({cov['covered']}/{cov['total']})", "modules", modules),
        (f"Sesiones documentadas: {len(done)}/{data['latest_number']}", "sessions", sessions),
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
        n = sum(i["estado"] != "pendiente" for _, i in items)
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
a{{color:#58a6ff}}h2{{font-size:1.1rem;margin:24px 0 8px;color:#fff}}
.grid{{display:grid;grid-template-columns:repeat({COLS},1fr);gap:2px}}
.cell{{aspect-ratio:1;border-radius:2px;display:inline-block;width:11px;height:11px;margin:1px}} .grid .cell{{width:auto;height:auto;margin:0}} {css}
table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #30363d;padding:2px 8px;text-align:left}}
td:nth-child(n+3):not(:last-child),td:last-child,th:nth-child(n+3){{text-align:right}}.sq{{line-height:0;width:60%}}
.legend span{{display:inline-block;width:12px;height:12px;border-radius:2px;margin:0 4px 0 12px}}
@media(max-width:600px){{.grid{{grid-template-columns:repeat(31,1fr)}}}}</style></head><body>
<h1>Progreso</h1>
<p class="legend"><span class="m-hito"></span>módulo con hito<span class="m-sub"></span>sub-etiqueta cubierta<span class="m-todo"></span>pendiente / sin informe / sin ejecutar<span class="s-cancel"></span>cancelada</p>
<h2>Módulos por familia — {cov['percent']}% ({cov['covered']}/{cov['total']})*</h2>
<table><tr><th>Familia</th><th>Etiquetas</th><th>Cubiertas</th><th>Total</th><th>%</th></tr>{fam_rows}</table>
<h2>Prioridad de investigación (top {TOP} pendientes)</h2>
<p>Ordenadas por cadenas de texto referenciadas en el firmware de la A6000: más cadenas = más código por descifrar.</p>
<table><tr><th>#</th><th>Etiqueta</th><th>Cadenas</th><th>Apariciones</th><th>Presencia</th></tr>{prio}</table>
<h2>Módulos decodificados</h2>
<table><tr><th>Etiqueta</th><th>Nombre</th><th>Hitos</th></tr>{done_rows}</table>
{other}
<p>*Censo <a href="{cov['source']}">S178</a>; pasa el ratón por un cuadrado para ver su etiqueta. Nombres tomados del
<a href="https://github.com/nicolvus/a6000-fw-decomp/blob/main/docs/capture/linea-general-re.md">catálogo de hitos</a>;
las pendientes aún no tienen nombre funcional. Generado por
<a href="https://github.com/nicolvus/a6000-fw-decomp/blob/main/scripts/build_pages_status.py">scripts/build_pages_status.py</a>.
Datos crudos: <a href="../status.json">status.json</a>.</p>
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
        "physical_tests": {
            "done": 0, "total": 21,
            "source": REPO + "docs/capture/physical-test-plan.md",
            "sources": [REPO + "docs/capture/" + name for name in (
                "physical-test-plan.md", "s402-physical-test-mapping.md", "physical-test-plan-2.md",
            )],
        },
        "decision": {"label": "No parchear: evidencia insuficiente", "source": REPO + "docs/capture/s51-decision.md"},
    }
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ROOT / "site" / "progress").mkdir(exist_ok=True)
    grids = groups(data)
    src_dir = ROOT / "docs" / "progress"
    (src_dir / "index.html").write_text(render_html(grids, data), encoding="utf-8")
    (ROOT / "site" / "progress" / "progress.svg").write_text(render_svg(grids), encoding="utf-8")  # solo en Pages, no versionado
    shutil.copyfile(src_dir / "index.html", ROOT / "site" / "progress" / "index.html")
    # Shields "endpoint" JSON: README badges read these from Pages, so they follow every deploy.
    cov, tests = data["module_coverage"], data["physical_tests"]
    for name, label, msg, color in (
        ("modulos", "módulos", f"{cov['percent']}% ({cov['covered']}/{cov['total']})", "yellow"),
        ("sesiones", "sesiones", f"{len(sessions)}/{data['latest_number']}", "blue"),
        ("pruebas", "pruebas físicas", f"{tests['done']}/{tests['total']}", "lightgrey"),
    ):
        badge = {"schemaVersion": 1, "label": label, "message": msg, "color": color}
        (ROOT / "site" / f"badge-{name}.json").write_text(json.dumps(badge, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(sessions)} sesiones documentadas; última {data['latest']}; salida {OUTPUT}")


if __name__ == "__main__":
    main()
