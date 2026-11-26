# FILM-PB-1 / sub-menú — ¿se puede exponer «Selector PAL/NTSC» en la A6000?

27-11-2026. Estático puro (cámara no accesible). **Espacio: VA del ELF** de `viewUnified2.so`, `CautionConfig.so`
y `cmn_view_processDataMgr.so` 3.21 (`.text/.rodata/.rel.dyn` VA == offset; `.data` va = off + 0x8000).
Evidencia: `reports/evidence/film-pb-1-sub-menu-20261127/`. Respuesta corta: se puede hacer visible con 24 B,
**pero el ajuste no hace nada** (stub de interfaz) ⇒ no arregla la reproducción.

## 1. La entrada: qué es y de qué cuelga (VERIFICADO)

**Nodo** (CautionConfig.so): `cmnViewSettingNodeRootSettingSetupNtscPalSEL` = `.bss 0x1C935C` (28 B), construido
desde `cmnViewSettingPropertyListSettingSetupNtscPalSELRoot` (`0x1648AC`, **0x3C B = 5 tripletas**):

| prop | flag | valor | significado |
|---|---|---|---|
| `0x00` | 0 | `0x0204EFC2` | texto «PAL/NTSC Selector» (es «Selector PAL/NTSC»), id de cadena **0xEFC2** |
| `0x06` | 0 | `0x0204EF53` | ayuda: «Puede hacer tomas con un ajuste de grabación de película diferente…» |
| `0x0B` / `0x0C` | 1 | `2` / `4` | indicadores; **idénticos en ítems visibles** (WhiteBalance, DriveMode…) |
| `0x0E` | 1 | `0x85` | **ProcessId 133** |

Sin propiedad de icono (no hay `0x02`/`0x03` con `0x0205xxxx`): la fila se dibuja solo con texto.

**Elemento de proceso** (pid `0x85`): `elem[0x85]` (tabla `0x3A5E1C`, stride 4) = caso `0x32`; descriptor
`D[0x85]` = `0x4B83B0` (tabla de punteros `0x4457D4`): `w6/w7 = 0/0` **sin modelo de datos**, `w8/w9 = 0/0`
**sin ids de respaldo NVRAM**, `w10 = 0x3A1AE0` → **«view/NTSCPALSEL»**. Clase
`CmnViewProcessDataElementCustomNTSCPALSelection` (vtable `0x46F298`), métodos en `viewUnified2.so`:
`getProcessId 0x24B434`, `getValue 0x24B448` → **`return 0`**, `setValue 0x24B450` → **`return 0`**,
`isValueDisable 0x24B458`, `isValueGrayedOut 0x24B460` (ambos 0), `isDisable 0x24B474` →
`BackupManager::Bkup_Read(0x01070148)!=0`, `isGrayedOut 0x24B4A8` → `CustomBase::isStillWritingImageToCard`,
`execProc 0x24B468` → `Normal::execProc (0x75E94)`.

**Dónde se coloca**: cada página es `CmnViewSettingNode(hijos, cuenta, props)` construida en la init
(`blx 0xE81C8`); el ítem es hijo en **10 arrays** de `.data`:

| objeto página | array (cnt) | idx | vecinos | se construye en |
|---|---|---|---|---|
| `0x4C3E14` | `0x4A4038` (6) | 4 | ShowTopMenu, ModeDialGuide, LCDQuality, StartPowerSave, **ítem**, DemoMode | `0x169ACE` |
| `0x4C4F0C` | `0x4A45D8` (6) | 1 | StartPowerSave, **ítem**, DemoMode, HDMIRes, CtrlHDMI, USBConn | `0x169726` |
| `0x4C2DEC` | `0x4A4908` (5) | 2 | PowerSave, StartPowerSave, **ítem**, CleaningMode, DemoMode | `0x166654` |
| `0x4C2ACC` `0x4C35FC` `0x4C2CD4` | `0x4A37C0` `0x4A4F54` `0x4A553C` (6) | 5 | ShowTopMenu … StartPowerSave | `0x169336` `0x168AE0` `0x1679E2` |
| `0x4C6018` + 3 más | `0x4A41EC`, `0x4A41FC`, `0x4A4D10`, `0x4A50E8` | 4 | — | `0x168362` `0x16A2C4` `0x16AE7C` `0x16A96A` |

