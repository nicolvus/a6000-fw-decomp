# S129 — `[CAMERA_MAIN_IM]`: la monitorización térmica del imager (42 trazas)

> Hito de la **línea de ingeniería inversa general**. Verificación contra los bytes del
> `analysis/rea-independent/input/av-cam.bin` (A6000 fw3.21); convención **vaddr =
> 0x43541000 + file_offset**. Regla de referencias: la **estricta** (canónica, ver
> [`pic_xref_methodology.md`](../s106_imaging_cap/pic_xref_methodology.md)). Sin efecto en S51.

## 1. Qué es

`[CAMERA_MAIN_IM]` es el submódulo **térmico** de la cámara. No desarrolla la sigla `IM` en
ningún texto: el contenido la identifica como la **monitorización de la temperatura del imager**
(`ImCheckThermal`, `StartImThermal`/`EndImThermal`, `ImStartMovThermal`/`ImEndMovThermal`,
`TimeA ImgTmp`, `THERMAL_CAUTION`/`THERMAL_SHUTDOWN`) más dos trazas ajenas de los drivers
**ZIT** (`ZitZ1cDriver`, `ZitDdcDriver`) que comparten la etiqueta.

- **42 cadenas** con el prefijo literal `[CAMERA_MAIN_IM]:`.
- **43 sitios** de referencia PIC (regla estricta): 42 cadenas, una de ellas
  (`0x43ca70f6`, `ImStartMovThermal set_timer:%x`) referenciada **dos veces**
  (`0x437b90fe` y `0x437b9268`).
- **10 funciones** las emiten; **0 cadenas sin referencia**.
- **40 cadenas contiguas** en `0x43ca6b32`–`0x43ca71e7`; **2 sueltas** en `0x43cb5fc1` y
  `0x43cb5ffa` (las de `ZitDdcDriver`).

El reparto temático de las 40 del bloque: temperatura y tablas por modo (12), umbrales
Abs/Env y avisos (11), arranque/parada del chequeo (10), diferencial de `movie` y `EcGain`
(4), y las 2 de `ZIT` fuera del bloque (más `ZitZ1cDriver` dentro).

## 2. Inventario (42 cadenas, 43 sitios)

