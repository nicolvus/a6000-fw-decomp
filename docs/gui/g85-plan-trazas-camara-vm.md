# G85 — Plan de trazas en cámara para completar la LIRO VM (17-11-2026)

Origen: petición del usuario («todo lo que hay que capturar en cámara para la VM de principio a fin», incluidos batería, SD, USB y HDMI). Pendiente: [TRAZA-VM](../PENDIENTES.md). Etiquetas: VERIFICADO (documentado en el repo), NO_VERIFICADO (por comprobar antes de usar). **Plan, aún sin ejecutar ninguna traza.**

## Canales (qué da cada uno)

| Canal | Cómo | Sirve para | Límite |
|---|---|---|---|
| **telnet** (OpenMemories Tweak, root, sin login, `192.168.1.29`) | `scripts/camera_telnet.py 'cmd1' 'cmd2'` | `dmesg`, `/proc`, `/sys`, `getevent`, leer ficheros, volcar `/proc/PID/maps` y `/proc/PID/mem` (NO_VERIFICADO) | Por Wi‑Fi: se puede enchufar USB/HDMI sin perder la sesión |
| **adb** | `adb logcat`, `adb shell`, `scripts/camera_pull.py`, `camera_push_file.py`; disparo remoto con app propia `CameraEx` | Registro de Android/`libObj`, disparo S1/S2 desde el PC, tomar ficheros | `/dev/input/event0` no vale para S1/S2; instalar APK escribe en `/data`. **No repetir `CameraSequence`** (dejó la cámara sin arrancar el 20‑10) |
| **service mode (senser)** | `scripts/senser_ram_dump.py OUTDIR [ini] [fin]`, `senser_shell_dump.py`, `senser_regions_dump.py` | Volcar RAM física (solo lectura) tras una acción | Instantánea, no traza; el anillo de consola ya se envuelve |
| **SWD** (RP2040 `debugprobe-zero`, OpenOCD 0.12, `cortex_a -ap-num 1 -dbgbase 0x80110000`; sonda aún soldada) | Guiones de [R47](../capture/e26-r47-primer-contacto-swd-lectura-ram.md); ejemplos con puntos de parada en `analysis/camera-dumps/20261105-bionz-swd-disparos` | Watchpoints/breakpoints hardware sobre direcciones de `av-cam`, lectura de RAM sin parar la CPU, arranque desde el reset | `halt` prolongado hace perder el APB‑AP (R47 §9); preferir leer sin parar y breakpoints que solo registran y reanudan |

## Trazas a hacer

**Bloque A — arranque de av-cam (desbloquea E2E-10/12/15).**
- **T1 Arranque completo en frío.** SWD desde el reset (halt al responder el DAP, luego reanudar) y leer el búfer de consola `0x83400000` cada ~1 s para que el anillo no se envuelva; telnet `dmesg` en paralelo. Registrar `CAMUSER ExcConf` (17 ids), `ExcBase DIADEM`, `DFECore DrvSGC0`, `CAMERA_MAIN_SYNC` y su orden con marca de tiempo. Hacer dos: arranque normal y con estado restaurado.
- **T2 Escritor de `0x43eb26c9` / `0x43eaeecd`.** SWD: watchpoint de escritura en ambas; breakpoints «solo registrar» en `0x439e2888` (init del driver), `0x4384fb7c`, `0x43729a76` (caso 22 de la tabla `tbh`) y `0x4372a0c6`. Anotar PC, `lr` y r0–r3 de cada golpe.
- **T3 Mensajes ObjCamera↔av-cam.** Breakpoints «solo registrar» en el envío/recepción de la cola `0x20002` (direcciones por REA) durante: encendido, S1, S2, `0x3003`, `0x3000`, `0x3024`. Salida con el mismo formato que `avcam.jsonl` para compararla con la VM.
- **T4 Montura de objetivo y módulos.** Con y sin objetivo: leer `[0x43ede338]`, `[0x43ede320]`, estados de módulo (`+0x5c`/`+0x1c`) y `0x43eaee84+0x49` por SWD, en reposo y 1 s después del encendido, cada 100 ms.

