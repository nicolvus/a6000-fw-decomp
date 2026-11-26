# FILM-PB-1 — sub-catálogo: origen del «0:02» y qué mira la guarda de contenido

27-11-2026, todo estático (cámara no accesible). **Espacios**: libObj y libmpr en **VA del ELF (base 0)**; en libmpr
REA = ELF + `0x10000` (`0x437BC0` = `FUN_00447BC0`). Ficheros: fw 3.21 `.../nflasha15_unpacked_unpacked/lib/`; bytes
citados en `reports/evidence/film-pb-1-sub-catalogo-20261127/`.

## 1. CORRECCIÓN: `m_durationOfContent` NO está en modelo+0x108

`0x432240` es el volcado de test `M_SinglePbBase::ActionTestCmdDebugPrint` (`0xCC9EFC`, nombre `0xCC9CEC`); recibe
el modelo en r4 y llama a cada bloque con su base: `0x432282-0x432288` = `add.w r0,r4,#0x530` · `adds r0,#4` ·
`bl 0x40E950` ⇒ **base PbTimeInfo = modelo+0x534**; `0x43228C-0x432290` = `add.w r0,r4,#0x90` · `bl 0x40E85C` ⇒
base PbStatus = modelo+0x90. `0x40E85C` imprime `[r4+0x60/0x64/0x68/0x6C]` = `m_pbStatusMode/Level/FinalMode/
FinalLevel` (`0xCC0700/0xCC0744/0xCC0788/0xCC07CC`) ⇒ modelo+0xF0..0xFC es **estado**, no tiempos. `0x40E950` es
el volcado de tiempos y lee, respecto de su `this` (= modelo+0x534):

| Campo | Offset bloque | **VA en el modelo** | Formato (`.rodata` libObj) |
|---|---:|---:|---|
| `m_pbTimeInContent` (h,m,s) | `0x60/0x64/0x68` | **0x594 / 0x598 / 0x59C** | `%02d:%02d:%02d` `0xCC0852` |
| `m_pbTimeInTotal` | `0x6C/0x70/0x74` | 0x5A0 / 0x5A4 / 0x5A8 | `0xCC08A2` |
| **`m_durationOfContent`** | `0x78/0x7C/0x80` | **0x5AC / 0x5B0 / 0x5B4** | `0xCC08F2` |
| `m_durationOfTotal` | `0x84/0x88/0x8C` | 0x5B8 / 0x5BC / 0x5C0 | `0xCC0942` |
| `m_currentFrameInContent/InTotal` | `0x90/0x94` | 0x5C4 / 0x5C8 | `0xCC0992/0xCC09D6` |
| `m_framesOfContent/OfTotal` | `0x98/0x9C` | **0x5CC** / 0x5D0 | `0xCC0A1A/0xCC0A5E` |

Typeinfo que confirman los bloques: `…19StreamAttributeInfoE` (`0xCC060C`; bloque modelo+0x108, volcado `0x40F1FC`),
`…12PbStatusInfoE` (`0xCC0654`), `…10PbTimeInfoE` (`0xCC27B8`); PbTimeInfo ocupa 0x534..0x5EF (el volcado
siguiente usa modelo+0x5F0). **La lectura futura del contador debe usar 0x594 (posición) y 0x5AC (duración).**

## 2. Quién escribe `m_durationOfContent` (modelo+0x5AC)

Barrido completo de `.text` de libObj (11 430 428 B con re-sincronización Thumb; 910 968 accesos memoria
indexados por registro+offset):
1. **Único escritor**: el inicializador `0x812436` (`str.w r2,[r0,#0x5ac]`) y la tanda `0x81248C-0x8124D8` que pone
   a cero 0x590..0x5D8 (`magic 0x05001033` en `[r0+0x4d4]`). No hay otro `str` a `[rX,#0x5ac/0x5b0/0x5b4/0x594…]`
   ni existe `add.w rX,rY,#0x534` (sólo el idiom `#0x530`+`adds #4` del volcado): sólo una **copia de bloque**
   (`memcpy`/`ldm-stm`) puede escribirlo sin que este barrido lo vea.
2. **El catálogo no lo alimenta**: `MprIf::GetMovieContentProperty` sólo se llama desde el envoltorio genérico
   `0x7258F8` (PLT `0xDFE30`), y éste sólo desde `0x75F34A` y `0x763A20`, funciones de test/volcado (buffer de
   0x10000 B, logs de nivel 11). Además **libObj no importa** `GetContentDuration` ni `GetMovieContentDuration`.
