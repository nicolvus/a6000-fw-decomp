# G85 — Plan de trazas en cámara para completar la LIRO VM (17-11-2026)

Origen: petición del usuario («todo lo que hay que capturar en cámara para la VM de principio a fin», incluidos batería, SD, USB y HDMI). Pendiente: [TRAZA-VM](../PENDIENTES.md). Etiquetas: VERIFICADO, NO_VERIFICADO. **Plan, sin ninguna traza ejecutada.**

## Reglas de ejecución (decididas por el usuario, 17-11-2026)

- **Versión: la instalada, CFW 3.78** (no el `.dat` más reciente, 3.81, que no está instalado). Todo se verifica contra lo instalado. Las direcciones de `libObj`/`av-cam` salen de REA/Ghidra sobre el firmware 3.21 y **cada breakpoint se comprueba antes**: se lee la memoria por SWD y se compara con los bytes de la imagen 3.78 (`analysis/gui/g22/pkg-378w/…`; `libObj.so` y `nflasha3` son idénticos al 3.77). Si no coinciden, no se pone el breakpoint.
- **Reparto del trabajo:** el agente lanza los scripts, lee las salidas y decide el siguiente paso. El usuario solo **toca la cámara** (encender, enchufar, disparar a mano si hace falta, insertar tarjeta) cuando se lo pida, una instrucción cada vez.
- Cada traza que toque el pipeline de captura o escriba algo necesita autorización expresa del usuario. Sin volcado NVRAM previo (preferencia del usuario); si hubiera que recuperar, usar uno existente. Disparo remoto por adb con `CameraEx`, nunca `CameraSequence`.
- Cada traza guarda en `analysis/camera-dumps/<fecha>-traza-<Tn>/` los datos crudos, un informe breve y el sha256 de la imagen/versión instalada.

## Prerrequisitos medidos hoy (17-11-2026)

- `ping 192.168.1.29`: **sin respuesta**; la cámara no estaba en la red (apagada o sin Wi‑Fi/telnetd).
- `lsusb`: **no aparece la sonda** `2e8a:000c` (RP2040 `debugprobe-zero`) ni la cámara.
- Antes de empezar hay que comprobar `pmca-console info` (debe dar firmware 3.78).

---

## GRUPO 1 — SWD (sonda RP2040 + OpenOCD 0.12, `cortex_a -ap-num 1 -dbgbase 0x80110000`)

**Por AP0 se lee la dirección física = virtual de `av-cam` + `0x40000000`** (`0x43ede338` → `0x83ede338`); leer `0x43…` directamente deja los AP en «stalled AP operation» (MEDIDO 17-11-2026). Sondeo del arranque: `scripts/swd_poll_arranque.sh` (reconecta, detecta corte de alimentación por el vector `0x0`, mata sesiones atascadas y no deja openocd huérfano). Sirve para lo que ocurre dentro del BIONZ/`av-cam` y no se ve desde Android: watchpoints, breakpoints «registrar y reanudar» y lectura de RAM sin parar la CPU. Guiones base: [R47](../capture/e26-r47-primer-contacto-swd-lectura-ram.md) y `analysis/camera-dumps/20261105-bionz-swd-disparos`. Un `halt` largo pierde el APB‑AP (R47 §9): leer sin parar por defecto.

