# S66 — Montura de lente E-mount en la A6000 (línea general de ingeniería inversa)

**Hito:** subsistema de **montura de lente** (`MOUNT` / protocolo "BL") y todo lo que cuelga de él:
identificación y alimentación de la lente, protocolo cuerpo↔lente, ficheros de datos por lente,
corrección de sombreado dependiente de la lente y actualización de firmware de la lente.

**Natureza:** línea de ingeniería inversa **general** de la cámara, **independiente** de la línea
SilentShutter/obturador electrónico. No cambia ninguna conclusión de S51–S61 (fin electrónico
**NO VERIFICADO**, S51 A/B/C = NO).

**Método:** análisis estático de bytes del `av-cam.bin` de A6000 (fw3.21) y comparación con el de
A7S (fw3.20). REA 6.5.0 + Ghidra 12.1.4 para la decompilación; Capstone (LLVM como referencia
independiente) para el barrido y las tablas. **Ningún firmware ejecutado, ninguna cámara tocada.**

**Pruebas:** `tests/test_s66_lens_mount.py` — 25 tests, todos contra bytes.

---

## 1. Resumen de hallazgos (VERIFICADO)

1. **Existe un subsistema de montura de lente completo** en `av-cam.bin`: código en
   `0x436dfe6c`–`0x436e9ea4`, 646 cadenas de traza en `0x43c95659`–`0x43c9a900`, con ficheros
   fuente internos `Mount_Controller.cpp` y `Mount_DividedInfo.cpp`.
2. **El bus cuerpo↔lente es serie (UART)** con handshake por líneas **CS** y **DATA** manejadas
   con primitivas GPIO (`gpio_get` en `0x43b5e2bc`). El tráfico va en dos direcciones etiquetadas
   `[B->L]` y `[L->B]`.
3. **Trama en el cable (VERIFICADO)**: cabecera `0xF0`, longitud total (`size+8`) **little-endian**
   (byte bajo en `+1`, alto en `+2`), tipo de comunicación (`tipo & 7`) en `+3`, ID de comando en
   `+5`, datos, **checksum u16 LE** (suma aritmética de los bytes de `buf+1` durante `len-4`,
   excluye cabecera/checksum/footer) y footer `0x55`. La recepción valida en orden:
   `HEADER_NG`(3) → `FOOTER_NG`(5) → `CHECKSUM_NG`(4) → `DATASIZE_NG`(2) → `COMMTYPE_NG_0`(6)/`_1`(7)
   → despacho por ID. Tipos: 1 = *Informations* (VSYNC/VD), 2 = síncrono, 3 = asíncrono.
4. **IDs de comando (VERIFICADO)**: van en el primer byte del payload:
   `0x07` ATTACH_INFO1 (`0x436e4444`), `0x0A` CS_CREDIT (`0x436e51ac`),
   `0x15` UPDATE_DATA (`0x436e4800`, payload `0x400` B), `0x16` LENS_SLEEP (`0x436e472c`),
   `0x2B` ALPHA_LENS_INFO (`0x436e509c`). La lente declara qué comandos conoce con **dos
   bitmaps** indexados por `(ID-1)>>3` (`0x436e00dc`); la tabla de descriptores de comando
   (`{u16 id, u16 size, u16 extra}`) se registra en runtime, por lo que su contenido no es
   recuperable estáticamente.
3. **El tipo de lente se decodifica de 2 bits** (`campo & 3`): 1 = lente alimentada a **4.8 V**
   (4.096 V en el argumento del log), 2 = lente **no registrada**, resto = **tipo desconocido**
   (código de error `0xFF`; `0x0A` = tipo válido).
4. **Ciclo de vida completo** documentado por los 63 logs de la tarea principal (`0x436e5e3c`):
   detección (LENS_WEAR) → negociación (UART_HZ, ATTACH_INFO1..4, STARTUP_INFO, CS_CREDIT) →
   operación (WAKE_UP) → apagado (POWEROFF handshake) → desmontaje (DETACH_1/2/COMP) → montaje
   (LOGIC_ON/LOGIC_OFF) → standby (STANDBY, PB→WAKEUP→OFF).
