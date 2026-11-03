"""Genera docs/PENDIENTES-VERIFICACION.md: cada afirmación sin verificar de docs/capture y cada etiqueta sin cubrir."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/PENDIENTES-VERIFICACION.md"
CLAIM = re.compile(r"NO[ _]VERIFICADO|CONFLICTO_PENDIENTE|\bFalta:", re.IGNORECASE)
# shortcut: palabras clave, no análisis de la afirmación; revisar a mano las dudosas.
PHYSICAL = re.compile(
    r"cámara real|en cámara|hardware|físic|osciloscop|hoja de datos|datasheet|prueba real|ejecución real|"
    r"telnet|sonda|medi[rc]|SWD|UART|volcado|en ejecución|runtime|dinámic|trazas? de bus|bus físico", re.IGNORECASE)
LIMIT = 230


REVIEW = ROOT / "analysis/review_reports/review.json"


def review() -> dict:
    return json.loads(REVIEW.read_text(encoding="utf-8")) if REVIEW.exists() else {"closable": [], "pending_unmarked": []}


def claims() -> list[tuple[str, int, str, str]]:
    rows = []
    for path in sorted((ROOT / "docs/capture").glob("*.md")):
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if CLAIM.search(line):
                text = re.sub(r"\s+", " ", line.strip(" |*-")).replace("|", "¦")
                kind = "físico/externo" if PHYSICAL.search(line) else "estático"
                rows.append((path.name, n, kind, text[:LIMIT] + ("…" if len(text) > LIMIT else "")))
    return rows


def labels() -> list[str]:
    detail = json.loads((ROOT / "analysis/s178_census/census_detalle.json").read_text(encoding="utf-8"))
    pend = sorted(((k, v) for k, v in detail.items() if v["estado"] == "pendiente"),
                  key=lambda kv: (-kv[1]["cadenas_referenciadas"], kv[0]))
    return [f"- `{k}` — {v['cadenas_referenciadas']} cadenas, {v['apariciones_token']} apariciones"
            f"{', solo A6000' if v['solo_a6000'] else ''}. Cierre (estático): informe de evidencia de cadenas con "
            f"direcciones, cargas PC-relativas y llamadores verificados contra `av-cam.bin`." for k, v in pend]


def render() -> str:
    rows, labs = claims(), labels()
    rev = review()
    tier_a = {(c["file"].removeprefix("docs/capture/"), c["line"]) for c in rev["closable"] if c["tier"] == "A"}
    seen = {(r[0], r[1]) for r in rows}
    extra = [p for p in rev["pending_unmarked"]
             if p["file"].startswith("docs/capture/") and (p["file"].split("/")[-1], p["line"]) not in seen]
    static = sum(r[2] == "estático" for r in rows)
    out = ["# Pendientes de verificación — registro exhaustivo", "",
           ("Generado por `scripts/build_pending_claims.py`; no editar a mano. Complementa [PENDIENTES.md](PENDIENTES.md) (índice maestro) "
           "con **todas** las afirmaciones marcadas `NO_VERIFICADO`, `CONFLICTO_PENDIENTE` o `Falta:` en `docs/capture/` y todas las etiquetas del censo sin cubrir."), "",
           f"- Afirmaciones abiertas: **{len(rows)}** en {len({r[0] for r in rows})} informes ({static} clasificadas estáticas, {len(rows) - static} físicas/externas).",
           f"- Etiquetas del censo sin cubrir: **{len(labs)}**; pendientes sin marca (sección D): **{len(extra)}**; candidatos a cerrar (⟳): **{len(tier_a)}**.",
           ("- Clase `estático`: se puede cerrar con `av-cam.bin`, REA/Ghidra y los documentos, sin cámara. Clase `físico/externo`: pide cámara, medición, hoja de datos o volcado. "
           "La clase sale de palabras clave y puede errar; una afirmación puede ser estática en parte."),
           "- Cada línea es una mención de texto, no necesariamente una afirmación distinta. Cierre de cada una: evidencia en bytes/instrucciones que la confirme o la corrija, y retirar la marca en su informe.", "",
           f"## A. Etiquetas sin cubrir ({len(labs)})", "",
           ("Todas son verificables estáticamente. Cierre de cada una: informe de evidencia de cadenas con direcciones, cargas PC-relativas y llamadores comprobados contra `av-cam.bin` (modelo: [S631](capture/s631-imaging_img.md)), "
           "o padre demostrado para pasarla a sub-etiqueta. Ordenadas por cadenas referenciadas."), ""] + labs
    for kind, title in (("estático", "B. Afirmaciones abiertas verificables estáticamente"),
                        ("físico/externo", "C. Afirmaciones abiertas que piden cámara, medición o documento externo")):
        sel = [r for r in rows if r[2] == kind]
        out += ["", f"## {title} ({len(sel)})", ""]
        out += [f"- **V-{rows.index(r) + 1:04d}** [{r[0]}:{r[1]}](capture/{r[0]}#L{r[1]})"
                f"{' ⟳ candidato a cerrar' if (r[0], r[1]) in tier_a else ''} — {r[3]}" for r in sel]
    out += ["", f"## D. Pendientes sin marca `NO_VERIFICADO` ({len(extra)})", "",
            ("Líneas de `docs/capture/` con «falta», «por hacer» o «sin verificar» que no llevan la marca; salen de "
            "[la revisión automática](../analysis/review_reports/RESUMEN.md) y son candidatas a marcar o a convertir en tarea."), ""]
    out += [f"- **W-{n:04d}** [{p['file'].split('/')[-1]}:{p['line']}](capture/{p['file'].split('/')[-1]}#L{p['line']}) — {p['text'][:LIMIT]}"
            for n, p in enumerate(extra, 1)]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(OUT, len(claims()), len(labels()))
