#!/usr/bin/env python3
"""Regenera el bloque generado de docs/INDEX.md: informes de docs/capture/ por subsistema.

Uso: python3 scripts/knowledge/build_subsystem_index.py [--check]
Cada informe aparece en una sola categoría (la primera regla que casa con su nombre), con sus pruebas
(tests/test_s<N>_*.py) y su evidencia (analysis/s<N>*/). --check falla si el índice está desactualizado.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INDEX = ROOT / "docs" / "INDEX.md"
BEGIN, END = "<!-- BEGIN:GENERATED -->", "<!-- END:GENERATED -->"

CATEGORIES = {
    1: "Pipeline de captura (botón, RecordStill/RecordImage, LIRO, RAW/JPEG, almacenamiento)",
    2: "Sensor e imager (IMX210/IMX235, registros, estados, drive modes)",
    3: "Obturador (cortinas, EFCS, SilentShutter, exposición electrónica completa)",
    4: "Control y comunicación (OSAL, colas, mensajes, callbacks, libObj, servicios)",
    5: "Procesamiento de imagen (DFE, CISIF, Scalar/SFRA, YC, DSP, SDF, DMM)",
    6: "Otros subsistemas (AF, estabilización, vídeo, audio, lentes, energía, visor, accesorios, módulos de trazas)",
    7: "Comparaciones A6000 / A7S / A6300 y controles positivos",
    8: "Herramientas, metodología, validación y coordinación",
}

# (categoría, regex sobre el nombre del archivo sin .md); gana la primera que casa.
RULES: list[tuple[int, str]] = [
    (8, r"^(?!liveview)(PENDIENTES_FINALES|RESEARCH_TASKS|pending-sync|repo-audit|rea-independent|linea-general|s178|s403-censo|s403-cierre|S605-S627|s20-s19-corr|s20-rtti|s146|s145|s51-static|s51-deepseek|s62-|s128|s130|s104|custom-fw|camera-reset|.*parallel.*|.*verdict)"),
    (7, r"^(a6300-|a7s-silent|s52-|s53-darwin-a7s|s55-bionz-gpio|s56-imx235|s57-imx235|s58-a7s|s385|s401|s135|s168|s169|s171|s172|s201|s202|s204|s206|s207|s208|s301|s302|s307|s309|s311|s312|s332|s333)"),
    (3, r"^(efcs-|imager-exposure|silent-|shutter-investigation|tesis-|electronic-still|fm3-gpio|darwin-|rea-tema3|s19-12|s19-mechanical|s50-|s51-|s53-|s54-(bionz|mech|p4c|conclusions)|s55-(exposure|gpio|conclusions)|s56-conclusions|s57-(ssb|xpi)|s56-imx210-electronic|s101|s64|s65|s402|physical-test|s17-a-e-p)"),
    (1, r"^(record-still|recordstill|encodestill|fea-|liveview-|mpr-dcf|objstillpool|objstillrecorder|pool-write|sony-dcf|capture-stage|capture-static|static-closure|shutter-trigger|research-plan|s16-codex-fea|s16-liveview|s17-codex-d|s17-main|s18-codex-h|s19-(dcf|fea|07-cbid|stage|post-s2|13)|s19-0[678]|s20-(codex-mpr|p4-stillc|p5|rawplay)|s21-|s29-|s30-|s54-capture|s105|s106|s114|s123|s403-e2-)"),
    (4, r"^(s18-(claude-a|claude-b|claude-c|claude-d|connect|main)|s17-(claude-b|public)|s19-(domain|s2|camerasequence|lifecycle|objid53|liro)|s19-0[123]|s20-(claude-topology|mailbox|p1|row78)|s20-p4-corr|s24-|s25-|s28-|s380|s381|s382|s383|s384|s174|s107|s112|s126|s403-e15|queue-40193|s19-codex-continuous|s20-claude-auto|s20-codex-mpr|s17-claude-a|branch-claude)"),
    (2, r"^(imx210-|s1(4[0-2]|4[5-7]|49|50|5[2-5]|5[7-9]|6[0-3])-|s115|s124|s129|s134|s143|s144|s171|s176|s205|s205|s3[0-9]{2}|s4[0-9]-|s5[6-9]-|s6[01]-|rea-tema[12]|s56-(imx210|sens|exp|cisif)|s55-(imx210|sens)|s54-imx210|s403-e14)"),
    (5, r"^(s1(08|09|10|13|16|17|18|19|20|37|39)-|s179|s197|s22-|s23-|s26-|s27-|s3[1-9]-|s16-|s17-codex-c|s18-codex|s19-(camera|sfra|11|objeffect)|s20-p3|sfra-|branch-codex|objhandover|objscalar|yc-unit|claude-main|s603|s604|s601|s103|s56-cisif)"),
]
FALLBACK = 6


def category(stem: str) -> int:
    for cat, rx in RULES:
        if re.search(rx, stem):
            return cat
    return FALLBACK


def title(path: Path) -> str:
    m = re.search(r"^#\s+(.+)$", path.read_text(errors="replace")[:1500], re.M)
    return (m.group(1) if m else path.stem).strip().replace("|", "/")


def related(kind: str, n: str) -> list[str]:
    base = ROOT / ("tests" if kind == "tests" else "analysis")
    pat = re.compile(rf"^(test_)?s{n}(?!\d)")
    out = sorted(p for p in base.iterdir() if pat.match(p.name) and p.suffix in ("", ".py") and p.name != "__pycache__")
    return [f"[{p.name}](../{p.relative_to(ROOT).as_posix()})" for p in out[:3]] + ([f"+{len(out) - 3}"] if len(out) > 3 else [])


def row(path: Path) -> str:
    stem = path.stem
    m = re.match(r"^[sS](\d+)", stem)
    ident = f"S{m.group(1)}" if m else "—"
    extra = []
    if m:
        for label, kind in (("pruebas", "tests"), ("evidencia", "analysis")):
            links = related(kind, m.group(1))
            if links:
                extra.append(f"{label}: " + " ".join(links))
    suffix = " · " + " · ".join(extra) if extra else ""
    return f"- **{ident}** [{title(path)}](capture/{path.name}){suffix}"


def build() -> str:
    docs = sorted(p for p in (ROOT / "docs" / "capture").glob("*.md") if p.name != "README.md")
    groups: dict[int, list[Path]] = {c: [] for c in CATEGORIES}
    for p in docs:
        groups[category(p.stem)].append(p)
    out = []
    for c, name in CATEGORIES.items():
        out.append(f"### {c}. {name}\n\n{len(groups[c])} informes.\n")
        out.extend(row(p) for p in groups[c])
        out.append("")
    return "\n".join(out)


def main() -> int:
    text = INDEX.read_text()
    head, rest = text.split(BEGIN, 1)
    tail = rest.split(END, 1)[1]
    new = f"{head}{BEGIN}\n\n{build()}\n{END}{tail}"
    if "--check" in sys.argv:
        return 0 if new == text else 1
    INDEX.write_text(new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
