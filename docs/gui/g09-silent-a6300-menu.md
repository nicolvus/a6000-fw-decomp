# G09 — Dónde vive el ajuste «Silent Shooting / Shutter Type» del A6300 y qué falta en la A6000 (estático, 07-11-2026)

**Base**: A6300 fw2.01 y A6000 fw3.21 extraídos (`nflasha15_unpacked_unpacked`). **Método**: lectura de bytes/símbolos
(`scripts/gui/setting_nodes.py`, `uxc_strings.py`), REA (`viewUnified2.so` A6300, `CautionConfig.so` A6000). Sin tocar la cámara.
**Objetivo del usuario**: replicar en la A6000 el selector de obturador silencioso del A6300 **sin** perder «EFCS off» (hoy el
electrónico reutiliza el selector EFCS, byte `+0x210`, [E25-24](../capture/e25-24-selector-efcs-electronico.md)).

## 1. Qué trae el menú del A6300 (VERIFICADO)

| Entrada de menú | Etiqueta / ayuda (`string_english`) | Opciones |
|---|---|---|
| **Silent Shooting** | `0xf840` «Silent Shooting» (`0xf846`) / `0xf847` «Suppress operation sounds… to the minimum» | Off `0xf2a1`, On `0xf849` |
| **Shutter Type** | `0xf901` / `0xf93a` «Sets the shutter type when shooting still images» | Auto `0xf912`, Mechanical Shut. `0xf907`/`0xf90d`, Electronic Shut. `0xf927`/`0xf935` |
| e-Front Curtain Shut. (ya en la A6000) | `0xf04e` / `0xe930` | On `0xe95a`, Off `0xe95b` |

Ninguno de estos ids `0xf840–0xf949` existe en `string_english.uxc` de la A6000 (4 360 textos frente a 5 415): habría que **añadirlos** (el editor
`uxc_strings.py` ya reindexa) o reutilizar los existentes de la A6000 (`0xf290` «Silent Shutter Mode», `0xf2a1`).

## 2. Las cuatro capas del ajuste

| Capa | Dónde | A6300 | A6000 |
|---|---|---|---|
| **1. Nodo de ajuste** (etiquetas, opciones, ProcessId) | `lib/CautionConfig.so`, símbolos `cmnViewSettingNode*` / `cmnViewSettingPropertyList*` (`.rodata`) | `SilentShutter` raíz: ProcessId `0x2b`; `CustomStillShutterType` raíz: ProcessId `0x13f`, opciones Auto=0 / Mechanical=1 / Electronic=2 | **Sin nodo real de Silent** (§3). EFCS: ProcessId `0x46` (A6300: `0x4e`), On=0 / Off=1 |
| **2. Elemento de proceso y página de menú** | `viewUnified2/4/7.so`: clases `CmnViewProcessDataElementCustom{SilentShutter,StillShutterType,FrontCurtainShutter}`, `ACT_SilentShutter*` | existen | `CustomFrontCurtainShutter` sí; los de Silent/StillShutterType **no** (150 elementos frente a 248) |
| **3. Camera-user (`libObj.so`)** | secuencias `N7CamUser28SequenceSetSilentShutterMode`, `…SetFrontEShutterMode`; A6300 añade `SequenceSetShutterType`, `pvt_ActionSetShutterType`, `pvt_ChangeShutterTypeParamApp2Obj/Obj2App`, `pvt_ActionNotifyShutterTypeEvt` | las tres | **Silent y FrontEShutter sí** (mensajes `0x768e`→selector LIRO `0x40e3`; `0x75fa`→`0x4099`, [investigación](../capture/shutter-investigation.md)); ShutterType **no** |
| **4. Núcleo (`av-cam.bin`, LiroSeq/CAIF)** | validación `CheckSetShutterType` (`shutterType`, `0x438c8b52`, [S169](../capture/s169-drive-api-a6300.md)); paquete CAIF `pkt[+0x12] \|= 0x20` si `*(cap+0x804)==2` ([S401](../capture/s401-a7s-silent-control-path.md)); `libScalarDaemon`: `setSilentShutterMode`, `s_silentShutterMode` | completo | sin handler de `0x40e3` ni campos `SilentShutterMode`/`shutterType`; sí `0x4099` (EFCS) |

Formato de la capa 1 (`setting_nodes.py`): tripletas `{prop, flag, valor}`; `0`=etiqueta, `6`=ayuda, `0xe`=ProcessId (solo raíz), `0xf/0x10`=valor interno de la opción.

## 3. Corrección: el nodo «SilentShutter» de la A6000 es de SteadyShot

[E007](../silent-shutter-trace.md) y [silent-shutter-status](../capture/silent-shutter-status.md) tomaron `cmnViewSettingNodeRootSilentShutter` de la A6000 por
un nodo de obturador silencioso. Sus propiedades dicen otra cosa (VERIFICADO en bytes, `test_gui_uxc_strings.py`): raíz con etiqueta `0xf199` «SteadyShot», ayuda `0xe589`
«Sets SteadyShot…», On `0xe27c` «Turns on SteadyShot.», Off `0xe27d`, ProcessId `0x26`. Es un resto con nombre engañoso (INFERENCIA: reutilización del símbolo); **no** es un menú
de Silent oculto. En el A6300 el mismo símbolo sí es el de Silent Shooting (etiqueta `0xf840`, ProcessId `0x2b`).

