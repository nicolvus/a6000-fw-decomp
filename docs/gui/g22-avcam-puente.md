# G22 — Puente entre `im.elf` (arnés) y `av-cam` (LIRO VM): ObjCamera recibe respuestas reales (13-11-2026)

Paso 2 de la emulación de av-cam ([paso 1](../PENDIENTES.md): `scripts/gui/avcam/liro_vm.py`). Hasta ahora el shim descartaba todo lo que `im.elf` enviaba a las colas de kernel de LIRO
([g22-respuesta-efcs-objcamera §11](g22-respuesta-efcs-objcamera.md)); ahora esos mensajes llegan a `av-cam.bin` ejecutándose en Unicorn y lo que `av-cam` contesta vuelve al invitado.

## 1. Cadena

```
im.elf (QEMU)                          anfitrión (live.py)
 libObj/ObjCamera ─ osal_snd_msg ─► sonyshim.c (AVQ=cola,…) ─ «\x01AVQ q tam cab cuerpo» ─► virtio-serial ─► puente.py ─► liro_vm.py (av-cam.bin, Unicorn)
 rcv_msg / callback ◄── avq_inject ◄── línea «Q q cab cuerpo» ◄──────────────────────────────── puente.py ◄── osal_snd_msg de av-cam a colas ajenas
```

- **Shim** (`scripts/gui/harness/shim/sonyshim.c`, variable `AVQ=hex,…`): un `snd_msg` a una cola de kernel de la lista (y que ningún servicio del shim atienda antes) se reenvía en lugar de descartarse; el tamaño sale de un anillo que anota `valloc_msg_wait`. La respuesta
  (`Q cola cabecera(12 B) cuerpo`) se entrega al callback registrado o, si la cola es de `rcv_msg`, a su buzón; una respuesta dataflow (`0xa0a0a0a0`) crea el buzón al llegar (su emisor hace `rcv_msg` después de enviar). Lo que llega antes de que `im.elf`
  registre la cola queda **pendiente** y se entrega al registrarla (`reg_msg_queue_cb`) o al primer `rcv_msg`, como hace la cola del kernel.
- **Puente** (`scripts/gui/avcam/puente.py`): arranca la LIRO VM (`entry(pre)`, `entry(main)`), ata su tiempo virtual al reloj real (`vm.limite`) y hace correr la VM con cada mensaje entrante. `NO_REENVIAR` excluye teclas (`0x7a0020`: las pone el anfitrión), reloj y trazas.
  En un arranque en frío del invitado reenvía los avisos que `av-cam` emitió al arrancar (en la cámara arranca antes que `im.elf`); con estado restaurado no, porque el invitado ya los recibió.
- **Activación**: `live.py` lo activa solo si hay `unicorn`, `av-cam.bin` y `liro.ko` (`--no-avcam` lo apaga). Evidencia de cada ejecución en `live/<perfil>/avcam.jsonl` (`entra`/`sale`/`arranque`). Cambia `SHIMENV` (`AVQ=` con las 125 colas de recepción de `av-cam`): el primer arranque tras actualizar es en frío.

## 2. Qué se midió (arranque en frío real, perfil `avq`)

| Tráfico | Resultado |
|---|---|
| Peticiones dataflow de `InfraAvbbcMsgManager`/`SDF` a `0x5700f9`, `0x5a0048`, `0x56000f` (antes «sin respuesta») | `av-cam` contesta cada una con el mismo formato que el shim fabricaba (cate `0x1000`, msg `0 ^ 0x8000`, cabecera −1 = cola destino); el arranque de `im.elf` sigue hasta la pantalla de disparo con ellas |
| Tras `S 11004012` (`Ts` en caliente): `ObjCamera`/`CAMUSER_CAMLIRO` envía mensajes LIRO a `0x40193` y `0x30001` | El hilo `CAMLIRO`, **bloqueado 111 s en `rcv_msg 0x20002`, despierta con la respuesta real** `{1, 0x4049, seq 5, estado 0x80, dato 0xf0}` de `av-cam` (tarea `tsk0x46`) y sigue (`ObjRenderer StartMute` continúa). Es el primer mensaje de `av-cam` que recibe `ObjCamera` |
| Avisos de arranque de `av-cam` (`0xc2019f`, `0x5c011c`, `0x2804b6/7`, `0x520250`, `0xd100ee`, `0x13603d1`, `0x118029a`, `0x60197`, `0x920277`) | Quedan pendientes: `im.elf` no registra esas colas (son de otros módulos). Solo `0x94016a` se entrega (callback) |

Formato LIRO observado (INFERENCIA): `{u8 tipo, u8 ?, u16 orden, u32 seq | 0x80000000, carga}`. `av-cam` despacha el tipo 5 por una tabla de 220 entradas de 12 B `{u16 id, ?, manejador, ?}` (`0x438052d8`). Las órdenes de **ajuste** (tipo 5) a `0x30001`
(`0x40ec`, `0x40eb`, `0x40f5`: el manejador guarda el byte en un global y no contesta) no tienen respuesta; las de `0x40193` (`0x4049`) sí, y `0x4081` solo traza (sin respuesta: `CAMLIRO` espera la siguiente).

## 3. Cambios en la LIRO VM que hicieron falta

`osal_msg_size` (bloques de 32 B × 32 − 12; sin él `av-cam` descartaba todo mensaje), cabecera `m−8` rellena en `valloc`, tamaño y cabecera de cada mensaje saliente, `osal_dynamic_id` de liberar (`0x4a`) sin salida,
respuesta DMM asíncrona con la cabecera de origen cambiada y `+6` = `u16` de la petición en `+0x14` (cierra `AsyncAllocNew: rcv Invalid Src` y `DIFFERENT_COMP` asíncrono).

