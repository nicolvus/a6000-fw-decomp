# E25-15 — ShutMode 0 y la temporización nativa del IMX210

Sesión **100 % offline** (28-10-2026). No se conectó la cámara, no se ejecutó firmware en la cámara,
no se escribió RAM/NVRAM/NAND y no se ejecutó T051.

| Binario | SHA-256 | Base |
|---|---|---|
| A6000 fw 3.21 `av-cam.bin` | `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9` | `0x43541000` |
| A7S fw 3.20 `av-cam.bin` | `b857d33879d610abd185148d676de7ea0f753af3a08389994e788d617925103e` | `0x43541000` |

Etiquetas: **V** = bytes/instrucciones leídos; **I** = inferencia; **N** = no verificado.
Emulación: `scripts/e25_15_emu.py` (Unicorn 2.1.4 + Capstone 5.0.7), evidencia en
`analysis/e25-15/emulacion.json`. Pruebas: `tests/test_e25_15_shutmode.py`.
Las pruebas E25-14 se ejecutan también (ver §14).

---

## 1. Respuesta a la pregunta decisiva

**No basta con cambiar ShutMode 3 → 0.** Con `ShutMode = 0` y `r5 = 1`, la exposición queda en
el cuadro completo (≈ 64–65 ms, uniforme; extrapolación de la ley medida en T046 — T051 debe medirlo); la llamada posterior al método `+0x30` **no puede**
acortarla a 1/250 s porque escribe **otro bloque de comandos** (`blk+0x66..0x6c`) y **no toca**
el parámetro de integración `r5` (`blk+0x52`). Para obtener 1/250 hay que cambiar además `r5`
a `4219 − 4002/15,2 ≈ 3956`.

La dependencia exacta es:

> `ShutMode = 0` selecciona **reinicio por filas**; la distancia reinicio→lectura la fija `r5`
> (`param+0` de `SetExposure`). El método `+0x30` programa la **posición de lectura** en una
> escala 0..4095 y un flag; no es el mismo parámetro ni el mismo registro.

Esto coincide con lo medido en T046 (mismo `r5`, velocidades 1/250 y 1/30, misma exposición) y con
la emulación diferencial de §7. **Corrige E25-14 en un punto:** el método `+0x30` no recibe el
código Tv directo ni una representación temporal lineal; recibe un **código de posición** derivado
de los ajustes de cuadro/lectura (ver §5.3). Que la velocidad seleccionada gobierne ese código
**no está demostrado**.

---

## 2. Diagrama de flujo de datos

```
Ajustes de captura (objeto global 0x43f79f94; espejo en cap+0x1198)
  +0x162  código de exposición (Tv según E24-05e/E25-11; no re-verificado)   +0x15e  código de modo   +0x164  código de cuadro/posición
      |                                          |                       |
      | (flag 0x436f0778, log)                   | 0x4382fefc            |
      v                                          v                       v
  [flag record+0xf6]                    sVar5 = [0x164] − líneas([0x15e])
                                                     |
                                                     v
                                   0x437b061c(1, sVar5, bloque12, ajustes, out...)
                                                     |
                                     out[0..3] = código de posición
                                                     v
  bloque de ajustes cap+0x5c8 (48 B, +0x14 = r5)   record+0x74..0x79 (bloque +0x30)
      |                                                  |
      | 0x437b43b4 / 0x43841070 copian                   |
      v                                                  v
  record estático 0x43ea5b4c / 0x43eee770  <---- 0x437f8a50 (solo foto) ----+
      |                                                                     |
      | record+0x64..0x73 (16 B: r5, ancho, alto, ..., ShutMode)             |
      v                                                                     v
  cap+0x64c  ── SetExposure (vtable+0x28, 0x436d6f6c) ──► blk+0x50/0x52/0x54/0x56/0x57
                                                                             
  record+0x74..0x79 (posición + flag) ── +0x30 (vtable+0x30, 0x436d7e08) ──► blk+0x66/0x68/0x6a/0x6c
                                                                             
  Después: 0x43ad9116 / 0x43ad911c(1) (commit del objeto imager) → transporte (no seguido al registro físico)
```

Secuencia real en `0x438c828c` (foto):

