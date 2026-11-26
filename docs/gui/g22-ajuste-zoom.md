# G22-ZOOM — «Ajuste de zoom» de la A6000: especificación estática y emulación en el arnés

Tarea G22-ZOOM (fila G22-E de [`PENDIENTES`](../PENDIENTES.md)): que la fila **«Ajuste de zoom»** del menú
cambie como en la cámara y sobreviva un arranque en frío.

Niveles: **VERIFICADO** = leído en instrucciones/bytes de los binarios de 3.21 (`libObj.so` md5
`eb12512e6b74a940f1ae6de1c38477db` del arnés; `av-cam.bin` 3.21 de `analysis/rea-independent/input`), o
medido en el arnés con la captura/log que se cita. **INFERENCIA** = deducido de esa evidencia sin
ejecutarlo. **NO_VERIFICADO** = hipótesis sin prueba.

## 1. Resumen

| Pieza | Valor | Nivel |
|---|---|---|
| Quién emite | `ModelCamera` (`libObj`): `0x4bf230` → orden *inteligente*, `0x4bf108` → orden *precisión* | VERIFICADO |
| Acción del modelo | despachador `0x4cfd62`: **`0x63` = inteligente**, **`0x64` = precisión** (`requestModelExecute("model/CAMERA", 0x63\|0x64)`) | VERIFICADO |
| Mensaje | `ObjMsg(categoría 0x3100, id 0x7612` \| `0x7614)`, `AddParam(0x9798` \| `0x979b, VALUEID)` | VERIFICADO |
| Destino | objeto **8** = `008_ObjCamera` (en el mismo proceso, por `MWF::ObjIf::IssueCommandAsync`, ruta `0x4bcc54`) | VERIFICADO |
| Valores | `0x2d9` 1,4× · `0x2da` 2,0× · `0x2db` apagado (inteligente); `0x2dc` activada · `0x2dd` desactivada (precisión) | VERIFICADO |
| Respuesta | CMP `0x7613`/`0x7615` (categoría `0x3130`, `+0x9502=0xf000`) y EVT `0x85b1`/`0x85b2` (`0x3100`) con `SET`/`ACT`(+`RATE`) | VERIFICADO |
| Quién responde | `ObjCamera`, **dentro de `libObj`** (secuencias `0x956ebc` y `0xa0d4b0`), sin LIRO/av-cam | VERIFICADO |
| CamMgr (`0x30001`) | **no interviene**: su tabla de despacho solo tiene ids `0x3000–0x3036` | VERIFICADO |
| Backup del ajuste | `PARAMID_BKUP_DIGITAL_ZOOM_SETTING` = **`0x2093`** (tabla PARAMID de `libScalarDaemon.so`); su registro `0x1070xxx` del Backup, sin identificar | PARAMID VERIFICADO, registro NO_VERIFICADO (ver §6) |

## 2. Ruta desde el menú

1. **Elemento de menú.** `analysis/gui/process-bindings-a6000.json` da el ProcessId **`0xd9` =
   `CustomZoomSetting`** ([G13](g13-barrido-ajustes-a6000-a6300.md) §6), es decir, un elemento *propio*
   (`CmnViewProcessDataElementCustomZoomSetting`, cadena de `viewUnified2.so`), no el genérico `Normal`:
   `modelos: []` y `respaldos: []` en esa tabla. La página del ajuste es el recurso
   `usr/share/app/viewDgtlZoomSetting.uxc`, y `viewUnified2.so` contiene el nombre del nodo de ajuste
   `cmnViewSettingNodeRootZoomSetting` (0x136ad) y el del plugin `viewDgtlZoomSetting.so` (0x3a0d37).
   VERIFICADO (cadenas y tabla de ProcessIds); el nombre del elemento y su clase, INFERENCIA de las
   cadenas `42CmnViewProcessDataElementCustomZoomSetting` (0x3b926d) y del ProcessId.
2. **El elemento habla con `model/CAMERA`.** En `viewUnified2.so`, `.data` contiene descriptores de
   104 B con el puntero a la cadena `model/CAMERA` (0x38fd71) en `+0`: `0x49970c`, `0x499774`,
   `0x4997dc`, … (VERIFICADO en bytes). Semántica de esos descriptores **NO_VERIFICADO**; lo que sí se
   mide es la llamada real (§7).
