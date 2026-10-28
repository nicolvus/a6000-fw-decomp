# E25-16 — Cálculo autónomo de `r5` en BIONZ para fotografía silenciosa

**Fecha:** 28-10-2026 · **Firmware:** `av-cam.bin` 3.21, SHA-256 `b60c845c…e56bb9`
**Alcance:** análisis estático y emulación *offline*. No se conectó la cámara, no se leyó/escribió
RAM/NVRAM/NAND, no se flasheó nada y no se ejecutó firmware en hardware.
**Pregunta:** ¿cómo calcula BIONZ el `r5` (líneas de integración) de una foto a partir del Tv real,
sin PC, para que la foto silenciosa sea uniforme y siga la velocidad?

**Respuesta corta:** BIONZ ya tiene un productor nativo de `r5`: `0x4383fa40`. Lo llaman los dos
constructores de la foto (normal `0x437b43b4` en `0x437b46d0` y EFCS `0x43841070` en `0x438417c0`).
Con los campos del registro (`Tv` en `+0xf6`, período de línea en `+0xc`, VTS en `+0x20`) calcula
`r5` y escribe además `ShutMode = 0` en `+0x6d`. El bloque se copia a `cap+0x64c` (`0x4383fd6c`) y
llega a `SetExposure` (`0x436d6320` → vtable `+0x28` → `0x436d6f6c`). La emulación con VTS = 4219
reproduce T047 dentro de ±1 línea. **No se hardcodea 4219:** el diseño usa el campo VTS del propio
registro; 4219 es la calibración medida, y la diferencia con el VTS de `0x4385de94` (4266) se
documenta como límite. **1/15, >1 cuadro, bulb y 30 s quedan fuera.**

---

## 0. Resumen de la cadena

```
settings+0x162  (Tv, código 1/256 EV; 0x1000 = 1 s)
   │  0x437b4340 (tabla de modo 9) y 0x437b4662/0x437b4670
   ▼
record+0xf6     (Tv de la foto)
   │  0x4383fa40(record, settings)   ← productor nativo, ya usado por normal y EFCS
   │     Tv → 0x4382fa94 (µs Q8) → / record+0xc (período de línea Q8) → líneas
   │     frame = max(record+0x20, 0x825700/record+0xc/settings+0x4b8)  (truncante)
   │     r5 = max(frame − líneas, record+0x1c)
   ▼
record+0x64 = r5          record+0x6d = 0 (ShutMode)
   │  0x4383fd6c (copia 16 B record+0x64..0x73)
   ▼
cap+0x64c (param de SetExposure: +0 = r5, +9 = ShutMode)
   │  0x438c828c: 0x437f8a50 (construye) → 0x436d6320 (vtable +0x28)
   ▼
0x436d6f6c SetExposure → blk+0x50/0x52/0x54/0x56/0x57
```

La foto actual no usa el productor porque el constructor tiene una compuerta (`cap+0x11b0`,
`0x437b46c6`) y, cuando está cerrada, el registro conserva `r5 = 1` (T032/T046). El cálculo existe;
lo que falta es **ejecutarlo en la ruta de foto** (C1/C3, §7).

---

## 1. Método y evidencia

- **REA primero:** sesión `analysis/rea-independent/run/e2516.sock` (daemon abierto durante el
  hito), consultas por lotes de `0x4383fa40`, `0x4385de94`, `0x437b4340`, `0x437f8a50`,
  `0x438c828c` y sus llamadores. Ghidra histórico solo como contraste de bytes.
- **Bytes:** todas las direcciones se verificaron contra `analysis/rea-independent/input/av-cam.bin`
  (mismo SHA). Las pruebas de `tests/test_e25_16_r5_autonomo.py` fallan si el binario cambia.
- **Emulación:** `scripts/e25_16/emu_core.py` (Unicorn 2.1.4, Thumb, stubs documentados) y
  `scripts/e25_16/emular_r5.py`. Evidencia: `analysis/e25-16/emulacion.json`.
- **Sin cámara:** no se ejecutó T052; el diseño de §8 es una propuesta.

Marcas usadas: **V** = verificado por bytes/emulación; **I** = inferencia con evidencia;
**N** = no verificado.

---

## 2. De dónde sale el Tv de la foto