| # | Dirección | Instrucción | Efecto | Estado |
|---|---|---|---|---|
| 1 | `0x438c829c` | `bl 0x437f8a50` | construye **cap+0x64c** y **cap+0x6bc** desde el registro de cuadro | V |
| 2 | `0x438c82a8..b6` | `0x43a12c64` ×2; `cmp #2/#3` | si el modo es 2/3: `param+9=0`, `param+0=2`, `param+4=0`, `param+6=0`, `param+8=0` | V |
| 3 | `0x438c8302..0c` | `add r1,cap,#0x64c`; `bl 0x436d6320` | `SetExposure` (vtable `+0x28`) | V |
| 4 | `0x438c8314..1e` | `add r1,cap,#0x6bc`; `bl 0x436d6398` | método `+0x30` (vtable `+0x30`, "SetRead") | V |
| 5 | `0x438c8326..30` | `0x43ad9116`, `0x43ad911c(1)` | commit del objeto imager | V (llamadas) |
| 6 | `0x438c8334` | `strh r7,[cap+0x650]` | restaura `param+4` | V |

Bytes: `0x438c829c: 30f7d8fb` (BL a `0x437f8a50`), `0x438c82b8: 00230221 84f85536 a4f85036 c4f84c16`
(`param+9=0`, `param+4=0`, `param+0=2`), `0x438c8302: 04f5c861 0c31 b6f89c20 0ef608f8`,
`0x438c8314: 04f5d661 0c31 b6f89c20 0ef63bf8`.

**Ni `cap+0x64c` ni `cap+0x6bc` son buffers estables de la aplicación**: `0x437f8a50` los reescribe
en cada captura (paso 1). Una escritura de datos anterior a ese paso se pierde.

---

## 3. Los dos bloques de parámetros

### 3.1 `cap+0x64c` (16 B + cola) — `SetExposure`

Construido por `0x437f8a50` → `0x4383fd6c` (16 B) y la cola `[sp+0xe..0x12]` → `cap+0x65c/65e/660`:

```
0x4383fda0  bl 0x4383fb6c            ; registro de cuadro (0x43ea5b4c o 0x43eee770)
0x4383fdaa  add r3,r0,#0x64
0x4383fdb0  ldm r3,{r0,r1,r2,r3}     ; 16 B desde record+0x64
0x4383fdb2  stm lr,{r0,r1,r2,r3}     ; → *param_3 = cap+0x64c
0x4383fdb6  add r3,r5,#0x74          ; record+0x74 → scratch (cap+0x6bc después)
0x437f8ace  ldrb r3,[sp,#0x12] ; 0x437f8ad6 strb r3,[r4,#0x660]   ; cola
```

Campos consumidos por `SetExposure` (`0x436d6f6c`):

| Campo | Lectura | Uso |
|---|---|---|
| `param+0` | `0x436d6fae ldrh r5,[r1]` | **r5**: bits 0–7 y 8–13 → dos campos de configuración; base de la integración |
| `param+4` | `0x436d6faa` | ancho/ventana (r6) |
| `param+6` | `0x436d6fb0` | alto/ventana (r7) |
| `param+8` | `param_2[4]` (modos 2/3) | campo auxiliar |
| `param+9` | `0x436d6fb6 ldrb.w r9,[r1,#9]` | **ShutMode** (0–4) |
| `param+0x10` | `0x436d717a ldrh.w r0,[sl,#0x10]` (modo 3) | temporización auxiliar (`/1000+1 → obj+0x3a0`) |
| `param+0x14` | `param_2[10]` (modo 2) | campo auxiliar |

Escrituras del método:

| Destino | Valor | Instrucción |
|---|---|---|
| `obj+0x10` | `param+4` | `strh` |
| `obj+0x12` | `r5` | `strh` |
| `obj+0x3a8` | `param+4` (u32) | `str.w` |
| `blk+0x50` | `param+4` | `0x43ad9a4a` |
| `blk+0x52` | **r5** | `0x43ad9a4e` |
| `blk+0x54` | `param+6` | `0x43ad9a52` |
| `blk+0x57` | **ShutMode** | `0x43ad9a56` |
| `blk+0x56` | 0 | `0x43ad9a5a` |
| `0x4401ca2e` | bits de cfg del modo | ramas 0/1/2/3/4 |
| `obj+0x3a0` | contador auxiliar (modos 0/1/2/3/4) | `strh` |

### 3.2 `cap+0x6bc` (16 B) — método `+0x30` ("SetRead")

Construido por `0x437f8a50`:

