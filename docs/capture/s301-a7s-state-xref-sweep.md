# S301 — mismo barrido en la A7S fw3.20 y diferencias con la A6000

Segunda sesión del carril B. Repite el barrido de S300 sobre el `av-cam.bin` de la **A7S
fw3.20** (SHA `b857d338…5103e`) para comparar el estado del imager y los gates `+3`/`+6`.
La A7S es la cámara de la misma generación que **sí** tiene obturador silencioso, así que
cualquier diferencia de estado es candidata a explicar esa función.

**Resultado:** los gates `+3`/`+6` son **idénticos** en ambas cámaras (mismo dumper,
mismas máscaras, 8 lecturas cada uno, cero escritores), por lo que **no** son el
mecanismo del silent shutter. La diferencia está en el resto del estado: la A7S tiene
**11 campos que la A6000 no lee** y **4 escrituras que la A6000 no tiene**, concentradas
en el clúster `+0xde..+0xea` y en `+0xae`.

## 1. Localización del objeto de estado en la A7S

No había dirección publicada para el estado de la A7S. Se derivó del propio dumper
(la función que en la A6000 es `FUN_43858338`), localizado por sus bytes de gate:

| Paso | Valor | Cómo se obtuvo |
|---|---|---|
| Patrón de gate `+3 & 2` | `f3 78 13 f0 02 0f 08 d0` en `0x437e09ec` | búsqueda de bytes (1 ocurrencia) |
| Prólogo del dumper | `0x437e0974` | `push.w {r4,r5,r6,r7,r8,sb,sl,lr}` + misma estructura |
| Base GOT | `0x44024540` | `ldr.w r8,[pc,#0x10]` @`0x437e097a` + `add r8,pc` @`0x437e0980` |
| Slot del estado | `0x440251e4` | `ldr.w r3,[pc,#0xb40]` @`0x437e09b6` → offset `0xca4` |
| **Puntero al estado** | **`0x43f7bce6`** | contenido del slot: `e6 bc f7 43` |
| Entrada en tabla de punteros | `0x43ff928c` | segunda (y última) aparición del literal `0x43f7bce6` |

Igual que en la A6000, **solo hay dos literales absolutos** con el puntero en todo el
blob (slot GOT y tabla), y los bytes del objeto están a cero en la imagen. La tabla que
lo contiene va de `0x43ff9244` a `0x43ff9498` (150 entradas) y el estado ocupa el
**índice 18**, la misma posición que en la tabla de la A6000 (`0x43ff3200`, 148
entradas, índice 18). Esa correspondencia estructural respalda que `0x43f7bce6` es el
objeto homólogo (INFERENCIA fuerte, no semántica probada).

## 2. Cobertura y clases

| Métrica | A6000 fw3.21 (S300) | A7S fw3.20 (S301) |
|---|---:|---:|
| Xrefs a la base | 15 | 16 |
| Xrefs al slot GOT | 42 | 53 |
| Lecturas tipadas de gates (`8+8`) | 16 | 16 |
| **Sitios únicos** | **67** | **79** |
| Lectura | 56 | 65 |
| Escritura (sitios) | 6 | 8 |
| Spill | 3 | 4 |
| Propagación | 1 | 1 |
| Dato (tabla) | 1 | 1 |

La A7S tiene **11 referencias más** al estado (53 vs 42 al slot, 16 vs 15 a la base).
Eso ya es una diferencia de superficie: más código de la A7S consulta el objeto.

## 3. Gates `+3`/`+6`: idénticos (no son el mecanismo)

El dumper completo es **el mismo código** en las dos firmware. Se decodificaron 3 948
bytes desde cada prólogo y se compararon las secuencias de instrucciones normalizando
solo destinos de salto y referencias a pool: **las únicas diferencias son los pools de
literales** (44 rangos de bytes, todos en `ldr [pc,…]`/datos), ninguna instrucción de
código cambia. En ambas:

- `+3` se lee 8 veces con `tst` de los bits 0..6 y una prueba de signo (`ldrsb`);
- `+6` igual, 8 veces, bits 0..6 + signo;
- **cero** escrituras a `+3`/`+6` en los 16 xrefs tipados y en los 79 sitios.

Traducción: los gates son un **bitfield de flags de diagnóstico** del dumper en las dos
cámaras. El silent shutter de la A7S no se activa escribiendo estos bytes. Esto cierra
la hipótesis que quedaba abierta desde S153 para el lado A7S y refuerza que el mecanismo
está en drive mode / timings (S204).

## 4. Diferencias de estado (lo nuevo)

### 4.1 Escrituras

