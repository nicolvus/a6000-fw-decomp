# G01 — Arquitectura de la GUI en el userland de la A6000 (reconocimiento)

**Fecha**: 28-10-2026
**Base**: firmware 3.21 extraído (`firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/`)
**Evidencia reproducible**: `scripts/gui/inventory.py`, `scripts/gui/elf_scan.py`, `analysis/gui/g01-inventory.json`,
`tests/test_gui_elf_scan.py`
**Estado global**: reconocimiento VERIFICADO; compositor y editor de recursos INFERENCIA; capacidad de
modificación NO_VERIFICADA.

---

## 1. Conclusión

La interfaz de la A6000 **no vive en `av-cam.bin`** (BIONZ) sino en una **pila Linux propia**: un lanzador
(`bin/im.elf`) que carga por `dlopen` un motor de UI (`/usr/lib/libObj.so`, 17,4 MB) y una colección de
«vistas» (`lib/viewUnifiedN.so`) más **238 recursos** de `share/app` (`.uxc`, `.uxb`, `.xdb`, fuentes `.ltt`/`.ttf`).
El motor es un framework C++ con espacio de nombres `ux::` (`gfxeng`, `resmgr`, `wgtlay`, `wgtsys`, `core`) apoyado
en bibliotecas de Sony (`libra`, `alcor`, `stella`, `andromeda`) y en `libMWF.so` (framework de mensajes).

Consecuencia para el proyecto: cualquier cambio de texto, icono, disposición, mensaje o entrada de menú es
**sustitución de recursos o de código en la partición `/usr`**, no un parche de `av-cam.bin`. Eso es un carril
distinto del obturador (ver [PENDIENTES](../../docs/PENDIENTES.md), sección G) y con riesgos distintos.

## 2. Método y límites

| Aspecto | Estado |
|---|---|
| REA sobre `libObj.so` | **NO VIABLE**: `list_documents` agota el plazo del proveedor (900 s) con un binario de 17 MB. Documentado como límite de herramienta, no como ausencia de contenido |
| Sustituto | Tabla de símbolos dinámicos + desensamblado Capstone (`scripts/gui/elf_scan.py`), más `readelf`/`nm` del sistema |
| Trampas conocidas | Capstone debe usarse con `cs.skipdata = True`; sin él el desensamblado Thumb se detiene en el primer bloque no decodificable. `.plt` es **ARM**, no Thumb |
| Ejecución | Ninguna: solo lectura de ficheros. No se ejecuta firmware ni se escribe en el dispositivo |
| Cadenas | Las cadenas de `.uxc` no son alcanzables por `movw/movt` ni por literales en `.text`: el motor parece trabajar con **ID de recurso**, no con punteros a texto. Por eso el avance se hace por símbolos y vtables, no por xrefs de cadena |

## 3. Inventario (VERIFICADO)

`share/lib` — 18 módulos con relación directa con la UI:

| Fichero | Bytes | SHA-256 (12) | Símbolos con nombre |
|---|---|---|---|
| `libObj.so` | 17 436 172 | `8e8a937aed23` | 1 814 |
| `viewUnified2.so` | 4 953 524 | `7fbfa8539717` | 1 450 |
| `viewUnified3.so` | 398 464 | `80ae3b94db54` | 19 |
| `viewUnified4.so` | 1 784 836 | `149282ac0f1e` | 83 |
| `viewUnified5.so` | 549 852 | `5c1f69ff5055` | 21 |
| `viewUnified6.so` | 394 432 | `13f18bf054f8` | 21 |
| `viewUnified7.so` | 366 676 | `ca581f5a2336` | 17 |
| `viewUnified8.so` | 240 764 | `5dcd54082f3e` | 19 |
| `cmn_menuTableUtil.so` | 9 912 | `832c45e2bf85` | 50 |
| `cmnviewViewModel.so` | 12 144 | `c0acc5c89cb8` | 76 |
| `cmn_view_processDataMgr.so` | 598 400 | `e2968b2836ed` | 2 840 |
| `cmnviewMRUtil.so` | 80 620 | `7e544afb630e` | 293 |
| `CmnShootingInfoLayoutMgr.so` | 31 124 | `921acc34620f` | 88 |
| `CmnViewIroiroConDataMgr.so` | 10 660 | `c9baf8a5a72b` | 67 |
| `cmnFnWrapper.so` | 37 920 | `c709b95a8d6f` | 107 |
| `zakoMenuUtil.so` | 13 040 | `4c860e78e036` | 60 |
| `libScalarDaemon.so` | 1 883 224 | `ca28cbf4c5c6` | 7 341 |
| `libmintx.so` | 1 502 248 | `a988cd8ae527` | 10 359 |

`share/app` — 238 ficheros, 55 175 204 B. Prefijos dominantes: `string` (66, uno por idioma), `image` (8,
el mayor de 25 MB), `view*` (146 ficheros, 144 nombres), `master_*` (4), `lang` (2), más `style_cmn.uxc`, `color_cmn.uxc`,
`LayoutMaster_Menu.uxc`, `global.xdb`, `fontlist.dat`, `Sony_DI_Icons.ttf` y 8 fuentes `.ltt`.