| # | vaddr | texto (interior) | sitio(s) | función(es) |
|---|---|---|---|---|
| 1 | `0x43ca6b32` | `movie thermal diffTemp < 0 :(%d)` | `0x43547394` | `0x43547362` |
| 2 | `0x43ca6b65` | `paramA%f paramB%f diff:%d` | `0x43547426` | `0x43547362` |
| 3 | `0x43ca6b91` | `envOld:%d env':%d boot:%d` | `0x4354746c` | `0x43547362` |
| 4 | `0x43ca6bbd` | `environmentalTemp:%d` | `0x437b87e0` | `0x437b8774` |
| 5 | `0x43ca6be4` | `movie Table` | `0x437b881c` | `0x437b8774` |
| 6 | `0x43ca6c02` | `bulb Table` | `0x437b8844` | `0x437b8774` |
| 7 | `0x43ca6c1f` | `still Table` | `0x437b8864` | `0x437b8774` |
| 8 | `0x43ca6c3d` | `ISOAuto TH` | `0x437b88de` | `0x437b8774` |
| 9 | `0x43ca6c5a` | `ISO1 TH` | `0x437b890a` | `0x437b8774` |
| 10 | `0x43ca6c74` | `ISO2 TH` | `0x437b8930` | `0x437b8774` |
| 11 | `0x43ca6c8e` | `ISO3 TH` | `0x437b8950` | `0x437b8774` |
| 12 | `0x43ca6ca8` | `Abs:Tnow=%d shutdownTh=%d cautionTh=%d` | `0x437b8982` | `0x437b8774` |
| 13 | `0x43ca6ce1` | `Abs:THERMAL_SHUTDOWN: %d > %d` | `0x437b89b2` | `0x437b8774` |
| 14 | `0x43ca6d11` | `Abs:THERMAL_CAUTION:%d > %d` | `0x437b89ea` | `0x437b8774` |
| 15 | `0x43ca6d3f` | `Env:Tnow=%d Tenv=%d envTh=%d shutdownTh=%d cautionTh=%d` | `0x437b8b14` | `0x437b8774` |
| 16 | `0x43ca6d89` | `Env:THERMAL_SHUTDOWN:(%d - %d) > %d` | `0x437b8b74` | `0x437b8774` |
| 17 | `0x43ca6dbf` | `Env:THERMAL_CAUTION:(%d - %d) > %d` | `0x437b8bc6` | `0x437b8774` |
| 18 | `0x43ca6df4` | `send THERMAL_CAUTION on` | `0x437b8c34` | `0x437b8774` |
| 19 | `0x43ca6e1e` | `sendCaution(true) return %d` | `0x437b8c5c` | `0x437b8774` |
| 20 | `0x43ca6e4c` | `send THERMAL_CAUTION off` | `0x437b8c7a` | `0x437b8774` |
| 21 | `0x43ca6e77` | `sendCaution(false) return %d` | `0x437b8ca0` | `0x437b8774` |
| 22 | `0x43ca6ea6` | `send THERMAL_SHUTDOWN` | `0x437b8cc8` | `0x437b8774` |
| 23 | `0x43ca6ece` | `upm_set_off_factor() return %d` | `0x437b8d1c` | `0x437b8774` |
| 24 | `0x43ca6eff` | `Error : GetImagerTemperature` | `0x437b8d38` | `0x437b8774` |
| 25 | `0x43ca6f2e` | `ImCheckThermal setTimer:%x` | `0x437b8d68` | `0x437b8774` |
| 26 | `0x43ca6f5b` | `EcGain:%x isoAuto:%x bulb:%x` | `0x437b8e8c` | `0x437b8e1c` |
| 27 | `0x43ca6f8a` | `startImagerThermalCheck` | `0x437b8ef4` | `0x437b8ed4` |
| 28 | `0x43ca6fb4` | `StartImThermal allocTimer:%x` | `0x437b8f2a` | `0x437b8ed4` |
| 29 | `0x43ca6fe3` | `StartImThermal setTimer:%x` | `0x437b8f5c` | `0x437b8ed4` |
| 30 | `0x43ca7010` | `EndImThermal freeTimer:%x` | `0x437b8fd6` | `0x437b8fb0` |
| 31 | `0x43ca703c` | `endImagerThermalCheck sendCaution(false) return %d` | `0x437b9002` | `0x437b8fb0` |
| 32 | `0x43ca7081` | `endImagerThermalCheck` | `0x437b9022` | `0x437b8fb0` |
| 33 | `0x43ca70a9` | `RecStart` | `0x437b908e` | `0x437b9064` |
| 34 | `0x43ca70c4` | `ImStartMovThermal allocTimer:%x` | `0x437b90ca` | `0x437b9064` |
| 35 | `0x43ca70f6` | `ImStartMovThermal set_timer:%x` | `0x437b90fe, 0x437b9268` | `0x437b9064 / 0x437b91e8` |
| 36 | `0x43ca7127` | `RecEnd` | `0x437b9184` | `0x437b915c` |
| 37 | `0x43ca7140` | `ImEndMovThermal freeTimer:%x` | `0x437b91a8` | `0x437b915c` |
| 38 | `0x43ca716f` | `TimeA ImgTmp:%d` | `0x437b9220` | `0x437b91e8` |
| 39 | `0x43ca7191` | `Err:Timer2Callback` | `0x437b92a0` | `0x437b91e8` |
| 40 | `0x43ca71b6` | `ZitZ1cDriver ch:%d is not exist.` | `0x437b942e` | `0x437b93c0` |
| 41 | `0x43cb5fc1` | `ZitDdcDriver: Invalid format. [%d][%d]` | `0x4386bc12` | `0x4386bbec` |
| 42 | `0x43cb5ffa` | `ZitDdcDriver: Invalid numPt. [%d][%d]` | `0x4386bc30` | `0x4386bbec` |

## 3. Las 10 funciones emisoras

