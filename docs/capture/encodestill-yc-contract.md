# Contrato YC de EncodeStill — sesión 13

> **Actualización S30:** servicio efectivo y retorno recuperados:
> `0x55001f` InfraAvbbc→`0x550123` InfraStillEncoder→`0x56000f` SDF,
> mensaje efectivo `0x2000/4`. MprAcsr espera completion y Execute libera
> las entradas al terminar. Se retiran las afirmaciones históricas de
> receptor desconocido y de espera no localizada; formato/planos/pitch y
> caché del YC de captura siguen abiertos. [Detalle S30](s30-pipelines-capture-encode.md).

Alcance: análisis estático. Direcciones ELF (Ghidra = ELF + 0x10000). Datos en `analysis/encodestill-yc-contract.json`. Decompilado base: `analysis/ghidra/libobj-100b-prod.json` (0x91ad20 Ghidra = ELF `0x90ad20`) y `libmpr-feaif-encodestill.json`.

## Resultado

`EncodeStill` **no recibe formato de píxel, stride ni submuestreo.** Recibe un `RegionInfo` de 0x40 B con dos descriptores de buffer (`dec` y `yc`), color de fondo, lienzo, región, rango Y y colorimetría. El formato está implícito en el *tipo de unidad* DMM/SDS y en el lienzo. Por eso la compatibilidad de un YC de Live View no se decide por ningún campo de formato, sino por el tipo de unidad y las dimensiones.

## RegionInfo (0x40 B) — VERIFICADO

Fuentes: pila de `0x90ad20`, volcador `MprIfLog::EncodeStill` (ELF `0x727718`) y copia de 16 palabras en `FeaIf::EncodeStill` (ELF `0x44f834`).

| Off | Tam | Campo |
|---|---|---|
| 0x00 | 4 | `dec.unitType` |
| 0x04 | 2 | `dec.unitHandle` (u16 DMM) |
| 0x08 | 4 | `dec.unitPhyAddr` |
| 0x0c | 4 | `dec.offset` (0) |
| 0x10 | 4 | `dec.size` = suma de extents del DMM |
| 0x14 | 3 | `outBgColor` Y,Cb,Cr |
| 0x17 | 1 | `b_isEnableLayout` |
| 0x18 | 4 | `canvasRectSize` {w,h} u16 |
| 0x1c | 4 | `regionLayout` {left,top} |
| 0x20 | 4 | `regionLayout` {width,height} |
| 0x24 | 4 | `yc.unitType` |
| 0x28 | 2 | `yc.unitHandle` |
| 0x2c | 4 | `yc.unitPhyAddr` |
| 0x30 | 4 | `yc.offset` (0) |
| 0x34 | 4 | `yc.size` = suma de extents |
| 0x38 | 4 | `outputYRange` (0/1) |
| 0x3c | 4 | `colorimetry` (0..3) |

`0x38` y `0x3c` salen del orden de la pila (VERIFICADO el orden, no el nombre exacto del campo en `libmpr`).

## EncodeStillParam (8 palabras)

`RegionInfo*`, `T_LTM*` (fecha, 10 B), `SQuality` (copia de `this+0x130`), tres `targetSize` (de `UtilStillSize`), `StillMetaAreaInfo*` (0x18 B), `JpgInfo*` (tabla `0x100b` convertida a 12 B/entrada). El orden Main/Thumb/Scn de los tres `targetSize` NO está verificado.

## Validaciones reales en Execute (0x90ad20)

| Qué | Error | Estado |
|---|---|---|
| `0x1018` presente y handle abre (DmmOpen por contexto) | `0xacc` / `0xab2` | VERIFICADO |
| colorimetría ∈ {0,1,2,3} | `0xae8` | VERIFICADO |
| rango Y ∈ {0,1} | `0xb02` | VERIFICADO |
| `0x1032` presente y handle abre | `0xb34` / `0xb1a` | VERIFICADO |
| `0x1034`, `0x1035`, `0x1036` presentes; si flag: `0x1038`, `0x1037` | `0xb44…0xb7f` | VERIFICADO |
| `UtilStillSize::GetStillTargetSize(modo==Pbcap, w/h región, this+0x130,…)` verdadero | `7` | VERIFICADO (función); tablas NO decodificadas |
| medio ≠ None y ranura válida | ver `pool-write-completion.md` | VERIFICADO (sesión 12) |

