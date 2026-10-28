# E25-10 — Tiempo efectivo de exposición por fila con 3.23 (27-10-2026)

Análisis **offline** de los 19 ARW de T044 (`analysis/camera-dumps/20261027-224101-T044-raw-iso100/`; ARW no versionados, resultados en `e25_10_tau_por_fila.json` y en
`scripts/e25_10_exposicion_por_fila.py`). No se tocó la cámara. Etiquetas: VERIFICADO = medido; INFERENCIA = interpretación.

## 1. Qué se midió

ISO fijo 100, RAW 6024×4024, 10 velocidades × 2. Por banda de filas (32 bandas de ≈126 filas) se ajustó
`lineal_b(T) = s_b · (T + τ_b)`: `T` es la velocidad fijada, `s_b` el brillo de escena (incógnita por banda, así se elimina la escena) y
`τ_b` el tiempo de exposición que **no controla la velocidad**.

| Resultado (VERIFICADO sobre estos datos) | Valor |
|---|---|
| Ajuste aditivo `T + τ` por banda | R² ≥ 0,988 en las 32 bandas; error máx. 17 % (bandas superiores, señal baja), 7 % en el resto |
| τ en la banda superior | **7,3 ms** (8,1 ms medido) |
| τ en la banda inferior | **66,6 ms** |
| Rampa de τ con la fila | **lineal, ≈ 15,2 µs por fila** (1,91 ms por banda; ≈ 59 ms de arriba abajo) |
| Modelo alternativo «tiempo efectivo = máx(T, suelo)» | residuo 6,9 veces mayor: **descartado** |

Es decir, la exposición de la fila `i` es **`T + 7 ms + 15,2 µs · i`**: la velocidad suma, pero cada fila recibe además un tiempo que
crece con su posición. Por eso la exposición apenas depende de `T` mientras `T` ≪ τ (1/4000–1/500) y por eso la fila inferior recibe 3–4 veces
la de la superior a velocidades rápidas (T044: 0,095 → 0,350 relativo a 1/8).

## 2. Interpretación (INFERENCIA)

- **Sin obturador mecánico y con lectura por filas, la luz sigue llegando mientras se lee el sensor.** La exposición de cada fila termina cuando
  se lee esa fila; la fila `i` se lee `i · 15,2 µs` después de la primera. La velocidad fijada solo adelanta el **comienzo común** de la exposición
  (reinicio global): exposición_i = T + (retardo fijo ≈ 7 ms) + (tiempo de lectura hasta la fila i).
- **El tiempo de lectura completo es ≈ 61 ms** (15,2 µs × 4024 filas; ≈ 64 ms con 4243 líneas totales). T025 estimó «~30 ms» sin medir por filas.
- Con un obturador mecánico, la cortina trasera corta esa luz; con B1a no hay cortina, así que el sesgo vertical queda a la vista. **No es un fallo de B1a**
  (B1a solo evita accionar el mecanismo): T025 (3.22, antes de B1a, JPEG) ya mostraba el mismo suelo plano 1/4000–1/250 y la subida desde 1/125.
  Comparación débil: T025 es JPEG y otra escena.

## 3. Relación con `r5` de E23 — VERIFICADO en T046

T046 (27-10-2026, autorizado por el usuario: «continua con los parches en ram»; solo RAM, parches de T035 revertidos y verificados; ISO 100, RAW; `analysis/camera-dumps/20261027-231049-T046-r5-raw/`):
tres referencias sin parche (1/8, 1/15, 1/60) fijan la escena y τ por banda; después ShutMode 0 forzado (`0x836d6fb6`) con `r5` forzado (`0x836d7000`).
Exposición efectiva = 1000·RAW/escena (ms), media y por octavos:

| `r5` (1/250, ShutMode 0) | Exposición media | Por octavos (arriba → abajo) |
|---|---|---|
| sin forzar | 64,9 ms | 65,0 64,9 64,7 64,8 64,8 64,9 64,9 65,0 |
| 0 | ≈ 0 (imagen negra) | — |
| 1000 | 49,1 ms | 49,2 … 49,2 |
| 2000 | 33,8 ms | 33,9 … 33,8 |
| 3000 | 18,5 ms | 18,7 … 18,5 |
| 3500 | 10,9 ms | 11,1 … 11,0 |
| 4000 | 3,3 ms | 3,4 … 3,4 |
| 4100 | 1,8 ms | 1,9 … 1,8 |
| 4200 | 0,3 ms | 0,3 … 0,3 |
| 4300 | 64,9 ms | sin efecto (= sin forzar) |