- Si `[0x44020e90+0x24] == 1`: de `record+0x74/0x76` (`0x437f8ab2: bdf80a30 bdf80820 a4f8be36 … a4f8bc26`).
- Si no: `0x437b21b8(cap+0x1198, cap+0x20, &blk3, &out)` y `out+2/out+4 → cap+0x6bc/6be`.

Campos consumidos por `+0x30` (`0x436d7e08`):

| Campo | Lectura | Uso |
|---|---|---|
| `+0` | `ldrh r3,[r8]` → `uStack_30` | **código de posición** (no Tv crudo) |
| `+2` | `[r8+2]` | reservado (no usado) |
| `+4` | `[r8+4]` | reservado |
| resto | — | solo el primero se lee; el resto no |

Escrituras del método:

| Destino | Valor | Instrucción |
|---|---|---|
| `blk+0x66` | `*param` (código) | `0x43ad9a66` |
| `blk+0x68` | conversión `0x436d8a90` (0..4095) | `0x43ad9a6a` |
| `blk+0x6a` | código ajustado (>0x1000) | `0x43ad9a6e` |
| `blk+0x6c` | flag `>0x1000` | `0x43ad9a72` |
| 4 pares de campos cfg | valor de líneas/posición | `0x43ad9262` ×4 |
| `obj+0x3a3` | 1 | `strb.w r7,[r4,#0x3a3]` |
| `obj+0x2e?` | `[row48+0x1a]`, `[row48+0x1c]` | defaults |

### 3.3 Comparación directa

| Aspecto | `SetExposure` (`+0x28`) | `+0x30` ("SetRead") |
|---|---|---|
| Entrada | 16 B: r5, ventana, ShutMode | 16 B: código de posición (solo +0 se lee) |
| Conversión | ninguna; r5 ya en líneas | `0x436d8a90`: código → posición 0..4095 (tabla exp2 de 256 entradas) |
| Bloque de comandos | `blk+0x50/0x52/0x54/0x56/0x57` | `blk+0x66/0x68/0x6a/0x6c` |
| Campos cfg globales | r5, ancho, alto, ShutMode | 4 pares (posición/líneas) |
| Contador `obj+0x3a0` | **sí** (modos 0–4) | no |
| Flag `obj+0x3a3` | no | **sí** (=1) |
| Depende de ShutMode | **sí** (despacho) | **no** (no lo recibe) |
| Depende de r5 | **sí** | **no** (no lo recibe) |

**Campos compartidos: ninguno de los dos parámetros de integración.** Comparten el objeto
(`obj+0xfc`) y el mecanismo de commit, pero escriben sub-bloques disjuntos.

Verificación del nombre: la cadena de error de `+0x30` es
`"[CAM_IMAGER]: Invalid SetRead Error!! [drive_mode:%2d]"` (`0x43c93d30`), y la de `SetExposure`
`"[CAM_IMAGER]: Invalid SetExposure Error!!"` (`0x43c9397a`). El nombre **no** se usa como prueba:
la prueba es el destino de las escrituras.

---

## 4. Quién construye cada bloque y de dónde sale la velocidad

1. **Registro de cuadro**: `0x4383fb6c` devuelve uno de dos buffers estáticos
   (`0x43ea5b4c` / `0x43eee770`, punteros en `0x44022648` / `0x44025dfc`).
2. **Constructor de la foto**: `0x437b43b4` (llamado desde `0x437f8948`, `0x437f89ec`,
   `0x43affec6`, `0x43afff26`) hace `memset(record,0,0x158)` y copia 48 B desde `cap+0x5c8` a
   `record+8`. La variante EFCS `0x43841070` (llamada desde `0x437f8816`) hace lo mismo y escribe
   `record+0x64`, `record+0x74..0x79`.
3. **r5**: `0x43841070` escribe `record+0x64 = record+0x1c` (`0x43841710: 6866`; también
   `0x438417d0: 6a66`). `record+0x1c` es el campo `+0x14` del bloque de 48 B copiado desde
   `cap+0x5c8`, es decir **`cap+0x5dc`**. En la cámara medida vale **1** (T032/T046).
   Hay overrides de depuración en `0x43f9b4fd`/`0x43f9b501` (r5) y `0x43eedec0` (ShutMode),
   a cero en reposo.
