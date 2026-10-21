# S69 — Subsistema de audio de la Sony A6000 (fw3.21)

Línea de ingeniería inversa GENERAL (no SilentShutter). Solo lectura de bytes; no se ejecutó firmware.
Entregables: `audio_subsystem.json`, `tests/test_s69_audio.py`.

## 1. Inventario del subsistema de audio en av-cam.bin

El subsistema de audio vive en dos grandes regiones de cadenas dentro de `av-cam.bin`:

- `0x43c26411`–`0x43c28e...` (ADF: Audio IP, senser ctrl, rec level, mic mode, mute, volume, wind NR).
- `0x43cdd14f`–`0x43cdf0f5` (AudioIp/Abb: backup, mic sens adjust, rec level, WindStage, MAGIC settings, SA driver).
- `0x43c5c419`–`0x43c6039c` (audio es buffer / channel num / mute rec / target format).
- `0x43c6909d`–`0x43c690f1` (codecs de audio en contenedor de vídeo).

Subsistemas auxiliares: Sound Analyzer (`0x43ce2ad9`–`0x43ce30ef`), NS scalar infra (`0x43ce561f`–`0x43cec98b`), AvcDec/Enc audio (`0x43cd1d6e`, `0x43cdaa43`).

Cadenas clave (VERIFICADO, direcciones exactas):

- `[ADF][INIT]AUDIOIP INIT COMP` @ `0x43c26411` (función `0x4356725c`).
- `[ADF][ADJ]AdfSenserCtrl::SetParamSetMicMode err %x` @ `0x43c26dc1`.
- `[ADF][ADJ]AdfSenserCtrl::SetParamSetRecLevel err %x` @ `0x43c26df4`.
- `[ADF][ADJ]AdfSenserCtrl::SetParamSetRecLevelMode err %x` @ `0x43c26e91`.
- `[ADF]AUDIO_IP_CONFIG_TYPE_VGS/PR/MF/CONS/BANDI` @ `0x43c264fa...`.
- `Abb::SetMicConfig Err mode %x` @ `0x43cddad4`.
- `AbbMicSensAdjustCtrl::SetStatus %x` @ `0x43cddd49`.
- `15AbbRecLevelCtrl` @ `0x43cdddf3`.
- `WindStage:%d, MagDataRsv:%d` @ `0x43cddea7` (función `0x43929db4`).
- `MAGIC SetNwnr` / `New WNR ON` / `New WNR OFF` @ `0x43cddec4`/`0x43cdDED3`/`0x43cdDEDf`.
- `MAGIC SetPremiumCloserVoice` / `ON` / `OFF` @ `0x43cddeec`/`0x43cddf09`/`0x43cddf20`.
- `MAGIC SetMyvoiceCanceling` / `ON` / `OFF` @ `0x43cddf38`/`0x43cddf53`/`0x43cddf68`.
- `MAGIC SetiVoice` / `ON` / `OFF` @ `0x43cddf7e`/`0x43cddf8f`/`0x43cddf9a`.
- `RecLevel SetRecLevel` @ `0x43cddfA6` (función `0x43929fa4`).
- `[RecLevel]SetRecLevel [volume]` @ `0x43cde0d3`.
- `audioChannelNum = %#x`, `targetAudioFormat = %#x`, `audioMuteRec = %#x` @ `0x43c5c6b1`/`0x43c5c68e`/`0x43c5ca62`.

## 2. Modelo de datos del audio

VERIFICADO:
- Codecs de audio en contenedor de vídeo: `AUDIO_CODEC_TYPE_XAVCS_LPCM` (`0x43c6909d`), `AUDIO_CODEC_TYPE_MP4_LPCM` (`0x43c690c8`), `AUDIO_CODEC_TYPE_AAC` (`0x43c690f1`), en código `ExCodecDecMp4`.
- Campos de depuración: `targetAudioFormat`, `audioChannelNum`, `audioMuteRec`.

