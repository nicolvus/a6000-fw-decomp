# S156 — el módulo `[TP_R]` (18 trazas) de la fw3.21 de la A6000

> **VERIFICADO** con bytes (sin REA/Ghidra). Regla de referencias: **estricta**
> (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`); los sitios puntuales se han
> verificado desensamblando. Reproducción: `analysis/s156_tp_r/build_tp_r.py` →
> `analysis/s156_tp_r/tp_r.json`; tests: `tests/test_s156_tp_r.py`.
>
> Convención: `vaddr = 0x43541000 + file_offset` en los **tres** firmwares.

## 1. Resumen

* `[TP_R]` es la etiqueta de un **módulo de panel táctil** (etiqueta interna `TP`, sigla
  **no desarrollada**) de la fw3.21 de la A6000: una *tarea* con cola OSAL propia,
  temporizador, ciclo de vida `boot_init_tp` / `boot_exit_tp` y una tabla de comandos de
  depuración registrada en el monitor `DebugVfcCmd` bajo el nombre `tp`.
* **18 cadenas** con el token `[TP_R]` entre `0x43c80f23` y `0x43c812f3`:
  **14 vivas** (20 sitios PIC en **8 funciones** emisoras) y **4 muertas**.
  Además hay **3 cadenas más** con la etiqueta antigua `[TP R]` (también muertas).
* La hipótesis de S151 **queda CONFIRMADA con bytes**: las trazas de `[TP_R]` no se
  emiten por `printf` sino por un helper (`0x4366c300`) que es **miembro de la familia
  de loggers** `push {r3}` … `movs r2,#0x9a` → `osal_try_valloc_msg` → `vsnprintf` →
  `osal_snd_msg`, y que usa el **GID de log `0x008f0139`**, el mismo que `[PANDA]`,
  `[ACCY]`, `[CAM_UTIL_ADJ]`, `[CAM_UTIL_SENS]` y `[CAMERA_MAIN_FC]`.
* **No toca la línea del obturador**: ninguna de las 21 cadenas menciona obturador,
  sensor, exposición ni lectura → **S51 (A/B/C = NO) se mantiene**.

## 2. Qué es `[TP_R]`

| Rasgo | Evidencia (vaddr) |
|---|---|
| Código del módulo | `0x4366c2a4` – `0x4366cd38` (18 funciones) |
| Tabla de comandos de depuración | `0x43fe3f28`, entradas de 12 B `{nombre, descripción, handler}` |
| Registro de la tabla | función `0x4366cadc`: `ldr r0,"tp"` (`0x43c8127a`) en `0x4366cae0` + `ldr r1,0x43fe3f28` en `0x4366cae2` + `b.w 0x435ab6f0` en `0x4366cae8` |
| Comandos | `start`, `set_mode` ("Set TP Mode"), `print_xy`, `dds_on` ("DDS On"), `dds_off` ("DDS Off") |
| Ciclo de vida | `boot_init_tp` `0x4366caf4` (llamado desde `0x43a464dc`, id de arranque **135**, parámetro 280) y `boot_exit_tp` `0x4366c6e8` (desde `0x43a4670c`, id **134**) |
| Colas OSAL (GID) | log **`0x008f0139`** (`0x4366c314`), eventos **`0x005c011c`** (`0x4366c56c`), control **`0x01010227`** (`0x4366c85c` = `osal_rcv_msg`, `0x4366cc2a` = `osal_reg_sync_msg_queue_cb`), **`0x00910040`** en el boot (`0x4366cbf0`, `0x4366c774`) |
| Callback de la cola de control | `0x4366ca90` (registrado en `0x4366cc30`; es el despachador de eventos táctiles `0x4366ca92`) |
| Publicación de eventos | `0x4366c8fc` (byte `0x11` en +0, u16 en +2, u32 en +4 y +8) y `0x4366c540` (byte `0x11` en +0, bytes en +1..+3, u32 en +4 y +8) construyen un mensaje de **12 B** y lo envían (vía `0x4366c498`) a la cola `0x005c011c` |
| Ids de campo publicados | `0x112`, `0x113`, `0x114` (evento de 3 campos, `0x4366c978`) y `0x136`, `0x13c` (evento de 2 campos, `0x4366c924`) |
| Recepción | `osal_rcv_msg(0x01010227, …, -1)` bloqueante en `0x4366c864` (bucle de `0x4366c840`) |

Contenido de las trazas: **errores de la API OSAL** (`osal_try_valloc_msg`,
`osal_snd_msg`, `osal_free_msg`, `osal_unreg_msg_queue_cb`, `osal_free_timer`,
`osal_rcv_msg`, `osal_set_timer`, `osal_alloc_timer`,
`osal_reg_sync_msg_queue_cb`), **ciclo de vida** (`boot_init_tp come`,
`boot_exit_tp come`), **control** (`unkown tp_type`, `unknown cmd`) y **tamaño de
lectura** (`read size error`).

**Sigla:** *no se desarrolla*. No hay ningún byte que exponga qué significa "TP";
los únicos contexts son el token `[TP_R]`, la etiqueta antigua `[TP R]` y el nombre
registrado `tp`. Por el **contenido de las cadenas muertas** (`key_code`, `xy`,
`status`, `ex_status`, `ex_info`, `<Water>`, `print_xy`, "Set TP Mode") el módulo
gestiona **eventos de panel táctil**; la sub-etiqueta `<Water>` aparece una sola vez.

## 3. Las 18 trazas `[TP_R]` (dirección → texto → sitios → función)

| # | cadena | texto | sitios PIC | función emisora |
|---|---|---|---|---|
| 1 | `0x43c80f23` | `[TP_R]: ERR. osal_try_valloc_msg. err=0x%x, L=%d` | `0x4366c3b0`, `0x4366c5a0`, `0x4366c65c` | `0x4366c388`, `0x4366c568`, `0x4366c624` |
| 2 | `0x43c80f54` | `[TP_R]: ERR. osal_snd_msg. err=0x%x, L=%d` | `0x4366c3e2`, `0x4366c5f4`, `0x4366c698` | `0x4366c388`, `0x4366c568`, `0x4366c624` |
| 3 | `0x43c80f7e` | `[TP_R]: debug_num=0x%02x` | **ninguno** | — (muerta) |
| 4 | `0x43c80faf` | `[TP_R]: ERR. osal_free_msg. err=0x%x, L=%d` | `0x4366c6cc`, `0x4366c8bc` | `0x4366c624`, `0x4366c840` |
| 5 | `0x43c80fda` | `[TP_R]: boot_exit_tp come` | `0x4366c704` | `0x4366c6e8` |
| 6 | `0x43c80ff4` | `[TP_R]: ERR. osal_unreg_msg_queue_cb. err=0x%x, L=%d` | `0x4366c7ba` | `0x4366c6e8` |
| 7 | `0x43c81029` | `[TP_R]: ERR. osal_free_timer. err=0x%x, L=%d` | `0x4366c802` | `0x4366c6e8` |
| 8 | `0x43c81056` | `[TP_R]: ERR. osal_rcv_msg. err=0x%x, L=%d` | `0x4366c88a` | `0x4366c840` |
| 9 | `0x43c81080` | `[TP_R]: ERR. osal_set_timer. err=%x, L=%d` | `0x4366ca22` | `0x4366c978` |
| 10 | `0x43c810aa` | `[TP_R]: ERR. unkown tp_type. tp_type=0x%x, L=%d` | `0x4366ca50` | `0x4366c978` |
| 11 | `0x43c810da` | `[TP_R]: ERR. unknown cmd. cmd=0x%x, L=%d` | `0x4366cad2` | `0x4366ca92` |
| 12 | `0x43c81103` | `[TP_R]: ERR. osal_valloc_msg. err=0x%x, L=%d` | **ninguno** | — (muerta) |
| 13 | `0x43c81130` | `[TP_R]: <Water> key_code=0x%08x, xy=0x%08x, status=0x%08x, ex_status=0x%08x, ex_info=0x%08x` | **ninguno** | — (muerta) |
| 14 | `0x43c811dd` | `[TP_R]: key_code=0x%08x, xy=0x%08x, status=0x%08x, ex_status=0x%08x, ex_info=0x%08x` | **ninguno** | — (muerta) |
| 15 | `0x43c8127d` | `[TP_R]: boot_init_tp come` | `0x4366cb14` | `0x4366caf4` |
| 16 | `0x43c81297` | `[TP_R]: ERR. read size error. size=0x%x, L=%d` | `0x4366cb56`, `0x4366cc9e` | `0x4366caf4` |
| 17 | `0x43c812c5` | `[TP_R]: ERR. osal_alloc_timer. err=0x%x, L=%d` | `0x4366cc1c` | `0x4366caf4` |
| 18 | `0x43c812f3` | `[TP_R]: ERR. osal_reg_sync_msg_queue_cb. err=0x%x, L=%d` | `0x4366cc56` | `0x4366caf4` |

**Cadenas con la etiqueta antigua `[TP R]` (las 3, muertas):**

| cadena | texto | sitios |
|---|---|---|
| `0x43c80f97` | `[TP R] debug_num = %02x` | ninguno |
| `0x43c8118c` | `[TP R] <Water> key_code=%08x, xy=%08x, status=%08x, ex_status=%08x, ex_info=%08x` | ninguno |
| `0x43c81231` | `[TP R] key_code=%08x, xy=%08x, status=%08x, ex_status=%08x, ex_info=%08x` | ninguno |

Las 7 cadenas marcadas como muertas se comprobaron **con las dos reglas**: sin
referencia PIC (estricta ni "ancha", en toda la imagen) **y** sin puntero absoluto de
4 B en los 11,4 MB.

## 4. Mapa función → traza (8 funciones emisoras)

| función | rol (verificado por desensamblado) | trazas |
|---|---|---|
| `0x4366c388` | mini-reporter de 4 B: `osal_try_valloc_msg(GID 0x005c011c, …, 4, 0)` + `osal_snd_msg` | #1, #2 |
| `0x4366c568` | emisor de un mensaje de 12 B (`0x4366c540` → `0x4366c498`) | #1, #2 |
| `0x4366c624` | emisor de un mensaje de 12 B, con liberación del mensaje previo | #1, #2, #4 |
| `0x4366c6e8` | **`boot_exit_tp`**: desregistra la cola (`0x43561298`), libera el temporizador | #5, #6, #7 |
| `0x4366c840` | **bucle de recepción**: `osal_rcv_msg` bloqueante y `osal_free_msg` | #4, #8 |
| `0x4366c978` | publicador de evento de 3 campos (`0x112/0x113/0x114`) + temporizador + comprobación de `tp_type` | #9, #10 |
| `0x4366ca92` | **despachador de eventos táctiles**: `cmd=[r0]`; `1` → `0x4366c978`, `2` → `0x4366c924`, otro → traza de error | #11 |
| `0x4366caf4` | **`boot_init_tp`**: registra la cola (`0x435612b4`), reserva temporizador (`0x435613b0`), publica la tabla `tp` (`0x4366cae0`) | #15, #16, #17, #18 |

Recuento: **20 sitios** de emisión en **8 funciones** (regla estricta).

Funciones auxiliares del módulo (sin traza propia): `0x4366c2a4` (handler `print_xy`,
activa/desactiva un flag global en `0x43e64548`), `0x4366c2bc` (cabecera de 32 B),
`0x4366c300` (reporter de log), `0x4366c410`, `0x4366c498`, `0x4366c540`,
`0x4366c8fc`, `0x4366c924`, `0x4366cadc` (registra la tabla `tp`).

## 5. Ficheros fuente

**NO VERIFICADO / no existen en el binario.** El módulo **no contiene ningún nombre de
fichero** (`.c`/`.cpp`/`.h`): en todo el rango `0x4366c2a4`–`0x4366cd38` las únicas
cadenas referenciadas por PIC son las 21 de `[TP_R]`/`[TP R]` más el literal `tp`.
Los únicos nombres de fichero de la imagen que contienen "tp/touch" son los cuatro de
`Camera::FC` (`FC/Feature/fc_feature_touch.cpp` `0x43cefe59`, `FC/Seq/fc_seq_touch.cpp`
`0x43cf082f`, `FC/Alg/fc_alg_touch.cpp` `0x43cf0847`,
`FC/Feature/fc_feature_touch_for_scanaf.cpp` `0x43cf085f`), que **no** pertenecen a
este módulo (son de la capa de AF/FC).

## 6. Relación con `[DMMYSIOCOM]` (S113 `[CAM_DMM]`) — **no es el mismo código**

S130 encontró que 2 de las 18 trazas de `[TP_R]` coinciden *textualmente* con la A7S.
Investigado:

* Los 2 textos son las plantillas OSAL `ERR. osal_snd_msg. err=0x%x, L=%d` y
  `ERR. osal_free_msg. err=0x%x, L=%d`.
* En la **A7S fw3.20** existen bajo la etiqueta `[DMMYSIOCOM]`
  (`0x43c73764`, `0x43c73792`), referenciadas desde `0x4362cc7a`/`0x4362cc9c`
  (función `0x4362cc44`).
* En el **A6300 fw2.01**: `0x43d7296b`/`0x43d72999` (ref. `0x4364841e`/`0x43648440`).
* En la **A6000 fw3.21** el módulo `[DMMYSIOCOM]` **sigue existiendo intacto**
  (`0x43c72e7d`, `0x43c72eab`, ref. `0x43628a5e`/`0x43628a80`) y son las **únicas
  2** cadenas con esa etiqueta en los tres firmwares.

⇒ El módulo `[DMMYSIOCOM]` es **otro subsistema** (código en `0x43628xxx`, cola
propia) que reutiliza las mismas plantillas de error OSAL. **No son "el mismo código
con otra etiqueta"**: son el mismo *texto* en dos módulos distintos. La coincidencia de
S130 es un **falso positivo de la comparación textual**.

## 7. Relación con la familia de loggers de S151 — **CONFIRMADO**

* Todas las trazas de `[TP_R]` salen por `0x4366c300`:
  `0x4366c300 push {r3}` (bytes `08 b4`) → `0x4366c302 movs r3,#0` →
  `0x4366c304 push.w {r0,r1,r2,r4…lr}` → `0x4366c318 movs r2,#0x9a` →
  `0x4366c31c bl 0x435612d0` (`osal_try_valloc_msg`) → `0x4366c346 bl 0x439c5004`
  (`vsnprintf`) → `0x4366c376 bl 0x4356120c` (`osal_snd_msg`).
* El **GID de log es `0x008f0139`** (pool `0x4366c384`), el **mismo** que `[PANDA]`
  (S151), `[ACCY]` (S136), `[CAM_UTIL_ADJ]`/`[CAM_UTIL_SENS]` (S143/S144) y
  `[CAMERA_MAIN_FC]` (S138).
* Recuento de la familia (bytes, no REA):
  * patrón **estricto** (`push {r3}` inmediatamente seguido de `movs r2,#0x9a`):
    A6000 **43**, A7S **0**, A6300 **0** → reproduce la cifra de S151;
  * patrón **laxo** (`push {r3}` … `movs r2,#0x9a` a ≤40 B): A6000 **561**,
    A7S **0**, A6300 **2**. El reporter del TP (`0x4366c300`) está en este
    subconjunto (lleva `movs r3,#0` en medio porque recibe el formato en `r3`).
* ⇒ La hipótesis de S151 queda **verificada**: `[TP_R]` **es** un módulo de
  tarea/cola y sus trazas se emiten por el *reporter* de un framework de mensajes.

## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| cadenas `[TP_R]` (con guion bajo) | **18** | 0 | 0 |
| cadenas `[TP R]` (con espacio) | 3 (muertas) | **3** (0x43c838e4, 0x43c838fc, 0x43c8394d) — **0 vivas** | **4** (0x43d8337f, 0x43d83397, 0x43d833e8, 0x43d83421) — **0 vivas** |
| trazas vivas del módulo TP | **14** (20 sitios, 8 funciones) | **0** | **0** |
| módulo TP presente (código) | `0x4366c2a4`–`0x4366cd38` | `~0x43674d00`–`0x43675600` (sin ninguna cadena referenciada) | `~0x43693000`–`0x43693400` (sin ninguna cadena referenciada) |
| tabla de comandos DDL | `0x43fe3f28` | `0x43fe54d0` | `0x441a59c0` |
| registro con el nombre `tp` | `0x4366cae8` → `bl 0x435ab6f0` | `0x43675370` → `b.w 0x435ae240` | `0x43693300` → `b.w 0x435aed78` |
| contenido de la tabla | `start`, `set_mode`/`Set TP Mode`, `print_xy`, `dds_on`/`DDS On`, `dds_off`/`DDS Off` | **idéntico** | **idéntico** |

Conclusiones:

1. El **módulo TP existe en los tres firmwares** (misma tabla de 5 comandos, misma
   entrada de 12 B `{nombre, descripción, handler}`, mismo registro con el nombre
   `tp`). **No es material propio de la A6000.**
2. La fw3.21 de la A6000 **añade 15 trazas nuevas** (ciclo de vida + 10 errores OSAL +
   `unkown tp_type` + `unknown cmd` + `read size error`) a un módulo que antes era
   **silencioso**: en la A7S el código del módulo no referencia ninguna cadena.
   Coherente con la tesis de S128 (la fw3.21 **reescribe el logging**).
3. La etiqueta antigua `[TP R]` **ya estaba muerta** en la A7S y en el A6300 (0
   referencias PIC y 0 punteros absolutos); en la A6000 sigue muerta **y** se
   duplica en la forma nueva `[TP_R]: …` (también muerta). El contenido de eventos
   (`key_code/xy/status/ex_status/ex_info`) **no se emite en ninguno** de los tres
   firmwares.
4. Los 2 "textos comunes" de S130 son plantillas OSAL compartidas con
   `[DMMYSIOCOM]` (§6), no código común.

## 9. Interés para la línea del obturador

**Ninguno.** Barrido léxico de las 21 cadenas (`shut`, `silent`, `electro`, `mech`,
`sensor`, `exposure`, `readout`, `drive`, `imager`, `bracket`, `sweep`, `interval`,
`jpeg`, `movie`, `fps`, `curtain`): la **única** coincidencia es `read` en
`[TP_R]: ERR. read size error. size=0x%x, L=%d` (`0x43c81297`), que habla del
**tamaño leído** por una llamada de la API OSAL (`0x435613b0`), no de lectura de
sensor. El módulo no menciona obturación, disparo, modo de lectura ni imager →
**S51 (A/B/C = NO) se mantiene**.

## 10. NO VERIFICADO / abierto

* **Significado de la sigla "TP"**: no se desarrolla (no hay bytes que la expandan).
  "DDS" (`dds_on`/`dds_off`, "DDS On"/"DDS Off") tampoco.
* **Significado de `<Water>`** y de los campos `ex_status`/`ex_info`.
* **Quién consume** los eventos de 12 B publicados en la cola `0x005c011c` (ids de
  campo `0x112`/`0x113`/`0x114`/`0x136`/`0x13c`): no se ha localizado el consumidor.
* **Nombres de las funciones OSAL** `0x43561244`, `0x4356127c`, `0x435613b0`,
  `0x43561420`: deducidos del texto de las propias trazas, no de una tabla de
  símbolos.
* **Fichero(s) fuente** del módulo: no hay ninguno embebido.
* Si la A7S tuvo alguna vez vivas las trazas `[TP R]`: en el binario disponible ya
  están muertas.
* La separación versión/modelo (ya señalada en S130 §4) sigue vigente: no hay una fw
  anterior de la A6000 en el repositorio.

## 11. Revisión del agente principal

*(vacío)*

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (19 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 18 cadenas `[TP_R]` en la A6000 fw3.21 entre `0x43c80f23` y `0x43c812f3`
   (**14 vivas**: 20 sitios PIC en 8 funciones emisoras; **4 muertas**) y **3** más con la etiqueta
   antigua `[TP R]`, todas muertas → 21 cadenas con el token en total. En la A7S hay 3 `[TP R]` y
   en el A6300 4, **0 vivas** → el módulo ya existía **silencioso**.
2. **Estructura verificada**: código `0x4366c2a4`–`0x4366cd38` (18 funciones), con
   `boot_exit_tp` `0x4366c6e8`, bucle de recepción `0x4366c840`, despachador `0x4366ca92` y
   `boot_init_tp` `0x4366caf4` (llamados desde `0x43a464dc` id 135 y `0x43a4670c` id 134);
   **tabla de comandos DDL** `0x43fe3f28` (`start`, `set_mode`, `print_xy`, `dds_on`, `dds_off`)
   registrada con el nombre **`tp`** en `0x4366cae8`; colas OSAL: log `0x008f0139`, eventos
   `0x005c011c`, control `0x01010227`.
3. **S151 confirmado**: el reporter `0x4366c300` (`push {r3}` … `movs r2,#0x9a` → `osal_try_valloc_msg`
   → `vsnprintf` → `osal_snd_msg`) es **miembro de la familia**; recuentos estricto 43/0/0
   (reproduce S151) y laxo 561/0/2 → el conteo con la regla estricta es el canónico.
4. **Corrección importante de S130 (falso positivo detectado)**: los 2 "textos comunes" de S130
   entre `[TP_R]` y `[DMMYSIOCOM]` son las **plantillas OSAL** `ERR. osal_snd_msg…` /
   `ERR. osal_free_msg…`; en la A7S están en `0x43c73764`/`0x43c73792` (ref. `0x4362cc7a`) y en el
   A6300 en `0x43d7296b`/`0x43d72999`, mientras que en la A6000 el módulo sigue intacto en
   `0x43c72e7d`/`0x43c72eab` (ref. `0x43628a5e`/`0x43628a80`) → **código distinto**, luego
   **falso positivo textual** (el texto es genérico de OSAL, no identidad de módulo).
5. **Diferencial**: la tabla de comandos y el registro `tp` existen en los tres firmware
   (`0x43fe3f28` / `0x43fe54d0` / `0x441a59c0`) → el módulo existía **silencioso** y la fw3.21
   **añade 15 trazas** nuevas.
6. **Negativo acotado**: barrido de las 21 cadenas → la única coincidencia es `read` en
   `[TP_R]: ERR. read size error` (tamaño leído por una llamada OSAL) → **sin efecto en S51**.
