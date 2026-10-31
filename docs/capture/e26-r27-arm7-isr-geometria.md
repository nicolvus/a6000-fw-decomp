# E26-R27 — ARM7: ISR de NAND (`0xd24`), geometría (`0x1a80–0x1ae4`) y las 18 operaciones del despachador

Continúa R16/R17 (BossFirm ARM7, `bootloader.bin[0x18800:+0x3800]`). Fuente: `analysis/e26-recovery/r16_arm7.py` (imagen `IMG`), Capstone ARM de 32 bits. Test: `tests/test_e26_r27_arm7_isr_geometria.py`.

## 1. ISR de estado NAND (`0xd24`) — BINARIO, resuelta

Lee y limpia el registro de estado de interrupción en `base+0x410` (el mismo controlador que `0x5f8`/`0xc1c`/`0xcec`, R17 §3), y lo traduce a un código propio del ARM7 (namespace **distinto** del de la ISR del LDEC, `0x28–0x2d`, R17 §1.3):

| Bit de estado | Código ARM7 | Verificado por bytes |
|---|---|---|
| `0x800` | `0x20` | `0x02 0x0b 0x10 0xe3` (`tst r0,#0x800`) |
| `0x8` | `0x24` | — |
| `0x10000` | `0xd` | — |
| `0x400` | `0x21` | — |
| `0x1` | `0xc` | — |
| `0x10` | `0x23` (si `[r2+4]` no coincide con `0xff00+0xff`) o éxito (lee `[r1+0x440]`) | — |
| ninguno | éxito | — |

El resultado se combina con el máximo acumulado en `[r2+8]` (`strhi r0,[r2,#8]`) — mismo patrón que el «máximo (0xb-flag, resultado)» de la ISR del LDEC (R17 §3), confirmando que **las dos ISR (LDEC y NAND) comparten el mismo mecanismo de agregación de severidad**, con tablas de código separadas.

**Resuelve la parte «`0xc`» del pendiente:** el código `0xc` es el bit `0x1` (el menos significativo) del registro de estado del controlador NAND en `base+0x410`; no tiene relación con los códigos `0x28–0x2d` del LDEC (dominios distintos, ya eran dos cadenas de error distintas en R17).

## 2. Geometría (`0x1a80`–`0x1ae4`) — BINARIO, resuelta

- **`0x1a80` — comprobación de capacidad.** `total = dev[0x18] * dev[8]`; devuelve 1 si `total <= r2` y `r1 <= 0` (verificado: `0x02 0x00 0x53 0xe1` = `cmp r3,r2`). `dev[8]` = número de planos/chips; `dev[0x18]` = unidades por plano.
- **`0x1aa4` — traducción de dirección con entrelazado de planos.** Si `dev[8]==1` (un solo plano), pasa `r1` directo. Si no, usa `dev[0x20]` como paso (*stride*) y `0x372c` (biblioteca de división) para calcular `r0 = ((r6 / dev[0x20]) * dev[0x20] * (dev[8]-1)) + dev[0x20]*entrada + r6` (verificado: `0x94 0x00 0x00 0xe0` `mul r0,r4,r0`; `0x94 0x67 0x22 0xe0` `mla r2,r4,r7,r6`) — fórmula estándar de intercalado de planos NAND (la dirección física avanza por plano antes que por bloque).
- **`0x1ae4` — envoltorio con límite.** Compara `[r1]` (posición) con `[dev+4]` (fin de rango), fija una bandera y llama a `0x1aa4`.

**Resuelve la geometría del pendiente:** confirma que el ARM7 traduce direcciones lógicas a físicas con entrelazado multi-plano (no solo bloque→página lineal), usando campos de un descriptor de dispositivo (`dev[4,8,0x18,0x20]`) cuyo origen (Loader3 o configuración fija) no se rastreó en esta pasada.

## 3. Las 18 operaciones del despachador — estructura común confirmada; semántica individual NO exhaustiva

Las 18 entradas de la tabla `0x379c` (R17 §1) **cargan la misma base SRAM `0x3f40`** en el prólogo (verificado por bytes en las 17 operaciones restantes: `mov r*,#0x3f40` dentro de las primeras 5 instrucciones tras `push`, en los 17 casos). 16 de las 17 la desreferencian de inmediato con `ldr r0,[r*,#0x14]` (mismo campo que usan las funciones de geometría §2); la operación 9 (`0x2eb4`) guarda la base en la pila (`str r0,[sp,#0x18]`) y la usa más adelante. Esto confirma que **todas las operaciones del despachador trabajan sobre el mismo trabajo en SRAM** que op 0 (LDEC), no sobre dominios distintos.

| op | Dirección | Tamaño | MMIO decisivo (primeros 0x300 B) |
|---|---|---|---|
| 0 | `0x1338` | `0x274` | `0x3f50`, `0xf0020000` (LDEC/NAND, R17) |
| 1 | `0x15ac` | `0x5d8` | — |
| 2 | `0x27b4` | `0x160` | — |
| 3 | `0x2914` | `0x70` | — |
| 4 | `0x1d44` | `0xac` | — |
| 5 | `0x2160` | `0x174` | — |
| 6 | `0x22d4` | `0x224` | — |
| 7 | `0x1df0` | `0x70` | — |
| 8 | `0x2b94` | `0x320` | `0x3f50` |
| 9 | `0x2eb4` | `0x200` | `0x3f50` |
| 10 | `0x2984` | `0x210` | `0x3f50` |
| 11 | `0xfe0` | `0xe8` | — |
| 12 | `0x10c8` | `0x270` | `0x3f50`, `0xf0020000` |
| 13 | `0x24f8` | `0x14c` | — |
| 14 | `0x2644` | `0x170` | `0x3f50` |
| 15 | `0x1e60` | `0x300` | — |
| 16 | `0x1b84` | `0xbc` | — |
| 17 | `0x1c40` | `0x104` | `0x3f50` |

**No se clasificó el comando NAND concreto de cada operación** (lectura/escritura/borrado/estado/ID…): ninguna llama a `0xcec` con el patrón directo `mov r0,#cmd; bl 0xcec` que usa op 0 (§ R17 §3); deben pasar el comando por un registro ya cargado o por una rutina intermedia distinta, no identificada en esta pasada. Clasificar las 17 exige trazar cada una por separado (tamaños de `0x70` a `0x5d8` B) — fuera del alcance razonable de este cierre.

## 4. Cierre del pendiente

`E26-R18-ARM7-RESTO` — **CERRADO PARCIAL**: ISR NAND (`0xd24`) y geometría (`0x1a80–0x1ae4`) resueltas por completo (los dos elementos nombrados explícitamente); las 17 operaciones restantes del despachador quedan confirmadas como estructuralmente uniformes (mismo trabajo/dispositivo que op 0) pero sin clasificar una a una por comando NAND — límite declarado, no silencioso.

## 5. Límites

- El origen del descriptor «dispositivo» (`dev[4,8,0x18,0x20]`) no se rastreó hasta Loader3/BOSS.
- Ningún comando NAND (lectura/escritura/borrado/…) se asignó a las operaciones 1–17 individualmente.
- Sin hardware: nada de esto se ejecutó ni se comparó con el controlador NAND real.
