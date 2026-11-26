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
| Mensaje | `ObjMsg(categoría 0x3100, id 0x7612` \| `0x7614)`, `AddParam(0x9798` \| `0x979b, VALUEID)` | VERIFICADO |
| Destino | objeto **8** = `008_ObjCamera` (en el mismo proceso, por `MWF::ObjIf::IssueCommandAsync`, ruta `0x4bcc54`) | VERIFICADO |
| Valores | `0x2d9` 1,4× · `0x2da` 2,0× · `0x2db` apagado (inteligente); `0x2dc` activada · `0x2dd` desactivada (precisión) | VERIFICADO |
| Respuesta | CMP `0x7613`/`0x7615` (categoría `0x3130`, `+0x9502=0xf000`) y EVT `0x85b1`/`0x85b2` (`0x3100`) con `SET`/`ACT`(+`RATE`) | VERIFICADO |
| Quién responde | `ObjCamera`, **dentro de `libObj`** (secuencias `0x956ebc` y `0xa0d4b0`), sin LIRO/av-cam | VERIFICADO |
| CamMgr (`0x30001`) | **no interviene**: su tabla de despacho solo tiene ids `0x3000–0x3036` | VERIFICADO |
| Backup/NVRAM del ajuste | sin identificar en estático | NO_VERIFICADO (ver §6) |

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
el valor viaja como **VALUEID**, no como número de menú:

| Ajuste | valor del modelo | VALUEID enviado | Nombre |
|---|---|---|---|
| Inteligente | 0 | `0x2d9` | `VALUEID_DIRECT_SMART_EZOOM_1_4` |
| Inteligente | 1 | `0x2da` | `VALUEID_DIRECT_SMART_EZOOM_2_0` |
| Inteligente | 2 | `0x2db` | `VALUEID_DIRECT_SMART_EZOOM_OFF` |
| Precisión | 0 | `0x2dc` | `VALUEID_DIRECT_PRECISION_EZOOM_ON` |
| Precisión | 1 | `0x2dd` | `VALUEID_DIRECT_PRECISION_EZOOM_OFF` |

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
`tests/test_g22_zoom.py` (6, verdes), con las del shim y las de bytes de `libObj`/`av-cam`.

## 8. Medida en el arnés (lo que se pudo medir y lo que no)

**Hecho y medido.** Arranque en frío del perfil propio `zoom` (puerto HTTP 8711) con el shim recién
compilado y `SHIMEXTRA="FULLLOG=1 SETLOG=1 IMCMDLOG=1 GMIDUMP=model/CAMERA"`: primera pantalla a **173–195 s**,
menú abierto con la tecla MENU (captura [`g22-zoom-menu-ajustes-p4.png`](img/g22-zoom-menu-ajustes-p4.png),
pestaña Ajustes, página 4) y **el shim nuevo no rompe el arranque** (la pantalla de disparo y el menú se
dibujan igual; captura [`g22-zoom-pantalla-disparo.png`](img/g22-zoom-pantalla-disparo.png)). Efecto
lateral medido en la NVRAM del perfil: el arranque escribe **175 propiedades nuevas `0x1070xxx`**
(`nvram.json` 17 → 192 claves; solo cambian `1070939` `02040100`→`02040000` y `10708ff`
`00b0d950`→`00b0e94a`), es decir, el modelo sí vuelca sus propiedades a Backup al arrancar; ninguna de esas
escrituras se puede atribuir al zoom todavía (§6).

**NO medido (y por qué).** La fila «Ajuste de zoom» **no se llegó a abrir** en esta sesión: llegar a ella
exige bajar a la página 3 del menú y, tras la primera ronda de navegación, el invitado entra en el cuelgue
ya documentado (0 listas de GPU; `/estado` sigue contando fotogramas pero la pantalla no cambia y las
flechas dejan de responder; MENU sigue abriendo/cerrando). Se intentó tres veces (dos arranques en frío y
un reinicio con estado guardado) con el mismo resultado. Además el equipo tenía el cupo de 2 `qemu-system-arm`
ocupado por otros agentes casi todo el tiempo, así que cada intento cuesta 3–4 min de espera más 3 min de
arranque. Por eso **la emulación de §7 está implementada y probada unitariamente, pero su efecto en la
pantalla queda NO_VERIFICADO**, igual que la persistencia.

**Siguiente paso concreto (para retomar).**
1. Arrancar con `FULLLOG=1` y, sin tocar pestañas (el cuelgue aparece al cambiar de pestaña), ir directo a
   «Ajuste de zoom»: MENU → la vista abre en Ajustes p4 → `abajo`/`arriba` (¡en este arnés están invertidas!)
   hasta la página 3, `intro`, elegir «Activ.: zoom digital», `intro`.
