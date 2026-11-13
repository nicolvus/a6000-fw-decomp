# G22 — Respuesta de `ObjCamera` a la orden EFCS (`0x75fa`): especificación estática (13-11-2026)

Análisis estático, sin QEMU ni REA (el binario es ELF Thumb con símbolos de PLT; bastó `llvm-objdump` + búsqueda propia de bytes y literales). Binarios: `libObj.so` de `analysis/camera-extract/usr/lib` (md5 `eb12512e…`, fw 3.21); el del arnés (`files-36x`, md5 `010a133e…`) es idéntico en todos los rangos citados (comprobado byte a byte; difieren 446 B en otra zona). `av-cam.bin` de `analysis/rea-independent/input` (desplazamientos de archivo). Contexto: [G22 §5.18z⁸](g22-arnes-ui-qemu.md).

Niveles: **VERIFICADO** = leído en instrucciones/bytes; **INFERENCIA** = deducido de evidencia estática coherente; **NO_VERIFICADO** = hipótesis sin prueba.

## 1. Identificadores (VERIFICADO)

La tabla de nombres de `libObj` (`.data.rel.ro`, archivo `0xfdb5ec`, 3364 punteros) es contigua por bloques: `MSGID_*` desde el índice 1 = `0x7500`, `PARAMID_*` desde el índice 726 = `0x9500`, `VALUEID_*` desde el índice 2076 = `0`. Se comprueba con valores ya conocidos (`0x75fa` = `MSGID_SET_FRONT_ESHUTTER_MODE_CMD`, `0x9776` = `PARAMID_FRONT_ESHUTTER_MODE`, `0x2b4/0x2b5` del conversor) y con los inmediatos del código:

| Nombre | Valor | Dónde se usa |
|---|---|---|
| `MSGID_SET_FRONT_ESHUTTER_MODE_CMD` | `0x75fa` | `0x6896d0` (modelo, emite) |
| `MSGID_SET_FRONT_ESHUTTER_MODE_CMP` | `0x75fb` | `0x678eb8` (modelo, recibe); en `ObjCamera` CMP = CMD + 1 para `0x7500–0x76c1` (`0x95a7ec`) |
| `MSGID_NOTIFY_FRONT_ESHUTTER_MODE_EVT` | **`0x85a6`** (no `0x7769`: los EVT van en el bloque `0x8500`) | `0x678e50` (modelo, recibe), `0x95a42c` (`ObjCamera`, emite) |
| `PARAMID_FRONT_ESHUTTER_MODE` | `0x9776` | orden |
| `PARAMID_FRONT_ESHUTTER_MODE_SET` | `0x9777` | CMP y EVT |
| `PARAMID_FRONT_ESHUTTER_MODE_ACT` | `0x9778` | EVT |
| `PARAMID_COMP_RESULT` | `0x9502` | CMP |
| `VALUEID_VALUEID_FRONT_ESHUTTER_ON` / `_OFF` | `0x2b4` / `0x2b5` | valores de los tres parámetros |

Categoría de todos los mensajes: `0x3100`. Los tres parámetros son tipo 7 (`ParamStd<int, Type7>`; descriptor `0x7, 0x20004, …` en la tabla de `0xaf4c1c`).

## 2. La orden (VERIFICADO)

`pvt_SetFrontEShutterMode` (`0x6896ac`): `ObjMsg(0x3100, 0x75fa)`; `SetCommonRelayParam(1, ParamStd<uint,8>(++[this+0x264]))` (contador de relevo); `AddParam(0x9776, ParamStd<int,7>(v))` con `v` = `0x68c24a(valor del modelo)`: **1 → `0x2b4` (Activar), 2 → `0x2b5` (Desactivar)**; destino `0x42067c(8)` = objeto 8 = `008_ObjCamera`; `IssueCommandAsync` (retorno `0x689744`). Medido en el `shim.log` de §5.18z⁸: el volcado del `IssueCommandAsync` lleva `000002b5` en la palabra 4, que es la ranura `r7+0x24` del valor convertido → **`0x9776 = 0x2b5` para Desactivar** (VERIFICADO también en ejecución ya registrada).

Lista de parámetros que `ObjCamera` acepta/emite por mensaje (tabla `0x7500` en `0xfe1f70` y `0x8500` en `0xfe2d60`, entradas de 8 B `{n, lista}`; VERIFICADO):

