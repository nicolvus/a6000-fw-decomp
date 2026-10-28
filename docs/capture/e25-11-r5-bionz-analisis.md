# E25-11 — Dónde calcula BIONZ `r5` y qué cambiar para que la foto use ShutMode 0 (análisis offline, 27-10-2026)

Sesión **100 % offline** (Capstone sobre `av-cam.bin` fw 3.21, SHA-256 `b60c845c…56bb9`, base `0x43541000`, físico = virtual + `0x40000000`).
No se conectó la cámara ni se escribió nada. Bytes verificados en `tests/test_e25_11_av_cam_r5.py` (9 pruebas; se omiten sin firmware).
Etiquetas: VERIFICADO = bytes/instrucciones leídos; INFERENCIA = interpretación.

## 1. Cómo consume `r5` el sensor (VERIFICADO)

`SetExposure` del IMX210 (`0x436d6f6c`, vtable `0x43fcc090+0x28`) lee el bloque de parámetros `param` (en `r1`):

| Campo | Lectura | Uso |
|---|---|---|
| `param+0` (h) | `0x436d6fae ldrh r5,[r1]` | **r5**: byte bajo → `+2` de una estructura sombra; bits 8–13 → otra |
| `param+4` (h) / `+6` (h) | `0x436d6faa`, `0x436d6fb0` | r6 / r7 (tiempos adicionales, sin efecto en T037/T038 salvo atascos) |
| `param+9` (b) | `0x436d6fb6 ldrb.w sb,[r1,#9]` | **ShutMode**; `tbb` de 5 ramas (0–4) |

`r5` es independiente del ShutMode (prólogo común); el ShutMode cambia bits de ID1 y la espera de Darwin `0x107` (S56, T028–T031).

## 2. Dos productores de `param` (VERIFICADO por llamadas; semántica = INFERENCIA)

`bl 0x436d6320` (envoltorio de `SetExposure`) se llama solo en 4 sitios: `0x438c79fc`, `0x438c830c`, `0x438c8824`, `0x438cc894`.

1. **Vista en directo — `0x437b27b8`** (único llamador `0x438cc868`, justo antes de `0x438cc894`): construye un registro de 16 B
   (`[r6+0x168..0x177]`, copiado a `*(r8+8)`) cuyo primer halfword vale
   `r5 = máx( [r8] − 0x4382fa94(h[obj+0x4da]) / [r6+0x134], [r6+0x144] )` (`0x437b288a..0x437b28c6`: `rsb sb,r0,sb` y `cmp/strhs/strlo`).
   Interpretación: `[r8]` = longitud de cuadro en líneas (≈ 4219–4270, T046), el cociente = líneas de exposición y `[r6+0x144]` = mínimo de `r5`. Es la fórmula
   medida en T046/T047 (E = (4219 − `r5`)·15,2 µs). **Sin verificar:** unidades de `0x4382fa94` y de `[obj+0x4da]`; que `[r8]` sea exactamente 4219.
2. **Foto — función de captura `0x438c828c`** (llamada al envoltorio en `0x438c830c`): el `param` lo copia `0x4383fd6c` desde un registro estático de modo
   (`R+0x64..0x73`, 16 B, vía `0x4383fb6c(cap+0x1c0, cap+0x1b8)`) a `cap+0x64c` (`param+9` = `cap+0x655`). Ese registro lleva **`r5` constante = 1** (T032), de modo
   que sin cortina la exposición sale como el cuadro completo (64,9 ms; T046 «sin forzar») y la cortina mecánica fijaba el tiempo real. Por eso la foto no sigue la velocidad.

## 3. Ya existe una ruta ShutMode 0 + `r5` fijo en la foto (VERIFICADO)

En `0x438c82a8..0x438c82cc`:

```
0x438c82a8  bl  0x43a12c64        ; clasificador de modo
0x438c82ac  cmp r0,#2 ; beq 0x438c82b8
0x438c82b0  bl  0x43a12c64 ; cmp r0,#3 ; bne 0x438c82d0     ; (0x438c82b6)
0x438c82b8  movs r3,#0 ; movs r1,#2
0x438c82bc  strb.w r3,[r4,#0x655]   ; param+9  = ShutMode 0
0x438c82c0  strh.w r3,[r4,#0x650]   ; param+4  = 0
0x438c82c4  str.w  r1,[r4,#0x64c]   ; param+0  = 2  (r5 = 2)
0x438c82c8  strh.w r3,[r4,#0x652]   ; param+6  = 0
0x438c82cc  strb.w r3,[r4,#0x654]   ; param+8  = 0
```

