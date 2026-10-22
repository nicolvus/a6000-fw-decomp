# S300 — barrido único de xrefs al objeto de estado del IMX210 (A6000 fw3.21)

Carril B, primera sesión. Pregunta: **¿existe algún escritor de los gates `+3`/`+6` del
objeto de estado `0x43f72d02`?** En vez de seguir clasificando xrefs de uno en uno
(S153–S176), esta sesión hace **un solo barrido** de las dos vías de acceso (dirección
del objeto y slot GOT `0x4401f990`), resuelve la función contenedora de cada sitio y
traza localmente el uso del puntero cargado.

**Veredicto (VERIFICADO, límite estático):** ninguno de los 67 sitios escribe `+3` ni
`+6`. Los únicos stores son a `+0x00` (1 instrucción) y `+0x02` (4 instrucciones).
Los gates tienen 8 lecturas cada uno y **cero** escrituras tipadas. No se observa
indexación dinámica, copia de bloque ni escape del puntero en los cuerpos barridos.
No se prueba alcanzabilidad runtime ni cubre DMA/otro CPU (`NO_VERIFICADO`).

## 1. Método y procedencia

| Paso | Herramienta / evidencia |
|---|---|
| Literales absolutos en el blob | búsqueda de bytes propia de `02 2d f7 43` (LE `0x43f72d02`) y `90 f9 01 44` |
| Xrefs exactos a `0x43f72d02`, `0x4401f990`, `0x43ff3248` | REA `xrefs` (3 llamadas, `raw1.jsonl`) |
| Tipo de acceso (READ/WRITE/PARAM/DATA) en el objeto y en los gates | REA `inspect_native_instruction` (5 llamadas) |
| Función contenedora de cada sitio | REA `resolve_containing_procedure` (67 llamadas, `raw2.jsonl`) |
| Rangos de cuerpo de cada función | REA `procedure_info` (35 llamadas, `raw3.jsonl`) |
| Uso local del puntero cargado | traza lineal Thumb propia (`sweep_trace.py`, capstone 5.0.7) |
| Verificación final | `verify_sweep.py` re-decodifica **cada** instrucción y offset desde `av-cam.bin` |

SHA-256 del binario analizado: `b60c845ccb90c0ff86b7f62f1f3f2ecda714aa20c37805959ebee2b429e56bb9`
(av-cam.bin de la A6000 fw3.21, base de carga `0x43541000`).

**Solo hay dos literales absolutos con el puntero en todo el blob** (VERIFICADO por
búsqueda de bytes): el slot GOT `0x4401f990` y la entrada `0x43ff3248` de la tabla
`0x43ff3200`. El resto del código alcanza el objeto por suma de offset al base GOT;
por eso el barrido incluye obligatoriamente el slot.

## 2. Cobertura

| Conjunto | Sitios |
|---|---|
| Xrefs exactos a la base `0x43f72d02` | 15 |
| Xrefs exactos al slot `0x4401f990` | 42 |
| Lecturas tipadas de los gates `+3` y `+6` | 16 (8 + 8) |
| **Unión (sitios únicos)** | **67** |

Seis sitios aparecen por las dos vías (base y slot) porque la instrucción que carga el
puntero y la que lo desreferencia son contiguas: `0x438363e6`, `0x4384cb06`,
`0x43858134`, `0x43859954`, `0x438d933e`, `0x438d9378`. La unión coincide exactamente
con los 67 sitios de la tabla (comprobado en `verify_sweep.py`).

Clases: **55 lectura**, **6 escritura** (5 instrucciones distintas), **3 spill**,
**2 propagación** (carga sin desreferencia en el sitio) y **1 dato** (tabla).

## 3. Escritores: solo `+0x00` y `+0x02`

| Instrucción | Función | Destino | Evidencia |
|---|---|---|---|
| `strb r3,[r2]` @ `0x4383ac90` | `FUN_4383abec` | `state+0x00` | edge WRITE tipado a `0x43f72d02`; bytes `13 70` |
| `strb r2,[r3,#2]` @ `0x4383415a` | `FUN_43833ff8` | `state+0x02` | xref READ al slot en `0x43834158`; `r3` = valor del slot |
| `strb r0,[r3,#2]` @ `0x4383418a` | `FUN_43833ff8` | `state+0x02` | idem, `r0` vale 0 en esa rama (`mov r0,r3` con `r3=0`) |
| `strb r4,[r3,#2]` @ `0x4383afd0` | `FUN_4383ace0` | `state+0x02` | `r3` = base GOT, `[r3,r2]` = slot |
| `strb r3,[r1,#2]` @ `0x4383b316` | `FUN_4383b2dc` | `state+0x02` | `r1` = valor del slot; `r3=0` |

