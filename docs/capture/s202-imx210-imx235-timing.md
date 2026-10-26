# S202 — Tiempos de lectura y exposición: IMX210 (A6000 fw3.21) vs IMX235 (A7S fw3.20)

22-10-2026. Agente A (sensor y driver), sesión S202 (rango S200–S299). **Solo investigación estática.**

## Veredicto resumen

| Aspecto | IMX210 (A6000) | IMX235 (A7S) | Clasificación | Veredicto |
|---|---|---|---|---|
| Registros de tiempo | svd/shd/spl en ID3–ID8 (sombra) | Columnas estáticas por modo de lectura | **DISTINTO** | VERIFICADO (rec_map ID3–8; matriz `0x43fee598`) |
| Fórmula svd | `svd = n·svr_num − 1` (o `n/VdNum − 1`) | No recuperada | **DISTINTO** | INFERENCIA (`0x4381106c` valida svd; S57-C) |
| Contador / base temporal | Contador de pasos del host `cap+0x4b9c` vs svd; periodos VD (INFERENCIA) | No identificada | **DISTINTO** | INFERENCIA (S57-C §3) |
| Espejo condicional | 0x144–0x149 si `[G+0x7f]≠0xFF` | No equivalente recuperado | **DISTINTO** | VERIFICADO (S57-C §1) |
| Tiempo de lectura (24 MP) | ≈ 4176 líneas ≈ 66,8 ms/cuadro (cálculo sobre matriz) | No recuperado en frames/ms | **DISTINTO** | Cálculo S57-F (no es dato de sensor) |
| Unidades de svd/shd/spl | No documentadas (líneas/ciclos) | No asignadas | — | NO_VERIFICADO en ambos |
| Fin de integración | Sin reescritura de registros al terminar | Sin comando extra de "fin de integración" | **IDÉNTICO** | NO_VERIFICADO (ningún modelo lo demuestra) |

## Detalle por bloque

### 1. Registros de tiempo (IMX210 ID3–ID8 vs columnas IMX235)

El IMX210 expone tres parámetros de temporización como registros sombra de 16 bits, escritos por `SetExposure` (`0x436d6f6c`):

| Registro | ID | Campo | Bits | Escritor |
|---|---:|---|---|---|
| ID3 | 3 | svd bajo | svd[7:0] | `SetExposure` |
| ID4 | 4 | svd alto | svd[11:8] (ID4[7:4] preservado) | `SetExposure` |
| ID5 | 5 | shd bajo | shd[7:0] | `SetExposure` |
| ID6 | 6 | shd alto | shd[13:8] (ID6[7:6] preservado) | `SetExposure` |
| ID7 | 7 | spl bajo | spl[7:0] | `SetExposure` |
| ID8 | 8 | spl alto | spl[11:8] (ID8[7:4] preservado) | `SetExposure` |

Además existe un espejo condicional en 0x144–0x149 (mismos bytes), activo solo si `[G(0x4f24)+0x7f]≠0xFF`. Los bits superiores de entrada se descartan (svd,spl [15:12]; shd [15:14]).

El IMX235 (A7S) no tiene un equivalente registro-por-registro: sus valores de tiempo son **columnas estáticas de la matriz de modos** (`0x43fee598`, 34 columnas), una por modo de lectura. No se recuperó ninguna fórmula ni nombre equivalente a svd/shd/spl. Clasificación: **DISTINTO** (VERIFICADO por bytes).

### 2. Fórmula svd y contador de pasos del host

`0x4381106c` valida svd: `n = [obj+0x1f8]` (o 1 si `[obj+0x1fc]==9`); `svd_esperado = (VdNum≤1) ? n·svr_num : n/VdNum`, menos 1; `svr_num = u8[X8+0x14e]`, `VdNum = u16[X8+0xcc]`, `n = [X8+0x3c]`. `svr_num`/`VdNum` salen del bloque de modo `X8`. Clasificación: **INFERENCIA media-alta** — svd se comporta como contador de periodos VD (o de lectura vertical), pero su unidad física (líneas/ciclos) no está demostrada y el productor AE no se recuperó.

Para el IMX235 no existe equivalente recuperado. Clasificación: **DISTINTO** (INFERENCIA).

### 3. Tiempo de lectura

IMX210: modo foto `0x0b` = 24 MP, 4176 líneas, ≈ 66,8 ms/cuadro (S57-F, cálculo a partir de bytes de la matriz de modos; no es un dato de sensor leído de un datasheet). Si el sensor cerrara la integración fila a fila en su lectura, la distorsión tipo obturador de persiana sería de ese orden (INFERENCIA, no comprobada).

IMX235: no se recuperó un tiempo de lectura en frames o ms. Clasificación: **DISTINTO** (cálculo solo para IMX210).

### 4. Fin de integración

Ninguno de los dos firmwares reescribe registros del sensor al terminar la exposición:
- IMX210: `ExposureTimerEnd!` (`0x438c893a`) no reescribe registros ni emite SSB/Execute.
- IMX235: no hay comando extra de "terminar integración" en la matriz ni en el pulso (S57-D D.6).

Clasificación: **IDÉNTICO** (ambién ausente), pero **NO_VERIFICADO** si el sensor cierra la integración internamente por temporización programada al inicio (hipótesis H57-9). Distinguirlo requeriría datasheet o traza pasiva CIS0+XPI+VD.

## Límites

- Sin datasheet IMX210/IMX235: no se asignan unidades (µs/líneas/ciclos) a svd/shd/spl ni significado óptico a ningún registro.
- Sin cámara: no se observa el fin real de integración ni la señal XPI/CIS0_SCK/SI.
- El productor AE (origen de svd/shd/spl en runtime) no se localizó; `X8` (bloque de modo) no se rastreó hasta su origen.
- Una consulta vacía de REA no prueba ausencia: la falta de fórmula equivalente en IMX235 se basa en el examen de la matriz, no en la ausencia de xrefs.

## Artefactos

- `analysis/s202_imx210_imx235_timing/timing.py` + `tests/test_s202_imx210_imx235_timing.py` (ver abajo).
- Alimenta S204 (clasificación final).

## Siguiente (S204)

Clasificación final resumida + veredicto sobre qué falta en la A6000; regeneración del backlog y cierre del ciclo.
