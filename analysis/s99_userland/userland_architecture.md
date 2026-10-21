# S99 — La arquitectura del userland: las capas de `libObj.so`

**Alcance:** línea de ingeniería inversa **general** de la cámara: el **esqueleto de software** del
lado Linux de la A6000, tal y como se ve en la mayor biblioteca del userland, `libObj.so` (17,4 MB).
Conecta con S87/S92 (la capa de medios), S86/S93 (el escalar y las colas OSAL) y S16–S30 (la capa
SDF/AVBBC). No es la línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD, ni ZPD, ni
`apc_*`, ni ZIT, ni ADF, ni el API del SA, ni el visor, ni las caras, ni el wireless, ni la
reproducción, ni los modos de disparo, ni el IDT, ni AutoFraming, ni los ficheros, ni los modos de
captura, ni la sincronización del codificador.

**Estado:** VERIFICADO = contra bytes/símbolos. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s99_userland.py`.

---

## 1. El tamaño de la capa (VERIFICADO)

| | A6000 fw3.21 | A7S fw3.20 |
|---|---|---|
| `libObj.so` | **17 436 172 B** | 16 184 848 B |
| símbolos mangled `_ZN…` | **2507** | 2538 |
| namespaces distintos | **167** | 168 |

→ el userland de la A6000 es **prácticamente el mismo** que el de la A7S en estructura (167 vs 168
namespaces, mismos símbolos por namespace salvo en `ux`, `OBJAVBBCBASECLASS` y `NetCommonLibrary_`).

## 2. Las capas (VERIFICADO por los namespaces, con nº de símbolos)

| namespace | símbolos | capa | qué es (evidencia) |
|---|---|---|---|
| `MprIf` | 318 | **medios** | interfaz del *media repository*: contenidos, carpetas por fecha, playlists (S87/S92) |
| `MWF` | 241 | **núcleo de mensajes** | `MWF::ObjMsgList` (`GetMsg`, `pop_head`, `pop_tail`, `Clear`, `Iterator`), `MWF::ObjMsg`, `MWF::ObjMsgEntry`, `MWF::RsrcAcsr` |
| `ux` | 227 | **gráficos/UX** | `ux::core::GraphicsImage` (`copy`, `clear` con `stella::CColor`), `ux::core::GraphicsSystem::setOSDGainParam`, `ux::core::TextLayout::registerFontFaceFile`, `ux::core::ID` |
| `AVBIZ` | 138 | **universo de apps** | `AVBIZ::UNIVERSE::UActiveObject` (`onStarting`, `onStopping`, `SendMsgToApp`, `eventProcessing`), `::UBbSuspend`/`UBbResume`, `::SelectorProxy` (`SelRegister`/`SelDeregister`), `::ULog_u16x5`/`ULog_u8x10` |
| `OBJAVBBCBASECLASS` | 128 | **SDF/AVBBC** | el puente de imagen `Obj → AVBBC` (documentado en S16–S30) |
| `MprCtrl` | 58 | medios (control) | controlador del repositorio de medios |
| `ViewBase`, `DefRootView`, `AppWidgetBase`, `LayoutableWidgetBase` | 53 / 22 / 27 / 45 | **GUI** | vistas, widgets y layout del menú |
| `GEN_*` | 45 (`GridList`), 34 (`Calendar`), 29 (`Button`), 24 (`Label`), 22 (`Balloon`), 20 (`EditBox`) | **widgets genéricos** | el toolkit de la interfaz de la cámara |
| `C_DataflowInfra_*` | 44 (`Entry_ImageSizeInfo`) | **dataflow** | el pipeline de datos de imagen (SDF) |
| `InputService` | 36 | entrada | servicio de entrada (botones, dial) |
| `UFW` | 34 | **recursos** | `UFW::DfsWrapper` (`ng`/`ok`), `UFW::MsgReceiver` (`RcvMsg`, `PostMsg`), `UFW::RsrcWrapper` (`AcquireSingle`, `ReleaseAll`) |
| `NetCommonLibrary_*` | 25 (A7S: 35) | red | utilidades de red (S72/S93) |
| `GCM_*` | 24 | red/GCM | gestión de conexiones |
| `CmnViewMenuData`, `SequenceBase`, `HighlightManager`, `GlobalAccessor`, `ScalarView`, `ObjAvbbcCmn`, `ObjActiveBaseAvbbc` | 23/23/19/18/17/22/12 | varios | el menú, las secuencias, el resaltado, el acceso global y la **vista del escalar** |

## 3. Lo que revela la estructura (VERIFICADO + INFERENCIA)

- El userland es **capas**: `MWF` (mensajes) + `UFW` (recursos) son la base; `MprIf`/`MprCtrl` la capa
  de medios; `ux` + `GEN_*` + `ViewBase` la **interfaz de usuario**; `AVBIZ::UNIVERSE` el **gestor de
  aplicaciones**; `OBJAVBBCBASECLASS` + `C_DataflowInfra_*` la capa de **imagen**; `NetCommonLibrary`
  + `GCM` la de **red**.
- INFERENCIA: `MWF::ObjMsg` + `AVBIZ::UNIVERSE::UActiveObject::SendMsgToApp` describen un
  **modelo de aplicaciones con mensajería asíncrona**: la app es un objeto activo que recibe
  mensajes y los reenvía; `UFW::RsrcWrapper::AcquireSingle/ReleaseAll` es el **arbitraje de recursos**
  (coherente con el `SyncResMgr` del lado firmware, S81).
- `ux::core::GraphicsSystem::setOSDGainParam` y `GraphicsImage` sobre `stella::CColor` (>libObj
  tiene 227 símbolos `ux` y usa `stella::`): la **interfaz se dibuja con el escalado de imagen
  propio** (`stella` = la biblioteca base, también presente en `wrapperCreativeStyle.so`, S77).
- El **"escalar"** aparece en el userland (`ScalarView`, `AVBIZ`, y la cola `SADRIVER` de S93) →
  el historial "Scalar" de S86/S71 conecta firmware y userland.

## 4. Abierto (NO_VERIFICADO)

- Qué son exactamente `MprIf` frente a `MprCtrl` (interfaz vs implementación) y `MWF` frente a `UFW`.
- La lista completa de los 167 namespaces (aquí los 30 primeros).
- Cómo se registran las "apps" del `UNIVERSE` (qué las lanza: la GUI, PlayMem, la app remota…).
- El papel de `NetCommonLibrary_` (10 símbolos menos en la A6000 que en la A7S: **la A6000 tiene
  menos código de red**, coherente con S72).

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s99_userland.py -q
```