| Campo | A6000 | A7S | Sitio A7S | Instrucción |
|---|---|---|---|---|
| `+0x00` | 1 instr. (`0x4383ac90`) | 1 instr. (`0x4385a334`) | `0x4385a334` | `strb r3,[r2]` (escribe 0 al expirar un contador) |
| `+0x02` | 4 instr. | 4 instr. | `0x438536a0`, `0x438536d0`, `0x4385a67c`, `0x4385a9c6` | `strb …,[rX,#2]` |
| **`+0xde`** | — | **1 instr.** | `0x4386521a` | `strb.w r5,[r3,#0xde]` en el epílogo de `FUN_43865100` |
| **`+0xe6`** | — | **1 instr.** | `0x438643a6` | `strh.w r0,[r4,#0xe6]` |
| **`+0xe8`** | — | **1 instr.** | `0x438643b2` | `strh.w r0,[r4,#0xe8]` |
| **`+0xea`** | — | **1 instr.** | `0x438643bc` | `strh.w r0,[r4,#0xea]` |

En `FUN_438642f0` los tres halfwords se calculan con tres divisiones `bl 0x4355de98`
(divisor 10) y se guardan consecutivos: es un trío de valores **escalados ×10**
(INFERENCIA: conversión de unidades), no un flag. `+0xde` es un byte escrito una sola
vez al salir de `FUN_43865100` (INFERENCIA: resultado/modo persistido).

### 4.2 Campos leídos solo por una cámara

| Solo A7S | Dónde | Contexto observado |
|---|---|---|
| `+0x47` | `0x43852086`, `0x4385c9ea` | predicados de byte |
| `+0x60`, `+0x61` | `0x43849f9a`, `0x43849fbc` | contadores que indexan una tabla (`lsls r1,#0xa`) |
| `+0x6d` | `0x4384a1ee` | predicado de byte |
| `+0xae` | `0x43864732` | `u16` **multiplicado por 1000** (`muls r7,r3,#0x3e8`) → valor de tiempo |
| `+0xde`, `+0xdf` | `0x4386521a` (W), `0x43861a8c` | byte escrito y comparado con 1 |
| `+0xe0`, `+0xe2` | `0x438477d8`, `0x438477ec` | dos `u16` que sustituyen a `+0xf8/+0xfa` si no son cero |
| `+0xe4` | `0x438478f6` | `u16` leído tras recarga del spill |
| `+0xe6` | `0x438647ec` | `u16` escrito en el trío ×10 |

| Solo A6000 | Dónde | Contexto |
|---|---|---|
| `+0x7f` | `0x438475ba` | byte sumado a otro y guardado en otro objeto |

**Lectura del conjunto (INFERENCIA, no verificada):** el bloque `+0xde..+0xea` de la A7S
parece un grupo de parámetros de **tiempo/exposición** (halfwords ×10, un `u16` ×1000 en
`+0xae`, contadores de tabla). Encaja con que la A7S implemente el silent shutter por
drive mode + tabla de timings (S204) y no por los flags del dumper. No se atribuye
semántica física ni se afirma que estos campos *sean* el silent shutter: para eso hace
falta seguir sus escritores hasta el selector `0x43826d58` (siguiente ítem).

## 5. Tabla completa de los 79 sitios (A7S)