3. **El modelo.** `ModelCamera` tiene dos acciones que emiten la orden (§3) y dos que reciben la
   respuesta (§4). Las acciones no se llaman desde ninguna otra función de `libObj` (barrido de `bl` a
   0x4bf108/0x4bf230 en todo `.text`: **solo** `0x4d00dc`/`0x4d00e6`, dentro del despachador de acciones
   del modelo), así que el disparo viene de fuera: `viewManagerIf::requestModelExecute("model/CAMERA", …)`
   de la vista (es lo que registra `SETLOG=1` del shim, §7).

## 3. La orden (VERIFICADO)

`ModelCamera`, acción *precisión* (`0x4bf108`) y *inteligente* (`0x4bf230`) — gemelas:

| Offset | Instrucción | Qué hace |
|---|---|---|
| `0x4bf132` | `mov.w r1, #0x3100` | categoría |
| `0x4bf136` | `movw r2, #0x7614` | `MSGID_SET_DIRECT_PRECISION_EZOOM_MODE_CMD` |
| `0x4bf16c` | `bl 0x4da51c` | añade `PARAMID_DIRECT_PRECISION_EZOOM_MODE` (`0x979b`) con el valor convertido y guarda la ranura 2 de la propiedad |
| `0x4bf180` | `movs r0, #8` | objeto destino = `008_ObjCamera` |
| `0x4bf182` | `bl 0x42067c` | resuelve el objeto por índice |
| `0x4bf18e` | `bl 0x4bcc54` | envío (`IssueCommandAsync`, PLT `0xdc144`) |
| `0x4bf25e` | `movw r2, #0x7612` | `MSGID_SET_DIRECT_SMART_EZOOM_MODE_CMD` (acción *inteligente*) |
| `0x4bf294` | `bl 0x4da600` | añade `PARAMID_DIRECT_SMART_EZOOM_MODE` (`0x9798`) |

Formato del mensaje: `ObjMsg{ categoría=0x3100, id=0x7612|0x7614, ParamList{ 0x9798|0x979b = VALUEID } }`;
el valor viaja como **VALUEID**, no como número de menú:| Ajuste | valor del modelo | VALUEID enviado | Nombre |
|---|---|---|---|
| Inteligente | 0 | `0x2d9` | `VALUEID_DIRECT_SMART_EZOOM_1_4` |
| Inteligente | 1 | `0x2da` | `VALUEID_DIRECT_SMART_EZOOM_2_0` |
| Inteligente | 2 | `0x2db` | `VALUEID_DIRECT_SMART_EZOOM_OFF` |
| Precisión | 0 | `0x2dc` | `VALUEID_DIRECT_PRECISION_EZOOM_ON` |
| Precisión | 1 | `0x2dd` | `VALUEID_DIRECT_PRECISION_EZOOM_OFF` |

**Códigos de acción (VERIFICADO en el despachador `0x4cfb...`/`0x4cfd...` del modelo).** Las dos acciones se
piden por `requestModelExecute("model/CAMERA", código)`: la cadena de comparaciones de `ModelCamera` lleva
`0x4cfd62 cmp r0,#0x63` → `0x4cfd64 beq.w 0x4d00d8` → `0x4d00dc bl 0x4bf230` (orden **inteligente** = código
**0x63**) y `0x4cfd68 cmp r0,#0x64` → `0x4cfd6e b 0x4d00e2` → `0x4d00e6 bl 0x4bf108` (orden **precisión** =
código **0x64**). Son los dos únicos `bl` a `0x4bf230`/`0x4bf108` de todo `.text`, como ya decía §2.

