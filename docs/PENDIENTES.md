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
7. Ningún otro documento mantiene su propia lista de pendientes: README, `knowledge/CURRENT.md` y `docs/STATE.md` solo resumen y enlazan aquí.

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
| E22 | CERRADO CON LÍMITE | Seguir `G+0x784` aguas abajo: hecho hasta `0x4378dfdc` y el gestor `0x4359xxxx` (no arma orden CAIF). Segunda pasada: las globales no salen del clúster `0x4378dd..e2a0`; el tipo 2 solo cambia constantes de temporización (`0x51762b/0xeaa/0xa2ec`). Tercera pasada: el registro es de relojes y el `+0x784` de `0x43737228` no es G. Sin camino hallado a CAIF; reabrir solo con traza del bus o volcado de Darwin | Hallar el emisor CAIF del disparo y comprobar si el bit `0x20` sale | [informe](capture/tipo2-analisis-estatico-2026-10-26.md) |
| E23 | ABIERTO (decisión del usuario) | Vía de parcheo de Darwin por actualización oficial: `0640_darwin` se reescribe con CRC-32 como única comprobación del updater. Falta: portar la puerta Silent de la A7S, recalcular sumas, comprobar que `ud_darwin_firmup` no valida más y que la cámara acepta un FDAT propio | Parche mínimo tipo 0 preparado en `analysis/darwin-patch/` (sin FDAT ni instalación). Emisor candidato (ID `0x16`, 210 B) DESCARTADO en T022: bloque a cero en vivo, el tipo de mecanismo no viaja por BIONZ→Darwin (probable config propia de Darwin). Vía RAM en `av-cam` descartada en la práctica (T023: los buffers de los IDs `0x0f/0x12/0x13` también a cero tras disparar); solo queda el FDAT de Darwin (sin autorizar). `ud_darwin_firmup` analizado: solo valida formato `VERM.mm` y CRC-16 del enlace; sin `darwin_boo.bin` reescribe el core siempre. FDAT tipo 0 (versión 3.22) generado y verificado por descifrado (`scripts/darwin_fdat_build.py`; el empaquetador reproduce el FDAT oficial byte a byte); sin instalar. Queda sin verificar el bootloader del MCU y que la cámara acepte el FDAT; ver informe. Exige flasheo (excluido hoy) y además el paquete Silent desde LIRO; solo con autorización expresa del usuario | [informe](capture/darwin-via-actualizacion-2026-10-26.md) |
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