4. **ShutMode**: `record+0x6d` se escribe desde el byte global `0x43eedeca`
   (`0x4384166c..ec`) y desde el override `0x43eedec0` (`0x438417d2..e0`). No es una constante
   `3` en el código: es un **dato de ajustes**. En la foto normal vale 3 (T032); la ruta de modo
   2/3 lo fuerza a 0 con `r5=2` (`0x438c82b8`).
5. **Bloque `+0x30`**: `record+0x74..0x79` lo escribe `0x437b061c(1, sVar5, …)` dentro de
   `0x437b43b4` (`puVar26[0x3a] = uStack_30`, `[0x3b] = uStack_2e`, `[0x76] = uStack_2c`, flag
   `+0x79 = 1`). En `0x437b43b4`, `sVar5 = [ajustes+0x164] − 0x4382fefc([ajustes+0x15e])`
   (`0x437b45bc..c0`, `0x437b44xx`); en la variante EFCS `0x43841070` sale de
   `[r4+0x30c]` ajustado (`0x4383fe6e`, `0x4383ff4a..ff8e`). En ambos casos es un **código de
   cuadro/posición**, no el Tv.
   El código de exposición `[ajustes+0x162]` (Tv según E24-05e/E25-11) se usa en `0x436f0778` para un flag (`record+0x134`), en el log
   (`0x438413b6`) y en el mensaje a Darwin, pero **no** se copia al bloque `+0x30`.
6. **Velocidad estabilizada**: el Tv vive en el objeto de ajustes (`0x43f79f94`, espejo
   `cap+0x1198`); el pipeline de ajustes lo copia campo a campo (`0x43b0c156`, p. ej.
   `0x43b0cae2: strh r3,[r5,#0x162]`). La captura lo lee ya estable, pero **no hay una función
   nativa que convierta ese Tv en `r5` dentro de la ruta de foto**: `r5` viene de otro campo
   (`cap+0x5dc`) y es constante 1 en la foto normal.
7. **Carrera de T050**: la velocidad se lee desde la app justo después de `/ss`; si el ajuste aún
   no se ha propagado al objeto de ajustes, el `r5` calculado corresponde a la velocidad anterior.
   Es una carrera de **datos de entrada**, no del firmware.

---

## 5. Escenarios A / B / C

### 5.1 Definición

| Escenario | ShutMode | r5 | `+0x30` |
|---|---|---|---|
| A (normal) | 3 | 1 | sin modificar, código de posición real |
| B (solo ShutMode) | 0 | 1 | sin modificar, mismo código |
| C (T046–T050) | 0 | `4219 − T/15,2 µs` | sin modificar, mismo código |

B **no se midió directamente** en T046–T050: se infiere de la ley `E = (4219 − r5)·15,2 µs`
(r5=0 → negro; r5≥4300 → 64,9 ms) y de que `+0x30` no toca r5. T051 incluye B como brazo propio.

### 5.2 Resultado de la emulación (mismo código de posición en A/B/C)

Con `SR_CODE = 0x0F00` (bloque `+0x30` idéntico en los tres):

| Campo | A | B | C (1/250: r5=3956) |
|---|---|---|---|
| `blk+0x50` (param+4) | 0 | 0 | 0 |
| `blk+0x52` (**r5**) | 1 | 1 | **3956** |
| `blk+0x54` (param+6) | 0 | 0 | 0 |
| `blk+0x56` | 0 | 0 | 0 |
| `blk+0x57` (**ShutMode**) | 3 | 0 | 0 |
| `obj+0x3a0` | 1 | 1 | 1 |
| `blk+0x66` (`+0x30`) | 3840 | 3840 | 3840 |
| `blk+0x68` (`+0x30`) | 2047 | 2047 | 2047 |
| `blk+0x6a` (`+0x30`) | 3840 | 3840 | 3840 |
| `blk+0x6c` (`+0x30`) | 0 | 0 | 0 |

**A y B solo difieren en ShutMode; B y C solo en r5.** El método `+0x30` es idéntico en los tres.
La emulación también confirma que `+0x30` **no escribe** `blk+0x50..0x57`, `obj+0x3a0` ni
`obj+0x3a3` (salvo el flag `0x3a3=1`), y que `SetExposure` **no escribe** `blk+0x66..0x6c`.

### 5.3 Conversión de `+0x30` (0x436d8a90)

