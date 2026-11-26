# FILM-PB-1 / sub-arnés-lista-contenidos — la orden que llena la lista de la galería (26-11-2026)

Sesión: **26-11-2026** (reloj del anfitrión: 26-11-2026 00:14–00:35, −03). Cámara **no usada** (ni red, ni USB,
ni `adb`, ni flasheo): todo en `qemu-system-arm`. Direcciones = **VA del ELF** de fw 3.21
(`analysis/camera-extract/usr/lib/…`, `libmpr.so` SHA-256 `9a74a3bb…`); REA/Ghidra suman `+0x10000`.
Etiquetas: **V** = medido/leído en esta sesión · **D** = deducido · **NV** = no verificado.

Evidencia: [`evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/)
· cliente [`ctl.py`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/ctl.py)
· traza [`lc1-trazas.txt`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/lc1-trazas.txt)
· tarjeta [`tarjeta-emulada-mdir.txt`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/tarjeta-emulada-mdir.txt)
· comando [`comando.sh`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/comando.sh).

## 0. Veredicto

| Pregunta | Respuesta | Prueba |
|---|---|---|
| ¿Dónde se llenan los dos `PrmCntInfoList` del ctor (`viewUnified3+0x3A100`)? | **`viewUnified3+0x3F960`** (manejador de evento de modelo, virtual, tabla `0x68B4C`) escribe **`this+0x1B0` en `0x3FC3E`**; para `+0x11C` **no hay escritura** en `viewUnified3` (NV) | §1 |
| ¿Quién debería pedir la lista y con qué cadena? | el modelo **`@M015`** = `ModelIndexPb` (`libObj+0x598930`); la vista lo interroga con **`ViewBase::getModelInfo("@M015", 0xC04)`** y lee la clave **`0x11FFFD23`** (helper `0x3F684`) y **`0x11FFFF06`** con `0xC03` (en `0x3F960`) | §1 |
| ¿Y quién llama a `GetAVIndexContentInfoList` / `GetIndexFilteringInfo`? | **nadie en `libObj`** (no lo importa ningún `.so` salvo `libInfraScalarMpr.so`): el emisor real es **`libInfraScalarMpr.so`** (`MprCb_GetAVIndexContentInfoList` `0x1B198`, `CnvAviFileInfo_MprToInfra` `0x20D24`, `Api_GetAviData` `0x1E668`), cargado por **`libIMDB.so`** | §1.3 |
| ¿Por qué no se llama en el arnés? | la vista **abre, instancia y genera capa+layout sin cautela** (§3), pero **nadie rellena ninguna lista**: `PrmCntInfoList::add` = **0 disparos**, `0x3F684` = **0**, y **0** en los cuatro goznes del MPR y en `libInfraScalarMpr`/`libIMDB` (ambas **sí mapeadas**) | §2 |
| ¿Se consiguió ≥1 entrada? | **NO**. Sí se consiguió **`Vo 00000017` + `Lc Layer` + `Lc Layout` y `Vn 011` = 0** (la sesión anterior daba `Vo FFFFFFFF` + cautela) | §3 |
| Eslabón exacto que falta | **el modelo `@M015` nace y nadie lo alimenta**: su lista `[modelo+0x5C]` sigue vacía y no emite el evento que hace a la vista tirar de él. Detrás, el aviso de «AVI actualizado» (`Api_WaitAviUpdate` `0x1DEF4` / `Api_NotifyAviUpateComplete` `0x1CF2C`) tampoco ocurre | §4 |

## 1. Estático: el recorrido completo de la lista (V)

### 1.1 El ctor y sus dos listas — `viewUnified3.so+0x3A100`

```
3a112  add.w  r8, r5, #0x11c      3a134  add.w  r4, r5, #0x1b0
3a126  blx    PrmCntInfoList::C1Ev      (this+0x11C)
3a130  blx    CmnViewViewMode::C1Ev     (this+0x198)
3a13a  blx    PrmCntInfoList::C1Ev      (this+0x1B0)
3a142  blx    View::setModelRequest(1)  ← la vista PIDE modelo
```
Objeto de **0x218 B**; se instancia con la fábrica de la tabla de nombres al abrir `view/INDEX_PLAYBACK` (id `0x3F`).

### 1.2 Quién escribe las listas — `0x3F960` y sus ayudantes

`viewUnified3+0x3F960` (entrada de función según `.ARM.exidx`, puntero **`0x3F961`** en la tabla de manejadores
`0x68B4C`) recibe `(this, ParamList* del modelo)` y:

| VA | Qué hace |
|---|---|
| `0x3F978` | `PrmCntInfoList::GET(paramList, 3)` |
| `0x3F982/98C/996/9A0` | lee los enteros de claves 4, 5, 6, 7 |
| `0x3FA3C…0x3FA7C` | arma 6 parámetros `0x11FFFD0D`, `0x11FFFD0E`, `0x11FFFD1A`, `0x11FFFD19`, `0x11FFFD1B`, `0x11FFFD1C` |
| `0x3FAC2/0x3FAD0` | **`ViewBase::getModelInfo("@M015", 0xC03, &params)`** (cadena `@M015` en `0x53928`) |
| `0x3FADE/0x3FAE8` | `PrmCntInfoList::GET(paramList, 0x11FFFF06)` + `getLength()` |
| **`0x3FC3E`** | **`0x2FC6E(this+0x1B0, temp)`** ⇒ la lista `+0x1B0` se llena **aquí** |
| `0x3FC54` / `0x3FC5E` | `0x3CD60(this, &lista)` (PAS_Index: `setContentsAllGroupNum`, `setStartContentsID`, `setStartGroupInfo`, `setPreContentsID`) y `0x3CB8C` (lee Backup `0x01070042`) |

El ayudante **`viewUnified3+0x3F684`** = `getContentListFromModel(PrmCntInfoList& out)`:

```
3f6a8  getModelInfo("@M015", 0xC04, &ParamList vacía)
3f6b4  PrmCntInfoList::GET(paramList, 0x11FFFD23)     ← la LISTA que responde el modelo
3f6bc  getGroup(0) == -1  ⇒ devuelve 0 (lista vacía)
3f6ca  getItem(0)  == -1  ⇒ devuelve 0
3f6e0  0x2FC6E(out, lista) ; devuelve 1               ← la copia
```
Llamado desde `0x3F736`, `0x3F8CE` y `0x3FA96` (los tres en rutas de **evento de modelo / paginación**).
`viewUnified3+0x3F724` sólo manda trabajo al modelo **si la lista ya tiene algo**:
`requestModelExecute("@M015", 0xC09, {0x11FFFF03 = lista})` en `0x3F76C`.

⇒ **La vista no pide la lista al abrirse: la pide cuando el modelo le manda un evento.** Sin evento de modelo
no hay `+0x1B0`, y sin `+0x1B0` la galería no tiene nada que pintar (`Vo FFFFFFFF` o capa vacía).
**NV**: para `+0x11C` no aparece ninguna escritura en `viewUnified3`; los únicos `&this+0x11C` que existen
(`0x48F62`, `0x48FB2`) son de **otra** clase de vista y lo usan como dos enteros de `ViewBaseProduct::GetHighlightPos`.

### 1.3 El lado MPR: quién emite de verdad la orden (V)

| VA | Qué es |
|---|---|
| `libmpr+0x7203C0` | **`MprIf::GetAVIndexContentInfoList(m,m,m,m,void*,m)`** — el que pide la lista al MPR |
| `libmpr+0x7202C8` | `MprIf::GetIndexFiltering(m, EntryCondition, EntryId, m, list*, m)` |
| `libmpr+0x454162` / `0x6146A4` / `0x667BEC` | `FeaIf::GetIndexFilteringInfo` / `AviMMgr::GetIndexFilteringInfo` / `AviMMgrIf::…` |
| `libmpr+0x7352CC` | **`MprIfMcmd::GetAVIndexContentInfoList(long, char**)`** — el único llamador **directo** de `0x7203C0` dentro de `libmpr` (`0x735336`); es la vía **de diagnóstico por texto**: cadena `ex) MPR MMGRIF GetAVIndexContentInfoList` en `0x93007C` |
| `libInfraScalarMpr.so+0x1B198` | **`InfraScalarMprCore::MprCb_GetAVIndexContentInfoList(ObjMsg*, CallerInfo*, mediaId)`** — el que **importa** `MprIf::GetAVIndexContentInfoList` (símbolo indefinido, `.dynstr` `0xA6D3`) |
| `libInfraScalarMpr.so+0x1E668` | `InfraScalarMprCore::Api_GetAviData(ObjMsg*, unsigned)` — comprueba `[+0xC]==0x24` = `sizeof(MPR::AVIndexFileInfo)` |
| `libInfraScalarMpr.so+0x20D24` | `InfraScalarMprUtil::CnvAviFileInfo_MprToInfra(MPR::AVIndexFileInfo*, DefInfraScalarMpr::AviFileInfo*)` |
| `libIMDB.so` cadenas `0x34AE`/`0x34C3` | **`libInfraScalarMpr.so`** + **`InfraScalarMpr_Init`** ⇒ `libIMDB` es quien lo carga |

Barrido de los 157 `.so` de `/usr/lib`: **ningún** módulo del UI importa `GetAVIndexContentInfoList` ni
`GetIndexFilteringInfo`; sólo lo definen `libmpr.so` y lo importa `libInfraScalarMpr.so`.

## 2. Por qué no se llama en el arnés (V, medido)

Perfil propio corto **`lc1`** (puerto 8641, arranque en frío 165 s, 1,5 fps con la máquina cargada),
`estable.sh lc1 live`; trampas repetibles armadas con `TRACEFN2`/`TRACELIB`, `TRACEMAX=32`.
**Control positivo**: `libObj+0x7EED0C` (`AppSystem::dispatch`) → **103 disparos** ⇒ la maquinaria de trampas
funciona en esta sesión (y las 16 direcciones usadas pasaron `chequea_trampas.py` como ENTRADA).

| Punto | Qué es | Disparos |
|---|---|---:|
| `libObj+0x598930` | `ModelIndexPbToInstance` (fábrica del modelo `@M015`) | **1** (`r1 = 0x1F44258` = ModelManager, t=219 s, justo tras la 1.ª apertura) |
| `libObj+0x11D90E` | **`PrmCntInfoList::add(group,item)`** | **0** |
| `libObj+0x59934C` | respuesta del modelo a `0x11FFFD23` (lee `[modelo+0x5C]`) | **0** |
| `viewUnified3+0x3F684` | `getContentListFromModel` (la vista tira del modelo) | **0** |
| `viewUnified3+0x3F960` | manejador del evento de modelo (el que escribe `+0x1B0`) | **0** |
| `viewUnified3+0x3F724` / `0x3F8A0` | paginación / `requestModelExecute(0xC09)` | **0** |
| `libmpr+0x7203C0, 0x7202C8, 0x454162, 0x6146A4, 0x720A30, 0x71E9DC, 0x7352CC` | los cuatro goznes del índice AV + `GetContentInfo`, `GetContentCountSync`, `MprIfMcmd` | **0** |
| `libInfraScalarMpr+0x1E668, 0x1B198, 0x20D24, 0x1CF2C, 0x1DEF4, 0x1DDA8, 0x1E098` | `Api_GetAviData`, `MprCb_GetAVIndexContentInfoList`, conversión, `NotifyAviUpateComplete`, `WaitAviUpdate`, `CancelWait…`, `GetBufferThumbnail` | **0** |
| `libIMDB+0x24B0` | `IMDB_find_entry` | **0** |

Ninguna de las dos bibliotecas del proveedor está ausente: el invitado las tiene mapeadas y el shim lo imprime
al armar (`libInfraScalarMpr.so base 0x827c2000`, `libIMDB.so base 0xb6dd8000`).
Aviso de lectura: las líneas `TRACE 2bf05d0c` y `TRACE 6dc30d0c` del volcado **no** son de `libmpr`; son el
mismo `libObj+0x7EED0C` impreso con la `trc_base` de otra biblioteca (el shim usa una sola base global y yo
rearmé cinco veces en caliente).

Conclusión medida: **el modelo `@M015` se crea, pero ni se le pide la lista ni la pide él a nadie.** El eslabón
que falla no es un ACK del MPR perdido por el camino: **la orden no se emite en ningún punto del proceso**.

## 3. Lo que sí cambió con la tarjeta (V) — y lo que no

Tarjeta que ve el invitado (`$HOME/A6000-SD` → FAT32, [`tarjeta-emulada-mdir.txt`]):
`AVF_INFO/AVIN0001.INP` **512 B con 2 registros válidos** (`MP_ROOT/100ANV01/MAH04198.MP4` 14 540 590 B y
`MP_ROOT/103ANV01/MAH04198.MP4` 14 545 696 B), `AVIN0001.BNP` 512 B, `AVIN0001.INT` 256 B,
`PRV00001.BIN` 256 B, `PRIVATE/M4ROOT/CLIP/C0001.MP4` 14 540 590 B y `DCIM/100MSDCF/DSC00001..3.JPG`.

```
Vn 03F_viewUnified3.so : 20      Vo 00000017 : 12  (con Lc Layer y Lc Layout)
Vn 011_ (view/CAUTION) : 0       Vd 03F_     : 0
```
⇒ la galería **genera capa y maqueta y ya no saca la cautela**, al contrario que la medición del 26-11 por la
mañana (`Vo FFFFFFFF` + `Vn 011` a los ~3 s). Con la lista vacía la pantalla sigue **uniforme** (PNG
`01-index-con-M015.png` y `02-index-ahora.png`: 307 200 píxeles a `(0,0,0,0)`), así que **`Vo` no es prueba de
«hay contenido»**: es la capa/maqueta, no la lista.
No es atribuible al forzado: `M @M015` **falló** (`PRECREATE mm=0x1f44258 id=0x15` / `PRECREATE -> -1`: el
shim lee el argumento como hexadecimal y `@M015` no lo es). **D**: lo que cambió es la tarjeta (AVF_INFO
completo + clips reales + 3 JPG), no la maniobra.

## 4. Eslabón exacto y comando para reintentarlo

**Eslabón**: `libObj+0x59934C` (respuesta del modelo `@M015` a `0x11FFFD23`) y su origen de datos
`[modelo+0x5C]` → **`PrmCntInfoList::add` = 0**. Nadie alimenta al modelo, y el modelo no emite el evento que
hace a la vista tirar de él (`viewUnified3+0x3F684`). Detrás hay dos candidatos que tampoco se ejecutan:
**(a)** el aviso de AVI actualizado (`Api_WaitAviUpdate` `0x1DEF4` / `Api_NotifyAviUpateComplete` `0x1CF2C`), que
en la cámara llega del MPR al montar/enumerar el volumen — y el log real ya dice que **el IFO no se carga**
(`MountCmd : Flash Mount Error`, [sub-mount-ifo](film-pb-1-sub-mount-ifo-20261126.md)); **(b)** el cliente del
protocolo `InfraScalarMpr` que emite `Api_GetAviData`, que no está en `libObj` ni en ningún `.so` del UI.

**Herramienta que falta para forzarlo desde el shim (y por qué no se pudo probar hoy)**: `F <off>` **sólo llama
a `libObj`** (usa la base de `dlsym(lobj_h, …)`); no hay forma de invocar `libmpr` ni `libInfraScalarMpr`. Para
la próxima sesión basta un `G <off> a0..a3` gemelo de `F` con la base de `libmpr` (o de `TRACELIB`), en
`scripts/gui/harness/shim/sonyshim.c` (≈10 líneas junto a `fnhot`), y entonces:

```sh
# 0) tarjeta: MP_ROOT/103ANV01/MAH04198.MP4 (14 545 696 B) + MP_ROOT/100ANV01/MAH04198.MP4 (14 540 590 B),
#    AVF_INFO/{AVIN0001.INP,BNP,INT,PRV00001.BIN}, PRIVATE/M4ROOT/CLIP/C0001.MP4 y 3 JPG en DCIM/100MSDCF.
# 1) arranque (estable.sh; el perfil NO debe existir; nombre corto; sube solo LIVE_ARRANQUE_MAX con la carga)
TRACELIB=libObj.so TRACEFN2=11d90e,59934c,598930 TRACEREP=1 TRACEMAX=32 PUERTO=8642 \
SHIMEXTRA='WAITLOG=1000 LOGMARK=viewUnified,OPENHOT' \
  sh scripts/gui/harness/estable.sh lc2 live
