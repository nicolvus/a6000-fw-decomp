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
| E1 | NO_VERIFICADO | Quién publica el local 4 a `ModelScalarPb` (`0x120EF004`), el 2 a `ModelPbCap` (`0x12030002`) y los mensajes `0x35001004`, `0x35003002`, `0x3a494026` | Ningún código de `libObj` construye esos ids; el emisor, si existe, es de datos o de ejecución. Reabrir solo si aparece un llamador que pase `@M0EF` o `@M030` a `0x12d780`. Reintento 26-10-2026: modelo nunca constante en los 92 sitios de `0x120168`; 3 de los 11 llamadores de `0x12d780` son la consola `[AppTestcmd]`. Ángulo de bytes 26-10-2026: el literal de 32 bits de `0x120EF004` no existe en los 4,6 GB extraídos y el de `0x12030002` solo en la partición Android (coincidencia); un emisor construiría el id en ejecución Segundo reintento 26-10-2026: sin vías estáticas restantes; todo emisor posible es de datos o de ejecución | [cierre S402 §8](capture/static-closure-2026-10-25.md) |
| E20 | ABIERTO | `[EXL]` (22 trazas de comprobación de dimensiones: `initCamdcv`, `calCamdcvTanz`, `hsiz_* > 2240`) es la única etiqueta alcanzable desde las raíces de captura que no es subetiqueta: dos rutinas a profundidad 6 (`0x436ca820`, `0x436cafc0`) en el grafo estricto | Determinar si alguna comprobación de dimensiones puede rechazar una captura (condición y destino del error) y fijar el límite estático; origen: auditoría 26-10-2026 sobre D1 | [D1](capture/s403-cierre-pendientes.md), [censo](capture/s403-censo-revision.md) |
| E6 | BLOQUEADO | Cadena CAIF → Darwin → LIRO/imager: el MCU Darwin queda fuera de `av-cam` | Solo con traza del bus o volcado de Darwin (ver F4) | [C-backlog](../knowledge/agents/C-backlog.md) |
| E9 | BLOQUEADO | Correspondencia funcional de los 112 registros IMX210/IMX235 restantes y mecanismo de fin de integración: la semántica eléctrica exige hoja de datos (ver D5) | Documento legítimo aportado por el usuario | [A-backlog](../knowledge/agents/A-backlog.md) |
| E11 | BLOQUEADO | Segunda cortina: enlace banco/bit `0xf2910048` → P4E (`2ND_CURTAIN_MG`). El escritor `0x43b5e2b0`/`0x4398f9a4` es un helper GPIO genérico con 78 llamadores directos; la correspondencia de ese banco/bit con el pin P4E (que S50 atribuye a Darwin) no consta en el firmware y exige mapa de pines/hoja de datos o traza | Documento externo o prueba física (ver F4, E6) | [S51](capture/s51-decision.md), [S50](capture/s50-parallel-conclusions.md) |
| E13 | BLOQUEADO | Servicio ODL del carril B y significado físico de sus registros MMIO (`0xf292b000..8`, canales `w0`): sin hoja de datos ni símbolos | Documento externo o prueba física | [S335](capture/s335-mmio-layer.md), [B-backlog](../knowledge/agents/B-backlog.md) |

## B. Documental y de calidad

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| D5 | BLOQUEADO | Hojas de datos IMX210/IMX235 (mapa de registros, semántica de modos) | Documento legítimo aportado por el usuario; no existe público | [S51](capture/s51-decision.md) |

