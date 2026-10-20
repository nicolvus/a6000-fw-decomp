# S20 (Claude): quién crea las topologías 0xae–0xb4 y 0xcb–0xcd, GetPin(6) de ObjScalar y CamUser::SequenceStillCaptureStart

Alcance: análisis estático de `libObj.so` fw3.21 (direcciones ELF). Se reutilizan el desensamblado
`llvm-objdump` existente, la RTTI de `analysis/session20/evidence/libobj-rtti-vtables.json` y
`libBizFw-rtti-vtables.json`, y la tabla `analysis/topology-table-libobj.json`. No se tocó la línea
`libmpr.so` de Codex. Evidencia estructurada: `analysis/session20/evidence/claude-topology-ae-b4-sequence.json`.
SilentShutter **no** se declara funcional.

## 1. Creadores de las topologías del objeto 53

**VERIFICADO (formato):** `createTopology` (`0x420630`) recibe en `r2` una lista `u32` de ids de
fila **terminada en 0**. El bucle está en `0x418956–0x41895e`. `destroyTopology` (`0x420656`)
usa el mismo formato. Las listas se localizaron resolviendo las 146 414 referencias PC-relativas
(`ldr rX,[pc]` + `add rX,pc`) del desensamblado.

Cada fila del obj 53 sustituye a una fila directa Camera→destino, y lo hace solo en variantes `SCALAR_*`
de los modelos (identificadas con `IdGenerator::Get("model/…")`):

