# S164 — el módulo `[CAMERA_IS]` (17 trazas): la capa de estabilización de imagen de la cámara

> Línea de RE general. Solo bytes (A6000 fw3.21; comparación con A7S fw3.20 y A6300 fw2.01).
> `vaddr = 0x43541000 + file_offset`. Referencias: regla **estricta** (canónica del repo).

## Veredicto

**`[CAMERA_IS]` es la capa de estabilización de imagen (IS) de la cámara**, con **4 sub-capas**:
`MOUNT` (5 trazas), `DIST` (5), `AS` (3), `EIS` (4). **17 cadenas, 21 sitios PIC, 13 funciones,
17/17 referenciadas (0 muertas), 7 envoltorios de traza.**

## Cifras

| magnitud | valor |
|---|---|
| cadenas / sitios PIC / funciones | 17 / 21 / 13 |
| categoría de log por sub-capa (`r1`) | DIST=1, EIS=2, AS=4, MOUNT=6 (`r0`=0xf) |
| sub-etiquetas | MOUNT 5, DIST 5, AS 3, EIS 4 |
| diferencial A7S fw3.20 / A6300 fw2.01 | token `[CAMERA_IS]` **0 / 0**; textos interiores **0/17** en ambos |

## Las 17 trazas (dirección → función)

| cadena | sub-capa | función | contenido |
|---|---|---|---|
| `0x43c98da6` | MOUNT | `0x436ea2d0` | `IS_LensMountExpStartCB (%x)` — mensaje ≠ `0xF0/0xF1` |
| `0x43c98dde` | MOUNT | `0x436ea2d0` | `IS_LensMountExpStartCB - checkData` — payload de 25 B inválido |
| `0x43c98e1d` | DIST | `0x436ea470` | `MakeDistCorPrm prm=null` |
| `0x43c98e4d` | DIST | `0x436ea50c` | `CnvPosInvDistCorr prm=null` |
| `0x43c98e80` | DIST | `0x436ea50c` | `CnvPosInvDistCorr prm=inv1 (%d, %d)` — fuera de rango |
| `0x43c98ebc` | DIST | `0x436ea50c` | `CnvPosInvDistCorr prm=inv2 (%d, %d)` |
| `0x43c98ef9` | DIST | `0x436ea65c` | `MakeDistRawAppliTag prm=null` |
| `0x43c9a1f3` | AS | `0x436fecbe` | `osal_reg_sync_msg_queue_cb %x` (2 sitios) |
| `0x43c9a234` | AS | `0x436fee80`, `0x4371e4cc` | `upm_get_hcrn_ura %x` (2 sitios) |
| `0x43c9a26b` | AS | `0x436ffab4` | `osal_unreg_sync_msg_queue_cb %x` (2 sitios) |
| `0x43c9a2b2` | EIS | `0x43702dac`, `0x43704d90` | `rcct_SetStblzPower error!` (2 sitios) |
| `0x43c9a2eb` | EIS | `0x43702dac` | `rcct_SetStblzGridH error!` |
| `0x43c9a324` | EIS | `0x437046a4` | `GyroAD[p],GyroAD[y], %d, %d` — ADC del giroscopio |
| `0x43c9a352` | EIS | `0x437046a4` | `%x, %d, %d` — contador + 2 valores |
| `0x43c9a3a7` | MOUNT | `0x43705d64` | `IS_LensMountPanoramaGyroCB (%x)` |
| `0x43c9a3e3` | MOUNT | `0x43705d64` | `IS_LensMountPanoramaGyroCB - checkData` — payload de 38 B |
| `0x43c9a426` | MOUNT | `0x43705dd0` | `IS_LensMountPanoramaGyro (%x)` — envío al objetivo |

## Qué aporta

* Programa el **recurso RC de estabilización**: `rcct_SetStblzPower` (`0x439417c8`,
  verificado por la cadena `rcct_SetStblzPower` `0x43ce190c` referenciada en `0x439417ee`) y
  `rcct_SetStblzGridH` (`0x43941814`, cadena `0x43ce186a` → sitio `0x4394183a`), ambos en
  `src/api_rc.cpp` (`0x43ce15d1`). La rejilla se redondea a múltiplo de 8 (`0x43702db0`).
