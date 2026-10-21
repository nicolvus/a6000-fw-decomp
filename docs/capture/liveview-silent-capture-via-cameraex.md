# Foto desde Live View / vídeo: qué se puede aplicar por telnet/adb (2026-10-20)

Base estática previa (no repetida aquí): [electronic-still-low-resolution.md](electronic-still-low-resolution.md), [imx210-video-readout.md](imx210-video-readout.md), [liveview-encodestill-parallel-verdict.md](liveview-encodestill-parallel-verdict.md). Resumen: Live View de foto usa los modos IMX210 `0x01` (2000×570) / `0x03` (2000×800) / `0x0F`, vídeo usa `0x1A/0x10/0x19/0x07`; un frame de lectura continua no mueve cortinillas. NO hay en el firmware (hasta ahora) una ruta documentada «frame de LV → JPEG» desde el disparo normal.

## Hallazgo nuevo: API `CameraSequence` en el framework de la cámara (VERIFICADO: clases y firmas del odex)

`sony.cameraex.odex` (extraído de la cámara, `analysis/camera-dumps/live-android-20261020/`, no versionado) contiene `com.sony.scalar.hardware.CameraSequence` con:

- `open(CameraEx)`, `startPreviewSequence(Options)`, `updatePreviewSequence`, `stopPreviewSequence`, `getPreviewSequenceFrames(int)` → `DeviceMemory[]`, `getPreviewSequenceFrameInfo()`.
- `Options`: `PREVIEW_FRAME_WIDTH/HEIGHT/FORMAT/RATE/MAX_NUM`, `PREVIEW_FRAME_INFO_VERSION`, `JPEG_COMPRESS_*`, `RECORD_COUNT`, `EXPOSURE_COUNT`, `MEMORY_MAP_FILE`, `PREVIEW_PLUGIN_*`.
- Almacenar: `storeImage(OptimizedImage, boolean[, boolean])`, `storeImage(RawData, boolean[, boolean])`; `setShutterSequenceCallback` (`onShutterSequence`, `RawData`, `getRawDataInfo`), `setRawFileStoreEnabled`.
- Procesado en dispositivo: `DSP` (`createImage`, `setProgram`, `execute`), `OptimizedImage(w,h,fmt)`, filtros (`ScaleImageFilter`, `SuperResolutionImageFilter`, …).
- Además `com.sony.scalar.media.MediaRecorder` (vídeo) y `CameraEx$PreviewStartListener`, `ShutterListener`.

Es la interfaz que usan las aplicaciones de PlayMemories para disparo en ráfaga / varias exposiciones a partir de frames de preview: **captura electrónica por construcción** (los frames salen del flujo de Live View), sin ciclo de cortinillas. NO VERIFICADO: que `storeImage` de un frame de preview genere un JPEG en la tarjeta en esta cámara, ni su resolución (el preview es ≈2 MP).

## Qué se puede aplicar vía telnet/adb

| Vía | Cómo | Estado |
|---|---|---|
| A. App con `CameraSequence` (preview frames → `storeImage` o volcado) | Ampliar `tools/remote-shutter/` (reflexión, como ya se hace con `CameraEx.open`); instalar por adb, abrir desde la lista de aplicaciones, disparo por HTTP | NO probada |
| B. `Camera.setPreviewCallback` / `CameraEx` con preview | Ya falló el overlay (`Overlay Creation Failed`) con la app en segundo plano; puede funcionar si la app tiene la cámara en primer plano | NO probada |
| C. `MediaRecorder` (vídeo) y extraer un frame en el PC | Totalmente silencioso, resolución de vídeo (FHD) | NO probada |
| D. Escribir RAM (ya hecho): Silent, copias, drive_mode, EFCS | Sin efecto sobre el obturador (ver [s64](s64-silent-ram-nvram-test.md)); solo `+0x210`=1 dio un sonido de «disparo múltiple» | VERIFICADO (oído) |

Ventaja de A/B/C: el criterio es objetivo para el oído: **sin ningún clic** = no hay obturador mecánico; no depende de decidir qué sonido es EFCS.

## Límites
- Resolución: preview/vídeo ≈ 2 MP (no 24 MP). La foto a 24 MP electrónica sigue NO demostrada (S51 en NO).
- `CameraSequence`/`DSP` pueden requerir permisos o firma de plataforma; no se ha comprobado que una app instalada por adb (usuario `shell`) pueda abrirlas.
- Nada se ha ejecutado aún: esto es el plan y el inventario de API.
