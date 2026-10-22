# S174 — el API de mensajes «…ForLiro» del `libObj.so`: 216/221/240 nombres, 0/0/6 soportados (y una advertencia metodológica)

> Hito de la **línea de ingeniería inversa general** con valor directo para la **línea del
> obturador electrónico**. Solo lectura de bytes del **`libObj.so`** (capa *camera-user*) de la
> **A6000 fw3.21**, la **A7S fw3.20** y el **A6300 fw2.01**.

## 1. Resumen / veredicto

El `libObj.so` contiene, en su conversor de mensajes `CamMsgConv`, una **lista de nombres de
mensaje `…ForLiro`** (de la capa *camera-user* hacia la capa LIRO). El resultado es doble:

1. **Hecho diferencial**: el A6300 fw2.01 **soporta 6** de esos mensajes; la A6000 fw3.21 y la
   A7S fw3.20 **no soportan ninguno** (0).

   | firmware | nombres `…ForLiro` | en mensajes de **SOPORTE** | en mensajes de **RECHAZO** |
   |---|---|---|---|
   | A6000 fw3.21 | **216** | **0** | 216 |
   | A7S fw3.20 | **221** | **0** | 221 |
   | A6300 fw2.01 | **240** | **6** | 234 |

   Los 6 soportados por el A6300 son `SetApertureSTFForLiro`, `SetAutoDualRecModeForLiro`,
   `SetExpandFocusAfModeForLiro`, `SetMountAdapterFocusTypeForLiro`, `SetPowerStatusForLiro` y
   `SetVolpfModeForLiro` — **ninguno de ellos es del obturador**.

2. **Advertencia metodológica (la más importante del hito)**: en la A6000 y la A7S, **los 216 y
   221 nombres `…ForLiro` aparecen todos dentro de mensajes de RECHAZO**
   (`… NON SUPPORTED MsgID[0x%04x]…`). Es decir, **la presencia del nombre de un mensaje NO
   prueba que la cámara lo soporte**: `SetSilentShutterModeForLiro`, `SetShutDriveForLiro`,
   `SetFrontEShutterModeForLiro`, `SetIrisDriveForLiro` y `SetDriveModeForLiro` están en el
   `libObj.so` de la **A6000**… **rechazados**.

   → Cualquier lectura del tipo «la A6000 conoce el mensaje de obturador silencioso, luego
   tiene la función» es **incorrecta**. Lo que decide es la **capa LiroSeq de `av-cam.bin`**
   (S169), donde la A6000 no tiene los campos `sc_ShutDrive`, `front_eshutter`,
   `SilentShutterMode` ni `shutterType`.

## 2. Cómo se verificó

La clasificación es **exacta**, no por proximidad: el formato del mensaje de error es
`… ERROR!!!  <Nombre> NON SUPPORTED MsgID[0x%04x]#####` y el de soporte
`… ERROR!!!  <Nombre> SUPPORTED MsgID[0x%04x]#####`, de modo que se comprueba que el nombre va
**seguido literalmente** de ` NON SUPPORTED MsgID` o de ` SUPPORTED MsgID`.

* A6000 fw3.21: `NON SUPPORTED MsgID` **222**, `SUPPORTED MsgID` (sin «NON») **0**.
* A7S fw3.20: **227** y **0**.
* A6300 fw2.01: **241** y **6**.

## 3. La familia del obturador en los tres firmware

