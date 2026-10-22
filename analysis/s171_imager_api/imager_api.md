# S171 — la API del imager y el canal «SteadyShot» del objetivo: el A6300 tiene 3 entradas y 1 canal más que la A6000

> Hito de la **línea de ingeniería inversa general** con valor para la **línea del obturador
> electrónico**. Solo bytes: `av-cam.bin` de la **A6000 fw3.21**, **A7S fw3.20** y **A6300
> fw2.01**. Convención: `vaddr = 0x43541000 + file_offset`. Regla de referencias: **estricta**
> (canónica del repo), con los mapas globales en `analysis/s106_imaging_cap/pic_refs_strict_global.json`
> (A6000, 17 525 destinos) y `analysis/s169_drive_api/pic_refs_strict_a6300.json` /
> `_a7s.json` (A6300 20 001; A7S 16 638).

## 1. Resumen / veredicto

Tres diferencias de **superficie de API** entre el A6300 fw2.01 y la A6000 fw3.21 / A7S fw3.20,
las tres **verificadas por bytes** y **relevantes para la estabilización**:

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| nombres de API del imager (`Get/Set*Imager*`) | **4** | **4** | **7** |
| → `GetImagerStabilizationTime` | 0 | 0 | **1** |
| → `SetImagerFrameSize` | 0 | 0 | **1** |
| → `SetImagerMode` | 0 | 0 | **1** |
| clase `Camera::Sync::SyncUtilityUpm` | **0** | **0** | **3** |
| tipo `Camera::Imager::IMAGER_DRIVEMODE` | **0** | **0** | **2** |
| traza `SetImagerFrameSize[%d]` | **0** | **0** | **1** |
| `SteadyShot` (cualquier grafía) | **0** | **0** | **11** |
| `SteadyShotInfo` (canal del objetivo) | **0** | **0** | **7** |
| `Mount_DividedInfo` (módulo que lo contiene) | 5 | 3 | 5 |

Los cuatro nombres comunes son `GetImagerDriveMode`, `GetImagerTemperature`,
`GetImagerTemperatureAD` y `GetPrelightImagerDriveMode` (este último, el `drive_mode` del
imager de **S134**).

Los tres nombres «extra» del A6300 **no son entradas de tabla sino texto real**:
`SetImagerMode` aparece dentro de la **firma C++**
`void Camera::Sync::SyncUtilityUpm::SetImagerMode(Camera::Imager::IMAGER_DRIVEMODE)`
(`0x43daf786`), es decir de una **clase de utilidad de sincronización del imager**
(`Camera::Sync::SyncUtilityUpm`, 3 apariciones) con su **tipo enumerado**
`Camera::Imager::IMAGER_DRIVEMODE` (2 apariciones); y `SetImagerFrameSize` aparece en la traza
`SetImagerFrameSize[%d]` (`0x43daccdd`). Ni la clase, ni el tipo, ni la traza existen en la
A6000 fw3.21 ni en la A7S fw3.20 (0/0).

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** Son diferencias de **firmware**; la
ausencia estática de una API no demuestra incapacidad del hardware.

## 2. `GetImagerStabilizationTime` (solo A6300)

* Cadena: `GetImagerStabilizationTime Request Error` `0x43d9ce7f`, **viva** con **1** sitio
  PIC: `ldr 0x43718d02` (pool `0x43718d14` = `0x00684177`) + `add r0,pc` `0x43718d04`, que
  llama al logger `0x43986518`.
* El manejador (función que envuelve ese `add`, prólogo en `0x43718cd8`) es:

```
0x43718cde: adds   r3, r0, r1           ; base + indice
0x43718ce0: ldrb.w r4, [r3, #0x258]     ; numero de elementos (byte)
0x43718ce4: movs   r3, #0
0x43718ce6: mov    r2, r3
loop:
0x43718cea: add.w  r5, r1, r1, lsl #1   ; 3*indice
0x43718cee: adds   r5, r0, r5
0x43718cf0: adds   r5, r5, r3
0x43718cf2: adds   r3, #1
0x43718cf4: ldrb.w r5, [r5, #0x25a]     ; byte de la tabla
0x43718cf8: adds   r2, r2, r5
0x43718cfa: uxtb   r2, r2
0x43718cfc: cmp    r3, r4
0x43718cfe: blt    loop
0x43718d00: b      #0x43718d0c          ; si count == 0 -> error
0x43718d02: ldr    r0, [pc, #0x10]      ; "GetImagerStabilizationTime Request Error"
0x43718d04: add    r0, pc
0x43718d06: bl     #0x43986518
0x43718d0a: movs   r2, #0
0x43718d0c: adds   r2, #2
0x43718d0e: uxtb   r0, r2
0x43718d10: pop    {r3, r4, r5, pc}
```

