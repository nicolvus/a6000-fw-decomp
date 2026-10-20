# S20 — Arquitectura real del OSAL de LIRO y por qué la búsqueda literal de `0x40193` fracasó en 4 sesiones

Continuación directa de `s20-p1-mailbox40193-rpc-pattern.md`. Objetivo:
identificar el receptor real del buzón `0x40193` (bloqueo citado en
`shutter-trigger-chain-0x3011.md` desde sesión 18). Alcance ampliado por
primera vez a los módulos del kernel (`.ko`) del firmware, no solo
`av-cam.bin`. Sin Codex, sin subagentes, sin modificar ningún binario.

## Hallazgo arquitectónico 1 (VERIFICADO): LIRO no es un procesador separado — es código ejecutado dentro del kernel Linux

Decompilación directa de `liro.ko` (`llvm-objdump`/símbolos):

- `liro_init()` llama `kthread_create_on_node(tsk_entry, ...)` — crea un
  **hilo del kernel Linux real**, no arranca un coprocesador.
- `tsk_entry()` abre el archivo de firmware (`filp_open`/`vfs_read`), **carga
  `av-cam.bin` en una dirección física** (`DAT_0001a2ac`, con corrección
  `-0x40000000` de mapeo), verifica la cabecera (magia `"LIRO"`, versión 4),
  y luego **llama directamente los punteros de entrada del propio blob**:
  `entry(pre)`, `entry(main)`, `suspend`, `resume`, `exit` (leídos de
  offsets fijos de la cabecera del blob) — `(**(code**)(DAT_0001a2ac+0xc))(0)`.
- Antes de esa llamada, `tsk_entry` hace `memcpy(blob+0x24, &DAT_00019e08, 0x344)`
  — copia una **tabla de 209 punteros de función (0x344/4)** desde el propio
  `liro.ko` hacia el blob cargado. Imprime "API support list: OSAL, Backup 2"
  y avisa si algún puntero es NULL.

