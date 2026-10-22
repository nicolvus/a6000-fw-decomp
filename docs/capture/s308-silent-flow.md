# S308 — A dónde va el modo Silent y cómo entra el bloque de tiempos

Sexta sesión del carril B. Cierra dos cabos de S302/S307: (a) qué hace el caller del
selector `0x43826d58` con el código de modo que devuelve, y (b) cómo se entra en el bloque
de tiempos que escribe `+0xde`/`+0xe6..+0xea` (S307).

**Resultado:** el código de modo Silent (`0x4e/0x4f`) se guarda en pila y se pasa a
`0x43ad9704`, un **thunk de llamada virtual** (S310): **no** va directo al bloque de
tiempos. El bloque de tiempos tiene **un único caller directo**, `0x43861be4`, dentro de
una ruta de configuración. El enlace silent→tiempos sigue **NO_VERIFICADO**.

## 1. El resultado del selector va a un constructor de mensajes

En el call site `0x4354908c` (función de configuración grande, en `0x4354xxxx`):

| Dirección | Instrucción | Papel |
|---|---|---|
| `0x43549084` | `ldr.w r1,[r3,#0x21c]` | argumento `sub` del selector |
| `0x43549088` | `ldr.w r2,[r3,#0x220]` | argumento `tipo` |
| `0x4354908c` | `bl 0x43826d58` | selector Silent (S302) |
| `0x43549098` | `str r0,[sp,#0x2c]` | guarda el código de modo |
| `0x435490c4` | `bl 0x43ad9704` | lo pasa al constructor/despachador |

Es decir, el modo (`0x4e/0x4f` cuando `tipo==2`) entra como argumento de una **llamada
virtual** (`obj->vtable[0x64]`, ver S310), no en una llamada al bloque de tiempos.

## 2. Entrada del bloque de tiempos (corrección de S307)

La entrada real es `0x438645bc` (`sub sp,#0x10` + `push {r4,r5,r6,r7,lr}`). S307 buscaba
`0x438645be` y concluía «sin llamadas directas»: era un error de un byte. El `bl` va a
`0x438645bc` y hay **exactamente un** caller directo:

| Caller | Contexto |
|---|---|
| `0x43861be4` | copia 0x70 B a pila, elige `r2 ∈ {1,2}` según `[r7+0x484]`/`[r7+0x485]`, pasa 4 argumentos (`ldm r4,{r0..r3}`) y después encadena `0x43864c34/c74/c80/c90/ca0` |

Ese patrón (buffer + selección de variante + cadena de setters) es una ruta de
**parametrización**, no un manejador de disparo. (INFERENCIA)

## 3. ¿Hay otras entradas?

Se buscaron **todos** los valores de 32 bits del blob que caen en `0x43864xxx`:

| Dónde | Valor | Qué es |
|---|---|---|
| `0x4375526e` | `0x43864770` | literal dentro de código (no puntero de tabla) |
| `0x43be1104` | `0x438643cd` | vtable/rodata → función vecina, no el bloque de tiempos |
| `0x43be6ba4` | `0x438643cd` | ídem |
| `0x4402d2dc` | `0x43864189` | puntero a otra función vecina |

Ninguno apunta a `0x438645bc`: la única entrada es el `bl` de `0x43861be4`. No se
observan tablas de punteros hacia el bloque.

## 4. Estado de la cadena silent → tiempos

```
selector 0x43826d58 (tipo==2 → 0x4e/0x4f)
        └─ 0x4354908c → [sp+0x2c] → 0x43ad9704   (mensaje/despacho)
bloque de tiempos 0x438645bc  ← 0x43861be4        (configuración)
        ├─ lee +0xae (×1000), +0xe0/+0xe2/+0xe4/+0xe6
        ├─ FUN_438642f0 → escribe +0xe6/+0xe8/+0xea
        └─ FUN_43865100 → escribe +0xde
```

Los dos caminos **no se tocan por llamada directa**. Podrían unirse por el valor de modo
en una estructura intermedia; probarlo exige seguir `0x43ad9704` y el consumidor de esa
estructura, que queda como siguiente paso.

## 5. Límites

- Solo transferencias directas y punteros absolutos de 32 bits; no cubre saltos calculados
  ni tablas de offsets relativos.
- La semántica de `0x43ad9704` y de `0x43861be4` es **INFERENCIA** por su forma.
- Que el bloque de tiempos se ejecute en una captura silent es **NO_VERIFICADO**.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s308_silent_flow/build_flow.py
python3 analysis/s308_silent_flow/verify_flow.py
python3 -m unittest tests.test_s308_silent_flow -v
```