`0x43a12c64` clasifica una variable global (literal `0x43a12ca4`): `0xbb` → 2; `1` → 3; `0x31–0x37`, `0xbc`, `0xee–0xef`, `0xfd–0xff` → 1; resto → 0.
INFERENCIA: es el código de modo de disparo; con 2 ó 3 la foto se hace en ShutMode 0 con `r5` = 2 (cuadro completo ≈ 64 ms, sin parámetro de velocidad).
Cuál es el modo 2/3 en la A6000 (¿automáticos?) **no está verificado**; hay una ruta análoga en la A7S (S52, `0x438b775c`). Los otros llamadores ponen `param+0 = 0` con ShutMode 4
(`0x438c79e2`, bandera `[r6+5]`) o ShutMode 1 (`0x438c87f0`).

## 4. Qué cambiar (diseño, no probado)

Objetivo: en M/A/S/P, ShutMode 0 con `r5 = máx(r5_mín, VTS − T/15,2 µs)`.

| Opción | Cambio | Ventajas / límites |
|---|---|---|
| **C1** (lo ya probado en RAM, T028–T047) | `0x436d6fb6` → `4ff00009` (`mov.w sb,#0`) y `0x436d7000` → `r5` calculado | Fuerza ShutMode 0 para **toda** llamada (vista en directo ya usa 0; vídeo y otros modos sin probar). `r5` no puede ser constante: necesita T |
| **C2** (propuesta) | En `0x438c82b6` sustituir `bne 0x438c82d0` (2 B) por `nop` (`00bf`) para tomar siempre el bloque de §3, y cambiar `movs r1,#2` (`0x438c82ba`) por un cálculo de `r5` en una cueva de código | Solo afecta a la ruta de captura. Falta T: **[cap+0x4da] (código Tv, §6)**, no `[cap+0x56c]` (descartado en §6). T → líneas: `0x4382fac8([cap+0x4da])` da µs; líneas = µs·5/76 (`0x4355faf0` es la división ya existente); constantes (4219, 15,2 µs) medidas en esta cámara |
| C3 | Llamar al constructor de la vista en directo `0x437b27b8` desde la captura | Descartada por ahora: argumentos y efectos laterales sin verificar |

Pendiente antes de cualquier prueba: que `[cap+0x4da]` lleve en la **foto** el código Tv de la velocidad (§6); valor de `[r6+0x134]` y `[r6+0x144]`; que Darwin (`0x107`) no dependa de `r5`; efecto sobre ráfaga/vídeo/AF.

## 5. Vía permanente: no recomendada hoy

- `av-cam.bin` está dentro de `nflasha3` (TPZL: vmlinux + initrd + av-cam + sabin) en `firmware.tar`. Cambiarlo exige un re-empaquetador reproducible byte a byte (existe para Darwin, **no** para `nflasha3`), que el arranque no valide firma/hash (sin verificar) y reescribe ≈ 212 MB de particiones ([E24-04 M16](e24-04-dictamen-seguridad.md)).
- Un `av-cam` defectuoso deja sin arranque el sistema principal, y **la única entrada al actualizador es por software desde ese sistema** ([E24-03 F6](e24-03-auditoria-recuperacion-usb.md)): el FDAT 3.24 de recuperación solo sirve si la cámara sigue llegando al actualizador. El riesgo es «alto y simétrico» (E24-04) y no hay recuperación independiente (E25-04).
- **Alternativa sin flasheo (no implementada):** reaplicar los parches de RAM (§4 C1/C2, con verificación y reversión) desde la app RemoteShutter tras cada arranque, vía telnet/adb. No persiste tras apagar, pero es reversible y no toca flash/NVRAM.

## 6. Unidades verificadas (offline, 27-10-2026)

**Tv → tiempo — VERIFICADO por bytes y por emulación** (`scripts/e25_11_tv_emu.py`, Unicorn sobre `av-cam.bin`; prueba `test_tv_a_tiempo_emulado`):

