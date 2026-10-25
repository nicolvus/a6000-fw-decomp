# Pendientes por cerrar — índice maestro

Creado el 25-10-2026. Es la lista única y viva de lo que falta en el proyecto. Los
backlogs de agentes ([A](../knowledge/agents/A-backlog.md), [B](../knowledge/agents/B-backlog.md),
[C](../knowledge/agents/C-backlog.md), [D](../knowledge/agents/D-backlog.md), [E](../knowledge/agents/E-backlog.md),
[NEEDS-HUMAN](../knowledge/agents/NEEDS-HUMAN.md)) conservan el detalle por carril; este
documento los resume y manda. Los índices generados ([OPEN-QUESTIONS](OPEN-QUESTIONS.md),
[CORRECTIONS](CORRECTIONS.md)) son candidatas automáticas, no tareas.

## Regla permanente: este documento se mantiene siempre

1. **Toda sesión que cierre, avance, descarte o reabra una tarea edita este archivo en el mismo
   commit**: estado, fecha y enlace a la evidencia. No se da una fase por terminada sin esa edición.
2. **Todo pendiente nuevo que se descubra se añade aquí** con ID nuevo (siguiente número libre de su
   sección; los IDs no se reutilizan), con origen (informe o sesión) y criterio de cierre.
3. **Lo cerrado no se borra**: pasa a la sección «Cerradas» con fecha y commit. Lo descartado indica el motivo.
4. Estados permitidos: `ABIERTO`, `PARCIAL`, `NO_VERIFICADO` (límite estático alcanzado), `BLOQUEADO`
   (necesita cámara, dato externo o decisión del usuario), `DIFERIDO`, `CERRADO`, `DESCARTADO`.
5. Toda cifra lleva su fuente. Si no se re-verificó en la sesión, se marca «sin re-verificar».
6. Una cola de agente, un informe o un `NEEDS-HUMAN` que cambie de estado actualiza también esta tabla.

## Alcance de la revisión que originó este documento (25-10-2026)

`HEAD` = `origin/main` = `dd3a8212`, árbol limpio. El repo tiene 23 632 archivos versionados; no se leyeron
uno a uno. Se leyeron `docs/STATE.md`, `knowledge/CURRENT.md` (bloque vigente), el cierre estático S402, el seguimiento
de los cinco puntos, las dos auditorías del 24-10, la matriz S51, la decisión S51, los planes P1–P21, los cinco
backlogs de agentes, `NEEDS-HUMAN`, `PENDIENTES_FINALES`, el censo S178 y el triaje S400. Lo no leído se cubre solo
por esos índices.

## A. Estático (sin cámara)

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| E1 | NO_VERIFICADO | Quién publica el local 4 a `ModelScalarPb` (`0x120EF004`), el 2 a `ModelPbCap` (`0x12030002`) y los mensajes `0x35001004`, `0x35003002`, `0x3a494026` | Ningún código de `libObj` construye esos ids; el emisor, si existe, es de datos o de ejecución. Reabrir solo si aparece un llamador que pase `@M0EF` o `@M030` a `0x12d780` | [cierre S402 §8](capture/static-closure-2026-10-25.md) |
| E2 | PARCIAL | Activación real de RecordImage/RecordStill: el check `0x907ba0` no condiciona la fila `0x10000005` (solo rechaza mensaje nulo o `0x10000003` con búsqueda fallida). Falta el productor externo de `0x10000005` (los dos constructores conocidos no son envíos externos) | Cadena disparo → mensaje → estado 2 demostrada por código, o declarada de ejecución | [S403](capture/s403-cierre-pendientes.md) §E2, [seguimiento](capture/capture-static-followup-2026-10-25.md) |
| E3 | PARCIAL | `params[+9]` de SetExposure (IMX210): cinco sitios de llamada y sus escritores identificados (valores 0, 1 y 4 por constante); los valores 2 y 3 sin constante directa (ver E14) | Origen de 2/3 resuelto o declarado de ejecución | [S403](capture/s403-cierre-pendientes.md) §E3 |
| E4 | PARCIAL | Modos `+8` de `0x40193`: hay tabla booleana `0x43ca530e` y clasificador por máscara en `0x4379d378`, pero los códigos de los ocho wrappers (`0xc/0xb/0x14/0xa`, `0x6/0x5/0xa/0x4`) no están todos en 0–10; sin nombre por modo | Tabla índice → estado nombrada | [S403](capture/s403-cierre-pendientes.md) §E4, [cierre S402 §9](capture/static-closure-2026-10-25.md) |
| E6 | BLOQUEADO | Cadena CAIF → Darwin → LIRO/imager: el MCU Darwin queda fuera de `av-cam` | Solo con traza del bus o volcado de Darwin (ver F4) | [C-backlog](../knowledge/agents/C-backlog.md) |
| E8 | PARCIAL | Estado `0x43f72d02`: 14 sitios lo leen por el slot (S176 solo contaba 2) y ninguno escribe; los dos lectores S176 tienen cadena de llamadores; el lector 2 cuelga de `0x437b5b14` (origen del bloque `B` de captura, S42). Falta activación efectiva y efecto de los campos | Activación solo en ejecución | [S403](capture/s403-cierre-pendientes.md) §E8 |
| E9 | BLOQUEADO | Correspondencia funcional de los 112 registros IMX210/IMX235 restantes y mecanismo de fin de integración: la semántica eléctrica exige hoja de datos (ver D5) | Documento legítimo aportado por el usuario | [A-backlog](../knowledge/agents/A-backlog.md) |
| E10 | ABIERTO | Ruta YC → archivo: productor de modo 1, creador del pin `0x2a` en disparo, formato YC y propiedad del buffer | Ciclo terminal de buffers demostrado | [matriz S51](capture/s51-static-coverage-and-tool-limits.md) |
| E11 | PARCIAL | Segunda cortina: enlace banco/bit `0xf2910048` → P4E y rutas alternativas de fin de exposición | Traducción física verificada | [S51](capture/s51-decision.md) |
| E12 | PARCIAL | Mensaje de `0x437b0390` (tipo 3, subtipo `0x22`, buzón `0x0110027c`): 13 emisores y ningún receptor por literal; entradas indirectas de `CURTAINMODE` sin seguir | Receptor localizado por registro de tareas (E15) | [S403](capture/s403-cierre-pendientes.md) §E12, [matriz S51](capture/s51-static-coverage-and-tool-limits.md) |
| E13 | BLOQUEADO | Servicio ODL del carril B y significado físico de sus registros MMIO (`0xf292b000..8`, canales `w0`): sin hoja de datos ni símbolos | Documento externo o prueba física | [S335](capture/s335-mmio-layer.md), [B-backlog](../knowledge/agents/B-backlog.md) |
| E14 | ABIERTO | Origen de los valores 2 y 3 de `params[+9]`: 14 `str`/`strh` con desplazamiento `0x654` (tipo de objeto sin confirmar) y el campo `[r4+0x1fc]` de `0x4381106c` | Escritores clasificados por tipo de objeto, o valores 2/3 declarados sin productor | [S403](capture/s403-cierre-pendientes.md) §E3 |
| E15 | ABIERTO | Receptor del buzón `0x0110027c` por el registro de tareas (no por literal) | Tarea receptora identificada | [S403](capture/s403-cierre-pendientes.md) §E12 |

