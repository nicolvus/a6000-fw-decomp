# S303 — Árbol de referencias de la tabla `0x43ff3200` y callers del dumper de gates

Cuarta sesión del carril B (rev.2). Resuelve los dos pendientes de S176/S153 con un
método **exhaustivo y byte-verificable**: escaneo de todas las codificaciones Thumb
`BL/BLX/B/B.W` del rango de código (`0x43541000..0x43d00000`) y re-decodificación de
cada borde. Sustituye la rev.1 de este informe, que dejaba los callers como pendientes
y contaba 60 entradas en la tabla.

## 1. La tabla `0x43ff3200` tiene 148 entradas, no 60

| Dato | Valor | Verificación |
|---|---|---|
| Base | `0x43ff3200` | literal en el slot GOT `0x4401f080` |
| Entradas | **148** | recorrido hasta el primer valor fuera del rango de punteros |
| Terminador | `0x43ff3450` | siguiente palabra ya no es puntero |
| Rango de destinos | `0x43e95950`..`0x43f9a322` | todos en BSS/datos, ninguno en código |
| Únicos | 148 de 148 | sin duplicados |
| Entrada del estado | índice **18** → **`0x43ff3248`** → `0x43f72d02` | lectura directa |
| Literales absolutos de la base | **1**: `0x4401f080` (slot GOT) | búsqueda de bytes |

La rev.1 se detuvo en 60 entradas (240 B) porque el recorrido se cortó en la primera
zona con ceros; el vector sigue hasta `0x43ff3450`. Los destinos son objetos BSS
inicialmente a cero (16 B verificados en varios), es decir un **directorio de objetos**,
no una tabla de parámetros.

**Por qué no hay xrefs por entrada:** el código carga la base desde el slot y indexa con
`base + 4·i`; no existen literales de las entradas individuales. La consulta de S300 a
`0x43ff3248` devuelve 0 referencias y eso **no** significa que nadie la use: significa
que el acceso es indexado. Los usuarios, por tanto, son los que cargan el slot
`0x4401f080` (siguiente apartado).

## 2. Callers del dumper `FUN_43858338`: dos, no trece

| Sitio | Instrucción | Tipo | Función contenedora |
|---|---|---|---|
| `0x43859868` | `bl #0x43858338` | bl | `0x43859710` |
| `0x43859892` | `bl #0x43858338` | bl | `0x43859710` |

Las dos llamadas están en `FUN_43859710` (`push.w {r4,r5,r6,r7,r8,lr}` en
`0x43859710`), separadas por el `bl 0x43857f88` que consulta el predicado del gate `+0`.
El escaneo es exhaustivo para llamadas **directas**; no hay ninguna otra `BL/B.W` a
`0x43858338` en 8,2 MB de código.

## 2b. Contraste con REA y usuarios del slot GOT `0x4401f080`

REA confirma a nivel de función lo anterior: `procedure_callers(0x43858338)` devuelve
**una** función (`0x43859710`) con dos sitios de llamada, y
`procedure_callers(0x43859710)` devuelve **cinco** funciones (`0x437b59b8`,
`0x437b5b14`, `0x437b5f98`, `0x43859944`, `0x43aef67a`). Tres de mis diez sitios
(`0x437b5a38`, `0x437b5a90`, `0x437b6246`) caen en **huecos de cuerpo de Ghidra**
(`resolve_containing_procedure` = «not in procedure»), pero los bytes confirman que son
`bl`/`b.w` reales; por eso la tabla conserva las dos columnas: `container_rea` y
`container_heuristic`.

**El slot `0x4401f080` es invisible para REA:** `xrefs` y `inspect_native_instruction`
devuelven vacío y `status = undecodable`. Eso **no** prueba ausencia. Por bytes, el slot
se carga en **`0x4378bb6c`** (`ldr r1,[r5,r2]`), donde `r5` es la base GOT `0x4401eee4`
(`0x4378bb64` + `add r5,pc` en `0x4378bb68`, comprobado con los literales del pool) y `r2`
vale `0x19c` (pool `0x4378bbf0`). `0x4401eee4 + 0x19c = 0x4401f080`. El valor cargado se
pasa como argumento a `0x435613e8` (junto a una cadena), es decir una ruta de
diagnóstico/log que recibe la base de la tabla, no un indexador.

Barrido complementario: solo **5** sitios en todo el código cargan el literal `0x19c`
como offset (`0x4378bb66`, `0x4378bd6c`, `0x4378bfe2`, `0x4378c290`, `0x4378c404`, todos
en la misma región `0x4378xx`). Los `add.w rX,#0x19c` (40 sitios) son en su mayoría
offsets de estructura, no de GOT; distinguirlos exige seguir la base de cada función y
queda **NO_VERIFICADO**. Conclusión: **un** usuario demostrado por bytes, sin prueba de
que sea el único.

