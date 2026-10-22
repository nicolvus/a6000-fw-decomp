# S166 — el módulo `[ADC_DEBUG]` (14 trazas): la capa de depuración del ADC

> Hito de la **línea de ingeniería inversa general**. Solo lectura de bytes del
> `av-cam.bin` de la **A6000 fw3.21** (`analysis/rea-independent/input/av-cam.bin`),
> con comparación contra la **A7S fw3.20** y el **A6300 fw2.01**.
> Convención: `vaddr = 0x43541000 + file_offset`.
> Referencias a cadenas: **regla estricta** (canónica del repo), ver
> `analysis/s106_imaging_cap/pic_xref_methodology.md`.
>
> VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.
> Restricciones del proyecto: **sin firmware ejecutado, sin cámara, sin flasheo**.

## 1. Resumen / veredicto

**`[ADC_DEBUG]` no es un módulo autónomo: es la traza de depuración que la fw3.21 de la
A6000 añadió a los *handlers* de los comandos de fábrica (`ADJ`) del driver LIRO del ADC.**

Las 14 trazas las emiten **exactamente dos funciones**, y esas dos funciones son
**los handlers de los comandos ADJ `get_d` y `get_da`** del driver LIRO ADC (verificado
contra la tabla de registro ADJ en `0x440189bc`). No hay ningún otro emisor.

Cifras (todas VERIFICADAS, regla estricta):

| magnitud | valor |
|---|---|
| cadenas con el token `[ADC_DEBUG]` | **14** (14 textos distintos) |
| rango | `0x43ce50dd` – `0x43ce5273` (bloque contiguo, paso 0x20 B) |
| sitios de emisión (pares PIC) | **15** (`few arg` se emite en 2 sitios) |
| pares PIC verificados a mano | **15 / 15** (recodificados desde los bytes) |
| cadenas referenciadas | **14 / 14** (0 muertas) |
| funciones emisoras | **2** (`0x4398eb20` y `0x4398ec7c`) |
| comandos ADJ del driver ADC | 3 (`get_d`, `get_da`, `set_da`) + `exit` |

## 2. Qué es exactamente `[ADC_DEBUG]`

1. **Pertenece al driver LIRO del ADC** (`ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_*`,
   `TSK_ADC`, `boot_exit_adcliro`), un driver de bajo nivel con acceso directo al
   **registro de hardware del ADC** en `0xf2406000` (unidad 0) / `0xf2407000` (unidad 1).
   Su despachador de sub-comandos es `0x4398e578` (§4.4).

2. **El ADC tiene 2 unidades × 12 canales**, valores de 16 bits:
   * array en RAM `0x43f84b80`, índice `= unidad*12 + canal`
     (`mla r2,r5,r1,r2` con `r5=0xc` en `0x4398e6c0`, `strh.w r0,[r3,r2,lsl #1]` en `0x4398e6c6`);
   * registro de hardware por canal: `0xf2406014 + unidad*0x1000 + canal*4` (u16),
     leído por `0x4398ee14` (`ldrh r0,[r3,#4]` en `0x4398ee1e`);
   * rango del canal validado en `cmp r2,#0xb` (`0x4398e6b8`) y de la unidad en
     `cmp r1,#1` (`0x4398e6b2`) → **canales 0..11, unidades 0..1**.

3. **Los handlers `get_d` / `get_da` leen del ADC y las imprimen canal por canal**:
   * `get_d` → mensaje `0xfff0` (1 canal) → imprime `[ADC_DEBUG]: ADC DATA = %04x`;
   * `get_da` → mensaje `0xfff1` (12 canales) → imprime `[ADC_DEBUG]: ADC DATA0..DATA11`;
   * `set_da` → mensaje `0xfff2` (escribe 12 canales) → **no imprime nada**.
   Los tres mensajes se envían al **servicio LIRO_ADC**, invocado con el handle
   `0x720018` a través del helper genérico `0x43561228` (llamada a la ranura de
   vtable `+0x1d8` del singleton de servicio).

4. **Las trazas no son un "log de servicio"**: el propio código del driver tiene otras
   trazas (`sem=%x`, `reg_sync err=%d`, `Backup Read Error!`, `unreg_sync=%d`), pero
   **`[ADC_DEBUG]` es la capa de volcado de valores crudos** de los handlers ADJ.

## 3. Las 14 trazas

`addr` = dirección de la cadena; `sitio` = dirección del `add rX,pc` (regla estricta);
`func` = entrada real de la función (la tabla ADJ apunta al `cmp` previo al `push`).