| entrada | sitios | papel | evidencia (bytes) |
|---|---|---|---|
| `0x43547362` | 3 | diferencial térmico de `movie`: resta dos `int16` globales y calcula `paramA`/`paramB`/`diff` | `0x4354736e ldrsh`, `0x4354737a ldrsh`, `0x43547380 subs r4,r4,r2`; `0x435473b0`–`0x435473f6` (`vcvt.f64.s32`, `vdiv.f64`, `vmls.f32`, `+0.5`, `vcvt.s32`) |
| `0x437b8774` | 22 | **chequeo térmico periódico**: temperatura del imager, tablas `movie`/`bulb`/`still`, umbrales Abs/Env, avisos y shutdown | `0x437b877a bl 0x436d6118`, `0x437b8780 bl 0x436d648c`, `0x437b8796 vldr s14,[sp,#0x34]`, `0x437b87f6 ldrb r3,[r4,#6]`, `0x437b87fe ldrb r5,[r4,#4]`, `0x437b8c44`/`0x437b8c8a bl 0x437b865c`, `0x437b8d56 bl 0x437b84a8` |
| `0x437b8e1c` | 1 | instantánea por mensaje (`EcGain`/`isoAuto`/`bulb`) y su traza; llamada **siempre** por el despachador | `0x437b8e50 ldr r3,[r3,#0x1bc]`, `0x437b8e8e bl 0x437b85ac` |
| `0x437b8ed4` | 3 | `StartImThermal`: si el estado es 1, asigna temporizador y lo arma con `[ctx+0x10]` | `0x437b8ede ldrb r4,[r5]`, `0x437b8f18 bl 0x437b86ac`, `0x437b8f3c ldrh r3,[r5,#0x10]`, `0x437b8f42 muls r2,r3,0x186a0`, `0x437b8f4a bl 0x437b84a8` |
| `0x437b8fb0` | 3 | `EndImThermal`: libera el temporizador y llama a `sendCaution(0)` | `0x437b8fba ldrb r5,[r3]`, `0x437b8fc4 bl 0x437b84f0`, `0x437b8fe6 movs r0,#0`, `0x437b8fe8 bl 0x437b865c`, `0x437b8ff4 strb r0,[r3]` |
| `0x437b9064` | 3 | `RecStart` / `ImStartMovThermal`: asigna y arma el temporizador de movie con `[ctx+0x4a]` | `0x437b906e ldrb r4,[r5]`, `0x437b9078 ldrb r3,[r3]`, `0x437b90b8 bl 0x437b86ac`, `0x437b90dc ldrh r3,[r5,#0x4a]`, `0x437b90e4 muls r2,r3,0x186a0`, `0x437b90ec bl 0x437b84a8`, `0x437b9114 strb r2,[r3]` |
| `0x437b915c` | 2 | `RecEnd` / `ImEndMovThermal`: libera el temporizador y baja la bandera | `0x437b9166 ldrb r4,[r3]`, `0x437b9170 ldrb r3,[r3]`, `0x437b9196 bl 0x437b84f0`, `0x437b91be strb r2,[r3]` |
| `0x437b91e8` | 3 | callback del temporizador: estado 1→2, copia el valor, registra `TimeA ImgTmp` y **rearma** con `([ctx+0x4c]−[ctx+0x4a])`; en estado 2 llama a `0x4378dd78` | `0x437b91f2 ldr r6,[r3]`, `0x437b9204 str r2,[r3]`, `0x437b9210 strh r7,[r3]`, `0x437b9246 subs r2,r2,r3`, `0x437b924e muls r2,r3,0x186a0`, `0x437b9256 bl 0x437b84a8`, `0x437b927a bl 0x4378dd78` |
| `0x437b93c0` | 1 | `ZitZ1cDriver`: valida el canal (0 o 1) y avisa si no existe | `0x437b9418 cbz r4` / `0x437b941a cmp r4,#1`, `0x437b942e` (traza) |
| `0x4386bbec` | 2 | `ZitDdcDriver`: valida formato y número de puntos de una tabla DDC | `0x4386bbf2 ldrb.w r3,[r3,#0x2f]`, `0x4386bc18`/`0x4386bc36 bl 0x4386baf4` (logger propio) |