Entrada: código de posición `x`; salida 0..4095. La conversión `0x436d8a90` tiene **dos
llamadores**: el método `+0x30` (`0x436d7e08`) y el método `+0x34` "SetReadZ" (`0x436d74b8`),
ambos de lectura. `SetExposure` **no** la usa.

| `x` | salida |
|---|---|
| `0x0a00` | 4031 (saturación) |
| `0x0b00` | 3967 |
| `0x0c00` | 3839 |
| `0x0d00` | 3583 |
| `0x0e00` | 3071 |
| `0x0f00` | 2047 |
| `0x0fe0` | 340 |
| `0x0ff0` | 174 |
| `0x0fff` | 11 |
| `0x1000` | 11 |

Es una posición normalizada (0..4095), **no** el número de líneas de integración (0..4219 medido).
La tabla es `0x43bdbebe` (256 × u16) y la división `0x4355faf0` es `__aeabi_uidiv` (truncante).

---

## 6. Emulación: resultados por velocidad

Tiempo Tv emulado con `0x4382fac8` (coincide con E25-11) y `r5 = 4219 − round(µs/15,2)`:

| Velocidad | Código Tv | µs | Líneas | r5 calculado |
|---|---|---|---|---|
| 1/8000 | `0x1cf7` | 125 | 8,22 | 4211 |
| 1/4000 | `0x1bf7` | 250 | 16,45 | 4203 |
| 1/1000 | `0x19f7` | 1000 | 65,79 | 4153 |
| 1/250 | `0x17f7` | 4002 | 263,29 | 3956 |
| 1/60 | `0x15e8` | 16674 | 1096,97 | 3122 |
| 1/15 | `0x13e8` | 66696 | 4387,90 | **−169** |
| 1/8 | `0x12f8` | 127737 | 8403,75 | **−4185** |
| 1 s | `0x1000` | 1 000 000 | 65 789 | **−61 570** |
| 30 s | `0x0b17` | 30 067 871 | 1 978 149 | **−1 973 930** |

Para 1/15 y más lentas el `r5` calculado es negativo: **no es representable**. El límite de la ruta
es el cuadro completo (≈ 64,9 ms). No se intentó extenderlo con valores fuera de rango.

---

## 7. Conclusión sobre la necesidad de `r5`

1. **Estructural (V):** `SetExposure` y `+0x30` escriben campos distintos; `+0x30` no recibe
   `ShutMode` ni `r5` y no puede sobrescribir `blk+0x52`.
2. **Emulación (V):** en A/B/C el bloque `+0x30` es idéntico; solo cambian `blk+0x52` y `blk+0x57`.
3. **Medición (V, T046/T047):** con ShutMode 0 y el mismo `r5`, 1/250 y 1/30 dan la misma
   exposición; la exposición sigue `E = (4219 − r5)·15,2 µs` con pendiente −15,2 µs/unidad.
4. **Por tanto (V/I):** B ≠ C. Cambiar solo ShutMode da cuadro completo uniforme; para 1/250 hay
   que poner `r5 ≈ 3956`. El `r5=1` mantiene una exposición cercana al cuadro completo.

No se observó ninguna ruta en la que `+0x30` reutilice el Tv para fijar la integración. La
afirmación de E25-14 «el método de velocidad ya recibe la velocidad real» queda **matizada**:
recibe un código de posición de cuadro/lectura; su dependencia del Tv seleccionado no está
demostrada.

---

## 8. Exposiciones superiores a un cuadro, Bulb y 30 s

Rutas acotadas (§8 del encargo):

- `0x4381106c` (**StrtExps**, `CaptureManager`): copia 16 B desde `*(0x4378f9b4()+0x24)`,
  los ajusta con `cap+0x1f8`, `cap+0x1fc`, `[obj+0xcc]`, `[obj+0x14e]`, y llama a
  `0x4380fcac` (setup) y **`0x43ae935a` → `SetExposure`** con `r2=1`. El bloque es una plantilla
  de 16 B en RAM (`0x43e9922c`, BSS), cuyo `param+9` y `param+0` son **estado de ejecución**;
  no se pudo leer su valor estático.
- `0x43ae9380` → **`SetRead` (`+0x30`)** con `r2=1`, llamado desde `0x43811042` con un bloque de
  6 B (código + dos campos) al final de la secuencia de bulb.
