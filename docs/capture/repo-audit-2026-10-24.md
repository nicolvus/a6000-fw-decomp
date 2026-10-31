# Auditoría integral de documentación y pendientes — 24-10-2026

**Seguimiento 25-10-2026:** la [investigación de los cinco pendientes](capture-static-followup-2026-10-25.md)
resuelve servicio/transporte OSAL, escritor S[0] y productor CAIF A7S,
reproduce S176 y retira el falso pendiente S305. Este informe conserva los
hallazgos de la auditoría del día 24; para la cola técnica actual usar el seguimiento.

Este documento es la referencia de esta revisión. Los informes históricos
conservan el alcance de su fecha; una casilla completada, un test verde o una
cadena presente no certifican toda la conclusión técnica de una sesión.

## Alcance y comprobaciones

- Inventario inicial: 23 582 archivos versionados y 898 Markdown; 699 Markdown
  propios fuera de `references/` y de las copias de habilidades. Las referencias
  de terceros se inventarían, pero no se modifica su documentación ni se ejecutan
  sus suites. Se examinan inventarios, casillas, rutas de artefactos, enlaces,
  estado de Git/GitHub y verificadores del proyecto.
- Los 3033 JSON propios versionados se pueden analizar sin errores de sintaxis.
  Esto no valida automáticamente su esquema ni sus conclusiones.
- El árbol estaba limpio y `HEAD` coincidía con `origin/main` en `c3e519a5`.
  La API de GitHub muestra dos PR, #1 y #2, ambas fusionadas, sin incidencias
  independientes ni PR abiertas. No existe una cola de issues que sustituya
  los pendientes documentados. Pages se había desplegado correctamente para
  ese commit; su workflow solo publica documentación, no ejecuta la suite.
- Sin cámara, flasheo ni nueva ejecución de firmware. Se reutiliza evidencia
  estática exportada de REA/Ghidra y se contrastan inventarios con verificadores
  de bytes. No se ha vuelto a descompilar cada función del firmware.

## Afirmaciones auditadas

