# S400 — triaje de `docs/OPEN-QUESTIONS.md` (22-10-2026)

Fuente: las 132 filas del 22-10-2026. Veredicto por fila en `triage.json`; test de cobertura en
`tests/knowledge/test_open_questions_triage.py`.

| Veredicto | Filas | Significado |
|---|---|---|
| CORRECCION_APLICADA | 51 | La corrección existe y está escrita en la fuente; el status «abierto» es el valor por defecto del extractor |
| FALSO_POSITIVO | 81 | 58 líneas de índice/tabla, 11 negadas, 5 duplicados históricos, 3 destino/dirección erróneos, 2 términos técnicos, 2 autorreferencias |
| VIGENTE | 0 | Ninguna pregunta técnica abierta sale de este grafo |

**Límite:** clasificado leyendo la cita de evidencia de cada fila, sin abrir los documentos destino ni
reverificar los bytes de cada corrección. Las dudas técnicas reales (runtime NO_VERIFICADO) viven en
`knowledge/CURRENT.md`, no aquí.

**Causa:** `build_graph.py` asigna `NO_VERIFICADO` por defecto y enlaza la palabra «corrige» a todos los
enlaces de la misma línea o ventana. Mejora pendiente (no aplicada): restringir el destino al enlace más
cercano a la palabra clave y excluir líneas de índice.

## Ampliación (23-10-2026)

Tras reindexar, `OPEN-QUESTIONS.md` pasó a 271 filas (+139), casi todas líneas de README/CURRENT/outbox de S300–S385 con la palabra «corrige». Veredictos nuevos, por **regla automática**: CORRECCION_APLICADA si la cita nombra la sesión del destino y una palabra de corrección; si no, FALSO_POSITIVO. Totales: 69 CORRECCION_APLICADA, 202 FALSO_POSITIVO, 0 VIGENTE.

**Límite:** la regla lee solo la cita; no se abrió cada documento destino ni se reverificaron bytes. Un FALSO_POSITIVO automático podría ocultar una corrección real si la cita no nombra al destino.

Para ampliar tras reindexar: `python3 analysis/s400_open_questions_triage/extend_triage.py` (idempotente; mismos criterios automáticos).