# 2) a mano (otra terminal). Armar sólo entradas de función: chequea_trampas.py antes.
sh scripts/gui/harness/estable.sh lc2 arma 8642 "E WLALL=1"
sh scripts/gui/harness/estable.sh lc2 arma 8642 "E TRACELIB=libmpr.so"
sh scripts/gui/harness/estable.sh lc2 arma 8642 "E TRACEFN2=7203c0,7202c8,454162,6146a4"
sh scripts/gui/harness/estable.sh lc2 arma 8642 "O view/INDEX_PLAYBACK 0"
#    y con el `G` nuevo, la orden directa (equivalente al mando de consola de la cámara):
#    G 7352cc 0 0        → MprIfMcmd::GetAVIndexContentInfoList   (o G 7203c0 … con los 6 argumentos reales)
grep -ao "TRACE [0-9a-f]*" analysis/gui/g22/harness/live/lc2/shim.log | sort | uniq -c
```
**Criterio de éxito**: `TRACE 11d90e` ≥ 1 (alguien añade a una `PrmCntInfoList`), después `TRACE 3f684` ≥ 1 y
`Vo` distinto de `FFFFFFFF` **con** píxeles distintos en la captura (`sha256` ≠ `460199dbac0a…`), y `Vn 011` = 0.
**Criterio de fracaso**: sigue `11d90e` = 0 ⇒ el modelo no recibe datos y hay que atacar el montaje/IFO, no la
vista.

## 5. Límites / NO_VERIFICADO

- **NV** la escritura de `+0x11C`: no aparece en `viewUnified3`; puede hacerla el marco (`setModelRequest`) o el
  mismo `0x2FC6E` desde otro punto no localizado.
- **NV** qué mensaje concreto (`msgId` de `MWF`) lleva `Api_GetAviData`: no hay tabla de ids en `libInfraScalarMpr`
  que se pueda leer sólo con `.dynsym`; el cliente que lo emite no está en ningún `.so` del UI (¿`im.elf`?).
- **NV** que `libIMDB` sea el único cargador de `libInfraScalarMpr`: lo dice la cadena + `InfraScalarMpr_Init`, no
  una traza de `dlopen` propia (en esta sesión `dlopen` sólo se registró para `viewUnified3.so`, porque el
  registro del shim se encendió después del arranque).
- La máquina estaba **compartida** (otro arnés arrancando en paralelo): 1,5 fps y arranque de 165 s. Las trampas
  se armaron **en caliente** (§2) con control positivo; las que dependen de un instante del arranque
  (`Api_WaitAviUpdate`, montaje) pueden haber ocurrido antes de armarlas — hay que repetirlas **al arranque**
  (`TRACEFN2=…` en el entorno de `estable.sh`).
- `Vo` **no** se interpreta como «hay contenido»: con la lista vacía también sale `00000017` y capa/maqueta.
- No se ha tocado la cámara, ni `docs/`, ni `build/`, ni `tests/`; el shim es el de 21-11 (sin modificar). El
  perfil `lc1` queda en `analysis/gui/g22/harness/live/lc1/` (ignorado por git).

## 6. Evidencia

| Fichero | Contenido |
|---|---|
| [`lc1-trazas.txt`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/lc1-trazas.txt) | recuento de `TRACE` por dirección, los 8 armados con su base, `Vn 03F`/`Vo 00000017`/`Lc Layer`/`Lc Layout`, `dlopen`, `PRECREATE` fallido |
| [`tarjeta-emulada-mdir.txt`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/tarjeta-emulada-mdir.txt) | la FAT32 que recibe el invitado (2 registros del `.INP` + los 2 MP4 + `C0001.MP4` + 3 JPG) |
| `01-index-con-M015.png`, `02-index-ahora.png` | capturas tras abrir la galería: **uniformes** (307 200 px a `(0,0,0,0)`), documentan que la capa existe pero no hay nada que pintar |
| [`comando.sh`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/comando.sh) · [`ctl.py`](evidence/film-pb-1-sub-arnes-lista-contenidos-20261126/ctl.py) | comando y cliente del arnés |
