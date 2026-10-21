# S75 — ZPD (Zone Plate Detection): calibración del sensor con datos de la lente

**Alcance:** línea de ingeniería inversa **general** de la cámara: el subsistema **ZPD** del
`av-cam.bin` de A6000 (fw3.21) — la calibración del sensor (defectos/microlens) a partir de datos
que viven **en la lente** y en el cuerpo. No es la línea SilentShutter, ni la trama de la montura
(S66), ni el AF (`analysis/s63_af/` de otro agente), ni el protocolo ADJ_CMD (`analysis/s73_adj/`).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s75_zpd.py`.

---

## 1. Namespaces y clases (VERIFICADO por los nombres de clase del blob)

El binario incluye los nombres RTTI/mangled de las clases:

| Clase | Dirección del nombre |
|---|---|
| `N6Camera3ZPD14MemFileLoadObjE` | `0x43ccf318` |
| `N6Camera3ZPD7MemObjTINS0_7Control14MemoryResource10SusResInfoEEE` | `0x43ccf336` |
| `N6Camera3ZPD6ITraceE` | `0x43ccf377` |
| `N6Camera3ZPD7Control13SyncSequencerE` | `0x43ccf38c` |
| `N6Camera3ZPD6MemObjE` | `0x43ccf3b1` |
| `N6Camera3ZPD13MemUnitBackupE` | `0x43ccf3c6` |
| `N6Camera3ZPD7MemUnitE` | `0x43ccf3e3` |
| `N6Camera3ZPD4Lens18LensInterpretChunkE` | `0x43ccf3f9` |
| `N6Camera3ZPD4Lens20LensInterpretChunkEdE` | `0x43ccf420` |
| `N6Camera3ZPD7Control14AsyncSequencerE` | `0x43cd1b51` |
| `N6Camera3ZPD7Control6DetectE` | `0x43cd1b77` |
| `N6Camera3ZPD7Control13SequencerBaseE` | `0x43cd1bf4` |
| `N6Camera3ZPD7Control10WorkerBaseE` | `0x43cd1c19` |
| `N6Camera3ZPD7Control9SequencerE` | `0x43cd1c3b` |

Estructura: `Camera::ZPD` tiene **memoria** (`MemObj`, `MemUnit`, `MemUnitBackup`, `MemFileLoadObj`),
**control** (`Control::Detect`, `Control::WorkerBase`, `Control::SequencerBase` → `SyncSequencer` /
`AsyncSequencer` / `Sequencer`) y un **sub-objeto de lente** (`ZPD::Lens::LensInterpretChunk` y
`…ChunkEd`): el "chunk" de interpretación de la lente es la unidad de datos que ZPD obtiene de ella.

## 2. De dónde salen los datos (VERIFICADO)

| Log | Dirección | Función |
|---|---|---|
| `[ZPD]: lens attach sequence end.` | `0x43ccf27f` | `0x43904ab4` |
| `[ZPD]: load dra data.` | `0x43ccf2a0` | `0x43904be8` |
| `[ZPD]: load lens data from lens.` | `0x43ccf2c7` | `0x43904c90` |
| `[ZPD]: load lens data from body.` | `0x43ccf2e8` | `0x43904cfc` |
| `[ZPD]: load:%s` | `0x43ccf309` | `0x43904cfc` |
| `/setting/psd.bin` (fichero de datos del cuerpo) | `0x43ccf33f` (junto a los anteriores) | — |

Tres orígenes distintos: **la lente** (datos de calibración almacenados en ella), **el cuerpo**
(fichero **`/setting/psd.bin`**, cadena inmediatamente posterior a los logs ZPD) y **"dra data"**
(otro conjunto de datos del sistema). INFERENCIA: la cámara recalibra
el sensor con los datos que trae la lente, y guarda una copia en el cuerpo.

## 3. Consumo en el DFE/sensor (VERIFICADO)

- **Factor de interrupción del DFE** por canal ZPD: `[DFECore]: [Err][SetZPD0IntFactor] …`
  (`0x43c91781`), `ClearZPD0IntFactor` (`0x43c917f8`), `SetZPD1IntFactor` (`0x43c91875`),
  `ClearZPD1IntFactor` (`0x43c918ec`): el DFE tiene **dos canales de interrupción** (ZPD0, ZPD1)
  con factor configurable.
- **Carga de posiciones de defecto en la SRAM del sensor**:
  `[DFECore]: ImgDdcSetter::loadDefectPos ZPD_SRAM shortage bank:%d addr:%x %x[byte]`
  (`0x43cf75ee`, ref `0x43a0f5c4`): las posiciones de defecto calculadas se escriben en la
  **SRAM del sensor** (DDC = defect data correction).
- **Interrupciones y registros APB** (trazas del lado DFE/SoC):
  `Detected IRQ : ZPD CH1` (`0x43fa9798`), `CPU IRQ : ZPD0` (`0x43fa9a4c`), `CPU IRQ : ZPD1`
  (`0x43fa9a60`), `CPU APB : ZPD_APB0/1 Value write (Min addr)` / `(Max addr)`
  (`0x43fa9f24`–`0x43faa1ac`) y `CPU AIF : ZPD W-ch0 / R-ch1 / W-ch2 / R-ch2 Start/Done`
  (`0x43faabb0`–`0x43faac88`): el bloque ZPD tiene **2 canales con 2 subcanales** y se programa
  por un bus APB con direcciones mínima/máxima.

## 4. Coordinación con la montura y con el AF (VERIFICADO)

- **Con el bus de la lente (S66)**: `[MOUNT_DEBUG]: [BL]ZPD change EclipseDataComState from
  STANDBY to START` (`0x43c976b5`, ref `0x436e3f18`). Además, el volcado de estado del protocolo de
  montura incluye el campo **`LC T.O. Cnt`** (`0x43c96c1e`, dentro de `BL Info`): es decir, el
  protocolo "BL" lleva **contador de timeout del canal LC** (LC = calibración de lente), lo que
  confirma que ZPD/LC es un servicio **dentro** del subsistema de montura.
- **Con el AF híbrido**: `[CAMERA_MAIN]: NOT_DETECT from ZPD MODULE in spite of ZpdPreEnable.
  lc_HybridAF.cpp` (`0x43c9d07e`, ref `0x43754be0`), `[CAMERA_MAIN]: time is zero
  Main/LC/ZPD/zpd_mario_afa.cpp` (`0x43c9db6a`, ref `0x43779bd4`), `[CAMERA_MAIN]: stabilize num
  error zpd_mario_afa.cpp line %d` (`0x43c9d9f4`, ref `0x43779924`), `[CAMERA_MAIN_LC]:
  LC_GetZpdResultInfo:Error` (`0x43ca78b6`) y `[CAMERA_MAIN_LC]: area[60].zpd_flags=%d,
  area[60].defocus=%d` (`0x43ca777c`).

INFERENCIA: en el AF **híbrido** (pixel-shift / DM AF) la cámara usa los datos ZPD como
**resultado de la medición** (`zpd_flags`, `defocus`, `stabilize num`), es decir, ZPD es el sensor
de medición *en el propio sensor* (DM = digital monitor) que complement al AF del objetivo.

## 4.bis Enlace con los ficheros de lente (S66) — INFERENCIA fuerte

Las secciones del fichero `/lens/VX91xx_lensfile.bin` (S66) son `ED` (tabla grande de u16),
`CS` (lista ordenada de u16) y **`LC` (12 B = 6 u16)**. Contenido de `LC` (verificado):

| fichero | LC (6 u16) |
|---|---|
| VX9101 | `0000 0260 0450 03b0 0d78 0000` |
| VX9102 | `0000 0360 0620 0461 0d49 0000` |
| VX9129 | `0001 02f0 0570 03a4 0d99 0000` |

Los valores **cambian por lente** (6 parámetros numéricos del orden de 10²–10³) → INFERENCIA
fuerte: `LC` = **datos de calibración de la lente** (el "chunk" que ZPD interpreta: coherente con
`ZPD::Lens::LensInterpretChunk` y con el canal `LC` del protocolo de montura, S66 §"LC T.O. Cnt").
No está probado que el ZPD de la A6000 lea *estos* ficheros (el log dice "load lens data **from
lens**", es decir, del propio objetivo por el bus, no del fichero del cuerpo).

## 5. Abierto (NO_VERIFICADO)

- Formato del "chunk" de lente (`LensInterpretChunk` / `…ChunkEd`): tamaño, campos, y si es el
  mismo tipo de bloque que el de `/lens/VX91xx_lensfile.bin` (S66) o uno distinto.
- Qué es exactamente "dra data".
- Cómo se calculan las posiciones de defecto (`loadDefectPos`) y de dónde sale el mapa.
- La relación entre `ZPD0`/`ZPD1` y los canales W-ch0/R-ch1/W-ch2/R-ch2 (2 canales × 2 subcanales).
- Si la A7S (fw3.20) tiene el mismo subsistema y con la misma estructura → **RESUELTO por
  comparación (21-10-2026)**: la A7S **no** tiene el namespace de aplicación `Camera::ZPD`
  (0 hits de `N6Camera3ZPD`), pero **sí** tiene los factores de interrupción ZPD en el DFE
  (`[Err][SetZPD0IntFactor] wrong int bit %08X` en `0x43c9a689`, `ClearZPD1IntFactor` en
  `0x43c9a7b2`, sin el prefijo `[DFECore]:`) y **no** tiene los logs `[ZPD]: …` de origen de datos
  (0 hits). Es decir: el soporte ZPD en el **DFE** ya existía en la fw3.20 y la fw3.21 (A6000) añade
  la **capa de aplicación** que carga el "chunk" de calibración desde la lente.

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s75_zpd.py -q
```