## 4. Límites

- **No se ve ningún icono nuevo**: la barrera de [g22-respuesta-efcs-objcamera §11](g22-respuesta-efcs-objcamera.md) sigue (`EE_START` no sale, `ModelStillRec` no ejecuta `SetInit`); sin modo de imagen en vivo `ObjCamera` no manda más órdenes a LIRO (probado: semipulsación y disparador no generan tráfico).
  Lo que cambia es que cuando las mande tendrá un `av-cam` real que las conteste.
- `av-cam` ve hardware inventado: registros MMIO a cero salvo las reglas de `mmio_reglas.json`, DMM de 2 MiB por unidad, RAM física `0x80000000` plana; sin sensor, ISP ni mecánica. Sus avisos asíncronos no dependen de eventos físicos.
- Quedan `Open: ERR_DMM_RET_CODE 1026/402`, `Open: DIFFERENT_COMP msg_id 5` y `Close: ERR_DMM_RET_CODE` del DMM síncrono (carga de aberración de lente): formato de `OpenUnit`/`CloseUnit` sin verificar (falta `DmmConfig.bin`/`dmm.ko`).
- `av-cam` emite teclas fantasma por `0x7a0020` (`0x1f1` a 512 ms, `0xa7` a 1012 ms; NO_VERIFICADO el origen, probablemente GPIO a cero leído como pulsado): se filtran.
- Dos tropiezos: con `sscanf` (libc 2.11) en el hilo de entrada del shim el invitado se paró tras la primera respuesta (causa NO confirmada; se usa un decodificador propio y no volvió a ocurrir) y los mensajes del invitado llevan la cabecera `m−8` a 0 (el tamaño lo da `valloc`).

## 5. Investigación de `EE_START` (13-11-2026, medido con `TRACEFN` en frío; estático con capstone sobre `libObj` 3.21)

**Lo que hace cada pieza (VERIFICADO).** `ModelStillRec::ExecAction` es `libObj+0x69c608(this, id, ev)` (`tbh` de 151 entradas). Cada `id` salta a un hilo-envoltorio `Action<Nombre>` que abre un ámbito de traza y llama a la rutina real:
`0 ModelInitialize · 1 ModelInitializeComp · 2 ObjectTopologyCreate · 7 ExeEeStart · 35 ExePanoramaEeStartCaptureStby · 42 GpSpinal · 49 SetInit · 71 EntryStStby · 84 PrepareOn · 85 PrepareOff · 111 EntryDeactivate · 113 EntryGotoActivate`.
**`ActionExeEeStart` (7) y `SetInit` (49) llaman a la misma rutina `0x68b4bc`** (la que emite `EE_START`). Lo llama el motor genérico de la máquina de estados (`lr` = `libObj+0x158d0c`, por vtable: sin llamadores directos), no un evento de `ModelManager`.

**Qué ocurre en el arnés (medido).** En el arranque, el modelo de disparo (`this` = el objeto de `ActionEntryStStby`) hace `Initialize → TopologyCreate → InitializeComp → EntryDeactivate → PrepareOn → PrepareOff → (107) → EntryStStby → PrepareOn`: **llega a «StStby» (espera de disparo)**. Después solo recibe `96`×3 y `GpSpinal` ×2 (al abrir la vista de disparo) y nunca `7`/`49`. Publicar en caliente `0x11004015/17/08/0d` o mover el dial de modos no genera ninguna acción; un segundo `Ts` lo devuelve a `EntryDeactivate`.
Es decir, el evento que lanza `ExeEeStart` no es de `ModelManager` y no llega: lo emite la propia máquina del modelo cuando recibe del objeto de cámara el aviso de «listo para EE» (INFERENCIA; no hay mensaje equivalente en el tráfico medido con av-cam).

**Forzarlo (`F` en el shim).** Línea `F desp a0 a1 a2` (por `/linea`): llama a `libObj+desp(...)` en caliente. `F 69c608 <this> 7 <this+0x10> 0` ejecuta `ActionExeEeStart` → `SetInit` («TRAZA SetInit»). Resultado:
1. `SetInit` pide a backup un **`read_multi`** (op 5 del shim, `libbackup` `Backup_read_multi`): `{ids[] = 0x1070015, 0x1070014, …, buf}` con 67 ids de 1 B. Implementado (datos de `bk.tbl` en orden y sin relleno; el recuento no viaja, se corta en el primer id ausente; `NOBKMULTI=1` lo desactiva; `BKMULTI=1` vuelca la tabla). Antes devolvía vacío.
2. Después **SIGSEGV en `libObj+0x7edad0`** (`r0 = 0`) desde `0x42ad04 ← 0x682a8c ← 0x68b6d8`: en `0x682a64` la rutina lee del mapa de propiedades del modelo (`this+0xc4`, clave `0x14d`) y, para el tipo 1, usa `[holder+4]` sin comprobar nulo; **falta la propiedad `0x14d`**, que no crea la inicialización del modelo (la rellena una notificación de `ObjCamera`/av-cam).

**Conclusión.** `EE_START` depende de que `ObjCamera` haya publicado antes sus propiedades de cámara (primera, la `0x14d`). Con el puente av-cam ya activo, el paso que falta es **qué mensaje de LIRO/`CamMgr` hace que `ObjCamera` emita esas notificaciones**: `ObjCamera` solo envió `0x40ec/0x40eb/0x40f5` a `0x30001` y `0x4049/0x4081` a `0x40193`; las de av-cam al arrancar (`0xc2019f`…) no tienen receptor en `im.elf`. Siguiente paso: identificar la clave `0x14d` (¿`PARAMID_*`?) y quién la escribe en el mapa `this+0xc4`.
