# S400 — revisión de preguntas del grafo

Auditoría 23-10-2026: se retiran los veredictos automáticos de la ampliación anterior. Detectar una palabra de corrección y un número de sesión en una cita no demuestra que la corrección esté aplicada; no detectarlos tampoco demuestra un falso positivo.

La migración reabre **141 filas** automáticas como `VIGENTE`, que aquí significa **pendiente de revisión manual**, no funcionalidad demostrada. Conserva **132 filas** de la revisión previa (51 `CORRECCION_APLICADA`, 81 `FALSO_POSITIVO`) sin volver a certificar sus conclusiones. El total puede crecer con la regeneración del grafo.

`extend_triage.py` registra las nuevas filas como `VIGENTE`, conserva las revisiones manuales y es idempotente. Cada cierre exige revisar la cita, el documento fuente y el destino; una afirmación técnica necesita además su evidencia original.

El grafo es un índice de relaciones extraídas de texto; su status no garantiza la verdad de la relación. No se modifica `docs/OPEN-QUESTIONS.md` a mano ni se fuerza su contador a cero para pasar tests.

Validación: `tests/knowledge/test_open_questions_triage.py` verifica cobertura, vocabulario, reapertura de decisiones automáticas, conservación de revisiones manuales e idempotencia. [Auditoría completa](../../docs/auditoria-2026-10-23.md).
