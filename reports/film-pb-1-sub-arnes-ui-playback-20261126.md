# FILM-PB-1 / sub-arnés-ui-playback — abrir y mantener `view/INDEX_PLAYBACK` (arnés QEMU, sin cámara)

Sesión: **26-11-2026** (reloj del anfitrión: 25-11-2026 23:31–23:52, −03). Cámara: **no usada**.
Espacio de direcciones: **VA del ELF** (`analysis/camera-extract/usr/lib/…`, fw 3.21); REA/Ghidra suman `+0x10000`.
Evidencia: [`evidence/film-pb-1-sub-arnes-ui-playback-20261126/`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/)
· cliente [`ctl.py`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/ctl.py)
· traza [`traza-vista-indice.txt`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/traza-vista-indice.txt)
· sonda [`sonda-funceventmode.txt`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/sonda-funceventmode.txt).

---

## 0. Veredicto

| Pregunta | Respuesta | Prueba |
|---|---|---|
| ¿`INDEX_PLAYBACK` «se cierra en 10 ms»? | **NO. Esa lectura era falsa** | `grep -ac 'B  Vd 03F_'` = **0** en toda la sesión (4 aperturas, `B  Vn 03F_` ×4); el `B`/`E` que se leía como «abre/cierra» es el **ámbito de instanciación** de la vista (`Vn`), no su vida |
| ¿Sigue abierta y es la vista de arriba? | **SÍ** | sonda `F 125104` (`getCurrentFuncEventMode`) = **0x15** con `INDEX_PLAYBACK` arriba 560 s después de abrirla; **0x1** al abrir `STLREC` encima |
| ¿Qué se cierra, entonces? | **`view/CAUTION` (id 0x11)**, no la vista de reproducción | `B Vn 011_` ×4 · `B Vd 011_` ×4 · `ViewBase::Exit()` (libObj+0x120A5E) sobre el objeto 011, ~3 s tras abrir |
| ¿Por qué la pantalla queda uniforme? | la vista **no produce capa/layout**: `Vo FFFFFFFF`; sólo la cautela produce `Vo 0000003B` | [`traza-vista-indice.txt`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/traza-vista-indice.txt) |
| ¿Se puede dejar abierta **con ≥1 entrada**? | **NO con lo medido**: la lista de contenidos del modelo está vacía y nadie la pide | `GetAVIndexContentInfoList` / `GetIndexFilteringInfo` = **0 llamadas** (medición del subagente hermano, coincide con mi traza: no hay `dlopen(modelIndexPb.so)` ni peticiones a `MP_ROOT`) |
| ¿Eslabón que falta? | **índice AV → lista de contenidos → evento de modelo a la vista** (§4) | — |

---

## 1. Corrección de método: qué es `B … E  Vn 03F_viewUnified3.so`

La sesión anterior ([sub-arnés-galeria §3.2](film-pb-1-sub-arnes-galeria-20261126.md)) leyó
`83 B  Vn 03F_…` → `83 E  Vn 03F_…` (10 ms) como «la vista abre y se cierra». Es un **ámbito de
instanciación**: el mismo par B/E lo produce `view/STLREC` (id 0x88), que se queda **toda la sesión**.
Las cadenas de formato están en `libObj.so`: `Vn %03X_%s` (`0xD8835E`), `Vd %03X_%s` (`0xD8826B`),
`Vo %08X`, `%s %03X_%s` — `Vn` = vista nueva, `Vd` = vista destruida, `Vo` = apertura (capa/layout).

Recuento sobre `live/uilive/shim.log`, canal `LOGMARK` (una línea por evento; `B`/`E` van en pareja,
así que cada `B … Vn` es una instanciación) — 4 aperturas forzadas de la galería:

```
B Vn 03F (INDEX_PLAYBACK): 4      B Vd 03F: 0
B Vn 011 (CAUTION)       : 4      B Vd 011: 4
B Vn 088 (STLREC)        : 1      B Vd 088: 0
```