**Esto resuelve una ambigüedad citada en `silent-shutter-status.md`** ("el
nombre LIRO por sí solo no establece que sea un procesador separado o un
RTOS independiente"): **se demuestra que no lo es**. LIRO es un blob
ejecutado en contexto de kernel, en un hilo real del scheduler Linux, con
su tabla de API (incluido el vtable OSAL ya conocido en
`DAT_440205c0+0x14`) poblada por `liro.ko` en tiempo de carga.

## Hallazgo arquitectónico 2 (VERIFICADO): el OSAL real vive en `osal_uipc.ko`/`osal_utm.ko`, no en `av-cam.bin`

Los wrappers ya conocidos de `av-cam.bin` (`FUN_4356120c`=Send,
`FUN_43561260`=Receive, `FUN_435612d0`=Alloc, `FUN_43561324`=
create/destroy) son *tail calls* puros a un vtable; **no implementan
lógica propia**. `liro.ko` tiene como símbolos **no definidos**
(`llvm-nm`): `osal_snd_msg`, `osal_rcv_msg_tmo`, `osal_reg_msg_queue_cb`,
`osal_reg_sync_msg_queue_cb`, `osal_create_thread`, `osal_subsystem_id`,
`osal_thread_id`, etc. Se localizaron los módulos reales que los
**exportan** (`llvm-nm --defined-only` sobre cada `.ko` del firmware):

- **`osal_uipc.ko`**: `osal_snd_msg`, `osal_rcv_msg_tmo`,
  `osal_reg_msg_queue_cb`, `osal_reg_sync_msg_queue_cb`,
  `osal_unreg_msg_queue_cb`, `osal_valloc_msg_wait`, `osal_free_msg`, etc.
  Contiene además `osal_dir` (BSS) — el registro de colas en tiempo de
  ejecución (no reconstruible estáticamente, se puebla en caliente).
- **`osal_utm.ko`**: `osal_subsystem_id`, `osal_thread_id`,
  `osal_create_thread` — pero se desensamblaron y **no son lo que su
  nombre sugería**: `osal_subsystem_id()`/`osal_thread_id()` leen campos
  del `task_struct`/`thread_info` del **hilo que llama** (vía la técnica
  clásica `bic sp, #mask` para obtener el puntero de pila del hilo actual),
  es decir, devuelven la identidad del llamador, **no decodifican un ID de
  mensaje compuesto**. Se descarta la hipótesis de que estas funciones
  sirvan para separar `0x40193` en subsistema+id.

## Hallazgo arquitectónico 3 (VERIFICADO, decisivo): el espacio de ID de cola del OSAL real es de 16 bits — `0x40193` no puede ser un ID de cola crudo

Desensamblado directo de `osal_reg_msg_queue_cb` y `osal_snd_msg` en
`osal_uipc.ko`:

```asm
; osal_reg_msg_queue_cb(r0=id, r1=callback, r2=context, r3=flags)
cmp   r0, #0            ; rechaza negativos
tst   r0, #32768        ; rechaza bit15 puesto
uxth  r6, r0            ; <-- TRUNCA r0 a 16 bits para la búsqueda de cola
cmp   r2, #0            ; exige contexto no nulo
```

```asm
; osal_snd_msg(r0=id, r1=msg, ...)
tst   r0, #32768
uxth  r8, r0             ; <-- misma truncación a 16 bits para localizar la cola
...
ubfx  r2, r5, #0x10, #0xf ; <-- extrae bits [16:30] del r0 ORIGINAL (sin truncar)
cmp   r2, #0              ; usado condicionalmente (solo si flag de cola lo pide)
```

**VERIFICADO**: la cola se identifica por los **16 bits bajos** (`uxth`);
los bits `[16:30]` del argumento completo se usan como un campo adicional
aparte (clase/prioridad/broadcast — no identificado con precisión, pero
confirmado que es un campo *distinto*, condicional, no parte del ID de
cola). **`0x40193` descompuesto así da: ID de cola = `0x193`, campo extra
= `0x4`.**

Esto **explica por qué 4 sesiones de búsqueda literal de `0x40193` como
argumento de recepción fracasaron**: ningún código legítimo llamaría
`osal_rcv_msg_tmo(0x40193, ...)` — el bit 15 está en cero así que no sería
rechazado por ese chequeo, pero la cola real que esa llamada consultaría es
`0x193`, no `0x40193`; buscar el valor completo como argumento de un
receptor está, en rigor, buscando algo que la propia API no trata como un
ID de cola único.

## Lo que se intentó para cerrar con la pista `0x193` y no cerró

- Búsqueda del literal `0x193` en las 44 decompilaciones ya obtenidas de
  llamadores reales de `FUN_43561260` (recepción): **0 coincidencias**.
- Búsqueda de `0x193`/`0x40193` como entrada de ID en la tabla de 220 filas
  ya conocida (`0x43fff30c`) y en la tabla nueva de 35 filas (`0x43ffff84`,
  sesión 20): **0 coincidencias** en ambas.
- `uipc_oom` (la función que `osal_snd_msg`/`osal_reg_msg_queue_cb` llaman
  tras truncar a 16 bits) se desensambló: **no es la tabla de colas** —
  es el contador de uso para reporte de OOM por ID; no revela la
  estructura de despacho real (`osal_dir`, BSS, no reconstruible
  estáticamente).

**Razón de no cierre**: el receptor real probablemente llama
`osal_rcv_msg_tmo`/`osal_reg_msg_queue_cb` con el ID de cola ya resuelto a
`0x193` a través de una variable (no un literal inline), o el valor
`0x193` nunca aparece como tal en `av-cam.bin` porque se construye en
tiempo de ejecución (p. ej. `subsistema | id_dinámico`, vía
`osal_dynamic_id`, no decompilada en detalle en esta tarea). `osal_dir`
(el registro real de colas↔callbacks) vive en BSS de `osal_uipc.ko` y se
puebla dinámicamente — **no es reconstruible desde la imagen estática**,
a diferencia de las tablas de LIRO ya resueltas en sesiones 18/20 (esas sí
tenían inicializadores estáticos; este registro del kernel no).

## Clasificación

- **VERIFICADO**: `liro.ko` ejecuta `av-cam.bin` como hilo de kernel real,
  no como procesador separado — resuelve ambigüedad de larga data.
- **VERIFICADO**: el OSAL real (`osal_snd_msg`, `osal_rcv_msg_tmo`,
  `osal_reg_msg_queue_cb`) vive en `osal_uipc.ko`, importado por `liro.ko`.
- **VERIFICADO**: el espacio de ID de cola es de 16 bits (`uxth`); `0x40193`
  se descompone en cola=`0x193` + campo extra=`0x4`.
- **DESCARTADO**: que `osal_subsystem_id`/`osal_thread_id` (en
  `osal_utm.ko`) decodifiquen IDs de mensaje compuestos — son identidad del
  hilo llamador, no relacionadas con el ID del mensaje.
- **NO_VERIFICADO (sin cambios de fondo, pero ahora mejor explicado)**: la
  identidad de la función/hilo receptor real de la cola `0x193`. El
  registro vive en una estructura BSS de un módulo del kernel que no se
  puede reconstruir estáticamente — se necesitaría una traza dinámica
  (no autorizada: está prohibido conectar o flashear la cámara) o
  localizar el llamador que construye dinámicamente el valor `0x193`/`0x40193`
  antes de pasarlo a `osal_reg_msg_queue_cb`, que no se logró en esta
  tarea.

## Cierre del paso pendiente: `osal_dynamic_id` desensamblada completa

**VERIFICADO**: `osal_dynamic_id` **no decodifica** IDs compuestos — es un
**asignador de IDs libres por mapa de bits** (`lsr r2,r8,#5`/`and r8,r8,#31`
= indexación clásica de bitmap de 32 bits por palabra; busca un hueco en
`[base, base+count)`, marca el bit ocupado, registra el resultado). Esta es
la pieza que subyace a "crear buzón temporal" (`param_4==-1` en
`FUN_43b04cd4`): entrega un ID **nuevo y dinámico** de un pool, no
decodifica uno ya existente. **Se descarta definitivamente** la hipótesis
de que esta función explique cómo se construye `0x40193`/`0x193` en tiempo
de ejecución — es lo opuesto (asigna IDs temporales nuevos, no resuelve
IDs fijos conocidos de antemano como `0x40193`).

## Estado final de esta línea de investigación

Se agotaron las vías estáticas razonables para esta tarea concreta:
búsqueda literal como receptor (44 sitios), como creador (38 sitios), como
entrada de las dos tablas de despacho conocidas (220 y 35 filas), y examen
de los tres módulos OSAL reales (`osal_uipc.ko`, `osal_utm.ko`) incluida su
única función de asignación dinámica de ID. El resultado honesto es: **se
reconstruyó por primera vez la arquitectura OSAL real (liro.ko en kernel +
osal_uipc.ko como proveedor de IPC) y se demostró que el ID de cola es de
16 bits**, lo que explica por qué la búsqueda literal de `0x40193` nunca
pudo tener éxito — pero **la identidad del receptor sigue sin
localizarse**, porque el registro real (`osal_dir`, BSS de
`osal_uipc.ko`) se puebla en tiempo de ejecución y no es reconstruible
desde la imagen estática. Cerrar esto definitivamente requeriría traza
dinámica, que está prohibida en este proyecto (no conectar/flashear la
cámara). Se considera esta línea **completamente investigada** con las
herramientas estáticas disponibles.

SilentShutter no se declara funcional.