Los cuatro stores a `+0x02` escriben un byte de estado/modo (el valor depende de la
rama); **su semántica física es INFERENCIA y no se afirma**. Lo VERIFICADO es el destino
y el tamaño. El store a `+0x00` ya lo había aislado S160; este barrido lo re-verifica y
confirma que es el **único** store a `+0`.

## 4. Gates `+3` y `+6`: 8 lecturas cada uno, cero escrituras

Los 16 accesos tipados a `0x43f72d05`/`0x43f72d08` son `READ` y viven todos en
`FUN_43858338` (el dumper de descriptores de S152/S153). La tabla siguiente muestra el
bit que prueba cada línea (VERIFICADO por decodificación de los bytes siguientes):

| Gate | Sitios | Máscaras probadas |
|---|---|---|
| `state+3` | `0x43858396`, `b0`, `ca`, `ec`, `0x43858406`, `20`, `3a`, `54` | bits 0,1,2,3,4,5,6 y prueba de signo (`ldrsb` + `cmp`) |
| `state+6` | `0x4385846e`, `88`, `a2`, `bc`, `d6`, `f0`, `0x4385850a`, `24` | bits 0,1,2,3,4,5,6 y prueba de signo |

Es decir, `+3` y `+6` se consumen como **bytes de flags de 7 bits + bit de signo**, no
como contadores. Los dos gates siguen **sin escritor estático** en todo el barrido.
Los bytes están a cero en la imagen (`+3..+6 = 00 00 00 00`), por lo que su valor en una
foto real es `NO_VERIFICADO`.

## 5. Spills y propagación (sin escape)

| Sitio | Instrucción | Recargas posteriores |
|---|---|---|
| `0x4384cb0a` | `str r3,[sp,#0x20]` | `0x4384cee4` → `+0xa5`; `0x4384d21a` → `+0xa5`; `0x4384d584` → `+0x42` |
| `0x4385b268` | `str r3,[sp,#0x20]` | `0x4385ba46` → `+0x26`; `0x4385beae` → `+0x29` |
| `0x4386001c` | `str r3,[sp,#0x1c]` | `0x43860112` y `0x43860506` → `+0xa2` (ya son xrefs propios) |

Todas las recargas se usan para **leer** campos; ninguna para escribir. Se comprobó el
orden lineal: las recargas de `sp+0x20` anteriores al spill (`0x4384c40e`, `0x4384c6ee`)
no pueden ser este puntero. El único `bl` que recibe el puntero en un argumento
(`0x43860134` y `0x43860528` → `FUN_4385ff94`, con el objeto en `r1`) lo descarta: el
callee reescribe `r1` en su prólogo (`add r1,sp,#0x10`) antes de usarlo. Por tanto no
hay escape a otro objeto/global en estos cuerpos.

## 6. Tabla completa (67 sitios)

