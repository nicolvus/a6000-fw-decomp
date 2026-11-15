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
