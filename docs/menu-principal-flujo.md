# Menú principal (botón MENU): cadena de carga y apertura

Estado: VERIFICADO = contra bytes/desensamblado/log real; INFERENCIA = razonado; NO_VERIFICADO = pendiente.
Fuentes: `analysis/camera-extract/usr/lib/{libObj,viewUnified2..8}.so`, `analysis/camera-dumps/mem-20261020-log/log.txt` (A6000 fw3.21). Desensamblado Thumb con capstone; REA/Ghidra solo para comprobar que no resuelven nombres (binarios sin símbolos locales).

## 1. Quién carga las `viewUnified*.so` (VERIFICADO)
1. `libObj.so` (singleton `getConfig`/`initializeConfig`, ctor en 0x106c7c) hace `dlopen` + `dlsym` de `libObj.so` (`initializeModelConfig/getModelConfig`) y de **`viewUnified2.so`** (`initializeViewConfig/getViewConfig`, `initializeModelTree/getModelTree`). Es la única `viewUnified*` que nombra `libObj` (cadena en 0xbcb832, xref desde 0x106cbc).
2. `viewUnified2.so` es la biblioteca maestra: contiene el **registro de vistas** (función ~0x19485c..0x195f..): por cada vista `view/<NOMBRE>` → `view<Nombre>.so` → `View<Nombre>ToInstance`. Los `.so` individuales no existen; las fábricas están dentro de `viewUnified2..8` (reparto: u4 49, u2 27, u6 17, u5 16, u8 15, u3 14, u7 14) y `viewUnified2` lista los nombres `viewUnified3..8.so` (0x3a2b8a).
3. El **índice** de cada vista en esa tabla coincide con el `Vn NNN_viewUnifiedK.so` del log real: `011`=CAUTION(u2), `080`=SINGLEPB(u2), `088`=STLREC(u2), `06F`=SCALAR(u8), `08C`=USBMASSSTORAGE(u6). La biblioteca que carga cada `Vn` casa con la que exporta la fábrica en los 5 casos comprobados.
4. El log muestra que todo corre en la tarea 83 (`[ViewRoot]`, `[INPUTSERVICE]`, `[POWER_CTRL]`).

## 2. Vistas de menú (VERIFICADO)
| índice | vista | fábrica (lib) |
|---|---|---|
| 0x0E | `BASE_MENU` | `ViewBaseMenuToInstance` (u2) |
| 0x39 | `GLOBAL_MENU` | `ViewGlobalMenuToInstance` (u2) |
| 0x7C | `SETTINGMENUX` | `ViewSettingMenuToInstance` (u2) |
| 0x30 | `FNMENU` | `ViewFnMenuToInstance` (u4; menú Fn) |
Datos del menú: `CmnViewMenuData`, `CmnMenuTableUtil`, nodos `cmnViewSettingNodeRoot*` (viewUnified2: 189; u7: 58; u4: 40; incluye `SilentShutter` en u7 y `CustomFrontCurtainShutter` en u2).