### 2.1 Escritor de `[settings+0x162]`

`0x437b4340` es un envoltorio del constructor. Si `[r1+0x294] == 9` (modo 9), elige una entrada de
una tabla global según `r0` (0, 1 o 2) y la escribe en `[r3+0x162]`:

```
0x437b4344  ldr.w r3,[r1,#0x294]
0x437b434e  cmp   r3,#9
0x437b4354  bne   0x437b4358
0x437b4382  ldr   r3,[pc,#0x2c]        ; tabla global
0x437b4384  cmp   r5,#1
0x437b4392  ldrh.w r3,[r3,#0x94]       ; índice 1
0x437b4398  ldrh.w r3,[r3,#0x98]       ; índice 2
0x437b439e  ldrh.w r3,[r3,#0x96]       ; índice 0
0x437b43a2  strh.w r3,[r4,#0x162]
```

Los índices 0/1/2 y el modo 9 no tienen semántica demostrada en este hito; se documentan como
**V** de código, **N** de significado. Lo importante es que el Tv de la foto se escribe en
`settings+0x162` desde una tabla, no que se lea de un registro de la app.

### 2.2 Copia al registro de foto

En el constructor `0x437b43b4` (el que usa la foto normal), con `fp` = objeto de ajustes y `r5` =
registro global:

```
0x437b465e  ldrh.w r1,[fp,#0x160]
0x437b4662  ldrh.w r2,[fp,#0x162]      ; Tv
0x437b4666  ldrh.w r3,[fp,#0x15e]
0x437b466a  strh.w r1,[r5,#0xfa]
0x437b4670  strh.w r2,[r5,#0xf6]       ; Tv -> record+0xf6
0x437b4674  strh.w r3,[r5,#0xf8]
```

**V** por bytes (`bbf86221`, `bbf85e31`, `a5f8fa10`, `a5f8f620`, `a5f8f830`).

### 2.3 `cap+0x1198` no es un bloque de datos

La recomendación de E25-15 mencionaba `[cap+0x1198+0x162]`. Eso era una **dirección de conveniencia**,
no una desreferenciación demostrada. La ruta real es:

```
0x437f8a8e  add.w r5,r4,#0x1180
0x437f8a92  add.w r5,r5,#0x18          ; r5 = cap+0x1198 (primer argumento)
0x437f8aa4  bl    0x4383fd6c           ; r0=cap+0x1198, r1=cap+0x20, r2=sp+4, r3=sp+0x6c
...
0x4383fd98  ldr.w r1,[r6,#0x1b8]       ; r6 = cap+0x20
0x4383fd9c  ldr.w r0,[r6,#0x1c0]
0x4383fda0  bl    0x4383fb6c           ; -> registro global (0x43ea5b4c / 0x43eee770)
0x4383fdaa  add.w r3,r0,#0x64
0x4383fdb0  ldm   r3,{r0,r1,r2,r3}     ; 16 B de record+0x64
```

`cap+0x1198` solo se usa como contexto (`r1` de `0x43859944` al final); **no** se lee `+0x162` desde
ahí. El registro global se selecciona con `[cap+0x1b8]`:

| Accesor | Selector de banco / `[cap+0x1b8] & 1` | registro |
|---|---|---|
| `0x4383fb6c` | banco A (`0x43b08d42` = 0) | `0x43ea5b4c` |
| `0x4383fb6c` | banco B, bit 0 = 0 | `0x43ea5b4c` |
| `0x4383fb6c` | banco B, bit 0 = 1 | `0x43eee770` |

`0x4383fbc4` devuelve los ajustes (`0x43f79f94`) con el mismo selector. **V** por GOT
(`0x4401eee4 + 0x3764/0x6f18/0x1904`) y por la emulación de `0x4383fd6c`.

---

## 3. El productor nativo `0x4383fa40`

### 3.1 Desensamblado anotado