## 2. Qué lo oculta: ni tabla de modelos ni flag de región (VERIFICADO); es la configuración de menú

- **Sin máscara de modelo/región en el ítem**: sus 5 propiedades son las mismas que las de ítems visibles; en la
  A6300 los dos rótulos (`NtscPalSEL` y `NtsctoPal`, pid 148) las tienen **idénticas** ⇒ la región la decide
  **qué nodo entra en la página**, no un campo.
- **Filtro de estado** de `CmnViewSettingNode` (CautionConfig.so): `[this+0x24]` = estado (1 normal, 2–6 gris,
  **0 = no seleccionable = oculto**). `getCountSelectable 0x10394A` recorre los hijos y **salta** los que
  `isItemSelectable 0x103CF8` (`ldr r0,[r0,#0x24]`; `!=0`) den 0; `setItemDisable 0x103FFC` vuelve 1→0. Pero
  `init 0x10412D` pone estado 1 a todos los hijos y `viewUnified2.so` **no importa `setItemDisable`** (solo
  `initSettingNode`, ctor y dtor): nada del módulo de vistas oculta el ítem por aquí.
- **13 configuraciones de menú completas** en la misma init de `viewUnified2.so` (13 raíces, 353 objetos,
  77–132 hojas; `…/arbol_paginas.log`): el ítem está en **7** (`0x4C4070 0x4C4418 0x4C4D54 0x4C5164 0x4C55C8
  0x4C5708 0x4C6B70`) y **falta en 6** (`0x4C43C8 0x4C53F4 0x4C5820 0x4C5D88 0x4C5DB8 0x4C6660`). Las **tres
  únicas sin `PhaseDetectionAF` ni `Output4kMode`** (las compatibles con A6000: `0x4C43C8 0x4C5DB8 0x4C6660`)
  **no lo llevan en ninguna página** (p. ej. Setup `0x4C3324`: 6 páginas, ninguna con el ítem).
  **NO_VERIFICADO** cuál de las 13 usa esta cámara: no hay tabla modelo→config, las 13 se construyen
  incondicionalmente y ninguna raíz se referencia después (haría falta traza en cámara).

## 3. Parche mínimo (24 B, sin mover nada) — `reports/evidence/…/parche_menu.py`

Las celdas de esos arrays son `R_ARM_ABS32` (tipo 2) con **addendo 0** y símbolo en `.dynsym`: cambiar de qué nodo
cuelga una celda = reescribir el índice de símbolo de **su** entrada de `.rel.dyn` (`r_info = (sym<<8)|2`), sin
tocar `.data`, tamaños ni relocaciones. Destino `dynsym[697]` = `cmnViewSettingNodeRootSettingSetupNtscPalSEL`
→ `r_info = 0x0002B902`, aplicado a la página Setup de las 6 configuraciones que no lo llevan (se sustituye un
nodo que la A6000 no usa):

| config | celda | array+idx | antes (`r_info`) | después |
|---|---|---|---|---|
| `0x4C43C8` | `0x4A3548` | `0x4A353C`+0xC | `0x0003B902` DropSensor | `0x0002B902` |
| `0x4C53F4` | `0x4A2F68` | `0x4A2F64`+0x4 | `0x00049402` SetupMenuStart | `0x0002B902` |
| `0x4C5820` | `0x4A49F0` | `0x4A49F0`+0x0 | `0x00049402` SetupMenuStart | `0x0002B902` |
| `0x4C5D88` | `0x4A496C` | `0x4A495C`+0x10 | `0x00048402` SetupGPSSettings | `0x0002B902` |
| `0x4C5DB8` | `0x4A40DC` | `0x4A40CC`+0x10 | `0x0003B602` 24pMode | `0x0002B902` |
| `0x4C6660` | `0x4A3368` | `0x4A3368`+0x0 | `0x00049402` SetupMenuStart | `0x0002B902` |

