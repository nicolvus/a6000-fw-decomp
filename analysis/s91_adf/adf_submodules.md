# S91 — Los submódulos del framework ADF: ADJ, SYSND, GS, FACE, AFNR y CH_SRC

**Alcance:** línea de ingeniería inversa **general** de la cámara: los submódulos del framework **ADF**
(S81) que quedaban sin decodificar, con sus enlaces al subsistema de audio (S69), a la detección de
caras (S71) y al visor (S86). No es la línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD
(S73), ni ZPD (S75), ni ZIT (S80), ni el API del motor de imagen (S84), ni el wireless (S72).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s91_adf_submods.py`.

---

## 1. `[ADF][ADJ]` — el ajuste del sensor de audio (24 trazas) — VERIFICADO

Todas son `AdfSenserCtrl::SetParamSet<algo> err %x`:

| parámetro | dirección |
|---|---|
| `SetParamSetMicMode` | `0x43c26dc1` |
| `SetParamSetRecLevel` | `0x43c26df4` |
| `SetParamSetChSource` | `0x43c26e28` |
| `SetParamSetInputType` | `0x43c26e5c` |
| `SetParamSetRecLevelMode` | `0x43c26e91` |
| `SetParamSetHpMonitor` | `0x43c26ec9` |
| `SetParamSetInputTrim` | `0x43c26efe` |
| `SetParamSetLowCut` | `0x43c26f33` |

**Enlace con S69 (audio) y S81 (ADF):** son exactamente los mismos parámetros que los comandos de
depuración `[ADF][DBGCMD] InputPro Set*` (`SetIntMicSens`, `SetInputType`, `SetInputTrim`,
`SetChSource`, `SetRecLevelMode`, `SetAgcLink`, `SetManualGainLink`, `SetRecLevelLimitter`,
S81) → el bloque `ADJ` es la **implementación** de esos comandos sobre el *sensor de audio*
(`AdfSenserCtrl`), es decir, el punto donde el audio del micro/teléfono se configura en la cámara.

## 2. `[ADF][SYSND]` — el sonido del sistema (27 trazas) — VERIFICADO

`[ADF][SYSND] PS ON` (`0x43c278f0`), `SET PATH SendComp Err %x` (`0x43c27904`),
`INIT m_dummySetOutputSysndDelay %x` (`0x43c27941`), `REQ INIT ERR m_dummySetOutputSysndDelay`
(`0x43c27970`), `INIT m_StartTransDelay60 %x` (`0x43c279a4`), `INIT m_StartTransDelay50 %x`
(`0x43c279f9`).

→ el "system sound" (pitido del obturador, sonidos de la interfaz) tiene una **compensación de
retardo** con dos valores, **60 y 50 Hz** → son las frecuencias de las redes de TV PAL/NTSC, es decir
el retardo del pitido se ajusta al estándar de TV de la región (mismo eje que el `DOWNCON` PAL/NTSC
del visor, S86). INFERENCIA: el pitido debe coincidir con el diagnóstico de TV cuando la cámara
actúa como fuente de vídeo.

## 3. `[ADF][GS]` — el "path" de un proceso (2 trazas) — VERIFICADO

`[ADF][GS]START PROC PATH ERR ` (`0x43c327d3`) y `[ADF][GS]START STATE ERR state : %x`
(`0x43c327f2`): un "path" (ruta de procesamiento) arranca con una máquina de estados; el mismo
vocabulario (`SET PATH`, `START PROC PATH`) aparece en `SYSND` y en los módulos de audio.

## 4. `[ADF][FACE]` — la coordinación con la detección de caras (2 trazas) — VERIFICADO

`[ADF][FACE]StartExecFace` (`0x43c32a3b`) y `[ADF][FACE]StopExecFace` (`0x43c32a54`).

→ el **framework ADF** es quien **arranca y detiene la detección de caras** (S71): el subsistema FC
no se arranca solo, lo dispara el ADF. Es el puente explícito entre ambos hitos.

## 5. `[ADF][AFNR]` — reducción de ruido del AF (2 trazas) — VERIFICADO

`[ADF][AFNR]StartExecAfnr:%x` (`0x43c32990`) y `[ADF][AFNR]StopExecAfnr` (`0x43c329ac`) → el ADF
gestiona un proceso de **reducción de ruido para el AF** (AFNR = *AF Noise Reduction*), con un
parámetro de modo (`%x`).

## 6. `[ADF][CH_SRC]` — el micrófono AVIO (1 traza) — VERIFICADO

`[ADF][CH_SRC] AvioMicStateStart fifoErr %x` (`0x43c2e99a`) → el **micrófono AVIO** (el micrófono
integrado, cf. `[ADF][INIT]AVIO INIT COMP` de S81) arranca con un FIFO.

## 7. Abierto (NO_VERIFICADO)

- Qué es exactamente el subsistema "GS" (¿*Game Sound*? ¿*Group State*?) y qué paths gestiona.
- El parámetro de modo de `AFNR` y qué algoritmo aplica.
- La tabla completa de los 24 mensajes de `ADJ` (aquí 8 de muestra) y su equivalencia completa con
  los `InputPro Set*` de S81.
- La relación exacta entre los retardos 60/50 Hz y el estándar de TV en uso.

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s91_adf_submods.py -q
```