```
0x4383fa40  push.w {r4,r5,r6,r7,r8,sb,sl,lr}
0x4383fa44  mov    r4,r0                 ; r4 = record
0x4383fa46  ldr    r7,[r0,#0xc]          ; r7 = período de línea (Q8) o 0
0x4383fa48  ldrb.w r5,[r1,#0x4b8]        ; r5 = factor o 0
0x4383fa4c  cmp    r7,#0
0x4383fa4e  it eq / moveq r7,#1
0x4383fa52  ldr    r0,[pc,#0xa8]         ; 0x00825700
0x4383fa54  cmp    r5,#0
0x4383fa56  it eq / moveq r5,#1
0x4383fa5a  mov    r1,r7
0x4383fa5c  bl     0x4355faf0           ; 0x825700 / r7
0x4383fa60  mov    r1,r5
0x4383fa62  bl     0x4355faf0           ; / r5
0x4383fa66  ldrh   r6,[r4,#0x20]        ; r6 = VTS del registro
0x4383fa68  movw   r3,#0xc54            ; umbral 16 s
0x4383fa6c  cmp    r0,r6
0x4383fa6e  it hs / movhs r6,r0         ; r6 = max(VTS, 0x825700/r7/r5)
0x4383fa72  ldrh.w r0,[r4,#0xf6]        ; Tv
0x4383fa76  cmp    r0,r3
0x4383fa78  bhi    0x4383fa82           ; Tv > 0xC54 -> rama Q8
0x4383fa7a  bl     0x4382fac8           ; µs entero (Tv <= 0xC54)
0x4383fa7e  lsrs   r1,r7,#8             ; período de línea entero
0x4383fa80  b      0x4383fa88
0x4383fa82  bl     0x4382fa94           ; µs Q8 (Tv > 0xC54)
0x4383fa86  mov    r1,r7                ; período de línea Q8
0x4383fa88  bl     0x4355faf0           ; líneas = tiempo / período
0x4383fa8c  ldrh.w r8,[r4,#0x1c]        ; suelo de r5
0x4383fa90  add    r8,r0
0x4383fa92  mov    sb,r0                ; sb = líneas
0x4383fa94  cmp    r8,r6
0x4383fa96  it lo / movlo r8,r6         ; r8 = max(suelo+líneas, frame)
0x4383fa9a  bl     0x43a12ca8           ; predicado de cuadro extra
0x4383fa9e  cbz    r0,0x4383faa2
0x4383faa0  add    r8,r6                ; +1 frame (solo si el predicado)
0x4383faa2  mov    r0,r8
0x4383faa4  mov    r1,r6
0x4383faa6  bl     0x4355faf0           ; frame count -> r7 (16 bits)
0x4383faaa  uxth   r7,r0
0x4383faac  cbz    r7,0x4383fab2
0x4383faae  subs   r7,#1
0x4383fab0  uxth   r7,r7
0x4383fab2  mov    r1,r6
0x4383fab4  mov    r0,r8
0x4383fab6  bl     0x4355fd4c           ; resto
0x4383faba  rsb    sl,sb,r8             ; r5 = r8 - líneas
0x4383fabe  movs   r3,#0
0x4383fac0  strh.w r7,[r4,#0x68]        ; frames
0x4383fac4  uxth.w sl,sl
0x4383fac8  strh.w r3,[r4,#0x6a]
0x4383facc  str.w  sl,[r4,#0x64]        ; r5
0x4383fad0  strb.w r3,[r4,#0x6c]
0x4383fad4  strb.w r3,[r4,#0x6d]        ; ShutMode = 0
0x4383fad8  str.w  sb,[r4,#0xf0]        ; líneas
```

**V** por bytes (`c4f864a0`, `84f86c30`, `84f86d30`, `c4f8f090`, `40f65443`, `20f548f8`).

### 3.2 Fórmula equivalente

Con `record+0x1c = 0` (el registro se memseatea a cero en `0x437b441e..24`; no se localizó un
escritor de `+0x1c`), `record+0x20` = VTS y `settings+0x4b8 = 1`:

```
q8     = 0x4382fa94(Tv)                 ; µs × 256, para Tv > 0xC54
lines  = q8 / record+0xc                ; división truncante (0x4355faf0)
frame0 = 0x825700 / record+0xc          ; división truncante
frame0 = frame0 / settings+0x4b8        ; división truncante
frame  = max(record+0x20, frame0)
r5     = max(frame - lines, 0)
```

Para `Tv <= 0xC54` (exposiciones ≥ 16 s) usa `0x4382fac8` (µs entero) y `record+0xc >> 8`.
El umbral `0xC54` no es un límite de la foto normal: es el cambio de precisión para tiempos largos.

