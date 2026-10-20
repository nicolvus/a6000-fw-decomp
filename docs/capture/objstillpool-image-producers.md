# Productores de imagen del Pool (sesión 12)

Alcance: análisis estático de `libObj.so` fw 3.21. Direcciones ELF salvo que se indique; VA Ghidra = ELF + 0x10000. Contrato de bytes en `analysis/objstillpool-100b-layout.json`.

## 1. Resultado central (VERIFICADO)

`ObjStillRecorder::Execute` (ELF `0x90b248`, orden `0x10000005`) **no recibe JPEG ya hechos**. Recibe un **frame YC** en DMM y hace tres cosas:

1. **Reserva** las áreas de salida (`0x90a810`): 5 búferes DMM vacíos (`0x173762`, `0x84d6d`, `0x50d17`, `0x170d0c`, `0x170d0b` B) y rellena la tabla de 11 descriptores de 16 B (`0x100b`).
2. **Codifica** (`0x90ad20` → `MprCtrl` `0x8fe6f8` → `MprIf::EncodeStill`): MPR produce JPEG principal, miniatura, screennail y maker note dentro de esas áreas. El volcador de MPR (`[MprAcsr] EncodeStill`) imprime la entrada (`decBufferInfo`, `ycBufferInfo`, colorimetría, `yRange`, `SQuality STD/FINE/EXFINE`, `targetSizeMain/Thumb/Scn`, `PublicMakerNote`, `RecDate`, `JpgInfo (Input)`) y la salida (`JpgInfo (Cmp)`).
3. **Registra** en el Pool: envía `ObjMsg(0x2008,0x1000)` con `0x1000` (captureId), `0x1001/0x1002` (fechas), `0x1006` (CamInfo 0x88 B), `0x1007` (GPS 0x90 B), `0x100b` (tabla 0xB0), `0x100e` (8 B), `0x1012` (8 B). Luego `RecordStill` (`0x908afc`) → `MprCtrl::WriteStill`.

Esto **corrige** la lectura de sesiones 10–11 (los `0x100b` serían «componentes ya existentes»): son áreas de salida que MPR rellena.

## 2. Traza del productor a los campos de `0x100b`

| Paso | Función | Evidencia |
|---|---|---|
| Orden de entrada | despachador `0x9162d0` (`GetMessageId-0x10000003`, tabla `tbb`, índice 2) y callback `0x90d7e8`; fila de registro en `.data.rel.ro` `0x101f128` (id `0x10000005`) | desensamblado + tabla de datos |
| Contenedor de entrada | `GetParam(msg,0x10000006,0x29)` → `0x1017`, `0x1031`, `0x1041` | decompilado Execute |
| `0x1017` (PresentationInfo del PlayData) | `0x1018` = 12 B {u16 memHandle, u32 unitType, u32 physTopAddr} = `ycBufferInfo`; `0x1072` colorimetría (0..3: 601/709/XV709/Adobe); `0x1073` yRange (0..1) | `0x90ad20` + volcador `PrintPlayDataParam` (ELF `0x906984`) |
| `0x1031` | `0x1032` = `decBufferInfo` (mismo triple 12 B); `0x1034` 3 B (YCbCrColor); `0x1035` flag layout; `0x1036` canvas (w,h u16); `0x1038` región (w,h); `0x1037` layout (left,top) | idem |
| `0x1041` | `0x1042` ExifMemInfo (0x18 B: handle + tipo + phys); `0x1043` GPS 0x90 B; `0x1044` CamInfo 0x88 B; `0x1045` 0x40 B; `0x1046` fecha 10 B | Execute + volcador |
| Reserva de salidas | `0x90a810` | decompilado completo |
| Codificación | `0x90ad20`: abre YC con `DmmOpen`, suma `GetExtSizeFromDmmAlloc`, calcula tamaños con `UtilStillSize` (`0x826080`), llama a `0x8fe6f8` (`MprIf::EncodeStill`) | decompilado |
| Envío al Pool | `0x912b4c` | desensamblado |

