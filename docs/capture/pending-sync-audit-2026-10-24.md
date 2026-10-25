# Auditoría de pendientes y sincronización — 24-10-2026

Revisión parcial previa. Para el alcance integral posterior, evidencia faltante
S176, rectificación de S207 y backlogs sincronizados, consultar la
[auditoría integral](repo-audit-2026-10-24.md). Los contadores de relaciones de
esta instantánea no se deben asumir invariables tras reindexar nuevos textos.

Alcance: contrastar la lista comunicada al usuario con inventarios, resultados
de verificadores, triaje y evidencia técnica vigente. No es una nueva
decompilación integral ni una observación de cámara. `NO_VERIFICADO` expresa
falta de prueba positiva, no falsedad ni obligación de perseguir cada caso.

| Elemento comunicado | Veredicto | Comprobación y alcance |
|---|---|---|
| 226 etiquetas pendientes | **ACEPTO como censo documental** | `census_detalle.json` contiene 372 etiquetas: 94 hitos, 39 subetiquetas, 226 pendientes y 13 fragmentos descartados como módulos. `audit_pending.build()` coincide exactamente con `pendientes_auditados.json`: cuatro candidatas `ACEPTO` sin decodificación terminada, 222 `NO_VERIFICADO`, 13 `RECHAZO`. Las 226 no equivalen a 226 funciones por decompilar ni son todas prerrequisito de S51. |
| 66 de 69 afirmaciones S605–S627 | **ACEPTO como estado de afirmaciones** | `analysis/s6xx_verification_results.json` contiene 23 fichas: 20 logger dual `NO_VERIFICADO`, tres `VERIFICADO_ESTATICO` (S607/S611/S616) y 46 equivalencias sin verificar. `verify_s6xx.py` comprueba 23 fichas, 94 trazas y siete gemelas sin errores. Una afirmación no probada se puede retirar; no exige demostrar que sea verdadera. |
| 48 relaciones S400 pendientes | **ACEPTO con precisión** | Las 302 relaciones de `docs/OPEN-QUESTIONS.md` aparecen en el triaje por cita, contexto y tipo: 48 pendientes, 193 aristas descartadas y 61 rectificaciones respaldadas. Las 302 son el índice de relaciones que el extractor marca abiertas, **no 302 tareas reales**. Las 84 filas pendientes del historial incluyen revisiones repetidas y no se suman a las 48. El grafo registra 169 `NO_VERIFICADO` y 133 `CONFLICTO_PENDIENTE`, pero sus estados automáticos tampoco sustituyen el triaje. |
| Cola `0x40193` | **ACEPTO, acotado** | [El trazado](queue-40193-flow-2026-10-23.md) prueba emisor, receptor LIRO, instalador, consumidor estático del descriptor y bucle de 372 inicializadores. Aún no identifica el destino/efecto de `[[GOT]+0x14]+0x3c`, el registro del callback OSAL Linux ni el transporte concreto Linux↔LIRO. La entrada `0x435410f0` vale cero en la imagen original; eso no determina su valor en ejecución. Ya no están pendientes el receptor ni el consumidor de arranque. |
| RecordImage/RecordStill | **ACEPTO, acotado** | [La auditoría de contrato](recordstill-contract-audit-2026-10-23.md) identifica las parejas A6000/A7S y demuestra que `StateMgr::CallFunc` consume los 25 punteros `call_fn`. Sigue sin demostrarse la activación de la entrada concreta durante un disparo, la equivalencia de todos los callees y la unión con `0x40193`. Ya no están pendientes la identidad de los dos niveles ni el consumidor de esos punteros. |
| Cadena completa de captura/S51 | **ACEPTO como huecos técnicos** | [La matriz S51](s51-static-coverage-and-tool-limits.md) delimita receptores indirectos de `CURTAINMODE`, modo 1, pin `0x2a`, ruta YC→archivo y cuerpos decisivos IMX210. Las propiedades eléctricas y el efecto físico no pueden certificarse solo con bytes. El censo de etiquetas no mide porcentaje de decompilación. |
| S56–S61 y otros esquemas | **ACEPTO como límite de validación** | En este entorno `unicorn` no está instalado. Los arneses que lo importan no se reproducen aquí; eso no invalida sus resultados anteriores ni constituye por sí mismo un hueco funcional del obturador. El validador de trazas no cubre todos los esquemas JSON históricos. |
| P1–P21 | **ACEPTO como propuestas diferidas** | Hay 8 pruebas en `physical-test-plan.md`, cuatro propuestas nuevas P9–P12 en `s402-physical-test-mapping.md` y nueve P13–P21 en `physical-test-plan-2.md`: 21 identificadores únicos. P0 es preparación, no una prueba adicional. Ninguna de estas 21 se ejecutó en los planes; S64 documenta un antecedente distinto. Por instrucción del usuario, no ejecutar pruebas físicas hasta completar la ingeniería inversa necesaria. |
| Seis pruebas del protocolo MCP | **RECHAZO como pendiente** | Las seis pasaron fuera del aislamiento en la sesión anterior; el conjunto de conocimiento quedó en 79 pruebas aprobadas. El bloqueo del ejecutor dentro del sandbox es ambiental, no un fallo de protocolo demostrado. |

## Desincronizaciones corregidas

- `knowledge/CURRENT.md` llamaba `RecordStill::Execute` a `0x90b248`, pese a la
  rectificación vigente a **RecordImage**, y mostraba 239 candidatos iniciales
  como si aún fueran pendientes tras descartar 13. También mantenía el origen
  de `0x40193` y la identidad A7S como huecos sin reflejar los trazados
  posteriores. Se actualizaron esas frases.
- `README.md` conservaba los dos BL como llamadas a RecordStill y declaraba
  no identificado RecordStill en la A7S. Las parejas y los límites actuales
  están en el contrato auditado.
- `s385-libobj-a6000-vs-a7s-diff.md` aún pedía el barrido de datos A7S y
  desconocía al consumidor de los 25 punteros Thumb. S384 y la auditoría de
  contrato ya habían resuelto ambos puntos en su alcance estático.
- `s381-libobj-a6000-dispatch.md` aún pedía hallar el consumidor de arranque
  del descriptor; se incorporó el consumidor y el bucle ya demostrados.
- `S605-S627_tabla_hallazgos.md` decía que cualquier `logger_dual` no nulo
  falla y que solo S611 tiene evidencia positiva. S607 y S616 también la tienen;
  el verificador exige rutas validadas para los tres.

**Prioridad antes de pruebas físicas:** aristas restantes de `0x40193`,
activación de RecordImage/RecordStill y ruta sensor→YC→archivo/cortina.
La clasificación de 226 etiquetas y la verificación de 66 afirmaciones son
trabajo de calidad documental más amplio; no constituyen, por sí solas, una
condición técnica demostrada para S51.

VEREDICTO: CAMBIOS. Los contadores eran reproducibles, pero varias frases
vigentes y la interpretación de esos contadores estaban desincronizadas.