- `0x43ae93ca` → wrapper `0x436d63d4` → vtable `+0x34` = `0x436d74b8` ("SetReadZ"). Es una
  variante de lectura exclusiva del IMX210 (en el A7S `+0x34` = `0x43ad9859` devuelve 5, no
  soportado): usa la misma conversión `0x436d8a90`, fija el flag `obj+0x3a4` (frente a `+0x3a3`
  de `+0x30`), escribe **un solo par** de campos de configuración (descriptores `0x44020280`/`0x4401f960`; el campo real es `[descriptor]+2`) y
  **no** escribe el bloque de comandos `blk+0x66..0x6c`. **No se encontró ningún llamador**
  (REA + barrido BL + búsqueda del puntero `0x43ae93cb` en el binario): es código no referenciado
  en este build, no una ruta de bulb demostrada.
- **No hay** contador de cuadros, acumulador ni máquina de armado en el IMX210 equivalente a
  `0x436f43c0/0x436f43f0` del A7S. `0x436f43c0` y `0x3dc` no existen en el método del IMX210
  (E25-14, V).
- La plantilla de bulb usa los **mismos** `SetExposure`/`SetRead`, con los mismos límites de
  conversión; no se encontró un modo de sensor con cuadro más largo ni una lectura distinta.

**Veredicto separado:**

| Rango | Veredicto |
|---|---|
| ≤ ≈ 65 ms | **SÍ** demostrable con ShutMode 0 + r5 (T046/T047); límite = cuadro completo |
| > 65 ms | **NO** con el mecanismo actual: no hay valor de r5 representable ni acumulador demostrado |
| Bulb | **NO demostrado**: usa SetExposure/SetRead con plantilla de runtime; no se demostró que esa plantilla supere un cuadro ni que el sensor acumule |
| 30 s | **NO demostrado**: ídem; además el Tv 30 s da r5 negativo en la ruta ShutMode 0 |

No se confunde «velocidad seleccionable en el menú» con «integración silenciosa demostrada».

---

## 9. Precisión de 1/8000

- Granularidad: 1 línea = 15,2 µs (T044/T046, independiente).
- 1/8000 = 125 µs = **8,22 líneas**. Con truncamiento: 8 líneas = 121,6 µs (−2,7 %); con
  redondeo: 8 líneas; con techo: 9 líneas = 136,8 µs (+9,4 %).
- `0x4355faf0` es `__aeabi_uidiv` (truncante). Si el firmware calcula `r5 = VTS − floor(τ/line)`,
  la exposición efectiva es `ceil(τ/line)·line` → **+9,4 %** a 1/8000; si redondea `r5` hacia
  arriba, −2,7 %. La ruta de la vista en directo trunca la división (`0x437b2894`), por lo que
  el sesgo esperado es **positivo** (exposición algo mayor).
- No se encontró un mínimo de líneas impuesto por `SetExposure`: `r5=0` da imagen negra (T046);
  `r5` útil medido 1..4219. El mínimo físico del SHR no está demostrado.
- Offset fijo: la ley medida usa 4219, no 4270 (VTS); hay ≈ 51 líneas de margen/blanking. Es un
  offset empírico, no una constante del código.
- No hay evidencia de que el modo de lectura cambie el tiempo de línea: 15,2 µs se midió en el
  modo normal; no se probaron todos los modos.
- Precisión garantizable sin hardware adicional: **±1 línea (15,2 µs)**, más la incertidumbre de
  calibración absoluta (±20–25 % de T050, que es de escena/tanda, no de cuantización).

---

## 10. ¿Se pueden evitar los parches de código? (P1–P5)

| Prioridad | Resultado | Evidencia |
|---|---|---|
| **P1** ShutMode 0 por datos | **PARCIAL**: `param+9` sale del byte de ajustes `0x43eedeca` (no es constante 3) y la ruta de modo 2/3 lo fuerza a 0 (`0x438c82bc`) con `r5=2`. No hay un dato que ponga 0 **y** un r5 variable | V |
| **P2** r5 calculado por función nativa | **NO cableado**: la aritmética existe en la vista en directo (`0x437b27b8`: `r5 = max(VTS − τ/line, mín)`), pero la foto usa el campo `cap+0x5dc` (constante 1). No hay función de foto que lo calcule | V |
| **P3** reutilizar `+0x30` sin duplicar cálculos | **NO**: su salida es una posición 0..4095 en otro bloque; no fija r5 | V (emulación) |
| **P4** cambio solo en foto | **Parcial**: el único sitio específico de foto es `0x438c82b6` (modo 2/3) y `0x438c82bc`; parchear `SetExposure` (`0x436d6fb6`) afecta a **todas** las llamadas (LV, vídeo, AF) | V |
| **P5** conservar vídeo/AF/ráfaga | **NO demostrado**: el parche global de ShutMode 0 se aplicó en T046–T050 con LV y foto, pero no se probó vídeo/AF/ráfaga a otras velocidades | N |

