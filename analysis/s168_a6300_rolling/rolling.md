# S168 — control positivo del «rolling shutter» del A6300: la cadena es **muerta**

> Hito de la **línea de ingeniería inversa general** (control positivo para la línea del
> obturador electrónico). Solo lectura de bytes: `av-cam.bin` de la **A6000 fw3.21**
> (`analysis/rea-independent/input/av-cam.bin`), **A7S fw3.20** y **A6300 fw2.01**.
> Convención: `vaddr = 0x43541000 + file_offset` (verificada también para A7S y A6300).
>
> Este hito **matiza y corrige** un colateral firmado por el agente principal en la revisión
> de **S164** (ver §6).

## 1. Resumen / veredicto

**La cadena `position num in rolling is strange %d` del A6300 fw2.01 no la referencia NINGÚN
código**: es una **cadena muerta** en `.rodata`. Por tanto **no** demuestra que el A6300
fw2.01 implemente compensación de *rolling shutter*; es un resto de una versión anterior
(o código que quedó fuera de este binario).

La única cadena viva de su entorno es
`position num in vd is strange %d`, y el código que la emite es un **cálculo de ancho en
bits del número de posición del VD** (visor), con control de rango.

| afirmación | estado |
|---|---|
| `position num in rolling is strange %d` existe en el A6300 fw2.01 (`0x43d9fe03`) | VERIFICADO |
| tiene **0** referencias PIC (regla estricta) en todo el `av-cam.bin` del A6300 | VERIFICADO |
| no hay puntero absoluto de 4 B ni par `movw`/`movt` que la compongan | VERIFICADO |
| no aparece en ningún otro fichero del paquete del A6300 (solo en `av-cam.bin`) | VERIFICADO |
| no aparece en la A6000 fw3.21 ni en la A7S fw3.20 | VERIFICADO |
| `position num in vd is strange %d` (`0x43d9fde2`) tiene **1** referencia viva | VERIFICADO |
| las 5 cadenas de la banda `0x43d9fd80`–`0x43d9fe80`: 4 vivas, 1 muerta («rolling») | VERIFICADO |
| el A6300 fw2.01 **implementa** rolling shutter | **NO VERIFICADO / NO** (sin evidencia viva) |

## 2. Método (reutilizable)

El escáner canónico del repo (`analysis/s106_imaging_cap/scan_pic_refs_strict.py`) está
fijado al binario de la A6000. Para este hito se han escrito **tres herramientas
parametrizadas** en `analysis/s168_a6300_rolling/`:

1. **`scan_refs.py`** — réplica exacta de la regla estricta con *blob* y *base* como
   parámetros (`destino = literal_relativo + (add + 4)`; el *pool* guarda el desplazamiento
   **relativo**, no la dirección absoluta).
2. **`find_ref.py`** — **método inverso**, independiente: recorre todos los candidatos de
   *pool* y calcula `add_addr = destino − W − 4`, comprobando que ahí hay realmente un
   `add rD,pc` y que el `ldr` del mismo registro más cercano por detrás tiene ese valor.
   Sirve de **control cruzado** del método 1.
3. **`alive_map.py`** — mapa vivo/muerto de una banda de `.rodata`: por cada cadena da
   nº de referencias PIC, punteros absolutos y pares `movw`/`movt`.

**Controles de validación (ambosCorrectos):**

| control | esperado | obtenido |
|---|---|---|
| A6000, `Get ADC CNF_ADC_CH_EVF_TEMP Val:0x%x(%d)` (`0x43c7751a`, S166) | 1 referencia | 1 (`ldr 0x43636ce2` + `add 0x43636ce6`) |
| A6300, `position num in vd is strange %d` (`0x43d9fde2`) | 1 referencia | 1 (`ldr 0x43729164` + `add 0x43729166`) |

Y **control negativo**: `position num in rolling is strange %d` → 0 por los **dos** métodos
independientes.

## 3. Evidencia

### 3.1 Mapa de la banda `0x43d9fd80`–`0x43d9fe80` (`alive_map.json`)