**No hay ninguna constante 4219 en el código.** 4219 es el VTS efectivo medido (T046/T047); el
firmware lee el VTS de `record+0x20`. La función `0x4385de94` (vista en directo) da 4266 para el
mismo período de línea; la diferencia de 47 líneas (0,71 ms) es el límite conocido de §5.3.

### 3.3 Quién la llama

| Llamador | Constructor | Condición | Estado |
|---|---|---|---|
| `0x437b46d0` | normal `0x437b43b4` | `[cap+0x11b0] != 0` (`0x437b46c6`) | **V** bytes |
| `0x438417c0` | EFCS `0x43841070` | `[objeto+0x15] == 1` (`0x438417b6`) | **V** bytes |

Ambos constructores son código vivo (no una función muerta): `0x437b43b4` tiene 4 llamadores
(`0x437f8948`, `0x437f89ec`, `0x43affec6`, `0x43afff26`) y `0x43841070` uno (`0x437f8816`).
En la foto medida (T046/T047) la compuerta estaba cerrada y el registro conservó `r5 = 1`; por eso
la foto no seguía la velocidad. **I** (la compuerta es la que decide; su semántica exacta no está
resuelta).

---

## 4. Entrega a `SetExposure`

`0x437f8a50` (llamada desde `0x438c829c`) construye dos bloques:

| Bloque | Constructor | Contenido |
|---|---|---|
| `cap+0x64c` | `0x4383fd6c` (16 B) + cola | `param+0` = r5, `param+4` = ancho, `param+6` = alto, `param+9` = ShutMode |
| `cap+0x6bc` | `0x43840150` / `0x437b21b8` | posición de lectura (método `+0x30`) |

La copia de `record+0x64..0x73` a `cap+0x64c` es **V**:

```
0x4383fd6c  ... 
0x4383fda0  bl    0x4383fb6c        ; registro global
0x4383fdaa  add.w r3,r0,#0x64
0x4383fdb0  ldm   r3,{r0,r1,r2,r3}  ; 16 B
0x4383fdb2  stm.w lr,{r0,r1,r2,r3}  ; -> *param_3 (stack; luego cap+0x64c)
```

Después, la secuencia de foto `0x438c828c` hace:

```
0x438c829c  bl 0x437f8a50            ; construye cap+0x64c y cap+0x6bc
0x438c8302  add.w r1,r4,#0x640
0x438c8306  adds  r1,#0xc            ; r1 = cap+0x64c
0x438c830c  bl 0x436d6320            ; envoltorio: [obj] -> vtable +0x28
0x438c8314  add.w r1,r4,#0x6b0
0x438c8318  adds  r1,#0xc            ; r1 = cap+0x6bc
0x438c831e  bl 0x436d6398            ; envoltorio: vtable +0x30 (SetRead)
```

`0x436d6320` no es SetExposure: carga `r0=[r0]`, `r3=[r0]`, `r3=[r3+0x28]`, `blx r3`; el destino
real es `0x436d6f6c` (vtable `+0x28`, E25-15). **V**.

`SetExposure` consume `param+0` (`0x436d6fae ldrh r5,[r1]`) y `param+9`
(`0x436d6fb6 ldrb.w r9,[r1,#9]`); escribe `blk+0x52` (r5) y `blk+0x57` (ShutMode). **V**.

`+0x30` (`0x436d7e08`) escribe `blk+0x66..0x6c` y no toca `blk+0x52`; su bloque es un código de
posición, no la integración (E25-15). **No se repite aquí.**

---

## 5. Emulación y comparación con las medidas

### 5.1 Arnés

`scripts/e25_16/emu_core.py` mapea el firmware en `0x43541000`, una pila, un scratch y un bloque de
configuración. Los stubs sustituyen funciones externas (logs, colas, getters) por valores fijos:

| Stub | Valor | Motivo |
|---|---|---|
| `0x43b08d42` | 0 | selector de banco A/B → banco A |
| `0x438fb300` | 0 | estado que fuerza la rama normal de `0x4385de94` |
| `0x43a12ca8` | 0 | predicado de cuadro extra → sin extra |
| `0x4355fd4c` | 0 | resto auxiliar |
| `0x439c5a04` / `0x439c5320` | 0 | memset/memcpy no emulados (destino fuera de lo comparado) |