Conversores del modelo (VERIFICADO instrucción a instrucción): `0x4e35e8` modelo→cámara y `0x4e3638`
cámara→modelo (inteligente); `0x4e3694` / `0x4e36dc` (precisión). Tabla de nombres de `libObj`
(`.data.rel.ro` 0xfdb5ec, 3364 punteros): índice 275 = `MSGID_SET_DIRECT_SMART_EZOOM_MODE_CMD` (0x7612),
277 = `…PRECISION…CMD` (0x7614), 1390 = `PARAMID_DIRECT_SMART_EZOOM_MODE` (0x9798), 1393 =
`PARAMID_DIRECT_PRECISION_EZOOM_MODE` (0x979b); con el ancla 618 = `MSGID_NOTIFY_FRONT_ESHUTTER_MODE_EVT`
(0x85a6) salen 629 = `…SMART_EZOOM_MODE_EVT` (**0x85b1**) y 630 = `…PRECISION…` (**0x85b2**).

## 4. La respuesta y quién la da (VERIFICADO)

`ObjCamera` atiende las dos órdenes en su despachador de comandos (`0xad4ce4`): `0xad58da`
`movw r3,#0x7612` + `beq.w 0xad7826` (inteligente), `0xad58e4 adds r3,#2` → `0x7614` + `beq.w 0xad7852`
(precisión). Cada caso crea un trabajo de 0x34 B con `0x956ebc` (inteligente) / `0xa0d4b0` (precisión) que
**se ejecuta en el propio proceso** y hace, en este orden (misma forma que la cadena EFCS documentada en
[`g22-respuesta-efcs-objcamera`](g22-respuesta-efcs-objcamera.md) §3):

1. copia los parámetros de la orden al almacén de `ObjCamera` (`0xa1f728`, `[obj+0xc70]`);
2. **CMP**: `ObjMsg(0x3130, cmd+1)` con los parámetros `SET` leídos del almacén (`0xa1f150`) más
   `AddParam(0x9502, 0xf000)`; se envía al emisor con `0xa16042(this, 0x3130, cmp_id, msg, cola)`
   (`0x956e14`/`0x956e20`, `0xa0d424`/`0xa0d430`);
3. **EVT**: `ObjMsg(0x3100, 0x85b1|0x85b2)` con `SET`/`ACT` del almacén, difundido con `0xa15f98`
   (`0x956e2e`/`0x956e58`, `0xa0d43e`/`0xa0d468`);
4. `0x951568` incrementa un contador del recurso; **no hay ningún envío a LIRO/av-cam en la secuencia**
   (ni `0xa1b21c` ni `osal_snd_msg`): el ajuste no necesita a `av-cam`.

El modelo aplica la respuesta en sus **sub-acciones**: `0x4eafd4` (inteligente; la llama la acción de
`0x85b1` en `0x4b5db0`) lee `0x9799` (`SET`) y `0x979a` (`ACT`); `0x4eae68` (precisión; la llaman
`0x4b5e1c` para `0x7615` y `0x4b5e88` para `0x85b2`) lee `0x979d`/`0x979f` (modo) y `0x979e`/`0x97a0`
(velocidad), con `0x4a54fc` para leer el parámetro y `0x4a5836(propiedad, ranura, valor)` para guardarlo:
ranura 0 = `SET`, ranura 1 = `ACT`. Las propiedades son `[ModelCamera+0x1480+0x34]` (inteligente),
`+0x38` (modo de precisión) y `+0x3c` (velocidad de precisión); el emisor ya había guardado el valor
pedido en la ranura 2. Nota: el modelo **no** tiene acción para el CMP `0x7613` (solo para los EVT).

La propiedad es un objeto de 0xC B creado por `0x4a57e8` = `{modelo, descriptor, id de aviso}`
(`stm r0,{r1,r2,r3}`, `0x4a57ee`); las tres del zoom se crean con id de aviso **`0x61`**
(`0x4cc83c`, `0x4cc852`, `0x4cc86c`), y `0x4a5836` —el «set» usado por las sub-acciones— avisa al modelo
con ese id (`0x4a584a`…`0x4a5858` → `0x4a5808` → `0x132754`), que es lo que refresca la vista.
El *descriptor* (2.º campo, objeto polimórfico con `get`/`set` en vtable `+0xc`/`+0x14`) es el candidato a
tener detrás el registro de Backup; su tabla de descriptores no se ha resuelto (**NO_VERIFICADO**, §6).

## 5. CamMgr (cola `0x30001`) no tiene nada que ver (VERIFICADO)

