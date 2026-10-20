---
name: knowledge-maintenance
description: Reindexar, reconstruir el grafo o regenerar los documentos derivados (CORRECTIONS.md, OPEN-QUESTIONS.md) del sistema de conocimiento Sony A6000 tras editar o crear documentación. Úsala después de modificar cualquier .md en docs/reports/analysis/references/research o CONTEXT.md/README.md.
---

# Mantenimiento del índice y el grafo (Sony A6000)

## Cuándo se activa

Después de crear, editar o eliminar cualquier `.md` indexado, o un JSON de
funciones en `analysis/`; cuando una búsqueda devuelve datos obsoletos;
antes de regenerar `docs/CORRECTIONS.md`/`docs/OPEN-QUESTIONS.md`.

## Procedimiento (orden obligatorio)

```bash
source .venv/bin/activate   # desde la raíz del repo
python3 scripts/knowledge/index_docs.py       # 1. reindexa Markdown (incremental, SHA-256)
python3 scripts/knowledge/build_graph.py      # 2. reconstruye entidades/relaciones
python3 scripts/knowledge/export_corrections.py  # 3. regenera los .md derivados
python3 scripts/knowledge/index_docs.py       # 4. reindexa los .md derivados que acaban de cambiar
python3 scripts/knowledge/build_graph.py      # 5. confirma estabilidad (debe dar el mismo total)
```

El paso 4/5 es necesario porque `docs/CORRECTIONS.md`/`docs/OPEN-QUESTIONS.md`
cambian de contenido en el paso 3 y deben reindexarse; el grafo excluye
explícitamente estos dos archivos como fuente de relaciones (`GENERATED_DOCS`
en `build_graph.py`), así que el paso 5 debe dar el MISMO total que el paso 2 —
si no, hay una regresión del bug de autocontaminación ya corregido una vez.

## Entradas / salidas

Sin parámetros (opera sobre todo el repo). Salida: conteo de archivos/secciones/
entidades/relaciones actualizados, impreso por cada script.

## Herramientas disponibles

`scripts/knowledge/index_docs.py --rebuild` (fuerza reindexado completo, ignora hashes),
`build_graph.py`, `export_corrections.py`. Tests: `python -m pytest tests/knowledge -q`.

## Limitaciones

- No reanaliza binarios ni reejecuta Ghidra/REA: solo reindexa Markdown y JSON
  ya existentes. Si falta un análisis, generarlo primero con las herramientas
  correspondientes de `scripts/` (fuera del alcance de esta skill).
- `ruff`/`mypy`/`pytest` solo existen en `.venv/` del proyecto (ver
  `knowledge/requirements-dev.txt`); no están instalados globalmente.

## Validaciones

Después de reconstruir, correr `python -m pytest tests/knowledge -q` y
`ruff check scripts/knowledge tests/knowledge` si se tocó código Python (no solo
documentación). Si el total de relaciones del paso 5 difiere del paso 2 sin que
hayas editado ningún documento real entre medias, hay un bug: no continuar sin
diagnosticarlo.

## Referencias bajo demanda

`knowledge/PROGRESS.md` — historial de fases e incidencias ya resueltas.