`view/INDEX_PLAYBACK` **nunca se destruye**. Lo que se abre y se cierra es **`view/CAUTION`**.

### Los ids de vista son el índice de la tabla de nombres (VERIFICADO)

`viewUnified2.so` lleva la tabla `"view/NAME" · "viewXxx.so" · "ViewXxxToInstance"` a partir de
`0x3A01E8`; el id que imprime la traza es **la posición en esa tabla**. Ojo al contarla: hay entradas
sin nombre (`viewScalar.so`, `viewStlrec.so`, `viewSinglePb.so`…) y **una entrada con nombre pero sin
`.so` ni fábrica**, `view/SCALARDUMMY1` (`…view/SCALARDUMMY1\0view/SCNSELECTION\0viewScnSelection.so…`,
alias de `viewScalardummy.so`); saltársela desplaza todos los ids ≥ `0x73` en uno:

| id | entrada | comprobación |
|---|---|---|
| `0x0E` | `view/BASE_MENU` | coincide con el comentario del shim (`@V00E`) |
| `0x3F` | `view/INDEX_PLAYBACK` | `Vn 03F_viewUnified3.so` |
| `0x88` | `viewStlrec.so` | `Vn 088_viewUnified2.so` |
| `0x80` | `viewSinglePb.so` (sin nombre en la tabla) | `Vn 080_viewUnified2.so` |
| `0x7C` | `view/SETTINGMENUX` | `@V00E → SETTINGMENUX 0x7C` (shim) |
| `0x11` | **`viewCaution.so`** | `Vn 011_viewUnified2.so` justo después de abrir la galería |

---

## 2. Secuencia real medida (una apertura cualquiera; las cuatro son idénticas)

```
[shim] TRACE 1251fc      r0=8d8b30 r1=0            ← viewManagerIf::openView("view/INDEX_PLAYBACK", 0)
       OPENHOT view/INDEX_PLAYBACK 0 -> 8238904
       LOG   83 B  Vn 03F_viewUnified3.so          ← se INSTANCIA ViewIndexPb (fábrica ViewIndexPbToInstance)
[shim] TRACE 7f1b3c      r0=56575348               ← View::View(ViewManager*) del objeto 03F
       LOG   83 E  Vn 03F_viewUnified3.so
       LOG   83 B  Vo FFFFFFFF                     ← la apertura de 03F NO produce capa/layout
       LOG   83 E  Vo FFFFFFFF
       LOG   83 B  Vn 011_viewUnified2.so          ← el marco abre view/CAUTION (0x11) 0,4 s después
[shim] TRACE 7f1b3c      r0=56574f90
       LOG   83 E  Vn 011_viewUnified2.so
       LOG   83 B  Vo 0000003B                     ← la cautela sí trae capa+layout (Lc Layer / Lc Layout)
[shim] TRACE 120a5e      r0=56574f90 r1=3          ← ViewBase::Exit() de la cautela (sin argumentos: r1 es basura)
       LOG   83 E  Vo 0000003B
[shim] TRACE 120a5e      r0=56574f90 r1=0 r2=1    ← ViewBase::Exit() otra vez, ya en el desmontaje
       LOG   83 B  Vd 011_viewUnified2.so          ← se DESTRUYE la cautela (~3 s después)
       LOG   83 E  Vd 011_viewUnified2.so
       … VdfIf cpp:283  should update because the internal handle is different …
```

**No hay ninguna línea `Vd 03F_`**: el objeto `ViewIndexPb` (0x218 B, ctor `viewUnified3+0x3A100`, que
construye dos `PrmCntInfoList` en `+0x11C` y `+0x1B0` y llama `View::setModelRequest(true)` en
`+0x3A142`) sigue vivo y **es la vista de arriba**: la sonda lo confirma.

### Sonda de estado (nueva, reutilizable)

`F 125104` llama a `viewManagerIf::getCurrentFuncEventMode()`, que recorre la pila de vistas
(`[pViewManager]` = nº, `[pViewManager+0x24]` = array de 0x10 B, de arriba abajo, `libObj+0x7F25A4`)
y devuelve el modo de la primera vista viva:

