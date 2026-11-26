# G22-PBMODEL — qué es `@M010` y quién debe llenarlo (medido 26-11-2026)

**Estado: el eslabón está identificado con bytes; la rejilla sigue sin pintar y la medida en el invitado que
lo cierra está pendiente (§7).** La duda que dejó abierta
[G22-PLAYVIEW §8](g22-playview-tecla-abre-reproduccion.md) era «`@M010` se puede precrear pero
`getModelInfo("@M010", 1)` sigue devolviendo 0: el problema no es crearlo sino llenarlo». Este informe cierra
**qué** es `@M010` y **quién** debería llenarlo:

| # | Resultado | Etiqueta | Dónde |
|---|---|---|---|
| 1 | `@Mxxx` **no es un nombre**: es el id en hex. `IdGenerator::Get` (libObj+0x12d670) compara 5 B con `@MFFE` (el «sin id») y si no coincide compone `(d2<<8 | d3<<4) + d4` con `name[2..4]`: `@M010` = 0x10, `@M00A` = 0x0A | **V** | §2 |
| 2 | La tabla **id → clase** está en `libObj.so`, en una sola función Thumb (`libObj+0x401f78`) que por cada entrada llama `IdGenerator::Get("@Mxxx")` (PLT 0xdffb8) + `IdSoTable::add(id, "<clase>.so", "<Clase>ToInstance")` (PLT 0xdf58c): **259 entradas** volcadas | **V** | §3 |
| 3 | **`@M010` = clase `ModelBrowser`** (`modelBrowser.so` / `ModelBrowserToInstance`); la clase vive dentro de `libObj.so` (RTTI `12ModelBrowser`, cola `[M_Browser]`), el módulo de la tabla es el nombre de antes de la fusión | **V** | §3.1 |
| 4 | `model/INDEX_PB` = 0x15 = **`ModelIndexPb`** y `model/CONT_SHOTS_PB` = 0x2f = **`ModelContShotsPb`**: la tabla coincide con los tres ids medidos en el invitado (0x0A, 0x15, 0x2F) | **V** | §3.2 |
| 5 | `ModelBrowser` es un modelo **de petición/respuesta asíncrona**: guarda `StsContentInfoReady` (+0x110), `StsContentInfoResult` (+0x114), `RefCntContentInfo` (+0x118), `IsNeedOpeGetContentExist` (+0x124) y `ContentsExist` (+0x130), y habla por `MWF::ObjIf::IssueCommandSync/Async` + `BackupManager::Bkup_Read/Write` | **V** | §4 |
| 6 | El dato que le falta a ese modelo es la **lista de contenidos del índice AV** (`…ContentInfo…`): la produce `MprIf::GetAVIndexContentInfoList` (libmpr+0x7203c0) y **la empuja** a la capa Infra con `InfraScalarMprCore::MprCb_GetAVIndexContentInfoList`; ni `libObj` ni los modelos la llaman (0 importaciones) | **V** | §5 |
| 7 | Con el medio aceptado (`SD_MEDIA_CAB=0`) la rejilla **sigue sin pintar** y `getModelInfo("@M010", 1) = 0`: el eslabón que falta está en la cadena del índice, no en la vista | **M** | §6 |
| 8 | La medida de cierre (`opacos ≥ 0,05` y `listas > 0` al pulsar Reproducción) **no se ha conseguido** en esta sesión: los arranques se quedaron en la firma de G22-CUELGUE con dos invitados en la máquina | **M** | §7 |

Direcciones = VA del ELF de `libObj.so` 3.21 (en el 1.er `PT_LOAD` VA == desplazamiento). Etiquetas: **V** =
verificado en bytes/instrucciones · **M** = medido en el invitado · **D** = deducido · **NV** = no verificado.
Evidencia: [`reports/evidence/g22-pbmodel-20261128/`](../../reports/evidence/g22-pbmodel-20261128/).

---

## 1. Lo que ya estaba medido (no se repite)

De [G22-PLAYVIEW](g22-playview-tecla-abre-reproduccion.md): la tecla abre `view/INDEX_PLAYBACK` (acción 4 →
`openView` → `dlopen(viewUnified3.so)`), con `SD_MEDIA=1 SD_MEDIA_CAB=0` el medio se acepta
(`getModelInfo(model/MEDIA, 0) = 1`) y la vista pide `getModelInfo("@M010", 1)` (=0) y se queda sin listas. De
[G22-PBMEDIA](g22-pbmedia-indice-avf.md): el índice `AVF_INFO/AVIN0001.INP` va **sin** cabecera (vector puro de
registros de 0x80 B) y en los arranques medidos el invitado **no lee ni un sector de datos** de `AVF_INFO` y
`Fsys_FindFirst` (libmpr+0x13e474) no se dispara.