**Bloque B — imagen y sensor/ISP (E2E-4/5).**
- **T5 Escrituras MMIO del sensor IMX210 y del ISP por disparo** (`r5`, ShutMode, VTS): watchpoints sobre las ventanas MMIO; reutilizar `camera_imx210_timing.py` y `camera_r5_raw.py`. Disparo remoto por adb; repetir con mecánico, EFCS y Silent.
- **T6 Volcados tras el disparo por configuración** (PP, gamma S‑Log2/3, HLG 1–3, Color Chrome, LUT 3D, DRO Lv3/Lv5, ISO 51200, Extra Fine, Keystone, Live ND): SWD (lectura sin parar) o `senser_ram_dump.py` justo tras la toma; buscar los búferes ya conocidos (LUT `0x654` B, HLG 3×4122 B, curva de 2048 pt, mensaje de colorimetría, tablas de cuantización, rejilla 11×11).
- **T7 Pares ARW+JPG de la misma escena** con cada perfil, mismo disparo remoto.
- **T8 `/proc/PID/maps` de `libObj` y `av-cam`** (LIBOBJ-MAP) por telnet.

**Bloque C — periféricos (sin cobertura hoy).**
- **T9 Batería.** telnet: `cat /sys/class/power_supply/*/*`, `dmesg`; adb: `logcat` con batería llena, media, baja y con carga por USB. SWD: breakpoint «registrar» en el manejador de los mensajes de batería de av-cam (dirección por REA); capturar el evento hacia `ObjCamera` por `0x20002` y los de `InfraInput`.
- **T10 SD.** adb/telnet: `dmesg` y `logcat` al insertar, extraer, formatear y llenar; `/proc/mounts`, `/proc/partitions`, `/sys/class/mmc_host/*`. Registrar respuestas de `Fsys`/`ObjMedia` (clase `0x8402` FAT32 vs `0x8400` exFAT), recuento STLREC, escritura de ARW/JPG, grabación XAVC S cruzando 4 GB en FAT32. Trazar `Fsys_Open/Stat` con breakpoints «registrar» (direcciones de `libInfraFsys` desde `/proc/PID/maps`).
- **T11 USB.** telnet por Wi‑Fi: `dmesg`, `/sys/class/udc`, `getevent` y `logcat` al conectar/desconectar en cada modo (almacenamiento masivo, PC remote, carga); registrar el evento `0x15040010` de `InfraInput` y su orden de llegada.
- **T12 HDMI.** telnet/adb: `dmesg`, `/sys/class/*hdmi*`/`drm` y EDID si existe (NO_VERIFICADO); conectar/desconectar con 1080p y 4K (g80); capturar `CmnViewNoHdmi` y la cola `0x9c015b`; SWD: breakpoint «registrar» en el manejador del hot‑plug.
- **T13 Teclas, dial, zoom y objetivo.** `getevent -t` por telnet, para tiempos y códigos reales de los eventos de `InfraInput`.

**Bloque D — medidas de funciones ya construidas.** INTERVAL‑AE‑F3, DRP‑F2, CCH‑F2, HLG‑3b y el límite inferior del VDF de Zebra, tal como están en `PENDIENTES.md`; sin duplicar aquí.

## Reglas
- Cada traza que toque el pipeline de captura o escriba algo necesita autorización expresa del usuario para ese caso; esta lista solo planifica.
- Nada de volcado NVRAM previo (preferencia del usuario); si hubiese que recuperar, usar un volcado existente.
- Disparo siempre remoto por adb con la app `CameraEx`, nunca `CameraSequence`.
- Lectura sin parar la CPU por defecto; breakpoints que registran y reanudan; evitar `halt` largos.
- Direcciones de `libObj`/`av-cam` por REA y verificadas contra bytes antes de poner un breakpoint.
