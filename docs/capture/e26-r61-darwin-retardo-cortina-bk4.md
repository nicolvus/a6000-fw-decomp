# E26-R61 — Darwin: duración de la espera de la segunda cortina y su corrección por unidad (BK4 `0x30102`)

Fecha: 05-11-2026. Estático (Capstone sobre `darwin_core.bin` 3.21, base `0x4200`) + lectura de BK4. **Experimento propuesto, no ejecutado.**

Etiquetas: **VERIFICADO** (código/bytes) · **INFERENCIA** · **NO VERIFICADO**.

## 1. Qué calcula Darwin (VERIFICADO por código)

* `0x19a12(Tv)` convierte el Tv (`4096 − 256·log2 t`) en **microsegundos**: `((lut[(0x1000−Tv)&0xff] + 0x800)·1 000 000) >> (11 − ((0x1000−Tv)>>8))`. Tv `0x1900` → 1953 µs; `0x1700` → 7812 µs. Se guarda en `S+0x48`.
* La espera del disparo con `S+0x32 ≠ 0` (`0x18d6e`) suma a esa duración un **`s16` por unidad** leído de la estructura `B = 0x20000300`: `[B+0x88]` (si `r5≠0`) o `[B+0x8a]` (si `r5=0`) en la rama de `0x18ea4`, y `[B+0x84]`/`[B+0x86]` en la de `0x18e5a`; el resultado (`r8 = T + corrección`, mínimo 1) se pasa a `0x2041e`, que arma el temporizador de Darwin. `r5 = 1` cuando `[S+0x31] & 3 == 0`.
* `B` (bloque de `0x180` B, código `0x00020280` de la tabla `0x2a160`) **no está en la imagen y Darwin no puede programar su flash**: llega en ejecución desde el BIONZ (protocolo `AdjCmd/RAM Read/Write` de `av-cam`).

## 2. Dato de esta unidad (MEDIDO en BK4)

BK4 `0x30102` (384 B; **INFERENCIA**: es el bloque `B`): `[+0x84] = 17629`, `[+0x86] = 0`, **`[+0x88] = +334 µs`, `[+0x8a] = +234 µs`**; la plantilla de fábrica del paquete los tiene a 0, así que son **ajuste de la unidad**. Idéntico en el primer volcado (20-10) y hoy.

## 3. Hipótesis y experimento (reversible por NVRAM)

Hipótesis: la espera de cierre de Darwin es `T + corrección`; con EFCS activado el reloj de esa espera arranca antes que el barrido electrónico, y la corrección de la unidad no lo cubre. **NO VERIFICADO**: que Darwin use la misma ruta con EFCS on y off (el paquete `0x0c` es idéntico, así que probablemente sí).

* Variantes generadas offline (`scripts/e26_r61/bk4_variante.py`, 3 B distintos, checksum recalculado), en `analysis/camera-dumps/20261105-experimento-30102/`: `var_088_mas500.bin` (`+0x88`: 334 → 834 µs, SHA-256 `9c52aee5…03e2`) y `var_08a_mas500.bin` (`+0x8a`: 234 → 734 µs, `0ee95f2e…c31c`).
* Aplicación: `scripts/senser_backup_restore.py FILE SHA256` (**escribe NVRAM**, reversible restaurando `20261105-volcado-total-nvram/backup_flash.bin`), reinicio, y fotos a 1/1000 con EFCS on y off.
* Lectura: si **solo EFCS on gana luz** → la corrección es la palanca (y se ajusta solo por NVRAM, sin tocar firmware); si **ambos modos cambian igual** → es una ruta común y no resuelve; si **ninguno cambia** → Darwin no recibió el cambio o usa otro campo (`+0x84/+0x86`).