**No hay** validación de formato, stride, alineación, submuestreo ni orientación en esta capa.

## Preguntas del encargo (1–15)

1. **`unitType`**: tipo de unidad del gestor de memoria (MMGR). INFERENCIA: unidad SDS de YC (`inputYcSdsUnitType`, `outputYcSdsUnitType` en `InfStillEncoder/InfDecoder`). Valores numéricos NO verificados.
2. **`physTopAddr`**: dirección física base de la unidad (campo `unitPhyAddr`). VERIFICADO el campo; semántica exacta (¿base de extents?) INFERENCIA.
3. **DMM/SDS/física**: handle DMM (u16) + tipo + dirección física a la vez. VERIFICADO que se transportan los tres.
4. **Formatos YC aceptados**: no se declaran; dependen del tipo de unidad. NO VERIFICADO.
5. **Planos Y y C**: NO VERIFICADO (implícito).
6. **Submuestreo**: NO VERIFICADO. (La tabla del baseband de libmpr muestra una columna `Y:Cb:Cr`, no analizada.)
7. **Stride**: no existe como campo. NO VERIFICADO si se deriva del canvas.
8. **Alineación**: no se valida en esta capa. NO VERIFICADO en FEA.
9. **Tamaño de buffers**: `size` = suma de extents del DMM; no se compara con canvas×bpp en esta capa.
10. **Canvas y región**: canvas {w,h} u16 obligatorio; región/layout solo si flag. VERIFICADO.
11. **Colorimetría**: 0..3 (601, 709, XV709, Adobe por el volcador). INFERENCIA de los nombres.
12. **Rango Y**: 0/1. VERIFICADO.
13. **Orientación**: no entra por `EncodeStill`; la fija la ruta de escritura (`rotateDegree` en `SendDeliverToConverter`). INFERENCIA.
14. **Sincronización/caché**: `FeaIf::EncodeStill` envía un mensaje a un servicio FEA y espera (vtable `+0x20`). NO VERIFICADO la coherencia de caché.
15. **Propiedad y liberación**: Execute abre y cierra el handle al preparar; libera solo la correspondencia de salida. El productor conserva el YC (ObjRenderer libera `YCC_CAP` en su orden Stop). NO VERIFICADO si FEA lee el YC después de volver.

## Dónde está el codificador

`MprCtrl 0x8fe6f8 → MprIf::EncodeStill (0x71cf58) → MprIfLog → FeaIf::EncodeStill (0x44f834)`, que empaqueta y envía el mensaje a un servicio FEA. El codificador real **no** está en `libObj` ni en `libmpr`; el parámetro equivalente en `InfStillEncoder` envía `MSG_ID_SDF_ENCODE_JPEG` al SDF (el mismo motor de LIRO). Que FEA use SDF es INFERENCIA.

## Tamaños

Las cadenas `DefStruct::PBCAP_SIZE_1920_1080 / 640_360 / 640_480` indican los tamaños de PbCap; su relación con el canvas que recibe `Execute` NO está verificada. Las cinco reservas de salida (`0x173762`, `0x84d6d`, `0x50d17`, `0x170d0c`, `0x170d0b`) no se pueden asignar todavía a los seis descriptores activos.

## NO VERIFICADO

Valores de `unitType`, disposición de planos, coherencia de caché, lectura asíncrona de FEA, orden Main/Thumb/Scn, contenido de `StillMetaAreaInfo` y del bloque `0xBC`.

## Corrección sesión 14
- Las cinco «reservas de salida (bytes)» (`0x173762`, `0x84d6d`, `0x50d17`, `0x170d0c`, `0x170d0b`) son **tipos de unidad DMM** (argumento de `DmmAccess::DmmAllocate/AllocateAndOpen(uint)`; todas existen en `kmod/dmm.ko`). Ver `yc-unit-types-and-layout.md`.
- Valores de `unitType` de PbCap: `dec=0x50b3f` (1920×1080) / `0x243`, `yc=0xe0b00`; hay además una cabecera SDS de 0x800 B con colorimetría/yRange (`0x1072/0x1073`). El PlayData producido por ObjEffect añade `0x1033` (u32 0), `0x1019/0x101a` (w,h) y `0x100a=2` (`analysis/yc-pin-delivery-flow.json`).
- `EncodeStill` es asíncrono (fin por `CBID_ENCODE_STILL`): ver `fea-encodestill-buffer-lifetime.md`.