| Afirmación | Veredicto | Evidencia y límite |
|---|---|---|
| 133/372 cubiertas, 226 pendientes, 13 descartadas | **ACEPTO como censo documental** | `analysis/s178_census/audit_pending.py:build()` reproduce exactamente el JSON: 94 hitos, 39 subetiquetas, cuatro candidatas aceptadas, 222 sin verificar y 13 rechazadas. No equivale a porcentaje de código ni de funciones recuperadas. |
| 66 de 69 afirmaciones S605–S627 pendientes | **ACEPTO en su alcance** | `analysis/verify_s6xx.py`: 23 fichas, 94 trazas, siete gemelas, cero errores. Solo tres logger dual verificados estáticamente; 20 logger y 46 equivalencias siguen abiertos. El verificador no demuestra ausencia funcional del obturador. |
| 302 preguntas = 302 tareas | **RECHAZO** | Es el índice automático de relaciones de la revisión inicial: el triaje contabiliza 48 pendientes, 193 aristas descartadas y 61 rectificaciones respaldadas. Las 483 filas históricas incluyen citas repetidas. Los cambios documentales pueden añadir o desplazar relaciones; no se suman como tareas técnicas nuevas sin revisión. |
| S206/S207 pendientes de publicar | **RECHAZO** | Existen ambos informes, JSON, generadores y tests. Quedan sin resolver la correspondencia funcional profunda y la semántica del fin de integración. |
| S207 demuestra ausencia/identidad del mecanismo de fin de integración | **RECHAZO** | Su test de bytes busca siete textos y cuenta registros; el generador asignaba `False` sin demostrar semántica. Se cambia a `null`/NO_VERIFICADO y se retira la conclusión global del informe y de los datos. |
| S301 no realizado; S304/S305 cerrados por completo | **RECHAZO** | S301 tiene informe y barrido. S304 estaba duplicado y marcaba como hechos dos puntos NO_VERIFICADO. S305 existe como informe parcial; 13 sitios estáticos de llamada no prueban 13 iteraciones. Backlog sincronizado por entregables y preguntas restantes. |
| S401/S402 y tesis pendientes | **RECHAZO como entregables** | Los informes existen. Se reabren tres casillas de C sobre productor CAIF/bit y propagación que el propio backlog calificaba como inferencia, pendiente o parcial. |
| S176 dispone de informe, artefactos y test reproducibles | **RECHAZO como entregable verificable** | Las rutas anunciadas `analysis/s176_imager_state_readers/`, `docs/capture/s176-imager-state-readers.md` y `tests/test_s176_imager_state_readers.py` no existen en el árbol ni en el historial Git disponible. No demuestra falsedad del resultado; impide certificarlo. Recuperar la evidencia o reproducir el análisis antes de marcarlo verificado. |
| Receptor/instalador y arranque de `0x40193` aún desconocidos | **RECHAZO** | El [trazado vigente](queue-40193-flow-2026-10-23.md) ya identifica receptor, descriptor, consumidor y bucle de 372 inicializadores. El resumen NEEDS-HUMAN estaba desfasado. |
| `0x90b248` es RecordStill y no se conoce el consumidor de sus punteros | **RECHAZO** | Es RecordImage; RecordStill está en `0x908afc`. La [auditoría de contrato](recordstill-contract-audit-2026-10-23.md) recuperó `StateMgr::CallFunc` y las parejas A7S. Activación real y todos los callees permanecen abiertos. |
| «Más cadenas = más código por descifrar»; «módulos decodificados» en Pages | **RECHAZO** | El generador ordena etiquetas por referencias candidatas y muestra informes existentes. Se rotula como cobertura documental y se retira esa equivalencia con volumen/prioridad técnica o cierre funcional. |
| La investigación estática está agotada y P5 es la única salida | **RECHAZO** | La tesis y el outbox C lo afirmaban pese a conservar productor CAIF y enlaces LIRO/imager sin demostrar. Se retira esa conclusión y la necesidad universal de flashear Darwin: no se deducen de una ruta hipotética. S55 y el registro de coordinación quedan contextualizados como historia parcial. |
| P1–P21 completadas o autorizadas por estar redactadas | **RECHAZO** | Son 21 propuestas únicas; P0 es preparación y S64 un antecedente distinto. Todas siguen diferidas hasta completar la ingeniería inversa necesaria. |

## Cola técnica vigente

1. `0x40193`: identificar destino/efecto del servicio indirecto `+0x3c`, registro
   del callback OSAL Linux y transporte concreto Linux↔LIRO. No repetir como
   pendientes el receptor, instalador ni consumidor de arranque conocidos.
2. RecordImage/RecordStill: demostrar activación de la entrada durante un
   disparo, comparar callees y unir esa ruta con `0x40193`, YC, archivo y cortina.
3. IMX210/IMX235: recuperar cuerpos decisivos y productores de `S[0]`, modo 1,
   gates y pin `0x2a`; resolver propiedad/formato del buffer y semántica del fin
   de integración hasta donde permita la evidencia estática. S206/S207 no lo cierran.
4. Completar flujo de `FUN_43858390`, acceso GOT `0x4401f080` y productor CAIF
   A7S del bit `0x20`; mantener los límites de S305 y C explícitos.
5. Recuperar o reproducir S176 y contrastar sus dos supuestos lectores.

La [matriz S51](s51-static-coverage-and-tool-limits.md) delimita la ruta.
Los backlogs [A](../../knowledge/agents/A-backlog.md),
[B](../../knowledge/agents/B-backlog.md), [C](../../knowledge/agents/C-backlog.md)
y [elementos diferidos](../../knowledge/agents/NEEDS-HUMAN.md) detallan sus límites.
No se afirma que las 226 etiquetas ni las 66 afirmaciones sean todas necesarias
para resolver S51. Su revisión documental continúa en sus inventarios.