## C. Entorno y código

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| C7 | ABIERTO | 11 herramientas fuera de línea de `scripts/` sin prueba que lleve su nombre: `dump_dmm_unit_types`, `dump_topology_table`, `elf_string_xrefs`, `elf_thumb_callers`, `fdat_guard_probe`, `func_owner`, `pin_signatures`, `rtti_vtables`, `schematic_pin_nets`, `thumb_callers`, `thumb_pc_strings` | Confirmar cobertura indirecta (por importación) o añadir pruebas sintéticas sin firmware; las 25 herramientas `camera_*`/`senser_*`/`updater_*` necesitan cámara y quedan fuera | [estado.json](../knowledge/audit/estado.json) |
| C8 | ABIERTO | `tests/test_pages_status.py` ejecuta `scripts/build_pages_status.py` y reescribe `site/*` y `docs/progress/index.html` (archivos versionados): cada corrida de la suite deja el árbol sucio | Que la prueba escriba en un directorio temporal o compare sin escribir | auditoría 26-10-2026 |


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
| R3 | BLOQUEADO | `analysis/ghidra/s37-input/libmprctrl.so` (221 700 B, biblioteca ELF ARM de Sony) está versionado desde el primer commit en un repositorio **público**; contradice la política de R1 (el firmware y los binarios no van a GitHub) | Decisión del usuario: retirarlo del árbol (`git rm`) y, si se quiere, reescribir el historial; no se hace sin orden expresa | auditoría 26-10-2026 |
| R4 | ABIERTO | Cuatro archivos `.zip` en la raíz (`.claude.zip`, `knowledge.zip`, `scripts.zip`, `tests.zip`; 10, 10, 43 y 31 archivos) son copias antiguas de carpetas que hoy tienen muchos más (p. ej. `tests/` tiene 290 archivos de prueba) | Confirmar con el usuario que no se usan y retirarlos, o regenerarlos | auditoría 26-10-2026 |
| R5 | ABIERTO | Nueve archivos versionados coinciden con reglas de `.gitignore` (seis registros `*.log` de `analysis/rea-independent/` y tres `analysis/s303_ref_tree/raw305*.jsonl`) | Decidir si se retiran del índice (`git rm --cached`) o se añade excepción a `.gitignore` | [estado.json](../knowledge/audit/estado.json) |

## Cerradas (no borrar)

