# S20 — Herramienta RTTI/vtables y avances en P3 (pin YC de Camera) y objeto 53

Prioridad baja desbloqueada con herramienta propia. **No se instaló nada**: Python
stdlib + `llvm-objdump`/`llvm-readelf`/`llvm-nm`/`c++filt` ya presentes.

## Herramientas nuevas (scripts/)

- `rtti_vtables.py lib.so out.json` — recupera clases C++ (RTTI Itanium) y vtables
  vía relocaciones `R_ARM_RELATIVE`/`R_ARM_ABS32`. Autocomprobación: todo `_ZTI`/`_ZTV`
  exportado debe coincidir (superada). `libObj.so`: 3278 clases, 3536 vtables,
  14786 métodos virtuales atribuidos.
- `func_owner.py dis rtti.json lib.so [--calls SIM] [addr…]` — función contenedora
  (inicios = vtables ∪ destinos `bl` ∪ exports; 53782 inicios en `libObj.so`).
- `pin_signatures.py lib.so dis rtti.json out.json` — firma de pines (tipo, índice,
  dirección) declarada por cada función vía constructores `ObjPin`/`BizObjPin`/`UObjPin`.
  Control positivo: el helper ya conocido de ObjCamera (`0x987dc6`) da exactamente sus
  9 salidas.

## P3 — pin YC de Camera

- **VERIFICADO**: la topología numera pines **por tipo**. ObjCamera (obj 8) declara
  `CAMERA_STATUS#0`, `SOUND#0`, `STILL_DATA#0`, `YC#0..#5` (9 pines).
- **VERIFICADO**: existen 9 clases `CamUser::PinParser*` (una por pin: `CameraStatusOut0`,
  `SoundOut0`, `StillDataOut0`, `YcOut0..5`), no documentadas antes. La clase real es
  `CamUser::ObjCamera` (vtable `0x1021078`).
- **VERIFICADO**: "Camera.out0" de la fila `0x0a` es `PIN_YC#0`. Su parser
  `CamUser::PinParserYcOut0` (método `0xa279c8`) es un relevo de mensajes de categoría
  `0x2001` (=PIN_YC en `m_pinTbl`) que maneja `0x1003` (=PlayData, ya documentado) y usa
  parámetros `0x1001..0x1005`, `0x1329..0x132e` (semántica NO_VERIFICADA; seguimiento de
  registros sin distinguir ramas).
- **DESCARTADO**: que `0x98f974` (sitio `Send` de ayer) pertenezca a ObjCamera: está en
  la función no virtual `0x98f770`.
- Nuevas: `CamUser::SequenceStillCaptureStart/Stop/Lock/UnLock` (base `SFW::SequenceBase`);
  `SequenceStillCaptureStart` contiene 12 `ObjPin::Send`. Sin analizar aún.
- Nota de trazabilidad: `m_objTbl`/`m_pinTbl` de `libSysDef.so` **ya estaban extraídas**
  (`analysis/topology-table-libobj.json`); no son hallazgo de esta sesión.

## Objeto 53

- **VERIFICADO**: `ObjScalar_Create` → constructores `0x3ad15c`/`0x3ad20c` (instalan vtable
  `OBJSCALAR::ObjScalar`, log "[ObjScalar]ObjScalar Constructor") → helper `0x3aca58`, que
  declara `YC` in/out `#0..#3` + `STILL_DATA` in/out `#0`.
- **VERIFICADO**: esa firma es la única coincidencia exacta con las entradas/salidas del
  objeto 53 entre las funciones que declaran pines con inmediatos en `libObj.so`,
  `libBizFw.so` y `libBizFw2.so`.
- **INFERENCIA fuerte**: objeto 53 = **ObjScalar**. Límite: objetos que declaran pines con
  argumentos calculados (p. ej. ObjEffect/Renderer/Display, presentes en `libObj.so`) no
  son visibles al extractor.
- **Corrección a `objscalar-playdata-bridge.md` (S14)**: allí se etiquetó "Scalar(30)". La
  firma del objeto 30 (`PB/REC_CNT_INFO`, `SOUND`, `YC#0`) no es la de ObjScalar y coincide
  con el constructor de `ObjDubbing` (`0x85be70`) → INFERENCIA: obj 30 = ObjDubbing. Por tanto
  la afirmación S14 "no hay topología Scalar → StillRecorder en YC" queda **en revisión**:
  si 53 = ObjScalar, la fila `0xb4` (obj53 YC → StillRecorder.in0, StsId 6) lo sería.
- Rol topológico del obj 53 (filas `0xae–0xb4`, `0xcb–0xcd`): interpuesto entre Camera
  (`YC#0`, `YC#1`, `STILL_DATA#0`) y Effect/StillRecorder.

## Impacto en el veredicto

Orden sin cambios (A > E > P ≈ E2), pero **E2 gana evidencia estática** que S14 le negaba.
No demuestra uso en disparo: sigue NO_VERIFICADO qué modelo crea las topologías `0xae–0xb4`.

## Siguiente paso

1. Qué modelo/LifeCycle crea las topologías `0xae–0xb4`/`0xcb–0xcd`.
2. Confirmar qué pin de ObjScalar es el `GetPin(6)` citado en S14.
3. Analizar `CamUser::SequenceStillCaptureStart`.

SilentShutter no se declara funcional.