Lo que añade esta sesión es la mitad que faltaba: **quién es `@M010`** y **qué dato** le falta.

## 2. `@Mxxx` es el id escrito en hexadecimal (V)

`IdGenerator::Get(const char*)` = **`libObj+0x12d670`**. Si `name[0] == '@'` no consulta ninguna tabla: compara
5 B contra el literal de `libObj+0xbcf1e1` (`@MFFE`, el «sin id») y, si no coincide, toma `name[2]`, `name[3]` y
`name[4]` como dígitos hex y compone el número.

```
0012d674  0546      mov   r5, r0
0012d678  0378      ldrb  r3, [r0]           ; name[0]
0012d67a  402b      cmp   r3, #0x40          ; '@'
0012d67c  47d0      beq   0x12d70e
...
0012d70e  1b49      ldr   r1, [pc, #0x6c]    ; slot 0x12d77c -> 0xaa1acb ; +pc = 0xbcf1e1 "@MFFE"
0012d710  0522      movs  r2, #5
0012d712  7944      add   r1, pc
0012d714  b2f750ea  blx   0xdfbb8            ; compara 5 B con "@MFFE"
0012d718  b0b1      cbz   r0, 0x12d748       ; igual que @MFFE -> id = -1
0012d71a  ac78      ldrb  r4, [r5, #2]
0012d71c  402c      cmp   r4, #0x40
0012d71e  01d9      bls   0x12d724
0012d720  373c      subs  r4, #0x37          ; 'A'..'F' = c - 0x37
0012d724  303c      subs  r4, #0x30          ; '0'..'9' = c - 0x30
0012d728  2402      lsls  r4, r4, #8
...
0012d742  1419      adds  r4, r2, r4         ; id = (d2<<8) + (d3<<4) + d4
0012d744  e418      adds  r4, r4, r3
```

Consecuencia práctica: **`@M010` = 0x10 por construcción** (no hay tabla de nombres cortos que consultar) y
`@MFFE` = -1 es el centinela. Encaja con lo medido por la orden `M <nombre>` del shim
([G22-PLAYVIEW §8](g22-playview-tecla-abre-reproduccion.md)): `M @M010` → id 0x10, `M model/INDEX_PB` → 0x15.

## 3. La tabla id → clase de los modelos vive en `libObj` (V)

La función que registra los modelos es **`libObj+0x401f78`** (`push.w {r4-r11,lr}` + `sub sp,#0x54`). Por cada
modelo hace lo mismo que el registro de vistas de
[G22-PBVISTA §2](g22-pbvista-carga-bajo-demanda.md) pero con la tabla de modelos:

```
0040210c  8048      ldr   r0, [pc, #0x200]   ; slot 0x402310 -> 0x8ba920 ; +pc = 0xcbca32 "@M010"
0040210e  7844      add   r0, pc
00402110  ddf452ef  blx   0xdffb8            ; IdGenerator::Get("@M010") -> 0x10
00402114  7f4b      ldr   r3, [pc, #0x1fc]   ; -> 0xcbca38 "modelBrowser.so"
0040211a  1a46      mov   r2, r3
0040211c  7e4b      ldr   r3, [pc, #0x1f8]   ; -> 0xcbca48 "ModelBrowserToInstance"
00402122  0146      mov   r1, r0             ; id
00402124  2046      mov   r0, r4             ; ModelIdSoTable::getInstance()
00402126  ddf432ea  blx   0xdf58c            ; IdSoTable::add(id, "modelBrowser.so", "ModelBrowserToInstance")
```

El pozo de `.rodata` en `0xcbca32` es literal: `"@M010\0modelBrowser.so\0ModelBrowserToInstance\0@M011\0…"`.

**Volcado completo** (259 entradas, resueltas emulando los registros del idioma `ldr rX,[pc]` + `add rX,pc`):
[`tabla-modelos-libobj.txt`](../../reports/evidence/g22-pbmodel-20261128/tabla-modelos-libobj.txt).

### 3.1 `@M010` es la clase `ModelBrowser`, no un `modelBrowser.so` (V)

