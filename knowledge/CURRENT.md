# Estado actual — léeme primero

Contexto operativo mínimo para agentes. Última revisión: 28-10-2026 (E25-16 y T052-A: productor nativo de `r5`, VTS sin leer y predicado de cuadro extra; R1 pendiente de copia externa). Este archivo **no** es
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
- **Recuperabilidad y B1a ([E25-04](../docs/capture/e25-04-recuperabilidad-y-decision.md)): A=NO, B=NO, C=NO, D=NO,
  E=SÍ, F=NO, G=NO.** No hay recuperación independiente de Darwin demostrada (USB, bootloader sin la aplicación
  o hardware verificado); B1a **no es instalable**. R1: procedimiento y manifiesto listos (62/62, `verify` OK contra
  el origen), **copia externa sin verificar**. La única acción que cambia G exige hardware (donante + SWD/UART).
  **E25-05**: paquetes **3.23** (tipo 0 + B1a) y **3.24** (recuperación con Darwin oficial) preparados y verificados
  offline en directorios separados (69 comprobaciones, 0 fallos). El 3.24 reutiliza el payload verificado del 3.23
  y **solo funciona si la cámara conserva acceso al actualizador**; no es recuperación independiente del MCU.
  Versiones: `3.22 < 3.23 < 3.24`; el antiguo `recuperacion-323` queda obsoleto. **T040: 3.23 (B1a) instalado; la cámara arranca en 3.23; **el usuario confirma que dispara en silencio y sin error (27-10-2026; sin capturas archivadas, E25-01)**. Recuperación: `recuperacion-324` (`e1345aff…`).**
  **E25-06** (auditoría independiente): paquetes binariamente correctos (145 comprobaciones, 0 fallos;
  L=NO, N=SÍ); instalación no segura con la evidencia actual (O/P/Q/R=NO). Hay dos 3.23 con config idéntica:
  comprobar el SHA-256 antes de instalar (E25-07).
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
- **Exposición electrónica (E25-14):** el IMX235 usa `SetExposure` (`0x436f4168`; `param+0`=SHR/líneas, `param+9`=ShutMode) y un
  método de velocidad `+0x30` (`0x436f4a94`). La A6000 tiene el mismo contrato (`0x436d6f6c`/`0x436d7e08`) y **ya llama a `+0x30`
  en la foto** (`0x438c831e`), pero no tiene el armado de exposición larga del A7S (`0x436f43c0`, `obj+0x3dc=2`). El límite de
  ~65 ms es también del firmware (clamp a un cuadro). [E25-14](../docs/capture/e25-14-imx235-imx210-exposicion-electronica.md).
