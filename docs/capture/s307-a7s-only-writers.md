# S307 — Las escrituras A7S de `+0xde` y `+0xe6..+0xea` están en código que la A6000 no tiene

Quinta sesión del carril B. S301 encontró que la A7S escribe en su estado cuatro campos que
la A6000 no escribe: `+0xde` y el trío `+0xe6/+0xe8/+0xea`. Esta sesión responde **de dónde
salen** y si ese código existe en la A6000.

**Resultado:** las tres instrucciones del trío y la de `+0xde` pertenecen a funciones cuya
secuencia de store (24 B alrededor) **no aparece en la A6000** (0 coincidencias). Dos
escritores de `+0x02` también son exclusivos de la A7S; en cambio los de `+0x00` y uno de
`+0x02` sí tienen gemelo en la A6000. Es decir, la A7S añade un bloque de código de
parámetros/tiempos que la A6000 no tiene.

## 1. Escritores y presencia en la A6000

| Función A7S | Campo | Store | Instrucción | Veces en A6000 |
|---|---|---|---|---|
| `0x43865100` | state+0xde | `0x4386521a` | `strb.w r5, [r3, #0xde]` | 0 |
| `0x438642f0` | state+0xe6/+0xe8/+0xea | `0x438643a6` | `strh.w r0, [r4, #0xe6]` | 0 |
| `0x438642f0` | state+0xe6/+0xe8/+0xea | `0x438643b2` | `strh.w r0, [r4, #0xe8]` | 0 |
| `0x438642f0` | state+0xe6/+0xe8/+0xea | `0x438643bc` | `strh.w r0, [r4, #0xea]` | 0 |
| `0x4385352c` | state+0x02 | `0x438536a0` | `strb r2, [r3, #2]` | 0 |
| `0x4385352c` | state+0x02 | `0x438536d0` | `strb r0, [r3, #2]` | 0 |
| `0x4385a290` | state+0x00 | `0x4385a334` | `strb r3, [r2]` | 1 |
| `0x4385a384` | state+0x02 | `0x4385a67c` | `strb r4, [r3, #2]` | 0 |
| `0x4385a98c` | state+0x02 | `0x4385a9c6` | `strb r3, [r1, #2]` | 1 |

Lecturas del mismo bloque (contexto):

| Función | Campo | Sitios | Veces en A6000 |
|---|---|---|---|
| `0x438642f0` | `+0xae` (u16 ×1000), `+0xe6` | `0x43864732`, `0x438647ec` | 0 |

La firma es la ventana de 24 bytes `[store−8, store+16)`, que incluye el inmediato del campo
(`#0xde`, `#0xe6`, `#0xe8`, `#0xea`). Una coincidencia de 0 significa que esa secuencia
exacta no está en el otro firmware.

## 2. La función de tiempos `FUN_438645be`

`FUN_438645be` (`push {r4,r5,r6,r7,lr}`) contiene:

- lectura de `state+0xae` (`0x43864732`) y multiplicación por 1000 (`muls r7,r3,#0x3e8`);
- llamada a `FUN_438642f0` (`0x438647e6`, `0x4386484e`) que escribe el trío `+0xe6/+0xe8/+0xea`
  tras tres divisiones por 10;
- llamada a `FUN_43865100` (`0x438648b0`) que escribe `state+0xde` en su epílogo;
- lecturas de `+0xe0/+0xe2/+0xe4` y de `+0xe6`.

**Pero no tiene llamadas directas ni aparece como literal de 32 bits en todo el blob.**
Se entra por vía indirecta (puntero de función, tabla o salto calculado), que este método no
resuelve. Por tanto su **alcanzabilidad runtime es NO_VERIFICADA**, aunque su contenido
(tiempos ×100/milisegundos) es coherente con un bloque de configuración de exposición.

## 3. Relación con el modo Silent

El selector `0x43826d58` (S302) traduce `tipo==2` → `0x4e/0x4f`. Sus **únicos** dos callers
directos son `0x4354908c` y `0x43826df2`. Ninguno de los dos llama directamente a
`FUN_438645be`, `FUN_438642f0` ni `FUN_43865100`: el modo silencioso y este bloque de tiempos
**no están conectados por una llamada directa**. La conexión, si existe, es por valor de modo
a través de estructuras; queda **NO_VERIFICADA**.

Esto es coherente con S204 (la A7S implementa Silent por drive mode + tabla de timings) y con
S301/S302 (los gates y la matriz de registros no distinguen los modos silent), pero **no
demuestra** que `+0xde/+0xe6..+0xea` sean el mecanismo: solo muestra que la A7S tiene código
de tiempos que la A6000 no tiene y que escribe un cluster propio.

## 4. Límites

- «Ausente en la A6000» = la firma exacta de 24 B no aparece. No prueba que no exista una
  función equivalente reescrita con otro registro/orden.
- Los callers directos se obtienen por escaneo exhaustivo `BL/BLX/B/B.W`; una llamada
  indirecta no se ve.
- Semántica física de `+0xae/+0xde/+0xe6/+0xe8/+0xea`: **NO_VERIFICADA**.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s307_a7s_writers/build_writers.py
python3 analysis/s307_a7s_writers/verify_writers.py
python3 -m unittest tests.test_s307_a7s_writers -v
```