## D. Físico (diferido por instrucción del usuario hasta cerrar la ingeniería inversa necesaria)

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| F1 | PARCIAL | P21 hecha (T021: `D+0x86`=`0x4c`/`0x4e` forzado en el disparo; dos disparos normales, sin efecto). T020: parche RAM del selector `0x83793166` ⇒ `G+0x784`=2 con 3 disparos, sonido normal (cubre P4; el tipo 2 no cambia el obturador). P3 hecha con límite (T019: sin efecto en latencia/tamaño, pero el forzado es intermitente). P2 hecha (T018: `G+0x808` se revierte en <80 ms; forzarlo exige bucle). P6 hecha (T014–T016: el shell de servicio no lee Darwin; `sio3/4` sin verificar). P1 hecha (T012, corrige T011: `+0x210` = 1 es EFCS desactivado; `G+0x808`=`0x120983c8`/`G+0x784`=0 en reproducción, `0x8040b24a`/1 en disparo; avance y modo de disparo no lo cambian). P1–P8 (P5 descartada con F4, P7 descartada: sin material de flicker; P3 pierde su criterio de imagen): observación de `G+0x808` (en reposo vale `0x120983c8`; P2/P3 escriben `0x120983c9`), forzado de tipo, traza en bus, shell de servicio, prueba de imagen, `+0x210` | Ejecución con autorización expresa, backup NVRAM previo | [plan](capture/physical-test-plan.md), [revisión](capture/physical-test-review-2026-10-26.md) |
| F2 | DIFERIDO | P9–P12: propuestas derivadas de S401/S402 (P9 y los casos «Silent A7S» bloqueados: sin A7S; P10 exige fijar antes el offset en la A6000) | Ídem | [mapeo S402](capture/s402-physical-test-mapping.md), [revisión](capture/physical-test-review-2026-10-26.md) |
| F3 | PARCIAL | P20 (T003, negativa) y P18 (T004: gates `+3/+6` = 0 en reposo, disparo, live view y medio pulsado; faltan otros drive/obturador) hechas; P16 también (T006: tabla constante en reposo y disparo, escritor de arranque sin identificar). P13 (T007) leída en reposo: `0xfc02a00c` = 0, no `0xf00`/`0xfff` (durante captura sin medir). P14 y P15 (T008) leídas en reposo, sin interpretación física. P19 (T009/T010): latencia EFCS ≈ 0,11 s menor (4 %), ráfaga sin medir. P17 y P7 (imagen con hélice/LED de flicker) DESCARTADAS el 26-10-2026: el usuario no dispone del material. Resto: P21 (P17 fusionada con P7; P16/P18 con línea base en reposo): lecturas de MMIO/RAM (gates `+3/+6`, DFE `0xfc02a00c`, canales `w0`, segunda matriz), latencia EFCS, modo fuera de vocabulario | Ídem; P0.2 decide si P13–P15 son viables (solo por RMEM, una página por sesión) | [plan 2](capture/physical-test-plan-2.md), [revisión](capture/physical-test-review-2026-10-26.md) |
| F4 | DESCARTADO | Traza pasiva CIS0+XPI+VD y analizador lógico en cortinas: requieren abrir la cámara. Descartado el 26-10-2026 por decisión del usuario: no se abrirá la cámara; solo software con la cámara conectada por USB | Reabrir solo si el usuario revoca la decisión | [plan](capture/physical-test-plan.md) |
| F5 | DESCARTADO | Acción real de Darwin sobre las bobinas y bootloader del FM3 (no está en el firmware). Descartado el 26-10-2026: exige hardware (misma decisión que F4) | Ídem | [plan](capture/physical-test-plan.md) |
| F6 | ABIERTO | Decisión S51: A=NO, B=NO, C=NO (sin ruta demostrada, sin base para parche, sin prueba de imposibilidad). Actualización 26-10-2026: T020 muestra que parchear en RAM el selector fuerza el tipo 2 y la cámara dispara; con el tipo 2 efectivo el usuario oyó disparos normales: no hay cambio de obturador | Se revisa solo si F1–F5 o D5 aportan evidencia | [S51](capture/s51-decision.md) |
| F7 | PARCIAL | P22 (traza lógica `CIS0_SCK/SI/XCS`, `CIS0_VD`, `CIS0_IMG_RST`, XPI en 1/1000 s, 1/4 s y EFCS) DESCARTADA el 26-10-2026: abre la cámara. P23 (lectura `0xf2a1xxxx` tras el flanco de `GPIO_9`) sigue DIFERIDA, solo software: propuesta de S55/S57/S31 que no tenía número | Ídem para P23 | [revisión](capture/physical-test-review-2026-10-26.md) |
| F8 | BLOQUEADO | P24: valores solo en ejecución (rectángulos de `0x436c25d0` de E20, `params[+9]`, activación de `RecordImage`/`0x40193`, `[estado+8]` de S134/S384); S134/S384 los remitían por error a P1 | Depurador o hook en cámara, inexistente | [revisión](capture/physical-test-review-2026-10-26.md) |

## E. Repositorio y respaldo

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| R1 | ABIERTO | **No están en GitHub, por diseño**: `firmware/` (5,3 GB), `analysis/camera-dumps/` (3,1 GB, con backups NVRAM/flash de la cámara), proyectos Ghidra, `*.bin`/`*.elf`, manuales con copyright, `.venv/`. De los volcados solo se versionan README y SHA256SUMS. No hay copia remota: un fallo del disco los pierde | Decisión del usuario sobre un respaldo externo propio; no se suben a GitHub | `.gitignore` |
| R3 | BLOQUEADO | La copia de `analysis/ghidra/s37-input/libmprctrl.so` (biblioteca ELF ARM de Sony, 221 700 B) ya no está en el árbol (R3a), pero **sigue en el historial público** desde el primer commit (`ac94c961`) | Decisión del usuario: reescribir el historial (`git filter-repo` y `git push --force`) cambia todos los SHA y exige que los clones se rehagan; no se hace sin orden expresa. Preparado: `scripts/r3_prepare_history_rewrite.sh DIR` genera en un clon aparte el historial sin el binario (515 commits, 0 rastros; comprobado 26-10-2026) sin tocar `origin` | auditoría 26-10-2026 |

## Cerradas (no borrar)