2. Comprobar en `guest.log`: `SETMOD requestModelExecute model/CAMERA …`, los dos
   `IssueCommandAsync cat=0x3100 id=0x7612|0x7614` y la línea nueva `ZOOM: … ranuras SET/ACT = v`.
3. Comparar `nvram.json` antes/después (si aparece un id nuevo, ese es el registro de Backup y se escribe a
   mano en el shim como en EFCS `0x107086e`).
4. Arrancar en frío (borrar `estado.zst`) y capturar la fila para la persistencia.

## 9. Límites de evidencia

- **VERIFICADO** (bytes): emisores `0x4bf108`/`0x4bf230`, ids `0x7612/0x7614` (+CMP `0x7613/0x7615`, EVT
  `0x85b1/0x85b2`), parámetros `0x9798/0x979b` y sus valores `0x2d9–0x2dd` (conversores `0x4e35e8`,
  `0x4e3638`, `0x4e3694`, `0x4e36dc`), destino objeto 8 por `0x4bcc54`, despacho de `ObjCamera`
  (`0xad4ce4` → `0xad7826`/`0xad7852`), CMP por `0xa16042` con categoría `0x3130` y `0x9502=0xf000`, EVT
  `0x85b1/0x85b2` por `0xa15f98`, lectura de `SET`/`ACT` por el modelo (`0x4e9538`, `0x4eae68`, `0x4eafd4`,
  `0x4a54fc`, `0x4a5836`), aviso a la vista con id `0x61` (`0x4a57e8`, `0x4cc83c/0x4cc852/0x4cc86c`), tabla
  de CamMgr de `av-cam.bin` (203 registros, ids `0x3000–0x3036`, sin `0x76xx`).
- **INFERENCIA**: que el elemento de menú `CustomZoomSetting` de `viewUnified2` sea quien manda la orden
  (cadenas y ProcessId `0xd9`; la llamada real está medida en §8 de [`g22-arnes-ui-qemu`](g22-arnes-ui-qemu.md)
  §5.18z⁸ como `requestModelExecute model/CAMERA 9/62`, pero no se ha relacionado con el código de la vista).
- **NO_VERIFICADO**: (a) que la emulación de §7 cambie la fila (no se pudo abrir en esta sesión);
  (b) el registro de Backup/NVRAM del ajuste; (c) el papel del valor que el emisor lee antes de convertir
  (la llamada `0x42ac00` de `0x4da600`/`0x4da51c` ignora el `r1 = 0x2e3`/`0x2e6` que el código carga, así
  que ese tag no identifica el parámetro); (d) que la cámara real escriba `SET = ACT = valor` (la emulación
  usa el valor que el emisor dejó en la ranura 2).

## PARA PENDIENTES.md

| G22-ZOOM | PARCIAL (26-11-2026) | **«Ajuste de zoom» (`model/CAMERA`) especificado en estático y emulado; falta medirlo.** Especificación ([§§1–5](gui/g22-ajuste-zoom.md)): la orden la emite `ModelCamera` (`libObj+0x4bf108` precisión / `0x4bf230` inteligente) como `ObjMsg(0x3100, 0x7614|0x7612)` con `PARAMID_DIRECT_PRECISION_EZOOM_MODE 0x979b` / `…SMART… 0x9798`, valores `0x2dc/0x2dd` y `0x2d9/0x2da/0x2db`, al objeto 8 (`ObjCamera`) por `0x4bcc54` → `IssueCommandAsync`. La respuesta la da `ObjCamera` **dentro de `libObj`** (despachador `0xad4ce4`, casos `0xad7826`/`0xad7852`): CMP `0x7613`/`0x7615` (cat `0x3130`, `0x9502=0xf000`) + EVT `0x85b1`/`0x85b2`; el modelo aplica `SET`/`ACT` en las ranuras 0/1 de `[ModelCamera+0x1480+0x34|0x38]` y avisa a la vista con el id `0x61`. **Corregido**: `CamMgr` (cola `0x30001`) no interviene — su tabla de despacho (`av-cam.bin` offset `0xabcd30`, 203 registros de 16 B) solo tiene ids `0x3000–0x3036` (el `0x43ffe09c` del comentario del shim era el campo `siguiente` del registro `0x300c`). Emulación en `sonyshim.c` (`issue_cmd`, bloque «ZOOM», `NOZOOM=1` la apaga) con las funciones reales del modelo; `tests/test_g22_zoom.py` (6). Medido: arranque en frío 173–195 s con el shim nuevo, menú abierto (captura) y 175 propiedades `0x1070xxx` escritas al arrancar. **Abierto**: (a) abrir la fila en la página 3 del menú y capturar antes/después — el invitado entra en el cuelgue de 0 listas al navegar y las flechas dejan de responder (3 intentos); (b) identificar el id de Backup del ajuste comparando `nvram.json` antes/después; (c) persistencia en frío. Siguiente paso exacto en [§8](gui/g22-ajuste-zoom.md).
