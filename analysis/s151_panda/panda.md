# S151 — el módulo `[PANDA]` (10 trazas) del subsistema de lente de la A6000 fw3.21

> Hito S151 de la línea de RE general. Todo lo que sigue está verificado sobre **bytes**
> del blob `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21, 11 427 236 B), con
> la convención **vaddr = 0x43541000 + file_offset** (también válida para la A7S fw3.20 y
> el A6300 fw2.01).
> Regla de referencias: **estricta** (canónica del repo,
> `analysis/s106_imaging_cap/scan_pic_refs_strict.py`; nota de sesgos:
> `analysis/s106_imaging_cap/pic_xref_methodology.md`).
> Datos estructurados: `analysis/s151_panda/panda.json` (generado por
> `analysis/s151_panda/build_panda.py`, que **recalcula todo desde los bytes**).
> Nota breve: `docs/capture/s151-panda.md`. Tests: `tests/test_s151_panda.py`.

---

## 1. Resumen

* `[PANDA]` **no es un módulo de logging registrado** (a diferencia de `LENS_MOUNT`, que sí
  lo es): el token sólo existe embebido dentro del texto de **10 cadenas de error**, todas
  con la misma forma `[PANDA]: Panda_SendMessage: <canal> osal_<valloc|snd>_msg error!\n`.
* El nombre de la función de origen está escrito en el propio mensaje: **`Panda_SendMessage`**.
  La sigla **no se desarrolla** en ningún byte del firmware (sin RTTI, sin nombre de
  fichero, sin glosario): queda **sin desarrollar**.
* Lo que sí es "Panda" es la **capa de envío de mensajes del subsistema de lente**
  (`Camera::Lens`, zona `LENS_MOUNT`): un gestor con **5 canales** —`Pre1`, `Pre2`,
  `Post1`, `Post2`, `Async`— y **7 colas OSAL**. Es un **gestor de colas/mensajes**, no una
  tarea y no una cola única.
* Las 10 trazas son **errores de asignación y de envío** de ese gestor: no hay ni una sola
  traza de datos, de estado o de tiempo. **0/10 mencionan obturación, disparo, lectura del
  sensor o tiempos de exposición** → **sin efecto en S51**.

## 2. Las 10 trazas (dirección exacta + texto)

Bloque **contiguo** `0x43c9a599`–`0x43c9a7c8` (10 × 57 bytes), en la zona de cadenas de la
lente, justo detrás de la cadena de módulo `LENS_MOUNT` (`0x43c9a58e`) y antes de
`[LENS_PDR]: BonoboDSP_Send: Data latch failed!` (`0x43c9a7ca`).

| # | vaddr | texto |
|---|---|---|
| 1 | `0x43c9a599` | `[PANDA]: Panda_SendMessage: Pre1 osal_valloc_msg error!\n` |
| 2 | `0x43c9a5d2` | `[PANDA]: Panda_SendMessage: Pre2 osal_valloc_msg error!\n` |
| 3 | `0x43c9a60b` | `[PANDA]: Panda_SendMessage: Post1 osal_valloc_msg error!\n` |
| 4 | `0x43c9a645` | `[PANDA]: Panda_SendMessage: Post2 osal_valloc_msg error!\n` |
| 5 | `0x43c9a67f` | `[PANDA]: Panda_SendMessage: Async osal_valloc_msg error!\n` |
| 6 | `0x43c9a6b9` | `[PANDA]: Panda_SendMessage: Pre1 osal_snd_msg error!\n` |
| 7 | `0x43c9a6ef` | `[PANDA]: Panda_SendMessage: Pre2 osal_snd_msg error!\n` |
| 8 | `0x43c9a725` | `[PANDA]: Panda_SendMessage: Post1 osal_snd_msg error!\n` |
| 9 | `0x43c9a75c` | `[PANDA]: Panda_SendMessage: Post2 osal_snd_msg error!\n` |
| 10 | `0x43c9a793` | `[PANDA]: Panda_SendMessage: Async osal_snd_msg error!\n` |

**Estructura de los 5 canales** (deducida de los nombres, verificada en el código):
5 × (*valloc*) + 5 × (*snd*). Los 5 nombres de canal aparecen en el mismo orden en el
código: `Pre1` → `Pre2` → `Post1` → `Post2` → `Async`.

## 3. ¿Qué es "Panda"? Base textual (¡no inventada!)

| Evidencia | Dónde | ¿Está en la A7S/A6300? |
|---|---|---|
| Nombre de la función de origen en el texto de las trazas: `Panda_SendMessage` | `0x43c9a599`…`0x43c9a793` | **No** (0 apariciones) |
| Parámetro del driver de **iris (drive analógico)**: `uc_PandaADErrorOpen` | cadena `0x43c99267`, puntero en la tabla de parámetros `0x43febe04` → variable `0x43e0a482` | **Sí** (1 en cada uno) |
| Parámetro del driver de iris: `uc_PandaADErrorClose` | cadena `0x43c9927b`, puntero en `0x43febe14` → variable `0x43e84c84` | **Sí** (1 en cada uno) |
| Tabla de parámetros donde viven los dos nombres anteriores | `0x43febd54`–`0x43febe60` (registros de 16 B: `{direccion_variable, puntero_al_nombre, 1, 0}`; p. ej. `0x43febe00`=var, `0x43febe04`=nombre, `0x43febe08`=1) | sí (estructura equivalente) |

Negativos verificados sobre el blob completo de la A6000:

* **0** clases RTTI con "Panda" (búsqueda insensible a mayúsculas sobre los 11,4 MB).
* **0** nombres de fichero `*Panda*`.
* **0** cadenas independientes iguales a `PANDA` → **no hay registro de módulo con ese
  nombre** (comparar con `LENS_MOUNT`, que sí existe como cadena suelta en `0x43c9a39c` y
  `0x43c9a58e` y se compara en `0x4370727a` con `strcmp`-like `0x439c5d18`; el getter del
  nombre de módulo está en `0x43705a84`).
* **0** glosario / expansión de la sigla.

⇒ **Conclusión**: "Panda" es un **nombre propio de un subsistema de mensajería de la
lente**, usado (a) como espacio de nombres de dos parámetros del drive de iris y (b) como
prefijo de las trazas de error de `Panda_SendMessage`. **La sigla se deja SIN DESARROLLAR**
(no se inventa su expansión).

## 4. Mapa función → traza (15 sitios de emisión, regla estricta)

Las **10 cadenas están referenciadas** (0 muertas) en **15 sitios** repartidos en **4
funciones** del código, más un **helper privado** que las formatea.

| Función | Inicio | Rango de código | Trazas que emite | Sitios (`add rX,pc`) |
|---|---|---|---|---|
| `F1_init` (init del gestor Panda) | `0x437073cc` | `0x437073cc`–`0x43707626` | Pre1/Pre2/Post1/Post2/Async **valloc** | `0x4370744a`, `0x4370745e`, `0x43707470`, `0x43707482`, `0x43707494` |
| `F4_pre` (envío "Pre") | `0x43707f8c` | `0x43707f8c`–`0x43708146` | Pre1 **snd**, Pre1 **valloc**, Pre2 **snd**, Pre2 **valloc** | `0x43708048`, `0x43708066`, `0x4370811a`, `0x43708138` |
| `F5_post` (envío "Post") | `0x437081b8` | `0x437081b8`–`0x43708372` | Post1 **snd**, Post2 **valloc**, Post2 **snd**, Post2 **valloc** | `0x43708280`, `0x4370829e`, `0x43708346`, `0x43708364` |
| `F6_async` (envío "Async") | `0x437083e4` | `0x437083e4`–`0x4370855e` | Async **snd**, Async **valloc** | `0x43708532`, `0x43708550` |

Nota sobre los inicios: `F4`, `F5` y `F6` tienen **shrink-wrapping** (el `ldr rX,[pc]`
precede al `push.w`); por eso la entrada real es `0x43707f8c` / `0x437081b8` /
`0x437083e4` y no la del `push`.

### Helper de reporte: `0x43707324`

Es el **logger privado del módulo PANDA**, y tiene la **misma familia** que el logger de
`[CAMERA_MAIN_FC]` (`0x437b7158`, S138) y que el de `[LENS_PDR]` (`0x437085b0`):

```
0x43707324  push {r3}                ; r3 = cadena de formato (varargs en la pila)
0x43707326  movs r2, #0x9a           ; tamaño del mensaje OSAL = 154
0x4370732c  add  r6, sp, #0x44
0x43707330  ldr  r0, [pc]            ; 0x008f0139  (GID de log)
0x4370733c  bl   0x435612d0          ; osal_try_valloc_msg(GID, &msg, 0x9a, 0)
0x43707352  strh r2, [r4]            ; msg[0x00] (u16) = 1
0x43707354  strh r3, [r4,#2]         ; msg[0x02] (u16) = 0x16 (22)  <-- id de log de PANDA
0x4370735c  strh r2, [r4,#0x10]      ; msg[0x10] (u16) = 1
0x43707372  bl   0x43561244          ; rellena 32 B de cabecera con el id 0x00910042
0x43707376  ldrd r2, r3, [sp, #0x18] ; los 8 ultimos bytes -> msg[0x08..0x0f]
0x43707388  bl   0x439c5004          ; vsnprintf(msg+0x14, 0x81, fmt, va_list)
0x437073a8  strb r2, [r3,#0x14]      ; msg[0x14+len] = '\n'
0x437073b4  bl   0x4356120c          ; osal_snd_msg(0x008f0139, msg)
```

⇒ **Las trazas `[PANDA]` no salen por una cola propia: salen por la cola de log del
firmware (GID `0x008f0139`)**, el mismo GID que usan `[ACCY]` (S136), `[CAM_UTIL_ADJ]`
(S143), `[CAM_UTIL_SENS]` (S144) y `[CAMERA_MAIN_FC]` (S138).

El patrón de prólogo `push {r3}` + `movs r2,#0x9a` aparece en **43 funciones** de la A6000
fw3.21 y en **0** de la A7S fw3.20 y del A6300 fw2.01 → es una **familia de loggers
introducida en esta fw**.

### Quién llama a las 4 funciones

| Función | Llamador | Sitio | Contexto del llamador |
|---|---|---|---|
| `F1_init` | `0x43721624` = **`void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)`** (cadena `0x43c9ae4e`) | `0x4372163e` (`bl`) | zona `Camera::Lens` |
| `F4_pre` | `0x437217f8` (envoltorio "Pre", zona `Camera::Lens`) → `0x43793efe` | `0x43721818` (`bl`) | función que registra `[CAMERA_MAIN_SYNC]: vfc%d[%d] shut%d->%d…` (`0x43ca3a50`) |
| `F5_post` | `0x43721840` (envoltorio "Post", zona `Camera::Lens`) → `0x4379064e` | `0x43721848` (`b.w`) | `[CAMERA_MAIN_SYNC]: HS_Main: BONOBO flg timeout %dV #%d, %04x` (`0x43ca3169`) |
| `F6_async` | `0x436f4d1c` | `0x436f4d74` (`b.w`) | zona de código de la montura/lente |

## 5. Mecánica interna (qué hace el "Panda")

* **7 colas OSAL** abiertas por `F1_init` a través del thunk `0x43561508` (slot `+0x2e0`)
  con los ids: `0x00f900bc`, `0x00f90078`, `0x00f900d5` (los tres primeros, en
  `0x437073d0`/`0x437073e0`/`0x437073ec`), `0x00f90191` (`0x437074a2`), `0x00f90184`
  (`0x43707556`), `0x00f90520` (`0x43707564`) y `0x00f90521` (`0x4370757c`); los siete
  valores están en el pool literal `0x43707628`–`0x43707640`.
* **5 buffers de mensaje de 0x40 B**, uno por canal, reservados con
  `osal_try_valloc_msg(GID=0x00740017, <handle>, 0x40)` a través del envoltorio
  `[CAM_UTIL]` `0x4390406c` (que en error deja la traza
  `[CAM_UTIL]: osal_try_valloc_msg 0x%02x error! %dtimes [%08x]`, `0x43ccf242`). Se guardan
  en la tabla global `0x4401eee4`:

  | canal | slot destino (buffer) | slot fuente (handle) |
  |---|---|---|
  | Pre1 | `+0x7570` | `+0x1420` |
  | Pre2 | `+0x4284` | `+0x4930` |
  | Post1 | `+0x2954` | `+0x1d10` |
  | Post2 | `+0x7350` | `+0x6248` |
  | Async | `+0x7c74` | `+0x5d88` |

* **Envío**: thunk OSAL `0x43561228` (slot `+0x1d8`) con `r0 = 0x00740017` (GID de los
  mensajes de lente) y `r1` = mensaje.
* Los **5 buffers** se comprueban justo antes de usarlos: si el buffer ya está ocupado
  (`cbz`) se emite la traza de *valloc*; si el envío OSAL devuelve error, la traza de
  *snd*. De ahí las 2 trazas por canal.

**Fichero fuente**: el código PANDA **no contiene ningún nombre de fichero** (las únicas
cadenas que referencia en `0x43707324`–`0x43708560` son las 10 trazas). La atribución
sólo puede hacerse a nivel de **módulo**: el código está **inmediatamente después** de la
función que registra el módulo `LENS_MOUNT` (`0x43707270`, compara `'LENS_MOUNT'`
`0x43c9a58e`) y **antes** del código `[LENS_PDR]` (`BonoboDSP_Send/Rcv`, `0x437085b0`).
⇒ **fichero NO VERIFICADO**; el módulo es la gestión de la lente (`Camera::Lens`).

## 6. Relación con los módulos ya documentados

| Módulo / hito | Relación con `[PANDA]` |
|---|---|
| **`[LENS_MOUNT]`** (S133, zona de montura) | **Contiguo**: el código PANDA va justo detrás de la función de registro de `LENS_MOUNT` (`0x43707270`); comparten la zona de código y la tabla global `0x4401eee4`. |
| **`[LENS_YC]` / `Camera::Lens`** | **Contiguo y es el propietario**: la función que inicializa el gestor Panda es `void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` (`0x43c9ae4e`, código `0x43721624`). La clase `Camera::Lens::ODL` (`0x43c9af18`–`0x43c9b30e`) usa `AsyncSend`/`AsyncRecieve` (`[LENS_YC]: %s: AsyncSend error (0x%x)` `0x43c9b026`, `AsyncRecieve error` `0x43c9b04c`), coherente con el canal **Async** del PANDA. |
| **`[LENS_PDR]`** (`BonoboDSP_Send/Rcv`, `0x43c9a7ca`–`0x43c9a86e`) | **Vecino inmediato** por el otro lado; "BONOBO" es el DSP de la lente (`[CAMERA_MAIN_SYNC]: HS_Main: BONOBO flg timeout` `0x43ca3169`). |
| **`[CAMERA_MAIN_SYNC]`** (S112) | **Consumidor**: los envoltorios "Pre" y "Post" del PANDA se llaman desde la zona de sincronización (`0x43793efe`, `0x4379064e`). El PANDA es la vía por la que la sincronización de captura habla con la lente. |
| **`[CAM_UTIL]`** (S143/S144) | **Interfaz de reserva**: los buffers del PANDA se reservan por el envoltorio `[CAM_UTIL]` `0x4390406c`. |
| **`[CAMERA_MAIN_FC]`** (S138) | **Hermano de logger**: su logger `0x437b7158` tiene el mismo prólogo y el mismo GID de log `0x008f0139` (pool `0x437b71f8`) que el logger PANDA `0x43707324`. |
| **Cola OSAL de S93** | **Comparte mecánica, no código**: el PANDA usa los thunks OSAL (`0x43561228` enviar, `0x4356120c` `osal_snd_msg`, `0x435612d0` `osal_try_valloc_msg`, `0x435612ec` `osal_free_msg`, `0x43561244`, `0x43561508` abrir cola). |
| **`[REL]` / `RelMgr`** (S125), **`[ACCY]`** (S136), **`[CDIAG]`/`[CTRLCORE]`** (S109/S137) | **Sin relación**: 0 llamadas desde el código PANDA a sus zonas; lo único común es la mecánica OSAL y, en `[ACCY]`, el GID `0x008f0139` (ambos usan la cola de log). |
| **`[CAM_IMAGER]`** (S115) / obturador | **Ninguna**: el código PANDA no referencia ninguna cadena `[CAM_IMAGER]` ni `[IMAGING]`. |

**Destinos de llamada del código PANDA** (`0x43707324`–`0x43708560`, exhaustivo, 47 `bl`/`blx`):
`0x43560cc8` (1), `0x4356120c` (1), `0x43561228` (5), `0x43561244` (1), `0x435612d0` (1),
`0x435612ec` (6), `0x43561508` (7) — *thunks OSAL*; `0x43707324` (7, el logger),
`0x43707d44` (1), `0x43707ec8` (1) — *helpers internos del propio módulo*;
`0x4390406c` (10, el envoltorio `[CAM_UTIL]` de `osal_try_valloc_msg`);
`0x439c5004` (1, `vsnprintf`), `0x439c5a04` (1, `memset`);
`0x43ada9fc` (1), `0x43adaa00` (1), `0x43b5e2a4` (1) — *helpers sin cadenas*; y 1 llamada
indirecta (`blx r4`). **Ninguna llamada entra en el driver del imager, en `[REL]`,
`[ACCY]`, `[CDIAG]`/`[CTRLCORE]` ni en ninguna zona de captura.**

## 7. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

### 7.1 Las trazas

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| ocurrencias del token `[PANDA]` | **10** | **0** | **0** |
| textos interiores (sin la etiqueta) presentes | 10/10 | **0/10** | **0/10** |
| `Panda_SendMessage` | 10 | **0** | **0** |
| `LENS_YC` (etiqueta hermana) | 21 | **0** | **0** |

(Confirma y precisa S130.)

### 7.2 …pero **el código sí existe en los tres**

Este es el hallazgo de fondo del hito:

* Los **7 ids de cola** (`0x00f900bc`, `0x00f90078`, `0x00f900d5`, `0x00f90191`,
  `0x00f90184`, `0x00f90520`, `0x00f90521`) aparecen **exactamente una vez en cada blob**,
  en el *pool literal* de la función equivalente:

  | función | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
  |---|---|---|---|
  | `F1_init` | `0x437073cc` | `0x43729910` | `0x437648d0` |
  | `F4_pre` | `0x43707f8c` | `0x4372a456` | — |
  | `F5_post` | `0x437081b8` | `0x4372a6b8` | — |
  | `F6_async` | `0x437083e4` | `0x4372a888` | — |

* La función equivalente de la A7S tiene **el mismo prólogo** (`push.w {r4-r8,lr}`) y
  **la misma secuencia de llamadas**, salvo las que reportan errores:

  | | A6000 `F1_init` | A7S `F1_init'` |
  |---|---|---|
  | abrir colas (thunk OSAL) | 7 | 7 |
  | registrar callback (`0x43b5e2a4` / `0x43b585aa`) | 1 | 1 |
  | comprobación (`0x43adaa00` / `0x43adbe76`) | 1 | 1 |
  | reservar 5 buffers de 0x40 B | 5 | 5 |
  | **reportar error (PANDA)** | **5** | **0** |

  Igual en `F4` (7 vs 6 llamadas) y en `F5` (5 vs 4): la diferencia es **exactamente la
  llamada al reporter**.

* La clase `Camera::Lens::ODL` está en los tres firmwares (**15** apariciones de su nombre
  en cada uno) y los mensajes `AsyncSend error` / `AsyncRecieve error` también (2 y 2).

⇒ **Lo propio de la fw3.21 de la A6000 es el LOGGING, no la funcionalidad** — el mismo
patrón que S130 (`[ACCY]`, `[DEPTH]`), S132 (`[CLK_CTRL]`) y S136 (`[ACCY]`).
Caveat de S130 §4: se mezcla versión y modelo (no hay una fw anterior de la A6000 en el
repositorio), así que no se puede separar "nuevo en la fw3.21" de "propio de este modelo";
lo que sí es sólido es que **no es "nuevo en la fw3.21" de la A6000 respecto a los otros
modelos**, porque el código ya está en la A7S fw3.20 y en el A6300 fw2.01.

## 8. Interés para la línea del obturador

* **Negativo acotado**: las 10 trazas no contienen `shut`, `shutter`, `silent`, `electro`,
  `mech`, `sensor`, `imager`, `expos`, `readout`, `bracket`, `sweep`, `interval`, `timer`
  (0 apariciones cada uno). El código PANDA no llama a ninguna zona del driver del imager.
* El **único vínculo** de "Panda" con un mecanismo físico es el par de parámetros
  `uc_PandaADErrorOpen` / `uc_PandaADErrorClose`, que están en la tabla del **drive
  analógico del diafragma (iris)** (`0x43febd54`–`0x43febe60`), junto a `uc_IrisHallAD`,
  `uc_iris_ad_min/max`, `us_IrisAnalogDrv`… → es decir, la gestión de **errores del drive
  del iris**, no del obturador.
* El PANDA gobierna el **intercambio de mensajes con la lente** (canales Pre/Post/Async) y
  se le invoca desde el código de sincronización (`[CAMERA_MAIN_SYNC]`); pero **no toca la
  exposición, la lectura del sensor ni el mecanismo de obturación** (0 llamadas fuera de los
  thunks OSAL y los helpers propios).
* ⇒ **Sin efecto en S51 (A/B/C = NO).** No se ha encontrado en el subsistema PANDA ningún
  mensaje de obturador electrónico.

## 9. NO VERIFICADO / abierto

1. **La sigla "PANDA"**: sin desarrollo textual posible. No se inventa.
2. **Fichero fuente** del código PANDA: no hay ningún nombre de fichero embebido; sólo se
   puede atribuir al módulo `LENS_MOUNT` / `Camera::Lens`.
3. **Significado de los 5 canales** (`Pre1`, `Pre2`, `Post1`, `Post2`, `Async`): se conocen
   los nombres y el orden; **NO** se ha determinado qué tarea los consume ni qué significan
   "pre"/"post" (¿pre-dataclamp/post-dataclamp? ¿antes/después del disparo?).
4. **Los 7 ids de cola OSAL** (`0x00f9xxxx`) no están decodificados (no se ha encontrado
   la tabla de nombres de cola en el blob).
5. **El GID `0x00740017`** no está decodificado (a qué destinatario/receptor corresponde).
6. El **id de log `0x16` (22)** escrito en `msg[0x02]` por el reporter no está decodificado
   (la familia de loggers escribe ids distintos: `[CAMERA_MAIN_FC]` escribe `3` en `msg[0x02]`
   y `5` en `msg[0x04]`).
7. **El papel de `0x00910042`** (primer argumento del thunk `0x43561244`, que rellena los 32 B
   de cabecera del mensaje) no está decodificado.
8. No se ha identificado **la cola OSAL de datos** que recibe los mensajes de lente que el
   PANDA envía (GID `0x00740017`): el thunk usado es `0x43561228` (slot `+0x1d8`), no el
   `osal_snd_msg` estándar `0x4356120c` (slot `+0x1d4`); el nombre de la función OSAL
   concreta NO VERIFICADO.
9. **El receptor final** de la cola de log `0x008f0139` está fuera de `av-cam.bin`
   (como en S136/S143/S144).
10. La comparación con la A6300 se ha limitado a `F1_init` (no se han localizado las
    equivalentes de `F4/F5/F6` en el A6300).

## 10. Revisión del agente principal

_(vacío)_

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (26 tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 10 apariciones de `[PANDA]` en la A6000 fw3.21 entre `0x43c9a599` y
   `0x43c9a7c8`; **0** en la A7S fw3.20 y el A6300 fw2.01 → confirmado con `bytes.count()`.
2. **Base textual, sin inventar la sigla**: "Panda" aparece en el **nombre de función**
   `Panda_SendMessage` (10/0/0) y en los **parámetros de iris** `uc_PandaADErrorOpen` `0x43c99267`
   y `uc_PandaADErrorClose` `0x43c9927b` (**1/1/1** en los tres firmware, tabla `0x43febe04`/
   `0x43febe14`). 0 RTTI, 0 ficheros y 0 cadena independiente `PANDA` → **`[PANDA]` no es un módulo
   de logging registrado** (al contrario que `[LENS_MOUNT]`).
3. **Mecánica verificada**: 10/10 referenciadas con **15 sitios** (regla estricta) en **4 funciones**
   (`F1_init` `0x437073cc` con 5, `F4_pre` `0x43707f8c` con 4, `F5_post` `0x437081b8` con 4,
   `F6_async` `0x437083e4` con 2) y logger privado `0x43707324` (7 `bl` + 3 `b.w`); **7 colas OSAL**
   (`0x00f900bc`, `0x00f90078`, `0x00f900d5`, `0x00f90191`, `0x00f90184`, `0x00f90520`,
   `0x00f90521`), **5 buffers de 0x40 B** con GID `0x00740017` (tabla `0x4401eee4`), envío por
   thunk `0x43561228` y errores por el GID de log `0x008f0139` (id `0x16`); lo inicializa
   `void Camera::Lens::Initialize(UPM_BOOT_FACTOR*)` `0x43721624` (`bl` en `0x4372163e`).
4. **Diferencial**: el token es 10/0/0 con 0/10 textos interiores, **pero el código existe en los
   tres** (los 7 ids de cola aparecen 1 vez en cada blob; `F1_init` equivalente en `0x43729910`
   (A7S) y `0x437648d0` (A6300), con el mismo prólogo y la misma secuencia de `bl` salvo las del
   reporter: F1 19 vs 14, F4 7 vs 6, F5 5 vs 4) → **lo nuevo es el logging, no la función**.
5. **Negativo acotado**: 0/10 menciones de obturador, sensor, exposición o tiempos; los 47 `bl` del
   código PANDA van solo a thunks OSAL, helpers propios y `[CAM_UTIL]`; el único vínculo físico es
   el **drive del iris** (`uc_PandaADError*`) → **sin efecto en S51**.