| # | addr | texto | sitio | func | qué informa |
|---|---|---|---|---|---|
| 1 | `0x43ce50dd` | `[ADC_DEBUG]: few arg` | `0x4398eb32`, `0x4398ec8e` | `0x4398eb20`, `0x4398ec7c` | número de argumentos insuficiente (`cmp r0,#1` en `0x4398eb20`; `cmp r0,#2` en `0x4398ec7c`) |
| 2 | `0x43ce50f3` | `[ADC_DEBUG]: ADC DATA0  = %04x` | `0x4398eb6a` | `0x4398eb20` | valor del **canal 0** (`ldrh r3,[r4,#6]` en `0x4398eb5e`) |
| 3 | `0x43ce5113` | `[ADC_DEBUG]: ADC DATA1  = %04x` | `0x4398eb7c` | `0x4398eb20` | canal 1 (`ldrh r3,[r4,#8]` en `0x4398eb70`) |
| 4 | `0x43ce5133` | `[ADC_DEBUG]: ADC DATA2  = %04x` | `0x4398eb8e` | `0x4398eb20` | canal 2 (`ldrh r3,[r4,#0xa]` en `0x4398eb82`) |
| 5 | `0x43ce5153` | `[ADC_DEBUG]: ADC DATA3  = %04x` | `0x4398eba0` | `0x4398eb20` | canal 3 (`ldrh r3,[r4,#0xc]` en `0x4398eb94`) |
| 6 | `0x43ce5173` | `[ADC_DEBUG]: ADC DATA4  = %04x` | `0x4398ebb2` | `0x4398eb20` | canal 4 (`ldrh r3,[r4,#0xe]` en `0x4398eba6`) |
| 7 | `0x43ce5193` | `[ADC_DEBUG]: ADC DATA5  = %04x` | `0x4398ebc4` | `0x4398eb20` | canal 5 (`ldrh r3,[r4,#0x10]` en `0x4398ebb8`) |
| 8 | `0x43ce51b3` | `[ADC_DEBUG]: ADC DATA6  = %04x` | `0x4398ebd6` | `0x4398eb20` | canal 6 (`ldrh r3,[r4,#0x12]` en `0x4398ebca`) |
| 9 | `0x43ce51d3` | `[ADC_DEBUG]: ADC DATA7  = %04x` | `0x4398ebe8` | `0x4398eb20` | canal 7 (`ldrh r3,[r4,#0x14]` en `0x4398ebdc`) |
| 10 | `0x43ce51f3` | `[ADC_DEBUG]: ADC DATA8  = %04x` | `0x4398ebfa` | `0x4398eb20` | canal 8 (`ldrh r3,[r4,#0x16]` en `0x4398ebee`) |
| 11 | `0x43ce5213` | `[ADC_DEBUG]: ADC DATA9  = %04x` | `0x4398ec0c` | `0x4398eb20` | canal 9 (`ldrh r3,[r4,#0x18]` en `0x4398ec00`) |
| 12 | `0x43ce5233` | `[ADC_DEBUG]: ADC DATA10 = %04x` | `0x4398ec1e` | `0x4398eb20` | canal 10 (`ldrh r3,[r4,#0x1a]` en `0x4398ec12`) |
| 13 | `0x43ce5253` | `[ADC_DEBUG]: ADC DATA11 = %04x` | `0x4398ec30` | `0x4398eb20` | canal 11 (`ldrh r3,[r4,#0x1c]` en `0x4398ec24`) |
| 14 | `0x43ce5273` | `[ADC_DEBUG]: ADC DATA = %04x` | `0x4398ecce` | `0x4398ec7c` | valor del **canal pedido** (`ldrh r3,[r5,#6]` en `0x4398ecc2`) |

> Los 14 textos terminan en `\n` (byte 0x0a); en la tabla se omite.

### Verificación manual de los pares PIC (regla metodológica §2)
Los **15** pares `ldr rX,[pc,#imm]` + `add rX,pc` se **recodificaron desde los bytes**
(`analysis/s166_adc_debug/scan_adc_debug.py`, función `decode_pic`) y se comprobó que
el destino calculado coincide con la cadena: **15/15 correctos**. Ejemplos:

