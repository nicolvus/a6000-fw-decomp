# Retorno de la grabación y `SetImageWrited` (sesión 12)

Corrección S29: [flujo WriteStill completo](s29-writestill-end-to-end.md).
SetImageWrited es `0x6108/0x1007`, tabla `0x101f838 → 0x939dd8`,
no `0x1009`. `WriteStill` responde `0x3500/0x10000004`; `0x3002` corresponde
a la ruta Execute. Los parámetros `0x10000011/12` son UniqueId y el `0x1000`
del grupo es CaptureId. Estas correcciones prevalecen sobre el texto histórico.

ELF de `libObj.so` fw 3.21 (Ghidra = ELF + 0x10000). Estático. Orden reconstruido del lado de `Execute`; el lado MPR/Pool solo parcialmente.

## 1. Secuencia en `Execute` (VERIFICADO, decompilado)

1. Pide `ImageSize/Quality`, resuelve medio (`0x910e1c`), arma `PinStateMgr`.
2. `0x90a810` reserva áreas; `0x90ad20` ejecuta `MprIf::EncodeStill`.
3. Envía `ObjMsg(0x2008,0x1000)` al Pool (`0x912b4c`) = **`RegisterImage`** (orden de Pool `0x1007`, función `0x9328b4`). El Pool responde `0x1003` = `uniqueId`, `0x100c` = flag.
4. Prepara en paralelo una respuesta `0x3500` con `0x10000008` (ExifMemInfo), `0x10000009` (bloque 0xBC) y `0x1000000A` (modelo 0x11 B).
5. Si `MediaMgr+0x2C != 4`: `0x90f698` pide `StillInfo` (0x6B0 B) al Pool por `captureId`/`uniqueId` y llama a `RecordStill` (`0x908afc`) → `MprCtrl::WriteStill` (`0x8fe0a0`): `MprIf::WriteStill(WriteStillParam×n 0x40 B, StillInfo, n)`, espera un semáforo y devuelve un bloque de 0x48 B de resultado.
6. Tras `RecordStill`: `0x910f28(mgr,&id,1,…)` y un bucle `do { 0x9105cc(mgr, MprCtrl, &flag, …) } while (flag != 0)` hasta que el flag se pone a 0 (espera de cierre).
7. Si el item `0x1045` (0x40 B) existe y no hubo error: `0x8fef48(MprCtrl, slot, 1, 1, cadena)`.
8. Liberación: `0x90f5b0`, `0x910524`/`0x910a70`, `0x9157e4(… 0x58 …)`, `0x919690` y, con `bVar2`, `0x90fec8`/`0x90ff8c`; libera también los handles de entrada con `DmmCloseAndFree` en las ramas de error.
9. Respuesta final `ObjMsg(0x3500,0x3002)` con `0x1001` = código de resultado y `0x100f` = 0x28 B de info de contenido, enviada por `vtable[+0xc]` de `this+0x18`.

## 2. Ruta alternativa: `ObjStillRecorderCore::WriteStill` (orden `0x10000003`, ELF `0x909a84`) (VERIFICADO)

Cadenas: `[WriteStill] UniqueId[%d]`, «UniqueId/CaptureId/CapDate/GpsInfo/RepresentativeImageInfo/StillRecCtrlInfo is not set». Lee `captureId` (`0x10000011/12`), `0x1000` (uniqueId), `0x1001` (fecha 10 B), `0x1007` (GPS 0x90 B), `0x1008` (2 B), `0x100e` (8 B), arma `WriteStillParam` (0x40 B ×n), pide `StillInfo` al Pool (`0x90f698`) y llama a `MprCtrl::WriteStill` (llamador `0x90a172`). No codifica: **escribe una imagen que ya está en el Pool** (registrada por un `RegisterImage` anterior). Solo hay dos llamadores de `MprCtrl::WriteStill`: `RecordStill` (`0x908d9c`) y este (`0x90a172`).

## 3. `SetImageWrited` (ELF `0x932a44`)

- VERIFICADO: es el manejador de la orden de Pool **`0x1009`** (fila `0x101f844`, función `0x939dd9`). Recibe `uniqueId` (`0x1003`), llama a `0x931c94` (marca la imagen como escrita en `ImageMgr`) y luego `0x93cab0` (sobre el gestor de contenidos del Pool) y vacía imágenes liberables (`0x93203c`/`0x93caf4`).
- VERIFICADO: el cliente `PoolWrap` de esa orden (`ObjMsg(0x6108,0x1009)` con ítems `0x1002`, `0x3001`, `0x1003`, `0x5002`) está en `0x8fc538`/`0x8fc62e`, invocado desde objetos-comando de `MprAcsr` (`0x8fd3b0`, `0x8fd498`, `0x8fd4b4`).
- **Corrección de sesión 11:** `0x6108/0x1009` **no** es «obtener StillInfo»; es `SetImageWrited`. El cliente que entrega `StillInfo` a `Execute` NO se ha re-identificado por id; NO VERIFICADO qué orden de Pool usa.
- NO VERIFICADO: quién emite `SetImageWrited` (¿`libmpr` tras `FeaCore::WriteStill`, o `MprAcsr` en `libObj`?). Solo `libObj.so` contiene la cadena `SetImageWrited`.

## 4. Orden Pool/MPR (INFERENCIA)

`RegisterImage` (antes de grabar) → `WriteStill` de MPR (confirma por semáforo) → `SetImageWrited` (después, marca el contenido como escrito y libera referencias) → respuesta `0x3500/0x3002`. No se ha demostrado que `SetImageWrited` se emita antes o después de la respuesta `0x3500`.

## 5. ¿Aparece en reproducción? (NO VERIFICADO)

Falta: (a) quién registra la entrada DCF en el índice de MPR (`DCFStillWriter`), (b) la relación `PreRegisterDcfContentSync` ↔ `PreRegisterImage` del Pool. Solo se puede afirmar que, si `WriteStill` termina sin error, el flujo nativo continúa con `SetImageWrited` y la respuesta `0x3500`.
