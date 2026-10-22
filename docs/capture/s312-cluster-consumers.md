# S312 — Todos los consumidores del cluster A7S `+0xae`/`+0xde..+0xea` son código A7S

Décima sesión del carril B. S301/S307 localizaron las escrituras exclusivas de la A7S.
Esta sesión cierra el círculo: **quién lee** ese cluster y si ese código existe en la A6000.

**Resultado:** los seis sitios de lectura del cluster están en **seis funciones, todas con 0
coincidencias** de sus primeros 24 bytes en la A6000. El cluster y sus consumidores forman
un subsistema exclusivo de la A7S.

## Consumidores

| Sitio | Función | Campos | Veces en A6000 |
|---|---|---|---|
| `0x438477d4` | `0x438477a0` | `+0xe0`, `+0xe2` | 0 |
| `0x438478ee` | `0x438477a0` | `+0xe4` | 0 |
| `0x43861a8a` | `0x43861a58` | `+0xdf` | 0 |
| `0x4386271a` | `0x438625a0` | `+0xdf` | 0 |
| `0x4386430e` | `0x438642f0` | `+0xe6` | 0 |
| `0x43864730` | `0x438645bc` | `+0xae`, `+0xe6` | 0 |
| `0x43864e3e` | `0x43864cb0` | `+0xde` | 0 |

Funciones únicas: `0x438477a0`, `0x43861a58`, `0x438625a0`, `0x438642f0`, `0x438645bc`,
`0x43864cb0`. Todas ausentes en la A6000 (firma de 24 B).

## Contexto de dos consumidores

- `0x4385f192` (caller de `0x438477a0`) escribe `+0xf8/+0xfa/+0xfc` de otro objeto justo
  antes de llamar: patrón de **volcado de parámetros de tiempo** a un destino, no de captura.
- `0x43864cb0` lee `+0xde`; es llamado desde `0x438629ae`, en la misma región que el bloque
  de configuración (`0x4386xxxx`).

Es decir, el cluster `+0xde..+0xea` se **produce** en el bloque de tiempos (S307) y se
**consume** en funciones de configuración/volcado, todas A7S.

## Interpretación (INFERENCIA)

El cuadro completo de las sesiones S300–S312:

| Evidencia | A6000 | A7S |
|---|---|---|
| Gates `+3/+6` del estado | flags de dumper, sin escritor | idénticos, sin escritor |
| Matriz de registros por modo | 59 filas, columna directa | 69 filas + 34 códigos + mapa |
| Selector con `tipo` | no existe | `0x43826d58` → `0x4e/0x4f` |
| Bloque de tiempos y cluster `+0xae/+0xde..+0xea` | **no existe** | presente, con consumidores propios |

La hipótesis más económica: el obturador silencioso de la A7S vive en el **drive mode**
(códigos `0x4e/0x4f`) y en este subsistema de tiempos, no en los gates ni en la matriz de
registros. **No se demuestra** que el cluster *sea* el mecanismo; se demuestra que es
código exclusivo de la cámara que sí tiene silent shutter.

## Límites

- Presencia por firma de 24 B; una reescritura equivalente no se detecta.
- No se resuelve el objeto/vtable del selector (S310) ni el consumidor último del modo.
- Semántica física de los campos: **NO_VERIFICADA**.
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s312_cluster_consumers/build_consumers.py
python3 analysis/s312_cluster_consumers/verify_consumers.py
python3 -m unittest tests.test_s312_cluster_consumers -v
```