| Sitio | Función | Instrucción en el sitio | Clase | Campos | Veredicto |
|---|---|---|---|---|---|
| `0x437d36be` | `0x437d1e30` | `ldr.w r3, [r8, r3]` | lectura | +0x40 | lee +0x40 |
| `0x437d36c2` | `0x437d1e30` | `str r3, [sp, #0x20]` | spill | +0x42, +0xa5 | spill; lecturas tras recarga: +0x42, +0xa5 |
| `0x437d648c` | `0x437d44e8` | `ldr r3, [r7, r3]` | lectura | +0x48 | lee +0x48 |
| `0x437dc840` | `0x437dc530` | `ldr r3, [r5, r3]` | lectura | +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 | lee +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 |
| `0x437dc97c` | `0x437dc920` | `ldr r3, [r3, r2]` | lectura | +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 | lee +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 |
| `0x437e059e` | `0x437e0598` | `ldr r3, [r3, r2]` | lectura | +0x00 | lee +0x00 |
| `0x437e05a0` | `0x437e0598` | `ldrb r0, [r3]` | lectura | +0x00 | lee +0x00 |
| `0x437e05be` | `0x437e05b8` | `ldr r3, [r3, r2]` | lectura | +0x00 | lee +0x00 |
| `0x437e05c0` | `0x437e05b8` | `ldrb r0, [r3]` | lectura | +0x00 | lee +0x00 |
| `0x437e0744` | `0x437e073c` | `ldr r3, [r5, r3]` | lectura | +0x04 | lee +0x04 |
| `0x437e07ce` | `0x437e07b8` | `ldr r7, [r4, r3]` | lectura | +0x04, +0x1c, +0x1e, +0x1f | lee +0x04, +0x1c, +0x1e, +0x1f |
| `0x437e09ba` | `0x437e0974` | `ldr.w r6, [r8, r3]` | lectura | +0x1f, +0x03, +0x03, +0x03, +0x03, +0x03, +0x03 | lee +0x1f, +0x03, +0x03, +0x03, +0x03, +0x03, +0x03 |
| `0x437e09d2` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e09ec` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0a06` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0a28` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0a42` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0a5c` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0a76` | `0x437e0974` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0a90` | `0x437e0974` | `ldrsb.w r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x437e0aaa` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0ac4` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0ade` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0af8` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0b12` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0b2c` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0b46` | `0x437e0974` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0b60` | `0x437e0974` | `ldrsb.w r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x437e0cf2` | `0x437e0974` | `ldr.w r7, [r8, r3]` | lectura | +0x0a, +0x0a, +0x0b, +0x0b, +0x0b, +0x0b, +0x0b | lee +0x0a, +0x0a, +0x0b, +0x0b, +0x0b, +0x0b, +0x0b |
| `0x437e10d6` | `0x437e0974` | `ldr.w r7, [r8, r3]` | lectura | +0x0f, +0x0f, +0x0f | lee +0x0f, +0x0f, +0x0f |
| `0x437e1d7a` | `0x437e1d6c` | `ldr r5, [r4, r3]` | lectura | +0x05, +0x1f, +0x02, +0x01, +0x2e, +0x24 | lee +0x05, +0x1f, +0x02, +0x01, +0x2e, +0x24 |
| `0x437e1fc0` | `0x437e1fb0` | `ldr r2, [r4, r3]` | lectura | +0x05, +0x0f | lee +0x05, +0x0f |
| `0x437e233c` | `0x437e22dc` | `ldr r3, [r3, r2]` | lectura | +0x26 | lee +0x26 |
| `0x437e243e` | `0x437e2410` | `ldr r3, [r4, r3]` | lectura | +0x28 | lee +0x28 |
| `0x437e2444` | `0x437e2410` | `str r3, [sp, #0x20]` | spill | +0x26, +0x29 | spill; lecturas tras recarga: +0x26, +0x29 |
| `0x437e3e90` | `0x437e3e18` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x437e3ec6` | `0x437e3e18` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x437e3ef4` | `0x437e3e18` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x437e3f20` | `0x437e3e18` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x437e3f60` | `0x437e3e18` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x437e49f8` | `0x437e4990` | `ldr r3, [r6, r3]` | lectura | +0xa1 | lee +0xa1 |
| `0x437e51e4` | `0x437e50c4` | `ldr r3, [r5, r3]` | lectura | +0xaa | lee +0xaa |
| `0x437e53ae` | `0x437e5390` | `ldr r3, [r7, r3]` | lectura | +0xa3 | lee +0xa3 |
| `0x437e6ae0` | `0x437e6ab8` | `ldr.w r3, [r8, r3]` | propagación | — | propaga |
| `0x437e6ae4` | `0x437e6ab8` | `str r3, [sp, #0x1c]` | spill | — | spill; lecturas tras recarga: ninguna |
| `0x437e6bdc` | `0x437e6ab8` | `ldr r1, [sp, #0x1c]` | lectura | +0xa2 | lee +0xa2 |
| `0x437e6fe2` | `0x437e6ab8` | `ldr r1, [sp, #0x1c]` | lectura | +0xa2 | lee +0xa2 |
| `0x437e7f2a` | `0x437e7f20` | `ldr r3, [r2, r3]` | lectura | +0xac | lee +0xac |
| `0x438453de` | `0x43844ba0` | `ldr r3, [r6, r3]` | lectura | +0x42 | lee +0x42 |
| `0x438477d4` | `0x438477a0` | `ldr r1, [r4, r2]` | lectura | +0xe0, +0xe2 | lee +0xe0, +0xe2 |
| `0x438477f0` | `0x438477a0` | `str r1, [sp, #0x14]` | spill | +0xe4 | spill; lecturas tras recarga: +0xe4 |
| `0x43849f98` | `0x43849a1c` | `ldr r6, [r1, r3]` | lectura | +0x60, +0x61 | lee +0x60, +0x61 |
| `0x4384a1ec` | `0x4384a138` | `ldr r3, [r4, r3]` | lectura | +0x6d | lee +0x6d |
| `0x4384bbda` | `0x4384bbb4` | `ldr r3, [r4, r3]` | lectura | +0x1c | lee +0x1c |
| `0x4384bc24` | `0x4384bc18` | `ldr r3, [r4, r3]` | lectura | +0x1c | lee +0x1c |
| `0x4384bc68` | `0x4384bc5c` | `ldr r3, [r4, r3]` | lectura | +0x1c, +0x1e | lee +0x1c, +0x1e |
| `0x4384c82a` | `0x4384c5bc` | `ldr.w r3, [lr, r3]` | lectura | +0x41 | lee +0x41 |
| `0x4385006c` | `0x4384fe44` | `ldr.w r3, [r8, r3]` | lectura | +0x51 | lee +0x51 |
| `0x43852084` | `0x4385205c` | `ldr r4, [r4, r3]` | lectura | +0x47 | lee +0x47 |
| `0x4385369e` | `0x4385352c` | `ldr r3, [r4, r3]` | escritura | +0x02 | **escribe** +0x02 |
| `0x438536ce` | `0x4385352c` | `ldr r3, [r4, r3]` | escritura | +0x02 | **escribe** +0x02 |
| `0x43855a42` | `0x43855a28` | `ldr r0, [r5, r3]` | lectura | +0x3a, +0x39, +0x3b, +0x38 | lee +0x3a, +0x39, +0x3b, +0x38 |
| `0x4385a332` | `0x4385a290` | `ldr r2, [r4, r2]` | escritura | +0x00 | **escribe** +0x00 |
| `0x4385a334` | `0x4385a290` | `strb r3, [r2]` | escritura | +0x00 | **escribe** +0x00 |
| `0x4385a67a` | `0x4385a384` | `ldr r3, [r3, r2]` | escritura | +0x02 | **escribe** +0x02 |
| `0x4385a9be` | `0x4385a98c` | `ldr r1, [r4, r3]` | escritura | +0x02 | **escribe** +0x02 |
| `0x4385c9e8` | `0x4385c9c4` | `ldr r5, [r5, r3]` | lectura | +0x47 | lee +0x47 |
| `0x4385e8ce` | `0x4385e8c4` | `ldr r5, [r3, r2]` | lectura | +0x22, +0x20 | lee +0x22, +0x20 |
| `0x4385e9dc` | `0x4385e978` | `ldr r3, [r5, r3]` | lectura | +0x22 | lee +0x22 |
| `0x4385f090` | `0x4385effc` | `ldr r0, [r4, r3]` | lectura | +0xfe, +0xff | lee +0xfe, +0xff |
| `0x43861a8a` | `0x43861a58` | `ldr r2, [r4, r2]` | lectura | +0xdf | lee +0xdf |
| `0x4386271a` | `0x438625a0` | `ldr r3, [r6, r3]` | lectura | +0xdf | lee +0xdf |
| `0x4386430e` | `0x438642f0` | `ldr r2, [r5, r2]` | lectura | +0xe6 | lee +0xe6 |
| `0x4386439e` | `0x438642f0` | `ldr r4, [r5, r3]` | escritura | +0xe6, +0xe8, +0xea | **escribe** +0xe6, +0xe8, +0xea |
| `0x43864730` | `0x438645bc` | `ldr r4, [r5, r3]` | lectura | +0xae, +0xe6 | lee +0xae, +0xe6 |
| `0x43864e3e` | `0x43864cb0` | `ldr r3, [r3, r1]` | lectura | +0xde | lee +0xde |
| `0x43865218` | `0x43865100` | `ldr r3, [r4, r3]` | escritura | +0xde | **escribe** +0xde |
| `0x43866cd0` | `0x438669d4` | `ldr r3, [r5, r3]` | lectura | +0xa8 | lee +0xa8 |
| `0x43ff928c` | `—` | `pop {r1, r2, r5, r6, r7}` | dato | — | puntero en tabla, sin xrefs |

## 6. Límites

- Barrido **estático** del blob A7S fw3.20; sin ejecución, cámara ni flasheo.
- No cubre indexación dinámica (`ldr rX,[state,rY]`), DMA ni otro CPU; no se observó
  ninguna indexación de ese tipo en los 79 cuerpos.
- La homología `0x43f7bce6` ≡ estado IMX210 se apoya en: mismo dumper, mismo patrón de
  gates, misma posición (índice 18) en la tabla de punteros y mismo rol de slot GOT.
  Es **INFERENCIA fuerte**; no hay símbolo que lo nombre.
- La semántica de `+0xde/+0xe6/+0xe8/+0xea/+0xae` es **NO_VERIFICADA**. S51 no cambia.

```sh
python3 analysis/s301_a7s_state_xref_sweep/build_sweep.py
python3 analysis/s301_a7s_state_xref_sweep/verify_sweep.py
python3 -m unittest tests.test_s301_a7s_state_xref_sweep -v
```