* RTTI `12ModelBrowser` en `libObj+0xcdf62c`; cola de log `[M_Browser] %s() ModelBrowser Info` en `libObj+0xcdf695`.
* No hay `modelBrowser.so` en `/usr/lib` (solo `viewUnified2..8.so`, `ModelCautionConfig.so`, `cmnviewViewModel.so`…):
  el build fusionó los modelos dentro de `libObj.so`, igual que fusionó las vistas. El nombre del módulo de la
  tabla es el de antes de la fusión y el cargador resuelve la fábrica por símbolo **exportado** del propio
  `libObj.so` (`ModelBrowserToInstance` = `libObj+0x47fa79`, bit Thumb).
* Fábrica: `new(0x134)` + constructor `libObj+0x47fa48`; el objeto mide **0x134 B**:
  [`modelbrowser-clase-y-fabrica.txt`](../../reports/evidence/g22-pbmodel-20261128/modelbrowser-clase-y-fabrica.txt).

```
0047fa78  b0b5      push  {r4,r5,r7,lr}
0047fa7a  4ff49a70  mov.w r0, #0x134      ; sizeof(ModelBrowser)
0047fa82  5cf43eeb  blx   0xdc100          ; operator new
0047fa88  fff7deff  bl    0x47fa48         ; ModelBrowser::ModelBrowser()
0047fa8c  2562      str   r5, [r4, #0x20]  ; [objeto+0x20] = argumento de la fábrica
```

### 3.2 Tres coincidencias que cierran el significado de la tabla (V+M)

| nombre | id en la tabla | clase | id medido en el invitado |
|---|---|---|---|
| `model/MEDIA` | 0x0A (`@M00A`) | `ModelMedia` | 0x0a ([G22-PBMEDIA](g22-pbmedia-indice-avf.md)) |
| `model/INDEX_PB` | 0x15 (`@M015`) | `ModelIndexPb` | 0x15 (§8 de G22-PLAYVIEW) |
| `model/CONT_SHOTS_PB` | 0x2F (`@M02F`) | `ModelContShotsPb` | 0x2f (§8 de G22-PLAYVIEW) |
| `@M00F` | 0x0F | `ModelStillRec` | 0x0f (comentario del shim, `PRECREATE`) |

Es decir: **`@M010` no es `model/INDEX_PB`** (ese es `ModelIndexPb`, 0x15) ni `model/CONT_SHOTS_PB`
(`ModelContShotsPb`, 0x2F). Es el **modelo navegador** (`ModelBrowser`), el que calcula las *condiciones* de la
rejilla (grupo, orden, agrupación de ráfagas, filtros…) y pide la **lista de contenidos** al que la tenga.

## 4. `ModelBrowser` es un modelo asíncrono con un `ContentInfo` que alguien debe servir (V)

`ModelBrowser::ActionTestCmdDebugPrint` (`libObj+0x4802b8`) imprime su estado completo; los campos y sus
desplazamientos en el objeto salen de las cargas que acompañan a cada línea:

| campo | offset | qué es |
|---|---|---|
| `CurrentState`, `CmdEnable`, `StatusView`, `SetViewResult` | — | estado de la petición en curso |
| `MedType`, `CntType`, `GrpCond`, `SortType`, `LumpContShots`, `HighlightEdited`, `FlatRequest`, `3DContents` | — | **condiciones** que pide la vista |
| `StsContentInfoReady` | **+0x110** | 1 = la lista de contenidos está lista |
| `StsContentInfoResult` | **+0x114** | resultado de la petición |
| `RefCntContentInfo` | **+0x118** | cuántos la tienen pedida |
| `IsNeedOpeGetContentExist` | **+0x124** | 1 = hay que preguntar «¿hay contenidos?» |
| `ContentsExist` | **+0x130** | 1 = la tarjeta tiene contenidos |
| `CreateCond : *`, `FilterCond : StartTime/EndTime`, `ContShotsCond` | — | condiciones de creación y filtros |

Y sus dependencias (símbolos de la PLT que usan las funciones de `libObj+0x47f600..0x482600`) son las de un
modelo de petición/respuesta:

```
MWF::ObjIf::IssueCommandSync(void*, MWF::ObjMsg*, MWF::ObjMsg*)
MWF::ObjIf::IssueCommandAsync(void*, MWF::ObjMsg*)
MWF::ObjMsg::SetCateIdMsgId(unsigned, unsigned) · GetCategoryId() · GetMessageId()
MWF::ParamStd_Template<unsigned, (MWF::Param::Type)8>::~ / ::ParamStd_Template
BackupManager::Bkup_Read(int, void*) · BackupManager::Bkup_Write(int, void const*)
ParamList::add · ParamList::~ParamList
```