| cadena | dirección | refs PIC | puntero abs. | `movw/movt` | texto |
|---|---|---|---|---|---|
| `[BL]Wait_BL_ASYNC_RCV (%+hd)` | `0x43d9fdc5` | **1** | 0 | 0 | viva |
| `position num in vd is strange %d` | `0x43d9fde2` | **1** | 0 | 0 | viva |
| `position num in rolling is strange %d` | `0x43d9fe03` | **0** | 0 | 0 | **MUERTA** |
| `this vsync command has another command` | `0x43d9fe29` | **1** | 0 | 0 | viva |
| `ASYNC BL COMMAND BANISH ! Mount_FcZm_BLComm.cpp %d` | `0x43d9fe50` | **1** | 0 | 0 | viva |

El discriminante funciona: 4 de 5 cadenas de la banda están referenciadas por código y
exactamente una —la del *rolling*— no lo está.

### 3.2 El código vivo: `0x4372914c` (A6300)

```
0x4372914c: push   {r3, lr}
0x4372914e: bl     #0x4372f7f8
0x43729152: bl     #0x43b902b0        ; -> r0 = número de bits
0x43729156: movs   r1, #1
0x43729158: lsls   r1, r0             ; r1 = 1 << n
0x4372915a: uxth   r1, r1
0x4372915c: subs   r3, r1, #1
0x4372915e: uxth   r3, r3
0x43729160: cmp    r3, #0xfe          ; (1<<n)-1 <= 254 ?
0x43729162: bls    #0x4372916e        ; si cabe -> devuelve r1 (ancho en bits)
0x43729164: ldr    r0, [pc, #0xc]     ; pool 0x43729174 = 0x00676c78
0x43729166: add    r0, pc             ; -> 0x43d9fde2
0x43729168: bl     #0x43986518        ; traza "position num in vd is strange %d"
0x4372916c: movs   r1, #8             ; valor de retorno: 8 bits
0x4372916e: mov    r0, r1
0x43729170: pop    {r3, pc}
```

Es un **cálculo de ancho en bits con control de rango**: el número de posición del VD debe
caber en 7 bits (`(1<<n)-1 <= 0xFE = 254`); si no, se avisa y se fuerza 8 bits.

### 3.3 Contexto del fragmento `.rodata` (A6300)

```
...ectsOverSharedPixels: work1 is shortage. req%dpt, act%dpt[BL]Wait_BL_ASYNC_RCV (%+hd)
position num in vd is strange %dposition num in rolling is strange %d
this vsync command has another commandASYNC BL COMMAND BANISH ! Mount_FcZm_BLComm.cpp %d
```

El fragmento pertenece a la zona del **driver BL** (`Mount_FcZm_BLComm.cpp`), coherente con
las trazas `[BL]` de la A6000 (S133 `[MOUNT_DEBUG]`, S66).

## 4. Diferencial A6000 fw3.21 / A7S fw3.20 / A6300 fw2.01

| elemento | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| `position num in rolling is strange %d` | 0 | 0 | **1** (`0x43d9fe03`) |
| refs de código de esa cadena | — | — | **0 (cadena muerta)** |
| `position num in vd is strange %d` | 0 | 0 | **1** (`0x43d9fde2`) |
| refs de código de esa cadena | — | — | **1** (viva, `0x43729166`) |
| `position num in` | 0 | 0 | **2** |
| `strange %d` | 0 | 0 | **2** |
| `rolling` (cualquier grafía) | **0** | **0** | **1** (la cadena muerta) |
| `roll`/`Roll`/`ROLL` (cualquier grafía) | 36 / 3 / 1 | 37 / 2 / 1 | 40 / 2 / 2 |

De las 36/37/40 apariciones de `roll` en las tres cámaras, la mayoría están dentro de
`Controller` / `Scroll` / `CompressScroll` (nombres de clase RTTI y de fichero) y **no** del
concepto de *rolling shutter*: el recuento bruto de `roll` **no** es evidencia de nada.

**Excepción (3 casos reales en la A6000, que NO son del concepto *rolling shutter*):**