| Traza | Qué se registra | Cómo | Acción del usuario |
|---|---|---|---|
| **S1 — arranque en frío completo** | Búfer de consola `0x83400000` (`ExcConf` 17 ids, DIADEM, `DFECore`, `CAMERA_MAIN_SYNC`) con orden y tiempos | Halt al responder el DAP, reanudar y leer el anillo cada ~1 s para que no se envuelva; dos tomas: arranque normal y con estado restaurado | Quitar y poner batería; pulsar encendido |
| **S2 — escritor de `0x43eaeecd`/`0x43eb26c9`** | PC, `lr` y r0–r3 de cada golpe | Watchpoint de escritura en ambas; breakpoints «registrar» en `0x439e2888`, `0x4384fb7c`, `0x43729a76` (caso 22) y `0x4372a0c6` | El mismo arranque que S1 (se hace a la vez) |
| **S3 — tráfico ObjCamera↔av-cam (`0x20002`)** | Mensajes, incluidos `0x3003`, `0x3000`, `0x3024`, con el formato de `avcam.jsonl` | Breakpoints «registrar» en envío/recepción de la cola (direcciones por REA, verificadas) | Encender; S1/S2 (si el disparo remoto no puede, a mano); grabar vídeo |
| **S4 — montura y módulos** | `[0x43ede338]`, `[0x43ede320]`, estados de módulo (`+0x5c`/`+0x1c`), `0x43eaee84+0x49` cada 100 ms | Lectura sin parar | Repetir con y sin objetivo |
| **S5 — MMIO del sensor IMX210 y del ISP por disparo** | Escrituras a `r5`, ShutMode, VTS | Watchpoints en las ventanas MMIO; reutiliza `camera_imx210_timing.py`, `camera_r5_raw.py` | Disparo (remoto por adb si se puede); repetir en mecánico, EFCS y Silent |
| **S6 — búferes de imagen tras el disparo** | LUT `0x654` B, HLG 3×4122 B, curva 2048 pt, colorimetría, cuantización JPEG, rejilla 11×11 | Lectura de RAM sin parar tras cada toma (alternativa: `senser_ram_dump.py`); repetir por configuración: PP, S‑Log, HLG, Color Chrome, LUT, DRO, ISO 51200, Extra Fine, Keystone, Live ND | Cambiar el ajuste en el menú y disparar |
| **S7 — manejadores de batería y hot‑plug** | Mensajes de batería de av-cam hacia `ObjCamera`; manejadores de USB y HDMI | Breakpoints «registrar» (direcciones por REA, verificadas) | Descargar/cargar batería, enchufar y quitar USB y HDMI cuando se pida |
| **S8 — llamadas de `Fsys`/`ObjMedia`** | `Fsys_Open/Stat` y respuestas (`0x8402`/`0x8400`) | Breakpoints «registrar» en `libInfraFsys` (base desde `/proc/PID/maps` de T1) | Insertar, extraer y llenar tarjeta |

---

## GRUPO 2 — telnet / adb (por Wi‑Fi, `192.168.1.29`; `scripts/camera_telnet.py`, `adb`)

Sirve para el sistema Android/Linux: kernel, sysfs, procesos y disparo remoto. Por Wi‑Fi se pueden conectar USB y HDMI sin perder la sesión.

| Traza | Qué se registra | Cómo | Acción del usuario |
|---|---|---|---|
| **T1 — mapas y versión** | `/proc/PID/maps` de `libObj` y `av-cam`, `uname`, versión instalada (LIBOBJ-MAP) | `camera_telnet.py` | Ninguna (cámara encendida) |
| **T2 — batería** | `/sys/class/power_supply/*`, `dmesg`, `logcat` | Muestreo cada 2 s | Batería llena, media y baja; con y sin carga por USB |
| **T3 — SD** | `dmesg`/`logcat` al insertar, extraer, formatear y llenar; `/proc/mounts`, `/proc/partitions`, `/sys/class/mmc_host/*`; recuento STLREC; clip XAVC S cruzando 4 GB en FAT32 | `camera_telnet.py`, `camera_pull.py` | Insertar, extraer, formatear, llenar |
| **T4 — USB** | `dmesg`, `/sys/class/udc`, `getevent` y `logcat` en cada modo (almacenamiento, PC remote, carga); evento `0x15040010` | `camera_telnet.py` | Enchufar y desenchufar el cable en cada modo |
| **T5 — HDMI** | `dmesg`, sysfs/EDID, `CmnViewNoHdmi`, cola `0x9c015b` | `camera_telnet.py` | Conectar y desconectar HDMI a 1080p y 4K |
| **T6 — teclas, dial, zoom** | `getevent -t` con tiempos reales | `camera_telnet.py` | Pulsar cada control cuando se pida |
| **T7 — disparo remoto y pares ARW+JPG** | Foto con cada perfil/ajuste; ficheros de la tarjeta | App `CameraEx` por adb + `camera_pull.py` | Ajustar el menú y confirmar la escena |
| **T8 — medidas de funciones construidas** | INTERVAL‑AE‑F3, DRP‑F2, CCH‑F2, HLG‑3b, VDF de Zebra (tal como están en `PENDIENTES.md`) | Disparo remoto + volcados | Según cada caso |

