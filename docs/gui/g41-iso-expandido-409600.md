# G41 — ISO expandido hasta 409600: código ISO = índice de tabla, topes localizados, origen del máximo sin encontrar (15-11-2026, ESTÁTICO, sin parche)

Resultado: **PARCIAL**. Sin CFW, sin cámara, sin tocar el arnés. No hay parche porque no se localizó la rama que fija el máximo (25600 normal, 51200 con Multi Frame NR); sí queda el mapa de datos y de topes.

## 1. Código ISO = índice de la tabla de `av-cam` (VERIFICADO en bytes)

* Tabla `av-cam` 3.21 (base `0x43541000`) a `0x43bc48e0`: `10, 10, 12, 16, 20, 25, 32, 40, 50, 64, 80, 100, 125, … 25600, 32000, 40000, 51200, 64000, 80000, 102400, 128000, 160000, 204800` (índice 0 … `0x2c`). **Código ISO del modelo = índice**: `0x8` = 50 (Lo), `0xb` = 100, `0x23` = 25600, `0x26` = 51200, `0x2c` = 204800. La copia de 100…204800 empieza en `0x43bc490c`; otra copia de 100…204800 en `0x43bc6070`.
* Único acceso resuelto a la tabla: `0x437b4044` (`ldr r3,[pc]; add r3,pc` → `0x43bc48e0`; `ldr.w r6,[r3,r0,lsl #2]`). Justo antes, `0x437b403e: movs r1,#0x2c; bl 0x43aeb8e4` acota el índice a `0x2c` (tamaño de la tabla, no es el tope de menú).
* **A7S** (`av-cam-a7s.bin`): la lista llega a 819 200 (`…204800, 256000, 320000, 409600, 512000, 640000, 819200`, tablas en `0x680c74`/`0x680d40`); la A6000 se corta en 204 800. 409 600 = índice `0x2f` en el esquema de la A6000 (no existe: 3 entradas más).

## 2. La UI solo representa hasta el código `0x26` (bytes de `wrapperIso.so` 3.21)

`WrapperIso::getIso` (`+0x1cb0`, Thumb) mapea con `cmp/movs` (sin tablas) tres entradas del modelo a enteros de UI:

| Entrada (claves de info `0x48`: `0x1f4/0x1f5/0x1f6`) | Códigos admitidos | Salida UI |
|---|---|---|
| actual | `0x8…0x26` (uno a uno, 31 valores, 50…51200), `0` = AUTO | `0x30…0x4e`, auto `0xf` |
| mín. y máx. (menú) | `0, 9, 0xb, 0xc, 0xe, 0x11, 0x14, 0x17, 0x1a, 0x1d, 0x20, 0x21, 0x23, 0x24, 0x26` | `0x11…0x1f` (mín.), `0x21…0x2f` (máx.) |

Un código `> 0x26` cae a `0x247e` (error): **ampliar el máximo exige también parchear `wrapperIso`** (añadir casos y ampliar la lista del `.uxc`), no basta con cambiar el modelo. La cadena `0x23` (25600) frente a `0x26` (51200) coincide con `PARAMID_ISO_MENU_STD_RANGE_MAX` (rango estándar) frente a `PARAMID_ISO_SPEED_RATE_MAX` (rango total, con MFNR) que `libObj` recibe de `av-cam` (cadenas `Invalid ObjMsg (PARAMID_ISO_SPEED_RATE_[MIN|MAX]_ACT)` y `…MENU_STD_RANGE_[MIN|MAX]_ACT`, `libObj` `0xcfbf3d…0xcfc008`).

## 3. Ganancia (no determinada)

No se leyó la conversión ISO → ganancia analógica/digital: el único consumidor localizado de la tabla es el anterior. Los 3 valores extra de la A7S (256000…819200) existen en el binario de otra cámara, pero eso no demuestra que el sensor de la A6000 admita el factor (×2…×16 sobre 25600): **no verificado**.

## 4. Arnés

`scripts/gui/avcam/ae.py` solo emite `0x2014` (velocidad) y `0x2023` (apertura); **no emite ningún `0x…ISO_SPEED_RATE_MIN/MAX`**, y su lista `ISOS` acaba en 25600 como dato propio. No existe, pues, MAX de ISO del firmware que se pueda ver en el arnés y no se sacaron capturas. Para probar hará falta (a) localizar el emisor real o (b) inyectar en `ae.py` un mensaje de ISO con los ids de `PARAMID_ISO_SPEED_RATE_*` (pendiente; `scripts/gui/harness/` es de otra sesión).

## 5. Intentos sin éxito (para no repetirlos)

* Búsqueda de `cmp #0x26` junto a `#0x23` en `av-cam` (17 sitios) y `movs #0x23/#0x26` pareados (81): todos eran enumeraciones de modos, cadenas→enum (`0x4362bd90`, `0x43b508ba`, `0x4381a5e8`) o cadenas de llamadas, ninguno el tope de ISO. Sin cadenas `MFNR`/`MultiFrame` en `av-cam` (solo en `libObj`: `PARAMID_MULTI_FRAME_NR` `0xd4ad94`, `pvt_subActionObjectMultiNrProcEvt`).
* Alineación A6000/A7S alrededor de las tablas ISO: la disposición de datos difiere (no hay desplazamiento constante), sin diff útil.

