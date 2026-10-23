# S347 — el campo `0x000d` de la tabla ODL es la constante 13 del camino de carga, y los ids de la A6000 son la lista A7S filtrada a `id ≤ 0x4e`

> **Alcance:** estático. Solo se leen los blobs `av-cam.bin` de los tres firmware y el
> fichero `lensbin_lensproperty/LensAberrationData.bin`. Sin firmware en ejecución, sin
> cámara, sin flasheo, sin red. Autoridad = **bytes**; REA/Ghidra solo corroboran.

S347 responde las dos preguntas que dejó abiertas S342: **qué codifica el segundo `u16`
(`0x000d`) de la tabla `{u16 id, u16 0x000d}`** y **si los 47 ids de la A6000 tienen
correlato funcional con los 69 de la A7S**.

Respuesta corta:

1. `0x000d` **no es un dato por id**: vale `13` en **las 138 entradas** de los tres modelos.
   Es la **capacidad del bloque de datos** que el ODL adjunta al mensaje de carga: el mismo
   `0x0d` se pasa como tamaño en el inicializador del camino de carga (los tres modelos) y
   como primer argumento del allocador de la tabla completa (los tres modelos), mientras la
   **cabecera** del mensaje que lo envuelve es de `0x18` = 24 B.
2. Los ids de la A6000 son **exactamente** la lista de la A7S filtrada por `id ≤ 0x4e` (78),
   **conservando el orden**; la A6300 es **idéntica** a la A7S. La A6000 simplemente no pide
   los 22 bloques `0x4f..0x64` (79..100).

---

## 1. La tabla y el campo, medidos

| Modelo | tabla | entradas | segundo campo | ids | bucle consumidor A / B |
|---|---|---|---|---|---|
| A7S fw3.20 | `0x43fef404` | 69 | **`0x000d` × 69** | 69 únicos en `0x01..0x64` | `cmp r7,#0x45` / `cmp.w r5,#0x114` |
| A6000 fw3.21 | `0x43feae1c` | 47 | **`0x000d` × 47** | 47 únicos en `0x01..0x4e` | `cmp r7,#0x2f` / `cmp r5,#0xbc` |
| A6300 fw2.01 | `0x441b0b1c` | 69 | **`0x000d` × 69** | 69 únicos (lista A7S) | `cmp r7,#0x45` / `cmp.w r5,#0x114` |

- **VERIFICADO:** el segundo `u16` es constante (`13`) en las 69/47/69 entradas; el
  terminador de cada tabla es la primera entrada cuyo segundo campo ya no es `0x000d`.
- **VERIFICADO:** los contadores de los dos consumidores cierran exactamente con el número de
  entradas (69 → `0x45` y `0x114`; 47 → `0x2f` y `0xbc`, con paso 4).
- **VERIFICADO:** las bases PIC de la tabla son **dos** por modelo
  (A7S `0x437056f8`/`0x43705754`; A6000 `0x436eb2d8`/`0x436eb334`;
  A6300 `0x43734be4`/`0x43734c40`) y hay **0 literales absolutos** a la tabla en los tres.

## 2. El `13` es un tamaño, y no es la cabecera

El camino de carga por id (una función por modelo) arranca con la misma secuencia:

```
A7S   0x4373d530  0221        movs r1, #2
A7S   0x4373d532  0d22        movs r2, #0xd        <-- 13
A7S   0x4373d538  ...         bl   0x43ae1332      <-- inicializador de stream
A7S   0x4373d544  1823        movs r3, #0x18       <-- capacidad de la cabecera: 24
A7S   0x4373d54a  ...         bl   0x43ae136e
A6000 0x43721ba0  0221 / 0d22  / bl 0x43ae071a / 0x43721bb4 1823 / bl 0x43ae0756
A6300 0x4373b938  0221 / 0d22  / bl 0x43b90054 / 0x4373b94c 1823 / bl 0x43b91d62
```

- **VERIFICADO:** la pareja `0221 0d22` aparece **una sola vez en cada modelo** (los tres
  blobs), y siempre en la cabecera de la función de carga.
- **VERIFICADO:** `13 ≠ 24`: la cabecera del mensaje se dimensiona aparte con `movs r3,#0x18`.
- **VERIFICADO:** el mismo inicializador recibe **longitudes de runtime** en otros sitios
  (A7S `0x438f7fdc ldrh.w r2,[sp,#0x4c]` → `0x438f7fe2 bl 0x43ae1332`), y en otros callers
  recibe capacidades del mismo orden (`5`, `3`, `0xb6`, `0xbc`, `0x13b`). Es un **tamaño**.