La hipótesis de partida (ids `0x7612`/`0x7614` a CamMgr) es **falsa**. La tabla de despacho de CamMgr en
`av-cam.bin` está en el **offset de fichero `0xabcd30`** (= `0x43ffdd30`, con la imagen cargada en
`0x43541000`), con **203 registros de 16 B** `{u32 handler, u32 msg_id, u32 tamaño, u32 siguiente}`;
todos los `msg_id` están en **`0x3000–0x3036`** y no hay ningún `0x76xx`. El valor `0x43ffe09c` que
figuraba en el comentario del shim cae en el **campo `siguiente`** del registro del id `0x300c` (offset
`0xabd090`), no en el comienzo de la tabla: se corrige aquí. Los ids `0x7612/0x7614` son mensajes
`MWF` internos de `libObj` (espacio `0x7500`) que van a `ObjCamera` **en el mismo proceso**, así que
`0x30001` no interviene ni en la orden ni en la respuesta.

## 6. Persistencia (NO_VERIFICADO de momento)

En estático **no se ha demostrado** ningún id de Backup para este ajuste:

- la propiedad no guarda id de Backup (solo el de aviso `0x61`, §4);
- el elemento de menú (`0x d9`) no declara respaldo en `process-bindings-a6000.json`;
- los candidatos `0x1070xxx` de la fila G22-E siguen sin evidencia para el zoom.

**Lo que sí está identificado (VERIFICADO en bytes, 26-11-2026).** `libScalarDaemon.so` (el demonio que
traduce PARAMID ↔ Backup) lleva la **tabla completa del enum PARAMID**: 960 entradas de 8 B en el fichero
`0x1b05a4` = `{puntero al nombre, id u32}` — la primera es `PARAMID_INVALID`/0 y la última
`PARAMID_CAMSETTING_MANUAL_RING_MODE`. De ahí salen los ids de este ajuste en el espacio *escalar* (distinto
del de `libObj`, que usa `0x95xx`/`0x97xx` para los mismos nombres):

| Nombre | id | Uso |
|---|---|---|
| `PARAMID_BKUP_DIGITAL_ZOOM_SETTING` | **`0x2093`** | ajuste del menú (lo que persiste) |
| `PARAMID_BKUP_EZOOM_MODE` | `0x2082` | modo de e-zoom |
| `PARAMID_BKUP_EZOOM_SUPER_RESOLUTION_MODE` | `0x2083` | zoom de imagen nítida |
| `PARAMID_SYS_DATA_EZOOM_MODE_SET` / `…_ACT` | `0x12a2` / `0x12a3` | datos del sistema (SET/ACT) |
| `PARAMID_CAMSETTING_EZOOM_MODE` | `0x5002` | ajuste de la cámara |

`PARAMID_BKUP_DIGITAL_ZOOM_SETTING = 0x2093` es el candidato natural a registro de Backup, pero **no se ha
podido unir con el espacio `0x1070xxx` de `bk.tbl`** (3 279 registros de 1 B entre `0x1070000` y `0x1070d0e`;
el del EFCS, `0x107086e`, tampoco aparece en la tabla escalar), así que el registro concreto sigue
**NO_VERIFICADO**. La tabla se lee en cualquier copia de 3.21 del binario
(`analysis/camera-extract/usr/lib/libScalarDaemon.so` o el `harness/stage/cam/usr/lib/` no versionado),
offset `0x1b05a4`, con `tests/test_g22_zoom.py`.

Por eso el valor se deja **en memoria del modelo** (que es lo que hace la cámara mientras está encendida) y
la persistencia se busca por la vía que sí es observable: lo que la **vista** escriba en el Backup al
cambiar el ajuste (`CmnViewProcessDataElementNormal::setValueToBackup`, que el shim ya registra) y la
diferencia de `nvram.json` entre arranques (§7). Si no aparece ninguna escritura, la persistencia queda
**NO_VERIFICADO** y se documenta como tal.

## 7. Emulación en el arnés