**Atribución**: prólogo Thumb más cercano hacia atrás, corregido a la **entrada real** cuando la
función tiene preámbulo PC-relativo antes del `push` (`0x437b8ed4`, `0x437b8fb0`, `0x437b9064`,
`0x437b915c`, `0x437b91e8`, `0x4386bbec`). El criterio "destino de salto" se descartó por
producir 41 discrepancias sobre 43 sitios.

## 4. El despachador `0x437b8384`

Es la puerta de entrada del módulo a los mensajes de la tarea de cámara:

1. Toma el **id de 16 bits** del mensaje: `0x437b8388 ldr r3,[r0]`, `0x437b8390 ldrh r6,[r3,#0x10]`.
2. Lo busca en una tabla de **24 entradas de 4 bytes** `{u16 id, u16 código}` en **`0x43befc32`**
   (`0x437b8392 ldr r3,[pc,#0xe4]` + `0x437b8394 add r3,pc`; recorrido `0x437b8396`–`0x437b83ac`,
   `cmp r2,#0x18` en `0x437b83aa`). En las 24 entradas el "código" es el **byte bajo del id**
   (`0x0a10`→`0x10`, `0x0af1`→`0xf1`, `0x0a00`→`0x00`).
3. Hace la búsqueda inversa código→id (`0x437b83e4`–`0x437b8402`) con **defecto `0xa00`**
   (`0x437b8404 mov.w r3,#0xa00`).
4. Despacha por id: `0xa20` → `bl 0x437b9064` (`0x437b843e`, arranque de movie); `0xa21` →
   `bl 0x437b915c` (`0x437b8444`, parada); `0xac0` → contador con tope 2 (`0x437b8454
   cmp.w r2,#0xac0`, `0x437b8460 adds r1,#1`, `0x437b8464 cmp r1,#2`).
5. **Siempre** termina en `0x437b844c bl 0x437b8e1c` (instantánea `EcGain/isoAuto/bulb`).

Ids de la tabla: `0x0a00, 0x0a10, 0x0a11, 0x0a12, 0x0a13, 0x0a81, 0x0a82, 0x0a83, 0x0a8a,
0x0a8b, 0x0a91, 0x0a92, 0x0a93, 0x0a94, 0x0a95, 0x0aa1, 0x0aa2, 0x0aa5, 0x0ab3, 0x0ab5,
0x0af1, 0x0aa8, 0x0a96, 0x0a97`.

## 5. Relación con `[CAM_IMAGER]` (S115): de dónde sale la temperatura

El dato térmico **no** se calcula aquí: se pide al driver del imager.

- `0x437b877a bl 0x436d6118` obtiene el contexto del imager (getter de 4 instrucciones:
  `0x436d6118 ldr r3,[pc,#8]` … `0x436d611e ldr r0,[r3,r2]`); el global es **`0x44026878`** y
  su valor **`0x43e7f858`**.
- `0x437b877e add r1,sp,#0x34` + `0x437b8780 bl 0x436d648c` llaman al **slot `0x6c`** de la
  vtable del imager con un `float*` en pila. El wrapper `0x436d648c` hace
  `r0=[r0]; r3=[r0]; ldr r3,[r3,#0x6c]; blx r3` y registra `'%s:NullPo'` (`0x43c9361a`) si
  el puntero es nulo.
- El módulo lee `0x437b8796 vldr s14,[sp,#0x34]`, multiplica por **`0x42c80000` = 100.0f**
  (literal en `0x437b8a0c`), pasa a `f64`, suma `0.5` (`0x437b87aa vmov.f64 d6,#0.5`) y trunca
  (`0x437b87b6 vcvt.s32.f64`) → entero en **centésimas** de grado, guardado con
  `0x437b87be strh`.
- Si el wrapper devuelve error (`0x437b878c cmp r0,#0` → `0x437b8d30`), emite
  `Error : GetImagerTemperature` (`0x437b8d38`).