| ldr | pool | W | add | destino | texto |
|---|---|---|---|---|---|
| `0x4398eb68` | `0x4398ec4c` | `0x356585` | `0x4398eb6a` | `0x43ce50f3` | `ADC DATA0  = %04x` |
| `0x4398ebf8` | `0x4398ec6c` | `0x3565f5` | `0x4398ebfa` | `0x43ce51f3` | `ADC DATA8  = %04x` |
| `0x4398ec2e` | `0x4398ec78` | `0x35661f` | `0x4398ec30` | `0x43ce5253` | `ADC DATA11 = %04x` |
| `0x4398eb2a` | `0x4398ec48` | `0x3565a7` | `0x4398eb32` | `0x43ce50dd` | `few arg` |
| `0x4398ec86` | `0x4398ece8` | `0x35644b` | `0x4398ec8e` | `0x43ce50dd` | `few arg` |
| `0x4398eccc` | `0x4398ecec` | `0x3565a1` | `0x4398ecce` | `0x43ce5273` | `ADC DATA = %04x` |

## 4. Mapa función → traza (2 funciones) y su registro ADJ

El registro de comandos ADJ del driver LIRO ADC está en **`0x440189bc`**:

```
+0x00  u32 0x440187e4   (apunta a una zona toda a cero)
+0x04  u32 0x43fa46e3   (apunta a BSS, sin contenido en el blob)
+0x08  u32 0x00000003   (nº de comandos del grupo)
+0x0c  u32 0x000000ff   (máscara del índice de comando)
+0x10  entradas de 12 B: {u32 nombre, u32 ayuda, u32 handler(Thumb)}
```

| comando | nombre | ayuda | handler |
|---|---|---|---|
| `get_d` | `0x43ce5299` | `ADC_GET_DATA     unit_no ch_no` (`0x43ce529f`) | **`0x4398ec7c`** |
| `get_da` | `0x43ce52be` | `ADC_GET_DATA_ALL unit_no` (`0x43ce52c5`) | **`0x4398eb20`** |
| `set_da` | `0x43ce52de` | `ADC_SET_DATA_ALL unit_no data0 data1 ... data11` (`0x43ce52e5`) | `0x4398e9dc` |
| `exit` | `0x43c39847` | `boot_exit_adcliro` (`0x43ce5315`) | `0x43b5e0b0` |

### 4.1 `0x4398eb20` — handler de `get_da` (13 sitios)

* entrada `0x4398eb20` (`cmp r0,#1`), prólogo `push {r4,r5,lr}` en `0x4398eb22`;
* `cmp r0,#1` / `bgt 0x4398eb3a` (`0x4398eb28`): con menos de 2 argumentos →
  `[ADC_DEBUG]: few arg` (`0x4398eb32`) y retorno;
* con argumentos: `osal_try_valloc_msg` (`0x435612d0`, 0x20 B) → mensaje con
  `msg[0]=0xfff1` (`movw r3,#0xfff1` en `0x4398eb48`), `msg[4]=unidad`
  (`ldr r0,[r5,#4]` en `0x4398eb4c`);
* llamada al servicio ADC (`bl 0x43561228` en `0x4398eb5a`, handle `0x720018`);
* volcado de las 12 medias palabras de la respuesta (`msg[+6] … msg[+0x1d]`);
* `osal_free_msg` (`0x435612ec`) en `0x4398ec3a`.

### 4.2 `0x4398ec7c` — handler de `get_d` (2 sitios)

* entrada `0x4398ec7c` (`cmp r0,#2`), prólogo `push {r4,r5,lr}` en `0x4398ec7e`;
* `cmp r0,#2` (`0x4398ec7c`) / `bgt` (`0x4398ec84`): con menos de 3 argumentos → `few arg` (`0x4398ec8e`);
* mensaje de 8 B con `msg[0]=0xfff0` (`0x4398eca4`), `msg[4]=unidad`
  (`ldr r0,[r4,#4]` en `0x4398eca8`), `msg[5]=canal` (`ldr r0,[r4,#8]` en `0x4398ecb2`);
* llamada al servicio ADC (`bl 0x43561228` en `0x4398ecbe`);
* imprime el valor (`ldrh r3,[r5,#6]` en `0x4398ecc2`) → `[ADC_DEBUG]: ADC DATA = %04x`.

### 4.3 Envoltorios de traza

* Las trazas `[ADC_DEBUG]` usan el envoltorio `0x4398ea78` con `r0=0xbe` (categoría,
  p. ej. `movs r0,#0xbe` en `0x4398eb60`), `r1=0` (`movs r1,#0` en `0x4398eb62`) y `r2=1`.
* Las **otras** trazas del propio driver usan otro envoltorio, `0x4398e4cc`, llamado con
  `r1=0xadc` (`movw r1,#0xadc`, p. ej. `0x4398e5a8`).