**`sonyshim.c`, en `issue_cmd` (el envoltorio de `MWF::ObjIf::IssueCommandAsync`), bloque «ZOOM».**
Enganche: `dladdr(ra)` y `(off & ~1) == 0x4bcc68` — es decir, el llamante es `libObj+0x4bcc54` (el envío del
propio modelo, §3); en ese punto `r5` es `ModelCamera` (`0x4bcc5a` `mov r5,r0`) y el mensaje está en `msg`.
Si la categoría es `0x3100` y el id es `0x7612`/`0x7614`:

1. lee la propiedad `[ModelCamera+0x1480+0x34]` (inteligente) o `+0x38` (precisión);
2. `v = 0x4a58b2(propiedad, 2)` — la ranura 2 la acaba de escribir el emisor con el valor del modelo;
3. `0x4a5836(propiedad, 0, v)` + `0x4a5914(propiedad, 0)` (SET, lo que aplica el CMP) y lo mismo en la
   ranura 1 (ACT, lo que aplica el EVT); `0x4a5836` avisa además a la vista con el id `0x61` (§4).

Son las funciones reales del firmware, no stores inventados: es el mismo efecto que el modelo aplica en
`0x4e9538`/`0x4eae68`/`0x4eafd4` cuando la respuesta llega. `NOZOOM=1` lo desactiva y hay **guardia de
versión** (como el bloque de EFCS): arma solo si `libObj+0x4bf136` es `f247 6214` (`movw r2,#0x7614`) y
`libObj+0x4bcc5a` es `4605` (`mov r5,r0`); si no, deja una traza `ZOOM: libObj distinta …` y no toca nada.
No se emula ningún registro de Backup (§6).

Compilación y pruebas: `sh scripts/gui/harness/shim/build.sh SYSROOT analysis/gui/g22/harness/stage/cam/lib
analysis/gui/g22/harness/overlay/cam/usr/lib/sonyshim.so` (SYSROOT = los dos `.deb` de `harness/dl`
extraídos; en este equipo sin `dpkg-deb` se extraen con `bsdtar -xf … data.tar.xz` + `tar`). Pruebas:
`tests/test_g22_zoom.py` (**9**: 8 verdes y 1 omitida sin el `av-cam.bin` no versionado), con las del shim, las de bytes de `libObj` y la de la tabla PARAMID de `libScalarDaemon`.

## 8. Medida en el arnés (26-11-2026, G22-ZOOM)

Perfil propio `zoom2`/`zoom3` (puertos 8721/8722), `SHIMEXTRA="FULLLOG=1 SETLOG=1 IMCMDLOG=1"`, shim
recién compilado (`build.sh`, md5 `d02772f2a84cf0026066df665a47d24e`, idéntico al de `main`). Dos arranques:
uno **en frío** (primera pantalla a **121 s**) y uno **restaurado** desde `estado.zst` (32 s). Todo lo que
sigue se midió **igual en los dos**, así que no es un artefacto de la restauración.

### 8.1 La navegación por teclas funciona y es corta (VERIFICADO)

**MENU abre el menú en la pestaña del engranaje, página 4** (`AEL con obturad.`, `e-Prim. cortin. obtur.`, …;
[`g22-zoom-menu-ajustes-p4.png`](img/g22-zoom-menu-ajustes-p4.png)). Desde ahí, **`izquierda` cambia de
página dentro de la pestaña** (p4 → p3, 80 479 px distintos, 26,2 % del fotograma) y **`abajo` mueve el foco
a la fila** (54 051 px, 17,6 %), que es «Ajuste de zoom — Solo zoom óptico». Tres pulsaciones y ninguna
pestaña tocada: **la ruta que §8 daba por imposible es esta** y no aparece el cuelgue de 0 listas.

- Las flechas **no** están invertidas en esta ruta (`abajo` baja el foco; comprobado por los píxeles y por
  el marco naranja de la fila).
- Cada tecla se manda **pulsación y suelta** (`POST /tecla {"k":"abajo","v":1}` y `v:0`): el driver descarta
  el evento repetido, y sin la suelta la pulsación siguiente se pierde.
- **Menú desincronizado**: si el interruptor del shim (`menu_open`) queda al revés, MENU no hace nada y la
  secuencia entera no pinta. Se arregla mandando la línea `N` al invitado (`POST /linea N`), que es lo que
  hace `live.py` al conectar; pasó una vez en esta sesión y se recuperó así.