`emular_r5.py` añade `Harness.native_r5(tv)`: crea un registro sintético con `record+0xc = 3891`,
`record+0x1c = 0`, `record+0x20 = 4219`, `record+0xf6 = Tv`, `settings+0x4b8 = 1`, ejecuta
`0x4383fa40` y lee `record+0x64`. **No es una reimplementación:** es la función del firmware.

### 5.2 Tabla (VTS = 4219; 1/256 EV; línea 15,2 µs)

| Vel. | Tv | µs | líneas | r5 (4219) | r5 nativo | T047 | Δ | error |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1/8000 | `1cf7` | 125 | 8 | 4211 | 4211 | — | — | −2,7 % (cuantización) |
| 1/4000 | `1bf7` | 250 | 16 | 4203 | 4203 | 4203 | 0 | +1,3 % |
| 1/2000 | `1af7` | 500 | 32 | 4187 | 4187 | — | — | −2,7 % |
| 1/1000 | `19f7` | 1000 | 65 | 4154 | 4154 | 4153 | +1 | −0,2 % |
| 1/500 | `18f7` | 2001 | 131 | 4088 | 4088 | — | — | −0,4 % |
| 1/250 | `17f7` | 4002 | 263 | 3956 | 3956 | 3956 | 0 | −0,8 % |
| 1/125 | `16f7` | 8005 | 526 | 3693 | 3693 | — | — | −0,1 % |
| 1/60 | `15e8` | 16674 | 1097 | 3122 | 3122 | 3122 | 0 | −0,5 % |
| 1/30 | `14e8` | 33348 | 2194 | 2025 | 2025 | — | — | +0,05 % |
| 1/15 | `13e8` | 66696 | 4388 | −169 | **0** | — | — | saturado |
| 1/8 | `1300` | 125000 | 8224 | −4005 | **0** | — | — | saturado |
| 1 s | `1000` | 1000000 | 65792 | −61573 | **0** | — | — | saturado |
| 10 s | `0cae` | 9988769 | 657189 | −652970 | **0** | — | — | saturado |
| 30 s | `0b18` | 29986572 | 869081 | −864862 | **0** | — | — | saturado |

- **T047:** 0,24 / 0,99 / 4,03 / 16,75 ms; el nativo da 4203 / 4154 / 3956 / 3122, es decir
  0 / +1 / 0 / 0 líneas. **V**.
- **1/15:** el nativo no devuelve un r5 negativo: satura a 0. Con r5 = 0 la foto sale negra (T046),
  no con 66,7 ms. Por eso 1/15 **no es compatible**. **V** emulación + T046.
- **1/30:** 33,35 ms, dentro de un cuadro (64,1 ms); sí es representable. Es el límite práctico.
- **1/8000:** 8 líneas = 121,6 µs, −2,7 %; el truncamiento de líneas domina. No es calibración.

### 5.3 Sensibilidad al VTS

Si el registro llevara el VTS de `0x4385de94` (4266) en lugar de 4219, el nativo daría 47 líneas
más y la exposición física (VTS real 4219) sería **47 × 15,2 µs = 0,71 ms más corta**:

| Vel. | r5 con 4266 | exposición real | error |
|---|---:|---:|---:|
| 1/8000 | 4258 | negativa (clamp) | negro |
| 1/4000 | 4250 | negativa (clamp) | negro |
| 1/1000 | 4201 | 0,27 ms | −72 % |
| 1/250 | 4003 | 3,28 ms | −18 % |
| 1/60 | 3169 | 15,96 ms | −4,3 % |
| 1/30 | 2072 | 32,6 ms | −2,1 % |

Por eso **el campo `record+0x20` es el dato crítico**: no se puede sustituir por 4219 a ciegas ni
por 4266 a ciegas. La prueba T052 (§8) lo lee antes de escribir nada. **N** (valor real en la foto).

### 5.4 Separación de errores