## B. Documental y de calidad

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| D1 | PARCIAL | Censo: 226 etiquetas revisadas de forma léxico-estructural (101 módulo propio, 118 subetiqueta, 6 campo de formato, 1 mixta); 4 `ACEPTO` decodificadas por texto. Los veredictos del censo no cambian; la función real de las 222 `NO_VERIFICADO` exige leer instrucciones | Una etiqueta se reabre solo si un hallazgo de captura la enlaza por código | [S403 D1](capture/s403-censo-revision.md), [censo](../analysis/s178_census/pendientes.md) |
| D3 | PARCIAL | Afirmaciones S605–S627: logger dual de 19 fichas sin respaldo estático (3 verificadas); equivalencia de código refutada en 10 rutinas comparadas (4 fichas); 7 trazas con homólogo sin rutina resuelta y 77 sin homólogo textual (ver D6) | Cotejo de las rutinas restantes contra bytes; la equivalencia funcional no se decide solo con código | [S403](capture/s403-cierre-pendientes.md) §D3, [auditoría](capture/S605-S627_tabla_hallazgos.md) |
| D4 | PARCIAL | Triaje S400: 518 filas, todas con revisión manual (322 `FALSO_POSITIVO`, 110 con rectificación respaldada, 86 `VIGENTE`). Las `VIGENTE` están razonadas, no certificadas | Cada `VIGENTE` pasa a respaldada o descartada al cerrar D3 o su historial | [triaje](../analysis/s400_open_questions_triage/README.md) |
| D5 | BLOQUEADO | Hojas de datos IMX210/IMX235 (mapa de registros, semántica de modos) | Documento legítimo aportado por el usuario; no existe público | [S51](capture/s51-decision.md) |
| D6 | ABIERTO | Equivalencia S605–S627: 7 trazas con homólogo en A7S cuya rutina REA no resolvió (Thumb sembradas) y 77 sin homólogo textual | Rutinas ubicadas con Capstone y comparadas, o declaradas sin homólogo | [S403](capture/s403-cierre-pendientes.md) §D3 |

## C. Entorno y código

Sin pendientes abiertos (C1–C4 cerrados el 25-10-2026, ver «Cerradas»).