- Capturas (mismo perfil, arranque en frío y restaurado dan el **mismo PNG byte a byte**, 70 513 B):
  [`g22-zoom-p3-fila.png`](img/g22-zoom-p3-fila.png) es la fila seleccionada;
  [`g22-zoom-p3-fila-deshabilitada.png`](img/g22-zoom-p3-fila-deshabilitada.png) es la misma página con el
  foco en «Pre-AF» y la fila **en gris** (deshabilitada, ver §8.2).

### 8.2 La fila se abre pero la UI la rechaza: falta `getModelInfo model/CAMERA 0xf` (VERIFICADO)

`intro` sobre la fila **sí llega a la vista**: contesta con el modal «Función desactivada actualmente.» y
«Aceptar» ([`g22-zoom-fila-desactivada.png`](img/g22-zoom-fila-desactivada.png); 92 073 px distintos de la
página, 30,0 %). En el registro del shim (`WAITLOG=60000` + `WLALL=1`, que se pueden encender **en
caliente** con `POST /linea "E WLALL=1"` / `"E WAITLOG=60000"`) la causa es literal:

```
SETMOD viewManagerIf::getModelInfo model/CAMERA f ab660a00 0 -> 0      (y 4 repeticiones)
```

Es decir: la fila pregunta el estado a `model/CAMERA` info **0xf** (el mismo bloque de estado que la pantalla
de disparo pide sin parar — 254 veces por arranque, §5.18z¹³, y que deja la OSD casi vacía), recibe **0** y
se pinta como deshabilitada. **No emite ninguna orden**: en la ventana del registro con `WLALL=1` no hay ni
una línea `IssueCommandAsync cat=…` ni `ZOOM: …`, porque el zoom nunca sale del modelo.

- **No es un problema de teclas ni de foco**: el resto de la misma página funciona («Pre-AF» → lista
  `Activar/Desactivar` con el foco, y los modelos de menú responden: `requestModelExecute @M00B 30 -> 0`,
  `@M00F 4f -> 0`, `@M00B 30 -> 0`).
- **No es una carrera**: con `E GMIRETRY=1` (20 reintentos × 50 ms) sigue en 0, y tampoco cambia en el
  arranque en frío.
- **Medido también en la cámara de verdad**: no; esto es del arnés (la cámara responde su info 0xf). Es el
  pendiente ya abierto de la OSD (`ObjCamera` retenido en el modo LRM `0x60`, §5.18z¹³), no del zoom.

### 8.3 Los dos caminos del arnés tampoco llegan al ajuste (VERIFICADO en caliente)

`POST /linea "O view/DIGITAL_ZOOM_SETTING"` (vista del ajuste) **abre la vista** pero no dibuja nada:

```
OPENHOT view/DIGITAL_ZOOM_SETTING 0 -> -2138198000
Vn 021_viewUnified4.so                      (id de vista 0x21, en viewUnified4.so)
SETMOD getModelInfo model/CAMERA 98 … -> 0   (info 0x98, la que necesita la página)
```

y la pantalla queda **0 px distinta** de la página 3 (se sigue viendo el menú detrás). O sea que la página
del ajuste pide **otra** info del mismo modelo que no contesta. **Este camino es del arnés, no de la
cámara**: sirve para saber qué pide la página (0x98), pero no demuestra nada del ajuste.

`POST /linea "X model/CAMERA 63"` (códigos de acción de §3) devuelve `requestModelExecute(model/CAMERA, 0x63)
-> 0` y **no** produce `IssueCommandAsync`: la ejecución de modelo desde el hilo del diagnóstico no llega al
despachador, así que el bloque «ZOOM» de §7 no se puede disparar por ahí. El camino `Z obj:clase:id` (mensaje
crudo a `ObjCamera`) tampoco vale para probar la emulación: salta al modelo, y el bloque se engancha
precisamente en el **envío del modelo**.

### 8.4 Qué queda demostrado y qué no

