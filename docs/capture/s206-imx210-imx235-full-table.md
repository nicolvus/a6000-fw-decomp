# S206 — Tabla completa de registros: IMX210 (A6000 fw3.21) vs IMX235 (A7S fw3.20)

22-10-2026. Agente A (sensor y driver), sesión S206 (rango S200–S299). **Solo investigación estática; sin ejecutar firmware, sin cámara, sin flasheo.**

## Veredicto resumen

| Clasificación | Cantidad | Detalle |
|---|---:|---|
| **IDÉNTICO** | 0 | — |
| **DISTINTO** | 119 | Todos los registros sombra IMX210 (esquema de dirección y valores distintos a IMX235) |
| **AUSENTE EN A6000** | 0 | — |

**Conclusión:** no hay correspondencia por dirección entre los registros sombra del IMX210 (119, direcciones `0x000`–`0x155`) y los registros matriz del IMX235 (35, direcciones `0x0000`–`0x00CF`). Cada familia de sensores tiene su propio conjunto de modos de lectura y su propio mapa de registros (S57-D.5 vigente). Clasificación global: **DISTINTO**.

## Metodología

- **IMX210:** 119 registros sombra del vector `0x43fe995c` (S56 rec_map.json, vigente tras contradiction-audit). Cada entrada: `{dirección, id u16, dato u8, funciones que la escriben}`.
- **IMX235:** matriz de modos `0x43fee370` (34 modos) + filas `0x43fee598` (35 registros, 5 B cada uno: `{dev, 0, dir u16, dato}`) (S57 vigente).
- **Comparación:** dirección por dirección; sin solapamiento (S57-D.5: "No hay correspondencia por dirección").

## Tabla por subsistema

| Subsistema | Registros IMX210 | Registros IMX235 equivalentes | Clasificación | Veredicto |
|---|---:|---:|---|---|
| Selección de modo de lectura | ID1 (1 reg: `0x4401ca2c`/`0x4401c734` duplicado) | Ninguno (modos en matriz estática, no registros sombra) | **DISTINTO** | VERIFICADO (rec_map ID1; matriz `0x43fee370`) |
| Temporización de exposición | ID3–ID8 (6 regs: svd/shd/spl) | Ninguno (tiempos en columnas de modo estático) | **DISTINTO** | VERIFICADO (rec_map ID3-8; S57-C; matriz `0x43fee598`) |
| Configuración P2S / sensor | 112 registros (IDs 0, 2, 9–341) | Ninguno (esquema de dirección distinto) | **DISTINTO** | VERIFICADO (rec_map; sin solapamiento de direcciones) |

## Detalle de registros clave

| Registro IMX210 | ID | Dato por defecto | Funciones escritoras | Equivalente IMX235 | Clasificación |
|---|---:|---:|---|---|---|
| `0x4401ca2c` / `0x4401c734` | 1 (duplicado A/B) | 0x40 | `0x436d6f70`, `0x436d7bc8` | Ninguno (modo en matriz) | DISTINTO |
| `0x4401c7e0` | 3 (svd bajo) | 0 | `0x436d6f70`, `0x436d7bc8` | Ninguno (svd en columna modo) | DISTINTO |
| `0x4401c678` | 4 (svd alto) | 0 | `0x436d6f70`, `0x436d7bc8` | Ninguno | DISTINTO |
| `0x4401c744` | 5 (shd bajo) | 2 | `0x436d6f70`, `0x436d7bc8` | Ninguno | DISTINTO |
| `0x4401c684` | 6 (shd alto) | 0 | `0x436d6f70`, `0x436d7bc8` | Ninguno | DISTINTO |
| `0x4401c698` | 7 (spl bajo) | 0 | `0x436d6f70`, `0x436d7bc8` | Ninguno | DISTINTO |
| `0x4401c764` | 8 (spl alto) | 0 | `0x436d6f70`, `0x436d7bc8` | Ninguno | DISTINTO |
| Otros 112 registros | 0, 2, 9–341 | varios | varios (ver rec_map) | Ninguno | DISTINTO |

## Comparación arquitectónica (A7S vs A6000 en este punto)

| Aspecto | IMX210 (A6000) | IMX235 (A7S) |
|---|---|---|
| Estructura de registros | 119 registros sombra (vector `0x43fe995c`), acceso vía puntero en registro (S205) | Matriz estática 34 modos × 35 registros (`0x43fee370`/`0x43fee598`) |
| Selector de modo | `S[0]` en estructura `S` (S205: escritor NO_VERIFICADO) | Selector `0x43826d58` drive mode `tipo==2` → `0x4e`/`0x4f` (S201) |
| Modos Silent | Ninguno (13 modos, `SetMode` rechaza `0x4e`/`0x4f`) | `0x4e`/`0x4f` dedicados (columnas 29, 30) |
| Correspondencia de direcciones | — | Ninguna (S57-D.5) |

## Límites

- Sin datasheet IMX210/IMX235: no se asigna significado eléctrico a ningún registro.
- Sin correspondencia de direcciones, no se puede decir qué registro del IMX235 "equivale" a cuál del IMX210.
- Los 112 registros P2S/sensor del IMX210 no tienen clasificación funcional profunda (sin datasheet).

## Artefactos

- `analysis/s206_imx210_imx235_full_table/full_table.json` — tabla completa (119 entradas, con ID, dato, subsistema, clasificación).
- `analysis/s206_imx210_imx235_full_table/full_table.py` (generador).
- `analysis/s206_imx210_imx235_full_table/test_s206_full_table.py` (3 pruebas de bytes).
- `tests/test_s206_imx210_imx235_full_table.py` (existente).
- `docs/capture/s206-imx210-imx235-full-table.md` (este informe).

## Siguiente (S207)

¿La A7S/IMX235 tiene algún registro o mecanismo de fin de integración o segunda cortina electrónica que falte al IMX210? Barrido de bytes en la matriz IMX235 y código A7S buscando registros de fin/exposición no presentes en la tabla IMX210.
