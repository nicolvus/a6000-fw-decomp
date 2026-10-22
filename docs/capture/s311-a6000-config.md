# S311 — La ruta de configuración de la A6000 también es código propio

Novena sesión del carril B. S309 mostró que la cadena silent/config de la A7S no aparece en
la A6000. Esta sesión hace la comprobación simétrica: ¿la ruta que en la A6000 escribe
`+0x00`/`+0x02` aparece en la A7S?

**Resultado:** dos de los cuatro escritores de la A6000 **no** están en la A7S y dos sí
(probablemente helpers compartidos). Ninguna cámara contiene el código de la otra: cada una
tiene su propia ruta de configuración y comparten solo piezas sueltas.

## Escritores de la A6000 y su presencia en la A7S

| Función A6000 | Campo | Stores | Veces en A7S | Callers directos |
|---|---|---|---|---|
| `0x43833ff8` | `state+0x02` | `0x4383415a`, `0x4383418a` | **0** | 2 |
| `0x4383ace0` | `state+0x02` | `0x4383afd0` | **0** | 1 |
| `0x4383b2dc` | `state+0x02` | `0x4383b316` | 1 (compartida) | 2 |
| `0x4383abec` | `state+0x00` | `0x4383ac90` | 1 (compartida) | 2 |

Firma = primeros 24 bytes del prólogo; el test vuelve a contar en el blob de la A7S.

## Lectura conjunta con S307/S309

| Pieza | A6000 | A7S |
|---|---|---|
| Escritores de `+0x00`/`+0x02` | 4 funciones, 2 exclusivas | 4 funciones, 2 exclusivas |
| Escritores de `+0xde`, `+0xe6..+0xea` | **no existen** | 2 funciones exclusivas |
| Selector de modo con `tipo` | **no existe** | `0x43826d58` |
| Cadena de tiempos | **no existe** | `0x43548c70` → … → `0x438645bc` |

La interpretación más simple y consistente con los bytes: **cada firmware trae su propio
código de configuración**, y el de la A7S incluye un bloque de tiempos y un selector de modo
silencioso que la A6000 no tiene. No es un parámetro distinto en el mismo sitio.

## Límites

- Presencia por firma de 24 B: una reescritura equivalente no se detecta.
- Los callers son solo directos (`BL/BLX/B/B.W`).
- No se compara la *semántica* de las dos rutas de configuración, solo su identidad de código.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s311_a6000_config/build_config.py
python3 analysis/s311_a6000_config/verify_config.py
python3 -m unittest tests.test_s311_a6000_config -v
```