| Fuente | Magnitud | Dónde |
|---|---|---|
| Cuantización de línea | 15,2 µs; 8 líneas a 1/8000 (−2,7 %), 16 a 1/4000 | `0x4355faf0`, truncamiento |
| Cuantización de Tv | 1/256 EV | código `0x1xxx` |
| Conversión Tv→µs | `0x4382fac8` trunca a µs; `0x4382fa94` conserva Q8 | dos ramas de `0x4383fa40` |
| Calibración/VTS | 4219 vs 4266 → 0,71 ms | `record+0x20` vs `0x4385de94` |
| Escena/tanda | ±20–25 % en T050 | no es de esta cadena |

T047 cae dentro de ±1,3 %, que es del orden de la cuantización; el sesgo de T050 (±20–25 %) es de
calibración de luz/referencia, no de la conversión. **V/I**.

---

## 6. Límites duros

1. **Un cuadro:** el registro y `SetExposure` trabajan con `r5` dentro de un cuadro. La exposición
   máxima es ~64 ms (4219 × 15,2 µs). 1/15 = 66,7 ms queda fuera. **V** emulación + T046.
2. **>1 cuadro:** `0x4383fa40` tiene una rama de “cuadro extra” (`0x43a12ca8` → `r8 += r6` y
   `record+0x68` = frames), pero el predicado no está identificado y no se demostró acumulación
   del sensor. **No se usa.** **N**.
3. **Bulb:** la ruta `0x4381106c` usa `SetExposure` con una plantilla de runtime; no hay mecanismo
   demostrado para superar un cuadro. **N** (no imposibilidad).
4. **30 s:** `0x4382fa94` satura en `0xC00` (≥16 s) y el nativo devuelve 0; además >1 cuadro. **V**.
5. **1/8000:** representable con r5 = 4211, pero −2,7 % por cuantización; no se declara ±5 % sin
   calibración. **V/I**.

---

## 7. Puntos de intervención C1–C4

| Punto | Dónde | Alcance | Ventaja | Riesgo | Veredicto |
|---|---|---|---|---|---|
| **C1** | `cap+0x11b0` (compuerta `0x437b46c6`) | constructor normal | dato, no código; el nativo ya está cableado | semántica de la compuerta desconocida; puede afectar a otros modos | **candidato**, **N** |
| **C2** | dentro de `0x4383fa40` (p. ej. forzar VTS o el período) | normal + EFCS | una sola función | cambia todos los modos que la usan; duplica la decisión de VTS | **rechazado** para la primera prueba |
| **C3** | tras `0x437f8a50` (`0x438c82a0`) y antes de `0x436d6320` (`0x438c830c`) | solo secuencia de foto | ventana estrecha; no toca Live/Video/AF; puede usar la función nativa | requiere cueva de código y copia del registro; no es un dato puro | **recomendado** (lógico) |
| **C4** | dentro de `0x436d6f6c` (SetExposure) | todas las llamadas | central | afecta a Live/Video/AF/bulb; imposible de acotar | **rechazado** |

### 7.1 C3: diseño lógico (sin parche binario)

Objetivo: que `cap+0x64c` llegue a `SetExposure` con el `r5` de la velocidad y `ShutMode = 0`, solo
en la foto. La secuencia:

1. En `0x438c82a0` (justo después de `bl 0x437f8a50`), guardar `r0-r3, lr`.
2. Obtener el registro y los ajustes como lo hace `0x4383fd6c`:
   `rec = 0x4383fb6c([cap+0x1c0], [cap+0x1b8])`,
   `set = 0x4383fbc4([cap+0x1c0], [cap+0x1b8])`.
3. Copiar el registro a un **scratch** (0x158 B) para no modificar el global; ejecutar
   `0x4383fa40(scratch, set)`. Así se obtiene el `r5` y el `ShutMode` con la aritmética del
   firmware, sin reimplementarla y sin tocar `record+0x6d`.
4. Leer `r5 = [scratch+0x64]`, `sm = [scratch+0x6d]`.
5. Si `r5 >= 2` y `Tv` está en el rango 1/8000..1/30, escribir `[cap+0x64c] = r5` y
   `[cap+0x655] = 0`; si no, no escribir nada (la foto sigue con el comportamiento normal).
6. Restaurar registros y volver a `0x438c82a4`.

No se entrega un binario ni un parche persistente: los pasos 1–6 son el **contrato lógico** que una
cueva de código o un harness de RAM tendría que implementar. La copia a scratch evita el efecto
lateral de `0x4383fa40` sobre el registro global (`+0x6d`), que es la objeción principal a C1/C2.

