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