| ID | Fecha | Qué se cerró | Evidencia |
|---|---|---|---|
| D11 | 26-10-2026 | Fechas «27-10-2026» corregidas a 26-10-2026 en este archivo, en [S403](capture/s403-cierre-pendientes.md) y en CURRENT; commits `60d04b4f` y `22a84402` fechados el 26-10-2026 (`git log`). El archivo histórico del README no se toca | `git log --format=%cd` |
| D12 | 26-10-2026 | `repo_audit.py` ya no cuenta como enlace el código en línea ni los destinos absolutos del sitio (`/…`); los 3 casos eran falsos positivos (`obj->vtable[slot](...)`, ejemplo de `old.md`, `/rea/product-catalog.json`); 0 enlaces rotos | [estado.json](../knowledge/audit/estado.json) |
| D10 | 26-10-2026 | Reorganización documental: README (portada), `knowledge/CURRENT.md` (contexto mínimo), `docs/STATE.md` (conclusiones vigentes) y nuevo `docs/INDEX.md` por subsistema; versiones íntegras anteriores en `docs/history/` y `knowledge/history/`; protocolo de sesión en `AGENTS.md`/`CLAUDE.md`/`docs/agent/` | [INDEX](INDEX.md), [CURRENT](../knowledge/CURRENT.md), [PROGRESS](../knowledge/PROGRESS.md) |
| C1 | 25-10-2026 | `unicorn 2.1.4` instalado en `.venv`; los 8 módulos S56–S61 se colectan y pasan (315 pruebas, 36 subpruebas) | [S403](capture/s403-cierre-pendientes.md) |
| C2 | 25-10-2026 | `tests/knowledge/test_mcp_server.py` colecta y pasa (6) con el `.venv`; el fallo era del entorno sin `mcp` | [S403](capture/s403-cierre-pendientes.md) |
| C3 | 25-10-2026 | mypy sin errores en `scripts/knowledge` y `tests/knowledge` (21 archivos): aserciones de tipo y `mypy.ini` para `capstone` | [S403](capture/s403-cierre-pendientes.md) |
| C4 | 25-10-2026 | Suite integral ejecutada completa: 3521 aprobadas, 35 omitidas, 0 fallos, 529 s | [S403](capture/s403-cierre-pendientes.md) |
| D2 | 25-10-2026 | Módulos S515 `[BL]`, S516 `[PNL]`, S628 `[FILE_NUM]`, S629 `[FSYSMODE]`, S630 `[RING_DIAL]`: informe y 8 pruebas | [informe](capture/s515-s516-s628-s630-modulos.md) |
| E21 | 26-10-2026 | Lecturas de los volcados del 20-10 sin cámara: `arm7sram` = código ARM de un coprocesador ARM7 (no Darwin; arranque y vectores leídos, papel en el obturador sin establecer), clave Backup `0x3000b` idéntica en las 18 copias (256 B, 10 bytes a 1; `+3`/`+6` a 0), matriz `0x43e80160` = tabla de 13 registros de 0x30 B con pares ancho×alto; escritor solo en ejecución. Límite: los volcados son instantáneas en reposo | [E21](capture/e21-lecturas-backups-2026-10-26.md) |
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
| E20 | 26-10-2026 | `[EXL]` sí puede rechazar una captura: `hsiz_arcout > 2240` (`0x8c0`), `arcout > arcin` y `hsiz_sig > 2240` registran el aviso y ponen a 0 la bandera que devuelven `0x436ca820` y `0x436cafc0`; la bandera sube por `0x43ad5b02` y `0x43ad5998` hasta `0x436c25d0`, que devuelve el código 7 sin ejecutar el resto; `0x437f5a04` lo registra como `snrBusThroughPrereviewParamSet Error!` y aborta. Límite estático agotado (26-10-2026): el ancho y el alto de salida se acotan aguas arriba a 2208 y 1242 (`0x43ad5998`), pero los rectángulos de entrada de `0x436c25d0` los arman en ejecución sus dos llamadores (`0x437f5a04` y el que contiene `0x438cb7ca`) con estado vivo del sensor (`r4+0x568`); los valores por modo de disparo no salen del binario | [auditoría](capture/s403-cierre-pendientes.md) (`analysis/s403_pendientes/e20_exl.py`, `tests/test_s403_e20_exl.py`) |
| C7 | 26-10-2026 | Las 11 herramientas fuera de línea tienen prueba sintética sin firmware ni cámara (ELF/volcados construidos al vuelo; `fdat_guard_probe` se comprueba por AST: nunca llama a `switchMode` ni `writeFirmware`): `tests/test_s404_herramientas_offline.py`, 11 pruebas | [auditoría](capture/s403-cierre-pendientes.md) |
| C8 | 26-10-2026 | `build_pages_status.py` acepta un directorio de salida (argumento opcional) y `tests/test_pages_status.py` escribe en un directorio temporal: la suite ya no modifica `site/` ni `docs/progress/` | [auditoría](capture/s403-cierre-pendientes.md) |
| R3a | 26-10-2026 | `libmprctrl.so` retirado del índice de git (`git rm --cached`; queda la copia local) y añadido a `.gitignore`; ningún código ni prueba lo leía desde esa ruta (`tests/test_s113_cam_dmm.py` usa la copia de `firmware/`). El historial sigue pendiente (R3) | [auditoría](capture/s403-cierre-pendientes.md) |
| R2 | 26-10-2026 | `.github/workflows/tests.yml` ejecuta `pytest tests` en cada push y pull request; `tests/conftest.py` omite en CI (variable `CI` y sin firmware) los fallos de módulos que leen firmware no versionado. Verificado en un clon limpio con `CI=1`: 799 aprobadas, 1 933 omitidas, 0 fallos (dependencias en `knowledge/requirements-ci.txt`). Límite: en CI solo corren las pruebas que no necesitan firmware, así que no sustituye a la suite local (3 595 aprobadas) | `tests/test_ci_conftest.py` |
| R4 | 26-10-2026 | Cuatro `.zip` antiguos de la raíz retirados del índice (copias locales conservadas) y `/*.zip` en `.gitignore`; nada los citaba | [auditoría](capture/s403-cierre-pendientes.md) |
| R5 | 26-10-2026 | Seis registros `*.log` de `analysis/rea-independent/` retirados del índice (regenerables, ya ignorados); los tres `raw305*.jsonl` de S303 (evidencia citada por `build_tree.py`, 185 KB) se conservan con la excepción `!analysis/s303_ref_tree/raw305*.jsonl` en `.gitignore` | [auditoría](capture/s403-cierre-pendientes.md) |
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
| 26-10-2026 | Auditoría, 2.ª ronda: cerrados E20 (límite), C7, C8, R4 y R5; R3 dividido (R3a árbol cerrado, historial BLOQUEADO); D9 sigue DESCARTADO. |
| 26-10-2026 | Tercera ronda: E20 en su límite estático; R2 cerrado (CI con la suite); R3 preparado en clon aparte, historial sin reescribir. |
| 26-10-2026 | Revisión de las pruebas físicas: inventario único P1–P24, nuevos P22–P24 (F7, F8) y E21; premisas corregidas en los planes. S51 sin cambios. |
| 26-10-2026 | Decisión del usuario: no se abre la cámara, solo software por USB. F4 y F5 DESCARTADOS, P22 (F7) descartada; E6 y E11 siguen BLOQUEADOS por su parte de hardware (la vía F4 ya no existe). |
| 26-10-2026 | E21 cerrado con límite (lectura de volcados del 20-10); P16/P18 parcialmente resueltas con esos datos. |
| 26-10-2026 | Primera prueba en cámara: T001 (backup) y T003/P20 (descartada como fuente de trazas); registro en `capture/registro-pruebas-camara.md`. |
| 26-10-2026 | Decisión del usuario: P17 y P7 (flicker/hélice) descartadas por falta de material; P5 y P11 caen con F4. |
| 26-10-2026 | Reorganización documental (D10 cerrado). Corrección posterior: D11 (rotulado «27-10-2026» de E20/R2/R3 y su registro → 26-10-2026, fecha real de los commits `60d04b4f` y `22a84402`; el archivo `docs/history/README-historial-2026-10-26.md` conserva el rotulado original por ser copia íntegra) y D12 (tres enlaces falsos de `repo_audit.py`) cerrados. |
| 26-10-2026 | E22 añadido: seguimiento estático del tipo 2 (parcial). |
| 26-10-2026 | E23 añadido: vía de parcheo de Darwin por la actualización oficial (solo análisis; sin flasheo). |
| 26-10-2026 | Decisión del usuario: la prohibición de flashear deja de ser absoluta; se levanta solo con autorización expresa del usuario para un caso concreto (no cambia "sin cámara"/"sin firmware ejecutado" salvo que también se autorice). Actualizado en CLAUDE.md, AGENTS.md, README.md, docs/STATE.md y demás documentos normativos. E23 sigue abierto: la autorización no se ha dado todavía. |
