# S95 — Los ficheros que la cámara lee y escribe: parámetros SPICA/PSF/DFE y trazas en RAM disk

**Alcance:** línea de ingeniería inversa **general** de la cámara: el **inventario completo de rutas de
fichero** que el firmware de la A6000 (fw3.21) usa — parámetros de procesado (`/usr/sabin/`), la
imagen del DFE, los ajustes (`/setting/`) y, sobre todo, los **ficheros de traza que la propia
cámara escribe en el disco RAM** (`/mnt/*.dat`). No es la línea SilentShutter, ni la montura (S66),
ni el AF, ni ADJ_CMD, ni ZPD, ni ZIT, ni ADF, ni el API del SA, ni el visor, ni las caras, ni el
wireless, ni el almacenamiento (S87), ni la reproducción (S90).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s95_files.py`.

---

## 1. El inventario (VERIFICADO)

**43 rutas** distintas en el `av-cam.bin`, en cuatro zonas:

| zona | nº | rutas |
|---|---|---|
| `/usr/sabin/` | 27 | parámetros de procesado (SPICA, PSF, STAR) |
| `/mnt/` | 11 | trazas y logs escritos por la cámara en el disco RAM |
| `/setting/` | 1 | `psd.bin` (S75/S87) |
| `/usr/dfe/`, `/etc/`, `/usr/share/` | 4 | imagen del DFE, zona horaria, locale |

## 2. `/usr/sabin/` — los parámetros de procesado (VERIFICADO)

### 2.1 Los ficheros SPICA ("musashi") — 22 ficheros

Nomenclatura: **`spica_musashi_<modo>_<canal>_tap_step<N>.bin`**, donde `<modo>` ∈ {still, mov,
mov_4k, mov_interlace, dualrec, dualrec_4k} y `<canal>` ∈ {c, y} (**C** y **Y** del espacio de
color), con **dos pasos** (`tap_step1`, `tap_step2`).

| fichero | dirección |
|---|---|
| `spica_musashi_still_c_tap_step1.bin` | `0x43cc3774` |
| `spica_musashi_still_c_tap_step2.bin` | `0x43cc3834` |
| `spica_musashi_still_y_tap_step1.bin` | `0x43cc3894` |
| `spica_musashi_still_y_tap_step2.bin` | `0x43cc3315` |
| `spica_musashi_mov_c_tap_step1.bin` | `0x43cc3375` |
| `spica_musashi_mov_c_tap_step2.bin` | `0x43cc33d5` |
| `spica_musashi_mov_y_tap_step1.bin` | `0x43cc3435` |
| `spica_musashi_mov_y_tap_step2.bin` | `0x43cc34f5` |
| `spica_musashi_mov_4k_c_tap_step1.bin` | `0x43cc35f4` |
| `spica_musashi_mov_4k_c_tap_step2.bin` | `0x43cc3495` |
| `spica_musashi_mov_4k_y_tap_step1.bin` | `0x43cc36b4` |
| `spica_musashi_mov_4k_y_tap_step2.bin` | `0x43cc3714` |
| `spica_musashi_mov_interlace_c_tap_step1.bin` | `0x43cc3654` |
| `spica_musashi_mov_interlace_y_tap_step1.bin` | `0x43cc37d4` |
| `spica_musashi_dualrec_c_tap_step1.bin` | `0x43cc3b3a` |
| `spica_musashi_dualrec_c_tap_step2.bin` | `0x43cc3cba` |
| `spica_musashi_dualrec_y_tap_step1.bin` | `0x43cc3ada` |
| `spica_musashi_dualrec_y_tap_step2.bin` | `0x43cc3bfa` |
| `spica_musashi_dualrec_4k_c_tap_step1.bin` | `0x43cc38f4` |
| `spica_musashi_dualrec_4k_c_tap_step2.bin` | `0x43cc3b9a` |
| `spica_musashi_dualrec_4k_y_tap_step1.bin` | `0x43cc3954` |
| `spica_musashi_dualrec_4k_y_tap_step2.bin` | `0x43cc3c5a` |

**22 ficheros SPICA** en total: 4 por modo (still, mov, mov_4k, dualrec, dualrec_4k → 5 modos × 4) y 2 para `mov_interlace` (un solo paso por canal).

Esto **confirma y precisa** lo que S76 Higgins apuntaba: el procesado **SPICA** (etapa
`Stage_SPICA`, S76/S84) toma sus parámetros de ficheros externos, con **dos pasos** ("tap step") y
**dos canales** de color, y con **variantes por modo de captura** (foto, vídeo, 4K, entrelazado y
"dualrec" = grabación dual BAYER+CLEARVID, S82).

### 2.2 Los demás ficheros de `/usr/sabin/`

- `star_kernel_param.bin` (`0x43cc3d1a`) → los parámetros del **kernel STAR** (`sa_func_STAR_*`,
  S84).
- `dcv_psf_table_still.bin` (`0x43cb9a34`), `dcv_psf_table_movie.bin` (`0x43cba98a`),
  `dcv_psf_table_movie_4k.bin` (`0x43cbaa4a`),
  `dcv_psf_table_dualrec.bin` (`0x43cba9ea`) → las **tablas de PSF** de la deconvolución
  (`Stage_Decomp`, `Stage_LoadDeconvPsfTbl`, S76).

## 3. `/mnt/` — la cámara escribe sus propias trazas en el disco RAM (VERIFICADO)

**11 rutas**, todas con extensión `.dat` o `.bin`:

| fichero | dirección | qué es (por el prefijo) |
|---|---|---|
| `/mnt/%s.%4d%02d%02d_%02d%02d%02d.dat` | `0x43cb4eeb` | traza genérica con **nombre + fecha/hora** (`%4d%02d%02d_%02d%02d%02d`) |
| `/mnt/FILE%04x.dat` | `0x43cbe562` | traza de **YC** (prefijo `YC_FILE` en S89) |
| `/mnt/FILE_IS_%04x.dat` | `0x43c9a535` | traza de **IS/EIS** (S70) |
| `/mnt/FILE_TC_COMMON_%04x.dat` | `0x43ca84f2` | traza de **TC/giro** (S70) |
| `/mnt/lc_mslog_%04x.dat` | `0x43ca7a7d` | traza de **LC** (calibración de lente / ZPD, S75) |
| `/mnt/Mount_ms_log_%03d.dat` | `0x43c97146` | traza de la **montura** (S66) |
| `/mnt/cc_ms_log%04x.dat` / `%s.dat` | `0x43cb5004` / `0x43cb4f4d` | traza de **CC** (control de captura, S82) |
| `/mnt/detect_ms_log%04x.dat` | `0x43c9162e` | traza de **detección** (caras/AF, S71) |
| `/mnt/log.bin` | `0x43c8f789` | log binario genérico |

**Hallazgo operativo (VERIFICADO):** la cámara **escribe ficheros de traza en su propio disco RAM**
(`/mnt`), con nombre por módulo y, en un caso, con **fecha y hora** en el nombre. Como el proyecto
ya dispone de volcados de RAM de la cámara (`analysis/camera-dumps/`, S64/S65), **estos ficheros
deben estar presentes en esos volcados** → son una fuente de datos primarios para contrastar los
hitos de RE (montura, ZPD, IS/EIS, detección) **sin necesidad de más instrumentación**.

## 4. Otros ficheros (VERIFICADO)

- `/usr/dfe/dfe.bin` (`0x43cd1b94`) → la **imagen de firmware del DFE** (la que el proyecto ya
  analiza en S16–S18).
- `/setting/psd.bin` (`0x43ccf2b6`) → ajustes (ZPD "from body", S75; también lo escribe
  `CameraOnDemandSaver.so`, S72/S87).
- `/etc/localtime` (`0x43bd5744`), `/usr/share/zoneinfo` (`0x43bd5754`),
  `/usr/share/locale` (`0x43bd92b4`) → **zona horaria y locale** (encaja con los retardos 60/50 Hz
  del sonido del sistema, S91, y con las marcas de tiempo del índice, S87).

## 5. Abierto (NO_VERIFICADO)

- El **formato binario** de los ficheros `spica_musashi_*_tap_step*.bin` y de las tablas PSF (¿son
  los mismos "tags" que S16–S18 analizan para el DFE?).
- Qué significa exactamente "musashi" (¿el nombre del algoritmo de procesado?).
- El formato de `/mnt/*.dat` (¿texto? ¿binario con cabecera?).
- Si los ficheros de `/mnt/` se borran al apagar o sobreviven en el volcado de RAM.
- Por qué `dualrec_4k` y `mov_4k` tienen_PARAMETER sets propios (¿parámetros distintos por
  resolución?).

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s95_files.py -q
```