- `0x75fa`: `{0x9776}`
- `0x75fb`: `{0x9777, 0x9502}`
- `0x85a6`: `{0x9777, 0x9778}`

## 3. Quién responde y cómo (VERIFICADO salvo lo indicado)

Responde **`ObjCamera` (en la propia `libObj`), en `CamUser::SequenceSetFrontEShutterMode` (`0x95a308`), de forma síncrona y sin esperar a LIRO**:

1. `memset(buf, 0, 9)`; despachador `0x9bbb5c(0x4099, cmd, buf, …)` → conversor `0x99e968`: `buf = {05, 00, 99 40, …, +8 = 0 (ON) / 1 (OFF)}`.
2. `0xa1b21c` → `osal_valloc_msg_wait` + `osal_snd_msg` del búfer de 9 B a la cola de LIRO. Si falla: traza `SeqSetFrontEShutterMode) ##### [%d] SEND MSG ERROR #####` y respuesta de error `0xf001` (`0xa1607c`); fin.
3. Si el envío va bien: `0xa1f728` copia los parámetros de la orden (`0x9776`) al almacén de `ObjCamera` (`[obj+0xc70]`, ranura `pid − 0x9500`, `0xa1ecb4`).
4. **CMP**: `ObjMsg(0x3100, 0x75fb)`; `0xa1f150` añade los parámetros de la lista (`0x9777`) **leídos del almacén**; `AddParam(0x9502, 0xf000)` (resultado correcto); `CopyCommonRelayParam(cmd)`; envío con `0xa16042(this, 0x3130, 0x75fb, cmp, cmd)` (respuesta al emisor).
5. **EVT**: `ObjMsg(0x3100, 0x85a6)`; `0xa1f150` añade `0x9777` y `0x9778` del almacén; `CopyCommonRelayParam(cmd)`; `0xa15f98` (difusión de evento).

Límites de este punto:
- En el almacén de `ObjCamera` solo hay código que escribe `0x9776` en esta ruta (valor por defecto `0x2b4` en la tabla inicial `0xa21d5e`). No hay en `ObjCamera` ningún inmediato `0x9777/0x9778`: sus valores llegan por la vía genérica de tablas (`0xe3d09c`, `0xe3ef8c` contienen `0x9777`/`0x9778`), probablemente desde el estado de LIRO. **NO_VERIFICADO** qué valor llevan en la cámara real justo tras la orden; lo coherente con el modelo (§4) es que `SET` = valor pedido y `ACT` = valor aplicado (INFERENCIA).
- En el arnés, tras el `IssueCommandAsync` no aparece **ningún** `osal_snd_msg` (el shim sí registra `snd_msg`), ni la traza de error: la secuencia `0x95a308` **no llega a ejecutarse** (o se bloquea antes del envío). Como `ObjCamera` no espera a LIRO para responder, el fallo está **antes**: el despacho de la orden dentro de `ObjCamera` (su hilo/estado), no la falta de respuesta de LIRO. Causa NO_VERIFICADA; se confirma con una sola trampa sin `TRACEREP` en `0x95a308` y `0xa1b21c` (requiere QEMU, no hecho aquí).

## 4. Qué hace el modelo al recibirlo (VERIFICADO)

- CMP (`pvt_ActionObjectFrontEShutterModeCmp`, `0x678e90`) y EVT (`pvt_ActionObjectNotifyFrontEShutterModeEvt`, `0x678e28`) llaman a `pvt_subActionObjectFrontEShutterModeCmpEvt` (`0x678d3c`):
  - lee `0x9777`; si existe, `0x693cb8` lo convierte (`0x2b4` → 1, `0x2b5` → 2; tabla `0xd534fc`) y lo guarda en la ranura 0 (`SET`); si falta, traza `Invalid PARAMID_FRONT_ESHUTTER_MODE_SET`;
  - lee `0x9778` → ranura 1 (`ACT`); si falta (caso CMP), traza `Invalid PARAMID_FRONT_ESHUTTER_MODE_ACT` sin más efecto.