* Ambos envoltorios escriben `r1` en `msg[4]` (`str.w r8,[r4,#4]` en `0x4398eac2` y en
  `0x4398e506`): el campo vale `0` en las trazas `[ADC_DEBUG]` y `0xadc` en las del
  driver. **INFERENCIA**: ese campo es un identificador de origen/módulo y el driver se
  identifica a sí mismo con `0xadc`; no hay ningún texto que lo confirme.

### 4.4 El despachador de comandos del driver (`0x4398e578`)

El driver **no** sólo expone el servicio: tiene además un despachador de **sub-comandos**
propios, con nombres de comando embebidos:

* el comando debe ser `0x901` (`movw r3,#0x901` + `cmp r2,r3` en `0x4398e594`/`0x4398e59c`);
* el sub-comando está en el byte `[r4+0x1a]` (`ldrb r3,[r4,#0x1a]` en `0x4398e5c2`), y se
  reparte con un `tbb` de 5 entradas (tabla en `0x4398e5d0`: `03 19 36 55 67`):

| sub-comando | `tbb` → | etiqueta embebida | qué hace |
|---|---|---|---|
| 1 | `0x4398e5da` | `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA` (`0x43ce4fc7`) | lee **1** canal (`cmp r2,#4` en `0x4398e5c6`, tabla de gain) |
| 2 | `0x4398e606` | `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_GET_DATA_ALL` (`0x43ce4ff2`) | lee los **12** canales y los copia a la respuesta |
| 3 | `0x4398e640` | `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_CHECK_DATA` (`0x43ce5021`) | comprueba el valor contra dos umbrales (`cmp r3,r5` / `cmp r3,r6` en `0x4398e66a`/`0x4398e670`); error `0x88` |
| 4 | `0x4398e67e` | `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_TEST_MODE` (`0x43ce504e`) | activa/desactiva el modo de test según `[r4+0x1c]` |
| 5 | `0x4398e6a2` | `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_SET_DATA` (`0x43ce507a`) | **escribe** un canal: `cmp r1,#1` (unidad) y `cmp r2,#0xb` (canal) en `0x4398e6b2`/`0x4398e6b8`, y `strh.w r0,[r3,r2,lsl #1]` en `0x4398e6c6` sobre el array `0x43f84b80` |

> El primer nombre de comando está precedido en el binario por los 2 bytes `@0`
> (`0x43ce4fc5`); el código apunta a `0x43ce4fc7`, es decir, al texto sin ese prefijo.

## 5. Canales ADC: qué se lee y qué significan

| elemento | dirección | contenido | estado |
|---|---|---|---|
| array de valores | `0x43f84b80` | 24 × u16 = **2 unidades × 12 canales** | VERIFICADO |
| registro HW por canal | `0xf2406014` (+`0x1000` por unidad) + `canal*4` | u16, leído por `0x4398ee14` | VERIFICADO |
| bloque HW del ADC | `0xf2406000` (u0) / `0xf2407000` (u1) | `+0x08` = selector de canal (`bfi r0,r1,#0,#2` en `0x4398ed10`), `+0x04` y `+0x48` = registros de configuración (inmediatos `0xd4`, `0xa2`, `0x7c`, `0x54` en `0x4398ed26`, `0x4398ed52`, `0x4398ed7a`, `0x4398eda6`; qué significan: NO_VERIFICADO) | VERIFICADO |
| handle del servicio | `0x720018` | `LIRO_ADC` | VERIFICADO |
| área de backup/NVRAM | `0x720000` | usada por `ADC::Initialize` (`mov.w r0,#0x720000` en `0x4378cfdc`) | VERIFICADO |
| nombre de tarea | `TSK_ADC` `0x43ce5291` | tarea del driver (`b.w 0x435ab6f0` en `0x4398ecf8`) | VERIFICADO |
| ids de mensaje | `0xfff0` / `0xfff1` / `0xfff2` | 1 canal / 12 canales / escribir 12 canales | VERIFICADO |

**Asignación canal → sensor: NO_VERIFICADO.** El número de unidad y de canal lo lee el
cliente de **parámetros de configuración en runtime** (`bl 0x43561508` con ids
`0xf9034d`, `0xf90413`, `0xf90414`, p. ej. `0x43636c9c`–`0x43636cb2`), por lo que **no
hay tabla de canales embebida**. El **único nombre simbólico de canal** que aparece en
todo el firmware es `CNF_ADC_CH_EVF_TEMP`, dentro de la traza
`Get ADC CNF_ADC_CH_EVF_TEMP Val:0x%x(%d)` (`0x43c7751a`, sitio `0x43636ce6`), emitida
por el cliente de panel/EVF (`0x43636c68`). **No se desarrolla la sigla**: no hay
expansión de `CNF` ni de `EVF_TEMP` en ningún byte.