5. **18 ficheros de lente** `/lens/VX9101_lensfile.bin` … `/lens/VX9129_lensfile.bin` existen en el
   firmware (`0800_appli/lens/` y `0700_part_image/dev/nflasha7_unpacked_unpacked/lens/`). Formato
   (57/57 ficheros, 18 de A6000 + 39 de A6300): cabecera `LF` de 16 B (`u16@2 = 0x10`,
   `u32@4 = filesize − 0x10`, `u16@12 = lens_id`), secciones `[magic u16][hdr_len u16=8]
   [payload_len u32][payload]` con magics `ED`, `CS` y `LC` (12 B) y un trailer fijo de 4 B. La
   tabla de nombres en `av-cam.bin` está en `0x43C22BF2` (18 slots × stride `0x42`, layout
   `[u16 key][ruta NUL-pad]`, claves `0x8011`–`0x802D`) y se consulta en `0x43907bc4`; el parser del
   fichero está en `0x43907c7c`. Los 18 ficheros de A6000 son **byte a byte idénticos** a los de la
   A6300; la A7S 3.20 **no tiene** nada de esto (0 hits de `/lens/`, `lensfile`, `VX9`).
6. **La carga de esos datos no ocurre en `av-cam.bin`**: `Camera::Lens::ODL::Load`
   (`0x43721b9c`) usa `AsyncSend`/`AsyncRecieve` → el fichero lo abre **otro servicio**.
7. **El sombreado depende de la lente**: 11 valores (`ss_LensMountShdValue[0..10]`) y 32 ganancias
   (`us_LensMountShdGain[0..31]`) por lente, y el perfil de corrección se elige con una **tabla
   `tbb` de 69 modos de captura → 14 ShdMode**.
8. **La fw3.21 de A6000 amplía el subsistema de montura respecto de la fw3.20 de A7S**: la A6000
   añade el prefijo de traza `[MOUNT_DEBUG]`/`[MOUNT_ERROR]` (223 vs 0 cadenas), la marca `[B->L]`,
   la alimentación 4.8 V, la rutina de desgaste (LENS_WEAR), el ciclo DETACH/attach,
   `ALPHA_LENS_INFO`, `CS_CREDIT`, `CHG FREQ`, `Eclipse`, `NEXTVD` y el handshake `[HS]` CS/DATA.
   La A7S conserva el núcleo (`Mount_Controller.cpp`, `Mount_DividedInfo.cpp`, `BonoboDSP_*`,
   `PREPARE UPDATE`, ruta de FW-update de la lente).
9. **El bloque de sombreado (SHD) es idéntico en ambas cámaras**: 217 cadenas `SHD::…` en cada
   una, con los mismos conjuntos; solo cambia el prefijo `[CAMERA_MAIN_YC]: `.
10. **La lente tiene su propio firmware** y la cámara lo actualiza **por el mismo bus**, con
    mensajes **CAIF/C3P**: emisor `[BL]` `0x436fe070` (estado 0 → `LUPDT_INFO`; estado 4 → trozos
    de `0x100` B → `LUPDT_DATA`), capa CAIF `0x436ba2c8` (`[p+4]=0xF0` cabecera Darwin, tag, cmd,
    longitud u16, payload), resultado en `0x436fe994`.
11. **Existe un segundo bus hacia el DSP de la lente** (`[LENS_PDR]`, "BonoboDSP"): getter de dos
    canales `0x437089d4`, parseo de 34 B `0x43708a88`, dispatcher `0x43708cc4`, MMIO en
    `0xf292d000`, transporte por CAIF (`0x43561228`).