Familia de wrappers virtuales del imager (mismo patrón `r0=[r0]; …; blx`): slots
`0x10,0x14,0x20,0x24,0x28,0x2c,0x30,0x34,0x4c,0x54,0x68,0x6c,0x70` en `0x436d6xxx`.
`0x68`=`0x436d6478`; `0x6c`=`0x436d648c` (float); `0x70`=`0x436d64c8`, usado con buffer
`ushort` (`ldrh [sp,#0x236]` / `strh #-1` en `0x438c7994`; otros sitios `0x438888ea`,
`0x43889b9a`, `0x438c7986`, `0x438c851e`).

## 6. Relación con el bloque de `drive_mode` (S124)

`0x437b8774` no solo mide: **selecciona tabla según el modo**. El contexto térmico es el global
**`0x44026884` → `0x43f72b82`** (misma base `0x4401eee4` + índice `0x79a0` que usan
`StartImThermal`/`EndImThermal`; p. ej. `0x437b8ed8 add r3,pc` + `0x437b8edc ldr r5,[r3,r2]`).

- `0x437b87f6 ldrb r3,[r4,#6]` y `0x437b87fe ldrb r5,[r4,#4]`: lee **dos campos de modo**.
- En S124, `FUN_436d6f70` lee `ldrh r5,[r1]` (NowDrv, +0), `ldrh r6,[r1,#4]` (PrevDrv, +4),
  `ldrh r7,[r1,#6]` (NextDrv, +6) y `ldrb sb,[r1,#9]` (`shut`).
- Coinciden los **desplazamientos +4 y +6**, pero aquí se leen como **bytes** (`ldrb`) y con
  otra base → **misma disposición de struct: NO VERIFICADO**.

## 7. Relación con la familia `[CAMERA_MAIN_*]` (S122/S123/S126/S127)

`[CAMERA_MAIN_IM]` es uno de los submódulos en que la fw3.21 parte el antiguo `[CAMERA_MAIN]`
(S128 lo clasifica **RENOMBRADO**: la A7S no usa el prefijo pero conserva los mismos mensajes).
Su vecino natural es **`[CAM_IMAGER]`** (S115), que sí contiene el bloque de exposición:
`[CAM_IMAGER]: SetExps : … [svd][shd][spl][shut]` en **`0x43c93cc2`** y
`SetExpsZ: … [epdsel]` en **`0x43c939b5`**.

**Negativo verificado**: en las 42 cadenas de `[CAMERA_MAIN_IM]` **no** hay `svd`, `shd`, `spl`,
`sint`, `gs:` ni `epdsel`. Las únicas apariciones de la subcadena `shut` son dentro de
`shutdownTh` (`0x43ca6ca8`, `0x43ca6d3f`). El módulo IM **no expone el obturador**.

## 8. Soporte del módulo

| pieza | dirección | qué hace |
|---|---|---|
| logger privado | `0x437b85ac` | construye un mensaje de `0x9a` bytes (`0x435612d0`), lo envía por OSAL (`0x43561244`) y formatea con `0x439c5004`; argumentos `r0=3` (nivel), `r1=0x10` (módulo), `r2=máscara`, `r3=cadena`, resto en pila |
| predicado de máscara | `0x437b848c` | `ldrb r3,[r3,#0xc]; tst r0,r3` → 1/0; decide si se emite la traza |
| temporizador: alloc | `0x437b86ac` | devuelve el handle que las trazas imprimen como `allocTimer:%x` |
| temporizador: set | `0x437b84a8` | `r2:r3` = intervalo 64 bits en ms; las trazas imprimen su retorno como `setTimer:%x` |
| temporizador: free | `0x437b84f0` | libera el handle (`freeTimer:%x`) |
| aviso `sendCaution` | `0x437b865c` | `r0` = 0/1; llamado en `0x437b8c44`, `0x437b8c8a` y `0x437b8fe8` |
| printf genérico | `0x43902718` | salida de la cadena ya formateada |
| OSAL | `0x43561244`, `0x4356127c` | envío / reserva usados por el logger |
| cola de mensajes del shutdown | `0x435612d0`, `0x43aefaf8`, `0x4356120c`, `0x435612ec` | asignar, inicializar, enviar y liberar el mensaje del `THERMAL_SHUTDOWN` (`0x437b8cde`–`0x437b8d10`); el retorno de `0x4356120c` es el que la traza llama `upm_set_off_factor() return %d` |

