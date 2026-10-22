# S302 — drive mode y exposición: A7S fw3.20 vs A6000 fw3.21, campo a campo

Tercera sesión del carril B. Compara las estructuras de **exposición** y **drive mode** de
las dos cámaras usando las direcciones ya conocidas (S124, S134, S140, S201) y
re-verificándolas contra bytes en esta sesión. No repite el censo de registros (S201);
se centra en los **offsets** y en la **forma de las tablas**.

**Resumen:** la estructura lógica es la misma (contexto de captura → estado del imager por
singleton → puntero a bloque de parámetros → tabla de registros por modo), pero **todos los
offsets del contexto y del estado están desplazados** y la A7S añade una indirección
**modo → columna** con 34 códigos de modo. El bloque de parámetros copiado tiene **4
palabras en la A6000 y 3 en la A7S**.

## 1. Función de comprobación de parámetros (S134) en las dos cámaras

| Dato | A6000 `FUN_4381106c` | A7S `FUN_4383260c` | Δ |
|---|---|---|---|
| Guard en el contexto | `ldrb [r0,#0xd70]` | `ldrb [r0,#0xd78]` | +8 |
| `ldrd` de entrada | `[r0+0xd60+8]` | `[r0+0xd70]` | −8 / reubicado |
| Accesor del estado imager | `bl 0x4378f9b4` | `bl 0x437b38ec` | distinto |
| Puntero a bloque de parámetros | `[state+0x24]` | `[state+0x24]` | igual |
| Palabras copiadas del bloque | **4** (`ldm r3,{r0..r3}`) | **3** (`ldm r2,{r0..r2}`) | −1 palabra |
| `shut` | `[ctx+0x1f8]` | `[ctx+0x200]` | +8 |
| `shut` alterno (`svd==9`) | `[ctx+0x1fc]` | `[ctx+0x204]` | +8 |
| `VdNum` (u16) | `[[state+8]+0xcc]` | `[[state+8]+0xd8]` | +0xc |
| `svr_num` (u8) | `[[state+8]+0x14e]` | `[[state+8]+0x15e]` | +0x10 |
| División sin signo | `bl 0x4355faf0` | `bl 0x4355de98` | distinto |

La fórmula es la misma en ambas (S134): `svd = (svd==9 ? 1 : shut) * svr_num − 1` o
`/ VdNum − 1`; el centinela `svd==9` y los mensajes `Imager param error…`/`Imager svd
error…` existen en las dos (A7S en `0x43cb2bcd`/`0x43cb2bfe`, referenciados desde
`0x438326a4`/`0x438326d8`). **VERIFICADO por instrucciones** en `compare.json`.

Consecuencia: cualquier análisis que use los offsets de la A6000 sobre la A7S falla por
8–16 bytes. El bloque de parámetros además perdió una palabra en la A7S.

## 2. Selección de modo: tabla (A6000) vs selector textual (A7S)

**A7S — `0x43826d58(modo, sub, tipo)`** (VERIFICADO instrucción a instrucción):

| Entrada | Salida |
|---|---|
| `modo == 5` | `0x0c` |
| `modo == 0x1b` | `0x1b` (sin cambio) |
| `tipo == 2` (Silent), `sub == 0` | **`0x4e`** |
| `tipo == 2`, `sub == 1` | **`0x4f`** |
| `tipo == 2`, `sub > 1` | log de error y `0x4e` |
| `tipo != 2`, `sub == 0` | `0x0b` |
| `tipo != 2`, `sub == 1` | `0x35` |
| `tipo != 2`, `sub == 2` | `0x17` |
| `tipo != 2`, `sub > 2` | log de error y `0x0b` |

**A6000 — `0x436d6570`**: no hay selector por `tipo`; la función recorre la tabla de
registros (`0x43fe9b74`) y copia el byte de la **columna** que recibe como argumento. La
A6000 elige columna directamente; la A7S traduce primero *código de modo* → columna.

## 3. Tablas de registros por modo

| | A6000 | A7S |
|---|---|---|
| Base de filas | `0x43fe9b74` | `0x43fee598` |
| Stride | `0x14` (20 B) | `0x14` (20 B) |
| Cabecera de fila | 4 B (puntero a descriptor) | 4 B (puntero a descriptor) |
| Payload | 16 B | 16 B |
| Filas (terminador = cabecera 0) | **59** | **69** |
| Códigos de modo | 13 (S201; no re-derivado aquí) | **34** en `0x43fee370` |
| Indirección modo→columna | no | sí, mapa `0x43c9c5b5` |

Los 34 códigos de la A7S (VERIFICADO por bytes) son:
`0b 37 35 38 13 1f 05 18 10 1a 07 19 32 34 33 46 01 30 03 31 0a 36 0f 12 3f 44 45 4c 4d 4e 4f 50 51 08`.
Las posiciones 27..30 son `4c 4d 4e 4f`, es decir los modos Silent `0x4e`/`0x4f` son
adyacentes a `0x4c`/`0x4d`.

### El mapa modo→columna

El accesor `0x436f3928` hace `ldrb r1,[mapa,modo]` y luego recorre las filas copiando
`fila[4+columna]`. El mapa está en `0x43c9c5b5` (82 bytes, índices 0..0x51). Valores
relevantes:

| modo | columna |
|---|---|
| `0x0b` | 4 |
| `0x17` | 9 |
| `0x35` | 0 |
| `0x46` | 1 |
| `0x4c` | 1 |
| `0x4d` | 1 |
| `0x4e` | **1** |
| `0x4f` | **1** |
| `0x51` | 0 |

**Hallazgo:** para **este** accesor, los modos Silent `0x4e`/`0x4f` usan la **misma
columna (1)** que `0x4c`/`0x4d`. Es decir, la matriz de registros no distingue el modo
silencioso: los cuatro modos producen el mismo conjunto de valores de registro. Esto
**discrepa** de la frase de S204 «sus filas de registro difieren mínimamente de
`0x4c`/`0x4d` (1 registro cada una: `0x000c` y `0x000a`)». No se corrige S204 aquí
(regla del carril), pero queda como **contradicción a re-verificar**: si S204 midió otra
tabla (p. ej. la de timings), ambas pueden ser ciertas; si midió esta, el dato es
incorrecto. Lo que sí queda VERIFICADO es el byte del mapa.

Con esto, el silent shutter de la A7S se apoya en el **código de modo** (`tipo==2` →
`0x4e/0x4f`) y en tablas posteriores (timings, S202), **no** en los gates `+3/+6` del
estado (S301) ni en la matriz de registros de este accesor.

## 4. Límites

- Comparación **estática**; sin runtime, cámara ni flasheo.
- «13 modos» de la A6000 se cita de S201 y **no** se re-deriva en esta sesión.
- La semántica de `sint`, `gs`, `epdsel` (S124) sigue **NO_VERIFICADA**.
- No se afirma equivalencia física de modos entre cámaras ni capacidad del IMX210.
- S51 no cambia (A=NO, B=NO, C=NO).

```sh
python3 analysis/s302_drive_modes/build_compare.py
python3 analysis/s302_drive_modes/verify_compare.py
python3 -m unittest tests.test_s302_drive_modes -v
```