Es decir: **`ModelBrowser` no lee el índice AV ni el sistema de ficheros**; manda `ObjMsg` a un objeto (el del
medio / la base de contenidos), guarda el resultado en su `ContentInfo` y responde a la vista cuando
`StsContentInfoReady = 1`. El setter de ese campo es `libObj+0x482248` (`str.w r1,[r0,#0x110]`), que no tiene
**ningún** `bl` en `.text` (267 567 `bl` T1 contadas): se llega a él por la tabla de métodos del modelo
(`.data.rel.ro` `0x1000a18..0x1000a50`, 11 punteros a `0x47f6xx..0x47fcfd`), no por llamada directa.

## 5. Quién produce la lista de contenidos del índice AV (V)

El API de «content info» del índice AV está en `libmpr` y lo envuelve `libInfraScalarMpr`:

| símbolo | dónde | qué hace |
|---|---|---|
| `MprIf::GetAVIndexContentInfoList(u32,u32,u32,u32,void*,u32)` | `libmpr+0x7203c0` | **petición** de la lista de contenidos del índice |
| `InfraScalarMprCore::MprCb_GetAVIndexContentInfoList(MWF::ObjMsg*, InfraScalarMprCore::CallerInfo*)` | `libInfraScalarMpr` (exportada) | **callback**: MPR *empuja* la lista a la capa Infra |
| `InfraScalarMprUtil::CnvAviFileInfo_MprToInfra(MPR::AVIndexFileInfo*, DefInfraScalarMpr::AviFileInfo*)` | `libInfraScalarMpr` | convierte cada registro `AVIndexFileInfo` (los 0x80 B de `AVIN0001.INP`) |

Comprobaciones de bytes:

* `GetAVIndexContentInfoList` **solo** aparece en `libmpr.so` (definición) y `libInfraScalarMpr.so` (importación).
  **`libObj.so`, `libScalarDaemon.so` y los `viewUnifiedN.so` no la importan**: ningún modelo la llama.
* `MprCb_GetAVIndexContentInfoList` **solo** aparece en `libInfraScalarMpr.so` (definición y registro): el que
  llama al callback es `libmpr`, es decir la lista **llega** desde MPR cuando MPR lee el índice.

Con esto la cadena queda: `AVIN0001.INP` → `libmpr` (lector `CS_AviFileIf`/`smf_avi_*`) →
`MprCb_GetAVIndexContentInfoList` → `DefInfraScalarMpr::AviFileInfo` → objeto del medio → `ObjMsg` de respuesta →
`ModelBrowser::StsContentInfoReady = 1` → `getModelInfo("@M010", 1) = 1` → rejilla con miniaturas.

## 6. Medido en el invitado: el medio se acepta y `@M010` sigue en 0 (M)

Con `SD_MEDIA=1 SD_MEDIA_CAB=0` (índice sin cabecera) y la receta de la tecla, el medio se acepta
(`getModelInfo(model/MEDIA, 0) = 1`, [G22-PLAYVIEW §6](g22-playview-tecla-abre-reproduccion.md)) pero al abrir
`view/INDEX_PLAYBACK` la petición del modelo navegador sigue vacía:

```
getModelInfo(@M010, 1) -> 0   (x5)
fotograma: 0 listas · opacos 0,0
```

La lectura de esta sesión: **el 0 no es de la vista ni del modelo** (ambos existen y la petición llega), sino
del `ContentInfo` que nadie ha servido, porque el lector del índice AV no se ejecuta en el arnés
([G22-PBMEDIA §4.2](g22-pbmedia-indice-avf.md): 0 lecturas de datos de la SD y 0 disparos de `Fsys_FindFirst`).

## 7. Lo que falta y cómo se cierra

1. **Medir `StsContentInfoReady`**: con el modelo creado, `G @M010 0x17` (orden nueva del shim, §8) devuelve el
   código que responde y cuántos parámetros trae; el código que en la cámara devuelve la lista debe dar 0 aquí.
   Es la medida que separa «no hay lista» de «la lista está vacía».
