# S174 — el API de mensajes «…ForLiro» del `libObj.so`: 216/221/240 nombres, 0/0/6 soportados

> Hito de la **línea de RE general** con valor directo para la **línea del obturador electrónico**.
> Solo bytes del `libObj.so` (capa *camera-user*) de la A6000 fw3.21, la A7S fw3.20 y el A6300 fw2.01.

## Veredicto (doble)

**1) Hecho diferencial.** El conversor de mensajes `CamMsgConv` del `libObj.so` conoce
**216 / 221 / 240** nombres de mensaje `…ForLiro` (A6000 / A7S / A6300) y **soporta 0 / 0 / 6**:

| firmware | nombres `…ForLiro` | en mensajes de **SOPORTE** | en mensajes de **RECHAZO** |
|---|---|---|---|
| A6000 fw3.21 | **216** | **0** | 216 |
| A7S fw3.20 | **221** | **0** | 221 |
| A6300 fw2.01 | **240** | **6** | 234 |

Los 6 del A6300: `SetApertureSTFForLiro`, `SetAutoDualRecModeForLiro`,
`SetExpandFocusAfModeForLiro`, `SetMountAdapterFocusTypeForLiro`, `SetPowerStatusForLiro` y
`SetVolpfModeForLiro` — **ninguno del obturador**.

**2) Advertencia metodológica (lo más importante del hito).** En la A6000 y la A7S, **los 216 y
221 nombres `…ForLiro` aparecen todos dentro de mensajes de RECHAZO**
(`… <Nombre> NON SUPPORTED MsgID[0x%04x]…`). **La presencia del nombre NO prueba soporte**:
`SetSilentShutterModeForLiro`, `SetShutDriveForLiro`, `SetFrontEShutterModeForLiro`,
`SetIrisDriveForLiro` y `SetDriveModeForLiro` **están** en el `libObj.so` de la A6000…
**rechazados**.

Lo que decide es la **capa LiroSeq de `av-cam.bin`** (S169), donde la A6000 **no** tiene los
campos `sc_ShutDrive`, `front_eshutter`, `SilentShutterMode` ni `shutterType`. Mensaje
(`libObj.so`) y parámetro (`av-cam.bin`) **concuerdan**: solo el A6300 tiene ambos.

El único miembro de la familia del obturador que el A6300 añade es
**`SetShutterTypeForLiro`** (**0/0/1**); el A6300 añade **25** nombres `…ForLiro` en total y la
A6000 añade **1** (`SetStepzoomModeForLiro`).

## Regla que deja este hito

> **La presencia de una cadena no prueba una funcionalidad.** Tres casos ya en el repo: la cadena
> del *rolling shutter* del A6300 **muerta** (S168), el bloque de 128 bytes de `0x43dcfa9e`
> **sin referencias** (S172) y ahora los nombres `…ForLiro` de la A6000 **todos rechazados**.

**Efecto en S51: NINGUNO — S51 sigue A=NO, B=NO, C=NO.**

Informe: [analysis/s174_forliro_api/forliro_api.md](../analysis/s174_forliro_api/forliro_api.md) ·
test: `tests/test_s174_forliro_api.py` (17 tests).
