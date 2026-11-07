# E26-R72 — Datos que el EFCS usa y nunca se habían mirado: `0x30087+0xa0..` en el BIONZ y la configuración `[0x20000050]` de Darwin (07-11-2026, estático)

> **Corregido por [R73](e26-r73-destino-30087-y-ganchos-efcs.md):** en §1, los consumidores `0x4384095c`/`0x4385d874` leen otra estructura. El valor de `0x30087` va a `StillInfo+0x2b4` (procesado de imagen en Linux), no al sensor: no es la palanca del reinicio. Los ganchos son variables de depuración del grupo 2.

Sigue a [R71](e26-r71-medida-gpio-bionz-efcs.md) (fotos a 1/1000 con EFCS activado: **negras, confirmado por el usuario**). El usuario no quiere analizador lógico, así que la búsqueda sigue en estático: Capstone sobre `av-cam.bin` 3.21 (base `0x43541000`) y `darwin_core.bin` 3.21, más los 28 `backup_flash.bin`. REA abrió `av-cam.bin` (901 s), pero `procedure_pseudo_code` falló por `provider_timeout`, así que todo lo que sigue sale de bytes e instrucciones.

## 1. BIONZ: el planificador EFCS escribe `record+0x156` desde la NVRAM `0x30087` (VERIFICADO)

* En `0x43841838–0x438418ce`, `0x43841070` (planificador EFCS) elige según el modo `[cap+0x1c0]`, `[cap+0x28]`, `[cap+0x6a8]`, `[cap+0x90]` y `[cap+0x4860]` un `u16` de la tabla `0x43f6b7de + {0xa0…0xb4}` y lo escribe en **`record+0x156`**; en los demás modos escribe 0. El planificador normal (`0x437b0db4/0x437b0f58/0x437b0f6e`) escribe ahí el valor del descriptor de modo del sensor (`cap+0x118`, o un valor de pila).
* **`0x43f6b7de` es la imagen en RAM de la propiedad `0x30087`.** Lo dice el emparejamiento por índice entre la tabla de punteros `0x43ff3200` (índice 36) y las de IDs `0x43ff2fac`/`0x43ff345c`. Ese emparejamiento queda **verificado** con dos entradas que también están en la tabla `{ID, RAM, tamaño}` `0x4400ea60`: `0x30100 → 0x43f76342` (índice 40) y `0x30086 → 0x43f786f2` (índice 35).
* Valores medidos de `u16[0x30087 + 0xa0 … 0xb4]`:

  | +0xa0 | +0xa2 | +0xa4 | +0xa6 | +0xa8 | +0xaa | +0xac | +0xae | +0xb0 | +0xb2 | +0xb4 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | 90 | 166 | 90 | 90 | 90 | 150 | 90 | 0 | 0 | 0 | 150 |

  Son **iguales en los 28 volcados (20-10 → 05-11)**: no explican un cambio.
* Consumidores (VERIFICADOS por instrucción):
  * `0x4384095c` (llamado desde `0x43b1eb84`) suma `record+0x15c + 0x156 + 0x160 + 0x162` y lo guarda en `[r4+4]` y `[r4+0x36]`.
  * `0x4385d874` (llamado desde `0x437b26c8`, la zona del cálculo de `r5`) calcula `0x156 + 0x158 − 0x1000` y lo copia a la estructura de ventana del sensor (`r6+0x116`, `r4+0x1c`).
  * `0x158` lleva un sesgo de `0x1000`, y los campos vecinos (`0x152`, `0x154`, `0x15c`) salen de la geometría del modo del sensor: **`record+0x156` es una posición en líneas dentro del plan de lectura y reinicio** (INFERENCIA).
* **Lectura (INFERENCIA, sin verificar):** con EFCS activado, el firmware sustituye esa posición por un valor de calibración de la NVRAM. 90 líneas × 15,2 µs ≈ 1,37 ms, el mismo orden que la pérdida medida (≈ 1,27 ms). Si es el adelanto del reinicio electrónico respecto a la cortina, sería una **palanca de compensación sin tocar código**: escribir solo en la NVRAM, `0x30087+0xa0`/`+0xac` (modo de foto única), como en R61, pero esta vez en una tabla que sí usa el EFCS. Falta comprobar el signo, las unidades y qué índice usa la foto única.
* El planificador EFCS también tiene **ganchos de depuración** (`0x43841722–0x438417ae`): bytes globales que, si no valen cero, sobrescriben `record+0x64` (`sl`, la línea de reinicio), `+0x68`, `+0x6a`, `+0x6e`, `+0x70` y `+0x72`. Están en `0x43f9b37c…0x43f9b451` y valen 0 en la imagen. Su valor en ejecución no se ha leído.

## 2. Darwin: la configuración del mecanismo `[0x20000050]` no la escribe `darwin_core` (VERIFICADO)

* `0x20c74()` = `0x1b080(0)` = (`[0x200002c0] ≠ 0` ? `[0x20000050] & 7` : 0), y lo reduce a {1, 2, 3} o 0. Decide si A suelta P4D (solo con 1 o 2) y si B sube P4E (≠ 0), es decir, si Darwin mueve los imanes de cortina.
* Ninguna de las dos celdas está en los bloques que se pueden escribir desde el BIONZ (`0x2a124`/`0x2a160`). La carga inicial de `darwin_core` no las inicializa (empieza en `0x20002a00`). Un barrido de escrituras con base `0x20000000` no encuentra ninguna en `+0x50` ni en `+0x2c0`.
* `darwin_core` **no lee la flash de arranque** `0x0000–0x41ff`: ninguna carga de literal apunta ahí (el único candidato, `0x800`, es un dato de una tabla).
* **Consecuencia:** esas celdas las pone algo **anterior a `darwin_core`**, probablemente el cargador de Darwin en `0x0000–0x41ff`. Es la única memoria por unidad que no se reescribe al actualizar y que nunca se ha volcado (R58 §6). INFERENCIA fuerte. No se puede leer sin el SWD de Darwin.
* Contra que sea la causa: con `0x20c74() = 0`, B no movería P4E. R71 midió que el fin de exposición sigue a B (4,2 frente a 4,57 ms), así que hoy vale ≠ 0.

## 3. Estado

* **Nuevo pendiente E26-R72-30087:** saber qué representa `record+0x156` con EFCS (adelanto del reinicio o ventana), qué índice usa la foto única y su signo.
  * Estático: decompilar `0x4385d874` y `0x4384095c` (REA sin tiempo de espera, o Ghidra).
  * Prueba barata de solo lectura por SWD: leer `0x83f6b7de+0xa0..0xb6` y los ganchos `0x83f9b37c…0x83f9b451` en vivo.
  * Si es el adelanto: ajustar la NVRAM (por ejemplo, 90 → 174 líneas) con copia de seguridad y autorización.
* **Nuevo pendiente E26-R72-DARWIN-CFG:** origen de `[0x20000050]`/`[0x200002c0]` (cargador de Darwin). Solo con el SWD de Darwin (`CN4906`).
* E26-R66-RESET sigue PARCIAL; el usuario descarta el analizador lógico.
