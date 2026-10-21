# S69 — Subsistema de audio de la Sony A6000 (fw3.21)

**Hito:** línea de ingeniería inversa **general** de la cámara: el subsistema de audio del
`av-cam.bin` (micrófono, niveles de grabación, reducción de ruido de viento/voz, códecs y enlace con
la captura de vídeo). **Independiente** de la línea SilentShutter y de la línea de montura de lente
(S66). Sin cambios en S51 (fin electrónico NO VERIFICADO; A/B/C = NO).

**Método:** análisis estático de bytes del `av-cam.bin` de A6000 (fw3.21) y comparación con A7S
(fw3.20). Capstone sobre bytes; **ningún firmware ejecutado, ninguna cámara tocada**.

**Pruebas:** `tests/test_s69_audio.py` (9 tests) · Informe detallado: `analysis/s69_audio/audio_subsystem.md`
· Tabla estructurada: `analysis/s69_audio/audio_subsystem.json`.

---

## 1. Resumen de hallazgos (VERIFICADO)

1. **El audio es un "IP" (Image Processing) más del driver de sensor**: `AUDIOIP INIT COMP`
   (`0x43c26411`) arranca el bloque de audio desde el subsensor (`AdfSenserCtrl`), con
   configuraciones de **VGS / PR / MF / CONS / BANDI**.
2. **Micrófono**: `AdfSenserCtrl::SetParamSetMicMode` (`0x43c26dc1`), `Abb::SetMicConfig`
   (`0x43cddad4`) y `AbbMicSensAdjustCtrl::SetStatus` (`0x43cddd49`).
3. **Niveles de grabación**: `AdfSenserCtrl::SetParamSetRecLevel` / `…RecMode`
   (`0x43c26df4` / `0x43c26e91`), `15AbbRecLevelCtrl` (`0x43cdddf3`) y
   `RecLevel SetRecLevel` (`0x43929fa4`, log `[RecLevel]SetRecLevel [volume]` en `0x43cde0d3`).
4. **Reducción de ruido**: hay un bloque propio de WNR ("wind noise reduction") y cancelación de voz
   (`WindStage:%d, MagDataRsv:%d` en `0x43cddea7`, `MAGIC SetNwnr`, `New WNR ON/OFF`,
   `PremiumCloserVoice`, `MyvoiceCanceling`, `iVoice` en `0x43cddeec`–`0x43cddf9a`).
5. **Códecs**: la app conoce `AUDIO_CODEC_TYPE_XAVCS_LPCM` (`0x43c6909d`),
   `AUDIO_CODEC_TYPE_MP4_LPCM` (`0x43c690c8`) y `AUDIO_CODEC_TYPE_AAC` (`0x43c690f1`).
6. **Diagnóstico**: `targetAudioFormat` (`0x43c5c68e`), `audioChannelNum` (`0x43c5c6b1`),
   `audioMuteRec` (`0x43c5ca62`).
7. **Enlace con el vídeo**: `ProcBuffMgrWrAudioPin` (`0x43c28d29`) y los escenarios
   `AVBB_SCN_START/STOP_AUDIO` del `CmnRecUtil`.
8. **Sonido y backup**: interfaz `9AudioIpIf` (`0x43cdd82e`), `SaDriverBase` (`0x43cde8f1`),
   `Sa SaChangeBackup` (`0x43cddfbc`).
9. **A6000 vs A7S**: el resto del audio es prácticamente idéntico (235 vs 237 cadenas clave), pero la
   **A7S tiene un subsistema de códec externo** (`15AbbExtCodecCtrl` en `0x43cd582e`,
   `ConvChSsau2AudioIpCh` en `0x43c2f48a`) que **la A6000 (fw3.21) no tiene**.

## 2. frontier (NO_VERIFICADO)

- Frecuencia de muestreo, profundidad de bits, tamaño de trama y número de canales concretos.
- "Reduce voltage" del micrófono (cadena presente, sin localizar el camino eléctrico).
- Muxer exacto del audio en el contenedor de vídeo.
- Coeficientes del DSP de WNR/supresión de voz.
- Ganancia y calibración del micrófono.
- La semántica de `VGS / PR / MF / CONS / BANDI` (configuración del bloque de audio).

## 3. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s69_audio.py -q
```

Referencias internas: `analysis/s69_audio/audio_subsystem.md` (informe), `.json` (tabla).