## 4. Cómo replicarlo en la A6000 sin perder «EFCS off» (propuesta, sin implementar)

Principio: **un selector nuevo e independiente del EFCS** (el A6300 también los separa: EFCS `0x4e` y Silent `0x2b` / Shutter Type `0x13f`).

1. **Capa 1**: clonar en `CautionConfig.so` de la A6000 los `PropertyList` del A6300 (Root + opciones) con ProcessId libre y textos propios (`uxc_strings.py`).
   Las listas son datos de `.rodata`; hace falta además el objeto nodo (`B`, 0x28 B) y el constructor estático (`_INIT_*`) que lo registra: parche de código o cueva, **no solo datos**.
2. **Capa 2**: elemento de proceso y fila en la tabla de la página (formato `CmnViewMenuItemStruct`, [G04](g04-menus-y-recursos.md)), con el mapeo ProcessId→mensaje.
3. **Capa 3**: la A6000 ya tiene `SequenceSetSilentShutterMode` (`0x768e`→`0x40e3`); basta con que el elemento la invoque (sin tocar el camino EFCS `0x75fa`/`0x4099`).
4. **Capa 4** (la difícil, ya conocida): dar a `0x40e3` un manejador en `av-cam` que active la ruta electrónica **sin** reescribir `+0x210`; usar un campo propio (análogo a `cap+0x804==2` del A6300). Comprometido con lo ya hecho desde el 3.30 (`pkt[0x0e]`) y con el parche EFCS v3 de Darwin, que no se tocan.

Alternativa mínima (sin menú nuevo): tercer estado en el selector EFCS — ya valorada y **no segura** en E25-24.

## 5. Hallazgos adicionales (misma fecha)

- **Capa de mensajes (`libObj.so`, VERIFICADO por cadenas)**: la A6000 ya trae `PARAMID_SILENT_SHUTTER_MODE{,_ACT,_SET}` y `PARAMID_FRONT_ESHUTTER_MODE{,_ACT,_SET}`; el A6300 añade solo
  `PARAMID_SHUTTER_TYPE{,_ACT,_SET}` y `ObjCamera::MSGID_SET_SHUTTER_TYPE_CMD`. Es decir, el camino Silent de capa 3 existe en la A6000; ShutterType sería el único añadido de `libObj`.
- **Las dos compilaciones no son intercambiables**: la A6000 tiene bibliotecas separadas (`cmnFnWrapper`, `wrapper*.so`, `cmn_view_processDataMgr`, `cmn_menuTableUtil`…) que el A6300 funde en `viewUnified*.so`
  (sin esos `.so`, y con `libInfra*` nuevas). Por eso las capas 1–2 del A6300 no se pueden trasplantar tal cual: hay que reescribirlas al esquema de la A6000, usando el A6300 solo como modelo de datos (propiedades, textos, ids).
- **Descartado**: el barrido de «listas de ProcessId» por todas las bibliotecas (`/tmp`, no versionado) da ruido (valores pequeños se repiten en tablas ajenas, p. ej. pares `{id, nombre de MSG_PARAM_ID}` de `libScalarDaemon`); **no** se usa como evidencia de dónde se registra un ProcessId.
- `CameraOnDemandSaver.so`, `arbiter.so` y `CmnViewIroiroConDataMgr.so` contienen listas con el ProcessId EFCS (`0x46`) en la A6000: candidatas a registros de persistencia/exclusión que un ajuste nuevo debería tocar. **NO_VERIFICADO** su función.

## 5b. Dónde se coloca el ajuste en el menú (VERIFICADO sobre relocaciones, 07-11-2026)

Las páginas de menú son **arrays de punteros a nodos raíz** (`cmnViewSettingNodeRoot*`, importados de `CautionConfig.so`) en `.data.rel.ro` de `viewUnified2.so`, con una relocación
`R_ARM_ABS32` por entrada (`readelf -r -W`). El orden del array es el orden del menú. La entrada del EFCS aparece en **5 páginas** en ambas cámaras:

| | A6000 fw3.21 (vaddr ELF) | A6300 fw2.01 (vaddr ELF) |
|---|---|---|
| Entradas EFCS | `0x4a2f3c`, `0x4a338c`, `0x4a366c`, `0x4a36cc`, `0x4a377c` | `0x75778c+4`, `0x757fe0+4`, `0x758728+4`, `0x759a98+4`, `0x75a0a0+4` |
| Vecinos | `AfWShutter`/`AelWShutter` → **EFCS** → `SuperiorAutoSettings`/`AutoImageExtract`/`TouchShutter` | `AfWShutter`/`AelWShutter` → **SilentShutter** → **EFCS** → `AutoImageExtract` |