12. **Los ficheros de lente tienen formato propio**: cabecera `LF` (16 B) con `lens_id` en `+0x0c`
    y secciones `ED` (datos u16), `CS` (tabla) y `LC` (6 u16) + trailer de 4 B; el parser está en
    `av-cam.bin` (`0x43907c7c`), es decir, el *contenido* se parsea en la cámara aunque el fichero
    lo traiga otro servicio (`Camera::Lens::ODL::Load`, `0x43721b9c`).

## 2. Documentos del hito

| Subtarea | Contenido | Informe |
|---|---|---|
| A | Mapa de funciones del controlador y framing del protocolo | `analysis/s66/mount_functions.md` · `.json` |
| B | Formato de los ficheros `VX91xx_lensfile.bin` y quién los carga | `analysis/s66/lensfile_format.md` · `.json` |
| C | Actualización de firmware de la lente (CAIF) y bus BonoboDSP | `analysis/s66/lens_fwupdate_dsp.md` · `.json` || D | Encendido, identificación y ciclo de vida de la montura | `analysis/s66/lens_power_attach.md` · `.json` |
| E | Corrección de sombreado dependiente de la lente (SHD) | `analysis/s66/lens_shading.md` · `.json` |
| F | Clase `Camera::Lens`, cargador ODL, jobs y barrera de lente | `analysis/s66/lens_class_and_jobs.md` · `.json` |

Scripts de apoyo: `analysis/s66/{lens_strings,mount_strings_map,func_strings,shd_modes}.py`;
evidencia cruda en `analysis/s66/out/`.

## 3. Mapa del subsistema (direcciones exactas)

| Elemento | Dirección A6000 |
|---|---|
| Strings del subsistema MOUNT | `0x43c95659`–`0x43c9a900` |
| Tabla de nombres `/lens/VX91xx_lensfile.bin` | `0x43c22bf4`–`0x43c23069` (paso 0x42) |
| Controlador de montura | `0x436dfe6c`–`0x436e9ea4` |
| Construcción del mensaje de envío | `0x436e046c` |
| Envío SYNC / ASYNC | `0x436e0d74` / `0x436e1328` |
| Volcado de estado (CommState/LensState/PowMode…) | `0x436e239c` |
| Handshake [HS] (CS/DATA) | `0x436e48fc`, `0x436e4d68` |
| Decodificación del tipo de lente | `0x436e4eb4` |
| Tarea principal de montura | `0x436e5e3c`–`0x436e7bf0` |
| `Camera::Lens::ODL::*` | `0x43721aa8`–`0x43721c80` |
| `SHD::GetShdMode` (tabla `tbb`) | `0x438ef40e` (tabla en `0x438ef418`) |

## 4. Qué NO se ha demostrado (NO_VERIFICADO)

- **Pines físicos** de CS/DATA y de la alimentación 4.8 V (descriptores en memoria reubicada,
  fuera del blob).
- **Unidades** de `UART_HZ 750/1500` y de los timeouts.
- **Nombre de cada ID de comando**: la tabla de descriptores se registra en runtime; solo se
  conhece el mecanismo (bitmaps "la lente conoce el comando") y el framing.
- **Identidad del servicio** que abre `/lens/VX91xx_lensfile.bin` (la entrada en `av-cam.bin` es
  `Camera::Lens::ODL::Load`, que usa mensajes asíncronos).
- **Semántica eléctrica** de la lente (fin de integración, obturación): fuera del alcance de esta
  línea; S51 se mantiene.

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s66_lens_mount.py -q
.venv/bin/python analysis/s66/mount_strings_map.py A6000 --lo 0x43c95600 --hi 0x43c9ab00
.venv/bin/python analysis/s66/func_strings.py A6000 0x436e5e3c 0x436e7bf0 --calls
.venv/bin/python analysis/s66/shd_modes.py A6000
```

Sesión REA: demonio `analysis/rea-independent/bin/session_daemon.py` + cliente `bin/q.py`
(≈8–10 min de análisis en frío de `av-cam.bin`).