## D. Físico (diferido por instrucción del usuario hasta cerrar la ingeniería inversa necesaria)

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| F1 | DIFERIDO | P1–P8: observación de `G+0x808`, forzado de tipo, traza en bus, shell de servicio, prueba de imagen, `+0x210` | Ejecución con autorización expresa, backup NVRAM previo | [plan](capture/physical-test-plan.md) |
| F2 | DIFERIDO | P9–P12: propuestas derivadas de S401/S402 | Ídem | [mapeo S402](capture/s402-physical-test-mapping.md) |
| F3 | DIFERIDO | P13–P21: lecturas de MMIO/RAM (gates `+3/+6`, DFE `0xfc02a00c`, canales `w0`, segunda matriz), latencia EFCS, modo fuera de vocabulario | Ídem; P0.2 decide si P13–P15 son viables | [plan 2](capture/physical-test-plan-2.md) |
| F4 | BLOQUEADO | Traza pasiva CIS0+XPI+VD y analizador lógico en cortinas: requieren abrir la cámara | Decisión del usuario | [plan](capture/physical-test-plan.md) |
| F5 | BLOQUEADO | Acción real de Darwin sobre las bobinas y bootloader del FM3 (no está en el firmware) | Solo con hardware | [plan](capture/physical-test-plan.md) |
| F6 | ABIERTO | Decisión S51: A=NO, B=NO, C=NO (sin ruta demostrada, sin base para parche, sin prueba de imposibilidad) | Se revisa solo si F1–F5 o D5 aportan evidencia | [S51](capture/s51-decision.md) |

## E. Repositorio y respaldo

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| R1 | ABIERTO | **No están en GitHub, por diseño**: `firmware/` (5,3 GB), `analysis/camera-dumps/` (3,1 GB, con backups NVRAM/flash de la cámara), proyectos Ghidra, `*.bin`/`*.elf`, manuales con copyright, `.venv/`. De los volcados solo se versionan README y SHA256SUMS. No hay copia remota: un fallo del disco los pierde | Decisión del usuario sobre un respaldo externo propio; no se suben a GitHub | `.gitignore` |
| R2 | ABIERTO | El flujo de Pages solo publica documentación y no ejecuta la suite de pruebas | CI con pruebas, si el usuario la quiere | [auditoría 24-10](capture/repo-audit-2026-10-24.md) |

## Cerradas (no borrar)

| ID | Fecha | Qué se cerró | Evidencia |
|---|---|---|---|
| C1 | 25-10-2026 | `unicorn 2.1.4` instalado en `.venv`; los 8 módulos S56–S61 se colectan y pasan (315 pruebas, 36 subpruebas) | [S403](capture/s403-cierre-pendientes.md) |
| C2 | 25-10-2026 | `tests/knowledge/test_mcp_server.py` colecta y pasa (6) con el `.venv`; el fallo era del entorno sin `mcp` | [S403](capture/s403-cierre-pendientes.md) |
| C3 | 25-10-2026 | mypy sin errores en `scripts/knowledge` y `tests/knowledge` (21 archivos): aserciones de tipo y `mypy.ini` para `capstone` | [S403](capture/s403-cierre-pendientes.md) |
| C4 | 25-10-2026 | Suite integral ejecutada completa: 3521 aprobadas, 35 omitidas, 0 fallos, 529 s | [S403](capture/s403-cierre-pendientes.md) |
| D2 | 25-10-2026 | Módulos S515 `[BL]`, S516 `[PNL]`, S628 `[FILE_NUM]`, S629 `[FSYSMODE]`, S630 `[RING_DIAL]`: informe y 8 pruebas | [informe](capture/s515-s516-s628-s630-modulos.md) |
| E7 | 25-10-2026 | Backup `0x3000b`: 14 sitios acceden al objeto `0x43f72d02` por el slot y solo leen; el productor es el callback de copia (S305); valores efectivos solo en ejecución | [S403 §E7](capture/s403-cierre-pendientes.md) |
| E5 | 25-10-2026 | Ausencia acotada del lector `+0x238` (A6000, 262 anclas) y del almacén `[S+0]` (A7S, 73 anclas); límite: anclas PIC con ventana de 16 instrucciones | [S403 §E5](capture/s403-cierre-pendientes.md) |
| — | 25-10-2026 | Id de modelo estático (`@M0EF`, `@M030`) y ocho emisores = autopublicaciones; E1 queda `NO_VERIFICADO` por exclusión, no por falta de búsqueda | `dd3a8212` |
| — | 25-10-2026 | Revisión manual de las 44 filas `VIGENTE` sin revisar del triaje | `dd3a8212` |
| — | 25-10-2026 | RecordStill/RecordImage A6000≡A7S (25 + 174 pares, solo cambian líneas de log) | [cierre S402 §2](capture/static-closure-2026-10-25.md) |
| — | 25-10-2026 | Servicio `sta_tsk` y transporte OSAL de `0x40193`; escritor `S[0]`; constructor CAIF A7S; S176 reproducido | [seguimiento](capture/capture-static-followup-2026-10-25.md) |

## Registro de cambios de este documento

| Fecha | Cambio |
|---|---|
| 25-10-2026 | Creación a partir de la revisión integral del repo: 13 pendientes estáticos, 5 documentales, 4 de entorno, 6 físicos, 2 de respaldo. |
| 25-10-2026 | S403: cerrados C1–C4, D2, E5 y E7; avanzados D1, D3, E2, E3, E4, E8, E12; reclasificados E6, E9 y E13 como BLOQUEADO; nuevos E14, E15 y D6. |