- **VERIFICADO:** el allocador de la tabla completa (slot `+0x2b0` de la interfaz importada)
  recibe también `0x0d` como primer argumento en los tres modelos
  (`movs r0,#0xd`: A7S `0x4370574a`, A6000 `0x436eb32a`, A6300 `0x43734c36`).
- **VERIFICADO:** el `13` es **independiente del número de entradas** (69 en A7S/A6300 y 47
  en A6000 comparten el mismo `0x0d`).

### El id viaja en el mensaje en `+0x12`

El constructor del mensaje ODL escribe, en los tres modelos, el **mismo prólogo de 20 B**
(`0123 0380 4380 0371 4ff0ff33 4482 8360 0133 0374`):

```
strh r3,[r0]      ; +0x00 msg_code = 1
strh r3,[r0,#2]   ; +0x02 option   = 1
strb r3,[r0,#4]   ; +0x04 prg_num  = 1
mov.w r3,#-1
strh r4,[r0,#0x12]; +0x12 = ID (u16, argumento r4)
str  r3,[r0,#8]   ; +0x08 timeout  = 0xffffffff
strb r3,[r0,#0x10]; +0x10 prg_id   = 0
strb r3,[r0,#0x11]; +0x11 usr_unq_id = 0
str  r3,[r0,#0x14]; +0x14 offset   = 0
```

Sitios: A7S `0x4373d554`, A6000 `0x43721bc4`, A6300 `0x4373b95c` (20 B idénticos).
El validador de respuestas de S604 (`ODL_RES_MSG`) imprime `msg_code`, `option`, `prg_num`,
`timeout`, `err_code`, `prg_id`, `usr_unq_id`, `offset` y `unit_type` — el `u16` de `+0x12`
es el **id de bloque** y no se confunde con `prg_id` (byte en `+0x10`) ni con `unit_type`
(`+0x18` de la respuesta).

### El «otro» `0xd` de la A6000 (homónimo, no confundir)

En la A6000 fw3.21 el logger `0x437219f8` se invoca como `log(0xd, 3, 1, formato)`:
`0xd` es el **id de módulo de traza** (`[LENS_YC]`). Aparece en las ramas de error de las
mismas funciones (`0x43721ad4`, `0x43721b54`, `0x436fd904`, …) y **no** tiene relación con
el tamaño 13 del camino de carga. En la A7S (fw3.20) ese logger no existe (su logger es
`0x438f7114`, sin id de módulo), y el `13` solo aparece como tamaño.

## 3. Relación funcional de los ids entre modelos

- **VERIFICADO:** `A6000 = [x for x in A7S if x <= 0x4e]`, con el **mismo orden**. Prefijo
  común: 41 entradas (`…62, 57`). Después la A7S inserta `79..99`, sigue con `63, 100, 74,
  76, 64, 69, 75`; la A6000 continúa directamente con `63, 74, 76, 64, 69, 75`.
- **VERIFICADO:** el conjunto que falta en la A6000 es **exactamente** `{79..100}` = `0x4f..0x64`
  (22 ids).
- **VERIFICADO:** `A6300 == A7S` (69/69, misma lista y mismo orden).
- **INFERENCIA (alta):** los ids enumeran **bloques de datos de aberración** que el cuerpo
  pide/recibe; la A6000 declara 22 bloques menos porque su tabla no se amplió (su build es
  posterior en otras áreas —logger nuevo, `[LENS_YC]`— pero esta tabla quedó congelada).
- **NO_VERIFICADO:** el contenido físico de cada bloque y el criterio con el que se
  eligieron `79..100`.

### El fichero `LensAberrationData.bin` no es la fuente de la lista

- Existe en los tres firmware: `…/nflasha3_unpacked_unpacked/lensbin_lensproperty/LensAberrationData.bin`.
- **VERIFICADO:** los tres son **byte a byte idénticos** (`sha256 40d17dbb…3062e`, 161766 B),
  luego el fichero es independiente del modelo; la diferencia 69/47 es **código**.
- **VERIFICADO (negativo):** el fichero no contiene la tabla `{id, 0x000d}` (máximo de pares
  consecutivos con segundo campo `0x000d`: **1**) ni la lista de ids de la A7S.
- Cabecera del fichero: `49 49 00 01 20 00 80 00` ("II", versión `0x0100`, **32** entradas de
  directorio de 8 B y bloques de `0x100` B desde `0x108`). Este formato no se interpreta aquí.

