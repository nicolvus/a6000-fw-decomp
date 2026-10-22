# S173 — `[CAM_UTIL]` (10) y `[CAMERA_ADJ]` (3): las utilidades compartidas de la familia `CAM_UTIL`

> Hito de la **línea de ingeniería inversa general**. Solo bytes de la A6000 fw3.21
> (`analysis/rea-independent/input/av-cam.bin`), con la A7S fw3.20 y el A6300 fw2.01 como
> comparación. Convención: `vaddr = 0x43541000 + file_offset`. Regla de referencias:
> **estricta** (mapa global en `analysis/s106_imaging_cap/pic_refs_strict_global.json`).

## 1. Resumen / veredicto

Las etiquetas **`[CAM_UTIL]`** (10 cadenas) y **`[CAMERA_ADJ]`** (3 cadenas) **no son un módulo
propio**: son el rótulo de **utilidades compartidas** por la familia `CAM_UTIL` (los módulos
`[CAM_UTIL_ADJ]` de S143 y `[CAM_UTIL_SENS]` de S144) y por el gestor de memoria **DMM** de
`[CAMERA_MAIN]`.

| etiqueta | cadenas | A6000 | A7S | A6300 | sitios PIC | funciones |
|---|---|---|---|---|---|---|
| `[CAM_UTIL]` | 10 | 10 | **0** | **0** | 13 | 10 |
| `[CAMERA_ADJ]` | 3 | 3 | **0** | **0** | 3 | 3 |

Las **13 cadenas están vivas** (0 muertas) y sus **16 sitios** caen en **13 funciones**:
5 en la zona **DMM** (`0x437e3c92`–`0x437e446e`) y 8 en la zona **`CAM_UTIL`** (`0x43900234`–
`0x43904092`), en funciones que **S143 y S144 no habían cubierto** porque emitían con otra
etiqueta.

**Hallazgo de coherencia**: la función de inicialización `0x4390178e` escribe el **id de módulo
`0xb5`** — exactamente el **módulo `0xb5`** que S144 identificó como compartido por
`[CAM_UTIL_ADJ]` y `[CAM_UTIL_SENS]`.

## 2. Las 13 cadenas y sus sitios

| # | cadena | sitio(s) | función | qué informa |
|---|---|---|---|---|
| 1 | `[CAM_UTIL]: DmmMemPool) MemPool Free Err addr:0x%08x [top 0x%08x btm 0x%08x]` | `0x437e3cb8` | `0x437e3c92` | error al liberar un bloque del *memory pool* del DMM |
| 2 | `[CAM_UTIL]: DmmMemPool) Dmm Close Err hdl:0x%04x` | `0x437e3d0e`, `0x437e4332` | `0x437e3ce4`, `0x437e4308` | error al cerrar un *handle* DMM |
| 3 | `[CAM_UTIL]: DmmMemPool) Dmm Open Err hdl:0x%04x` | `0x437e3dba`, `0x437e446e` | `0x437e3d92`, `0x437e4446` | error al abrir un *handle* DMM |
| 4 | `[CAM_UTIL]: AV DDS Alloc Msg Err:%x` | `0x43900254` | `0x43900234` | fallo al **asignar** un mensaje OSAL en «AV DDS» |
| 5 | `[CAM_UTIL]: AV DDS SndMsg Err:%x` | `0x4390029a` | `0x43900234` | fallo al **enviar** el mensaje |
| 6 | `[CAMERA_ADJ]:   Utility Adjust Ctrl OSAL MEM ALLOC Error : %x` | `0x43900da6` | `0x43900d54` | fallo de reserva OSAL en el **control de ajuste** |
| 7 | `[CAMERA_ADJ]:   Utility MS Mount Start OSAL MEM ALLOC Error : %x` | `0x43900e8a` | `0x43900d54` | ídem en el **Mount Start** de «Utility MS» |
| 8 | `[CAMERA_ADJ]:   Utility MS UnMount Start OSAL MEM ALLOC Error : %x` | `0x43900f6c` | `0x43900f1c` | ídem en el **UnMount Start** |
| 9 | `[CAM_UTIL]: EvtDrvnTsk) Send Err tid:%d->%d, func:%08x, arg:%x, %x` | `0x43901938` | `0x4390178e`… `0x43901938` | error al enviar un evento: *task id* origen→destino, función y argumentos |
| 10 | `[CAM_UTIL]: EvtDrvnTsk) Send Err Print Max...` | `0x43901968` | idem | se alcanzó el máximo de impressions de error |
| 11 | `[CAM_UTIL]: EvtDrvnTsk) Task tid:%d, func:%08x, arg:%x, %x` | `0x439019e2` | `0x4390199c` | registro de una tarea del **driver de eventos** |
| 12 | `[CAM_UTIL]: osal_try_valloc_msg 0x%02x error! %dtimes` | `0x43904034` | `0x4390400e` | contador de fallos al pedir un mensaje OSAL |
| 13 | `[CAM_UTIL]: osal_try_valloc_msg 0x%02x error! %dtimes [%08x]` | `0x43904092` | `0x4390400e` | ídem con el *handle* que falló |