NO VERIFICADO:
- Frecuencia de muestreo, profundidad de bits, tamaño de trama y número concreto de canales no aparecen como cadenas en `av-cam.bin`.
- Muxer exacto de audio en el contenedor de vídeo no localizado estáticamente.

## 3. Micrófono interno/externo

VERIFICADO:
- Configuración de modo de micro: `AdfSenserCtrl::SetParamSetMicMode` (`0x43c26dc1`), `Abb::SetMicConfig` (`0x43cddad4`).
- Ajuste de sensibilidad: `AbbMicSensAdjustCtrl::SetStatus` (`0x43cddd49`).
- No se encontró cadena "reduce voltage" asociada al micrófono en `av-cam.bin` (solo `E-MountLens ReduceVoltage`).

NO VERIFICADO:
- Ganancia analógica/digital concreta, calibración y selección interno/externo no localizadas como cadenas.

## 4. Reducción de ruido de viento y de voz

VERIFICADO:
- WNR: `MAGIC SetNwnr`, `New WNR ON/OFF`, `WindStage:%d, MagDataRsv:%d` (`0x43cddec4`–`0x43cddea7`).
- Cancelación de voz: `PremiumCloserVoice ON/OFF`, `MyvoiceCanceling ON/OFF`, `iVoice ON/OFF` (`0x43cddeec`–`0x43cddf9a`).
- Sound Analyzer: `SaDriverBase` (`0x43cde8f1`), `SA OpenConfigCb Ack` (`0x43cdd844`), `Sa SaChangeBackup` (`0x43cddfbc`).
- NS scalar infra: `N15NS_SCALAR_INFRA*` en `0x43ce561f`–`0x43cec98b`.

NO VERIFICADO:
- Algoritmo DSP concreto y parámetros (coeficientes) no recuperados.
- Interfaz app↔audio: `WrapperAudioRecordingLevel` (userland) identificada por símbolos (`getAudioRecordingLevel`, `setAudioRecordingLevel`, `isInhOn`, `convertValueToProcessValueId`).

## 5. Enlace con la captura de vídeo

VERIFICADO:
- Audio procesado en flujo de movie: `ProcBuffMgrWrAudioPin` (`0x43c28d29`), `ExCodecDecMp4` con codecs LPCM/AAC.
- `CmnRecUtil` (`recUtil.so`/`movieRecUtil.so`) gestiona `isMovieRecording`/`getMovieMedia`; escenarios `AVBB_SCN_START_AUDIO.so`/`AVBB_SCN_STOP_AUDIO.so`.

Antecedente (no reanalizado): `docs/capture/record-still-image-route.md`, `docs/capture/mpr-dcf-recording.md`.

## 6. Comparación A6000 (fw3.21) vs A7S (fw3.20)

VERIFICADO (nivel de cadenas):
- El subsistema de audio (RecLevel/Wind/Mic/AudioIp/Abb) es prácticamente idéntico: 235 vs 237 cadenas clave.
- A7S tiene subsistema de codec externo completo (`AbbExtCodecCtrl`, `ProcMsgSetExternalCodecMgr`, `ProcTimeKeeperExtCodec`, `ProcPinDecoderExtCodec`, etc.) que A6000 NO tiene (solo `SetExternalCodecState` minimal y `23ProcMsgSetExternalCodec`).
  - Ejemplos A7S-only: `15AbbExtCodecCtrl` @ `0x43cd582e`, `[ADF]ProcMsgSetExternalCodecMgr::ConvChSsau2AudioIpCh` @ `0x43c2f48a`.

## 7. Frontera

NO VERIFICADO / no encontrado:
- Frecuencia de muestreo, canales concretos, tamaño de trama, profundidad de bits.
- Cadena "reduce voltage" para micrófono.
- Muxer exacto de audio en contenedor de vídeo.
- Parámetros DSP (coeficientes WNR/NS).
- No se ejecutó firmware ni se flasheó cámara.