## Integridad y reproducción

Los índices derivados escapaban incorrectamente las citas: sus enlaces se
interpretaban desde `docs/` y quedaban rotos o truncados. El exportador ahora
conserva la cita como texto; solo fuente y destino crean enlaces navegables.
El catálogo tenía enlaces a S143 con nombre S140 y anunciaba archivos S176
ausentes. Se reparan las rutas recuperables y se explicita la evidencia faltante.
Las rutas del README archivado se ajustan a su directorio actual sin alterar
sus conclusiones históricas. Los informes S1–S48 y los binarios se conservan.

Se reparan 124 enlaces del README archivado y cuatro enlaces de resultados de
agentes. El catálogo JSON estaba desfasado: 2146 archivos/108 familias frente
a 2982 archivos/537 familias del árbol actual bajo `analysis/`; se regenera
con su herramienta existente. Las familias describen formas, no equivalencia
semántica ni cobertura del grafo.
El workflow de Pages también se activa al cambiar el JSON del censo que consume
el generador; antes solo contemplaba los Markdown de `analysis/`.

Validaciones de esta revisión: ver la sección de resultados al final. No se
instalan dependencias para ocultar limitaciones del entorno ni se convierten
tests omitidos en pruebas aprobadas.

## Resultados de validación

- Conocimiento: **79 pruebas aprobadas** (73 dentro del aislamiento y seis del
  protocolo MCP fuera de él; dentro se reproduce el bloqueo del ejecutor).
- `analysis/`: **91 pruebas aprobadas**. Regresión de Pages, S205–S208 y S301:
  **30 aprobadas**; es un subconjunto de las suites, no un total adicional de
  pruebas únicas.
- Ejecución combinada de conocimiento sin protocolo, regresiones seleccionadas
  y `analysis/`: **194 aprobadas**. Sumadas las seis del protocolo probadas por
  separado: **200 pruebas seleccionadas aprobadas**, sin declarar verde el resto.
- Ruff y Mypy: sin avisos en los siete Python modificados. Se reprodujeron
  antes los fallos de exportación de citas, rotulación de Pages y falsa certeza
  del JSON S207; las regresiones pasan después de las reparaciones.
- Colección integral: **3375 pruebas recopiladas y ocho módulos con error de
  importación por `unicorn` ausente** (S56, S57, S58, S59-Claude, S59-Sol,
  S60-Claude, S60-Sol y S61). No se instala el paquete ni se presenta la suite
  integral como aprobada. El intento general sin protocolo MCP agotó 330 s;
  no se afirma que las 3375 pruebas se hayan ejecutado. Los subconjuntos
  aprobados son exclusivamente los enumerados arriba.
- SHA-256: **5 archivos de firmware, 9 de `silent-liro` y 1328 de Ghidra**
  coinciden con los manifiestos finales; ninguno falta. S1–S48 sin cambios.
- Enlaces Markdown locales: **2061 destinos comprobados, cero faltantes**,
  excluyendo URLs y ejemplos de código. No se afirma haber comprobado todos
  los enlaces externos ni todos los anchors internos.
- Dos reconstrucciones sucesivas: **1460 entidades y 3100 relaciones**, estables;
  374 filas de correcciones y 325 relaciones abiertas extraídas. Tras reparar
  rutas aparecen 23 candidatas documentales adicionales: el triaje pasa de
  483 a 506 filas históricas. El índice actual tiene 71 candidatas pendientes,
  193 aristas descartadas y 61 rectificaciones respaldadas. Las 23 nuevas no
  se cierran automáticamente ni se interpretan como 23 tareas técnicas.

Estos resultados validan el alcance indicado; no certifican semántica eléctrica,
ejecución real ni todas las afirmaciones de cada informe histórico.

VEREDICTO: CAMBIOS. Se resuelven errores documentales reproducidos; las preguntas
técnicas y la evidencia faltante anteriores permanecen abiertas. S51 A/B/C=NO.