Es decir, en el A6300 «Silent Shooting» es **una entrada insertada justo antes de EFCS en las mismas cinco páginas** (y `Shutter Type` va en otras: `0x757248`, `0x7585a8`, `0x7599e0`, `0x75a65c`, junto a `StillMemory`/`SelfPortrait…`).
Además `viewUnified7` lista `SilentShutter` antes de `StillSteadyShot` en ambas cámaras (A6000 `0x5f7b8`, A6300 `0x75638`).

**Consecuencias de diseño** (INFERENCIA; sin verificar el consumidor de los arrays): (a) añadir la entrada exige alargar cinco arrays — hay que localizar el contador/consumidor — o **sustituir** el puntero de una entrada poco usada
cambiando solo el símbolo de su relocación (sin tocar tamaños); (b) el nodo nuevo ha de ser un símbolo definido en `CautionConfig.so` (el stub `SilentShutter` de la A6000, con sus nodos On/Off ya construidos, es la base más barata: cambiar su `PropertyList`
—etiquetas, ProcessId— son datos de `.rodata`, y añadir los textos a `string_*.uxc`).

## 5c. Consumidor de las páginas: `_INIT_70` de `viewUnified2.so` (A6000, VERIFICADO con REA)

Cada página es un nodo local construido con `CmnViewSettingNode::CmnViewSettingNode(nodo, hijos**, cuenta, propiedades)`; `hijos` es el array de punteros de §5b y `cuenta` una **constante en el código** (`_INIT_70`, Ghidra `0x11b674+`; hay 394 construcciones en esa función).
Páginas que contienen el EFCS (direcciones Ghidra = ELF + `0x10000`):

| Nodo de página | Array de hijos | Cuenta | Índice del EFCS | Propiedades | Tras el array |
|---|---|---|---|---|---|
| `0x4d4c88` | `0x4b2f38` [`AelWShutter`, **EFCS**, `SuperiorAutoSettings`, `CustomFaceRecognition`, `CustomLensComp`] | 5 | 1 | `0x4d2034` | 2 palabras nulas y luego otros datos |
| `0x4d4da4` | `0x4b337c` [`StillDigitalZoom`, `StillClearImageZoom`, `ReleaseWOLens`, `AelWShutter`, **EFCS**, `TouchShutter`] | 6 | 4 | `0x4d24a4` | 2 palabras nulas |
| `0x4d4738` | `0x4b3664` [`AfWShutter`, `AelWShutter`, **EFCS**, `SuperiorAutoSettings`] | 4 | 2 | `0x4d6bd8` | contiguo con otro array |
| `0x4d2c0c` | `0x4b36c8` [`AelWShutter`, **EFCS**, `AutoImageExtract`, `CustomExpCompSet`, `CustomBracketOrder`] | 5 | 1 | `0x4d5960` | contiguo |
| `0x4d3494` | `0x4b3778` [`AelWShutter`, **EFCS**, `AutoImageExtract`, `CustomExpCompSet`, `ExposureCompSaveReset`, `CustomBracketOrder`] | 6 | 1 | `0x4d2668` | contiguo |

(Comprobado: cada EFCS cae dentro de `[array, array + 4·cuenta)` en las 5 páginas.) Añadir una entrada exige **tres** cosas: (1) mover o ensanchar el array, (2) una relocación dinámica nueva (`R_ARM_ABS32` contra el símbolo del nodo; el `.rel.dyn` no tiene hueco evidente), (3) subir la constante `cuenta` en `_INIT_70`.
Solo las páginas 1 y 2 tienen palabras nulas de relleno tras el array, pero un puntero nulo hijo no es válido y aun así faltaría la relocación.
**Ruta sin crecimiento** (la más barata): *sustituir* el símbolo de una relocación existente en cada página (`r_info`), p. ej. `AelWShutter` → nodo Silent, a costa de esa entrada de menú; no cambia tamaños ni cuentas. La variante «insertar» queda como trabajo de parcheo ELF (NO_VERIFICADO que sea viable sin reconstruir el `.rel.dyn`).
No he comprobado que las cuentas del A6300 sean las de la A6000 + 1 (NO_VERIFICADO; el A6300 solo se leyó por relocaciones).

## 6. Límites / siguiente

- **NO_VERIFICADO**: qué tabla de página incluye cada elemento (G4) y cómo se conecta ProcessId → elemento (vtables de `viewUnified2` del A6300 sin resolver: REA no enlaza la relocación del vptr, las funciones salen sin símbolo y la vtable hallada por RTTI es de una clase genérica de rango `0x15a/0x15c`; se dejó para G4/G7). El significado de las props `0xb/0xc/0x11/0x14`.
- Las 4 capas son estáticas; **ninguna** probada en cámara ni parcheada. La capa 4 es el bloqueo real del proyecto (sin handler `0x40e3`).
- Siguiente: (0) decidir entre sustituir o insertar entrada (§5c) y comprobar contra el A6300 las cuentas de página; (a) localizar la tabla de la página «Shooting Settings» del A6300 que contiene Shutter Type/Silent Shooting (G4); (b) volcar ProcessId→elemento; (c) diseñar el manejador `0x40e3` con el selector independiente (carril obturador, requiere autorización para cualquier prueba).
