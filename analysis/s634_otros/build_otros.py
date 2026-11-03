#!/usr/bin/env python3
"""S634: etiquetas del censo S178 que seguían pendientes (familia OTROS): tabla medida y estado en el censo.

Lee analysis/camera_closure/labels.json (generado por run_labels.py) y escribe docs/capture/s634-otros-pendientes.md,
analysis/s634_otros/otros.json y actualiza analysis/s178_census/*.
"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
L = json.load(open(ROOT / "analysis/camera_closure/labels.json"))
P = {k: v for k, v in L.items() if v["estado_previo"] == "pendiente"}


def main():
    rows = []
    for k, v in sorted(P.items(), key=lambda kv: -kv[1]["cadenas"]):
        t = v["tokens"]; fu = ", ".join(f"`{x}`" for x in v["fuentes"]) or "—"
        refs = {r: sum(f["refs"][r] for f in v["funciones"]) for r in ("bl", "literal", "pic", "movw_movt")}
        rows.append(f"| `{k}` | {v['cadenas']} | {v['sitios']} | {len(v['funciones'])} | {refs['bl']} | {refs['literal']}/{refs['pic']}/{refs['movw_movt']} | "
                    f"{t['a6000_fw321']}/{t['a7s_fw320']}/{t['a6300_fw201']} | {fu} | {', '.join(v['obturador']) or '—'} |")
    sin = [k for k, v in P.items() if v["cadenas"] and not v["sitios"]]
    md = f"""# S634 — etiquetas pendientes de la familia OTROS: evidencia medida de cadenas, funciones y referencias

**03-11-2026.** Documenta las {len(P)} etiquetas del censo S178 que seguían pendientes (todas las que quedaban fuera de las familias con tres o más etiquetas). Mide, para cada una y sobre `av-cam.bin` (A6000 fw3.21, base `0x43541000`), lo que se puede comprobar con bytes; no atribuye significado a ninguna sigla ni módulo. Es el mismo criterio que los informes de evidencia de cadenas S605–S631.

Datos: [otros.json](../../analysis/s634_otros/otros.json). Generador: `analysis/camera_closure/labels.py` y `analysis/s634_otros/build_otros.py`. Prueba: [test_s634_otros.py](../../tests/test_s634_otros.py).

## Método (VERIFICADO contra bytes)

- **Cadenas:** todas las cadenas NUL-terminadas de `av-cam.bin` que contienen el token `[ETIQUETA]`.
- **Sitios:** cargas `ldr rX,[pc,#imm]` + `add rX,pc` (regla estricta del repo) cuyo destino cae en la cadena, antes o en el token.
- **Función contenedora:** primer `push {{…,lr}}` hacia atrás (≤ 0x2000 B). **Llamadores:** `bl`/`blx`/`b.w` directos, por patrón de halfwords. **Punteros:** literal de 32 bits (con o sin bit Thumb) / `ldr`+`add pc` en la misma función / `movw`+`movt`.
- **Fuentes:** cadenas `.cpp/.h/.c` desnudas cargadas dentro de esas funciones. **Obturador:** alcance por `bl` directo hasta profundidad 3 a las 7 funciones de obturador conocidas (C3-B, productor de `r5`, `SetExposure`, `SetRead`, constructor normal, EFCS, BULB).
- **Modelos:** coincidencias exactas del token en `av-cam.bin` de A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01.

## Resultados

| Etiqueta | Cadenas | Sitios | Funciones | `bl` | Punteros lit/pic/movw | Token A6000/A7S/A6300 | Fuentes citadas | Obturador |
|---|---:|---:|---:|---:|---|---|---|---|
{chr(10).join(rows)}

Etiquetas con cadenas pero sin ningún sitio de carga: {', '.join('`'+k+'`' for k in sorted(sin)) or 'ninguna'}. Ninguna de las {len(P)} alcanza por `bl` directo (profundidad ≤ 3) una de las 7 funciones de obturador conocidas: {'se cumple' if not any(v['obturador'] for v in P.values()) else 'excepciones en la columna Obturador'}; [S51](s51-decision.md) se mantiene.

## Alcance

Los nombres de las etiquetas son texto del firmware. Este informe no afirma qué hace cada módulo, ni expande siglas, ni compara cuerpos de función entre modelos (solo la presencia del token), ni sigue llamadas indirectas (vtable, tablas indexadas o registros calculados). No se ejecutó firmware.

## Reproducción

```bash
.venv/bin/python analysis/camera_closure/run_labels.py
.venv/bin/python analysis/s634_otros/build_otros.py
.venv/bin/python -m pytest -q tests/test_s634_otros.py
```
"""
    (ROOT / "docs/capture/s634-otros-pendientes.md").write_text(md, encoding="utf-8")
    json.dump(P, open(ROOT / "analysis/s634_otros/otros.json", "w"), indent=1, ensure_ascii=False)
    print(len(P), "etiquetas;", len(sin), "sin sitio")


if __name__ == "__main__":
    main()