## 3. Qué hace `DefRootView` (VERIFICADO) y corrección de una hipótesis anterior
- Las clases `DefRootView::ActionOpen*Menu` (SettingMenu, FnMenu, FakeMenu, LinkMenu, ContentsMenu) existen en `viewUnified2.so` (vtables VA 0x451928, 0x4513c0, …). `ActionOpenFnMenu::exec` (0x175d44) abre `"view/FNMENU"` (`vtbl[0x14](nombre, 3)`); `ActionOpenSettingMenu::exec` (0x17a090) llama `helper(1)` y `vtbl[0x10]("@V00E")`.
- `@V00E` es un token `@Vxxx` (análogo a `@Mxxx` = modelos, tabla en libObj 0xcbc832: `@M001 modelRoot.so`, `@M004 modelCaution.so`…). Aparece en 13 sitios de viewUnified2, 11 de u3, ~70 de u4 y 2 de u5, y otros `@Vxxx` se eligen por modo en funciones de vista (p. ej. `@V091/@V080/@V078/@V074` según flags 0x10/0x20/0x40/0x80 en 0x1be480..). **No se pudo demostrar** que `@V00E` sea el índice de BASE_MENU (la hipótesis `@V`+índice hex queda como NO_VERIFICADO: no hay tabla `@V`→nombre en claro y los `@V` parecen etiquetas de estado/diseño).
- **Corrección**: la función de registro 0x174216 (vt[3] de la clase con `DispatchEvent` en 0x173af8, switch de eventos 5..0x23) registra por id: 0 ConnectUsbAtPreStable, 1 SetPreStableViewComplete, 2/16 OpenRecMode, 3 OpenModeDial, 4 OpenPatchMovRec, 5 OpenFnMenu, **6 OpenSettingMenu**, 7 SinglePbViewOpen, 8 OpenRecovery, 9 OpenRepair, 10 SetAutoMuteIfNeed, 11 SetCautionLedStatusOnFirst, 12/13 Unset/SetOsdMute/PowerLed…, 14 OpenUSBChargerSinglePb, 15 OpenUsbFeedingCaution, 17 SetForceTime. Es decir, es el **árbitro de arranque (vista raíz)**: decide qué vista abrir al encender según el evento de arranque (SettingMenu se encadena en el evento 9: ids 1,17,2,6,8..12). **No es el manejador de la pulsación de MENU en modo disparo.** Mi afirmación previa («ActionOpenSettingMenu es candidata al botón MENU») queda REFUTADA para este camino.
- Teclas: `InputService::callback_convert` (libObj 0x112f50) convierte el evento base del driver `_InfraInputEvent` en código `0x1501xxxx`: base + 1 (push), +2 (release), +4 (hold). La tabla de nombres de teclas de libObj (0x109df50, {nombre,id}) da `KEY_TACT_MENU`=0x1AC pero **no** es el código de evento. En Android, `ScalarInput.ISV_KEY_MENU` = 514 (`ScalarInput.odex`), y `services.odex` lo usa para el `KEYCODE_MENU` de las apps PMCA (p. ej. Tweak sale con MENU).
- Tabla de teclas `KEY_UP_PUSH/DOWN/LEFT/RIGHT/BURST/SS` → `view/HARDKEYMENU_{DISP,SELFTIMER,FLASH}`, `HARD_KEY_MENU_BURST` en viewUnified2 (0x3b70d9): atajos de cruceta en disparo (vistas HARDKEYMENU), no el menú.

## 4. Veredicto de cierre
- CERRADO (verificado): quién carga (`libObj`→`viewUnified2`→`viewUnified3..8`), cómo se registran y se numeran las vistas (coincide con el log real), cuáles son las vistas de menú (BASE_MENU 0x0E, GLOBAL_MENU 0x39, SETTINGMENUX 0x7C, FNMENU 0x30), cómo llega una tecla (InputService → `0x1501xxxx` → ViewRootSelector → mapas de acciones `DefRootView`), y que el árbitro raíz de arranque abre vistas por `ActionOpen*`.
- NO DEMOSTRADO: el código base de evento de la tecla MENU y la vista de disparo (STLREC u otras) que, al recibirlo, abre BASE_MENU. Las clases y funciones están sin símbolos locales (RTTI solo en `DefRootView`); no hay tabla evento→vista en claro; la cámara real no estuvo accesible en esta sesión (192.168.1.29 fuera de red).
- Hipótesis de trabajo (INFERENCIA, no demostrada): el menú principal que sale con MENU es `BASE_MENU` (nombre «menú base»), `SETTINGMENUX` es el menú de ajustes y `GLOBAL_MENU` el menú global/de red; `FNMENU` es el menú Fn (confirmado por `ActionOpenFnMenu` → `view/FNMENU`).
- Cómo cerrarlo con certeza: (a) con cámara, volcar el log del búfer 0x83400000 (como `mem-20261020-log`) justo tras pulsar MENU y buscar `Vn 00E_viewUnified2.so`/`Vo` (el log de vistas imprime el índice hex de la vista cargada); (b) estáticamente, recorrer la fábrica `ViewStlrecToInstance` (índice 0x88) y los manejadores de eventos de esa clase hasta una llamada `openView`/`vtbl[0x14]` con el nombre `view/BASE_MENU` o el token que lo represente.
