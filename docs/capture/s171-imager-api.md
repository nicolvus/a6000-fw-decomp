# S171 — la API del imager y el canal «SteadyShot» del objetivo

> Hito de la **línea de RE general** con valor para la **línea del obturador electrónico**.
> Solo bytes: `av-cam.bin` de la A6000 fw3.21, la A7S fw3.20 y el A6300 fw2.01.

## Veredicto

Tres diferencias de **superficie de API** entre el A6300 fw2.01 y la A6000 fw3.21 / A7S fw3.20,
las tres verificadas por bytes y relevantes para la estabilización:

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| nombres de API del imager (`Get/Set*Imager*`) | **4** | **4** | **7** |
| → `GetImagerStabilizationTime` | 0 | 0 | **1** |
| → `SetImagerFrameSize` (traza `SetImagerFrameSize[%d]`) | 0 | 0 | **1** |
| → `SetImagerMode` (firma C++) | 0 | 0 | **1** |
| clase `Camera::Sync::SyncUtilityUpm` | 0 | 0 | **3** |
| tipo `Camera::Imager::IMAGER_DRIVEMODE` | 0 | 0 | **2** |
| `SteadyShot` (cualquier grafía) | **0** | **0** | **11** |
| `SteadyShotInfo` (canal del objetivo) | **0** | **0** | **7** |
| `Mount_DividedInfo` (módulo que lo contiene) | 5 | 3 | 5 |

Los cuatro nombres comunes: `GetImagerDriveMode`, `GetImagerTemperature`,
`GetImagerTemperatureAD` y `GetPrelightImagerDriveMode` (este último, el `drive_mode` del
imager de **S134**).

## `GetImagerStabilizationTime` (solo A6300)

Cadena `GetImagerStabilizationTime Request Error` `0x43d9ce7f`, **viva** con **1** sitio PIC
(`ldr 0x43718d02`, pool `0x43718d14` = `0x00684177`, `add r0,pc` `0x43718d04`, logger
`0x43986518`). El manejador (`0x43718cd8`) **suma** los `count` bytes de una tabla en
`base + 3·índice + 0x25a` (count en `+0x258`) y devuelve `(suma + 2) & 0xFF`; con la tabla
vacía avisa («Request Error») y devuelve 0. **NO VERIFICADO**: qué magnitud devuelve (el
nombre viene de la tabla de API, no del código).

## El canal «SteadyShot» del objetivo (solo A6300)

Las 7 apariciones de `SteadyShotInfo` están en el **driver de la montura (BL)**: el objetivo
manda su información de estabilización al cuerpo y el cuerpo la recibe en dos callbacks
(`CallBack_SteadyShotInfo_Com_1st` y `_2nd`), con `Mount_DividedInfo_SteadyShotInfo.cpp`
como fichero.

**Matiz**: el módulo que lo contiene (`Mount_DividedInfo`) **existe en los tres** firmware
(5/3/5); lo exclusivo del A6300 es la **variante `SteadyShotInfo`**. La A6000 **no** carece de
estabilización (tiene el subsistema IS/EIS de **S164**): lo que le falta es **este canal del
objetivo** y la entrada de API `GetImagerStabilizationTime`.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** Son diferencias de **firmware**; la
ausencia estática de una API no demuestra incapacidad del hardware.

Informe: [analysis/s171_imager_api/imager_api.md](../../analysis/s171_imager_api/imager_api.md) ·
test: `tests/test_s171_imager_api.py` (20 tests).