Los intervalos de temporizador son siempre `campo u16 × 0x186a0` (100 000):
`[ctx+0x10]` en `0x437b8f42`, `[ctx+0x4a]` en `0x437b90e4`, y
`max(1, [ctx+0x4c]−[ctx+0x4a])` en `0x437b924e`.

## 9. Diferencial A6000 fw3.21 vs A7S fw3.20 / A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| cadenas con prefijo `[CAMERA_MAIN_IM]:` | **42** | **0** | **0** |
| textos interiores idénticos | — | **34/42** | **33/42** |
| textos ausentes | — | 8 | 9 |

- **A7S**: faltan `movie thermal diffTemp < 0 :(%d)`, `paramA%f paramB%f diff:%d`,
  `sendCaution(false) return %d`, `RecStart`, `RecEnd`, `TimeA ImgTmp:%d`, `Err:Timer2Callback`
  y `ZitDdcDriver: Invalid format. [%d][%d]`. Conserva `environmentalTemp:%d`, las tablas,
  `ISOAuto`/`ISO1`–`ISO3 TH`, `Abs:`/`Env:`, `send THERMAL_*`, `upm_set_off_factor`,
  `ImCheckThermal`, `Start`/`EndImThermal`, `ImStart`/`ImEndMovThermal` y
  `EcGain:%x isoAuto:%x bulb:%x` (`0x43ca3206`). Su `TimeA ImgTmp:%d, mode:%d`
  (`0x43ca3356`) lleva un campo extra. `RecStart` solo aparece dentro del RTTI
  `22RecStartInfoMsgHandlerE` (`0x43c87e1b`) y `RecEnd` no existe.
- **A6300**: a la lista anterior añade `EcGain:%x isoAuto:%x bulb:%x` (usa
  `EcGain:%x isoAuto:%x bulb:%x 4K:%x USB:%x ` en `0x43da73f6`).
- En ambos, los mensajes comunes existen **sin prefijo** (p. ej. `movie Table` en
  `0x43ca3026` de la A7S y `0x43da7295` del A6300).

→ **RENOMBRADO, no módulo nuevo**: la fw3.21 añade la etiqueta y unos pocos mensajes de
instrumentación; el mecanismo térmico ya estaba.

## 10. Verificaciones hechas

| afirmación | cómo se comprueba |
|---|---|
| 42 cadenas, rango `0x43ca6b32`–`0x43ca71e7` + 2 sueltas | `extract` de `scan_s129.py` (prefijo literal + corte en NUL) |
| 43 sitios, 10 funciones, 0 muertas | mapa PIC estricto global + prólogos Thumb corregidos (`func_map.json`) |
| una cadena con 2 referencias (`0x43ca70f6`) | sitios `0x437b90fe` y `0x437b9268`, ambos `add rX,pc` a la misma vaddr |
| tabla de 24 pares en `0x43befc32` y despacho `0xa20`/`0xa21`/`0xac0` | desensamblado `0x437b8384`–`0x437b8474` |
| temperatura vía slot `0x6c` y escala ×100 | `0x437b877a`/`0x437b8780`, wrapper `0x436d648c`, literal `0x42c80000` |
| 34/42 y 33/42 textos comunes | comparación texto a texto de los interiores en los tres blobs (`diff.json`) |
| 0 prefijos en A7S/A6300 | búsqueda de `[CAMERA_MAIN_IM]` en los tres blobs |
| IM no contiene `svd/shd/spl/sint/gs/epdsel` | búsqueda en las 42 cadenas; `shut` solo dentro de `shutdownTh` |

## 11. NO VERIFICADO / abierto

- **Invocación de `0x437b8774`**: no tiene ningún `bl` ni puntero de 32 bits en toda la imagen
  (0 referencias). Se invoca por despacho indirecto, tabla o callback de temporizador **no
  resuelto**.