## 4. Persistencia del «aberration data info»

Independiente de la tabla, el módulo guarda un `u16` seleccionado en la configuración `0x402`,
offset `+0x680`:

| Modelo | escribe | lee | id de config |
|---|---|---|---|
| A7S | `0x437051e6` `strh.w r4,[r3,#0x680]` | `0x43705248` `ldrh.w r5,[r3,#0x680]` | `movw r0,#0x402` (`0x437051cc`/`0x4370522c`) |
| A6000 | `0x436fda42` `strh.w r6,[r3,#0x680]` | `0x436fdad4` `ldrh.w r6,[r3,#0x680]` | `0x436fda3c`/`0x436fdab4` |
| A6300 | `0x437346d2` `strh.w r4,[r3,#0x680]` | `0x43734734` `ldrh.w r5,[r3,#0x680]` | `0x437346b8`/`0x43734718` |

`SetAberrationDataInfo(u16)` (A6000 `0x436fd9b0`) copia ese valor a un global
(`DAT_43f64f66`) y relee la config. **NO_VERIFICADO:** si ese `u16` es el id de un bloque de
la tabla o un selector distinto (no hay correspondencia estática con `0x43fef404`).

## 5. Corroboración con decompiladores (no autoridad)

- **Ghidra histórico** (`analysis/ghidra/silent-liro.gpr`, solo lectura, programa `av-cam.bin`
  = **A6000**) confirma el patrón: `candidate_436eb2cc` itera `while (iVar4 != 0x2f)` y pasa
  a `FUN_435614d0` la terna `{tabla[i], 0x43ada547, item_i}`; `FUN_436eb328` llama a
  `FUN_43561458(0xd, &tabla, companion, …)` y luego `FUN_435614ec(item_i)` 47 veces;
  `candidate_43721bc4` escribe `param_1[9] = id` (`+0x12`); `candidate_437219f8` es el logger
  `(0xd, 3, 1, fmt)`.
- **REA** sobre `av-cam-a7s.bin` (sesión `run/b347.sock`, lista en 551,3 s):
  `FUN_43ae1332(buf,2,13)` → `*buf = 2; FUN_4355f5e4(0x2a, 13, buf+1)` (allocación de 13 B) y
  `FUN_43ae136e(dst, src, const, 0x18)` construye la cabecera de 24 B y enlaza el bloque de
  13 B (`*(int*)(iVar1-4) = src`). `FUN_437056ec`/`FUN_43705748` reproducen los dos bucles.
  Tres funciones (`0x4373d52c`, `0x4373d0b0`, `0x437051c0`/`0x43705224`) devolvieron
  `invalid_request` (entradas Thumb no sembradas en REA): se cubren con bytes y con el
  proyecto Ghidra de la A6000.

REA y Ghidra comparten motor: su acuerdo prueba configuración coherente, **no independencia**.
Las cifras de este informe se re-decoden de los bytes con `verify_odl_field.py`.

## 6. Límites

- **NO_VERIFICADO** si los 13 B son la **petición** o el **destino de la respuesta**: el
  mensaje se entrega a la interfaz importada (slots `+0x2b0/+0x2c8/+0x2cc`), cuyo cuerpo vive
  fuera de este blob.
- **NO_VERIFICADO** el significado físico de cada id y el motivo de la ausencia de `0x4f..0x64`
  en la A6000.
- El espacio numérico de ids (`1..0x64`) **se solapa** con 20 de los 34 códigos de drive mode
  (`{1,3,5,7,8,15,25,26,31,49,55,63,69,70,76,77,78,79,80,81}`). Es solo coincidencia de
  rango: S342 ya probó que la tabla **no** se indexa por modo.
- S51 (A/B/C) **no cambia**: `Camera::Lens::ODL` gestiona aberración del objetivo, no el
  obturador.

## 7. Reproducción

```sh
.venv/bin/python analysis/s347_odl_field/build_odl_field.py    # escribe odl_field.json
.venv/bin/python analysis/s347_odl_field/verify_odl_field.py   # 595 comprobaciones (bytes)
.venv/bin/python -m unittest tests.test_s347_odl_field          # 9 tests
.venv/bin/ruff check analysis/s347_odl_field tests/test_s347_odl_field.py
.venv/bin/mypy --ignore-missing-imports analysis/s347_odl_field
```

Artefactos: `analysis/s347_odl_field/{build_odl_field.py,verify_odl_field.py,odl_field.json}`
y `tests/test_s347_odl_field.py`.
