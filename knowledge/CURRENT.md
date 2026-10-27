# Estado actual — léeme primero

Contexto operativo mínimo para agentes. Última revisión: 26-10-2026 (reorganización documental). Este archivo **no** es
historial ni fuente de verdad de los pendientes: ver [Responsabilidades](#responsabilidades-documentales).
La versión íntegra anterior (2264 líneas, instantáneas S59–S627) está en
[history/CURRENT-historial-2026-10-26.md](history/CURRENT-historial-2026-10-26.md); nada se borró.

## Objetivo técnico vigente

Determinar con evidencia **estática** si la Sony A6000 (fw 3.21, sensor IMX210) puede capturar a resolución completa sin
cierre mecánico (obturador totalmente electrónico). Se separa siempre `VERIFICADO` / `INFERENCIA` / `NO_VERIFICADO`;
el análisis estático no prueba ejecución ni ausencia en cámara. Comparación con A7S fw3.20 (IMX235, tiene Silent) y
A6300 fw2.01 (controles positivos). Restricciones: sin ejecutar firmware, sin cámara, sin parche, sin
flasheo salvo autorización expresa del usuario para un caso concreto.

## Estado actual

- **Decisión [S51](../docs/capture/s51-decision.md): A=NO, B=NO, C=NO.** No hay ruta de exposición totalmente electrónica
  demostrada (A), ni base para un parche justificable (B), ni prueba de imposibilidad por hardware (C). Sin cambios desde S51.
- Estático: todo cerrado **con límite** salvo E1 (`NO_VERIFICADO`, sin vías estáticas); lo restante está bloqueado por datos
  (E6, E9, E11, E13, D5) o es físico (F1–F6; pruebas por USB ya hechas el 26-10-2026: T001–T021, ver [registro](../docs/capture/registro-pruebas-camara.md); el tipo 2 se fuerza y no cambia el obturador; E22 cerrado con límite). Lista y estados:
  [PENDIENTES](../docs/PENDIENTES.md).
- Los censos (133/372 etiquetas, 35,75 %) y las cifras de pruebas **miden documentación**, no código descompilado ni
  funcionamiento físico. Datos de auditoría: [estado.json](audit/estado.json), [memoria.json](audit/memoria.json)
  (`python scripts/audit/repo_audit.py`).

## Hallazgos críticos confirmados (VERIFICADO salvo nota)

- **Captura:** RecordStill (`0x908afc`) y RecordImage (`0x90b248`) de `libObj.so` A6000 ≡ A7S (199 pares, solo cambian líneas
  de log); RecordImage llama a RecordStill; llamadores BL `0x90de2e` y `0x91634e`; 25 punteros Thumb a `0x90d7e8` son
  `call_fn` de `StateMgr::_FuncEntry`, ejecutados por `StateMgr::CallFunc` (`libmprctrl.so:0x1cef2`). Activación real: `NO_VERIFICADO`.
  [S402](../docs/capture/static-closure-2026-10-25.md), [contrato](../docs/capture/recordstill-contract-audit-2026-10-23.md).
- **Cola `0x40193`:** construcción desde literales `.text` (LDR), 16 B hasta `osal_snd_msg`, receptor LIRO `0x4381d16c`, tabla
  `0x44000174` (35×12 B); servicio LIRO `+0x3c` = `sta_tsk(0x46, descriptor)`; recepción bloqueante. Instalador `0x4379e93c`
  (fila 189 de 372 punteros Thumb, bucle `0x4356082c`). Ejecución real no observada. [flujo](../docs/capture/queue-40193-flow-2026-10-23.md),
  [seguimiento](../docs/capture/capture-static-followup-2026-10-25.md).
- **Mensaje `0x10000005`:** dos constructores (PlayData y secuencia `0x3026`); único emisor de `ObjMsg(0x3a49,0x3026)` = `0x659cb0`
  (acción 13 de `ModelScalarPb`). Quién publica el local `4`/`2` a Pb/PbCap: ningún código de `libObj` (E1).
- **Imager IMX210:** estado `0x43f72d02` (A7S `0x43f7bce6`): gates `+3/+6` idénticos en ambos y **sin escritor** (S300/S301);
  Backup `0x3000b` = 256 B con gates a 0; `S[0]` y copia G→S resueltos (S205); mecanismo por modo
  `modo → matriz 69/59 filas → T1/T2/T3 → pares (flag,bit) → máscara u16 → MMIO DFE/CISIF (0xfc02a00c)` idéntico en código
  A7S/A6000; la diferencia está en los **datos** (34 vs 13 modos). Síntesis: [S341](../docs/capture/s341-synthesis-b2.md).
- **Silent A7S:** UI → LIRO `0x40e3` → `+0x250` → bit `0x20` (`no_silent`); el driver IMX210 conmuta modos 0–4, el IMX235 0,1,3,4;
  `…ForLiro` rechazado (0 soportados) en A6000 y A7S ([S174](../docs/capture/s174-forliro-api.md), [S383](../docs/capture/s383-forliro-silentlibobj.md)).
  La A6000 carece del parámetro y del código de selector/tiempos de la A7S (S307–S312, S169). Ausencia estática ≠ incapacidad de hardware.
- **Cortinas:** GPIO P4D=1ST_CURTAIN_MG, P4E=2ND_CURTAIN_MG, P4C=CA_1ST_CURTAIN_START, P4B=CA_RELEASE_LOCK_MSS (esquema + inspección;
  no son serie). El enlace banco/bit `0xf2910048` → P4E no consta en el firmware (E11).
- **Recuperación (E24-01):** Darwin también controla la energía del cuerpo (`DD_ON1/2/3` desde `darwin_core`, tabla `0x28c6c`).
  No está demostrado que el actualizador USB arranque sin `darwin_core`. Cualquier parche de Darwin arriesga la vía de reinstalación.
  [informe](../docs/capture/e24-01-arranque-recuperacion.md).
- **Bootloader de Darwin (E24-02):** hay arranque propio en `0x0–0x41ff` (el core salta a él con el buzón `[0x20000706]=4`); protocolo de
  `ud_darwin_firmup` reconstruido (`0x11/0x14/0x15`, CRC-16). No está demostrado que reprograme una aplicación rota ni que encienda
  el BIONZ solo (A=SÍ, B=NO, C=NO). Un parche de Darwin no debe tocar encendido, `InitCom`, `Upd` ni el watchdog.
  [informe](../docs/capture/e24-02-protocolo-actualizacion-darwin.md).
- **Recuperación (E24-03):** respaldos íntegros pero incompletos; el FDAT 3.23 lleva el `darwin_core` original y se reconstruye bit a bit, pero solo está
  demostrada una restauración de NVRAM (A=NO, B=SÍ, C=NO, D=NO). El guard exige versión mayor: el script 3.21 ya no sirve; un FDAT 3.24 exigiría recuperación 3.25.
  [informe](../docs/capture/e24-03-auditoria-recuperacion-usb.md).

## Correcciones fundamentales (no reutilizar las versiones previas)

Para la trazabilidad completa: [CORRECTIONS](../docs/CORRECTIONS.md) y [STATE § Conclusiones corregidas](../docs/STATE.md).

- S401 negaba el manejador LIRO `0x40e3` en la A7S: **sí existe** (fila `0x43ff79e4` → `0x437a9cb1`); lo corrige S402.
- La etiqueta `RecordStill::Execute` de A6000 `0x90b248` no está demostrada: es **RecordImage**; RecordStill es `0x908afc`.
- Destinos BL `0x7484dc`/`0x755af8` (S382) y los encodings MOVW/MOVT de `0x40193` (S384) eran falsos; el ID sí se construye desde `.text`.
- S305 original invalidado por sesgo `+0x58`; tabla148/fila18 → Backup `0x3000b`. S303 corrigió el mismo sesgo de S303rev1/S304.
- Carril B: S325 corrige S302/S321 (mapa **posición→columna**, no modo→columna); S329 corrige bases T2/T3 (4 B menos) y no hay tabla de
  tiempos por modo; S331 refuta S327/S330 (`obj+0x2b4` es un flag de log; la fila es la posición del modo); `0x43fef404` es la tabla
  de ids de `Camera::Lens::ODL`, no de tiempos (S337→S342/S347/S348).
- Cadenas ≠ funcionalidad: la cadena `rolling` del A6300 está muerta (S168); los 128 B de `0x43dcfa9e` no tienen referencias (S172, corrige S135).
- S605–S627: las pruebas originales ocultaban siete gemelas erróneas y 13 textos truncados; logger dual verificado solo en S607/S611/S616;
  66 de 69 afirmaciones de equivalencia siguen sin verificar ([auditoría](../docs/capture/S605-S627_tabla_hallazgos.md)).
- S207 no demuestra ausencia de un fin de integración (JSON/generador declaran `NO_VERIFICADO`). S51 A/B/C no se altera sin evidencia nueva.
- Darwin: base ROM `0x4200`, no `0`. SetImageWrited = `0x6108/0x1007`, no `0x1009`.

## Decisiones técnicas vigentes

- **REA primero**, Ghidra histórico (`silent-liro.gpr`, readOnly) como respaldo; una consulta vacía de REA no prueba ausencia.
  Una sola sesión `session_daemon.py` + `q.py` (`av-cam.bin` ~8 min en frío); verificar lo decisivo contra bytes. Detalle:
  [STATE § Política de ingeniería inversa](../docs/STATE.md).
- Pruebas en cámara solo por USB/software (la cámara no se abre); antes de cualquier prueba, backup NVRAM y registro T0NN.
- Commits convencionales por fase; actualizar [PENDIENTES](../docs/PENDIENTES.md) en el mismo commit; nunca firmware ni archivos ignorados.

## Pendientes activos prioritarios (autoridad: PENDIENTES)

| ID | Estado | Qué falta |
|---|---|---|
| E1 | NO_VERIFICADO | Origen del local 4/2 a `ModelScalarPb`/`ModelPbCap`; todo emisor posible es de datos o ejecución |
| E6, E9, E11, E13, D5 | BLOQUEADO | Darwin fuera de `av-cam`; semántica de 112 registros y fin de integración; enlace banco/bit→P4E; servicio ODL/MMIO `0xf292b000`; hojas de datos IMX210/IMX235 |
| F1–F8 | DIFERIDO / BLOQUEADO | P1–P24 (inventario en [revisión](../docs/capture/physical-test-review-2026-10-26.md)); traza de bus; Darwin real; revisión de S51 solo con evidencia nueva |
| R1, R3 | ABIERTO / BLOQUEADO | Sin respaldo externo de firmware/volcados; historial público con `libmprctrl.so` (reescritura solo con orden expresa) |

## Bloqueos y límites de evidencia

- Sin sembrar funciones Thumb a mano REA no cubre `0x437…`/`0x438…`; usar Ghidra histórico para verificar bytes.
- Valores en ejecución (rectángulos de `[EXL]`, contenido de Backup, `params[+9]` = 2/3, activación de RecordImage) no salen del binario.
- Cobertura del censo (133/372) y 3521 pruebas aprobadas (C4, sin re-verificar hoy) no acreditan funcionamiento en cámara.

## Próximos pasos concretos

1. Si se reabre lo estático: seguir el productor de `0x10000005` hasta la entrada de estado 2 de `StateMgr` y `0x90de2e → RecordImage`;
   fijar tamaño/contenido de Backup `0x3000b` antes de atribuir valores a los gates `+3/+6`; enlaces IMX210/YC/archivo/cortina y cuerpos locales de RecordStill (ocho parejas).
2. Pedir al usuario: hojas de datos (D5), mapa de pines (E11), decisión sobre respaldo (R1) e historial (R3), P10 (offset del campo de captura), medir ráfaga y verificar `sio3/sio4` si se quiere seguir con la cámara.
3. Mantener la documentación según el protocolo de abajo.

## Protocolo de sesión

**Al empezar:** instrucciones del proyecto (`AGENTS.md`/`CLAUDE.md`) → este archivo → pendientes relevantes en
[PENDIENTES](../docs/PENDIENTES.md) → solo los informes necesarios (buscar con `scripts/knowledge/search.py`, por tema en [INDEX](../docs/INDEX.md)).
**Durante:** `knowledge-navigation`, `contradiction-audit` antes de reutilizar un hallazgo; marcar `VERIFICADO` / `INFERENCIA` / `NO_VERIFICADO`.
**Al terminar (en este orden):** informe en `docs/capture/` (+ prueba/evidencia) → fila afectada de PENDIENTES → [STATE](../docs/STATE.md) si cambió una conclusión
→ este archivo solo si cambió el contexto mínimo (máx. ~150 líneas; no añadir un párrafo por sesión) → una entrada en [PROGRESS](PROGRESS.md)
→ `python scripts/knowledge/build_subsystem_index.py` y `knowledge-maintenance` → commit y push. El README **no** se toca por una sesión nueva.

## Responsabilidades documentales

[README](../README.md) portada pública · **este archivo** contexto mínimo · [STATE](../docs/STATE.md) conclusiones y límites vigentes ·
[PENDIENTES](../docs/PENDIENTES.md) tareas (única fuente) · [PROGRESS](PROGRESS.md) historial cronológico ·
[INDEX](../docs/INDEX.md) informes por subsistema · `docs/capture/` informes · `analysis/` evidencia · `tests/` verificadores ·
[subproyecto](../projects/electronic-shutter/README.md) · archivos históricos en [docs/history/](../docs/history/) y [knowledge/history/](history/).