| Filas | Sustituye a | Creador | Condición | Clasificación |
|---|---|---|---|---|
| `0xae`,`0xaf` (Camera YC#0→53 in0→Effect in0) | `0x0a` | `ModelCamera` init `0x4acc70` (vslot48), lista en `this+0x84`; create `0x4ae6d4`/destroy `0x4ae720` | `model/SCALAR_CAMERA`: `[9,ae,af(,9e)]` frente a la normal `[9,a(,9e)]` | VERIFICADO |
| `0xb0`,`0xb1` (Camera STILL_DATA#0→53→StillRecorder) | `0x08` | `ModelStillRec` init `0x6943fc` (vslot48), lista en `this+0xdc`; create `0x699bd4`/destroy `0x699c32` | `model/SCALAR_STILL_REC`: `[b0,b1,10]` frente a la normal `[8,10]` | VERIFICADO |
| `0xae–0xb3` | — | `ModelScalar`, despachador vslot68 `0x649ef8`: acción 7 → create(`0x101`) y acción 8 → destroy(`0x102`) | lista `0xd44550` `[ae,af,9,10,b0,b1,b2,b3]` | VERIFICADO |
| `0xb2`,`0xb3` (obj12→53 in1→Effect in4) | — | `ModelScalarPb` (`0x65a720`/`0x65a740`) | lista `[b2,b3,7,5,6]` | VERIFICADO (el propietario se deduce por la cercanía de su vtable) |
| **`0xb4`** (53 YC out2→StillRecorder in0, StsId 6) | — | `ModelScalarPb` vslot68 → `0x65b0bc` → `0x65a8a4`: lista en heap `[r6, 0xb4, 0]`, create id `0x109` (`0x65a95e`) | `r6` es la fila que encaja con la plantilla `0xd4627c` {REC_CNT_INFO, src=obj11 out0, dst dinámico} | VERIFICADO (literal y create); INFERENCIA (semántica de `r6`) |
| `0xcb`,`0xcc` (Camera YC#1→53 in3→Effect in1, StsId 2) | `0x0b` | `ModelMovieRec` `0x5f76d4` (vslot68) | `model/SCALAR_MOVIE_REC` ("CreSc"): `[cb,cc,e,f]` frente a la normal `[b,e,f]` | VERIFICADO |
| `0xcd` (53 out0→obj0) | — | `ModelMovieRec` `0x5f6bb4` (create `0x2f`) | `SCALAR_MOVIE_REC`: `[9d,cd,43,1,ad,b5]` frente a la normal `[9d,1,ad,b5]` | VERIFICADO (la lista); INFERENCIA (que las filas con destino 0 sean sumideros nulos) |

- **VERIFICADO:** ninguna lista estática contiene `0xb4`. Su único creador localizado es el dinámico de `ModelScalarPb`.
- **INFERENCIA fuerte:** los modelos `SCALAR_*` son la variante PMCA/Scalar (`com.sony.scalar.*`,
  ruta P). ObjScalar (obj 53, categoría `0x3a49` fijada en `0x3ace8a`) se intercala en Live View, en la
  captura de still (STILL_DATA) y en vídeo cuando el modelo activo es la variante Scalar.
- **Uso en captura de still:** sí, pero solo por **STILL_DATA** (`0xb0/0xb1`, `ModelStillRec`
  `SCALAR_STILL_REC`), no por YC. El YC de ObjScalar hacia el recorder (`0xb4`) solo aparece en
  `ModelScalarPb`, que es reproducción o edición basada en ticket.
- **Corrección parcial a S14 (VERIFICADO):** "no hay topología Scalar → StillRecorder en YC" es
  falso: existe `0xb4` y su creador es `ModelScalarPb`. Que `ModelScalarStillRecPatch` sea mínimo no
  cambia.

## 2. Qué es el GetPin(6) de S14

- **VERIFICADO:** `ObjScalar+0x4c` es un `GlobalAccessor`. Su vtable en `libBizFw.so` tiene
  `+0xc SetPinInfo(BizObjPin*,int)`, `+0x10 GetPinInfo(int)` y `+0x2c SetObjCategoryID`.
- **VERIFICADO:** el helper `0x3aca58` crea 10 `BizObjPin` (`+0x68..+0x8c`) y los registra en
  `0x3ace08..0x3ace7e` con estos índices: `0–3` YC in#0..3, `4–7` YC out#0..3, `8` STILL_DATA in#0,
  `9` STILL_DATA out#0.
- **VERIFICADO (sitio):** en `0x3d2fae` se ejecuta `[seq+0x14]->vtbl[+0x10](6)`, es decir `GetPinInfo(6)`.
  Luego viene `pin->vtbl[+0x10](0x1002, msg 0x2001/0x1027)`.
- **Conclusión (INFERENCIA fuerte):** GetPin(6) = **PIN_YC out#2** de ObjScalar, que es el origen de la
  fila **`0xb4`** → StillRecorder in0 (StsId 6). Concuerda con S14, donde el manejador `0x919ca0` del
  recorder recibe `0x1027`. El único eslabón no verificado es que `seq+0x14` sea ese mismo accessor.

## 3. CamUser::SequenceStillCaptureStart (vslot1 `0xa3b63c` → `0xa3b650`)

**VERIFICADO:** el getter de pin es `0xa15fb4` → `0xad422c`, que devuelve `*(holder+0x58+4·idx)`.
Los pines de ObjCamera se crean en `0x987de0..0x987eb0` en este orden: `0–3` YC#0..3,
`4` STILL_DATA#0, `5` SOUND#0, `6` CAMERA_STATUS#0, `7–8` YC#4..5.

| # | Sitio | Pin | Clave de Send | Mensaje (cat/id) | Notas |
|---|---|---|---|---|---|
| 1 | `0xa3b8d0` | 4 STILL_DATA | 0x1003 | `0x2008/0x1003` | parámetro `0x1009` |
| 2 | `0xa3ba9e` | 6 CAMERA_STATUS | 0x1003 | `0x200a/0x100c` | anidado `0x3100/0x8553` {0x9526,0x9527} |
| 3 | `0xa3bb2c` | 4 | 0x1003 | `0x2008/0x1001` | |
| 4 | `0xa3bc22` | 6 | 0x1003 | `0x200a/0x101b` | anidado `0x3100/0x8599` {0x9735,0x9736} |
| 5 | `0xa3bd10` | 4 | 0x1003 | `0x2008/0x1002` | |
| 6 | `0xa3c3ba` | 4 | **0x1002** | `0x2008/0x1000` | |
| 7 | `0xa3c460` | 4 | 0x1003 | `0x2008/0x1004` | |
| 8, 9 | `0xa3c4d8`, `0xa3c662` | 6 | 0x1003 | `0x200a/0x1003` | ramas distintas |
| 10, 11 | `0xa3c9b4`, `0xa3ca5a` | 0 YC#0 | **0x1002** | `0x2001/0x1002` | {0x1009, 0x1008, `0x130f`=true, `0x1322`} |
| 12 | `0xa3cc56` | 6 | 0x1003 | `0x200a/0x100b` | anidados `0x3100/0x85d2`, `0x3100/0x8509` |

- **VERIFICADO:** los 12 envíos usan solo 3 pines: STILL_DATA#0 (6 envíos), CAMERA_STATUS#0 (4) y YC#0 (2).
  Ninguno usa YC#1..5. Además se construyen unas 22 `ObjMsg(0x3100, 0x85xx)` internas de cámara; solo
  3 viajan anidadas en mensajes de pin.
- **INFERENCIA:** con `ModelStillRec` normal, STILL_DATA#0 llega al StillRecorder por la fila `0x08`. Con
  `SCALAR_STILL_REC` llega primero a ObjScalar (`0xb0`) y de ahí sigue por `0xb1`. YC#0 llega a Effect
  (`0x0a`), o a ObjScalar (`0xae`) con `SCALAR_CAMERA`.
- **NO_VERIFICADO:** el significado de los ids `0x1000–0x1004` (STILL_DATA), `0x100b/0x100c/0x101b/0x1003`
  (CAMERA_STATUS) y `0x2001/0x1002`, y el de la clave de Send `0x1002` frente a `0x1003`.

## Impacto sobre E2 y el veredicto

- E2 gana **coherencia estática**. El pin de ObjScalar que S14 dejaba sin destino (GetPin(6)) está
  cableado por la fila `0xb4` al StillRecorder, y existe un modelo que crea esa fila.
- E2 **no gana uso en disparo**. `0xb4` solo lo crea `ModelScalarPb` (reproducción/edición con ticket),
  y `0x1027` sigue siendo "armar + eco" (S14). En el disparo Scalar (`SCALAR_STILL_REC`), ObjScalar solo
  se intercala en STILL_DATA, no en YC.
- La interposición Scalar en Live View y en still refuerza la ruta **P** (PMCA/CameraSequence) como
  camino del firmware, sin mostrar obturador electrónico.
- **Veredicto sin cambios: A > E > P ≈ E2.** SilentShutter no se declara funcional.

## Siguiente paso

1. Decompilar `0x65b0bc`/`0x65a8a4` (`ModelScalarPb`): qué mensaje dispara la acción y quién es el
   destino dinámico de la fila REC_CNT_INFO.
2. Comprobar qué hace ObjScalar con STILL_DATA in#0 → out#0 en `SCALAR_STILL_REC`: si es un relevo puro
   o si puede reinyectar datos.
3. Semántica de los mensajes `0x2008/0x1000–0x1004`, cruzando con el manejador de STILL_DATA del
   StillRecorder.

Límites: el propietario de `0x65a720/0x65a740/0x5f6bb4` se fija por proximidad de vtable o llamador.
Las listas construidas en heap con ids no literales siguen fuera del alcance de este barrido.