## Orden recomendado

1. Grupo 2 T1 (comprueba red, versión y mapas; no toca nada).
2. Grupo 1 S1+S2 (la única que destraba E2E‑10/12/15) y S3–S4.
3. Grupo 2 T2–T6 (batería, SD, USB, HDMI, teclas).
4. Grupo 1 S5–S8 y Grupo 2 T7–T8 (imagen; las más delicadas, con autorización expresa).

## Límites
- Que `getevent`, EDID o sysfs de HDMI/UDC existan en la cámara no está verificado (NO_VERIFICADO).
- `/proc/PID/mem` por telnet no está probado.
- Los breakpoints sobre código parcheado (cuevas g55/g65, ganchos G33) dependen de las direcciones del 3.78 instalado; hay que verificarlas.

## Resultados

### S1 (sondeo) — arranque en frío real, CFW 3.78 instalado (17-11-2026, MEDIDO)

`analysis/camera-dumps/20261117-traza-S1/poll_arranque4.log` (no versionado; 1954 muestras, ~0,15 s, 300 s). Palabras leídas por AP0 en físico (`virtual + 0x40000000`). Tiempos relativos al inicio del sondeo; la batería se quitó en ≈ 15,9 s.

| t (s) | `[0x43ede338]` | `[0x43ede320]` | palabra `0x43eaeecc` | Lectura |
|---|---|---|---|---|
| 0–15,9 | 0 | 0 | `0x00010000` | resto del arranque anterior |
| 15,9 | 0 | 0 | 0 | sin alimentación / RAM a cero |
| 20,5 | 0 | 0 | `0x00010000` | RAM inicializada (`0x43eaeece` = 1) |
| 39,27 | 0 | **2** | `0x00010000` | lo deseado pasa a 2 |
| 39,42 | 0 | 2 | `0x00010104` | **`0x43eaeecd` = 1** (`0x43eaeecc` = 4) |
| 39,57 | **2** | 2 | `0x00010107` | actual = 2 (`0x43eaeecc` = 7): el paso que acepta `0x3003` |
| 40–292 | 2 ↔ `0x10` | 2 ↔ `0x10` | `0x00010107` | estable en 2 (1496/1571 muestras tras 60 s) con excursiones breves a `0x10` (primero cada ≈ 3 s, luego cada ≈ 60 s) |

Conclusiones:
- **La barrera de E2E-12b ocurre en la cámara real**: `0x43eaeecd` pasa de 0 a 1 en un único intervalo de muestreo justo antes de que `[0x43ede338]` llegue a 2, ≈ 19 s después de que la RAM se inicialice. Confirma el mecanismo de la VM (con ese byte a 1 el guion llega a 2).
- El estado 2 se mantiene en reposo con la pantalla de disparo; el `1/1` y `0x43eaeecd = 0` del volcado `ram-servicio` y de la primera lectura de hoy son otro estado posterior (NO_VERIFICADO cuál: ¿ahorro de energía?).
- `0x10` es una secuencia periódica (primero cambia `[0x43ede320]`, después `[0x43ede338]`), NO_VERIFICADO qué es.
- Resolución de 0,15 s: no distingue los pasos intermedios del guion (0→2→0x1b→1 del volcado). El escritor de `0x43eaeecd` sigue sin identificar: hace falta S2 (watchpoint).

### S2 (watchpoint) — 17-11-2026 (MEDIDO)

Herramienta: `scripts/swd_wp_arranque.sh` (DBGWVR/WCR 0–1 por AP1 en los 4 Cortex-A5, WFAR + r0–r3/lr por ITR). Logs en `analysis/camera-dumps/20261117-traza-S2/` (no versionados).