* Lee el **giroscopio** (canales ADC p/y) en `0x437046a4` vía `0x4370665c`.
* Aplica la **corrección de distorsión** (`0x436ea50c`): `pos -= (coef·(pos−centro)) >> 10`,
  con coef/centro en los globales `0x43f61884`/`0x43f61886`.
* Se registra como cliente del servicio **`LENS_MOUNT`** (`0x43c9a39c`; comparación en
  `0x43707270`) y recibe dos callbacks de la montura (`0xF0`/`0xF1`).
* Escribe el **fichero de calibración IS por lente** `/mnt/FILE_IS_%04x.dat` (`0x43c9a535`,
  contador u16 en `0x43f65d3c`, texto `Ch.0/00,…` `0x43c9a54b`).

## Relación con S70 / S66 / S133

S70 ya tenía 12 de las 17 trazas y 12 de las 13 funciones → **coincidencia total** con el
mapa manual de S70 (validación cruzada). S164 añade `0x4371e4cc` (máquina de estados del AS,
sitio `0x4371e738`) y 5 trazas. El código del IS vive **en la misma región** que el driver de
la montura (`0x436ea2d0`–`0x43707152`) y que `Camera::Lens` (`0x43c99f7a`–`0x43c9b2f5`).

## Diferencial

La etiqueta **y la capa de aplicación** (giroscopio, matemática de distorsión, callbacks de
montura, cola "AS") son **propias de la A6000 fw3.21**. Pero la **infraestructura RC**
(`rcct_SetStblz*`, `WrapRcctSetStblz*.cpp`) y el **fichero** `/mnt/FILE_IS_%04x.dat`
existen en los **tres** firmwares → la diferencia está en la capa de cámara, no en el driver.
Salvedad S130 §4: se mezclan versión de firmware y modelo.

## Línea del obturador

**Negativo verificado**: 0 menciones de obturador/lectura/`rolling` en las 17 trazas, y **0
apariciones de `rolling` y `readout` en toda la A6000 fw3.21** (0 también en la A7S). Lo
único enlazado con el disparo: el callback **`IS_LensMountExpStartCB`** (exposición empezada)
y la programación de la **rejilla del EIS desde `Sync_EndExpose`** (`0x43702dac` llamado en
`0x4354a97c`, en `[CAMERA_MAIN_SYNC]`). Dos datos diferenciales fuera del módulo: el
**A6300** tiene la API **`GetImagerStabilizationTime`** (`0x43d9ce7f`) y el texto
**`position num in rolling is strange %d`** (`0x43d9fe03`), **ambos ausentes** en la A6000
fw3.21 y en la A7S fw3.20.

> **Corrección (S168, 22-10-2026)**: el texto del *rolling* del A6300 es una **cadena MUERTA**
> (0 referencias de código, 0 punteros absolutos, 0 pares `movw`/`movt`; control cruzado con un
> método inverso independiente) → **no** demuestra que el A6300 fw2.01 implemente *rolling
> shutter*. `GetImagerStabilizationTime` sí es una API viva, pero **no se ha analizado** aquí.
> El único código vivo de esa banda de `.rodata` es el cálculo de ancho del **número de posición
> del VD** (`0x4372914c`). Ver `analysis/s168_a6300_rolling/`.
>
> **S51 (A/B/C = NO) se mantiene.**

## NO VERIFICADO / abierto

Fichero fuente propio del módulo (**no embebido**); significado de `upm_get_hcrn_ura` y de las
siglas `AS`/`DIST`; significado de las `u16` `ctx+0xbd8`/`ctx+0xbda`; destino físico de
`SetStblzGridH`; formato binario completo de `FILE_IS_%04x.dat`; tabla de registro de los
callbacks (no hay punteros absolutos a las 4 funciones sin llamadores `bl`).

Informe completo: [`analysis/s164_camera_is/camera_is.md`](../analysis/s164_camera_is/camera_is.md) ·
Datos: `analysis/s164_camera_is/camera_is.json` · Tests: `tests/test_s164_camera_is.py`.
