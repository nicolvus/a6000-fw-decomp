# G52 — Post Focus (DESCARTADO tal cual; variantes derivadas)

Fecha 15-11-2026. Solo estático (strings de `av-cam.bin` 3.21, libs del rootfs, manual de servicio); sin cámara, sin parche, sin CFW.

## 1. Sin pantalla táctil
- `docs/references/sony-ilce-6000-level3-sm.txt`: 0 coincidencias de «touch panel/touchpanel/touch screen»; las únicas «TACTILE» son `SWITCH, TACTILE` (S0018–S0025, pulsadores de botones).
- Firmware `av-cam.bin`: las cadenas «Touch» (35) son del módulo de detección de caras (`faceTouch`, `CamTouchParam`, `vtime_Touchfirst`, `WAIT_Touch`): «touch» = punto/cara seleccionado por software, no panel. No hay `TouchOperation` ni controlador táctil.
- Consecuencia: el elegir en reproducción «toca un punto» no tiene entrada; solo sería posible con cursor de cruceta (reduciría el UI, no es límite duro).

## 2. Control de enfoque durante grabación
- No hay comando de lente de posición/paso reutilizable localizado: `av-cam.bin` solo expone `FocusPos*` como parámetro informativo del DSP (`job_YC_*`, `focusPositionNumerator/Denominator/Valid` en camInfo/recInfo, `VdfSrvcCmdSetFocusLockFrameInfo` que graba la posición en el fotograma) y `agus_debug_dmaf_fc_pos_set` (depuración).
- Rootfs: `libScalarDaemon.so` / `libcameraex_jni.so` solo tienen `startOneShotFocusDrive` (disparo de AF de un golpe, no posición); `viewUnified2.so` tiene `cmnViewSettingNodeRootMFAssist` (nodo de menú MF Assist, no un paso).
- Lectura: el movimiento de lente lo hace el bucle AF/MF (otro módulo, no localizado en esta búsqueda breve). No se descarta un comando absoluto/relativo en el protocolo de lente; queda como pendiente para Focus Shift Shooting. Una búsqueda vacía no prueba ausencia.

## 3. Veredicto
Post Focus tal cual: **descartado**. Motivos: (1) depende de 4K/6K Photo, ya descartado ([g50](g50-4k-6k-photo.md): sin modo de lectura ≥3840 ni codificador suficiente); (2) sin pantalla táctil.
- Variante (a), barrido en vídeo FHD 1996×1124@60 con extracción de fotograma en reproducción: se cierra dentro de `G50-FHDPHOTO` (nota añadida).
- Variante (b), barrido como ráfaga a resolución completa: es Focus Bracketing, derivada al objetivo «Focus Shift Shooting / Focus Stacking» (pendiente `FOCUSSHIFT-LENS`).