```
863.88  F -> 0x15     # INDEX_PLAYBACK arriba, 560 s después de abrirla y con la cautela ya retirada
870.34  F -> 0x1      # tras «O view/STLREC 3»: manda STLREC
```

### Capturas

| PNG | Qué se ve |
|---|---|
| [`01-stlrec.png`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/01-stlrec.png) | pantalla de disparo con OSD parcial (23 s tras el primer fotograma) |
| [`04-index-1s.png`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/04-index-1s.png) / [`05-index-5s.png`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/05-index-5s.png) | **uniformes** (0 píxeles ≠ 0), idénticas entre 1 s y 5 s: `sha256 460199dbac0a…` — el mismo hash que la sesión anterior llamó «blanca» |
| [`06-index-tras-caution.png`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/06-index-tras-caution.png) | igual, ya retirada la cautela |

La pantalla uniforme **no** es «vista cerrada»: es la vista de índice sin contenido y sin capa
(`Vo FFFFFFFF`). La anterior la describió como blanca porque el búfer RGBA4444 uniforme se
interpreta así; los valores son 0 (negro) en mi lectura.

### Matiz medido: `view/SINGLEPB` sí se retira sola (y tampoco es «10 ms»)

`O view/SINGLEPB 0` (id 0x80) produce una secuencia **distinta** de la del índice:

```
OPENHOT view/SINGLEPB 0 -> 8238904
       LOG   83 B  Vn 080_viewUnified2.so          ← se instancia ViewSinglePb
[shim] TRACE 7f1b3c      r0=552ffdf8
       LOG   83 B  Vo 00000015                     ← SÍ produce capa/layout
       LOG   83 B  Lc Layer …  Lc Layout           ← la conversión de layout tarda ~2,4 s
[shim] TRACE 120a5e      r0=633d0828 r1=4          ← ViewBase::Exit() de la vista anterior (STLREC)
[shim] TRACE 120a5e      r0=552ffdf8 r1=1          ← ViewBase::Exit() de la propia SINGLEPB
       LOG   83 E  Vo 00000015
```

No hay `Vn 011` (no saca cautela) ni `Vd 080` (el objeto sigue vivo, en caché). Es decir:
`SINGLEPB` **abre con capa y se retira a los ~2,4 s**, que sigue sin ser «10 ms» y no es una
destrucción. Sin una entrada que mostrar, la vista no tiene nada que pintar y se va sola.

---

## 3. Por qué la vista de índice no pinta: la lista de contenidos está vacía

- El ctor de `ViewIndexPb` (`viewUnified3+0x3A100`) crea **dos** `PrmCntInfoList` (`+0x11C`, `+0x1B0`)
  y un `CmnViewViewMode` (`+0x198`), y activa `setModelRequest(true)` ⇒ la vista **pide modelo**.
- No se instancia ningún modelo al abrir: `ModelIndexPbToInstance` (`libObj+0x598930`) y
  `ModelCautionToInstance` (`libObj+0x4EF7E4`) armados con `TRACEFN` en caliente → **0 disparos**;
  tampoco aparece `dlopen(modelIndexPb.so)`. El modelo, o no existe, o existe con la lista vacía.
- Medición del subagente hermano (misma tarjeta, mismo `.INP` corregido): el invitado **sólo** pide
  `ms:/AVF_INFO`, `ms:/AVF_INFO/PRV00001.BIN` y `ms:/AVF_INFO/AVIN0001.INP`; **cero** peticiones de
  `MP_ROOT`/`MAH04198.MP4`; `avi_man_NewAviFileManager` se instancia 3 veces pero
  **`GetAVIndexContentInfoList` y `GetIndexFilteringInfo` se llaman 0 veces**.