- **ShutMode 0 y temporización nativa (E25-15):** `SetExposure` y `+0x30` escriben bloques disjuntos (`blk+0x50/0x52/0x54/0x56/0x57` vs `blk+0x66/0x68/0x6a/0x6c`); `+0x30` no recibe ShutMode ni r5. Emulación A/B/C: solo cambian r5 y ShutMode; B (r5=1) ≈ 64–65 ms, C sigue la velocidad. El bloque `+0x30` es un código de posición (0..4095, conversión `0x436d8a90`, compartida con SetReadZ), no el Tv: corrige E25-14 A. >65 ms, bulb y 30 s siguen sin mecanismo demostrado. [E25-15](../docs/capture/e25-15-shutmode0-temporizacion-nativa.md).
- **Cálculo autónomo de `r5` (E25-16):** BIONZ ya tiene el productor nativo `0x4383fa40`, llamado por los constructores normal (`0x437b46d0`, compuerta `cap+0x11b0`) y EFCS (`0x438417c0`). Lee Tv de `record+0xf6`, período de línea de `record+0xc`, VTS de `record+0x20` y multiplicador de `imager+0x4b8` (el 2.º argumento no es el objeto de ajustes); escribe `r5` y ShutMode 0. `0x4383fd6c` copia el bloque a `cap+0x64c` y `0x438c828c` llega a `SetExposure`. Emulación con VTS 4219: T047 ±1 línea; con 4266: 47 líneas (0,71 ms) de desviación; 1/15 y mayores saturan a 0. **No se hardcodea 4219**; el valor real de `record+0x20` no se verificó. [E25-16](../docs/capture/e25-16-r5-autonomo-fotografia.md).
- **T052-B0 (28-10-2026, sin cámara):** no ejecutada físicamente. `record+0x20 ← cap+0x5e0 ← [descriptor+6]`; `ctx=0x43eaadd8`, descriptor `0x43ea13dc`, `+6=0` en reposo; el VTS de foto sigue **N** (falta el escritor/selector). **Predicado:** `0x43deb360` es el bloque 5 (`0xbc0005`) de un conjunto de 10 bloques de 0x100 B copiado de Backup/NVRAM (`0x74218`, SHA `2a42df46…e370`, `+0x10=0` en 12 backups 3.21–3.22 (pre-B1a; B1a no toca BIONZ) y en RAM); no se encontró escritor directo de `+0x10` en `av-cam`. El cuadro extra está activo: el `r5` nativo es inválido (8422/8175/7341). **C3-A no autorizable; C3-B preferible:** `r5 = 4219 − record+0xf0` es independiente de VTS/predicado y reproduce T047 (4203/3956/3122). Recolector `scripts/t052_b0_readonly.py` listo (offline separado). [T052-B0](../docs/capture/t052-b0-vts-predicado-fotografia.md).
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
- **Dictamen de seguridad (E24-04):** NO hay evidencia para autorizar otro flasheo persistente de Darwin (A=NO, B=SÍ, C=NO, D=NO, E=SÍ, F=SÍ solo RAM). Ningún fallo de Darwin tiene recuperación demostrada; M6 no es cerrable hasta trazar estado 4→`Upd` (E24-05). La aceptación del riesgo no cuenta como comprobación. [informe](../docs/capture/e24-04-dictamen-seguridad.md).