| cadena | A6000 | A7S | A6300 | sitio de referencia en la A6000 |
|---|---|---|---|---|
| `SetDistRoll` | `0x43c7b1f3` | `0x43c7b800` | `0x43d7b055` | `0x43643846` |
| `SetRoll` | `0x43c7fc61` | `0x43c81de8` | `0x43d8189d` | `0x4366581e` |
| `RollAD,%d,%d,%d,%d,%d,%d,%d,%d` | `0x43c9ae2e` | — | — | `0x43721324` |

`SetRoll` y `SetDistRoll` son **comandos de la API RC** (recursos) y son **comunes a las tres
cámaras** (`1/1/1`); `RollAD` es **propio de la A6000 fw3.21** (`1/0/0`). El análisis de esta
familia de comandos se hace en el hito **S169**; aquí solo se deja constancia de que **ninguno
de los tres es evidencia de *rolling shutter***: `SetRoll`/`SetDistRoll` están junto a
`SetStblzPower`, `SetDistItp`, `SetHoldX/Y`, `SetSync`, `SetMirror` (comandos RC de recursos),
y `RollAD` imprime 9 valores AD leídos de un global (`0x437212b8`), no una shutter.

La cadena del *rolling* **no aparece en ningún otro fichero** del paquete del A6300 (solo en
`av-cam.bin`), ni en los `.so` de la A6000.

## 5. Qué NO se afirma

- **NO** se afirma que el A6300 fw2.01 implemente *rolling shutter*: la única evidencia era
  una cadena sin código.
- **NO** se afirma que el A6300 *no* lo implemente: la ausencia de la cadena viva no lo
  descarta; solo que **esta fw2.01 no lo demuestra**.
- **NO** se desarrolla la sigla «vd» (visor / *viewfinder display*): en la A6000 la cadena
  `VD` es de otra línea (S90) y aquí es un número de posición del VD; la correlación es
  **INFERENCIA**.
- **NO** se ha seguido el destino de `0x4372f7f8` ni `0x43b902b0` (los doshelpers que
  producen el número de bits): **NO VERIFICADO**.
- **NO** se ha identificado el *fichero fuente* de la función `0x4372914c`.

## 6. Corrección que este hito impone sobre S164

La revisión del agente principal en **S164** (`analysis/s164_camera_is/camera_is.md`) escribió:

> «el A6300 fw2.01 sí tiene 1: `position num in rolling is strange %d` → el concepto de
> rolling shutter **existe en el A6300 y no en la A6000/A7S**».

**Eso queda matizado**: la cadena **existe** en el A6300 fw2.01, pero **está muerta** (0
referencias de código) → **no** prueba la existencia del concepto en ese firmware. Lo que
sigue en pie es el dato bruto (la cadena está en el A6300 y no en la A6000/A7S), y lo que
**cae** es la inferencia «el A6300 implementa *rolling shutter*».

Este matiz **no cambia S51** (A=NO, B=NO, C=NO) ni el resultado de S135 (control positivo
del subsistema `ElecShutter/` en el HAL del A6300, que es un hallazgo **independiente** de
esta cadena). De hecho, **debilita** un argumento potencial: la única pista de *rolling
shutter* en el A6300 no está respaldada por código.

## 7. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
A6300=firmware/extracted/a6300-fw201/payload/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin
.venv/bin/python analysis/s168_a6300_rolling/scan_refs.py $A6300 0x43541000 0x43d9fe03   # 0
.venv/bin/python analysis/s168_a6300_rolling/scan_refs.py $A6300 0x43541000 0x43d9fde2   # 1
.venv/bin/python analysis/s168_a6300_rolling/find_ref.py  $A6300 0x43541000 0x43d9fe03   # 0 (control cruzado)
.venv/bin/python analysis/s168_a6300_rolling/alive_map.py $A6300 0x43541000 0x43d9fd80 0x43d9fe80
.venv/bin/python -m pytest tests/test_s168_a6300_rolling.py -q
```

## 8. Revisión del agente principal

_(vacía)_