- Direcciones del puente que falta (para el siguiente paso, `libmpr.so`):
  `MprIf::GetAVIndexContentInfoList(m,m,m,m,void*,m)` = `+0x7203C0`;
  `MprIfMcmd::GetAVIndexContentInfoList(long,char**)` = `+0x7352CC`;
  `FeaIf::GetIndexFilteringInfo` = `+0x454162`; `AviMMgr::GetIndexFilteringInfo` = `+0x6146A4`;
  `AviMMgrIf::GetIndexFilteringInfo` = `+0x667BEC`.

⇒ **Eslabón exacto que falta**: nadie convierte el índice AV en *lista de contenidos* y nadie se la
entrega al modelo; sin lista, `PrmCntInfoList` queda vacía, la vista no genera capa (`Vo FFFFFFFF`)
y el marco saca la **cautela 0x11** (`Vo 0000003B`) que se retira sola. No es un timeout, ni una
transición sin confirmar, ni un ACK perdido: es un **modelo sin datos**.

---

## 4. Secuencia que mantendría la vista abierta (criterio y candidatos)

La vista sólo se queda «llena» cuando su lista de contenidos tiene ≥1 entrada. La secuencia que hay
que conseguir, en este orden, y cómo se verifica cada paso:

1. **Construir la lista** (hoy 0 llamadas): ordenar al MPR el índice AV →
   `MprIf::GetAVIndexContentInfoList` (`libmpr+0x7203C0`) y/o `GetIndexFilteringInfo`
   (`+0x454162`/`+0x6146A4`). Criterio: `grep -c 'TRACE 7203c0'` ≥ 1 con la tarjeta presente.
2. **Entregarla al modelo** (`ModelIndexPb`) con su evento de actualización. Criterio: `Vn 03F` va
   seguido de un `Vo` con **número distinto de `FFFFFFFF`**.
3. **Abrir la vista** (`O view/INDEX_PLAYBACK 0`, o la tecla `0x1f7` cuando el parche de menú/teclas
   esté hecho) y comprobar que la pantalla deja de ser uniforme: `sha256` distinto de
   `460199dbac0a…` y `grep -c 'Vn 011_'` **no** aumenta (no debe salir cautela).

Candidatos ya disponibles en el shim (sin recompilar), por orden de coste:

- `E TRACELIB=libmpr.so` + `E TRACEFN2=7203c0,454162,6146a4,667bec` → medir quién llama (o que
  nadie llama) a la construcción de la lista; **sólo entradas de función**.
- `X model/… <código>` (`viewManagerIf::requestModelExecute`) y `M <modelo>` (`PRECREATE`) para
  forzar el modelo del índice antes de abrir; `A <i>` (`acquireStatus`) si el modelo existe pero
  está «sin estado».
- `S <id>[:modelo]` (`ModelManager::pushEvent`) para inyectar el evento de modelo ya construido;
  `Z <msgid>` para la orden a `ObjCamera` (`8:3100`).
- `F <off>` sólo sirve para `libObj` (usa la base de `libObj`): **no** puede llamar a `libmpr`, así
  que la lista no se puede fabricar hoy con `F`.

---

## 5. Comando exacto para repetirlo

