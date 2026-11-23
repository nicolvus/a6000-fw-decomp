# G92 — Auditoría de la cadena de color del BIONZ X para una LUT «general» (vídeo, vista en vivo y foto) (23-11-2026)

Petición: cambiar la tabla de color del procesador para aplicar la LUT de forma general, no solo en el JPEG (G91). Solo estático + Unicorn sobre `av-cam.bin` (Capstone, sesión REA compartida para descompilar); sin cámara ni CFW. Código: `scripts/lut/tono_post.py`; tests `tests/test_g92_tono_post.py` (4). Contexto: [g71](g71-lut3d-formato-y-cube.md), [g90](g90-lut-interpolacion-optimizacion-geometria.md), [g91](g91-lut-completa-por-software.md).

## 1. Conclusión
- **La LUT 3D del hardware no se puede ampliar** (G90 §C, se mantiene): 5×9×9 en YCbCr, bancos SRAM llenos.
- **Sí hay una segunda etapa programable que aplica a todo** y no estaba aprovechada: una **curva 1D propia después de la gamma**, en una ranura libre de la cadena de tono del firmware (§3). Curva 1D + LUT 5×9×9 es la descomposición «shaper + LUT 3D» habitual y **reduce el error 2–4× en LUT con curva** (§4). Verificado con Unicorn sobre el código real; falta integrarlo (cueva) y verlo en cámara.
- **No hay curvas por canal**: el firmware compone **una sola** curva de 512 puntos para R, G y B (§2). Lo que difiera por canal sigue yendo al residuo de la LUT 3D.

## 2. Mapa de etapas de color programables (A6000 fw 3.21)
| Etapa | Dónde | Tamaño | Alcance | Estado |
|---|---|---|---|---|
| Matriz 3×3 | color mode (G27) | 9 s16 Q10 | todo | VERIFICADO (G27); ajustarla por LUT empeora (G90 §B) |
| Gamma (por número) | `0x44001404[bd9·2+bd6]` | 2048 u16 → 10 bits | todo | VERIFICADO (G25/G67) |
| **Cadena de tono tras la gamma** | `FUN_438538e4` → `obj+0x26e` | 512 × 11 bits | todo (es la curva que se envía) | **VERIFICADO (Unicorn)**, §3 |
| Segunda curva de 512 puntos | `FUN_43854a28`: `memcpy(buf+0xef6, 0x43bfaa86, 0x400)` (y `+0xab0` por modo) | 512 × 11 bits | ? | constante **identidad** (v = 4·i); consumidor y etapa NO localizados |
| Rejilla de 96 nodos + 9 parámetros | HW `+0x15300` (0x180 B) / `+0x15494` (`FUN_43853660`, `FUN_4385353c`) | 96 u32 + 9 | ? | dos tablas fijas de la imagen; `FUN_43854614` busca un valor en los 96 nodos con segmentos de 2ⁿ: rejilla no uniforme de la curva 1D (inferido), no es de color |
| LUT 3D | HW `+0x17000…0x17880` (8 bancos) + 18 registros `+0x15c100…0x144` | 5×9×9 × 7 bits | todo | VERIFICADO (G71/G90); fija |
| Sat / Fase / Color Depth ×6 | paquete de colorimetría (G69) | s8 | todo | se suman a la misma LUT 3D |
| 3 tablas gemelas de 61 s32 | HW `+0x3600/+0x3700/+0x3800` (`0x43851fb0`) | 3 × 0xF4 B | ? | otro bloque (`+0x3000…0x3FFF`, junto a `+0x3950` 0x200 B); forma radial por canal: probable corrección de óptica (sombreado/aberración), **no de color**; no estudiado |

Mapa obtenido barriendo los accesores de registro del controlador (`add r0,#off; str/ldr` y copias a SRAM por `0x43b7f878`) en `0x43b60000…0x43b80000`: el IP de la LUT 3D ocupa `+0x11000…+0x17FFF`; sus únicas SRAM escritas son `+0x15300` (0x180 B), `+0x15b08` (0x70 B) y la LUT 3D. **Límite**: la curva de 512 puntos va a búferes de parámetros (`[+0x4a70]`, `+0xaf6`) cuyo consumidor no se localizó; no se ha visto en qué registro acaba ni si el HW tiene tres RAM de gamma.

