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

## 5. Límites / siguiente

- **NO_VERIFICADO**: qué tabla de página incluye cada elemento (G4) y cómo se conecta ProcessId → elemento (vtables de `viewUnified2` del A6300 sin resolver: REA no enlaza la relocación del vptr y las funciones salen sin símbolo; se dejó para G4/G7). El significado de las props `0xb/0xc/0x11/0x14`.
- Las 4 capas son estáticas; **ninguna** probada en cámara ni parcheada. La capa 4 es el bloqueo real del proyecto (sin handler `0x40e3`).
- Siguiente: (a) localizar la tabla de la página «Shooting Settings» del A6300 que contiene Shutter Type/Silent Shooting (G4); (b) volcar ProcessId→elemento; (c) diseñar el manejador `0x40e3` con el selector independiente (carril obturador, requiere autorización para cualquier prueba).