## 4. Capas de símbolos de `libObj.so` (VERIFICADO sobre `.dynsym`)

| Espacio | Símbolos | Papel |
|---|---|---|
| `ux::wgtlay` | 102 | conversión y gestión de *layouts* (`LayoutConverter`, `LayoutGroupManager::openLayout`) |
| `ux::gfxeng` | 28 | motor gráfico: `GraphicsEngine`, `Sprite`, `TextSprite`, `ResourceUpdater` |
| `ux::core` | 21 | tipografía y texto (`TextLayout::registerFontFaceFile`) |
| `ux::resmgr` | 12 | `ResourceManager` (base de datos y creación de fuentes/imágenes) |
| `ux::wgtlay`/`wgtsys` | — | `Widget`, `Layer`, `Action`, `KeyEvent`, `MouseEvent`, `GestureAnalyzer` |
| `ViewBase` | 53 | clase base de vista |
| `LayoutableWidgetBase` | 45 | base de widget con layout |
| `InputService` | 36 | entrada (`callback_convert` y familia) |
| `CmnViewMenuData` / `CmnViewMenuItemStruct` | 23 | modelo de datos de menú |
| `DefRootView` | 22 | raíz de vistas |
| `HighlightManager` | 19 | resaltado/selección |
| `ScalarView` | 17 | vista escalar |
| `stella` | 3 | colores (`CColor`) |
| `ux::animeng` | 1 | animación (`Animation::addEventCallback`) |

Secciones relevantes: `.text` @ `0xe2b70` (11 430 428 B), `.plt` @ `0xdb3c4` (30 624 B, ARM), `.rodata` @
`0xbc9598` (2 918 938 B; **vaddr == offset** en este binario), `.data.rel.ro` @ `0xfd29d0`, `.got` @ `0x102cbd0`,
`.rel.dyn` 655 944 B (60 946 `R_ARM_RELATIVE`), `.rel.plt` 19 360 B (2 420 `R_ARM_JUMP_SLOT`).

## 5. Arranque y dependencias (VERIFICADO)

`bin/im.elf` (23 108 B) es el lanzador: importa `dlopen`/`dlsym`/`dlclose`, contiene la cadena
`/usr/lib/libObj.so` y depende de `libIMDB.so`, `libosal_uipc.so`, `libosal_utm.so`, `libbackup.so`, `libdl`,
`libpthread`, `libstdc++`, `libm`, `libgcc_s`, `libc`, `librt`. También importa `IMDB_get_entries`,
`IMDB_find_entry`, `IMDB_find_target_bit`: es un **cargador basado en una base de datos de módulos (IMDB)**, no
un ejecutable monolítico.

`libObj.so` declara 17 `DT_NEEDED`: `libInfraFsys`, `libmprctrl`, `libMWF`, `libmpr`, `libutil_date`,
`libcompassutil`, `libsencore`, `libBizFw`, `libBizFw2`, `libNetContUtil`, `libUsbControl`, `libNetCommon`,
`libGOConnectionManager`, `libInfraMediaCommon`, `libbackup`, `libgcc_s.so.1`, `libc.so.6`. Es decir: el motor de UI
**sí** depende del *middleware* de negocio y de comunicación, y no solo de gráficos.

> Corrección de registro: una nota previa de la sesión afirmaba que `libObj.so` no tenía `NEEDED`. Es falso; la
> tabla dinámica tiene 17 entradas (verificado con `readelf -d` y por lectura directa de `.dynamic`).

## 6. Carga de vistas (VERIFICADO con traza real)

En el log del 20-10-2026 (`analysis/camera-dumps/mem-20261020-log/log.txt`) la tarea 83 se identifica como
`[ViewRoot]` y se registran cargas de `Vn 080/011/088_viewUnified2.so`, `Vn 08C_viewUnified6.so` y
`Vn 06F_viewUnified8.so`. Por tanto:

- las vistas son **módulos `.so` cargados bajo demanda**, no recursos interpretados;
- un mismo `viewUnifiedN.so` sirve a **varias** pantallas (el nombre del fichero no identifica la vista);
- el menú y las páginas concretas se seleccionan por datos (`CmnViewMenuData`, `cmn_menuTableUtil.so`,
  `LayoutMaster_Menu.uxc`), lo que encaja con la ausencia de xrefs a cadenas.

## 7. Motor de composición (INFERENCIA basada en símbolos y cadenas)