**Reversibilidad:** si se prueba en RAM, un apagado/encendido borra la cueva y el registro vuelve a
su valor de arranque; no hay escritura en NAND. **Seguridad real:** no se debe instalar en firmware:
BIONZ no tiene recuperación independiente demostrada (E24-04/E25-04) y `nflasha3` no tiene
reempaquetador reproducible. La corrección lógica no es un firmware instalable.

---

## 8. Prueba física propuesta (T052, reversible, no ejecutada)

**Fase A — solo lectura (sin escribir nada):** con el harness de RAM de T050, en modo silencioso y
para 1/4000, 1/250 y 1/60, leer:

| Campo | Dirección | Qué confirma |
|---|---|---|
| `record+0xf6` | registro global + `0xf6` | Tv de la foto |
| `record+0xc` | + `0xc` | período de línea Q8 (esperado 3891) |
| `record+0x20` | + `0x20` | VTS efectivo (4219 vs 4266) |
| `record+0x1c` | + `0x1c` | suelo de r5 (esperado 0) |
| `settings+0x4b8` | ajustes + `0x4b8` | factor (esperado 1) |
| `cap+0x11b0` | cap + `0x11b0` | compuerta del constructor |

Criterio: si `record+0x20 == 4219`, el nativo debe dar exactamente la tabla de §5.2. Si da 4266,
**detener**: el firmware estaría usando un VTS distinto del físico y el diseño C3 necesitaría
corrección de calibración, no un simple `r5`.

**Fase B — escritura RAM en C3:** solo si A pasa. Escribir `cap+0x64c` (r5) y `cap+0x655` (0) entre
`0x437f8a50` y `0x436d6320`, capturar RAW y medir la exposición por filas como T046/T047.
Criterios de éxito:

- `r5` calculado = `r5` nativo (±1 línea).
- Exposición media dentro de ±5 % del objetivo en 1/4000, 1/250 y 1/60.
- Uniformidad por filas dentro de ±5 %.
- Live/Video/AF sin cambios; apagado/encendido revierte; bytes de `av-cam` intactos.

**Parada:** cualquier `r5 < 2`, lectura de VTS distinta de la esperada, error de captura o
diferencia >5 % que no se explique por calibración. No se prueba 1/15, bulb ni 30 s.

---

## 9. Veredictos A–P

| # | Pregunta | Veredicto | Base |
|---|---|---|---|
| A | ¿Existe un cálculo autónomo de `r5` en BIONZ a partir del Tv de la foto? | **SÍ, lógicamente** (productor nativo `0x4383fa40`, llamado por los dos constructores) | V bytes/emulación; falta prueba física |
| B | ¿De dónde sale el Tv? | `settings+0x162` (tabla de modo 9, `0x437b4340`) → `record+0xf6` (`0x437b4662/70`) | V |
| C | ¿Se demostró la desreferenciación real o se asumió `cap+0x1198`? | **Real:** `0x4383fd6c` → `0x4383fb6c` → `record+0x64`; `cap+0x1198` es solo `param_1` | V |
| D | ¿El conversor usa el VTS del firmware o una constante? | **El campo `record+0x20`**; no hay 4219 en el código. El valor real de ese campo no se verificó | V código / N valor |
| E | ¿Qué VTS es el efectivo? | 4219 medido (T046/T047); 4266 desde `0x4385de94`; Δ47 líneas = 0,71 ms | V/I |
| F | ¿La cadena reproduce T047? | **SÍ**, 0/+1/0/0 líneas (1/4000, 1/1000, 1/250, 1/60) | V emulación |
| G | ¿1/15 es compatible? | **NO**: 66,7 ms > 64,1 ms de cuadro; el nativo satura a 0 (negro) | V |
| H | ¿Se puede superar un cuadro? | **NO demostrado**; la rama de cuadro extra existe pero el predicado no se identificó | N |
| I | ¿Bulb? | **NO demostrado**; misma primitiva, sin acumulador | N |
| J | ¿30 s? | **NO**: clamp `>0xC00` en `0x4382fa94` y >1 cuadro | V |
| K | ¿`+0x30` (SetRead) ajusta la integración? | **NO**: escribe `blk+0x66..0x6c`, no `blk+0x52` (E25-15) | V |
| L | ¿Dónde intervenir? | **C3**: tras `0x437f8a50`, antes de `0x436d6320`; C1 es candidato de dato; C2/C4 rechazados | V/I |
| M | ¿Afecta a Live/Video/AF? | C3 solo en la secuencia de foto; la copia a scratch evita tocar el registro global | I |
| N | ¿Reversibilidad y seguridad real? | **RAM sí; firmware no**: sin recuperación independiente ni reempaquetador | V política |
| O | ¿Se separan cuantización, conversión y calibración? | **SÍ**: línea 15,2 µs; Tv 1/256 EV; VTS 4219/4266; escena T050 ±20–25 % | V/I |
| P | ¿Qué queda NO VERIFICADO? | Valor real de `record+0x20`/`+0xc`/`+0x1c`; escritor de `+0x20`; prueba física; efecto de la compuerta; >1 cuadro/bulb/30 s | N |

