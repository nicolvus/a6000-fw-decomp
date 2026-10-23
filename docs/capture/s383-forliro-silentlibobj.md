# S383 — Mensajes `…ForLiro` y SilentShutter en libObj.so (A6000 fw3.21)

## 1. …ForLiro en libObj.so (base: S174)

| Firmware | Nombres `…ForLiro` | En mensajes de SOPORTE | En mensajes de RECHAZO |
|---|---|---|---|
| A6000 fw3.21 | 216 | 0 | 216 |
| A7S fw3.20 | 221 | 0 | 221 |
| A6300 fw2.01 | 240 | 6 | 234 |

**Los 6 del A6300:** `SetApertureSTFForLiro`, `SetAutoDualRecModeForLiro`, `SetExpandFocusAfModeForLiro`, `SetMountAdapterFocusTypeForLiro`, `SetPowerStatusForLiro`, `SetVolpfModeForLiro` — ninguno del obturador.

## 2. Nombres del obturador en A6000 — TODOS rechazados

Los siguientes nombres de la familia del obturador aparecen en `libObj.so` de la A6000 **dentro de mensajes de RECHAZO** (`… <Nombre> NON SUPPORTED MsgID[0x%04x]…`):

- `SetSilentShutterModeForLiro`
- `SetShutDriveForLiro`
- `SetFrontEShutterModeForLiro`
- `SetIrisDriveForLiro`
- `SetDriveModeForLiro`

**La presencia de la cadena NO prueba soporte.** Todos están rechazados en la capa `libObj.so` (camera-user).

## 3. Qué decide el soporte: capa LiroSeq de `av-cam.bin`

La decisión real está en `av-cam.bin` (capa del núcleo de cámara), no en `libObj.so`. La A6000 **no tiene** los campos:
- `sc_ShutDrive`
- `front_eshutter`
- `SilentShutterMode`
- `shutterType`

El único miembro de la familia del obturador que el A6300 añade es `SetShutterTypeForLiro` (0/0/1).

## 4. Efecto en S51

**NINGUNO.** S51 sigue A=NO, B=NO, C=NO. No hay ruta de exposición electrónica demostrada.

## 5. Búsqueda adicional en libObj.so (esta sesión)

Se verificó en `libObj.so` de la A6000:
- No hay strings "NON SUPPORTED" adicionales más allá de las 216 ya catalogadas en S174
- No hay nuevas cadenas de obturador electrónico más allá de las 5 listadas arriba
- Los nombres `…ForLiro` aparecen como datos de string (en .rodata), no como llamadas de función

**Evidencia:** `docs/capture/s174-forliro-api.md`, barrido de strings en `libObj.so` (esta sesión).