`ux::gfxeng::GraphicsEngine` expone `sys_getInstance` (`0x5cfad1`), `getFramebufferWidth` (`0x5cfae9`),
`getFramebufferHeight` (`0x5cfaf5`) y `updateResource` (`0x5d02a7`). En `.rodata` hay evidencia de la capa de
ventanas: `src/WindowServer_DI.cpp`, `WindowServerEGL.cpp`, `ViewSystem` con `updateFrame`, `notifyDraw`,
`drawFramebuffer`, `initializeArena`, `OSD Gain Filter`, `readPixels getTextureId(front/back)`,
`Can not allocate mDirtyRegion[i]`, `pSurface is null as a return of detachSurface`; y las cadenas `/dev/fb0`
(`0xd5f904`, `0xd7798f`) y `/usr/share/app/` (`0xd8858b`).

Lectura: la composición es **EGL/GLES sobre framebuffer Linux (`/dev/fb0`)**, con `ViewSystem` gestionando
regiones sucias y `GraphicsEngine` exponiendo el tamaño de framebuffer. `updateResource` recorre el árbol de
nodos con un `ResourceUpdater` (patrón *visitor*): `sys_getInstance()` ×2 + `ResourceUpdater(ResourceManager*)`,
bucle sobre nodos y, por nodo, `visit()` (vtable `+0x10`). Está **sin verificar** dónde se hace el `swap` final y
quién escribe `/dev/fb0`.

## 8. Tabla PLT → símbolo importado (VERIFICADO)

Problema previo: las llamadas externas de `libObj.so` aparecían como `blx #0xdb508` sin nombre. Resuelto sin
REA: `.plt` es ARM de 12 B (`add ip, pc, #hi ; add ip, ip, #lo ; ldr pc, [ip, #off]!`), y cada stub consume su
slot de `.got` en el mismo orden que `.rel.plt`. `elf_scan.py plt` decodifica el slot destino y lo cruza con
`R_ARM_JUMP_SLOT`:

```
.plt           0x0db3c4  (30 624 B, ARM; cabecera 24 B + 2 550 huecos de 12 B)
.rel.plt       2 420 R_ARM_JUMP_SLOT, slots GOT 0x102cbdc … 0x102f1a8
resueltos      2 419 stubs -> nombre (1 hueco sin relocación)
```

Ejemplos que desbloquean el compositor:

| Stub | Símbolo importado |
|---|---|
| `0xdb508` | `ux::gfxeng::GraphicsEngine::sys_getInstance()` |
| `0xdf01c` | `ux::resmgr::ResourceManager::sys_getInstance()` |
| `0xdc950` | `ux::gfxeng::ResourceUpdater::ResourceUpdater(ResourceManager*)` |
| `0xe1058` | `ux::gfxeng::ResourceUpdater::~ResourceUpdater()` |

Con eso, `updateResource` (`0x5d02a7`) queda:

```asm
0x5d02ac  blx 0xdb508        ; GraphicsEngine::sys_getInstance()
0x5d02b2  blx 0xdf01c        ; ResourceManager::sys_getInstance()
0x5d02ba  blx 0xdc950        ; ResourceUpdater(rm)
0x5d02c2  bl  0x5d0008       ; recorrido (local, sin símbolo dinámico)
0x5d02cc  bl  0x5ac480       ; idem
0x5d02e4  bl  0x7789d4       ; visit() por nodo (vtable +0x10)
0x5d02f6  bl  0x5cfd78       ; cierre (local)
0x5d02fc  blx 0xe1058        ; ~ResourceUpdater()
```

## 9. Abierto

1. **`/usr` escribible**: si la partición es de solo lectura o está verificada, la sustitución de recursos exige
   un mecanismo de *overlay* (G8).
2. **Formato `.uxc`**: sin descifrar el *payload* de texto (`string_english.uxc` usa unidades de 16 bits no
   ASCII), no hay edición de cadenas (G2).
3. **Relación vista ↔ fichero**: qué `viewUnifiedN.so` sirve cada pantalla y cómo se declara en `master_*.uxc`.
4. **`swap`/framebuffer**: quién llama a `eglSwapBuffers`/`drawFramebuffer` y con qué *timing* (G3).
5. **Entrada**: `InputService` y `GestureAnalyzer` están identificados por símbolo, sin trazar la ruta física
   (teclas, rueda, táctil) (G6).
6. **Arranque**: qué script lanza `im.elf` (`startup_candidates` del inventario: 14 scripts; ninguno confirmado
   como lanzador).

## 10. Reproducibilidad

```bash
# inventario completo (libs + recursos + SHA-256)
.venv/bin/python scripts/gui/inventory.py --json analysis/gui/g01-inventory.json

# símbolos por capa
.venv/bin/python scripts/gui/elf_scan.py sym <libObj.so> '^_ZN2ux(6gfxeng|6resmgr|6wgtlay|4core)'

# tabla PLT completa / resolución de una llamada
.venv/bin/python scripts/gui/elf_scan.py plt <libObj.so>
.venv/bin/python scripts/gui/elf_scan.py resolve <libObj.so> 0xdb508

# desensamblado con nombres de importados
.venv/bin/python scripts/gui/elf_scan.py dis <libObj.so> 0x5d02a6 40

# verificación
.venv/bin/python -m pytest tests/test_gui_elf_scan.py -q
```
