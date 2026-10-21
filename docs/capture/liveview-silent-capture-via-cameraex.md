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

## Prueba en cámara de `CameraSequence` (2026-10-20) — resultado

- `tools/remote-shutter/` ampliado con `GET /seq?w=&h=&f=&n=&p=&t=` (reflexión sobre `CameraSequence`); `scripts/camera_install_apk.py` instala por ADB.
- VERIFICADO: `CameraSequence.open(cameraEx)` y `startPreviewSequence(Options)` aceptan la llamada desde una app instalada por adb (`open-ok`, `preview-ok` con `startPreview()` sin pantalla, `start-ok`); `getPreviewSequenceFrameInfo().detailData` devuelve 4096 B (cabecera `02008000 0800 1803 …`, significado NO VERIFICADO).
- `getPreviewSequenceFrames(0..2)` devolvió **null** (4 s tras el inicio, sin disparo): no se obtuvieron frames. Registrar `setShutterSequenceCallback` (1 y 2 argumentos, con `RECORD_COUNT=1`, `EXPOSURE_COUNT=1`, también tras parar la secuencia) falló con `RuntimeException: setShutterSequenceCallbackMode failed`. Sin frames, sin foto: la vía A no se logró.
- **Incidente:** al instalar y abrir la última versión (callback registrado antes de arrancar el preview), la cámara se colgó; tras reinicio duro **no arranca con el objetivo puesto** (el objetivo «queda abierto»); conectada por USB arranca en modo MTP y se pudo reactivar ADB/telnet. En ese arranque: sin proceso `av-cam`, logcat sin excepciones de `ar.shutter` ni cierres forzados, `dropbox` solo `SYSTEM_BOOT`; `dmesg` solo ruido wifi. Espejo de ajustes en RAM sin valores forzados (Silent=0, `+0x210`=0; otras 19 palabras difieren del inicio por ser otro modo de arranque). **Causa NO VERIFICADO**; no hay evidencia de que haya persistido nada en NVRAM/flash, pero tampoco se pudo descartar (el volcado de backup por USB service mode no estaba disponible). `ar.shutter` desinstalada por ADB al final.
- Lección: `CameraSequence` toca el pipeline de captura de la cámara (no es solo RAM del espejo); no se repite sin un plan de recuperación.

## Recuperación tras el incidente (2026-10-20)

- Reflasheo 3.21: `scripts/camera_reflash_fw321.sh` (`pmca-console firmware`) → `Firmware update error: Invalid version` en `checkGuard` (misma versión rechazada); no se escribió nada.
- Volcado de solo lectura en service mode (`post-incidente-20261020-213936`, no versionado): ~1 070 B distintos (145 regiones) respecto a `silent-nvram-20261020/1-base_*` (18:48); causa de cada cambio NO VERIFICADO.
- Restauración a petición del usuario: `scripts/senser_backup_restore.py silent-nvram-20261020/1-base_flash.bin db9e7324…` (`setBackupPresetData(2, …)` + `saveBackup(0)`): verificación en memoria OK (bytes `0x100..` idénticos; la cabecera de 0x100 B no cambia con esta escritura), sincronizado a flash. La cámara salió de service mode al terminar y no se pudo re-volcar para verificar la flash. Efecto sobre el obturador: NO VERIFICADO.