## 6. Pendiente

**ISO-A** (ver `docs/PENDIENTES.md`).

## 7. Método identificador → emisor (15-11-2026, ESTÁTICO; sigue PARCIAL, sin parche)

**Ids numéricos (VERIFICADO)**: la tabla de nombres `PARAMID_*` de `libObj` (`0xfdc144`, 1350 punteros, índice = id − `0x9500`; calibrada con `PARAMID_FNO`=`0x951b` y `SHUT_SPEED_NUMER`=`0x951c` de `ae.py`) da `ISO_SPEED_RATE`=`0x951e`, `_MIN`/`_MAX`=`0x96fe`/`0x96ff` (`_SET` `0x9701/2`, `_ACT` `0x9704/5`), `MENU_STD_RANGE_MIN`/`MAX`=`0x989e`/`0x98a1` (`_ACT` `0x98a0/3`).

**av-cam no emite esos ids**: sin `movw #0x96ff/0x98a1/0x951e` (los halfwords `0x96ff`/`0x98a1` hallados son punteros a cadenas `0x439c96ff`, etc.; el `movw #0x9705` de `0x43b2a4c6` es otro mensaje, de AF). Las constantes `0x1ee/0x1ef/0x1f0` de av-cam (`0x435edd80`, `0x439382cc`…) son **números de línea de log** (`0x435ec380` imprime), no claves. Intento descartado: no repetir.

**Receptor en `libObj` (VERIFICADO en bytes)**: el conversor `0x4db7c4` (puntero en la tabla `0x102c34c`; llamado desde `0x4c12a4`) lee del mensaje (`0x42ac00(msg, clave, &v)`) las claves `0x1ee` (valor), `0x1ef` (mín.), `0x1f0` (máx.) y `0x376`/`0x377` (rango estándar mín./máx.), las convierte y escribe `0x951e`, `0x96fe`, `0x96ff`, `0x989e`, `0x98a1` (`0x49fc94`). **Conversores de código propios de `libObj`, que topan antes que `wrapperIso`**:
* `0x4e0ea8` (valor/mín./máx.; `tbh`, índice ≤ `0x4a`): código `k` → id interno `0x21+k`, con los pasos enteros como ids especiales (`k=0x20`→`0x274` 12800, `0x23`→`0x275` 25600, `0x26`→`0x276` 51200, `0x29`→`0x277` 102400); **`k=0x2a` devuelve 0 (no válido)**; `0x2b…0x4a` son otra serie (`0x1e5…0x501`).
* `0x4e41c4` (rango estándar; `tbb`, ≤ `0x2a`): misma correspondencia `k`→`0x21+k` con los mismos 4 especiales.

Por tanto el firmware ya porta en `libObj` los códigos hasta **`0x29` (102400)** con id propio; 160000/204800 (`0x2a…0x2c`) exigirían ampliar ambas tablas de `libObj`. El mensaje que trae las claves `0x1ee…0x377` es de av-cam hacia `libObj` (tipo de mensaje del conversor `0x4db7c4`); su emisor en av-cam **sigue sin localizar** (las claves no son inmediatos en av-cam: probablemente `av-cam` las numera con otra base o las genera desde una tabla).

**`wrapperIso::getIso` (`+0x1cb0`)**: es una cadena lineal `cmp r0,#k; movs r3,#ui` (sin tabla, `0x1d3c…0x1f8c+`), con el centinela `0x4f` = «sin valor» y los ids de UI `0x30…0x4e` ya ocupando el rango; **no hay hueco para casos nuevos** (hace falta una cueva y ids de UI nuevos + el `.uxc`): parche (b) no trivial, **no escrito**.

**Cadena exacta y mínima para 102400 (primer paso viable)**: (a) emisor av-cam de `0x1ef/0x1f0/0x376/0x377` (sin localizar) → tope `0x26`→`0x29`; (b) `getIso` y `.uxc` con códigos `0x27…0x29` (UI nuevos > `0x4e`, p. ej. 64000/80000/102400); (c) tabla `0x43bc48e0` ya incluye hasta 204800 (índice `0x2c`), sin ampliar; 409600 (`0x2f`) exigiría 3 entradas más en tabla y en ambos conversores de `libObj` (sin hueco verificado).

**Ganancia**: no leída (sin avance); la tabla de av-cam solo está acotada a `0x2c` por `movs r1,#0x2c; bl 0x43aeb8e4` (`0x437b403e`).

**Siguiente paso concreto**: abrir `av-cam` en REA y buscar los emisores del mensaje de ISO por el **tipo de mensaje** que despacha la tabla `0x102c34c` de `libObj` (índice de `0x4db7c4` en la tabla = id de mensaje: usar ese id como inmediato en av-cam, como `0x2014` de `ae.py`), no por los ids `PARAMID`.