- `0x4382fac8(x)` devuelve **µs** = `1e6 · 2^((4096 − x)/256)` (±1 µs); `0x4382fa94(x)` devuelve ese tiempo en **1/256 µs** y `0xFFFFFFFF` si `x ≤ 0xC00` (≥ 16 s). Entrada `x` = `0x1000 + 256·log2(1/t)`: `0x1000` = 1 s, un paso de 1/256 EV por unidad.
  Tablas internas: `0x43902924` = `2^(x/256)·65536` (exp2 con tabla de 256 entradas).
- Velocidades enteras (calculado con la función): 1/4000 → `x`=`0x1bf7` → 250 µs; 1/1000 → `0x19f7` → 1000 µs; 1/250 → `0x17f7` → 4002 µs; 1/60 → `0x15e8` → 16 674 µs.

**`[cap+0x56c]` NO es el tiempo de exposición (INFERENCIA moderada):** es un `u32` que `0x438c7aee` pone a `10·k + valor` o `2·valor`, y `0x438c7df0` reescribe desde `fp`; se usa como `1000·[0x56c] / …` y como mitad baja de la carga del mensaje a Darwin `0x107` junto con `[0x570]` (`0x438c83ae..ba`). Es la espera/sincronización asociada al mensaje `0x107` (S56), no `T`. Se descarta como entrada de C2.

**`[cap+0x4da]` es el candidato correcto (VERIFICADO por bytes; significado = INFERENCIA):** halfword copiado de `[src+0x29c]` en una tira de seis halfwords `+0x4d4..+0x4de` (`0x43b0cbc6`, simétrico en `0x43b0c554`); la única lectura que lo usa es el constructor de la vista en directo (`0x437b2878`), que lo pasa a `0x4382fa94`. Falta comprobar que en la **foto** lleve el código de la velocidad elegida (dump en vivo, con autorización).

**Constantes del sensor (INFERENCIA fuerte):** `0x4385de94(a, m, c)` = `(0x271000 | 0x4e2000) / a · m` (u16), que se usa como longitud de cuadro (VTS). Con `a = 600`: 2 560 000/600 = **4267 líneas**, el cuadro completo medido (≈ 4270; T046: 64,9 ms). Y 15,2 µs/600 = 25,33 ns = 64,9 ms/2 560 000: **una misma unidad de 25,3 ns (≈ 39,5 MHz) explica tanto el tiempo de línea como el de cuadro**. No se pudo leer `[r6+0x134]` (la estructura está a cero en el volcado de servicio en reposo `ram-servicio-20261020`).
**No resuelto:** el constructor de la vista en directo divide `256·t_µs` entre `[r6+0x134]` (`0x437b2894`); con `[0x134]`=600 daría 2,34 µs por línea (6,49 veces menos que los 15,2 µs medidos). Hay una escala (¿unidad de `0x4382fa94`? ¿otra fuente de `[0x134]`?) sin explicar; para la foto C2 usaría las constantes **medidas** (T044/T046/T047), no esa división.

**Fórmula C2 propuesta (calculada, no medida salvo T047):** `r5 = máx(r5_mín, 4219 − round(µs/15,2))` con `µs = 0x4382fac8([cap+0x4da])`:

| Velocidad | µs | líneas | `r5` | medido (T047) |
|---|---|---|---|---|
| 1/4000 | 250 | 16 | 4203 | 0,24 ms (obj. 0,25) |
| 1/2000 | 500 | 33 | 4186 | — |
| 1/1000 | 1000 | 66 | 4153 | 0,99 ms (obj. 1,00) |
| 1/500 | 2001 | 132 | 4087 | — |
| 1/250 | 4002 | 263 | 3956 | 4,03 ms (obj. 4,00) |
| 1/125 | 8005 | 527 | 3692 | — |
| 1/60 | 16 674 | 1097 | 3122 | 16,75 ms (obj. 16,7) |
| 1/30 | 33 348 | 2194 | 2025 | — |
| 1/15 | 66 696 | 4388 | **−169 (imposible)** | — |

**Límite nuevo:** con ShutMode 0 la exposición máxima uniforme es el **cuadro completo (≈ 64,9 ms ≈ 1/15,4)**; desde 1/15 hacia velocidades más lentas `r5` queda fuera de rango y habría que dejar la ruta normal (ShutMode 3, donde el τ de T044 pesa poco) o un modo de varios cuadros. C2 debería caer a la ruta original cuando `líneas > 4218`.