**Buffers preparados que se sobrescriben:** sí. `0x437f8a50` reescribe `cap+0x64c` y `cap+0x6bc`
en cada captura; el registro de cuadro se limpia (`memset 0x158`) al entrar en `0x437b43b4`.
Una inyección de datos debe caer **después** del constructor del registro y **antes** de
`0x438c829c`; no hay una dirección estable ni una ventana determinista. No se propone.

---

## 11. Diseño de T051 (no ejecutado)

**Objetivo:** medir si B (ShutMode 0, r5=1) es igual a C (ShutMode 0, r5 calculado) y si A
(ShutMode 3) difiere; validar la ley y la precisión de 1/8000.

**Precondiciones:** 3.23 instalado; RAW+JPEG; ISO 100; M; trípode; escena fija con luz estable;
telnet/adb del PC; **sin** persistencia.

**Brazos (ABBAAB, 6 disparos por velocidad):**
- A: sin parche.
- B: solo `0x436d6fb6` (`91f80990` → `4ff00009`), `r5` intacto.
- C: `0x436d6fb6` + `0x436d7000` (`28125ffa85fe` → `hi 20 4ff0 lo 0e`) con
  `r5 = 4219 − round(µs/15,2)`; solo si `r5 ≥ 2`.

**Velocidades:** 1/8000, 1/4000, 1/1000, 1/250, 1/60, 1/15 (C solo si `r5 ≥ 2`, es decir T ≤ ~64 ms; 1/15 = 66,7 ms queda fuera; B/A también 1/8).

**Medición:** exposure por bandas de filas (E25-10); uniformidad (σ/µ entre octavos); tiempo
efectivo = 1000·RAW/escena con referencia de la misma tanda; comparar A/B/C.

**Criterios:** B ≈ cuadro completo (±5 %) y C ≈ nominal (±5 %, uniforme ±5 %) → r5 necesario;
B ≈ C → ShutMode bastaría (no esperado); C fuera de rango para T > ~64 ms → límite confirmado.

**Seguridad:** comprobar bytes originales; guardián `sh` que revierte ambos sitios si no aparece
el aviso en 25 s; aplicar ambos sitios en **un solo** comando; revertir en un solo comando y
verificar; abortar a los 45 s; no tocar NVRAM/NAND; no flashear. **No ejecutar sin autorización
expresa.**

---

## 12. Veredictos

| # | Pregunta | Respuesta | Tipo |
|---|---|---|---|
| A | ¿El método `+0x30` recibe la velocidad real de fotografía? | **NO demostrado** (recibe un código de posición de cuadro/lectura; el Tv va a un flag/log, no al bloque) | falta de evidencia; corrige E25-14 |
| B | ¿Se identificó su productor? | **NO** (se identificó el campo `[ajustes+0x164]`, el constructor `0x437b061c` y el escritor del bloque, no quién deriva ese campo del Tv) | falta de evidencia |
| C | ¿Se identificaron todos los campos relevantes de los dos bloques? | **NO** (los consumidos por ambas funciones sí; el resto de los 16 B y los 0x5c B del registro no) | falta de evidencia |
| D | ¿El método `+0x30` modifica el mismo parámetro/comando de integración que `SetExposure`? | **NO** (`blk+0x50..0x57` vs `blk+0x66..0x6c`; campos y escalas distintos) | contradicción demostrada |
| E | ¿ShutMode 0 con r5=1 puede dar tiempos distintos solo mediante `+0x30`? | **NO** (el bloque `+0x30` es idéntico y no toca r5; T046: con el mismo r5, 1/250 y 1/30 dan la misma exposición) | contradicción demostrada (T046) |
| F | ¿Es necesario modificar r5 además de ShutMode? | **SÍ** (B ≈ 64–65 ms por la ley; C sigue la velocidad; T051 mide B) | V/I |
| G | ¿Hay una función reutilizable que calcule r5 desde la velocidad de foto? | **NO** (la aritmética existe en LV `0x437b27b8`, no cableada a la foto; la foto usa `cap+0x5dc`) | falta de evidencia |
| H | ¿Puede seleccionarse ShutMode 0 por datos sin sobrescribir instrucciones? | **NO** con efecto útil (el byte `0x43eedeca` y la ruta 2/3 existen, pero fijan `r5=2`; no hay dato para r5 variable) | falta de evidencia |
| I | ¿Hay un camino demostrado que preserve vídeo, AF y funcionamiento normal? | **NO** (el parche global afecta a todas las llamadas; el específico de foto no está probado) | falta de evidencia |
| J | ¿Se identificó un mecanismo electrónico para superar un cuadro? | **NO** (sin acumulador; bulb usa las mismas primitivas; sin cuadro más largo) | falta de evidencia (no imposibilidad) |
| K | ¿La emulación reproduce coherentemente A, B y C? | **SÍ en escrituras** (A/B/C: +0x30 idéntico; r5/ShutMode distintos). **NO en tiempo físico** (no se emula el sensor) | V (software) |
| L | ¿La evidencia permite diseñar una T051 reversible? | **SÍ** (§11) | V |
| M | ¿Hay base para un parche persistente seguro? | **NO** (E24-04/E25-04: sin recuperación independiente; BIONZ no tiene reempaquetador reproducible) | falta de evidencia |