| Sitio | Función | Instrucción en el sitio | Clase | Campos | Veredicto |
|---|---|---|---|---|---|
| `0x4382e526` | `0x4382dd78` | `ldr r3, [r5, r3]` | lectura | +0x42 | lee +0x42 |
| `0x43830994` | `0x4383075c` | `ldr.w r3, [r8, r3]` | lectura | +0x51 | lee +0x51 |
| `0x43834158` | `0x43833ff8` | `ldr r3, [r4, r3]` | escritura | +0x02 | **escribe** +0x02 |
| `0x43834188` | `0x43833ff8` | `ldr r3, [r4, r3]` | escritura | +0x02 | **escribe** +0x02 |
| `0x438363e6` | `0x438363cc` | `ldr r0, [r5, r3]` | lectura | +0x3a, +0x39, +0x3b, +0x38 | lee +0x3a, +0x39, +0x3b, +0x38 |
| `0x4383ac8e` | `0x4383abec` | `ldr r2, [r4, r2]` | escritura | +0x00 | **escribe** +0x00 |
| `0x4383ac90` | `0x4383abec` | `strb r3, [r2]` | escritura | +0x00 | **escribe** +0x00 |
| `0x4383afce` | `0x4383ace0` | `ldr r3, [r3, r2]` | escritura | +0x02 | **escribe** +0x02 |
| `0x4383b30e` | `0x4383b2dc` | `ldr r1, [r4, r3]` | escritura | +0x02 | **escribe** +0x02 |
| `0x4383f0d2` | `0x4383f0c8` | `ldr r5, [r3, r2]` | lectura | +0x22, +0x20 | lee +0x22, +0x20 |
| `0x4383f1e0` | `0x4383f17c` | `ldr r3, [r5, r3]` | lectura | +0x22 | lee +0x22 |
| `0x438475b8` | `0x43844e80` | `ldr r0, [r6, r0]` | lectura | +0x7f | lee +0x7f |
| `0x4384cb06` | `0x4384b268` | `ldr.w r3, [r8, r3]` | propagación | — | propaga |
| `0x4384cb0a` | `0x4384b268` | `str r3, [sp, #0x20]` | spill | +0x42, +0xa5 | spill a stack; lecturas tras recarga: +0x42, +0xa5 |
| `0x4384f7e4` | `0x4384d8bc` | `ldr r3, [r7, r3]` | lectura | +0x48 | lee +0x48 |
| `0x43857f8e` | `0x43857f88` | `ldr r3, [r3, r2]` | lectura | +0x00 | lee +0x00 |
| `0x43857f90` | `0x43857f88` | `ldrb r0, [r3]` | lectura | +0x00 | lee +0x00 |
| `0x43857fae` | `0x43857fa8` | `ldr r3, [r3, r2]` | lectura | +0x00 | lee +0x00 |
| `0x43857fb0` | `0x43857fa8` | `ldrb r0, [r3]` | lectura | +0x00 | lee +0x00 |
| `0x43858134` | `0x4385812c` | `ldr r3, [r5, r3]` | lectura | +0x04 | lee +0x04 |
| `0x438581a6` | `0x43858190` | `ldr r7, [r4, r3]` | lectura | +0x04, +0x1c, +0x1e, +0x1f | lee +0x04, +0x1c, +0x1e, +0x1f |
| `0x4385837e` | `0x43858338` | `ldr.w r6, [r8, r3]` | lectura | +0x1f, +0x03, +0x03, +0x03, +0x03, +0x03, +0x03 | lee +0x1f, +0x03, +0x03, +0x03, +0x03, +0x03, +0x03 |
| `0x43858396` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x438583b0` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x438583ca` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x438583ec` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x43858406` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x43858420` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x4385843a` | `0x43858338` | `ldrb r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x43858454` | `0x43858338` | `ldrsb.w r3, [r6, #3]` | lectura | +0x03 | lee +0x03 |
| `0x4385846e` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x43858488` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x438584a2` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x438584bc` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x438584d6` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x438584f0` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x4385850a` | `0x43858338` | `ldrb r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x43858524` | `0x43858338` | `ldrsb.w r3, [r6, #6]` | lectura | +0x06 | lee +0x06 |
| `0x438586b6` | `0x43858338` | `ldr.w r7, [r8, r3]` | lectura | +0x0a, +0x0a, +0x0b, +0x0b, +0x0b, +0x0b, +0x0b | lee +0x0a, +0x0a, +0x0b, +0x0b, +0x0b, +0x0b, +0x0b |
| `0x43858a9a` | `0x43858338` | `ldr.w r7, [r8, r3]` | lectura | +0x0f, +0x0f, +0x0f | lee +0x0f, +0x0f, +0x0f |
| `0x4385971e` | `0x43859710` | `ldr r5, [r4, r3]` | lectura | +0x05, +0x1f, +0x02, +0x01, +0x2e, +0x24 | lee +0x05, +0x1f, +0x02, +0x01, +0x2e, +0x24 |
| `0x43859954` | `0x43859944` | `ldr r2, [r4, r3]` | lectura | +0x05, +0x0f | lee +0x05, +0x0f |
| `0x4385b160` | `0x4385b100` | `ldr r3, [r3, r2]` | lectura | +0x26 | lee +0x26 |
| `0x4385b262` | `0x4385b234` | `ldr r3, [r4, r3]` | lectura | +0x28 | lee +0x28 |
| `0x4385b268` | `0x4385b234` | `str r3, [sp, #0x20]` | spill | +0x26, +0x29 | spill a stack; lecturas tras recarga: +0x26, +0x29 |
| `0x4385d3c8` | `0x4385d350` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x4385d3fe` | `0x4385d350` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x4385d42c` | `0x4385d350` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x4385d458` | `0x4385d350` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x4385d498` | `0x4385d350` | `ldr r2, [r4, r2]` | lectura | +0xa0 | lee +0xa0 |
| `0x4385df4c` | `0x4385dee4` | `ldr r3, [r6, r3]` | lectura | +0xa1 | lee +0xa1 |
| `0x4385e6fc` | `0x4385e5dc` | `ldr r3, [r5, r3]` | lectura | +0xaa | lee +0xaa |
| `0x4385e8c2` | `0x4385e8a4` | `ldr r3, [r7, r3]` | lectura | +0xa3 | lee +0xa3 |
| `0x43860018` | `0x4385fff0` | `ldr.w r3, [r8, r3]` | propagación | — | propaga |
| `0x4386001c` | `0x4385fff0` | `str r3, [sp, #0x1c]` | spill | — | spill a stack; lecturas tras recarga: ninguna |
| `0x43860112` | `0x4385fff0` | `ldr r1, [sp, #0x1c]` | lectura | +0xa2 | lee +0xa2 |
| `0x43860506` | `0x4385fff0` | `ldr r1, [sp, #0x1c]` | lectura | +0xa2 | lee +0xa2 |
| `0x4386140a` | `0x43861400` | `ldr r3, [r2, r3]` | lectura | +0xac | lee +0xac |
| `0x438693ec` | `0x438690dc` | `ldr r3, [r5, r3]` | lectura | +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 | lee +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 |
| `0x43869528` | `0x438694cc` | `ldr r3, [r3, r2]` | lectura | +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 | lee +0x30, +0x31, +0x32, +0x33, +0x34, +0x35, +0x36, +0x37 |
| `0x43869990` | `0x438698fc` | `ldr r0, [r4, r3]` | lectura | +0xfe, +0xff | lee +0xfe, +0xff |
| `0x438d933e` | `0x438d9318` | `ldr r3, [r4, r3]` | lectura | +0x1c | lee +0x1c |
| `0x438d9378` | `0x438d936c` | `ldr r3, [r4, r3]` | lectura | +0x1c | lee +0x1c |
| `0x438d93a8` | `0x438d939c` | `ldr r3, [r4, r3]` | lectura | +0x1c, +0x1e | lee +0x1c, +0x1e |
| `0x438d9ee6` | `0x438d9cc0` | `ldr.w r3, [lr, r3]` | lectura | +0x41 | lee +0x41 |
| `0x438e758e` | `0x438e72d8` | `ldr r3, [r5, r3]` | lectura | +0xa8 | lee +0xa8 |
| `0x43ff3248` | `—` | `cmp r5, #2` | dato | — | puntero en tabla, sin xrefs de código |

