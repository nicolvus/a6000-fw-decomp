# S83 — Los módulos "menores" del firmware, decodificados (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: identificar por evidencia qué hace
cada uno de los módulos de tamaño medio del `av-cam.bin` que el mapa de S79 dejó sin descodificar.
No es la línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD, ni ZPD (S75), ni ZIT (S80),
ni ADF (S81), ni las caras (S71).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s83_modules.py`.

---

## 1. Método (VERIFICADO)

Para cada prefijo de log se toman las primeras cadenas del módulo y se leen sus **nombres de función
y sus campos de estado**: es la evidencia disponible en el propio firmware. Lo que sigue es la
lectura de esa evidencia, no una conjetura.

## 2. Los módulos decodificados

### 2.1 `[ACCY]` — accesorios (106 trazas) — VERIFICADO

`[ACCY][INFO][HW]:AD=%d, ID=%d` (`0x43c24cac`) → **enumeración de accesorios** con dirección e ID.
`NotifyAttachedUart(%08X)` (`0x43c24cca`), `NotifyAttached(%d)` (`0x43c24cf7`), `NotifyDetached`
(`0x43c24d1e`), `NotifyUartCommand[%c%c%c...]` (`0x43c24d41`), `Uart Send Err` (`0x43c24d71`),
`NotifyUartResponse[%c%c%c...]` (`0x43c24d94`) → la cámara **habla por UART con los accesorios**
(hotshoe) y notifica su conexión/desconexión. Es el mismo hardware que el grupo de colas
`MSGQ_GID_HOTSHOE_INFRA1` del framework ADF (S81).

### 2.2 `[CAM_FUNC_MGR]` — gestor de funciones de captura (43 trazas) — VERIFICADO

- `CAPCON WARNING! FILE:%s LINE=%d func:%s param=%x %x %x` (`0x43ca12af`).
- `SyncProcMargin[usec] HS0:%u HS1:%u HS2:%u HS3@CPU2:%u HS3@CPU0(IDT):%u HS3@CPU3(RCH):%u`
  (`0x43ca12f6`) → **márgenes de sincronización** entre los flujos HS0..HS3 y **las tres CPU**
  (CPU0 = IDT, CPU2, CPU3 = RCH).
- `SetCapMode:Invalid CapMode[0x%x: %d: %d: %d: %d]` (`0x43caf036`) → el **modo de captura** es un
  parámetro con 4 sub-valores.
- `receive[%d,%d] before comp[%d,%d] (QUEUEING)` (`0x43caf077`) y `(FAILED)` (`0x43caf0b4`) → control
  de orden entre recepción y completado.

### 2.3 `[ENCOUCSTAT]` — estado de la codificación de vídeo (49 trazas) — VERIFICADO

`AVC_ENC_VIDEO_ERR_STATE/MEMORY/PARAM/INDEX` (`0x43c50693`–`0x43c50730`), `ES Overflow!!`
(`0x43c5066b`), `MSG SET ERROR` / `MSG SEND ERROR` (`0x43c505bc`/`0x43c50631`) → **códigos de error
del codificador AVC (H.264)** con su estado (state), memoria, parámetros e índice.

### 2.4 `[VIDENCSTAT]` — estado del encoder de vídeo (70 trazas) — VERIFICADO

`[VIDEO INFO] Pts = 0x%08x EndFlug = 0x%02x` (`0x43cd680b`) → **PTS** (timestamp de
presentación) y marca de fin; `Notify Final Es` (`0x43cd6843`); `augi,paddingAreaLength:%#x`
(`0x43cd6861`) → el encoder de vídeo **consume bloques de datos "AUGI"** (ver §2.8) con *padding*;
`ExecuteEncPictureFailure` (`0x43cd6888`); `Use 2nd Latest Index` (`0x43cd68af`).

### 2.5 `[ENCSEQCTRL]` — control de secuencia de encoding (46 trazas) — VERIFICADO