3. La única vía de datos de película en la capa de objetos es `MprIf::GetMovieMediaInfo` (PLT `0xE10C0`, API
   `0x41000022` → `0x4517FC`), llamada en `0x83B230`, `0x8CAA5A`, `0x8D551C`, `0x8F95CE`; en `0x8CAA5A` el
   resultado se reenvía al reproductor como mensaje (`GetParam(0x21,0x28)`), no se copia al modelo.

**NO_VERIFICADO** qué deja el valor final en 0x5AC; dos caminos vivos: (a) nadie lo escribe ⇒ 0x5AC = 0 y el «0:02»
es otra magnitud; (b) copia de bloque desde `MPR::MovieMediaInfo`.

## 3. Qué comprueba la guarda «Detect UnSupported Content» (`0x437C3C`)

| VA (libmpr) | Hecho verificado |
|---|---|
| `0x437BEE-0x437BFA` | guarda A: `0x447A1E(id=[core+0x1EC], media=[core+0xDC0], mask=[core+0xDB8])` |
| `0x437C10-0x437C2C` | guarda B: `0x447F26(r0=id, r1=[core+0xDC0], r2=msg[0], r3=msg[4], pila=msg[8..0x14])` |
| `0x447F26` | `0x447810(id,media,&ent)`; si falla ⇒ `r0=1` (**fail-open**: se da por soportado) |
| `0x66D0C8` | `ent = (*(mediaObj+0x24))->vtable[6]()` (`ldr r0,[r0,#0x24]; ldr r3,[r0]; ldr r3,[r3,#0x18]; blx r3`) |
| `0x447F52-0x447F5A` | `ldr r4,[vt,#0x58]` · `blx r4` con `this=ent` y 6 palabras |
| `0x447A38/0x447A4C` | misma entidad: `vtable+0x60()` y `vtable+0x5C(kind)`, `kind∈{6,8,0x10,0x20,0x80,0x100,0x200}` |

Los 6 argumentos de `vtable+0x58` son `msg[0x00..0x14]` (el `EntryId` y palabras reservadas de la cabecera del
mensaje `0x4000001D`), **no** el `PlayMovieCtrl` de `msg+0x64`: la guarda identifica el contenido por `EntryId` y
pregunta «¿es reproducible?». La entidad se fija con la máscara en `0x437A4E/0x437A52` (prepare, desde
`param[0]`/`param[4]`) y se borra en `0x437B64/0x437B68` (stop); su familia de slots (`+0x58` contenido, `+0x5C(kind)`,
`+0x60()`) es una interfaz de **capacidades/formato**: nunca se le pasa una duración.

**NO_VERIFICADO** qué clase implementa `vtable+0x58`. Resultado negativo del método: 108 tablas de punteros en
`.data.rel.ro` de libObj con slots `0x58/0x5C/0x60` resueltos vía `.rel.dyn` (81 993 relocaciones); ninguna de las
inspeccionadas implementa el par `0x5C(kind)`/`0x60()` de la guarda A. Siguiente paso: partir de la construcción de
la entidad en `MprIf::EnterMoviePb` (`0x7231B0` → API `0x40000017` → `0x44F2F4`) y leer allí `vtable[0x58]`.

## 4. ¿Puede venir de una base de datos de la tarjeta? Sí: este firmware la tiene
`xavcIfo_MediaProfile` / `xavcIfo_DbIf` (cadenas `.rodata` `0x944E00-0x945FD0`):

| Evidencia (VA libmpr) | Contenido |
|---|---|
| `0x947D02` `0x947D1C` `0x94E528` | `\PRIVATE\M4ROOT\MEDIAPRO.XML`, `…\MEDIAPRO.BAK`, `…\STATUS.BIN` (+ `CUEUP.XML`) |
| `0x9450C0-0x9450F1` | `.\CLIP\C0001.MP4` · `.\SUB\S01.MP4` · `M01.XML` · `R01.BMI` · `.\THMBNL\T01.JPG` |
| `0x945E2B/0x945E68` | raíz XML: `xmlns="http://xmlns.sony.net/pro/metadata/mediaprofile"` `version="2.10"` |
| `0x945C76` `0x945C71` `0x945C3C` | atributo **`dur`**, log **`Copy dur`**, atributo `videoType` |
| `0x9458FF-0x945984`, `0x945CA9` | tabla `AVC_<res>_<MP|HP>@L<level>`; `XML has inconsistency`, `videoType is invalid` |
| `0x775540-0x7755BA` + pool `0x7755BC` | manejadores de atributo → destinos `r5+0x60/0x68/0x84/0x8C/0xB0` del registro de clip |