- **Demostrado**: la ruta de teclas hasta la fila (3 pulsaciones, sin cuelgue, reproducible y determinista);
  que la fila **está deshabilitada por falta de la info 0xf de `model/CAMERA`**; que la página del ajuste
  existe (`view/DIGITAL_ZOOM_SETTING`, id 0x21) y pide la info 0x98; que en toda la sesión el invitado **no
  escribe ni una vez el Backup** (`WLALL=1` no deja ninguna línea `backup op=8`, solo lecturas `op=3`), o sea
  que la fila deshabilitada no escribe nada: la parte (b) del pendiente **no se puede cerrar por esta vía**.
- **NO demostrado**: que el ajuste cambie en pantalla y que el zoom emulado se vea. Para eso hace falta que
  `model/CAMERA` conteste la info **0xf** (habilitación) y la **0x98** (estado de la página). Fabricarlas
  sin la cámara real sería inventar el dato, y el proyecto exige medirlo antes; el molde para hacerlo
  existe y es el de `RELOJEMU` (§7 de [`g22-fecha-hora`](g22-fecha-hora.md)): responder solo cuando el
  modelo no contesta, con valores **medidos**.

**Para retomar (con el molde de `RELOJEMU`)**: volcar en la cámara real la info `model/CAMERA` 0xf y 0x98
(`GMILOG=1 GMIDUMP=model/CAMERA` en el arnés da la forma de la respuesta; en la cámara, `0xf` es el bloque
grande de estado y `0x98` el del zoom), rellenarlas en el shim cuando `getModelInfo` devuelva 0 —igual que
`reloj_params` con `@M018`— y entonces sí: `intro` abre la lista, `abajo` elige «Activ.: zoom digital»,
`intro` emite `requestModelExecute model/CAMERA 0x63`, el bloque de §7 aplica SET/ACT y la fila cambia.

## 9. Límites de evidencia

- **VERIFICADO** (bytes): emisores `0x4bf108`/`0x4bf230` y sus **códigos de acción `0x64`/`0x63`** en el
  despachador (`0x4cfd62`/`0x4cfd68` → `0x4d00d8`/`0x4d00e2`), ids `0x7612/0x7614` (+CMP `0x7613/0x7615`,
  EVT `0x85b1/0x85b2`), parámetros `0x9798/0x979b` y sus valores `0x2d9–0x2dd` (conversores `0x4e35e8`,
  `0x4e3638`, `0x4e3694`, `0x4e36dc`), destino objeto 8 por `0x4bcc54`, despacho de `ObjCamera`
  (`0xad4ce4` → `0xad7826`/`0xad7852`), CMP por `0xa16042` con categoría `0x3130` y `0x9502=0xf000`, EVT
  `0x85b1/0x85b2` por `0xa15f98`, lectura de `SET`/`ACT` por el modelo (`0x4e9538`, `0x4eae68`, `0x4eafd4`,
  `0x4a54fc`, `0x4a5836`), aviso a la vista con id `0x61` (`0x4a57e8`, `0x4cc83c/0x4cc852/0x4cc86c`), tabla
  de CamMgr de `av-cam.bin` (203 registros, ids `0x3000–0x3036`, sin `0x76xx`), tabla PARAMID de
  `libScalarDaemon.so` (`0x1b05a4`, 960 entradas) con `PARAMID_BKUP_DIGITAL_ZOOM_SETTING` **`0x2093`**,
  `PARAMID_BKUP_EZOOM_MODE` `0x2082` y `PARAMID_SYS_DATA_EZOOM_MODE_SET/ACT` `0x12a2/0x12a3`.
- **VERIFICADO** (arnés, 26-11-2026, §8): la ruta MENU → `izquierda` → `abajo` llega a la fila sin cuelgue y
  de forma determinista; `intro` la abre y la UI contesta «Función desactivada actualmente.» porque
  `viewManagerIf::getModelInfo("model/CAMERA", 0xf)` devuelve 0; la página del ajuste es
  `view/DIGITAL_ZOOM_SETTING` (id de vista `0x21`, en `viewUnified4.so`) y pide la info `0x98`; la sesión no
  escribe ni un registro de Backup.
