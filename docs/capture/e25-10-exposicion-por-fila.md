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

## 3. Relación con `r5` de E23 (INFERENCIA)

- T039 (ShutMode 0 forzado): la luminancia a 1/250 cae de forma casi lineal al subir `r5` entre 4000 y 4200 (27,2 → 16,3 → 4,8) y **extrapola a cero en
  `r5` ≈ 4244**; a partir de 4300 `r5` no actúa. 4244 coincide con el orden de las **líneas totales del cuadro** (≈ 4024 visibles + blanking).
- Hipótesis consistente con T044: `r5` fija en **líneas** cuánto antes de la lectura se reinicia cada fila (reinicio por filas, como el obturador electrónico
  de cortina delantera); exposición ≈ (límite − `r5`) líneas × 15,2 µs, con `r5` ≈ 4200 ⇒ exposición corta y casi uniforme (lo que se vio en T039).
  En ese modo el degradado vertical desaparece porque el reinicio también es por filas. **No está demostrado:** falta la unidad de `r5` (¿líneas?) y
  una medida RAW a `r5` conocido.

## 4. Qué cambia para el proyecto

- Con 3.23 **no hay obturador electrónico de cortina trasera/uniforme**: hay exposición con reinicio global y lectura por filas. Utilizable para velocidades
  lentas (≤ 1/60) donde τ pesa poco, y con sujetos sin movimiento; a velocidades rápidas hay sesgo de exposición de hasta 3,7× arriba-abajo y distorsión por lectura (≈ 61 ms).
- Para velocidades rápidas uniformes haría falta **reinicio por filas** (programar el reinicio del IMX210, lo que hacía `r5` en E23). Eso exige parches en RAM
  (como T035–T039, con el incidente de T037) o una versión nueva de Darwin/BIONZ: **no autorizado**.

## 5. Límites

Una sola escena y un solo encuadre; ISO 100 y modo M; velocidades 1/4000–1/8; RAW sin corregir por viñeteo/lente (se asume que `s_b` lo absorbe, constante entre disparos).
No se midió con movimiento (la distorsión por lectura se infiere del tiempo de lectura, no de imágenes con sujetos rápidos). La unidad de `r5` sigue sin verificar.