## 6. Quién usa el servicio LIRO_ADC (11 clientes)

De los **282** puntos de llamada al helper genérico `0x43561228` en toda la imagen,
**11** usan el handle `0x720018`:

| sitio | función | contexto verificado |
|---|---|---|
| `0x43562a44` | `0x43562a08` | `[ACCY][INFO][HW]:AD=%d, ID=%d` (`0x43c24cac`) — módulo de accesorios |
| `0x435ad4a6` | `0x435ad474` | `[ILLUMI]AD MAXOVER. ADwork=0x%x, line=%d` (`0x43c40945`), `[ILLUMI]C_AD. ADcor=0x%x, line=%d` (`0x43c4096e`) — módulo de iluminación |
| `0x43636cc0` | `0x43636c68` | `Get ADC CNF_ADC_CH_EVF_TEMP Val:0x%x(%d)` — **temperatura del EVF** |
| `0x436f9f6e` | `0x436f9f44` | lectura de 1 canal (sin traza propia) |
| `0x4385eb80` | `0x4385eb2c` | lectura de **3 canales** en bucle (`cmp r5,#3` en `0x4385ebbc`), sin traza propia |
| `0x438d14e8`, `0x438d1514` | `0x438d14b0` | `[CAMERA_MAIN]: osal_alloc_msg(liro_adc) error:%d` (`0x43ccabd8`), `osal_send_sync_msg(liro_adc)` (`0x43ccac0a`), `osal_free_msg(liro_adc)` (`0x43ccac40`) |
| `0x438d2204` | `0x438d21d4` | cliente sin traza propia |
| `0x4398ea60` | `0x4398e9dc` | ADJ `set_da` |
| `0x4398eb5a` | `0x4398eb20` | ADJ `get_da` → **`[ADC_DEBUG]` DATA0..DATA11** |
| `0x4398ecbe` | `0x4398ec7c` | ADJ `get_d` → **`[ADC_DEBUG]` ADC DATA** |

Además, la capa `[CAMERA_MAIN_SYNC]` usa el ADC por otra vía (la **tarea** `TSK_ADC`):
`ADC::Initialize` (`0x4378cfa8`, llamada desde `0x43788186`), `SendToADCTask`
(`0x4378d3b4`, llamada desde `0x43790866` dentro de `HS_Main` `0x4378fef4`) e
`int_ADC_Handler` (`0x4378d444`).

## 7. Relación con `[CAMERA_IS]` (S164) — **NO es el mismo servicio**

**Conclusión: el ADC del giroscopio de `[CAMERA_IS]` NO pasa por el servicio LIRO ADC.**
Son dos mecanismos distintos que comparten la palabra "ADC".

Verificaciones:

1. **La región del estabilizador no llama al servicio LIRO_ADC.** Se recorrieron todos los
   `bl 0x43561228` de las dos regiones de código del módulo IS
   (`0x436e8000`–`0x43708000` y `0x4371d000`–`0x43721000`): **0 y 1** llamadas
   respectivamente, y **ninguna** con el handle `0x720018`
   (`analysis/s166_adc_debug/servicecalls.py`).
2. **El "acceso ADC" del giroscopio es una lectura de constantes + calibración.**
   `0x4370665c` (el lector de `GyroAD[p]`,`GyroAD[y]`) llama a `0x436eace0`, que lee
   una **tabla de constantes en .rodata** en `0x43bdc0a6`
   (`ldrh.w r0,[r3,r2,lsl#1]` en `0x436eacf0`, con `r3 = 0x43bdc0a6`; valores
   `0x0032`, `0x0030`, …) y devuelve `0x3c` (60) si el índice está fuera de rango
   (`0x436eacf6`). Encima, `0x4370665c` aplica las tablas de calibración
   `0x43be6336` / `0x43be6518` (`ldrh.w r3,[r3,r6,lsl#1]` en `0x43706720`).
   No hay ninguna llamada al servicio `0x720018` ni al driver LIRO ADC.
3. Los **únicos** puntos en que el IS y el ADC LIRO se tocan son **negativos**: el
   giroscopio del IS **no** consume ninguno de los 12 canales del ADC LIRO.

**Conclusión operativa:** `[ADC_DEBUG]` documenta el ADC **de la placa** (12 canales,
2 unidades, HW `0xf2406000`), que alimenta al ACCY, a la iluminación, a la temperatura
del EVF y a la sincronización de la secuencia HS; **no** documenta el giroscopio.