| ID | Fecha | Qué se cerró | Evidencia |
|---|---|---|---|
| C1 | 25-10-2026 | `unicorn 2.1.4` instalado en `.venv`; los 8 módulos S56–S61 se colectan y pasan (315 pruebas, 36 subpruebas) | [S403](capture/s403-cierre-pendientes.md) |
| C2 | 25-10-2026 | `tests/knowledge/test_mcp_server.py` colecta y pasa (6) con el `.venv`; el fallo era del entorno sin `mcp` | [S403](capture/s403-cierre-pendientes.md) |
| C3 | 25-10-2026 | mypy sin errores en `scripts/knowledge` y `tests/knowledge` (21 archivos): aserciones de tipo y `mypy.ini` para `capstone` | [S403](capture/s403-cierre-pendientes.md) |
| C4 | 25-10-2026 | Suite integral ejecutada completa: 3521 aprobadas, 35 omitidas, 0 fallos, 529 s | [S403](capture/s403-cierre-pendientes.md) |
| D2 | 25-10-2026 | Módulos S515 `[BL]`, S516 `[PNL]`, S628 `[FILE_NUM]`, S629 `[FSYSMODE]`, S630 `[RING_DIAL]`: informe y 8 pruebas | [informe](capture/s515-s516-s628-s630-modulos.md) |
| E12 | 26-10-2026 | Mensaje de `0x437b0390` (tipo 3, subtipo `0x22`, buzón `0x0110027c`): registro de `kikilog`, no de control; 13 emisores en av-cam | [E15](capture/s403-e15-kikilog.md) |
| E15 | 26-10-2026 | Receptor del buzón `0x0110027c` = `kikilog_main_thread` de `kikilog.ko` (Linux), que llama a `record_log`; también envían `libObj.so` y `upm.ko` | [E15](capture/s403-e15-kikilog.md) |
| E3 | 26-10-2026 | `params[+9]` de SetExposure: valores 0/1/4 por constante en tres sitios; 2 y 3 sin productor constante (ver E14) | [E14](capture/s403-e14-params9.md) |
| E14 | 26-10-2026 | Los 14 escritores anchos de `+0x654` clasificados (10 de bloque de parámetros, 4 de otra clase FSM); ninguno guarda 2 o 3 como constante; 4 fuentes de datos enumeradas | [E14](capture/s403-e14-params9.md) |
| E2 | 26-10-2026 | Productores de `0x10000005` en libObj enumerados (2 publican en cola: gestor `View` `0x8382f8` y método `0x91c1c8`); activación por pulsación solo en ejecución | [E2](capture/s403-e2-productores.md) |
| E8 | 26-10-2026 | Objeto `0x43f72d02`: 7 de 14 sitios lectores cuelgan de las raíces de captura (≤7 niveles de llamadores); valores y activación declarados de ejecución | [S403 adenda](capture/s403-cierre-pendientes.md) |
| E4 | 26-10-2026 | `0x4379d378` = `IsNeedForceS1ON(trig)`; `trig` 0–10 clasificado (forzar S1: 3, 8, 9, 10; no: 0, 1, 4–7; condicional: 2); el significado físico de cada `trig` queda sin establecer | [S403 adenda](capture/s403-cierre-pendientes.md) |
| D3 | 26-10-2026 | Afirmaciones S605–S627: logger dual sin respaldo estático en 19 fichas (3 verificadas); equivalencia de código refutada en las 17 trazas con homólogo (A7S); 77 sin homólogo textual | [S403 adenda](capture/s403-cierre-pendientes.md) |
| D6 | 26-10-2026 | 7 trazas con homólogo sin rutina REA ubicadas por prólogo y comparadas: ninguna igual; 77 declaradas sin homólogo | [S403 adenda](capture/s403-cierre-pendientes.md) |
| E16 | 26-10-2026 | Entradas del grupo que lee `CURTAINMODE`: 26 nodos y 6 raíces, todas ranuras de tablas (punteros); el invocador de cada ranura es de ejecución | [S403 adenda](capture/s403-cierre-pendientes.md) |
| D1 | 26-10-2026 | 226 etiquetas del censo: 216 sin emisor bajo las raíces de captura por llamadas directas (grafo mínimo, calibrado con E8) y 10 alcanzables, todas subetiquetas o campos de módulos conocidos salvo `[EXL]` | [S403 adenda](capture/s403-cierre-pendientes.md) |
| D4 | 26-10-2026 | Triaje S400: las 86 filas pendientes resueltas con casos razonados y evidencia con hash; 518 filas, 364 descartadas, 154 con rectificación respaldada, 0 pendientes | [triaje](../analysis/s400_open_questions_triage/README.md) |
| E18 | 26-10-2026 | `[LGA]` GetDfeDrvParam (`0x4389b320`): lee los u16 `+0xa`, `+0xc`, `+0xe` del registro DFE (`0x28` bytes) de dos ids, uno fijo (`0xb` → `0xfc0`, valor por defecto `0xfc4` si falla) y otro de `r8+0x6a4`; 13 de los 69 ids resuelven a siete registros estáticos (sumas `0x23e`, `0x2c4`, `0x326`, `0x474`, `0xec`, `0xfc0`); el modo solo entra por el segundo id (seguimiento en E19) | [S403 adenda](capture/s403-cierre-pendientes.md) |
| C5 | 26-10-2026 | Pruebas para `memscan`, `dual_scan` y `e10_vtable_refs` (`tests/test_s403_utilidades.py`, 4) y para `build_pages_status` (2) | [auditoría](capture/s403-cierre-pendientes.md) |
| C6 | 26-10-2026 | Auditoría mecánica del repositorio: `scripts/audit/repo_audit.py` escribe `knowledge/audit/estado.json` y la memoria temporal `memoria.json`; prueba `tests/test_repo_audit.py` | [auditoría](capture/s403-cierre-pendientes.md) |
| D7 | 26-10-2026 | Documentos de estado sin rastro del 26-10 (`STATE`, `CURRENT`, `PROGRESS`, `CONTEXT`, `NEEDS-HUMAN`, backlogs A–E): bloque «Estado vigente — 26-10-2026» y estados de S515, S516, S628–S630 alineados con D2 | [auditoría](capture/s403-cierre-pendientes.md) |
| D8 | 26-10-2026 | Tres rutas citadas que no existían (prueba de S68, `state_readers.json` y `verify_timing.py`) apuntan ahora a los archivos reales; la cifra de pruebas de S68 pasa de 7 a 19 | [auditoría](capture/s403-cierre-pendientes.md) |
| D9 | 26-10-2026 | DESCARTADO: otras 12 cifras «N pruebas» de documentos históricos difieren de lo colectado hoy (crecieron o cuentan subpruebas); son instantáneas de su fecha y no se reescriben | [estado.json](../knowledge/audit/estado.json) |
| E19 | 26-10-2026 | Campo `+0x6a4` (id DFE de `[LGA]`): 10 escritores `str.w` de 32 bits; 7 en el bloque de modo (escriben también `+0x6a8` o `+0x738`; un lector lee `+0x6a8`) guardan siempre la constante 1, es decir, el id 1 (registro estático `0x43bb9264`, suma 574 = `0x23e`); un reinicio masivo guarda 0 (`0x4380d2d0`); 2 son de otra estructura (matriz de paso `0x74`, `0x4376cf46` y `0x4376d1c8`). Límites: evaluación lineal, identidad de la estructura probable (campo `+0x6a8` compartido) y no demostrada por tipos, y valor inicial de la imagen | [S403 adenda](capture/s403-cierre-pendientes.md) |
| E17 | 26-10-2026 | 151 sitios de `createTopology`/`destroyTopology`: 72 con lista y 79 descartados con motivo (44 vector de registros en `this+0x9c` armado en bucle, 16 rama sin seguir, 8 listas dinámicas, 4 miembro sin tienda, 4 `std::vector` de las clases Neutral, 3 sin tienda estática); ninguno de los 79 es de un modelo de disparo (`sin_resolver_de_disparo` = 0) | [S403 adenda](capture/s403-cierre-pendientes.md) |
| E10c | 26-10-2026 | Resto de E10: `0x154990` solo lo crea la fábrica de `ComponentMovieRec` (`0x152168`) y `0x1e069c` solo se alcanza por cuatro subclases de reproducción/edición (`StillEditBase`, `BigImageOpen`, `VgaCache`, `SplitResizeImage`); `StsId=6` son solo las filas `0x2a` y `0xb4`, que ningún modelo de disparo usa (StsId {0}, {0,2} y {1}); `StillConverter` libera su propia memoria de trabajo (8 funciones con `DmmFree`/`DmmCloseAndFree`/`BufFree`). Sin resolver y sin objeto: `unitType`/formato del YC de Camera (no hay fila que lo entregue al grabador). Límites: llamadas directas; la única otra conexión de pines es una orden de texto (`0x901680`) | [S403 adenda](capture/s403-cierre-pendientes.md) |
| E10b | 26-10-2026 | Creador de las filas YC `0x2a` y `0xb4` en disparo: ninguno. Los 20 sitios de `ModelStillRec`, `ModelMovieRec`, `ModelBootEE`, `ModelBootEE3D` y `ModelCamera` están resueltos y sin filas YC; `0xb4` solo lo crea `ModelScalarPb` (reproducción, `0x65a95e`); `createTopology` se alcanza solo por llamada directa (sin punteros a la función) | [S403 adenda](capture/s403-cierre-pendientes.md) |
| E10a | 26-10-2026 | Creador del pin `0x2a` en disparo: solo seis modelos de edición (más PbCap); `ModelStillRec` usa STILL_DATA (`0x8`, `0xb0`, `0xb1`); 149 de 300 listas resueltas | [S403 adenda](capture/s403-cierre-pendientes.md) |
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
| 26-10-2026 | E15 y E12 cerrados (receptor = `kikilog.ko`); nuevo E16 (entradas indirectas de `CURTAINMODE`). |
| 26-10-2026 | E14 y E3 cerrados con límite (2/3 solo por flujo de datos). |
| 26-10-2026 | E2 cerrado con límite (activación declarada de ejecución). |
| 26-10-2026 | E8 cerrado con límite (lectores alcanzables desde la captura enumerados). |
| 26-10-2026 | E4 cerrado con límite (`trig` = argumento de IsNeedForceS1ON). |
| 26-10-2026 | D6 y D3 cerrados con límite (17/17 trazas con homólogo difieren). |
| 26-10-2026 | E16 cerrado con límite (6 raíces por puntero). |
| 26-10-2026 | E11 reclasificado BLOQUEADO (la traducción banco/bit→P4E no consta en el firmware). |
| 26-10-2026 | D4 y D1 cerrados con límite; E10 dividido (E10a cerrado); E1 reintentado sin cambio; nuevos E17 y E18. |
| 26-10-2026 | E18 cerrado con límite; E10 reducido (E10b cerrado); E17 reducido a 79 sitios; E1 sin cambio (ángulo de bytes); nuevo E19. |
| 26-10-2026 | E19, E17 y E10 (resto, E10c) cerrados con límite; E1 queda `NO_VERIFICADO` sin vías estáticas. |
| 26-10-2026 | Auditoría integral: nuevos E20, C7, C8, R3, R4, R5; cerrados C5, C6, D7, D8; D9 descartado. |