⇒ **Sí existe un campo de duración por clip**: el atributo `dur` de `MEDIAPRO.XML` (con `ch:`, `aspectRatio:`,
`umid:`, `mainStreamFileName:` del registro de clip, `0x9456B9-0x9456CF`; `STATUS.BIN` aporta `STATUS_INDEX_INVALID/
VACANT`). `AVF_INFO` aparece una sola vez en libmpr (`0x7A637F`) **dentro de la tabla de nombres de mensajes**
(`AVF_INFO\0Unknown Message ID\0…`), no como ruta: no hay evidencia de que sea un fichero de esta cámara.
**NO_VERIFICADO**: la unidad de `dur` y el contenido real de `PRIVATE/M4ROOT/MEDIAPRO.XML` del caso.

## 5. Por qué «0:02» — hipótesis ordenadas por evidencia
Datos: 9,5095 s = 285 cuadros a 29,97 fps (0x11D) = 9 509 ms (0x2525); 2 s ≈ **60 cuadros**.
- **H1 (la que más apoya el código): el «0:02» es el tiempo en contenido, no la duración.** `modelo+0x5AC`
  (duración) no tiene escritor (§2) mientras `modelo+0x594` (posición) se mueve y se siembra con el *resume*; 2 s =
  60 cuadros es un punto de reanudación típico. libObj usa `GetContentResumePoint` (`0x7267FA`, `0x8CAE60`) y
  `SetContentResumePoint` (`0x7269CE`, `0x8CB4B2`) en la ruta de película, y la guarda B tiene el efecto lateral
  «ResumeInfo is updated».
- **H2: manda la DB de la tarjeta.** Si `MEDIAPRO.XML` tuviera la entrada con `dur` ≈ 60 (o quedó de un clip de 2 s)
  la cámara mostraría 0:02. En contra: `PRIVATE/M4ROOT/CLIP` está **vacío** ⇒ la DB no tiene registro de clip y no
  puede aportar 2 s; a favor: el módulo existe y la BD de imágenes gobierna la reproducción de películas.
- **H3: error de escala.** 9 509 ms / 4096 = 2,32 ⇒ «0:02», sin evidencia de una escala 1/4096 en el código.
- **Descartadas aritméticamente**: truncamiento a 8/16 bits (0x2525, 0x011D: ningún corte da 2); 1/30 s leído como
  s (285 → 4:45); ms leídos como s (9 509 → 2:38); campo del MP4 (ya descartado).

## 6. Receta de reparación a nivel de fichero (si la DB es la fuente)

1. Copia íntegra de la tarjeta antes de tocar nada (los MP4 están en `MP_ROOT/100ANV01`, `103ANV01`).
2. Inspeccionar en orden: `PRIVATE/M4ROOT/MEDIAPRO.XML` (¿un `<clip>` por MP4 con `uri="./CLIP/…"`, `dur`,
   `videoType`, `fps`?) → `MEDIAPRO.BAK` → `CUEUP.XML` → `STATUS.BIN` → `CLIP/` (`M01.XML`, `R01.BMI`) → `SUB/`,
   `THMBNL/`. Anotar `dur` y `videoType` de cada entrada: es el dato que falta.
3. Si la BD está vacía, obsoleta o inconsistente: **renombrar** (no borrar) `MEDIAPRO.XML`, `MEDIAPRO.BAK`,
   `CUEUP.XML`, `STATUS.BIN` y los `.XML`/`.BMI` de `CLIP/`, encender y ejecutar **Menú → Recuperar BD imág.**, que
   es lo que promete la cadena del firmware («Recovers the image database file for movies…»): la cámara reconstruye
   la BD recorriendo los MP4 de `MP_ROOT`.
4. Nunca borrar ni mover los `.MP4`; no tocar `AVCHD/` ni otros directorios. Si tras regenerar sigue el 0:02, la DB
   queda descartada y hay que leer en RAM `modelo+0x594` frente a `modelo+0x5AC` para decidir H1.

## 7. Límites
- **NO_VERIFICADO** el escritor de `m_durationOfContent` más allá del inicializador (falta buscar `memcpy`/`ldm-stm`
  con destino al bloque, o medirlo en RAM).
- **NO_VERIFICADO** qué clase implementa `vtable+0x58`; sí están verificados sus argumentos, el contrato (0 = no
  soportado) y el fail-open de `0x447810`. **NO_VERIFICADO** también la unidad de `dur` de `MEDIAPRO.XML`.
- Reproducibilidad: desensamblado local (Capstone 5) de los ELF 3.21 (SHA-256 libmpr `9a74a3bb…4c30`, libObj
  `8e8a937a…5b6a`) con `.dynsym`/`.rel.plt`/`.rel.dyn`; sin ejecutar firmware ni abrir la cámara.