Es decir: **suma** los `count` bytes de una tabla situada en `base + 3·índice + 0x25a` y
devuelve `(suma + 2) & 0xFF`; si la tabla está vacía avisa («Request Error») y devuelve 0.

**NO VERIFICADO**: qué magnitud devuelve (el nombre viene de la **tabla de API**, no del
código de la función), qué es la tabla de `+0x25a` y quién la escribe. La A6000 **no** tiene
esta entrada, luego no hay equivalente con el que comparar.

## 3. El canal «SteadyShot» del objetivo (solo A6300)

Las 7 apariciones de `SteadyShotInfo` del A6300 están en el **driver de la montura (BL)**:

| cadena | dirección | sitio PIC |
|---|---|---|
| `[BL]STEADYSHOTINFO_COM_STATE is INIT in VSYNC at Mount_DividedInfo_SteadyShotInfo.cpp %d` | `0x43da45b1` | `0x4374eb60` |
| `[BL]MOUNT_ERR RECEIVE DATA error : %x in CallBack_SteadyShotInfo_Com_1st` | `0x43da460a` | `0x4374ec40` |
| `[BL]MOUNT_ERR CHECK RECEIVE DATA ERR CommandId[%d] in CallBack_SteadyShotInfo_Com_1st` | `0x43da4653` | `0x4374ec5c` |
| `[BL]MOUNT_ERR RECEIVE DATA SIZE error : %ld in CallBack_SteadyShotInfo_Com_2nd` | `0x43da46aa` | `0x4374ecf2` |
| `[BL]MOUNT_ERR in CallBack_SteadyShotInfo_Com_2nd : the receive data is ...` | `0x43da46f9` | `0x4374ed44` |
| `[BL]MOUNT_ERR RECEIVE DATA error : %x in CallBack_SteadyShotInfo_Com_2nd` | `0x43da477b` | `0x4374ed5e` |
| `[BL]MOUNT_ERR RECEIVE DATA ERR CommandId[%d] in CallBack_SteadyShotInfo_Com_2nd` | `0x43da47c4` | `0x4374ed6c` |

Es un **canal de información de estabilización entre el objetivo y el cuerpo**: el objetivo
(«SteadyShot» es la marca de Sony para su estabilización) envía su estado al cuerpo y el
cuerpo lo recibe en dos\columnwidth (`_Com_1st` y `_Com_2nd`).

**Matiz importante**: el módulo que lo contiene (`Mount_DividedInfo`) **existe en los tres**
firmware (5/3/5 apariciones del nombre); lo **exclusivo del A6300** es la variante
`SteadyShotInfo` (0/0/7). Es decir: **no es que la A6000 carezca del driver de la montura**
(ya visto en S66/S133), es que **no tiene este canal de estabilización del objetivo**.

Las otras 4 apariciones de `SteadyShot` son propiedades de la capa `LiroSeq` de **S169**:
`CheckSetFrameLockOnSteadyShot` `0x43dc5494` (sitio `0x438c7672`),
`CheckSetSteadyShotAdvancedStill` `0x43dca7b7` (6 sitios `0x438c891c`–`0x438c8996`),
`CheckSetS1SteadyShotMode` `0x43dca8b5` (`0x438c887e`) y
`CheckSetSteadyShotAdvancedMovie` `0x43dcabd7` (6 sitios `0x438c89f4`–`0x438c8a6e`).

## 4. Salvedad metodológica (heredada de S130 §4)

La comparación mezcla **versión de firmware** y **modelo de cámara** (el A6300 es de otra
generación de plataforma, LIRO/CXD). Con los tres blobs disponibles no se puede separar
«nuevo en el fw2.01» de «propio de la plataforma del A6300».

## 5. Qué NO se afirma

- **NO** se afirma que la A6000 carezca de estabilización: tiene el subsistema IS/EIS de
  **S164** (`rcct_SetStblzPower`, `rcct_SetStblzGridH`, giroscopio, `FILE_IS_%04x.dat`).
  Lo que falta es **el canal «SteadyShot» del objetivo** y **la entrada de API
  `GetImagerStabilizationTime`**.
- **NO** se afirma qué devuelve `GetImagerStabilizationTime` (el nombre viene de la tabla de
  API, no del código).
- **NO** se ha seguido el canal `SteadyShotInfo` más allá de los callbacks de recepción.
- **NO** se ha comparado el **formato** del paquete `SteadyShotInfo` con el de la A6000
  (no existe allí).

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s171_imager_api.py -q
```

## 7. Revisión del agente principal

_(vacía)_
