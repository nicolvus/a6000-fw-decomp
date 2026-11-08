# G12 — Menú Fn, secciones nuevas y filtros (estático, 08-11-2026)

**Método**: lectura de `CautionConfig.so`/`viewUnified4.so` de 3.21 con `setting_nodes.py`, `elf_scan.py` y Capstone. Sin cámara.
Estado: VERIFICADO = leído en los bytes; INFERENCIA = razonado; NO_VERIFICADO = pendiente.

## 1. Cómo se define el menú Fn (VERIFICADO)
- Vista `view/FNMENU` (índice `0x30`, fábrica `ViewFnMenuToInstance` en `viewUnified4.so` `0xdb807`); `DefRootView::ActionOpenFnMenu` la abre. Layouts `LG_viewfnmenu::LayoutFNMENU_BELT_EVF/LCD`; la franja es `PAS_MenuSelectBeltFn` (`openMenuSelectBelt(CmnViewSettingNode*,…)`, `hasOptions`, `getCurrentItemMenuID`), de modo que el menú Fn **se alimenta de nodos de ajuste** como el resto.
- «Function Menu Set.» = nodo `cmnViewSettingNodeRootFnFunction` con 2 páginas (`…FnFunctionPage1/2`, `0xb=2`; la lista por defecto `cmnViewSettingNodesFnFunctionDefault` tiene 2 punteros).
- 12 ranuras `FnFunctionCustomFunction1..12` (Upper1–6 y Lower1–6). ProcessIds de las ranuras: `0x55..0x60` (consecutivos). Raíz de cada una: `0xb=2, 0xc=0`.
- Cada ranura tiene **37 opciones** (`0xb=0, 0xc=2`), con `0xf/0x10` = identificador de función **`0x00..0x24` contiguo, sin huecos**: DriveMode 0, FlashMode 1, FlashComp 2, FocusMode 3, FocusArea 4, ExpComp 5, ISO 6, Metering 7, WB 8, DRO/HDR 9, CreativeStyle 0xa, Subexposuremodes 0xb, PictureEffect 0xc, ObjectTracking 0xd, SmileFace 0xe, SoftSkin 0xf, PortraitFraming 0x10, ImageSize 0x11, AspectRatio 0x12, Quality 0x13, RecordingMedia 0x14, SteadyShot 0x15, Gain 0x16, AutoBackLight 0x17, Cinematone 0x18, MovieSteadyShot 0x19, AudioRecLevel 0x1a, Zebra 0x1b, GridLine 0x1c, PeakingLevel 0x1d, PeakingColor 0x1e, SteadyShotOnly 0x1f, AudioLevelDisplay 0x20, NDFilter 0x21, MemoryRecall 0x22, NotSet 0x23, ShootMode 0x24.
- **No hay opción de obturador (EFCS/Silent) en el menú Fn.** Hay dos conjuntos distintos de ids entre ranuras (causa sin investigar).

## 2. Qué haría falta para añadir «Silent Shooting» al menú Fn (INFERENCIA)
1. Una opción nueva por ranura (12) con `0xf/0x10 = 0x25`, texto propio y `0xb/0xc` como las demás: igual que el parche del 3.54, pero ×12 y con arrays de hijos de 37→38 (patrón `add_menu_entry.py`).
2. **El id `0x25` debe entender el código**: en `viewUnified4.so` hay una tabla de saltos por función (stubs `mov r0,r4; …; b.w` en `0x1666a4–0x16765a`; que sean uno por id no está comprobado) que construye el elemento de la franja y cuya cota habría que ampliar; además `CmnFnWrapper` (`cmnFnWrapper.so`) y la persistencia de la asignación en NVRAM (qué rango admite). Ninguna de las tres está leída aún → NO_VERIFICADO.
3. Alternativa más barata (INFERENCIA): **reasignar una ranura existente** (p. ej. sustituir la opción «Cinematone», id 0x18, por el nodo EFCS) cambiando solo el texto y el ProcessId de la opción, sin tocar el código; se pierde esa función en el Fn.

## 3. Secciones nuevas y filtros (INFERENCIA)
- Una sección nueva en MENU = nodo raíz nuevo + entrada en la página (patrón ya probado con «Silent Shooting» en el 3.53/3.54; `PAGES` en `add_menu_entry.py` y `LISTS`/`COUNT_MOVS` en `build_silent_menu_test.py`).
- «Filtros» (efectos de imagen): ya existen `PictureEffect` (Fn id `0xc`) y `CreativeStyle`; sus tablas están en `viewUnified2.so` `0x4cc640/0x4cc960` ([G04 §8](g04-menus-y-recursos.md)). Añadir un filtro propio exige además el algoritmo en el procesador de imagen (BIONZ/Darwin): fuera del alcance de la GUI; sí es posible ocultar o renombrar los existentes.
- Todo lo que sea solo texto/orden/visibilidad no depende de G7 (middleware); lo que cambia el comportamiento sí.

## 4. Límites
Sin leer el consumidor del id (§2.2) no se sabe si `0x25` es viable. Sin cámara: nada se ha probado; el selector del 3.54 sigue sin comprobar.