## 8. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[ADC_DEBUG]` | **14** | **0** | **0** |
| textos `[ADC_DEBUG]` presentes | 14/14 | **0/14** | **0/14** |
| `ADJ_CMD_LIRO_DRIVERS_ADC_*` (apariciones; 5 etiquetas distintas) | **6** | **0** | **0** |
| `get_d` / `get_da` / `set_da` | sí | sí | sí |
| `ADC_GET_DATA     unit_no ch_no` | 1 | 1 | 1 |
| `ADC_GET_DATA_ALL unit_no` | 1 | 1 | 1 |
| `ADC_SET_DATA_ALL unit_no data0 data1 ... data11` | 1 | 1 | 1 |
| `TSK_ADC`, `boot_exit_adcliro` | 1 / 1 | 1 / 1 | 1 / 1 |
| handler `get_da` | `0x4398eb20` | `0x4397c860` | `0x43a23480` |
| handler `get_d` | `0x4398ec7c` | `0x4397c89c` | `0x43a234bc` (tabla en `0x441e9764`) |
| **handlers con impresión `[ADC_DEBUG]`** | **sí** | **no** | **no** |
| trazas internas del driver (`sem=%x`, `reg_sync err=%d`, `unreg_sync=%d`, `Backup Read Error!`) | 1/1/1/1 | **0/0/0/0** | **0/0/0/0** |
| `liro_adc` | 3 | 3 | 3 |
| `CNF_ADC_CH_EVF_TEMP` | 1 | 1 | 1 |
| `int_ADC_Handler` / `ADC::Initialize` / `SendToADCTask` | 3 / 1 / 1 | 3 / 1 / 1 | 3 / 1 / 1 |
| `jitter NG` / `ADC flg timeout` / `ADCkeyInfo` | 3 / 2 / 1 | 3 / 2 / 1 | 3 / 2 / 1 |
| `0xf2406000` (base HW del ADC) | 5 | 5 | 5 |

**Lectura del diferencial (VERIFICADO):**

1. El **driver LIRO ADC y sus comandos ADJ existen en los tres firmwares** con el mismo
   layout (2 unidades × 12 canales, ids de mensaje `0xfff0`/`0xfff1`/`0xfff2`, mismo
   registro de comandos). Los handlers de la A7S (`0x4397c860`, `0x4397c89c`) y del
   A6300 (`0x43a23480`) son **estructuralmente idénticos** a los de la A6000
   (mismo `cmp r0,#1`, mismo `movw r3,#0xfff1`, mismo `osal_try_valloc_msg` de 0x20 B,
   misma llamada de servicio) **pero no imprimen nada**: les falta el volcado
   `DATA0..DATA11`.
2. Lo **propio de la A6000 fw3.21** es (a) la **capa de traza `[ADC_DEBUG]`** (14
   mensajes) y (b) las **etiquetas de comando del driver**
   `ADJ_CMD_LIRO_DRIVERS_ADC_LIRO_ADC_{GET_DATA, GET_DATA_ALL, CHECK_DATA, TEST_MODE,
   SET_DATA}` (5 etiquetas distintas, 6 apariciones porque `GET_DATA` es subcadena de
   `GET_DATA_ALL`), que no existen en los otros dos firmwares. Es el mismo patrón de
   "se reescribe el logging" descrito en S128.
3. La fw3.21 de la A6000 **añade también trazas internas al driver ADC**
   (`sem=%x`, `reg_sync err=%d`, `unreg_sync=%d`, `Backup Read Error!`), ausentes en
   A7S y A6300.
4. **Salvedad metodológica (S130 §4):** la comparación mezcla **versión de firmware y
   modelo de cámara**; con los tres blobs disponibles no se puede separar «nuevo en la
   fw3.21» de «propio del A6000».

## 9. Interés para la línea del obturador

**Negativo verificado sobre `[ADC_DEBUG]`:**

* Las 14 trazas contienen **0 apariciones** de `shut`, `silent`, `electro`, `mech`,
  `rolling`, `readout`, `exposure`, `sensor`, `gyro`, `jitter`, `temp`, `volt`.
* `[ADC_DEBUG]` **no menciona** obturador, lectura del sensor, *rolling shutter* ni
  tiempo de exposición → **sin efecto directo en S51 (A/B/C = NO)**.

**Lo que sí aporta el ADC a la línea del obturador (todo VERIFICADO, y fuera de
`[ADC_DEBUG]`):**