- **INFERENCIA**: que el elemento de menú `CustomZoomSetting` (ProcessId `0xd9`) sea la fila medida — la
  llamada real a `model/CAMERA` desde esa fila **no se ha podido ver** todavía (la fila no pasa de la info
  0xf); sí está medido que la fila ocupa la página 3 de la pestaña del engranaje y que se llama «Ajuste de
  zoom» con el valor «Solo zoom óptico».
- **NO_VERIFICADO**: (a) que la emulación de §7 cambie la fila (la fila no se puede habilitar sin la info
  0xf); (b) el registro de Backup/NVRAM del ajuste (el PARAMID `0x2093` no se ha podido mapear a un id
  `0x1070xxx`); (c) el papel del valor que el emisor lee antes de convertir (la llamada `0x42ac00` de
  `0x4da600`/`0x4da51c` ignora el `r1 = 0x2e3`/`0x2e6` que el código carga, así que ese tag no identifica el
  parámetro); (d) que la cámara real escriba `SET = ACT = valor` (la emulación usa el valor que el emisor
  dejó en la ranura 2); (e) la semántica de las infos `0xf` y `0x98` de `model/CAMERA` (es lo que falta para
  poder emularlas con datos medidos).

## PARA PENDIENTES.md

| G22-ZOOM | PARCIAL (26-11-2026) | **«Ajuste de zoom»: la fila se alcanza con las teclas y se abre, pero la UI la rechaza por una info del modelo que el arnés no tiene.** Especificación estática ([§§1–7](gui/g22-ajuste-zoom.md)): la orden la emite `ModelCamera` (acción **`0x63`** inteligente → `libObj+0x4bf230`, **`0x64`** precisión → `0x4bf108`, despachador `0x4cfd62`/`0x4cfd68`) como `ObjMsg(0x3100, 0x7612|0x7614)` con `PARAMID_DIRECT_…EZOOM_MODE 0x9798/0x979b`, valores `0x2d9–0x2dd`, al objeto 8 (`ObjCamera`) por `0x4bcc54` → `IssueCommandAsync`; responde `ObjCamera` dentro de `libObj` (CMP `0x7613`/`0x7615` cat `0x3130` + EVT `0x85b1`/`0x85b2`) y el modelo aplica `SET`/`ACT` avisando a la vista con `0x61`. `CamMgr` no interviene. Emulación en `sonyshim.c` (bloque «ZOOM» de `issue_cmd`, `NOZOOM=1` la apaga). **Nuevo**: tabla PARAMID de `libScalarDaemon.so` (`0x1b05a4`) → `PARAMID_BKUP_DIGITAL_ZOOM_SETTING` **`0x2093`** (`PARAMID_BKUP_EZOOM_MODE 0x2082`), sin poder unirla aún al registro `0x1070xxx` del Backup. **MEDIDO (arnés, dos arranques, frío 121 s y restaurado 32 s, resultado idéntico)**: la fila se alcanza con **MENU → `izquierda` (Ajustes p4→p3) → `abajo`** y se captura ([`g22-zoom-p3-fila.png`](img/g22-zoom-p3-fila.png)); `intro` la abre y la UI contesta «Función desactivada actualmente.» ([`g22-zoom-fila-desactivada.png`](img/g22-zoom-fila-desactivada.png)) porque **`viewManagerIf::getModelInfo("model/CAMERA", 0xf) -> 0`**; no sale ninguna orden (`IssueCommandAsync`/`ZOOM:` ausentes) y no se escribe Backup (`backup op=8` ausente). `O view/DIGITAL_ZOOM_SETTING` abre la vista (id `0x21` en `viewUnified4.so`) pero pide `model/CAMERA 0x98 -> 0` y **no dibuja** (0 px): **ese camino es del arnés, no de la cámara**. La ruta de teclas funciona; lo que falta es la info. **Abierto**: (a) volcar en la cámara real las infos `model/CAMERA` `0xf` y `0x98` y emularlas en el shim con el molde de `RELOJEMU` (solo si el modelo devuelve 0) — con eso `intro` abrirá la lista y la orden disparará el bloque «ZOOM»; (b) mapear `PARAMID_BKUP_DIGITAL_ZOOM_SETTING 0x2093` al registro `0x1070xxx`; (c) persistencia en frío. Pruebas: `tests/test_g22_zoom.py` (9).