2. **Ver si el índice se lee con el medio aceptado**: `TRACELIB=libmpr.so` en el arranque y
   `E TRACEFN2=7203c0,13e474` en caliente (armar **después** de tener OSD, para no interferir en el arranque),
   más `SDIO=20000` para ver sectores de datos. Si `Fsys_FindFirst` sigue a 0, el eslabón es el lector del índice
   y hay que atacarlo en `libmpr` (`CS_AviFileIf`, `smf_avi_*` en `libmpr 0x1d13xx`), no en la UI.
3. **Si el índice se lee y el modelo sigue a 0**: el eslabón es el `ObjMsg` de respuesta al navegador; el
   `IMCMDLOG=1` del shim ya registra categoría, id y llamante de cada `IssueCommandAsync`
   (`docs/gui/g22-respuesta-efcs-objcamera.md`), así que la medida es un arranque con `IMCMDLOG=1` y la tecla.
4. La medida de cierre de G22-REPRO sigue siendo la de siempre: `getModelInfo("@M010", 1) → 1` **y** `/estado`
   con `opacos ≥ 0,05` y `listas > 0` tras pulsar Reproducción, con PNG antes/después y su diff.

## 8. La orden de diagnóstico `G` del shim (nueva, inerte)

`«G modelo [max]»` por `/linea` (o `e2e_drv.py … linea=G\ @M010`) sondea
`viewManagerIf::getModelInfo(modelo, código)` para los códigos `0…max` (0x17 por omisión) con una lista propia y
registra, por código, el retorno y cuántos parámetros trae:

```
[shim] G @M010 codigos 0…0x17
[shim] G @M010 codigo 0x0 -> 1
[shim] G   @M010 0x0: 3 parametros [4/62/0] [4/63/0] [4/64/1]
...
```

* Solo lee: no escribe memoria del invitado, no lee variables de entorno y no se arma en el arranque
  (`tests/test_g22_pbmodel.py::test_la_orden_g_del_shim_solo_lee`).
* Sirve para separar «el modelo no existe» de «existe y ese código no tiene dato», que es justo lo que faltaba
  para no confundir el 0 de `@M010` con un fallo de creación.

```sh
# arranque medido (perfil y puerto propios; cerrar con POST /salir)
cd /home/nicolas/hv/harness && rm -rf live/pbmodel
SD_MEDIA=1 SD_MEDIA_CAB=0 SHIMEXTRA='PLAYVIEW=1 INSHORT=1 GMILOG=1 WAITLOG=3000 WLALL=1' \
  LIVE_ARRANQUE_MAX=200 LIVE_REINTENTOS=4 \
  /home/nicolas/a6000-arnes/.venv/bin/python <repo>/scripts/gui/harness/live.py /home/nicolas/hv/harness \
  --perfil-dir pbmodel --puerto 8697 --config /tmp/final/cfg.json
# con /estado en opacos ≥ 0,05 y listas ≥ 20:
.venv/bin/python scripts/gui/harness/e2e_drv.py 8697 'linea=G @M010' png=/tmp/a.png esp=1 reproduccion esp=16 png=/tmp/b.png
curl -s http://127.0.0.1:8697/estado
curl -s -X POST http://127.0.0.1:8697/salir
```

## 9. Evidencia

| fichero | qué es |
|---|---|
| [`tabla-modelos-libobj.txt`](../../reports/evidence/g22-pbmodel-20261128/tabla-modelos-libobj.txt) | las 259 entradas `@Mxxx → módulo → constructor` de `libObj+0x401f78`, con los ids ya resueltos |
| [`idgenerator-get.txt`](../../reports/evidence/g22-pbmodel-20261128/idgenerator-get.txt) | `IdGenerator::Get` (`+0x12d670`) desensamblado y el literal `@MFFE` de `0xbcf1e1` |
| [`modelbrowser-clase-y-fabrica.txt`](../../reports/evidence/g22-pbmodel-20261128/modelbrowser-clase-y-fabrica.txt) | RTTI y cola de log de `ModelBrowser`, fábrica `+0x47fa78` (`new(0x134)`), constructor, los campos del volcado y los símbolos de PLT que usa |
| [`arranques-con-dos-vm.txt`](../../reports/evidence/g22-pbmodel-20261128/arranques-con-dos-vm.txt) | los arranques de esta sesión que se quedaron en G22-CUELGUE por tener dos invitados en la máquina |

Tests sin QEMU: `tests/test_g22_pbmodel.py` (8 casos) — la regla `@Mxxx` = id, la entrada `@M010` de la tabla,
las tres coincidencias con ids medidos, la clase y la fábrica, y que la orden `G` es inerte.