- Correspondencia exacta del **slot `0x6c`** con el nombre
  `C_Imager::GetImagerTemperature(float*)` (`0x43c936a3`): inferida por el tipo y el uso, pero
  las tres sobrecargas (`0x43c932d4` `AD(unsigned short*)`, `0x43c936a3` `(float*)`,
  `0x43c93773` `(unsigned short*)`) no aparecen como puntero de 32 bits en ninguna vtable.
- Que el contexto leído en `0x437b8774` sea **el mismo struct** de S124 (coinciden +4/+6, pero
  aquí son `ldrb` y la base es otra).
- Significado de los **24 ids** del despachador y de sus códigos; quién envía `0xa20`, `0xa21`
  y `0xac0`.
- **Fichero fuente** del módulo: no hay ningún `*Thermal*.cpp` en el binario; los vecinos del
  bloque son `CS_imaging.cpp` (`0x43ca3dd7`), `SyncYCOut.cpp` (`0x43ca4de4`) y
  `lc_PreReadAF.cpp` (`0x43ca793f`).
- Qué hace exactamente el helper `0x4378dd78` en el estado 2 del callback (`0x437b927a`).

## 12. Ficheros de este hito

| fichero | contenido |
|---|---|
| `camera_main_im.json` | inventario completo: 42 cadenas, 43 sitios, 10 funciones, despacho, soporte, relaciones S115/S124, diferencial y no verificado |
| `build_json.py` | reconstruye el JSON desde los bytes (reproducible) |
| `scan_s129.py` | extracción de cadenas y comparación con A7S/A6300 |
| `diff.json` | diferencial corregido (34/42 y 33/42) |
| `func_map.txt` / `func_map.json` | mapa función → sitios → cadenas |
| `disasm.py`, `find_entries.py`, `entries_cmp.json` | desensamblador y comparación de entradas |
| `strings_raw.json` | las 42 cadenas con vaddr/offset/texto |

## 13. Revisión del agente principal

_(vacía)_

---

## Revisión del agente principal (21-10-2026)

**Verificado y aceptado (21 tests del hito + comprobaciones a mano):**

1. **Recuento**: 42 apariciones del token `[CAMERA_MAIN_IM]:` — 40 contiguas `0x43ca6b32`–`0x43ca71e7`
   y 2 sueltas (`0x43cb5fc1`, `0x43cb5ffa`) → coincide con el informe.
2. **Despachador**: `0x437b8384` es una función real (prólogo Thumb `0xb5f8`) y la tabla de
   24 pares que cita el informe está en `0x43befc32` con los bytes
   `000a0000100a1000110a1100120a1200` → se ven los ids `0x0a00/0x0a10/0x0a11/0x0a12` con sus
   destinos, tal como describe (`0xa20`→`0x437b9064`, `0xa21`→`0x437b915c`).
3. **El negativo importante, bien acotado**: el módulo **no** expone el obturador. Las únicas
   apariciones de `shut` en sus 42 trazas son la subcadena de `shutdownTh` en
   `[CAMERA_MAIN_IM]: Abs:Tnow=%d shutdownTh=%d cautionTh=%d` `0x43ca6ca8` y
   `Env:Tnow=%d Tenv=%d envTh:%d shutdownTh:%d cautionTh:%d` `0x43ca6d3f` (que pertenecen al
   texto de `[CAM_IMAGER]`, S124) → **ningún parámetro `shut`/`svd`/`shd`/`spl`/`sint`/`gs`/
   `epdsel`** en este módulo → **sin efecto en S51**.
4. **Diferencial**: 0 prefijos en la A7S y el A6300, con **34/42** y **33/42** textos interiores
   idénticos → módulo **renombrado** (no nuevo): el mecanismo térmico ya existía en la A7S con
   otro etiquetado, y la fw3.21 añade instrumentación. Coherente con el mapa de S128.

**Nota**: el informe traía la sección "Revisión del agente principal" vacía, como se le pidió;
esta es la real.
