# G38 — Objetivo «Obturación máxima 1/8000» (origen ≈Sony α7): DESCARTADO (15-11-2026)

Sin cámara ni CFW nuevo. Evidencia ya medida en cámara y verificada offline; se enlaza, no se repite.

## 1. Veredicto
No es viable en ninguno de los tres estados de obturador del CFW. Es un límite físico/electrónico, no una tabla de menú.

| Estado | Por qué 1/8000 no sirve | Evidencia |
|---|---|---|
| Mecánico | 1/4000 es el límite de la cortinilla de fábrica (velocidad de recorrido); ninguna constante de firmware lo cambia | A6000 de serie 1/4000 |
| EFCS (cortinilla delantera electrónica) | La cortinilla trasera sigue siendo mecánica; ya a ≥ 1/1000 hay degradado vertical (la rendija trasera no cubre el barrido del sensor) | [R85](../capture/e26-r85-calibracion-fotos-3749-3779.md), [R87 §6](../capture/e26-r87-disparo-remoto-y-recalibracion.md) |
| Silent (electrónico) | Exposición efectiva medida **E = 17,135 µs·n + 564 µs** (n = líneas, 7 velocidades, ISO 100/800). Mínimo con n = 1: **≈ 0,58 ms ≈ 1/1700**. 1/8000 = 125 µs: sobreexposición ≈ +2,2 EV (ya +0,5…+1,3 EV a 1/2000–1/4000) | [R87 §3, §6](../capture/e26-r87-disparo-remoto-y-recalibracion.md) |

## 2. Dónde está el límite en el modelo
- La ruta Silent calcula `r5 = 4252 − T/17,135 µs` ([`scripts/g22/patch_silent_r5.py`](../../scripts/g22/patch_silent_r5.py), rango Tv `0x1400…0x1E00`, que ya incluye 1/8000 = `0x1cf7`). Si `r5 < 10` no toca nada.
- Para 1/8000 el modelo pide ≈ 7,3 líneas ([E25-15 §6/§9](../capture/e25-15-shutmode0-temporizacion-nativa.md)); pero por encima de ~1/600 el modelo medido da ≤ 0 líneas efectivas y el sensor integra al menos 1 línea más el desfase fijo de 564 µs. Subir `TV_MAX` no cambia la exposición real: solo cambiaría el EXIF.
- Rolling shutter: con lectura ≈ 61 ms el barrido completo (≈ 15,2–17,1 µs/línea) dejaría banding/deformación para cualquier velocidad; a 1/8000 la rendija sería de ≈ 7 líneas sobre ≈ 4219 (acentúa el skew y el flicker), por lo que aunque se bajara el piso de 564 µs el resultado seguiría siendo un modo de uso muy limitado.
- Aunque el menú/dial permitiera el valor (el productor nativo `0x4383fa40` ya acepta `0x1cf7`, [E25-26 §5](../capture/e25-26-c3b-exposicion-electronica.md)), no hay forma de eliminar el piso de 564 µs sin conocer su origen eléctrico (reset de fila/Darwin; sin datasheet, [E25-17 §Límites](../capture/e25-17-bulb-exposicion-electronica-larga.md)).

## 3. Límites de esta conclusión
- No se localizó (ni hacía falta) la tabla de velocidades del menú/dial ni se comprobó si el dial permite 1/8000 en modo Silent: el piso medido lo hace inútil.
- El piso de 564 µs es empírico (residuo ±10 %); si algún día se descubriera un modo de integración sub-línea (reset anticipado en Darwin), se reabriría: ver G38-A.
