---
name: contradiction-audit
description: Averiguar si un hallazgo o documento del proyecto Sony A6000 está vigente, corregido o superado, y por qué fuente. Úsala antes de reutilizar cualquier conclusión de docs/capture/, analysis/ o CONTEXT.md como si fuera definitiva.
---

# Auditoría de contradicciones y correcciones (Sony A6000)

## Cuándo se activa

Antes de reutilizar un hallazgo técnico como verdadero; cuando el usuario pregunta
"¿qué corrigió la sesión Sxx?", "¿sigue vigente este resultado?", "¿qué supera a
este documento?"; o al detectar dos documentos con afirmaciones que podrían
contradecirse.

## Procedimiento

1. `source .venv/bin/activate` desde la raíz del repo.
2. Conclusión vigente de un documento concreto (qué lo corrige, con evidencia):
   ```bash
   python3 scripts/knowledge/search.py claim docs/capture/<doc>.md
   ```
3. Qué corrige/supera un documento (relaciones salientes):
   ```bash
   python3 scripts/knowledge/search.py graph --doc docs/capture/<doc>.md --direction out
   ```
4. Vista completa generada del grafo: leer `docs/CORRECTIONS.md` (todas las
   relaciones CORRECTS/SUPERSEDES con status, fuente y cita) y
   `docs/OPEN-QUESTIONS.md` (secciones NO_VERIFICADO/CONFLICTO_PENDIENTE).
   **No editar estos dos archivos a mano**: regenerarlos con
   `python3 scripts/knowledge/export_corrections.py` tras reindexar.
5. Nunca tratar una relación con status `NO_VERIFICADO` como si fuera
   `VERIFICADO`: el status refleja el vocabulario controlado del propio texto
   fuente, no una garantía de exactitud del extractor.

## Entradas / salidas

Entrada: ruta de documento (`.md`) relativa a la raíz del repo.
Salida: lista de relaciones con tipo (CORRECTS/SUPERSEDES/CALLS), status,
fuente (archivo:línea) y cita textual literal — nunca una relación sin evidencia.

## Herramientas disponibles

CLI: `scripts/knowledge/search.py` (`claim`, `graph`), `docs/CORRECTIONS.md`,
`docs/OPEN-QUESTIONS.md`. MCP: `query_graph`, `find_corrections`, `get_open_questions`.

## Limitaciones

- Las relaciones se extraen de forma determinista (palabras clave que el propio
  investigador escribió + enlace Markdown o referencia de sesión sin ambigüedad).
  Si una sesión corrige a otra pero el texto no usa un marcador reconocible
  (CORRECCIÓN/corrige/supera/superado) o la referencia es ambigua (>2 documentos
  candidatos con ese número de sesión), la relación NO aparecerá en el grafo —
  buscar también con `knowledge-navigation` por si la corrección está en prosa.
- Solo hay entidades `Function`/`CALLS` para los JSON con el esquema exacto de
  `analysis/functions/dossiers.json`; direcciones de otros análisis (GPIO, IMX210,
  REA) no están todavía en el grafo.

## Validaciones

Si vas a citar una corrección en un informe nuevo, verifica la cita exacta con
`search.py section <node_id>` (skill `knowledge-navigation`) antes de repetirla.

## Referencias bajo demanda

`knowledge/PROGRESS.md` sección "Fase 3/4" documenta el método de extracción y
un bug real de proximidad ya corregido (no asumir que todo enlace cercano a la
palabra "corrige" es una corrección real: el extractor ya filtra esto, pero al
leer manualmente un documento largo aplica el mismo criterio).