Un **NO** por falta de evidencia no es una prueba de imposibilidad física.

---

## 13. Recomendación técnica para terminar E25-12

1. **Corto plazo (reversible, sin PC persistente):** mantener el modo silencioso de T050
   (PC + guardián + RAM), añadiendo: (a) esperar a que la velocidad se estabilice antes de
   calcular `r5`; (b) limitar a `T ≤ 1/15`; (c) comprobar `r5 ≥ 2`; (d) medir 1/8000 con la
   calibración de la misma tanda.
2. **Para eliminar el PC:** la modificación mínima es **en BIONZ**, en la ruta de foto:
   - seleccionar ShutMode 0 solo en foto (p. ej. en `0x438c82b6` o en el byte `0x43eedeca`);
   - calcular `r5` desde el Tv de la foto (`[cap+0x1198+0x162]` o el campo equivalente) con la
     aritmética ya existente (`0x4382fa94` → µs; `r5 = VTS − líneas`, VTS de `0x4385de94`);
   - escribir `r5` en `cap+0x64c+0` (o en `record+0x64`) **después** de `0x437f8a50` y antes de
     `SetExposure`; la ventana es estrecha y exige código, no datos.
   No instalar: no hay recuperación independiente (E24-04) y `nflasha3` no tiene reempaquetador
   reproducible (E25-11 §5).
3. **> 65 ms:** no seguir con `r5`. Si se reabre, la única vía es demostrar que el bulb
   (`0x4381106c` → `0x43ae935a`) usa un modo de sensor con cuadro más largo o acumulación; hoy
   no hay evidencia.
4. **Calibración:** luz controlada y referencias por tanda; el sesgo ±20–25 % de T050 no es de
   cuantización.

---

## 14. Pruebas y regresiones

- `tests/test_e25_15_shutmode.py`: bytes de la secuencia, constructores, bloques, destinos,
  emulación A/B/C y aritmética de 1/8000. Se omite si falta el firmware (no cuenta como
  verificación).
- `tests/test_e25_14_exposicion.py`: 13 pruebas, se ejecutan también.
- `scripts/e25_15_emu.py`: arnés reproducible; `analysis/e25-15/emulacion.json` como evidencia.

---

## 15. Límites de esta sesión

- No se siguió el bloque `blk+0x50..0x6c` hasta el registro físico del sensor ni el transporte
  (el commit `0x43ad911c` es una llamada virtual; el objeto es de runtime).
- No se identificó el escritor último de `[ajustes+0x164]` ni su relación exacta con el Tv.
- No se emuló el constructor completo `0x437b43b4` (requiere el objeto de ajustes y la pila de
  parámetros); el código de posición real por velocidad queda sin valor numérico.
- La emulación no prueba comportamiento eléctrico; las conclusiones de tiempo se apoyan en
  T046/T047 (mediciones) y en la ley lineal.
- No se ejecutó T051 ni se tocó la cámara.
