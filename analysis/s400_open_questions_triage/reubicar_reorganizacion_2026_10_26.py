"""Traslada el triaje de las aristas cuyo marcador pasó a un archivo histórico (reorganización del 26-10-2026).

README.md y docs/STATE.md se archivaron sin cambiar su texto (salvo enlaces relativos) en docs/history/, con 2 líneas de cabecera.
Cada fila ya revisada a mano se copia con la fuente nueva, conservando veredicto y motivo; `revision_fuente` pasa a ser el commit
que introdujo el archivo (argumento). Falla si queda alguna arista sin origen: esas deben revisarse a mano.

Uso: python -m analysis.s400_open_questions_triage.reubicar_reorganizacion_2026_10_26 <sha del commit del archivo histórico>
"""

import json
import sys

from analysis.s400_open_questions_triage import extend_triage as x

P = x.P
ARCHIVOS = {
    "docs/history/README-historial-2026-10-26.md": "README.md",
    "docs/history/STATE-historial-2026-10-26.md": "docs/STATE.md",
}


def pendientes(triage: list[dict]) -> list[dict]:
    vistos = {x.identity(r) for r in triage}
    out = []
    for line in (x.ROOT / "docs" / "OPEN-QUESTIONS.md").read_text(encoding="utf-8").splitlines():
        if m := x.ROW.match(line):
            c = {"fuente": m[4], "fuente_actual": m[4], "destino": m[1], "tipo": m[2], "status_grafo": m[3], **x.citation(m[4], m[5])}
            if x.identity(c) not in vistos:
                out.append(c)
    return out


def main(revision: str) -> None:
    triage = json.loads(P.read_text(encoding="utf-8"))
    por_origen = {(r.get("fuente_actual", r["fuente"]), r["destino"], r.get("tipo")): r for r in triage}
    nuevas = []
    for c in pendientes(triage):
        path, _, num = c["fuente"].rpartition(":")
        origen = por_origen.get((f"{ARCHIVOS[path]}:{int(num) - 2}", c["destino"], c["tipo"])) if path in ARCHIVOS else None
        if not origen:
            raise SystemExit(f"arista sin origen que trasladar; revisar a mano: {c['fuente']} -> {c['destino']}")
        nuevas.append({**origen, "fuente": c["fuente"], "fuente_actual": c["fuente"], "cita": c["cita"], "contexto": c["contexto"],
                       "revision_fuente": revision, "reubicada_desde": f"{ARCHIVOS[path]}:{int(num) - 2}"})
    P.write_text(json.dumps(triage + nuevas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(nuevas), len(triage) + len(nuevas))


if __name__ == "__main__":
    main(sys.argv[1])
