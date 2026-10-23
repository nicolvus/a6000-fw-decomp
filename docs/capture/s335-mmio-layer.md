# S335 — La capa de máscaras termina en MMIO (carril B)

22-10-2026. Carril B. Sesión S335. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S334 dejó abierto si las máscaras `u16` acababan en una trama P2S. ¿Qué hay detrás de `0x436f8290/82a0/82b0/82c0/82d0/82e8/8300/8314/8324`?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| Las nueve funciones son **accesores de 32 bits sobre direcciones absolutas** (MMIO) | **VERIFICADO** | Cada una hace `ldr rX,[pc,#imm]` → literal `0xf…` y `ldr`/`str` directo |
| Escriben en `0xf292b004` y `0xf292b008` y leen `0xf292b000` | **VERIFICADO** | `0x436f8290`→`…b008`, `0x436f82a0`→`…b004`, `0x436f82b0`→`…b000` |
| `0x436f82c0` escribe `0x1000` en `0xf292b008`; `0x436f82d0` escribe `0x10000` en `…b008` o `…b004` según `r0` | **VERIFICADO** | `mov.w r2,#0x1000`; `mov.w r3,#0x10000` + `cbnz r0` |
| `0x436f82e8/8300/8314/8324` operan sobre **`0xfc02a00c`** con un campo de **12 bits** y el **bit 12** | **VERIFICADO** | `bic/orr` + `bfi r1,r2,#0,#0xc`; `bfc r2,#0xc,#1` |
| El camino modo → máscara → registro **termina en MMIO**, no en P2S | **VERIFICADO** | Los nueve accesores apuntan a `0xf…`; la hipótesis P2S de S334 queda descartada |
| La A6000 tiene la **misma capa**, con los mismos literales y el mismo número de sitios | **VERIFICADO** | `0x436dbdf8..0x436dbe8c`; conteos 1/2/3/4 idénticos |
| Qué bloque es `0xf292b000` ni qué controla `0xfc02a00c` | **NO_VERIFICADO** | Sin datasheet ni símbolos |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. Los nueve accesores

| Función | Rol | Destino/fuente |
|---|---|---|
| `0x436f82b0` | lee 12 bits | `0xf292b000` |
| `0x436f82a0` | escribe 12 bits | `0xf292b004` |
| `0x436f8290` | escribe 12 bits | `0xf292b008` |
| `0x436f82c0` | escribe `0x1000` | `0xf292b008` |
| `0x436f82d0` | escribe `0x10000` | `0xf292b008` o `0xf292b004` (`r0`) |
| `0x436f8314` | lee 12 bits | `0xfc02a00c` |
| `0x436f8300` | `orr` 12 bits (RMW) | `0xfc02a00c` |
| `0x436f82e8` | `bic` 12 bits (RMW) | `0xfc02a00c` |
| `0x436f8324` | limpia bit 12 | `0xfc02a00c` |

Forma típica (`0x436f82b0`):

```
0x436f82b0: ldr r3, [pc, #8]     ; literal 0xf292b000
0x436f82b2: ldr r0, [r3]
0x436f82b4: lsls r0, r0, #0x14   ; conserva 12 bits
0x436f82b6: lsrs r0, r0, #0x14
0x436f82b8: bx lr
0x436f82ba: nop
0x436f82bc: .word 0xf292b000
```

Y el RMW (`0x436f8300`):

```
0x436f8300: ldr r3, [pc, #0xc]   ; 0xfc02a00c
0x436f8302: ldr r2, [r3]
0x436f8304: ldr r1, [r3]
0x436f8306: orrs r2, r0
0x436f8308: bfi r1, r2, #0, #0xc ; campo [0:12]
0x436f830c: str r1, [r3]
```

## 2. Consecuencia para la cadena del carril B

La cadena medida queda así:

```
modo (posición) → matriz de registros (slot 40) + tablas T (S329/S331)
   → 12 pares (flag, índice de bit) → máscara u16 (S334)
   → accesor de 12 bits sobre MMIO 0xf292b000..8 / 0xfc02a00c (S335)
```

Es decir: el modo silent del A7S **no** produce un mensaje distinto por sí mismo; cambia qué bits de un registro de hardware se activan (máscara) y con qué código de operación (S334). La escritura final es MMIO directa.

## 3. A6000

La capa equivalente está en `0x436dbdf8..0x436dbe8c`, con los mismos cuatro literales y exactamente el mismo número de sitios por dirección (`0xf292b000`: 1; `…b004`: 2; `…b008`: 3; `0xfc02a00c`: 4). Es la misma capa de acceso, lo que refuerza que el mecanismo de S332 es compartido y que la diferencia A7S/A6000 está en los datos (modos, máscaras, op codes), no en el acceso.

## Límites

- Las direcciones se identifican como MMIO por su rango (`0xf…`) y por el acceso directo; **no hay datasheet** que diga qué bloque es `0xf292b000` ni qué controla `0xfc02a00c`.
- No se ha verificado si el bloque pertenece al driver del sensor, al P2S/DFE o a otro periférico.
- Sin runtime no se observa el efecto de las escrituras.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s335_mmio_layer/build_mmio_layer.py
.venv/bin/python analysis/s335_mmio_layer/verify_mmio_layer.py  # 60 comprobaciones
.venv/bin/python -m unittest tests.test_s335_mmio_layer           # 8 tests
```

Artefactos: `analysis/s335_mmio_layer/mmio_layer.json`, `build_mmio_layer.py`, `verify_mmio_layer.py`, `tests/test_s335_mmio_layer.py`.