## 3. La ranura libre (VERIFICADO en Unicorn)
`FUN_438538e4(obj)` (llamado desde `0x43854da0` y `0x43854e54`, dentro de `FUN_43854a28`, único llamador `0x4386971a`) llena `obj+0x26e` con 512 valores `cola(gamma[x])`, `x = obj+0x66e`:
- sin indicadores: `gamma[x]`;
- `bd1` (Black Gamma): `c5c[bdb][gamma]` (`0x440014fc`, 7 niveles);
- `bd3`: `c5c[bdb][c60[bdd][…]]` (`0x440013b0`, 8 tablas, centro = identidad);
- **`bd5`: `c68[be1][min(gamma, 1023)]`** (`0x440013cc`, 14 tablas de 1024 u16). Entradas 0, 6 y 8…13 = la identidad `0x43bfaf2a`; 1–5 y 7 son curvas de efecto (p. ej. 4 levanta negros, 3 binariza).
- Prioridad: `bd1`/`bd3` excluyen a `bd5`. `FUN_43854a28` anula `be1 > 13`.

Unicorn sobre el código real (`tono_post.emula`): sin indicadores = `gamma[x]`; ranura 8 de fábrica = `gamma[x]`; con una tabla propia en `c68[8]` y `bd5 = 1`, `be1 = 8` la salida = `T[gamma[x]]` exacta; con Black Gamma la tabla se ignora (test).

**Integración propuesta (LUT-T-1, sin hacer):** dos ganchos de 4 B en las llamadas `0x43854da0` y `0x43854e54` (`bl 0x438538e4` → `bl cueva`); la cueva lee el ajuste «LUT» (como `lut_patch`), y si está activo escribe `obj+0xbd5 = 1`, `obj+0xbe1 = 8`, `obj+0xbd1 = obj+0xbd3 = 0` y el puntero `0x440013ec` = curva de la LUT elegida, y salta a `0x438538e4`; con Off no toca nada. La curva (1024 u16) puede guardarse como 65 nodos y expandirse en la cueva. Al estar tras la gamma del usuario, sirve para LUT diseñadas para cualquier entrada (Rec.709, S-Log2/3).

## 4. Ganancia medida (métrica ΔE2000 ya corregida, G91 §5)
`cube_a6000.descompone(usa_M=False)` con y sin T; medio / p95 / máx; uniformes (20 000) | foto `DSC03986`:

| LUT | solo LUT 5×9×9 | T + LUT 5×9×9 |
|---|---|---|
| película | 0,79/1,81/6,0 · 1,23/2,39/6,1 | **0,19/0,50/1,3 · 0,34/0,47/0,7** |
| agresiva | 2,81/6,91/16,3 · 1,10/3,09/7,5 | **1,23/3,26/8,4 · 1,05/1,28/2,7** |
| teal & orange | **0,06/0,15/0,4 · 0,16/0,36/0,6** | 0,19/0,59/6,0 · 1,52/3,36/5,0 |
| suave | **0,09/0,24/1,0 · 0,44/0,72/1,1** | 0,16/0,52/3,5 · 1,14/2,17/3,4 |

La T actual (medias por intervalo de todos los canales) empeora las LUT sin curva tonal: hay que elegir por LUT (`elige` ya existe) o ajustar T y LUT conjuntamente en ΔE (pendiente LUT-T-1). Con LUT con curva, la cadena general se acerca a lo que el software logra en foto (G91).

## 5. Qué falta
- **LUT-T-1** (offline): cueva + almacenamiento de la curva (`.dat` y blob de la SD), elección T sí/no por LUT, ajuste conjunto en ΔE; test Unicorn de los ganchos sobre `FUN_43854a28`.
- **LUT-T-2** (cámara): que la curva compuesta llegue al procesador en vídeo, vista en vivo y foto, y que el look coincida con el modelo.
- **LUT-2C-1**: localizar el consumidor de la segunda curva de 512 puntos (identidad) y el destino real de `+0xaf6`: si fuese otra etapa (p. ej. tras la LUT 3D), daría una curva 1D posterior; si el HW tuviera RAM de gamma por canal, una curva por canal.
