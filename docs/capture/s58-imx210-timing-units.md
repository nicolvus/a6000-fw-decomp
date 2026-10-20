# S58-B — Unidades y límites de temporización IMX210

20-10-2026. Evidencia: S58-01…11 en [matriz](../../analysis/s58-evidence-matrix.json), código original A6000 3.21 y [productores](s58-ae-timing-producers.md).

## Relaciones recuperadas

| Campo | Transformación comprobada | Interpretación y límite |
|---|---|---|
| Tv | `0x4382fa94`: 0x1000→256000000; 0x1100→128000000; 0x1800→1000000 | escala exponencial tabulada, paso candidato 1/256 EV; la fórmula exponencial continua es aproximada |
| T | Tv≤0xc00→0xffffffff; 0xc01→4084937500 | saturación de 32 bits; unidad física sin verificar |
| n_i | `sdiv(T, M[0x20]·svr)` en `0x4383d4d0` | cociente con signo; el resto se calcula con wrap de 32 bits |
| shd_i | `VMAX−líneas`, con suelo y recortes posteriores | posición aritmética compatible con líneas; VMAX es nombre interpretativo |
| fino_i | `hmax−1000·resto_fino/tick`, acotado | va a fila+0xa; **distinto de spl** |
| svd | rama modo=0: `(N−f)·svr/VdNum−1`, después ajustes y recortes | 12 bits efectivos en ID3/4; no es tiempo absoluto |
| spl | remanente `max(0,N·svr/VdNum−1−n_i·svr)`, limitado a svd | 12 bits en ID7/8; cuenta aritmética de pasos, no término sublínea |
| svr_num | byte X8+0x14e→G+0x16 | multiplicador de periodo; no equivale por sí solo a Hz |
| VdNum | u16 X8+0xcc→G+0x38 | productor lo lee con signo; la rama de división usa el valor convertido a u32 |

Las fórmulas resumidas omiten casos especiales: modo≠0, svr=0, VdNum=0, indicador de depuración y casts. La especificación reproducible está en `analysis/s58/timing_model.py`; Unicorn ejecuta las instrucciones originales y comprueba las salidas, no una reimplementación aislada.

## Unidad física: INFERENCIA

`tick=256000000/(clk/1000)`; con clk=0 se usa 3555. Si clk fuese Hz, esto sería compatible con una unidad T de 1/256 µs y un reloj nominal próximo a 72 MHz. En esa interpretación, Tv=0x1000 correspondería a 1 s y 0xffffffff a unos 16,78 s. **No se ha demostrado que clk tenga unidades Hz**: P+0x4c0 se forma con dos u16 de `0x438667e0`.

Las muestras `analysis/s58/out/a6000_timing_scenarios.json` usan M sintético. Sus etiquetas 1/4000…1 s son condicionales a esa interpretación; no son calibración ni tiempos medidos de cámara. La reconstrucción ideal con periodos/líneas/reloj no es exacta tras división entera, clamps u overflow.

## Productor frente al host

El host `0x4381106c` valida `N·svr−1` para VdNum≤1 y `N/VdNum−1` para VdNum>1. No introduce siempre el factor svr que sí usa el productor. El caso sintético N=6, svr=4, VdNum=3 produce svd=7 en `0x4383c9dc`, frente a 1 en la expresión del host. **No demuestra un fallo del firmware**: no conocemos las combinaciones alcanzables ni todas las restricciones de modo.

La anterior afirmación del borrador S58 de equivalencia incondicional queda corregida. `test_row_formula_is_not_unconditionally_host_formula` conserva el contraejemplo con ejecución del productor real.

## Verificación y siguiente frontera

Suite: 120 vectores para tiempo y 80 para filas, con dos rellenos de páginas no mapeadas. Campañas adicionales: `a6_verify.py` 600/600 y `a7_verify.py 150` 300/300. Los patrones no sustituyen un constructor real ni alteran automáticamente la memoria ya mapeada. Se comprueban truncamiento, ramas y estados sintéticos; no se emula el sensor.

Próximo paso: recuperar la fuente de los 12 u16 que `0x437aa65c` copia desde `0x437876dc()+0xdd0` y un estado de M/Tv alcanzable por modo. Para asociar estos números al fin físico de integración hace falta documentación del IMX210 o una traza pasiva autorizada CIS0+XPI+VD.
