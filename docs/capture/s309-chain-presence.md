# S309 — La cadena silent/config de la A7S no aparece en la A6000

> **Aviso D4 (25-10-2026):** [S310](s310-vtable-thunk.md) rectifica el mecanismo: `0x43ad96fa`/`0x43ad9704` son thunks de llamada virtual, no un constructor de mensajes.

Séptima sesión del carril B. Cierra la pregunta que dejaron S302/S307/S308: ¿la cadena que
selecciona el modo silent y escribe el cluster de tiempos existe en la A6000?

**Resultado:** las **siete** funciones de la cadena tienen 0 coincidencias de sus primeros
24 bytes en el `av-cam.bin` de la A6000. No es que la A6000 escriba otros valores: es que
**ese código no está**. La A6000 tendrá su propia ruta de configuración, pero no es ésta.

## La cadena y su presencia

| Paso | Función A7S | Papel | Veces en A6000 |
|---|---|---|---|
| 1 | `0x43548c70` | configura y llama al selector | **0** |
| 2 | `0x43826d58` | `tipo==2` → `0x4e/0x4f` | **0** |
| 3 | `0x43ad96fa` | constructor de mensaje que recibe el modo | **0** |
| 4 | `0x43861a58` | buffer 0x70 B + variante 1/2 + llamada al bloque | **0** |
| 5 | `0x438645bc` | lee `+0xae`, escribe `+0xde`/`+0xe6..+0xea` | **0** |
| 6 | `0x438642f0` | escribe `+0xe6/+0xe8/+0xea` | **0** |
| 7 | `0x43865100` | escribe `+0xde` | **0** |

Firma = primeros 24 bytes del prólogo. Una firma de 12 bytes de `0x438642f0` sí aparecía una
vez en la A6000, pero era un prólogo genérico (`push; sub sp; movs r2,#0xc; mov r4,r0`); con
24 bytes desaparece. Por eso el criterio de este informe son 24 B.

## Qué implica

- La diferencia A7S↔A6000 **no** es un valor distinto en el mismo código: es **código
  ausente**. Encaja con S204 (modos `0x4e/0x4f` solo en la A7S) y con S301/S302 (gates y
  matriz de registros iguales, sin rastro del silent).
- Los campos `+0xde/+0xe6/+0xe8/+0xea` no tienen escritor en la A6000 porque no hay código
  que los escriba (S300: 0 escrituras en 67 sitios).
- La A6000 sí tiene su propia ruta de configuración: escribe `+0x02` desde cuatro funciones
  (S300) y lee `+0x7f` en exclusiva. No se comparan aquí esas rutas.

## Límites

- Coincidencia exacta de 24 B: una función equivalente **reescrita** (otros registros, otro
  orden) no se detectaría. No se afirma «la A6000 no puede hacerlo», solo «este código no está».
- No se sigue el consumidor del mensaje de `0x43ad96fa`; el enlace modo→tiempos sigue
  **NO_VERIFICADO** (S308).
- Sin firmware ejecutado, sin cámara, sin flasheo. S51 no cambia.

```sh
python3 analysis/s309_chain_presence/build_presence.py
python3 analysis/s309_chain_presence/verify_presence.py
python3 -m unittest tests.test_s309_chain_presence -v
```