- El almacén es `[ModelStillRec+0x534]` = envoltorio `{dueño, propiedad, aviso 0x4f}` (`0x681eae`); guardar (`0x68e0ce`) llama a `propiedad->set(ranura, v)` y avisa a la vista con el id **`0x4f`**, que es justo el `getModelInfo model/STILL_REC 4f` que aparece en el registro tras pulsar Desactivar.
- La propiedad (`[+0x428]`, `0x6817f8`, clase de 0x30 B creada por `0x4a55f0`) se llama **`FRONT_E_SHUTTER_MODE`** y guarda el id **`0x107086e`** en `+0x10`. Su `set` (`0x41589e`) escribe la ranura (`+0x20`/`+0x24`) y una palabra de estado empaquetada (`0x10a06c`, índice `0x44`); **no escribe Backup** (sus métodos de guardar/cargar son vacíos).

## 5. Registro de Backup del EFCS

**`0x107086e`, 1 byte, 1 = Activar, 2 = Desactivar** (confianza ALTA; la escritura, MEDIA):
- `libObj` asocia ese id (único literal, `0x681b14`) a la propiedad `FRONT_E_SHUTTER_MODE` (VERIFICADO).
- `av-cam.bin` `0x2d7368` (VERIFICADO): lee 1 B de `0x107086e`, lo pasa por `0x2d9e7c` (byte − 1 → tabla `{0, 1}`: **1 → 0, 2 → 1**) y envía el búfer de 9 B `{05, 99 40, +8}` del **mismo selector `0x4099`** que la orden del menú; es la restauración del ajuste al arrancar. 1 → 0 coincide con `0x2b4` (ON) → 0 del conversor de `libObj`.
- Está en las listas de ids de Memory Recall de `viewUnified2.so` (`0x1bb670`) y `cmnviewMRUtil.so` (`0x10c98`) (VERIFICADO).
- En `bk.tbl` del volcado real vale `02` (EFCS desactivado cuando se volcó; INFERENCIA por la tabla anterior).
- `0x1070361` queda **descartado** como registro del EFCS: no aparece en esta cadena (sus 5 usos en `libObj` están en `0x10f5ac–0x113a7c`, fuera de ella); en `bk.tbl` vale `00`.
- **NO_VERIFICADO quién escribe `0x107086e` al cambiar el ajuste**: no hay `Backup_write` con ese id en `libObj` ni otro literal en `av-cam`; probablemente se escribe por una tabla de ids en el lado de cámara (fuera del arnés). Por eso el arnés no verá nunca `NV 107086e` aunque `ObjCamera` responda: la emulación debe escribirlo.

## 6. Especificación para la respuesta emulada (lista para implementar)

Disparador: `IssueCommandAsync` a `ObjCamera` (objeto 8) con `ObjMsg` categoría `0x3100`, id `0x75fa`, parámetro `0x9776 = v` (`v` ∈ {`0x2b4`, `0x2b5`}; otro valor → no responder, como `ObjCamera` con `NON SUPPORTED`/`UNKNOWN`).

Preferente (máxima fidelidad): que se ejecute la secuencia real `0x95a308` (arreglar el despacho de §3); entonces `ObjCamera` emite CMP y EVT por sí misma y el shim solo añade el Backup. Si no es posible, emulación equivalente:

1. **CMP** al emisor: `ObjMsg(0x3100, 0x75fb)`, `0x9777 = v`, `0x9502 = 0xf000`, parámetros de relevo copiados de la orden (`CopyCommonRelayParam`). Confianza ALTA en forma; MEDIA en que `0x9777 = v`.
2. **EVT** (difusión): `ObjMsg(0x3100, 0x85a6)`, `0x9777 = v`, `0x9778 = v`, relevo copiado. ALTA en forma; MEDIA en los valores (§3).
3. **Backup**: `0x107086e` ← `01` (si `v = 0x2b4`) o `02` (si `0x2b5`), 1 byte. ALTA en id y codificación; MEDIA en que la cámara lo escriba en ese instante.

Resultado esperado: la fila pasa a «Desactivar» (aviso `0x4f`), `NV 107086e 02` y persistencia en frío. Ni `SET`/`ACT` reales ni el instante de la escritura están medidos en la cámara: comprobar con un volcado de NVRAM antes/después de cambiar el EFCS (pendiente de autorización, solo lectura).

## 7. Fuera de alcance / no hecho

