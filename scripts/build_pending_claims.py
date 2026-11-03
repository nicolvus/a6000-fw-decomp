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
    static = sum(r[2] == "estático" for r in rows)
    out = ["# Pendientes de verificación — registro exhaustivo", "",
           ("Generado por `scripts/build_pending_claims.py`; no editar a mano. Complementa [PENDIENTES.md](PENDIENTES.md) (índice maestro) "
           "con **todas** las afirmaciones marcadas `NO_VERIFICADO`, `CONFLICTO_PENDIENTE` o `Falta:` en `docs/capture/` y todas las etiquetas del censo sin cubrir."), "",
           f"- Afirmaciones abiertas: **{len(rows)}** en {len({r[0] for r in rows})} informes ({static} clasificadas estáticas, {len(rows) - static} físicas/externas).",
           f"- Etiquetas del censo sin cubrir: **{len(labs)}**.",
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
        out += [f"- **V-{rows.index(r) + 1:04d}** [{r[0]}:{r[1]}](capture/{r[0]}#L{r[1]}) — {r[3]}" for r in sel]
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(), encoding="utf-8")
    print(OUT, len(claims()), len(labels()))