- **En reposo** (cámara arrancada): los bloques `0x43eb2680` y `0x43eaee84` (`0x8cc` B) se copian **entre sí en ambos sentidos** cada fotograma con el `memcpy` de `0x439c535c` (WFAR; r0/r1 = destino/origen), unas 20 veces/s. No hay otro escritor de `0x43eb26c9`/`0x43eaeecd` en reposo (22 s vigilados).
- El watchpoint del A5 es síncrono: si se reanuda armado, la misma instrucción vuelve a saltar sin fin (primer intento: núcleo 2 parado ≈ 300 ms). Corregido: desarmar el núcleo, reanudar y rearmar.
- **Durante el arranque** se vio que `0x439c5a6c` (lr `0x437b5635`) pone a cero `0x43eb2680` (`0x8ac` B): inicialización del bloque.
- **Incidente:** armado desde la inicialización de la RAM, las ~20 paradas/s del núcleo 2 durante el arranque provocaron reinicios cada ≈ 24 s y después la cámara no arrancó (DP vivo, AP atascados). Se desarmó todo (WCR = 0, HDBGen = 0); tras quitar la batería ≥ 30 s arrancó normal (`[0x43ede338]` = `[0x43ede320]` = 2, `0x43eaeecc` = `0x00010107`). Sin escrituras en RAM/NAND/NVRAM. Desde entonces el script **solo arma con el arranque terminado** (`[0x43ede338]` == 2).
- Pendiente: el escritor real del flag en el arranque. Vía sin parar la CPU en cada fotograma: S1 lo sitúa en un único intervalo ≈ 19 s tras la RAM; opciones: armar solo en esa ventana, o vigilar la orden del caso 22 (`0x4372a0c6`) con un breakpoint de un solo golpe.

### S2b (breakpoints de un solo golpe) — 17-11-2026 (MEDIDO)

`scripts/swd_bp_unico.sh` (BVR/BCR 0–2, ≤ 1 parada por dirección y núcleo; validado en reposo con ARM `0x439c534c`, BAS `0b1111`, y Thumb `0x4386b5da`, BAS `0b1100`). Bytes de las tres direcciones iguales en la RAM del 3.78 y en `av-cam.bin` 3.21. Log: `analysis/camera-dumps/20261117-traza-S2/bp_arranque.log`.

- Armados en `0x4384fd06` (`strb.w r0,[r2,#0x49]`), `0x4384fd6e` (`strb.w r1,[r2,#0x49]`) y `0x4372a0c6` (`bl 0x439e2888`, caso 22) desde el encendido (rearmados al volver la alimentación de cada núcleo): **ninguno saltó** y la cámara llegó al estado 2 con `0x43eaeecc` = `0x00010107` (flag a 1). Arranque normal, sin incidencias.
- Conclusión: en la cámara real el flag `+0x49` **no** lo escriben `0x4384fd06`/`0x4384fd6e` y el caso 22 del despachador no se ejecuta en el arranque; la cadena estática de E2E-12c no es la que actúa. S1 sugiere una escritura conjunta de `+0x48`/`+0x49` (`0x0104`, luego `+0x48` = 7).
- En reposo prolongado la cámara pasa sola de 2 a 1 con el flag a 0 (estado del volcado `ram-servicio`).
- Siguiente: watchpoint en el arranque con un manejo barato de los golpes del `memcpy` (solo WFAR, sin leer registros), previa autorización por el riesgo del incidente S2.

### S2c (watchpoint solo en la ventana del arranque) — 17-11-2026 (MEDIDO)

`swd_wp_arranque.sh` con `ARMAR=ram` (armado solo con la RAM inicializada y `[0x43ede338]` = 0, desarmado al llegar a 2, una sola sesión), golpes del `memcpy` reanudados sin leer registros (≈ 5 ms por parada, ≈ 30–50 golpes/s) y `PARES=1` (destino←origen de cada golpe ignorado). Logs `wp_arranque2.log`, `wp_arranque3.log`.

- Dos arranques completos (20,8 s y 15,7 s de ventana armada, ≈ 760 y ≈ 280 golpes del `memcpy`): **ningún escritor fuera del `memcpy`** y solo los dos pares conocidos (`0x43eb26c0←0x43eaeed4`, `0x43eaeec4←0x43eb26d0`); aun así el flag llega a 1.
- Hipótesis abiertas: (a) la escritura cae en los ms en que el núcleo está desarmado tras un golpe (≈ 15–25 % del tiempo; improbable dos veces seguidas), (b) la hace otro maestro del bus (DMA) o la CPU por **otra dirección virtual** (alias del mismo físico): el watchpoint compara direcciones virtuales.
- **Interferencia con el encendido (MEDIDO):** con el sondeo SWD activo durante el encendido la cámara no arrancó en 5 ciclos de batería seguidos (sin watchpoint armado: solo lecturas de AP0 y reconexiones del DP cada ≈ 1,3 s); arrancó al desconectar el SWD. Regla nueva: lanzar los scripts SWD **con la cámara ya encendida** (la RAM de av-cam se inicializa segundos después; el flag ≈ 20 s más tarde).
- Siguiente: muestreo sin paradas (`swd_poll_arranque.sh` con `PCS=1 PERIODO=0`, 5,6 ms por muestra: flag + PC de los 4 núcleos) para fechar el cambio del flag y ver qué ejecutaba cada núcleo en ese instante.

