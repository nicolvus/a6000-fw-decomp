# S153 — gates de los descriptores son flags de lectura diagnóstica

S153 sigue la alcanzabilidad parcial de S152. **VERIFICADO:** el despachador
`0x43858338` lee `S_dump+3` y comprueba bit `0x02`, y lee `S_dump+6` y
comprueba bit `0x20`; los `beq` omiten la salida correspondiente cuando el bit
está a cero. Esos accesos gobiernan líneas de volcado de descriptors, no una
escritura/configuración del sensor. **NO_VERIFICADO:** quién pone los bits y si
alguna ejecución los activa.

## Objeto y gates

El puntero al objeto de estado es `0x43f72d02` (slot GOT `0x4401f990`), por lo
que los bytes son `+3=0x43f72d05` y `+6=0x43f72d08`. El cuerpo REA sitúa los
gates en la función de volcado `FUN_43858338` (`ev_886455ee1975b4322bb38b02e4d4326f373aa0505804e3fd75893a2d13eb89d0`);
las instrucciones completas están en `ev_74804f459247fbbe0d22d0b1e7e58bba3e8ee690e33a1b6d20ffacc7020ba7fc`.

| Flag | Instrucciones | Operación |
|---|---|---|
| `+3 & 0x02` | `0x438583b0 ldrb r3,[r6,#3]`; `0x438583b2 tst r3,#2`; `0x438583b6 beq 0x438583ca` | si el bit no está establecido, se salta esa línea de volcado |
| `+6 & 0x20` | `0x438584f0 ldrb r3,[r6,#6]`; `0x438584f2 tst r3,#0x20`; `0x438584f6 beq 0x4385850a` | si el bit no está establecido, se salta esa línea |

Bytes exactos: `f37813f0020f08d0` y `b37913f0200f08d0` (offset = VA −
`0x43541000`); reproducción en `analysis/s153_imager_dump_gates/dump_gates.json`.
REA xrefs de `+3` son ocho lecturas (`ev_2988fcffcf7768198b5e5d25f616294bfa4ee489710012b6f85b06434aabfde4`),
las de `+6` son otras ocho lecturas (`ev_7a31d71d07dc687daced9c48fe2a917ae8a24bf330dd09d4cb5d966c77a1669a`). Los bytes de ambos flags
son cero en la imagen estática (`ev_498f8dc63dab90ff677e302176e0737dcbb3d54be6fc4bc97ad00cafe4ce158d`).

## Escritor y alcanzabilidad: PARCIAL

Las consultas de xrefs exactas a los dos bytes muestran lectores del dumper; no
revelan un escritor. No se identificó un escritor reproducible para `+3`/`+6`
en esta tarea. Tampoco se descarta escritura mediante copia de bloque, DMA o
ruta no decodificada; por ello no se afirma ausencia global.

Los llamadores estáticos observados (`0x43859868` y `0x43859892`) usan el
copiador raw; que el call site exista no demuestra que se ejecute. El contenido
del estado estático no informa su valor runtime. **Conclusión:** los bits son
gates de formato/registro en esta ruta diagnóstica; si habilitan la lectura
del byte gap en una captura es **NO_VERIFICADO**. No altera S51 y no atribuye
ningún efecto físico al sensor.

```sh
python3 analysis/s153_imager_dump_gates/verify_gates.py
python3 -m unittest tests.test_s153_imager_dump_gates -v
```
