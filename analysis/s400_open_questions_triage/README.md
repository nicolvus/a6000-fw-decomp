# S400 — revisión manual de relaciones documentales

**Actualización 24-10-2026:** el índice tiene 300 relaciones: 61 rectificaciones
documentales respaldadas, 193 aristas descartadas y **46 pendientes**. El historial
contiene 460 filas: 103 respaldadas, 282 descartadas y 75 pendientes. Se cotejaron
nueve citas nuevas con la revisión Git; seis quedaron clasificadas y tres siguen
pendientes. Dos relaciones antiguas se resolvieron mediante bytes originales:
`0x43ad6034` es un despachador con `BLX r3`, y el callsite del log de overflow
`0x4379cb2e` usa la cadena de `0x43ca519f`, contrastados con bytes originales.
Esto no certifica las seis listas VD ni ejecución física.

Cinco filas adicionales proceden del cambio de contexto de una cita de
`CONTEXT.md`: dos aristas de procedencia invertida se descartan y tres
relaciones con módulos S605/S625/S627 conservan `VIGENTE`. No son cinco
hechos técnicos nuevos. El índice mantiene 46 pendientes.

Revisión del 23-10-2026. El encargo abarca 207 filas `VIGENTE` y las 132 decisiones anteriores: **339 filas**, de las cuales quedan 63 pendientes, 75 con rectificación respaldada y 201 aristas descartadas. Al iniciar esta revisión ya había **392 filas**; el índice adicional había pasado de las 264 relaciones del encargo a **299**. Se examinaron también las 53 filas posteriores y las 54 entradas adicionales del índice actual.

Resultado histórico sobre **446 filas revisadas el 23-10-2026**:

| Veredicto | Filas históricas | Relaciones del índice actual |
|---|---:|---:|
| `CORRECCION_APLICADA` | 100 | 59 |
| `FALSO_POSITIVO` | 275 | 192 |
| `VIGENTE` (pendiente) | 71 | 48 |
| Total | 446 | 299 |

Estos totales no son preguntas técnicas independientes: hay citas repetidas en distintas revisiones y relaciones entre los mismos documentos. El status del grafo tampoco equivale a un veredicto técnico. Se conserva `docs/OPEN-QUESTIONS.md` como índice generado, sin forzar su contador a cero.

De las 132 decisiones anteriores, **37 cambian**: 17 cierres pasan a aristas descartadas, nueve aristas descartadas pasan a rectificaciones respaldadas y 11 casos se reabren. Ejemplos: el conteo de callbacks S49/S50 y las notas históricas S28 sí contienen rectificaciones; S135→S172 invertía la procedencia; la tabla de S59 sobre el objeto de histogramas requiere evidencia adicional. S105 menciona el S101 del SDF, distinto del S101 del selector mecánico.

## Trazabilidad

Cada fila de `triage.json` conserva fuente, destino y tipo originales, veredicto/motivo anteriores, revisión Git de la fuente, marcador completo y contexto de cinco líneas. `destino_cita` identifica el documento contrastado en la revisión fijada por `manual_review.json`. `revision_manual` remite al caso razonado de ese registro, con fragmentos originales, localizadores y SHA-256 de la evidencia cuando procede. Las aristas descartadas se justifican con la cita documental conservada: índice, negación, procedencia invertida, homonimia de sesiones o destino vecino. No se descarta una relación solo por contener varios enlaces.

Los casos se resolvieron individualmente; compartir caso expresa el mismo alcance y evidencia, no una regla de clasificación por vocabulario. Se agrupan copias históricas de una cita únicamente tras comprobar su texto y destino. `CORRECCION_APLICADA` respalda la rectificación delimitada en el motivo; no implica haber reescrito todo el destino histórico ni validar todas las conclusiones del hito.

Las comprobaciones estáticas sobre evidencia original incluyen S28, S114, S156, S166, S168, S172, S329, S331, S336, S342 y S380. Para S49/S50 se cotejaron las instrucciones LLVM de copia/cursor/lista/BLX con los artefactos y las listas originales. Las ausencias se mantienen acotadas al método y región examinados. Sin ejecución del firmware ni pruebas en cámara.

## Pendientes

Los 71 registros pendientes explican su carencia: mapas/exports PIC originales, correspondencia entre revisión y afirmación, equivalencia de código entre modelos, seguimiento del slot/objeto, orden condicionado de callbacks, escenarios originales o alcance de las síntesis. Incluyen la discrepancia S204 y resúmenes S605–S627 que no justifican cerrar equivalencias ni logger dual. No se reafirma una decisión anterior solo porque ya era manual.

## Mantenimiento y pruebas

`extend_triage.py` solo registra candidatos pendientes. Identifica una relación por documento fuente, destino, tipo, cita completa y contexto; si solo cambian números de línea conserva la decisión y actualiza `fuente_actual`. Si cambia el texto o contexto exige una entrada nueva. No reutiliza una decisión por coincidir `archivo:línea`, ni confunde `CORRECTS` con `SUPERSEDES`.

Validación reproducible:

```sh
.venv/bin/python -m pytest tests/knowledge/test_open_questions_triage.py -q
.venv/bin/ruff check analysis/s400_open_questions_triage/extend_triage.py tests/knowledge/test_open_questions_triage.py
.venv/bin/mypy --explicit-package-bases --ignore-missing-imports analysis/s400_open_questions_triage/extend_triage.py tests/knowledge/test_open_questions_triage.py
```

Las regresiones comprueban cobertura con cita/contexto/tipo completos, desplazamiento de líneas, reutilización de una línea con otra cita, cambios de contexto, idempotencia, conservación de decisiones anteriores, fragmentos históricos recuperables desde Git y evidencia que no haya cambiado. Nuevas relaciones sin revisión permanecen pendientes. La prueba histórica requiere el historial Git con las revisiones registradas.

Resultado: **78 tests de conocimiento** (incluidos 11 de triaje) y **186 pruebas estáticas de evidencia** pasan; Ruff y Mypy sin avisos en los dos Python modificados. El protocolo MCP se probó fuera del aislamiento tras bloquearse su ejecutor dentro del sandbox. S50: 103 instrucciones LLVM y 12 punteros de cuatro listas contrastados con bytes originales. El grafo conserva 1455 entidades y 3066 relaciones en las dos reconstrucciones; el contenido de los derivados no cambia.