Un **NO** por falta de evidencia no es una prueba de imposibilidad física.

---

## 10. Pruebas y evidencia

- `tests/test_e25_16_r5_autonomo.py`: **29 pruebas**, todas verdes. Cubren:
  - SHA del firmware; bytes de la copia Tv→`record+0xf6`; compuerta y llamada al nativo;
  - escrituras `+0x64/+0x6c/+0x6d/+0xf0`; umbral `0xC54`; constantes `0x825700`;
  - escritor de Tv `0x437b4340` y sus dos llamadores;
  - `cap+0x1198` como argumento, no bloque; desreferenciación `0x4383fd6c`;
  - `Tv→µs` (8 velocidades), `0x4382fa94` con clamp, VTS nativo 4266;
  - `0x4383fa40` nativo contra T047 (±1 línea), saturación a 0 en 1/15..30 s;
  - SetExposure recibe `blk+0x52`/`blk+0x57`; `cap+0x64c` solo lo escribe `0x437f8a50`;
  - ambos constructores llaman al nativo.
- `scripts/e25_16/emu_core.py`, `scripts/e25_16/emular_r5.py`; `analysis/e25-16/emulacion.json`.
- Regresiones: `tests/test_e25_14_exposicion.py`, `tests/test_e25_15_shutmode.py` y E25-16:
  **59 pruebas verdes** (13 + 17 + 29 en la ejecución conjunta).
- Comando: `python3 -m pytest tests/test_e25_14_exposicion.py tests/test_e25_15_shutmode.py tests/test_e25_16_r5_autonomo.py -q`.

---

## 11. Límites de esta sesión

- No se leyó el registro en ejecución: `record+0x20`/`+0xc`/`+0x1c` son **N**; la emulación usa
  4219/3891/0 porque es lo que reproduce T047, no porque se haya leído.
- No se identificó el escritor de `record+0x20` ni la semántica de la compuerta `cap+0x11b0`.
- No se siguió el bloque `blk+0x50..0x57` hasta el registro físico del sensor ni el transporte.
- No se ejecutó T052; no se tocó la cámara.
- No se entrega parche ni firmware instalable. La corrección lógica de C3 no cambia la conclusión
  de E24-04/E25-04: un firmware BIONZ persistente sigue sin recuperación independiente demostrada.

---

## 12. Recomendación

1. **No instalar nada.** Mantener el modo silencioso de T050 (PC + guardián + RAM) como única vía
   probada.
2. **Antes de escribir:** ejecutar la fase A de T052 y confirmar `record+0x20`, `+0xc`, `+0x1c`,
   `settings+0x4b8` y `cap+0x11b0`. Sin esos valores, cualquier `r5` es una suposición.
3. **Si A confirma 4219/3891/0/1:** implementar C3 en RAM (scratch + `0x4383fa40` + copia a
   `cap+0x64c`), solo para 1/8000..1/30, con guardas `r5 ≥ 2`; medir y revertir.
4. **Si A da 4266 u otro VTS:** no hardcodear 4219; investigar el escritor de `record+0x20` o
   corregir la calibración en el punto de copia, y volver a medir.
5. **>1 cuadro, bulb y 30 s:** no seguir con `r5`; solo reabrir si se demuestra acumulación o un
   modo de sensor con cuadro más largo (E25-14/E25-15 siguen vigentes).
