# E26-R81 — Auditoría independiente del parche de calibración EFCS (R76/R76b/R80) (07-11-2026, estático)

Revisa `scripts/e26_r76/`, [R76](e26-r76-calibracion-propia-efcs.md), [R76b](e26-r76b-verificacion-parche.md), [R80](e26-r80-auditoria-parche-r76.md) y los commits `77da6565` y `239e2370`. No se tocó la cámara. No se construyó ni instaló ningún paquete.

## 1. Hallazgos

| # | Severidad | Hallazgo | Evidencia (dos métodos) | Corrección |
|---|---|---|---|---|
| 1 | **CRÍTICA** | El hueco del cave `0x13d5a..0x13dc0` **no es una función muerta**. La función empieza en `0x13d58` (`ldr r1,[pc,#0x3fc]` antes del `push {r4,lr}`), y `0x1516c: bl 0x13d58` la llama. Es una de las seis llamadas seguidas `0x13c36, 0x13f0a, 0x13c82, 0x13d58, 0x13dc0, 0x13e46` que rellenan bytes de estado `[r4+0x10..0x27]`. El parche rompería esa función: la llamada ejecutaría el cave y `[r4+0x25]` no se escribiría. | (a) Capstone: decodificación en cada halfword de la imagen, ramas hacia `[0x13d58, 0x13dc0)`. (b) Cálculo a mano de la codificación BL T1 en `0x1516c` (`fef7 f4fd` → `0x13d58`; test). (c) Recorrido recursivo desde todas las palabras-puntero y los vectores: alcanza `0x13d58`. | `parchear()` rechaza el hueco y `selftest` termina con «BLOQUEADO». Test `tests/test_e26_r81_parche_efcs.py` |
| 2 | **ALTA** | El criterio de función muerta de R76b/R80 (inicio = `push {…,lr}`) falla en las funciones que tienen una instrucción antes del `push`. **Las cinco alternativas de R80 están vivas:** `0xaba0` (`bl` desde `0x8170`), `0x11d6a` (desde `0x7b2a`), `0x14fca` (desde `0x1503a/0x15054/0x15070`), `0x13806` (desde `0x13854` y otros), `0x1d2c8` (rama y `ldr` pc-rel). | Bloques tras terminadores incondicionales con referencias entrantes, y recorrido recursivo. Cada `bl` confirmado desensamblando el sitio llamador. | R80 §4 queda corregido: no hay 266 B libres |
| 3 | **ALTA** | No hay en la imagen ningún hueco contiguo de código libre de ≥ 40 B. Fuera de la tabla de vectores, el recorrido recursivo cubre todo el código hasta `0x25c5c`. La única zona de ceros (`0x4316..0x4327` + `0x4330`) ya la usa el parche 3.30–3.38. | Recorrido recursivo (53 426 instrucciones, 709 raíces, más los destinos `tbb/tbh`) y barrido de ceros/`0xff`. | El parche (c) de R76 **no tiene sitio** en la imagen con el diseño actual. Ver §3 |
| 4 | MEDIA | `ajustar --previo` usa `c_por_velocidad` (el punto fijo por velocidad) como el `c` que aplicó Darwin. Darwin aplica el `c` **de la tabla**, que es el promedio del tramo y lleva los saltos de guarda. Los puntos `(x, pérdida)` del pase 2 salen desplazados. | Lectura de `puntos()`/`ajustar()` frente a `_camara_sintetica()`, que sí usa la tabla. | Pendiente `E26-R81-CPREV` (no se corrigió: el parche está bloqueado) |
| 5 | MEDIA | `calibrar` usa el `T` nominal (`1/4000` = 250 µs); Darwin usa el `T` de `0x19a12` (244 µs). Diferencia de hasta ≈ 2,4 % en `x` y en la pérdida. | Tabla de R76b §3 (244, 1953, 3102, 3906 µs) frente a `t_nominal()`. | Pendiente `E26-R81-CPREV` |
| 6 | MEDIA | `escribir_tabla_nvram` abortaba con `assert` (se omite con `python -O`) y no validaba la tabla. Con más de 14 entradas, `ljust` no recorta, así que G pasaría de 128 B. | Lectura del código. | Corregido: `SystemExit` si G ≠ 128 B, si `G+0x48..` no está a cero, si hay más de 13 entradas o si `c ∉ [0, C_MAX]` |
| 7 | BAJA | El emulador de `0x18d6e` sustituye `0x1a738`. Esa función recibe `r1 = ip` y `r2 = S+0x48`, así que el `c` del parche sí le llega en la rama corta (`ip = S+0x3a − S+0x48`). R70 §3 ya la había separado de las líneas de cortina. El emulador no lo muestra. | Desensamblado de `0x18e10..0x18e48` y de la entrada de `0x1a738` (`mov r4,r1; mov r5,r2`). | Documentado. No se amplió el análisis |
| 8 | INFO | `0x1b308` es `bx lr`: sustituirlo no oculta nada. Si `S+0x94 ≠ 0`, `S+0x48` se sobrescribe después del gancho y el parche no hace nada (inocuo). | Desensamblado. | — |
| 9 | INFO | Los registros del cave (`r1–r3`) no se leen en `0x18d6e` antes de volver a cargarse. La compuerta del cave coincide con la de `0x18a2e` (`lsls #30` + `bne` sobre `S+0x31`, y bit 1 de `S+0x60`). | Desensamblado de `0x18a2e` completo y de `0x18d80..0x18e10`. | — |

## 2. Cambios de `77da6565` y `239e2370`

* `77da6565` añadió R76, R76b y los scripts v2. Elegir `0x13d5a` vino del criterio de `push` (hallazgo 1). Lo demás que comprobé (tabla en `G+0x48`, compuerta `&3`) es correcto.
* `239e2370` reparó los imports y `keystone`, y añadió al cave el límite de 13 entradas y la validación de `c`. Las dos medidas son correctas en sí. R80 §4 heredó el criterio erróneo y dio por libres funciones que están vivas.

## 3. Consecuencia y lo que queda

* El parche (c) **no se puede empaquetar** tal como está. Hay tres salidas, todas pendientes de decisión: (i) anexar el cave tras `0x2a85c`, que exige que el cargador admita un `darwin_core` más largo (solo se decide en cámara; R76b lo descartó por eso); (ii) un rediseño que no necesite cave; (iii) quedarse con la vía (a) de R76 (solo NVRAM: `B+0x86` o `G+0x42`), que no requiere parche de Darwin.
* No se preparó `allowed_addresses` en `build.py`: no hay ubicación válida.
* El bloqueo hace que no tenga sentido repetir ahora la emulación de la imagen parcheada ni aplicar las propuestas de modelo de R80 §3. Siguen pendientes y dependen de la salida elegida.
* Solo en cámara: la premisa NVRAM → Darwin, si el cargador acepta un tamaño mayor, la curva δ real y el degradado vertical (R80 §2).

REA: abrí una sesión sobre `darwin_core.bin` y la cerré sin resultados (el autoanálisis no terminó a tiempo). Las conclusiones se apoyan en Capstone y en el cálculo a mano.

> **Corrección ([R82](e26-r82-parche-efcs-v3.md)):** el bloqueo de §3 se levanta: el parche (c) se reescribe en sitio dentro del prefijo `0x18d6e..0x18e0f` (vía A, mismo tamaño, sin hueco). Se confirma con un segundo método que no hay hueco de código ≥ 40 B (cadenas ASCII de `printf` = datos vivos). `E26-R81-CPREV` queda aplicado en `e26_r76_calibrar_efcs.py`.