- «Ajuste de zoom» (`model/CAMERA 9/62`): no analizado aquí; mismo síntoma, misma hipótesis (despacho de `ObjCamera`).
- No se implementó en el arnés: la causa del no-despacho (§3) y los valores de `SET`/`ACT` necesitan ejecución en vivo.

## 8. Implementado en el arnés (13-11-2026, medido en QEMU)

**Trampas (perfil `efcs`, puerto 8693, `HARNESS_OUT=analysis/gui/g22/harness/runs/efcs-*`, gitignored).**
- `0xa1b21c` sí se ejecuta en el arranque, llamada desde otra secuencia de `ObjCamera` (`0x960be8`, selector `0x40ec`): el envío a LIRO funciona.
- Con trampas de un disparo en `0x95a308` (la secuencia), `0xad76f2` (el caso `0x75fa` del despachador de órdenes `0xad4ce4`, único que construye la secuencia) y `0xad7712/0xad7716` (crear y encolar), tras `IssueCommandAsync … ra=libObj.so+0x689745 -> 0` **no salta ninguna**. Tampoco se despierta ningún hilo de `ObjCamera` (`CAMUSER_OBJCAME`, `CAMUSER_CAMMANA`, `CAMUSER_CAMPOST`, `ObjCameraAgent`) en `WAITLOG`.
- Conclusión (VERIFICADO): la orden **no llega al despachador de `ObjCamera`**; se corta antes, en la entrega del mensaje por `MWF`. LIRO no interviene. No se encontró por qué no llega a la cola de `ObjCamera` (el hilo `CAMUSER_OBJCAME` está en una espera indefinida desde el arranque; las pilas de `WAITSTACK` salen entrelazadas). Por eso no se pudo arreglar el reparto y se emula (opción B).

**Emulación (`sonyshim.c`, `NOEFCS=1` la desactiva).**
- `IssueCommandAsync` es ahora un envoltorio desnudo que pasa `r4`/`r5` del llamante. Si el llamante es `libObj+0x689745` (`pvt_SetFrontEShutterMode`), la orden se acepta (`-> 0`) y `r5` ∈ {1, 2}:
  - aplica el efecto de CMP + EVT: `0x68e0ce([modelo+0x534], 0|1, v)` (ranuras `SET` y `ACT` = valor pedido, con aviso `0x4f` a la vista), igual que `0x678d3c`;
  - escribe **Backup `0x107086e` = v (1 B)** por el servicio de Backup del shim (`NV 107086e 0v` → `nvram.json`).
- Arranque: trampa de un disparo en `libObj+0x681eb2` (`ModelStillRec`, justo después de crear el envoltorio `+0x534`). Carga las dos ranuras desde `0x107086e` con el `set` de la propiedad (vtable `+0x14`), para que la fila y el diálogo coincidan. En la cámara real eso lo hace la notificación de arranque de `ObjCamera` (aquí no hay).
- No se fabrican los `ObjMsg` `0x75fb`/`0x85a6`: se aplica su efecto en el modelo (`pvt_subActionObjectFrontEShutterModeCmpEvt` solo guarda las dos ranuras y avisa a la vista).

**Medido.** Arranque en frío con `0x107086e = 02` (`bk.tbl` real) → fila «Desactivar». Activar en caliente → `NV 107086e 01`, la fila cambia. Arranque en frío → ranuras = 1. Desactivar → `NV 107086e 02`. Borrado `estado.zst` y arranque en frío → «Desactivar» (`runs/efcs-emu1/caliente_activar.png`, `caliente_desactivar.png`, `frio_desactivar.png`). Prueba `test_efcs_emula_respuesta_objcamera_y_backup_107086e`.

**Límites.** Igual que en §6: `SET = ACT = v` y el momento de escribir el Backup son INFERENCIA (falta comparar la NVRAM real antes y después). Con la `libObj` de otro firmware no se arma (comprueba los bytes de `0x681eb2`).

**«Ajuste de zoom» (`model/CAMERA`): no hecho.** Por INFERENCIA tiene la misma causa: sus dos órdenes van al mismo objeto de `ObjCamera` y tampoco reciben respuesta. Emularlo exige otra especificación estática (órdenes candidatas `MSGID_SET_DIRECT_SMART_EZOOM_MODE_CMD` `0x7612` / `…PRECISION…` `0x7614`, parámetros `0x9798`/`0x979b`, registro de Backup sin identificar).