`[O/U Crank] Table[%d] fR[0x%x] sR[0x%x]` (`0x43c4bd2b`) y `OuCrank Config Err: FrameRate = %x,
SamplingRate = %x` (`0x43c4bd5f`) → tabla de **frame rate y sampling rate** por crank (tabla de
velocidades); `[state]0x%x -> 0x%x` (`0x43c4bda2`); `Warning, m_beginEncCompTime < refTime, change
state forcibly` (`0x43c4bdc4`) → **máquina de estados** del secuenciador de encoding con corrección
forzada de estado por retraso.

### 2.6 `[SAD]` — gestor de programas del SA (45 trazas) — VERIFICADO

`Same Unit Handle Get` (`0x43ce546b`), `same hndl get_cnt=0x%08x` (`0x43ce5486`), `alloc_cnt=0x%08x`
(`0x43ce54a5`), `!!! CdcSaPrg Hdr Err !!!` (`0x43ce55bc`), `!!! NmlSaPrg Hdr Err !!!`
(`0x43ce55db`), `!!! RsdSaPrg Hdr Err !!!` (`0x43ce55fa`), `DbgPrt CmdRcv` (`0x43ce564c`) → SAD
**recibe y valida programas del motor de imagen** (SA) con cabecera: hay tres clases de programa
(`Cdc…`, `Nml…`, `Rsd…`) y un contador de recepción de comandos.

### 2.7 `[PNL]` — panel/display (41 trazas) — VERIFICADO

`Backup_read() error %d` (`0x43c76138`), `Backup_read() b_id %08X` (`0x43c76155`),
`cmd_set_conf_dev = %d` (`0x43c76185`), `cmd_set_conf_rev = %d` (`0x43c761a1`),
`cmd_set_conf_cb_NULL` (`0x43c761bd`), `cmd_set_conf_id = %d` (`0x43c761d8`) → el **panel** se
configura por **callbacks** (dev/rev/cb) y su configuración se **guarda y restaura** (backup) con
identificadores. Enlaza con el protocolo de ajuste del display `ADJ_CMD` (S73).

### 2.8 `[AUGI]` — bloque de datos con cabecera (75 trazas) — VERIFICADO

`[PRINT] size[%d] %s` (`0x43c6a28a`) y el volcado de campos de cabecera
(`0x43cd9968`–`0x43cd99f4`): `length`, `Reserved2`, `end_flag`, `PS_flag`, `EP_flag` → es el **formato
de bloque que consume el encoder de vídeo** (§2.4) y el propio motor de imagen. Ojo: el
token `[AUGI]` aparece 75 veces en el binario, pero solo **26** cadenas empiezan por el prefijo
(las demás lo llevan incrustado).

### 2.9 `[WSX]` — búsqueda en fichero (59 trazas) — VERIFICADO

`BSFS INIT: TG: %x` (`0x43ce41bd`), `BSFS CLOSE: MEMMAN FREE err: %ld` (`0x43ce41d6`), `BSFS SEARCH
LOOP ERROR` (`0x43ce41fe`), `BSFS CLOSING ERR` / `BSFS CLOSING EXIT` (`0x43ce421d`/`0x43ce4236`),
`BsfsWSXClear Err` (`0x43ce4250`) → WSX usa un servicio **"BSFS"** (búsqueda en fichero) con
asignación de memoria; queda abierto qué fichero/índice recorre (NO_VERIFICADO).

## 3. Abierto (NO_VERIFICADO)

- Significado de las siglas BSFS, AUGI, SAD, WSX, ENCOUCSTAT.
- Qué son exactamente los programas `Cdc…`, `Nml…`, `Rsd…` del SA (§2.6).
- Los 4 sub-valores de `CapMode` y su relación con los 69 modos de captura de S66.
- La tabla "O/U Crank" completa (frame rates y sampling rates).
- Formato exacto de la cabecera AUGI (más allá de los campos imprimidos).
- Módulos aún sin decodificar: `IDT`, `VDF`, `VEF`, `CLK_CTRL`, `SFRS`/`SFRA`, `GOLFSHOT`, `AUGI`
  (resto), `SAN`, `GS`, `CH_SRC`, `AFNR` (dentro de ADF).

## 4. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s83_modules.py -q
```