## 7. Corrección de la rev.1 de este informe

La primera versión de S300 (commit `75f5fa28`) publicó la tabla de 15 xrefs con **todas
las direcciones desplazadas +0x58** (`0x4383643e` en vez de `0x438363e6`, `0x4383ace8`
en vez de `0x4383ac90`, `0x4384cb5e` en vez de `0x4384cb06`, `0x43857fe8` en vez de
`0x43857f90`, `0x43ff32a0` en vez de `0x43ff3248`, …). **VERIFICADO en esta sesión:**
REA devuelve exactamente las 15 direcciones sin sesgo (`raw1.jsonl`) y cada byte de la
tabla se re-decodifica desde `av-cam.bin`; el sesgo desaparece. `xrefs_classified.json`
se regeneró con las direcciones correctas y conserva su esquema para el test existente.
El veredicto de la rev.1 («0 writers a +3/+6») se mantiene y ahora está respaldado por
los 67 sitios, no solo por 15.

## 7. Observaciones y correcciones candidatas

- **S176 no es reutilizable:** `knowledge/CURRENT.md` cita `analysis/s176_imager_state_readers/`
  y `docs/capture/s176-imager-state-readers.md`, pero **no existen en el árbol ni en el
  historial git** (`git log --all --diff-filter=A` no devuelve nada). Sus dos direcciones
  se re-verificaron aquí desde bytes: `0x4386140a` carga el slot y `0x43861410` lee
  `state+0xac`; `0x438693ec` carga el slot y el bloque lee `+0x30..+0x37`, guardando
  **cero** en `[r6,#0x664..#0x67c]` cuando el byte es cero (`cbnz` precede al `str`).
  No se observa el «default 6» que atribuía S176 en ese bloque.
- `0x43ff3248` (entrada de la tabla `0x43ff3200` que contiene el puntero al estado) tiene
  **0 xrefs de código**; queda para el ítem del árbol de referencias de `0x43ff3200`.
- Los cuatro escritores de `+0x02` son buenos candidatos para el ítem de drive modes:
  `+2` es el único byte de estado con múltiples escritores además de `+0`.

## 8. Límites explícitos

- **No cubre** indexación con registro (`ldr rX,[state,rY]`) porque no se observó ninguna
  en los 67 cuerpos; si existiera en código no alcanzado por estas xrefs, el barrido no
  la vería. Tampoco cubre DMA, otro CPU ni memoria mapeada.
- **No prueba ausencia global** en el sentido de ejecución: prueba que, en esta imagen y
  para estas 67 referencias, no hay instrucción de escritura a `+3`/`+6`.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s300_state_xref_sweep/build_sweep.py   # reconstruye el JSON desde raw*.jsonl
python3 analysis/s300_state_xref_sweep/verify_sweep.py  # re-decodifica todo desde el blob
python3 -m unittest tests.test_s300_state_xref_sweep -v
```
