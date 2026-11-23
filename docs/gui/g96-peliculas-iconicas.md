# G96 — Seis películas analógicas icónicas para la LUT de la A6000 (23-11-2026)

Petición del usuario: crear seis LUT de las películas más icónicas, ajustadas a la A6000, y dejarlas en la SD. Código: `scripts/lut/peliculas.py` (modelo, ajuste y panel). Test: `tests/test_g96_peliculas.py`. Las salidas de referencia en 33³ están en `luts/peliculas/` (sin versionar). La vista previa es `img/g96-peliculas-panel.png`.

## 1. Elección y rasgos (investigación)
Las fuentes son reseñas y foros, no densitometría ([Shutterbug](https://www.shutterbug.com/node/456370), [Adorama](https://www.adorama.com/alc/7-great-films-analog-shooters), [Emulsive E100 vs Velvia 50](https://emulsive.org/articles/my-2020-lockdown-journey-a-comparative-test-of-kodak-ektachrome-e100-and-fujifilm-velvia-50-bonus-portra-lomography-included), [Ken Rockwell E100G](https://www.kenrockwell.com/kodak/e100g.htm), [Photrio Kodachrome 64](https://www.photrio.com/forum/threads/kodachrome-64-where-does-it-shine-not-shine.42651), [Fstoppers Portra vs 400H](https://fstoppers.com/film/archenemies-kodak-portra-400-versus-fuji-pro-400h-507223)).

| Ranura | Película | Rasgos modelados |
|---|---|---|
| LUT1 | Kodachrome 64 | Rojos densos y cálidos, azules profundos, verdes y cian contenidos, contraste alto, sombras densas |
| LUT2 | Ektachrome E100 | Diapositiva limpia, neutra o algo fría, saturación moderada, azules limpios |
| LUT3 | Velvia 50 | Saturación muy alta, azules y púrpuras ricos, verdes más cálidos, contraste alto |
| LUT4 | Portra 400 | Contraste bajo, sombras levantadas, piel cálida sin llegar al naranja, verdes oliva, luces cremosas |
| LUT5 | Kodak Gold 200 | Cálida y amarilla, amarillos y naranjas fuertes, azules algo apagados |
| LUT6 | Fuji Pro 400H | Fría, verdes hacia el cian, piel neutra, sombras pastel |

Tri-X 400 se descartó porque el blanco y negro no cabe en la LUT del hardware (ΔC ±18 %). Con desaturación total, el ajuste da 10,6 ΔE de media y 565 nodos al tope.

## 2. Modelo y ajuste
El modelo trabaja sobre la señal de pantalla (sRGB supuesto, como en `cube_a6000`):
- saturación global y por tono en YCbCr (ventanas gaussianas de 28° en el ángulo Cb/Cr);
- curva S por canal mezclada con la identidad (cruce de color);
- virado de sombras y luces, negro levantado, blanco por canal y desaturación de altas luces.

La tabla 5×9×9 se ajusta en ΔE2000 (`descompone`, sin M ni T) y se guarda como paquete `.LUT` v1 (G95). Error frente al modelo (20 000 colores al azar):

| LUT | ΔE medio | p95 | máx | nodos al tope |
|---|---|---|---|---|
| Kodachrome 64 | 0,65 | 1,83 | 4,9 | 0 |
| Ektachrome E100 | 0,37 | 0,87 | 3,0 | 0 |
| Velvia 50 | 0,67 | 1,77 | 6,1 | 27 |
| Portra 400 | 0,23 | 0,59 | 1,5 | 0 |
| Gold 200 | 0,31 | 0,83 | 2,7 | 0 |
| Pro 400H | 0,28 | 0,93 | 2,2 | 0 |

## 3. Estado y límites
- Los seis `LUT1…6.LUT` están en `LUT/` de la SD. Se verificaron byte a byte, y se borraron el `.LUT` de la GH7 y los `.CUB` anteriores.
- La foto JPEG y la vista en vivo deberían usar la misma tabla (G94 §3 bis). Falta verlo en la cámara (LUT-SD-2).
- Los parámetros son una interpretación de descripciones, no una medida de cada película. La entrada sRGB tampoco está medida en la A6000. Si el Estilo creativo no es «Estándar» cambian la base y el resultado.