Bytes exactos (fila `0x4C5DB8`, `.rel.dyn` @`0xE18F4`): `02 B6 03 00` → `02 B9 02 00`. Antes de escribir, el
script comprueba: addendo 0, tipo 2, símbolo de origen esperado, **una sola** entrada `.rel.dyn` por celda y
**una sola** aparición del par `(r_offset, r_info)`. Escribe solo `/tmp/viewUnified2.menu.so` (mismo tamaño,
4.953.524 B) y verifica en la copia que las 6 celdas apuntan al símbolo nuevo (10 → 16) y nada más cambia
(`log`: 24 B escritos, 11 con valor distinto).

## 4. ¿El ajuste se aplica de verdad? **No**: el parche es solo interfaz

1. `setValue(int)` del elemento = **`return 0`** (`0x24B450`): no escribe modelo ni NVRAM; `getValue` = **`return 0`**
   (`0x24B448`): la fila no tiene valor que leer ni pintar. Descriptor `D[0x85]`: `w6/w7 = 0/0` (sin modelo de
   datos) y `w8/w9 = 0/0` (**sin ningún id de respaldo**): no hay dónde persistir la elección. Coincide con
   [nvram](film-pb-1-nvram-pal-ntsc-20261127.md): el elemento no tiene id en la NVRAM.
2. La única acción real es la de la página, `DefRootView::ActionNtscCaution::execute` = **`0x17A930`** (vtable `0x451AC8`):
   ```
   0x17A93E ldr r0,[pc] -> 0x01070148 ; Bkup_Read ; 0x17A94C cmp r3,#1 ; bne -> fin
   0x17A958 ldr r0,[pc] -> 0x010704FD ; Bkup_Read ; 0x17A962 cmp r2,#1 ; bne -> fin
   0x17A96C movw r1,#0x89E ; ldr r3,[r0]; ldr r3,[r3,#0x68]; blx r3   ; evento 0x89E
   ```
   En los 30 volcados (`analysis/camera-dumps/*/backup_flash.bin`): **`0x01070148 = 00`** y `0x010704FD = 01`,
   luego la acción **no manda nada**: el ítem se abriría y no haría nada.
3. `TvSystem`, lo que lee la guarda de reproducción, es `*(u32*)0x28F850` **dentro de `libmpr`**: la UI no tiene
   ruta que lo escriba (ni mensaje, ni propiedad, ni respaldo en `D[0x85]`). **NO_VERIFICADO** que otro camino de
   modelo lo cambie; sí está verificado que éste no.

## 5. Veredicto

**Se puede hacer visible (24 B, 6 VAs; §3), pero no sirve**: el ajuste es un stub de interfaz (`getValue`/
`setValue` = 0, sin modelo, sin respaldo NVRAM) y su acción de cambio está cerrada por `0x01070148 = 0`. Cambiarlo
no persistiría ni alteraría el sistema de TV: los clips de 30p seguirían sin reproducirse.

- **NO_VERIFICADO**: qué configuración de menú (de las 13) usa esta cámara; el valor *actual* de `0x01070148`
  (último volcado 22-11-2026, anterior al CFW 3.93); y si algún evento distinto de `0x89E` escribe `TvSystem`.
- Recomendación sin cambios respecto a [causa](film-pb-1-causa-sistema-tv-20261127.md) §4: **V1** (reescribir la
  cadencia declarada del clip) sigue siendo la única vía probada y sin riesgo; **V2** (este parche) queda descartado por inútil, no por arriesgado.