### S2d (muestreo de PC sin paradas, 5,6 ms por muestra) — 17-11-2026 (MEDIDO)

`swd_poll_arranque.sh` con `PCS=1 PERIODO=0`, lanzado con la cámara recién encendida (`pcs_arranque.log`, 21 962 muestras en 120 s, sin paradas de CPU).

- Durante los 120 s el arranque **se quedó en la barrera**: `[0x43ede338]` = `[0x43ede320]` = 0 y `0x43eaeecc` = `0x00010000` (flag a 0); al acabar el muestreo, `[0x43ede320]` = 2 con `[0x43ede338]` = 0 (el mismo bloqueo que la VM), y **≈ 10–15 s después de cesar el tráfico SWD** el flag pasó a 1 y el guion siguió (6 → 2 → `0x3b` → 2).
- Con el sondeo a 150 ms (S1) el flag se puso con normalidad ≈ 19 s tras la RAM. Conclusión: el suceso que pone el flag es sensible al tráfico intenso por el AHB-AP (≈ 7 accesos cada 5,6 ms), mientras la CPU sigue corriendo. Refuerza la hipótesis (b) de S2c: el flag llega por un **periférico/DMA** (encaja con `MOUNT_ERROR CAM_INFO2_RCV_WAIT_TIMEOUT_ERR` del volcado `ram-servicio`: comunicación con el objetivo), no por una escritura de CPU en esa dirección virtual. Es inferencia, NO_VERIFICADO.
- Siguiente: muestreo de PC a ritmo moderado (≈ 50 ms) que no bloquee; y en la VM, buscar el periférico/DMA de la comunicación con el objetivo (`CAM_INFO2`) que escribe el bloque.

### Grupo 2 — avance (17-11-2026, MEDIDO)

Herramientas: `scripts/camera_get.py` (trae ficheros por el adbd del Tweak, puerto 5555 sin claves, vía tmpfs `/android/mnt/obb`; el FTP de `camera_pull.py` no llega al PC) y `scripts/camera_evento.py inicio|fin` (ventana por acción física: búfer de log del firmware `0x83400000`, logcat, dmesg, `dumpsys battery`, montajes, getevent). Datos en `analysis/camera-dumps/20261117-traza-T2T6/` (no versionado).

- **T1:** cámara en `192.168.1.30`; busybox sin `head/cut/tr/wc` pero con `busybox md5sum`; `logcat`, `getevent`, `dumpsys` funcionan en el chroot `/android`.
- **T2 batería:** no hay `/sys/class/power_supply`; la fuente es `dumpsys battery` (BatteryService recibe avisos de las colas `0x9241c2`/`0x924126` de `im.elf`): 56 % → 48 % en la sesión, 4,0 V, sin carga.
- **T6 teclas:** `getevent` no ve nada (solo el teclado ficticio `D keyboard`): teclas y diales no pasan por la entrada de Linux. El búfer del firmware no registra códigos de tecla y C1/C2 (ampliación de enfoque) lo llenan en ≈ 15 s (`ViewFocusMagnification`). Límite: capturar teclas reales exigiría leer la cola de `InfraInput` (`0x7a0020`) por SWD; el mapa estático `KEY_TACT_*` de g22 sigue siendo la referencia.
- **T3 SD:** `dmesg` registra la extracción (`mmc_hwip_system_off`, 1061,4 s) y la inserción (`mmca10: p1`, 1072,9 s; tarjeta de 32 GB). Ni el búfer del firmware ni logcat anotan nada. Las respuestas de `Fsys`/`ObjMedia` necesarias para la VM requieren breakpoints en `libInfraFsys` (SWD, pendiente).
- **T4 USB, T5 HDMI:** pendientes (pausado por el usuario).