| mensaje `…ForLiro` | A6000 | A7S | A6300 | en la A6300 |
|---|---|---|---|---|
| `SetShutDriveForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetShutDriveModeForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetShutLowLimitForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetSilentShutterModeForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetFrontEShutterModeForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetIrisDriveForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetDriveModeForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| `SetMovieAutoSlowshutModeForLiro` | sí (rechazado) | sí (rechazado) | sí (rechazado) | — |
| **`SetShutterTypeForLiro`** | **0** | **0** | **1** (rechazado) | — |

**Matiz**: la A6000 y la A7S **no** tienen `SetShutterTypeForLiro` (0/0/1), pero **sí** tienen
las demás mensajes de la familia del obturador… **rechazados**. El único miembro de la familia
que el A6300 añade es el **tipo de obturador**.

## 4. Los 25 nombres que el A6300 añade (y el 1 que la A6000 añade)

| solo en el A6300 (24) | | solo en la A6000 (1) |
|---|---|---|
| `SetApertureSTFForLiro` | `SetPowerStatusForLiro` | `SetStepzoomModeForLiro` |
| `SetAutoDualRecModeForLiro` | `SetRingFocusDirectionForLiro` | |
| `SetExifInfoForLiro` | `SetRingZoomDirectionForLiro` | |
| `SetExpandFocusAfModeForLiro` | `SetRingZoomModeForLiro` | |
| `SetFlickerModeForLiro` | `SetS1SteadyShotModeForLiro` | |
| `SetIntervalRecAEModeForLiro` | `SetShutterTypeForLiro` | |
| `SetMRProfileDataLoadRequestForLiro` | `SetStandardExposureSettingForLiro` | |
| `SetMRProfileDataSaveForLiro` | `SetSteadyShotAdvancedMovieForLiro` | |
| `SetMotionShotModeForLiro` | `SetSteadyShotAdvancedStillForLiro` | |
| `SetMountAdapterFocusTypeForLiro` | `SetSteadyShotHighForLiro` | |
| `SetStillEEHiSpeedFrameRateModeForLiro` | `SetVolpfModeForLiro` | |
| `SetVignettingPreventionForLiro` | `SetZoomAssistModeForLiro` | |
| `SetZoomAssistRangeForLiro` | | |

La A7S añade 5 respecto de la A6000 (`SetMRProfileDataLoadRequestForLiro`,
`SetMRProfileDataSaveForLiro`, `SetMotionShotModeForLiro`, `SetRingZoomDirectionForLiro`,
`SetS1SteadyShotModeForLiro`).

## 5. Coherencia con S169 y con la línea del obturador

* **Coherencia con S169**: los nombres `…ForLiro` son el **otro extremo** del camino
  *camera-user* → LIRO; el **parámetro** que los transporta vive en la capa LiroSeq de
  `av-cam.bin`, donde la A6000 no tiene `sc_ShutDrive` / `front_eshutter` /
  `SilentShutterMode` / `shutterType`. Los dos datos **concuerdan**: el A6300 es el único con
  el parámetro *y* el único con el mensaje `SetShutterTypeForLiro`.
* **Lo que este hito NO dice**: que la A6000 pueda disparar con obturador electrónico. El
  `libObj.so` es una capa de *mensajería*, no una implementación.
* **Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.** La ausencia estática no demuestra
  incapacidad del hardware; la prueba física sigue pendiente de autorización.

## 6. Regla metodológica que deja este hito

> **La presencia de una cadena no prueba una funcionalidad.** En este repo hay ya tres casos
> del mismo tipo: la cadena del *rolling shutter* del A6300 **muerta** (S168), el bloque de 128
> bytes de `0x43dcfa9e` **sin referencias** (S172) y ahora los nombres `…ForLiro` de la A6000
> **todos en la lista de rechazo**. Antes de afirmar que una cámara «tiene» algo por el mero
> hecho de que su binario contenga su nombre, hay que comprobar que el nombre está **usado**.

## 7. Salvedad metodológica (heredada de S130 §4)

El A6300 es de otra **generación de plataforma** (LIRO/CXD): con los tres blobs disponibles **no**
se puede separar «nuevo en el fw2.01» de «propio de la plataforma».

## 8. NO VERIFICADO / abierto

1. Por qué el `CamMsgConv` de la A6000 y la A7S **no soporta ninguno** de los 216/221 mensajes
   `…ForLiro` (¿otra ruta de conversión? ¿mensajería por `TYPE_PARAM`?).
2. Qué gana exactamente el A6300 con los 6 mensajes soportados.
3. Si los mensajes `…ForLiro` rechazados en la A6000 se envían por otro camino (p. ej. una
   tabla de `MsgID` → manejador).
4. El resto de los mensajes `SUPPORTED MsgID` del A6300 que no son `…ForLiro` (6 de 247).

## 9. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s174_forliro_api.py -q
```

## 10. Revisión del agente principal

_(vacía)_
