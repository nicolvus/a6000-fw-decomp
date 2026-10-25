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
| E2 | ABIERTO | Activación real de RecordImage/RecordStill en un disparo: condiciones del check `0x907ba0` y productor externo de `0x10000005` (los dos constructores conocidos no son envíos externos) | Cadena disparo → mensaje → estado 2 demostrada por código, o declarada de ejecución | [seguimiento](capture/capture-static-followup-2026-10-25.md) |
| E3 | ABIERTO | Origen de `params[+9]` en `SetExposure` (IMX210): el llamador de `SetExposure` no se trazó; relación con Silent | Llamador y origen del valor identificados | [cierre S402 §6](capture/static-closure-2026-10-25.md) |
| E4 | NO_VERIFICADO | Nombre y efecto de cada modo `+8` de la cola `0x40193` (solo se sabe que es un índice de tabla de estado) | Tabla índice → estado nombrada | [cierre S402 §9](capture/static-closure-2026-10-25.md) |
| E5 | PARCIAL | `S[0]=&G` en A7S (evidencia estructural, no asignación) y lector del byte A6000 `+0x238` (no existe en `av-cam`) | Escritor/lector localizado o ausencia acotada | [S205](capture/s205-imager-s0-writer.md) |
| E6 | NO_VERIFICADO | Cadena CAIF → Darwin → LIRO/imager: el MCU Darwin queda fuera de `av-cam` | Solo con traza del bus o volcado de Darwin (ver F4) | [C-backlog](../knowledge/agents/C-backlog.md) |
| E7 | ABIERTO | Backup `0x3000b`: tamaño (256 B) y defaults resueltos; faltan productores anteriores de los campos y valores efectivos | Productores localizados; valores efectivos solo en ejecución | [B-backlog](../knowledge/agents/B-backlog.md) |
| E8 | ABIERTO | Estado `0x43f72d02`: condiciones de invocación y efecto de los campos; S176 acredita lectores, no activación | Lectores enlazados a una ruta de captura | [B-backlog](../knowledge/agents/B-backlog.md) |
| E9 | PARCIAL | Correspondencia funcional de los 112 registros IMX210/IMX235 restantes y mecanismo de fin de integración | Equivalencia funcional por registro; la semántica eléctrica exige hoja de datos (ver D5) | [A-backlog](../knowledge/agents/A-backlog.md) |
| E10 | ABIERTO | Ruta YC → archivo: productor de modo 1, creador del pin `0x2a` en disparo, formato YC y propiedad del buffer | Ciclo terminal de buffers demostrado | [matriz S51](capture/s51-static-coverage-and-tool-limits.md) |
| E11 | PARCIAL | Segunda cortina: enlace banco/bit `0xf2910048` → P4E y rutas alternativas de fin de exposición | Traducción física verificada | [S51](capture/s51-decision.md) |
| E12 | ABIERTO | Receptores del mensaje de `0x437b0390` y entradas indirectas de `CURTAINMODE` | Receptores identificados | [matriz S51](capture/s51-static-coverage-and-tool-limits.md) |
| E13 | ABIERTO | Servicio ODL del carril B y significado físico de sus registros MMIO (`0xf292b000..8`, canales `w0`) | Identidad de los bloques con evidencia estática | [B-backlog](../knowledge/agents/B-backlog.md) |

## B. Documental y de calidad

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| D1 | ABIERTO | Censo de etiquetas: 226 pendientes (4 `ACEPTO` sin decodificar: `[EXL]`, `[SFR]`, `[IMAGING_IMG]`, `[DECMODEMGR]`; 222 `NO_VERIFICADO`) de 372. Mide documentación, no código; no son todas prerrequisito de S51 | Revisión individual por etiqueta, priorizando captura/sensor (prioridad 0–1) | [censo](../analysis/s178_census/pendientes.md) |
| D2 | ABIERTO | Colas de módulos sin hacer: D `[BL]` (S515), `[PNL]` (S516); E `[FILE_NUM]` (S628), `[FSYSMODE]` (S629), `[RING_DIAL]` (S630) | Informe y test por módulo | [D-backlog](../knowledge/agents/D-backlog.md), [E-backlog](../knowledge/agents/E-backlog.md) |
| D3 | ABIERTO | 66 de 69 afirmaciones S605–S627 sin verificar: 20 de logger dual y 46 de equivalencia (3 verificadas estáticamente) | Cotejo módulo a módulo contra bytes | [auditoría](capture/S605-S627_tabla_hallazgos.md) |
| D4 | PARCIAL | Triaje S400: 518 filas, todas con revisión manual (322 `FALSO_POSITIVO`, 110 con rectificación respaldada, 86 `VIGENTE`). Las `VIGENTE` están razonadas, no certificadas | Cada `VIGENTE` pasa a respaldada o descartada al cerrar D3 o su historial | [triaje](../analysis/s400_open_questions_triage/README.md) |
| D5 | BLOQUEADO | Hojas de datos IMX210/IMX235 (mapa de registros, semántica de modos) | Documento legítimo aportado por el usuario; no existe público | [S51](capture/s51-decision.md) |

## C. Entorno y código

| ID | Estado | Pendiente | Criterio de cierre / límite | Fuente |
|---|---|---|---|---|
| C1 | ABIERTO | `unicorn` no está instalado: 8 módulos de test no se colectan (S56, S57, S58, S59 Claude/Sol, S60 Claude/Sol, S61). Instalarlo está permitido y no se hizo | Instalar en `.venv` y reejecutar; documentar el resultado real | [auditoría 24-10](capture/repo-audit-2026-10-24.md) |
| C2 | ABIERTO | `tests/knowledge/test_mcp_server.py` falla en la colección (ya fallaba antes de los últimos cambios) | Causa diagnosticada y test colectable | sin re-verificar su causa |
| C3 | ABIERTO | mypy: 5 errores en 3 archivos (uno por stubs de `capstone`). Deuda previa, sin tocar | Stubs o `ignore` justificado | sesión 25-10-2026 |
| C4 | ABIERTO | La suite integral (3375 pruebas recopiladas) nunca se ejecutó completa; solo hay subconjuntos aprobados | Ejecución completa documentada, con tiempo y fallos | [auditoría 24-10](capture/repo-audit-2026-10-24.md) |

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
| — | 25-10-2026 | Id de modelo estático (`@M0EF`, `@M030`) y ocho emisores = autopublicaciones; E1 queda `NO_VERIFICADO` por exclusión, no por falta de búsqueda | `dd3a8212` |
| — | 25-10-2026 | Revisión manual de las 44 filas `VIGENTE` sin revisar del triaje | `dd3a8212` |
| — | 25-10-2026 | RecordStill/RecordImage A6000≡A7S (25 + 174 pares, solo cambian líneas de log) | [cierre S402 §2](capture/static-closure-2026-10-25.md) |
| — | 25-10-2026 | Servicio `sta_tsk` y transporte OSAL de `0x40193`; escritor `S[0]`; constructor CAIF A7S; S176 reproducido | [seguimiento](capture/capture-static-followup-2026-10-25.md) |

## Registro de cambios de este documento

| Fecha | Cambio |
|---|---|
| 25-10-2026 | Creación a partir de la revisión integral del repo: 13 pendientes estáticos, 5 documentales, 4 de entorno, 6 físicos, 2 de respaldo. |