1. **Sincronización temporal de la secuencia de alta velocidad (HS).**
   `HS_Main` (`0x4378fef4`, capa `[CAMERA_MAIN_SYNC]`) llama a `SendToADCTask`
   (`bl 0x4378d3b4` en `0x43790866`) y espera la bandera del ADC:
   `HS_Main:(TC::Last1st) ADC flg timeout %dV #%d, %04x` (`0x43ca30fd`, sitio
   `0x437904ee`) y su gemelo `…(TC::Last2nd)…` (`0x43ca31c1`, sitio `0x4379069a`).
   El ADC participa, por tanto, en la **sincronización temporal de la secuencia de
   disparo HS**, que es donde el obturador mecánico impone su tiempo de lectura.
2. **Medida de jitter.** `int_ADC_Handler` (`0x4378d444`) mide la diferencia de ticks
   (`bl 0x43ad5fba` en `0x4378d4a4`; `rsb r8,r1,r0` en `0x4378d4ae`) y avisa cuando
   supera el umbral `cmp.w r8,#0x320` (`0x4378d4b4`):
   `int_ADC_Handler #%d jitter NG %d->%d, jitter:%dusec` (`0x43ca241e`, sitio
   `0x4378d4d6`). Es una medida de **jitter temporal**, no de mecanismo.
3. **Error de factor ADC**: `int_ADC_Handler #%d ADC error fact:%d` (`0x43ca23e4`) y
   `int_ADC_Handler #%d stop state:%d` (`0x43ca23ae`).

**Lo que NO se ha encontrado (y no se afirma):**

* **Ningún canal del ADC LIRO está ligado a la decisión mecánico/electrónico del
  obturador.** No hay ninguna traza, parámetro ni tabla de la fw3.21 que nombre un
  canal de ADC en relación con el obturador; el único canal con nombre simbólico es
  `CNF_ADC_CH_EVF_TEMP` (temperatura del visor EVF).
* El ADC **no** entra en la ruta del obturador electrónico: el A6300 fw2.01, que **sí**
  implementa `ElecShutter/` (S135), tiene el **mismo** ADC LIRO (`get_d`/`get_da`/
  `set_da`, `TSK_ADC`, `CNF_ADC_CH_EVF_TEMP`, `int_ADC_Handler`, `jitter NG`) y **no**
  añade ningún canal ni traza de obturador electrónico. Es un argumento **a favor** de
  que el ADC no es el portador de esa decisión.

## 10. NO VERIFICADO / abierto

1. **Fichero fuente y clase RTTI del driver LIRO ADC: no hay ninguno embebido.**
   De las **30** cadenas referenciadas desde la región de código del driver
   (`0x4398e000`–`0x4398f200`, listadas en `adc_debug.json` → `ficheros_fuente`),
   **ninguna** es un nombre de fichero `.cpp`/`.c`/`.h` ni un nombre de clase RTTI.
   Los nombres embebidos más cercanos son de otros módulos
   (`src/RcDriver.cpp` `0x43ce1b1d`, `src/api_rc.cpp` `0x43ce15d1`, `Stage_Adjust.cpp`
   `0x43cc6cc6` — esta última es la etapa ADJ **de la cámara**, en `0x438bd79c`…, no
   el driver LIRO). **No se puede atribuir un fichero fuente al módulo.**
2. **Qué sensor físico hay detrás de cada uno de los 12 canales** (y de las 2
   unidades): NO_VERIFICADO. La numeración llega en runtime desde parámetros de
   configuración; no hay tabla embebida.
3. **Alcance de `EVF_TEMP`**: se sabe que el cliente de panel/EVF lee un canal
   parametrizado y lo etiqueta `CNF_ADC_CH_EVF_TEMP`, pero **no** se ha verificado que
   ese canal concreto sea el que devuelve ese cliente (el índice viene de un parámetro).
4. **Cómo se registra `int_ADC_Handler`** (`0x4378d444`): **0** llamadas `bl` directas
   y **0** punteros absolutos de 32 bits a su dirección → se invoca por un mecanismo
   indirecto no identificado (probablemente tabla de offsets, como la tabla ADJ).
5. **Significado del campo `0x43fa46e3`** del descriptor ADJ (apunta a BSS vacío en el
   blob) y de `0x440187e4` (lista de comandos común, también vacía).
6. **Alcance en runtime de los comandos ADJ**: son comandos de **ajuste de fábrica**
   (`get_d`, `get_da`, `set_da`, `boot_exit_adcliro`); no se ha ejecutado el firmware
   (restricción del proyecto), por lo que **no** se afirma que se puedan ejecutar en una
   cámara de usuario.
7. **Los 12 valores impresos** por `get_da` son **crudos** (u16 tal cual); no se ha
   verificado que no lleven un offset/escala aplicado antes de imprimirse.
