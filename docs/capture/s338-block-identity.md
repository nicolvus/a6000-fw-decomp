# S338 — El bloque de destino es DFE/CISIF (carril B)

22-10-2026. Carril B. Sesión S338. **Solo lectura estática; sin firmware en ejecución, sin cámara, sin flasheo.**

## Pregunta

S335 midió que las máscaras acaban en `0xfc02a00c` y en `0xf292b000..8`. ¿Qué bloque es cada uno?

## Veredicto

| Afirmación | Clasificación | Evidencia |
|---|---|---|
| `0xfc02a00c` es el **cuarto DWORD** del bloque `0xfc02a000` | **VERIFICADO** | `register − base = 0xC`; literales de `0xfc02a000` en ambos blobs |
| El bloque `0xfc02a000` se usa en ambos modelos: hay un *getter* que devuelve `base+8` y un *writer* a `base` | **VERIFICADO** | A7S `0x436f2014` (`adds r3,#8; str r3,[r0]`) y `0x436f202c` (`str r0,[r3]`); A6000 `0x436d2c9c` y `0x436d2cb4` |
| El bloque es el **DFE** | **INFERENCIA ALTA** | El mapa Ghidra del repo (`analysis/ghidra/efcs-dfe-base-map.json`, `FUN_436d1c98`, cadena `DFE_INIT_Start`) hace `_DAT_fc02a008 |= 8`; el bloque aparece en las cadenas `DFECore` (22 sitios A7S / 143 A6000) |
| El receptor es **CISIF** (códigos de sincronía / carriles) | **INFERENCIA ALTA** | S56-B documenta el mismo par de tablas `0x43bc20dc`/`0x43bc2248` y el mismo colapso de 12 pares (carril, bit) → máscara u16 alimentando CISIF (`SIF SetSyncCode`, `SIFSyncCode`, presentes en ambos blobs) |
| El transporte P2S de registros (`0xfc088300`, S56) **no** se ve afectado | **VERIFICADO (por dirección)** | Las únicas escrituras de esta cadena son a `0xfc02a00c` y `0xf292b000..8` |
| `0xf292b000` | **NO_VERIFICADO** | Sin símbolos ni documentación; único vecino documentado en `0xf292xxxx`: DSP de lente `0xf292d000` (S66) |

**S51 no cambia (A = NO, B = NO, C = NO).**

## 1. El bloque `0xfc02a000`

Literales en ambos firmwares:

| Modelo | Sitios del literal `0xfc02a000` | Getter `base+8` | Writer de `base` |
|---|---|---|---|
| A7S | `0x436f2034`, `0x436f2044` | `0x436f2014` | `0x436f202c` |
| A6000 | `0x436d2cbc`, `0x436d2d78` | `0x436d2c9c` | `0x436d2cb4` |

```
0x436f2014: ldr r3, [pc, #0xc]
0x436f2016: ldr r2, [pc, #0x10]
0x436f2018: add r3, pc
0x436f201a: ldr r3, [r3, r2]     ; *(GOT) = 0xfc02a000
0x436f201c: adds r3, #8          ; 0xfc02a008
0x436f201e: str r3, [r0]         ; devuelve el puntero al registro
```

## 2. Cadena completa del carril B

```
modo (posición en u32[34])
  → matriz de 69 filas (slot 40)                          [S321/S329]
  → tablas T1/T2/T3: descriptor (0/1) + máscara 12 bits    [S329/S331]
  → 12 pares (flag, índice de bit) → máscara u16           [S334]
  → 0x436f822c aplica ~valor ^ máscara
  → accesores de 12 bits: 0xfc02a00c (bloque DFE/CISIF) y 0xf292b000..8  [S335]
```

Es decir: el modo silent del A7S cambia **qué bits de un registro DFE/CISIF** se activan, no la RAM del formateador P2S.

## 3. Correcciones que arrastra esta sesión

- **S334**: la hipótesis «las máscaras acaban en una trama P2S» queda descartada; el destino es un registro del bloque `0xfc02a000`.
- **S332**: el par de tablas `0x43bc20dc`/`0x43bc2248` del A6000 es el mismo que S56-B documentó como CISIF (sync codes / carriles), no una tabla de exposición.

## Límites

- La identificación DFE/CISIF es **INFERENCIA ALTA**: se apoya en el mapa Ghidra del repo y en S56-B (evidencia derivada), más las cadenas presentes en ambos blobs; no hay datasheet del bloque `0xfc02a000`.
- `0xf292b000` sigue sin identificar.
- No se asigna significado físico a los bits del registro ni se afirma efecto sobre el sensor.
- S51 (A/B/C) no cambia.

## Reproducción

```bash
.venv/bin/python analysis/s338_block_identity/build_block_identity.py
.venv/bin/python analysis/s338_block_identity/verify_block_identity.py  # 218 comprobaciones
.venv/bin/python -m unittest tests.test_s338_block_identity              # 9 tests
```

Artefactos: `analysis/s338_block_identity/block_identity.json`, `build_block_identity.py`, `verify_block_identity.py`, `tests/test_s338_block_identity.py`.
