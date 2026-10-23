# S341 — Síntesis del carril B: la cadena modo→registro y sus correcciones (S314–S340)

22-10-2026. Sesión de consolidación del carril B. **No introduce hallazgos nuevos**: cada cifra remite a su JSON y está comprobada por `analysis/s341_synthesis_b2/verify_synthesis.py` (27 cifras). Sustituye a `docs/capture/s313-synthesis-carril-b.md` en lo que quedó corregido.

## 1. La cadena, de extremo a extremo

```
modo (código)  →  posición en la lista u32[34]          (A7S)  /  u32[13] (A6000)
  →  matriz de registros (slot 40): 69 vs 59 filas, 15 vs 13 columnas
  →  tablas T1/T2/T3: (w0 selector, +4/+5/+6 selectores, +0x14 descriptor, +0x18 máscara)
  →  12 pares (flag, índice de bit) → máscara u16 (obj+0x68 / obj+0xf8)
  →  0x436f822c aplica ~valor ^ máscara
  →  MMIO: 0xfc02a00c (bloque DFE/CISIF 0xfc02a000) y 0xf292b000..8 (sin identificar)
```

## 2. Cifras verificadas

| # | Afirmación | Valor | Sesión |
|---|---|---|---|
| 1 | Filas de la matriz A7S | **69** (`0x43fee598`) | S321 |
| 2 | Códigos de modo | **34** A7S / **13** A6000; 12 compartidos, `0x2f` solo A6000 | S333 |
| 3 | Vectores de registro distintos | **15/34** A7S / **7/13** A6000 | S333 |
| 4 | Bases de T1/T2/T3 | `0x43bbeb70` / **`0x43bbf2e8`** / **`0x43bbef30`** | S329 |
| 5 | Filas por tabla T | 34 × `0x1c` B | S317/S329 |
| 6 | Descriptor (filas) | **2** A7S / **3** A6000 (identidad + permutación + `1,1,1,1,0,…`) | S329/S332 |
| 7 | Máscaras cero | **30** en A7S / **0** en A6000 | S332 |
| 8 | `0x4e` vs `0x4c` / `0x4f` vs `0x4d` (matriz) | **14** / **11** registros distintos; `0x4c≡0x4d` | S329 |
| 9 | Fila de T | **posición del modo** (no `obj+0x2b4`, que es un flag de log) | S331 |
| 10 | Pares | `(flag, índice de bit)` → máscara u16 en `obj+0x68` / `obj+0xf8` | S334 |
| 11 | Referencias a T1/T2/T3/B | **13** en **7** funciones; 5 leen campos de fila | S336 |
| 12 | Destino final | **MMIO**: `0xfc02a00c` (bloque `0xfc02a000`, DFE/CISIF) y `0xf292b000..8` | S335/S338 |
| 13 | P2S | **no** participa en esta cadena (la RAM `0xfc088300` no se toca) | S335/S338 |
| 14 | `w0` | **selector de canal MMIO**: 6 casos (`0xf3122xxx`, `0xfc0a3xxx/4xxx`), offset `+0x30`/`+0x24` | S340 |
| 15 | Límite del setter | **`0x47`** A6000 / **`0x51`** A7S → `0x4e`/`0x4f` fuera del vocabulario A6000 | S324 |

## 3. Qué distingue al silent (A7S) en esta cadena

1. **Vocabulario**: `0x4c`–`0x51` existen solo en el A7S (22 códigos exclusivos).
2. **Matriz**: `0x4c`/`0x4d` y `0x4e`/`0x4f` difieren en 14 y 11 registros; pero `0x4c`/`0x4d` comparten vector con `0x32`/`0x33`/`0x34` y `0x4e`/`0x50`, `0x4f`/`0x51` son alias → **no hay un vector de registro exclusivo de silent**.
3. **Tabla T2**: la máscara de 12 bits es `0x3ff` en `0x4c`/`0x4d` y **0** en `0x4e`/`0x4f` (y en `0x50`/`0x51`). Es la única diferencia de las tres tablas T entre esos pares.
4. **Códigos de operación**: `0x4c`–`0x4f` usan (T1=0, T2=2); `0x50`/`0x51` usan (1, 3) — son los sub-modos, no los silent, los que cambian de operación.
5. **Destino**: registro del bloque DFE/CISIF; no hay paso por P2S.

## 4. Correcciones que esta síntesis asume (y que sustituyen a S313)

- El mapa `0x43c9c5b5` es **posición→columna** (34 entradas), no `modo→columna` (S325).
- La matriz **sí** distingue los modos silent (14/11 registros); el «comparte columna 1» de S302/S321 queda superado (S325/S329).
- Las bases de T2/T3 publicadas en S317/S326 estaban **4 B altas** (S329).
- La fila de T se elige por la **posición del modo**; `obj+0x2b4` es un **flag de log** (S331), no un índice (S327/S330).
- Los pares **no** llevan valores: llevan índices de bit (S334).
- El destino **no** es P2S, es MMIO DFE/CISIF (S335/S338).
- `w0` **no** es un código de operación abstracto: es un selector de canal MMIO (S340).

## 5. Preguntas abiertas (con el experimento que las cerraría)

| Pregunta | Estado | Qué haría falta |
|---|---|---|
| Qué mide cada canal `0xf3122200/2300/3200/3300`, `0xfc0a3100/4100` | NO_VERIFICADO | datasheet del SoC o traza de sus valores en runtime |
| Qué bloque es `0xf292b000..8` | NO_VERIFICADO | datasheet/símbolos; solo la capa de máscaras lo usa |
| Semántica física de las máscaras (bits 0..11 + bit 12) | NO_VERIFICADO | datasheet del DFE/CISIF |
| Efecto real del cambio de máscara T2 en los modos silent | NO_VERIFICADO | ejecución/traza (prohibida en este proyecto sin autorización) |
| Consumidor indirecto de `0x43fef404` | NO_VERIFICADO | rastreo de punteros `0x43f9c6xx` |

## Límites

- Todo el carril es estático: sin firmware en ejecución, sin cámara, sin flasheo.
- Las identificaciones DFE/CISIF son INFERENCIA ALTA (mapa Ghidra del repo + S56-B + cadenas), no datasheet.
- S51 (A/B/C) no cambia: nada de lo medido demuestra obturador electrónico a resolución completa en la A6000.

## Reproducción

```bash
.venv/bin/python analysis/s341_synthesis_b2/verify_synthesis.py   # 27 cifras
```

## Siguiente

S341 deja el carril en estado publicable. Prioridades propuestas: (1) identificar los canales de `w0` con la documentación del SoC si aparece; (2) rastrear punteros `0x43f9c6xx` para `0x43fef404`; (3) comparar el efecto de las máscaras T2 entre A6000 y A7S para los modos equivalentes (`0x0b` vs `0x0b`).