8. No se ha seguido el recorrido físico `0xf2406000` → sensor; sólo se ha verificado el
   acceso por registros y el contenido de la capa de software.

## 11. Revisión del agente principal

_(vacía)_

## 12. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python analysis/s166_adc_debug/make_prologues.py     # cache de prólogos Thumb
.venv/bin/python analysis/s166_adc_debug/scan_adc_debug.py      # -> adc_debug.json
.venv/bin/python -m pytest tests/test_s166_adc_debug.py -q
```

Ayudas:

* `analysis/s166_adc_debug/disasm2.py 0x4398eb20 40` — desensamblado anotado con
  literales resueltos.
* `analysis/s166_adc_debug/scan_context.py 0x4398e000 0x4398f900` — cadenas
  referenciadas desde una región.
* `analysis/s166_adc_debug/service_handles.py 0x43561228` — agrupa las 282 llamadas al
  servicio genérico por handle (11 con `0x720018`).
* `analysis/s166_adc_debug/servicecalls.py 0x436e8000 0x43708000` — llamadas al
  servicio dentro de una región (para el negativo de §7).
* `analysis/s166_adc_debug/rd.py u32 0x440189bc 12` — lectura de la tabla ADJ.

---

## Revisión del agente principal (22-10-2026)

**Verificado y aceptado (tests del hito + comprobaciones a mano):**

1. **Recuento y rango**: 14 cadenas `[ADC_DEBUG]` en la A6000 fw3.21 entre `0x43ce50dd` y
   `0x43ce5273` (bloque contiguo, paso 0x20 B); **0** en la A7S fw3.20 y el A6300 fw2.01 →
   comprobado con `bytes.count()`.
2. **Estructura**: 14/14 referenciadas, **15 sitios** (regla estricta; `few arg` se emite en 2
   sitios) en **2 funciones** (`0x4398eb20` = handler ADJ `get_da`, `0x4398ec7c` = handler ADJ
   `get_d`); los **15 pares PIC verificados a mano 15/15**.
3. **El driver ADC ya existía en los tres firmware** (verificado): `TSK_ADC` **1/1/1**,
   `get_d` **1/1/1**, `get_da` **1/1/1**, `set_da` **2/2/2**, `CNF_ADC_CH_EVF_TEMP` **1/1/1**,
   `ADC_GET_DATA     unit_no ch_no` / `ADC_GET_DATA_ALL unit_no` /
   `ADC_SET_DATA_ALL unit_no data0 … data11` **1/1/1**, `0xf2406000` (base HW) **5/5/5**; los
   handlers equivalentes están en `0x4397c860`/`0x4397c89c` (A7S) y `0x43a23480`/`0x43a234bc`
   (A6300) y son **estructuralmente idénticos pero sin imprimir nada** → lo propio de la fw3.21
   es la **capa de volcado** y las **etiquetas de comando**
   (`ADJ_CMD_LIRO_DRIVERS_ADC_*` **5/0/0**, más `sem=%x`, `reg_sync err=%d`,
   `Backup Read Error!` **1/0/0** cada una).
4. **Corrección de una lectura posible de S164 (importante)**: el «acceso ADC» del giroscopio
   de `[CAMERA_IS]` **NO** es el servicio LIRO ADC — la región del estabilizador hace **0** y
   **1** llamadas al helper genérico `0x43561228` y **ninguna** con el handle `0x720018`; el
   lector de `GyroAD` lee una **tabla de constantes** en `0x43bdc0a6`. Son dos mecanismos
   distintos que comparten la palabra "ADC" → la hipótesis de S164 de que el giroscopio usa el
   servicio LIRO ADC **queda descartada**.
5. **Aportación a la línea del obturador (verificada)**: el ADC participa en la
   **sincronización temporal de la secuencia HS** (`HS_Main` `0x4378fef4` → `SendToADCTask`
   `0x4378d3b4`, espera de bandera con `ADC flg timeout` `0x43ca30fd`) y en la **medida de
   jitter** (`jitter NG %d->%d, jitter:%dusec` `0x43ca241e`, umbral `cmp.w r8,#0x320`), pero
   **ningún canal está ligado a la decisión mecánico/electrónico**: el único canal con nombre
   simbólico es `CNF_ADC_CH_EVF_TEMP` (temperatura del EVF), y el **A6300 fw2.01, que sí
   implementa `ElecShutter/` (S135), tiene el MISMO ADC LIRO y no añade ningún canal ni traza de
   obturador electrónico** → argumento **a favor** de que el ADC **no** es el portador de esa
   decisión → **S51 sigue A/B/C = NO**.