Mapas de claves de `0x1017/0x1031/0x1041` por **orden de campos del volcador**: INFERENCIA fuerte (las claves aparecen en el mismo orden que las cadenas).

## 3. ¿Entra la imagen al grabador desde la notificación de captura o por registro previo?

- VERIFICADO: Execute tiene como única fuente de imagen un handle YC del mensaje de la orden. `SeqStillCap` libera `ycc_freeze` y `sds_ycc_freeze` (`us_UnitHandle`) en sus ramas de error, es decir, **maneja esos YC**; es coherente con que sean los que se pasan en `0x1017`.
- NO VERIFICADO: quién construye y envía la orden `0x10000005` (no hay llamadores directos; solo filas de registro). Tampoco cómo se relaciona con el `StillInfo.jpg_info` de LIRO (`mainJpg`…): Execute no lo consume.
- Distinguir: `0x1006` de la notificación LIRO (mensaje de captura) ≠ ítem `0x1006` (CamInfo) del mensaje al Pool. Execute lee `0x1044` y lo reenvía como `0x1006`.

## 4. `ImageMgr::PreRegisterImage` (ELF `0x931e14`)

- VERIFICADO: único llamador directo `0x933154`, que es el manejador de la orden del Pool **`0x1017`** (fila de registro `0x101f908`, función `0x939d19`).
- Lee del mensaje: `0x1003` (uniqueId), `0x1008` (captureId), `0x4001/0x4002` (u16), `0x100c` (flag), `0x4005` (10 B, fecha).
- Crea un registro de 0x138 B **sin búferes**: reserva `uniqueId`↔`captureId` y responde `0x1003` (id) y `0x1004` (16 B de `0x94c6cc`). Es una reserva (el nombre `MprIf::PreRegisterDcfContentSync` en la misma librería indica que se reserva la entrada DCF antes de escribir).
- NO equivale a `RegisterImage`; no contiene imagen. NO VERIFICADO si `RegisterImage` exige un `PreRegister` previo.
- NO VERIFICADO quién la envía (cliente `PoolWrap` en `0x8fc864`, invocado por objetos-comando de `MprAcsr`, `0x8fd794`).

## 5. Evaluación para una imagen de origen electrónico

- Un JPEG de SFRA **no sirve** como entrada de Execute: `EncodeStill` solo acepta YC (`ycBufferInfo`/`decBufferInfo`).
- Sí se podría registrar en el Pool un JPEG propio si se aportaran las 11 entradas con handles/offset/size válidos, pero faltarían miniatura, screennail, maker note y EXIF source (entradas 0,1,4,9,10) y esas las produce MPR, no SFRA.
- Camino con evidencia: dar a `Execute` un frame YC de Live View (handle + unitType + phys + canvas) y que MPR haga el resto. Requisitos NO VERIFICADOS: formato YC admitido, sender de la orden, `MediaMgr` fuera de `None`, estado de MPR.

## Sesión 13 — corrección sobre el remitente
- Se sustituye «remitente NO VERIFICADO» (§3): `0x10000005` no viaja entre objetos; lo crea el recorder en `0x919f1a` al recibir un `PlayData` por su pin YC. El remitente real del flujo es `MSGID_RECORD_IMAGE_CMD` (`0x3500/0x3001`) desde `ModelPbCap`/`ModelPaint`/Mcmd. Ver `encodestill-command-origin.md`.
- Contrato de entrada detallado en `encodestill-yc-contract.md` (RegionInfo 0x40 B).

## Corrección sesión 14
- Las «5 reservas de salida» de `0x90a810` son tipos de unidad, no tamaños en bytes (ver `yc-unit-types-and-layout.md`). El productor del `PlayData` es ObjEffect (`objhandover-2a-topology.md`).