## 3. Detalles de comportamiento verificados

### 3.1 Inicialización de la familia `CAM_UTIL` (`0x4390178e`)

```
0x4390179c: ldr    r1, [pc, #0x50]      ; puntero
0x439017a6: add    r1, pc
0x439017a8: strb   r0, [r1, r2]         ; limpiar
0x439017aa: adds   r2, #1
0x439017ac: cmp    r2, #0x11            ; 17 entradas
0x439017ae: bne    #0x439017a2
0x439017b4: add.w  r0, r2, #0x198       ; fin de la tabla
0x439017be: strh   r1, [r2, #0x12]
0x439017c0: strh   r1, [r2, #0x10]
0x439017c2: strd   r4, r5, [r2, #8]
0x439017c6: strd   r4, r5, [r2], #0x18 ; limpiar registros de 0x18 B
0x439017ca: cmp    r2, r0
0x439017cc: bne    #0x439017b8
0x439017d2: movs   r2, #0xb5            ; ID DE MODULO
0x439017da: str    r2, [r3]
0x439017dc: subs   r2, #0xb0            ; 0xb5 - 0xb0 = 5
0x439017de: str    r2, [r3, #4]
```

Limpia una tabla de **17 entradas** y **22 registros** de 0x18 B (`0x198 / 0x18`), y deja el
**id de módulo `0xb5`** y un contador **5**.

### 3.2 Contador de fallos de `osal_try_valloc_msg` (`0x4390400e`)

```
0x43904012: ldrb.w r3, [r6, #0xfc]      ; byte de estado
0x43904016: tst.w  r3, #1               ; bit 0 = "hay error"
0x4390401a: beq    #0x43904052
0x43904036: bl     #0x43903f5c          ; traza "…error! %dtimes"
0x43904042: bl     #0x43902718          ; traza "…error! %dtimes [%08x]"
0x4390404a: bic    r3, r3, #1           ; limpiar el bit
0x4390404e: strb.w r3, [r6, #0xfc]
```

Es un **reintento con contador**: si el bit 0 del byte de estado está activo, registra el error
(un par de trazas) y **limpia el bit**.

### 3.3 Registro de tareas del driver de eventos (`0x4390199c`)

Construye una cadena (formateo en `0x43b2a10a` / `0x43b2a116`) y compara el *task id* con dos
entradas de una tabla (`ldrb r1,[r2]`, `ldrb r2,[r2,#1]`); si no coincide, cae en la rama de
error que emite `[CAM_UTIL]: EvtDrvnTsk) Task tid:%d, func:%08x, arg:%x, %x`.

## 4. Diferencial

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[CAM_UTIL]` | **10** | **0** | **0** |
| token `[CAMERA_ADJ]` | **3** | **0** | **0** |
| cadenas totales con referencia | 13/13 | — | — |
| cadenas muertas | **0** | — | — |

Las etiquetas son **propias de la fw3.21 de la A6000** (otra vez el patrón S128/S130: se
reescribe el *logging*). Los **nombres** de lo que avisan («DmmMemPool», «AV DDS»,
«Utility MS», «EvtDrvnTsk») sí describen **utilidades preexistentes** del framework.

**Salvedad** (S130 §4): la comparación mezcla versión de firmware y modelo.

## 5. Interés para la línea del obturador

**Negativo verificado**: ninguna de las 13 cadenas menciona obturador, disparo, lectura del
sensor, exposición ni tiempos de exposición; hablan de **memoria** (DMM, OSAL), **mensajes**
(AV DDS, `osal_try_valloc_msg`) y **tareas** (EvtDrvnTsk) → **sin efecto en S51**.

## 6. NO VERIFICADO / abierto

1. Qué es exactamente «AV DDS» y «Utility MS» (siglas **sin desarrollar**: no hay expansión en
   los bytes).
2. La tabla de 17 entradas y los 22 registros de 0x18 B de `0x4390178e`: qué campos tienen y qué
   los escribe.
3. Los dos contadores (`0xb5` = id de módulo y `5`): su semántica.
4. El significado del byte de estado `+0xfc` y del bit 0.
5. Por qué la A6000 usa dos etiquetas distintas (`[CAM_UTIL]` y `[CAMERA_ADJ]`) para el mismo
   subsistema (¿herencia del código original?).

## 7. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s173_cam_util_labels.py -q
```

## 8. Revisión del agente principal

_(vacía)_