A 1/30: sin forzar 65,4 ms; `r5` 1240 → 45,4 ms; 2500 → 26,2 ms; 4000 → 3,4 ms (los mismos valores que a 1/250: **con ShutMode 0 la velocidad fijada no interviene**).

Conclusiones (VERIFICADO sobre estas medidas):

1. **Con ShutMode 0 la exposición es uniforme en todas las filas** (octavos iguales dentro de ±0,2 ms): reinicio por filas, no el reinicio global + lectura de ShutMode 3.
2. **`r5` fija la exposición en líneas: E = (4219 − `r5`) × 15,2 µs**, con `r5` entre 1 y ≈4219. La pendiente medida (−15,2 µs por unidad) **coincide con los 15,2 µs por fila** de T044 medidos de forma independiente: `r5` es una distancia en líneas entre el reinicio y la lectura.
3. Sin forzar (o con `r5` ≥ 4300) la exposición es el cuadro completo, **64,9 ms ≈ 4270 líneas**; con `r5` = 0 es nula.
4. Predicción para velocidades uniformes (**comprobada en T047**, ver abajo): `r5` = 4219 − T/15,2 µs → 1/4000 ≈ 4203, 1/1000 ≈ 4153, 1/250 ≈ 3956, 1/60 ≈ 3122.

Así, la limitación de T044 (sesgo vertical) es del modo ShutMode 3 (el de la foto normal, T031); el reinicio por filas ya existe en ShutMode 0 y solo falta que la foto lo use con `r5` calculado a partir de la velocidad.

## 4. Qué cambia para el proyecto

- Con 3.23 **no hay obturador electrónico de cortina trasera/uniforme**: hay exposición con reinicio global y lectura por filas. Utilizable para velocidades
  lentas (≤ 1/60) donde τ pesa poco, y con sujetos sin movimiento; a velocidades rápidas hay sesgo de exposición de hasta 3,7× arriba-abajo y distorsión por lectura (≈ 61 ms).
- Para velocidades rápidas uniformes hace falta **reinicio por filas** (ShutMode 0 con `r5` calculado, §3). Ese parche está en **BIONZ/av-cam** (`0x836d6fb6`, `0x836d7000`), no en Darwin: un FDAT de Darwin no lo instala. Hoy solo es posible en RAM (T046); hacerlo permanente exigiría modificar el firmware de BIONZ (fuera de alcance y sin recuperación probada).

## 5. Límites

Una sola escena y un solo encuadre; ISO 100 y modo M; velocidades 1/4000–1/8; RAW sin corregir por viñeteo/lente (se asume que `s_b` lo absorbe, constante entre disparos).
No se midió con movimiento (la distorsión por lectura se infiere del tiempo de lectura, no de imágenes con sujetos rápidos). T046: una escena y un encuadre; `r5` = 0 no estudiado más allá de «exposición nula».

### T047 — comprobación de la predicción (27-10-2026)

`r5` = 4203, 4153, 3956, 3122 a 1/250 con ShutMode 0 (RAM, `analysis/camera-dumps/20261027-233006-T047-r5-pred/`):

| Velocidad objetivo | `r5` | Objetivo (ms) | Medido con escena de T046 | Medido con refs de T047 |
|---|---|---|---|---|
| 1/4000 | 4203 | 0,25 | 0,24 (−1 %) | 0,19 (−23 %) / 0,27 (+13 %*) |
| 1/1000 | 4153 | 1,00 | 0,99 (−1 %) | 0,79 (−21 %) / 1,12 (+12 %*) |
| 1/250 | 3956 | 4,00 | 4,03 (+1 %) | 3,20 (−20 %) / 4,55 (+14 %*) |
| 1/60 | 3122 | 16,7 | 16,75 (0 %) | 13,3 (−20 %) / 18,9 (+13 %*) |

\* sin la referencia a 1/8 de T047, que salió ≈ 20 % más alta que en T046 con 1/15 idéntico (lectura anómala, probablemente cambio de luz en esa toma).

La **linealidad es sólida** (proporciones entre puntos dentro de 3 %, uniforme por filas); la **escala absoluta tiene ±20 % de incertidumbre** por la calibración de la escena por tanda. Con la escena de T046 la ley `E = (4219 − r5)·15,2 µs` se reproduce a ±1 %. Conclusión: valores de `r5` calculados desde la velocidad dan exposiciones uniformes de 0,25 ms a 16,7 ms, **verificado en RAM**; una calibración absoluta fina requiere una referencia más fiable (p. ej. varias tomas por tanda o luz controlada).