## 3. Callers de `FUN_43859710`: 10 sitios en 7 funciones

| Sitio | Instrucción | Tipo | Función contenedora |
|---|---|---|---|
| `0x437b5a20` | `b.w #0x43859710` | b.w | `0x437b59b8` |
| `0x437b5a38` | `bl #0x43859710` | bl | `0x437b5a30` |
| `0x437b5a90` | `b.w #0x43859710` | b.w | `0x437b5a30` |
| `0x437b5b20` | `bl #0x43859710` | bl | `0x437b5b14` |
| `0x437b5cc8` | `bl #0x43859710` | bl | `0x437b5b14` |
| `0x437b6100` | `bl #0x43859710` | bl | `0x437b5f98` |
| `0x437b6110` | `bl #0x43859710` | bl | `0x437b5f98` |
| `0x437b6246` | `bl #0x43859710` | bl | `0x437b617e` |
| `0x438599c6` | `b.w #0x43859710` | b.w | `0x43859944` |
| `0x43aef6b4` | `b.w #0x43859710` | b.w | `0x43aef67a` |

`FUN_43859710` es el bucle de volcado de estado (S157 lo llama «snapshot»), no un
manejador de captura: lee `+5/+0x1f/+1/+2/+0x24/+0x2e`, llama al dumper y escribe
contadores. Destaca que **`FUN_43859944`** (el lector de snapshot de S157) lo invoca por
cola (`b.w 0x438599c6`), y que `FUN_43859944` tiene a su vez **35 llamadas directas**
(medidas en este barrido), lo que lo convierte en el nodo más conectado del árbol.

## 4. Tercer nivel (resumen)

| Función | Callers directos |
|---|---:|
| `0x437b59b8` | 1 (`0x43aef4d8`) |
| `0x437b5a30` | 1 (`0x437b4dd8`) |
| `0x437b5b14` | 1 (`0x437b4e10`) |
| `0x437b5f98` | 1 (`0x43aef4b2`) |
| `0x437b617e` | **0** (solo alcanzable por vía indirecta o no alcanzable) |
| `0x43859944` | **35** |
| `0x43aef67a` | 1 (`0x43aef4fa`) |

Que `0x437b617e` no tenga llamadas directas es un resultado **negativo local**: puede
entrarse por puntero de función, tabla o cola. No se concluye inalcanzabilidad.

## 5. Corrección de las direcciones de la rev.1 / S304

La revisión anterior publicó `FUN_438581e8` como dumper y `FUN_43858390` como su caller
único con 13 llamadas. Ambas direcciones son **entradas reales + 0x58**:

| Dirección publicada | Bytes | Decodificación | Qué es en realidad |
|---|---|---|---|
| `0x438581e8` | `1ca0b8f5` | `adr r0, #0x70` | interior de `FUN_43858190` (prólogo en `0x43858190`) |
| `0x43858390` | `4b467844` | `mov r3, sb` | interior de `FUN_43858338` (prólogo `push.w` en `0x43858338`) |

`0x43858190 + 0x58 = 0x438581e8` y `0x43858338 + 0x58 = 0x43858390`: es el mismo sesgo
sistemático que ya se corrigió en S300. Las «13 llamadas» de la rev.1 son instrucciones
internas del propio dumper desplazadas, no llamadas. La comprobación decisiva es que
`0x43858338` decodifica como `push.w {r4,r5,r6,r7,r8,sb,sl,lr}` y `0x43858390` como
`mov r3, sb` (mitad de una instrucción anterior).

También se corrige la afirmación de que el gate `+3` se lee en `state+4`: la instrucción
es `ldrb r3,[r6,#3]` en `0x438583b0` (bytes `f3 78`), verificada en S300 y S301.

## 6. Límites

- Solo llamadas **directas** `BL/BLX/B/B.W`; no cubre llamadas por registro, punteros en
  tablas, ni retornos.
- Rango escaneado `0x43541000..0x43d00000` (todo el código observado); más allá solo hay
  datos.
- Las funciones contenedoras del nivel 2/3 son **INFERENCIA** por prólogo más cercano
  (heurística), no símbolos de Ghidra.
- Alcanzabilidad **runtime** de una captura: `NO_VERIFICADO`. Que exista un camino
  estático no prueba que se ejecute al disparar.
- Los usuarios del slot GOT `0x4401f080`: **1 demostrado** (`0x4378bb6c`); REA no los ve
  (slot undecodable) y los 40 `add.w #0x19c` no se han desambiguado uno a uno. No se
  afirma que sea el único usuario.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s303_ref_tree/build_tree.py
python3 analysis/s303_ref_tree/verify_tree.py
python3 -m unittest tests.test_s303_ref_tree -v
```