- **Ruta `Upd` y rearme (E24-05):** `InitCom → Upd → 0x45bc` trazada con bytes (solo en `Seton`; clausura C1 480 / C2 571 funciones; el arranque sigue sin binario). `0x1fe66`→0 **sí** selecciona la lista `[0,7,8,9,10]` de la máquina exterior y evita el motor (salvo el freno de la operación 5 sin compuerta); control volátil NO demostrado, watchdog NO cerrado. No cambia E24-04: sin recuperación demostrada no hay base para flashear. [informe](../docs/capture/e24-05-upd-y-rearme.md).
- **Candidato sin rearme (E25 / E25-02):** sobre el tipo 0, `0x1fe6a: 28 46 → 0a e0` (2 bytes) fuerza la compuerta a 0; L0 en los tres arrancadores, `0x1f5a6` retorna y no se alcanzan las primitivas del motor en captura/rearme. Tipo 0 intacto; P4B/P4C siguen; operación 5 (P40/P41=3, XOR=0) es **apagado**, no freno demostrado. **E25-02 cierra la vía volátil: A=NO** (sin emisor BIONZ de `InitCom 0x16`; actualizador solo `0x11/0x14/0x15`; Micon `NoAction`; `0x16` copia 129 B con `length=0x81`, no 1 B). B1a válido estáticamente con auditoría independiente (42 pruebas). Candidato offline no instalable (E24-04); M0 normal estático sí, M0 físico/M1 pendientes. [E25-02](../docs/capture/e25-02-validacion-candidato-y-via-volatil.md), [E25](../docs/capture/e25-desactivacion-mecanica.md).
- **Captura y fin (E24-05a):** el ID `0x0c` (22 B) entra por la tarea `0x1811a` → `0x17f8c` → `0x1961c`, que elige entre cinco listas de la máquina de 49 estados (`S+0x44.b0`, `S+0x32`, `S+0x3c`); los estados 4/5/0x1f arrancan los rearmes y el 4 depende del predicado de clase `0x196a2`. `[0,7,8,9,10]` cumple las esperas internas de Darwin; el lector BIONZ del fin sigue sin localizar (C/D/F/G = NO; E24-05d/e). [informe](../docs/capture/e24-05a-captura-fin-bionz-darwin.md).
- **Consumidor BIONZ (E24-05d):** BIONZ recibe de Darwin ocho mensajes mss (`0x0b,0x0d,0x0e,0x10,0x11,0x14,0x15,0x17`) por la tabla CAIF `0x43fe87f0` → buzón `[0x43e77284]` → `caif_recv` `0x437db9f0` (bloquea sin plazo, exige la subclase esperada). **Corrige E24-05a:** máscara de ocupación y anillo no viajan a BIONZ (el «bloque de estado» `0x6c78` es el registro de fallos). A=SÍ, B=NO, C=NO, D=SÍ, E=SÍ, F=NO, G=NO. [informe](../docs/capture/e24-05d-consumidor-estado-darwin-bionz.md).
- **Emisores mss (E24-05f):** `0x0b` (admisión `0x17f8c`), `0x0d/0x15` (estado de captura 9/11), `0x0e/0x10` (estado 31 → FSM `0x296f0` estado 5), `0x11/0x14` (FSM de ajustes `0x294f8`, evento `0x18a`), `0x17` (`0x125f6`, orden de modo). Los cinco primeros no dependen de la compuerta `0x1fe66` y salen en el mismo orden en `[0,7,8,9,10]`; el byte 0 del `0x0b` lleva la clase de ocupación (corrige E24-05d B). A=SÍ, B=NO, C=NO, D=NO, E=NO, F=NO, G=NO; falta el disparo de `0x11/0x14/0x17` (E24-05g). [informe](../docs/capture/e24-05f-emisores-mss-darwin.md).
- **Ajustes, modo y ocupación (E24-05g):** `0x18a` eran flags de `0x29514`; `0x11/0x14` los dispara el gancho de trama `0x1c04c` o el arrancador por disparo `0x17c26` (modos 0–8); `0x17` lo pide Darwin (estado 27, modo 0), no BIONZ; BIONZ lee la clase del `0x0b` en `0x438c2538` (0 acepta, 1 reintenta ≤19, 2 error). A=SÍ, B=SÍ, C=NO, D=SÍ, E=SÍ, F=NO, G=NO, H=NO demostrada; candidatos P29 y `0x2041e`→P4E (E24-05h). [informe](../docs/capture/e24-05g-ajustes-modo-ocupacion.md).
- **Dependencias finales (E24-05h):** estado 31 con dos variantes: `S+0x32=0` espera P29 bajo (`MSS_S2_REQ_CA`, BIONZ→Darwin, sin plazo), `S+0x32≠0` (T022: `0x1600`) espera la FSM ADC-B (temporizada). Con `0x20c74=0` no hay escritura estática a P4D/P4E (P4C sí); FAIL = reintento sin avance. Sin bloqueo real demostrado ni ausencia demostrada (A=NO,B=NO,C=SÍ,D=NO,E=NO,F=SÍ,G=NO,H=NO,I=SÍ); eslabones físicos: conductor de P29 y `pkt[1]`/`pkt[2..3]` en BIONZ. [informe](../docs/capture/e24-05h-dependencias-finales-captura.md).
- **ADC-B y P29 (E24-05h-3):** ADC-B (`0x29dc8`, terminal 7) arranca (`0x19b9e`: `S+0x444` b4=0 ∧ `S+0x170` b0=0, sin leer el tipo) y termina con `0x20c74=0` por `[1,4,6,7]`; única espera = evento 0 del canal 0 de `0x40023000`; el estado 31 espera `0x203ae` sin plazo. P29→INT05; grupo de pines activo en captura sin determinar (salida en grupos 0/1/5/6, entrada en 2/4, INT05 en 3). [E24-05h-3](../docs/capture/e24-05h-3-adcb-p29.md)
- **ADC-A, P29 e IRQ (E24-05h-4):** ADC-A `[2,4,6,16,17]` (desde el estado 4 de ADC-B) retorna sin bloquear; los estados 3/32 de la captura exigen ADC-A y ADC-B en terminal (FAIL = reintento; ADC-A usa 2 eventos del temporizador base canal 11). P29 en `On` = grupo 3 (INT05, entrada). Evento de ADC-B: IRQ 32, vector `0xf8d3` (tabla base `0x42fc`). Sin bloqueo demostrado; ausencia no demostrable sin medir. Pendiente: E24-05h-5 (cámara, diferido). [E24-05h-4](../docs/capture/e24-05h-4-adca-p29-irq.md)
- **Protocolo de lectura (E24-05e/h-5, preparado, no ejecutado):** T022/T023 leen DRAM de BIONZ, no SRAM de Darwin; los valores de Darwin de E24-05h-4 §6 no tienen vía. `pkt[1]`/`pkt[2..3]` del `0x0c` los construye `0x43841070`. Matriz EFCS ON/OFF ABBAAB (6 disparos) y criterios C1–C5; una foto normal no prueba el funcionamiento sin rearme. [Informe](../docs/capture/e24-05e-05h5-protocolo-lectura.md)

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
- E23 «`0x1fe66`→0 no desactiva el rearme» queda **superado** por E24-05: la compuerta elige la lista de estados de la máquina exterior.

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
| E25 | CERRADO CON LÍMITE; E25-01/03 BLOQUEADOS; E25-15 cierra la relación SetExposure/+0x30 | Candidato offline tipo 0 + compuerta 0 (2 bytes); **E25-02 cierra A=NO** (sin emisor BIONZ de `0x16`; `0x16` copia 129 B, no 1 B); B1a auditado (42 pruebas); falta validación física (M0 físico/M1) y fin de L0/BIONZ |
| E25-04 | CERRADO CON LÍMITE | Recuperación de Darwin: A/B/C/G=NO; H exige hardware (donante + SWD/UART + corromper/recuperar); R1 sin copia externa |
| E25-05 | CERRADO CON LÍMITE | Paquetes **3.23** (tipo 0 + B1a) y **3.24** (recuperación oficial) preparados y verificados offline (69 checks); falta autorización y medida del guard; el 3.24 solo sirve con acceso al actualizador |
| E25-06 / E25-07 | CERRADO CON LÍMITE / ABIERTO | Auditoría independiente: sin defecto binario; puntos ciegos en las pruebas de E25-05; E25-07 = procedimiento con verificación de SHA-256 y `recuperacion-323` marcado obsoleto |
| E25-17 | PARCIAL | T052-B0 estático hecho sin cámara: predicado = bloque NVRAM `0x43deb360`, `+0x10=0` (cuadro extra activo), C3-A inválido; VTS de foto sin leer; C3-B (`record+0xf0` + 4219) preferido y ya respaldado por T047. Falta B0 físico (tres fotos, ambos registros, predicado) |
| E25-18 | BLOQUEADO | T052-B1: C3-B en RAM (scratch + `0x4383fa40` + `record+0xf0` + `4219 − líneas`), guardián y reversión; exige B0 físico, scratch verificado y autorización expresa; no 1/15/bulb/30 s |
| E6, E9, E11, E13, D5 | BLOQUEADO | Darwin fuera de `av-cam`; semántica de 112 registros y fin de integración; enlace banco/bit→P4E; servicio ODL/MMIO `0xf292b000`; hojas de datos IMX210/IMX235 |
| F1–F8 | DIFERIDO / BLOQUEADO | P1–P24 (inventario en [revisión](../docs/capture/physical-test-review-2026-10-26.md)); traza de bus; Darwin real; revisión de S51 solo con evidencia nueva |
| R1, R3 | PARCIAL / BLOQUEADO | R1: procedimiento y manifiesto listos (62/62), **copia externa sin verificar**; R3: historial público con `libmprctrl.so` (reescritura solo con orden expresa) |

## Bloqueos y límites de evidencia

- Sin sembrar funciones Thumb a mano REA no cubre `0x437…`/`0x438…`; usar Ghidra histórico para verificar bytes.
- Valores en ejecución (rectángulos de `[EXL]`, contenido de Backup, `params[+9]` = 2/3, activación de RecordImage) no salen del binario.
- Cobertura del censo (133/372) y 3521 pruebas aprobadas (C4, sin re-verificar hoy) no acreditan funcionamiento en cámara.

## Próximos pasos concretos

1. Si se reabre lo estático: seguir el productor de `0x10000005` hasta la entrada de estado 2 de `StateMgr` y `0x90de2e → RecordImage`;
   fijar tamaño/contenido de Backup `0x3000b` antes de atribuir valores a los gates `+3/+6`; enlaces IMX210/YC/archivo/cortina y cuerpos locales de RecordStill (ocho parejas).
2. Pedir al usuario: hojas de datos (D5), mapa de pines (E11), copia externa y verificación (R1), decisión sobre historial (R3), P10 (offset del campo de captura), medir ráfaga y verificar `sio3/sio4` si se quiere seguir con la cámara.
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