```sh
# 0) tarjeta y perfil (nombre CORTO: el socket de control tiene 108 B)
H=/tmp/uilive/home
mkdir -p $H/A6000-SD/{DCIM/100MSDCF,MP_ROOT/103ANV01,AVF_INFO}
cp -n /home/nicolas/Documents/a6000/MAH04198.MP4 $H/A6000-SD/MP_ROOT/103ANV01/
cp -n reports/evidence/film-pb-1-sub-avin-20261127/AVIN0001_sintetico.INP $H/A6000-SD/AVF_INFO/AVIN0001.INP

# 1) arnés (una terminal; arranque en frío ≈ 150–190 s hasta la primera pantalla)
HOME=$H SD_ESTRUCTURA=1 LIVE_REINTENTOS=1 \
SHIMEXTRA='WAITLOG=800 LOGMARK=viewUnified,Vd,OPENHOT TRACEFN=1251fc,120a5e,7f1b3c TRACEREP=1 TRACEMAX=16' \
.venv/bin/python3 scripts/gui/harness/live.py analysis/gui/g22/harness --perfil-dir uilive --puerto 8633

# 2) abrir la galería y sondear el estado (otra terminal)
C=reports/evidence/film-pb-1-sub-arnes-ui-playback-20261126/ctl.py
.venv/bin/python3 $C esperafotograma 300
.venv/bin/python3 $C linea "E WLALL=1"            # LOG del firmware → shim.log (¡frena! apagar después)
.venv/bin/python3 $C linea "O view/INDEX_PLAYBACK 0"
.venv/bin/python3 $C linea "F 125104"             # 0x15 = la vista de índice está arriba
.venv/bin/python3 $C refrescar
.venv/bin/python3 $C captura /tmp/index.png       # uniforme = sin capa
.venv/bin/python3 $C linea "E WLALL="             # quitar con valor VACÍO (VERB=0 NO lo apaga)

# 3) leer
grep -a 'Vn 03F\|Vn 011\|Vd 011\|Vo ' analysis/gui/g22/harness/live/uilive/shim.log
grep -ac 'Vd 03F_' analysis/gui/g22/harness/live/uilive/shim.log      # 0 = no se destruye
```

Avisos de método medidos aquí: `E VERB=0` **deja VERB encendido** (`getenv` devuelve `"0"`, que es
cierto); para apagarlo hay que escribir `E VERB=` (valor vacío). `WLALL=1` inunda `shim.log` y frena
el arranque: encenderlo sólo durante la maniobra.

---

## 6. Límites / NO_VERIFICADO

- **NO_VERIFICADO** que la tarjeta que ve el invitado en esta sesión sea la de `$H/A6000-SD`: otro
  subagente mide que con `HOME=/tmp/...` la tarjeta sale **vacía** (la ruta por defecto es
  `~/A6000-SD`). No afecta a las conclusiones de §1–§3 (la vista no pinta por falta de lista, no por
  falta de fichero), pero **sí** al criterio «≥1 entrada»: hay que repetir con la tarjeta verificada.
- **NO_VERIFICADO** el significado exacto del número de `Vo %08X` (no es el id de vista: `03F` imprime
  `FFFFFFFF`, `088` imprime `6`, `080` imprime `15`, `011` imprime `3B`). Se usa sólo como *presencia
  de capa/layout* (los demás imprimen un número; la galería imprime `-1`).
- **NO_VERIFICADO** que `FFFFFFFF` signifique «sin capa»: es la lectura que encaja con que no se
  emita ningún `Lc Layer`/`Lc Layout` para `03F` y sí para `011`.
- No se ha tocado la cámara, ni `docs/`, ni `knowledge/`, ni el código del arnés. El perfil usado es
  `analysis/gui/g22/harness/live/uilive/` (ignorado por git); `reports/evidence/…` sólo contiene
  cliente, trazas y PNG. **El perfil no se deja con estado guardado**: el autoguardado cayó después de
  la primera apertura de la galería (4 vistas de índice apiladas) y restaurarlo daría una medida
  sucia; `initrd.gz` y `huella.txt` sí se conservan, así que el siguiente arranque en frío reutiliza
  el initrd (≈150–190 s hasta la primera pantalla).

## 7. Evidencia

| Fichero | Contenido |
|---|---|
| [`traza-vista-indice.txt`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/traza-vista-indice.txt) | recuentos `Vn/Vd 03F/011/088` + la secuencia completa de una apertura |
| [`sonda-funceventmode.txt`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/sonda-funceventmode.txt) | `F 125104` = `0x15` con la galería arriba, `0x1` con STLREC encima |
| `01-stlrec.png`, `04-index-1s.png`, `05-index-5s.png`, `06-index-tras-caution.png` | capturas citadas en §2 |
| [`ctl.py`](evidence/film-pb-1-sub-arnes-ui-playback-20261126/ctl.py) | cliente del arnés (`estado`, `esperafotograma`, `tecla(s)`, `linea`, `captura`, `refrescar`) |
