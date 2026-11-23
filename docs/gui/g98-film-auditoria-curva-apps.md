# G98 — CFW 3.88 «Film»: por qué parte de los looks no cambiaban en el 3.87, la curva por la gamma extendida de Sony y lo que aportan JPEGCAM y RecipeLab (23-11-2026)

Petición: el 3.87 ([G97](g97-cfw-film-sosang.md)) arrancó en la cámara, pero «algunos looks cargaban bien y otros quedaban idénticos». Auditarlo, corregir
los errores y usar todas las etapas (LUT 5×9×9 + curva 1D + lo que falte del PP). Además, decompilar JPEGCAM 2.08 y RecipeLab 1.13.1 y ver qué se puede aprovechar.
Código: `scripts/lut/film_patch.py` (cuevas de `av-cam`), `scripts/lut/userland/films.c` + `film_userland.py`; tests `tests/test_g97_films.py` (8, Unicorn sobre el código real).

## 1. Diagnóstico (estático + Unicorn; sin traza en cámara)
- **Que algunos looks cambien prueba el camino entero de la LUT** en la cámara real: el menú guarda la fila, el hilo userland escribe el blob en el Backup `0x150005` y el ACK, y `av-cam` entrega la tabla al ISP. Es la primera tabla 5×9×9 no trivial vista en la cámara.
- **Causa principal: la curva 1D no llegaba al hardware.** `FUN_43854a28` construye dos curvas a partir de los mismos indicadores (`bd1`/`bd3`/`bd5`/`be1`):
  - la **rejilla de 96 nodos + 9 parámetros** (`FUN_43853200`), que va a la SRAM `+0x15300` del bloque de la LUT (G92 §2);
  - la curva de 512 puntos (`FUN_438538e4`, `obj+0x26e`).

  La cueva del 3.87 solo reescribía la de 512 puntos, después de construirla; la rejilla se calculaba antes y sin la curva. Sin curva, los looks que dependen de ella se quedan casi en el original:

  | Looks | Cambio en DSC03769 (ΔE mediana): solo LUT | LUT + curva |
  |---|---|---|
  | De cine con curva: Vision3 200T/500T, Verita 200D, Eterna 400/500/Vivid 160/Vivid 500, Reala 500D | **2,4–3,5** | **8,4–10,2** |
  | Solo LUT: Vision3 50D/250D, Eterna 250D, F-64D, las 9 Fuji Sim | 2,5–10,2 (completo) | igual |

  Coincide con lo observado: los looks de solo LUT cambiaban y los de cine con curva parecían idénticos.
- **Fallo secundario en la LUT en caliente:** la máquina `0x437a2502` daba el cambio de ACK por atendido aunque todavía no estuviera el blob del look (llega 16 KB después del ACK de 1 B). En ese caso, o sin contexto (`this`, config u objeto nulos), se quedaba con la LUT de fábrica hasta el siguiente cambio.
- **Userland:** escribía el ACK sin comprobar que el blob se hubiera grabado.
- Sin errores en el resto: ids de las filas, numeración 1…38, tablas empaquetadas (iguales a `empaqueta_hw`) y comprobación de magia y número de look.

## 2. Arreglos del 3.88
1. **Curva por el mecanismo de la gamma extendida de Sony.** Es el que usa `CameraEx.setExtendedGammaTable` de las apps, visto en JPEGCAM §3.
   - En libObj, `SequenceSetExGammaTableControl` envía `PARAMID_EX_GAMMA_TABLE_SW/POINTER`.
   - En `av-cam`, se aplica con la ranura `c68[8]` (`0x440013ec`) y `bd5 = 1`, `be1 = 8`.
   - El 3.88 hace lo mismo, sin mensaje, en las **cuatro** llamadas a `FUN_43852f7c` que preceden a cada construcción de la curva (`0x438548b0`, `0x43854c46`, `0x43854ff6`, `0x43b098cc`; `r0` = objeto de tono, con los indicadores ya copiados de la config). Con look activo y curva en el blob: copia la curva a un búfer propio, `c68[8]` = búfer, `bd5 = 1`, `be1 = 8`, `bd1 = bd3 = 0` (el firmware da prioridad a `bd1`/`bd3` sobre `bd5`).
   - Con Off o con un look sin curva: indicadores de fábrica, y `c68[8]` vuelve a la identidad `0x43bfaf2a` si era nuestro búfer.
   - Se retiran los ganchos de 512 puntos del 3.87.
2. **LUT robusta.**
   - La cueva de la LUT anota el look que entregó de verdad (celda +9).
   - La máquina fuerza el `Copy3DLUT` al cambiar el ACK y, mientras el look aplicado no sea el del ACK, lo reintenta cada 32 pasadas.
   - Sin contexto no consume el cambio.
3. **Userland.**
   - Relee el blob tras escribirlo y solo entonces escribe el ACK; si no, reintenta en el sondeo siguiente.
   - Cada ~3 s comprueba que el Backup siga con el blob y el ACK del look activo.

**Evidencia (Unicorn, código real de `av-cam` 3.21; `tests/test_g97_films.py`, 8 tests):**
- Off = fábrica bit a bit en las dos curvas, con Black Gamma incluida.
- Con look: rejilla del hardware = `T[min(gamma', 1023)]` en los 96 nodos.
- La curva de 512 puntos es idéntica a la del propio firmware con `c68[8] = T`. Solo difiere de la `T[cola(gamma)]` del 3.87 por encima de ~0,93 (orden con la cola).
- Blob sin curva o de otro look: fábrica.
- LUT con el blob tardío: fuerza en la pasada del cambio, reintenta y, cuando llega el blob, aplica el look y se queda quieta. Con Off, una sola pasada.
- Userland: con dos escrituras perdidas no hay ACK hasta que el blob está entero.
- Diff de la imagen: solo los 7 ganchos y la zona A.
- Suites G86/G89/G92/G97: 56 tests en verde.

**CFW 3.88:**
- Fichero: `build/cfw_film388/pkg-3.88/package-3.88/firmware_packed.dat`, sha256 `a3610a6035578d090f59d6cf92b29d928598bd4bc3794f77ed65505923b6c039`.
- `audit_package_nflasha15 --darwin-v3 --sin-wbi --bionz-g22`: `todo_ok`.
- Mismo menú y mismos looks que el 3.87 (sin instalar).

**Cuándo se ve cada cosa (inferido, falta en cámara):**
- La LUT cambia en vivo (máquina).
- La curva se recalcula en cada captura: `FUN_43558910` se llama desde la captura (`0x438c42c8`) → `FUN_43b000ca` → `FUN_43854a28`, así que **la foto lleva el look completo**.
- En la vista en vivo, la curva cambia en la siguiente reconstrucción del tono (cambio de modo o de ajuste de imagen); no se ha forzado.

## 3. JPEGCAM 2.08 (`com.jpegcam.sony`, base pmcademo/OpenMemories; decompilado con androguard)
- **Hardware:** cada receta fija ajustes nativos de `Camera.Parameters`:
  - `creative-style`, contraste, saturación, `color-depth-{red,green,blue,cyan,magenta,yellow}`;
  - `rgb-matrix` (matriz RGB en %, «advMatrix»), `pro-color-mode`;
  - `white-balance-shift-lb/cc`, `dro-mode/level`, `sharpness-gain`, `lens-correction-shading-color-*`, efectos `pe-*`.
- **Curva tonal nativa:** `GammaCurveManager` da 1024 entradas con 5 controles (negros, sombras, medios, luces y blancos, ±5 × 12 códigos en x = 64/256/512/768/960). `NativeToneManager` la instala con `createGammaTable`/`setExtendedGammaTable`. Admite ILCE‑6000 en su lista de modelos.
- **Software, solo sobre el JPEG o el fotograma de la vista en vivo** (`LutEngine`, `LiveLook` + `libnative-lib.so`):
  - `.cube` con opacidad;
  - shadow toe, roll-off, halation, bloom, viñeta, «subtractive sat»;
  - grano por textura (`assets/grain/*.png`).
- **Recetas incluidas:** 24 *starters*, estilizadas (Double Feature, Night Bus, Noir…). Sobre todo estilo, contraste y saturación, y una matriz suave (diagonal 0,85–1,15). No son emulaciones de película medidas.

## 4. RecipeLab 1.13.1 (`com.voxivoid.recipelab`)
- **77 recetas en 12 grupos** (Sony, Fuji Sim, Fuji Film, Kodak, Cine, Ricoh GR, Leica, Hasselblad, Canon/Nikon, Pana/Olympus, Other Stocks, Ilford). Cada una es solo una combinación de ajustes nativos: estilo, saturación, contraste, nitidez, modo de balance de blancos y kelvin, ámbar-azul, verde-magenta, EV, efecto y DRO.
  - Ejemplo: Portra 400 = Retrato, sat −1, con −1, AB +3, GM +1.
  - Ejemplo: Classic Chrome = Estándar, sat −1, con +2, AB +3, GM +1.
- **Las escribe directamente en el Backup** (`NativeBackup.read/write/sync`, `librecipelab.so`) y espera a que vuelva la vista en vivo. Ids:
  - estilo `0x1070175`, contraste `0x1070178`, saturación `0x1070187`, nitidez `0x107018a`;
  - balance de blancos: modo `0x1070019`, temperatura `0x1070018`, AB `0x1070017`, GM `0x1070016` (y sus variantes AWB/K `0x107067e/f`, `0x1070682/3`);
  - DRO `0x1070104`, EV `0x10700b8`, efecto `0x10706f1`.

## 5. Comparación y qué se aprovecha
| | RecipeLab | JPEGCAM | CFW Film (3.88) |
|---|---|---|---|
| Color por tono | No: solo saturación y desplazamiento global | Matriz 3×3 + Color Depth en 6 tonos; `.cube` solo por software | **LUT 3D 5×9×9 en el ISP** (toda la imagen, vivo + foto + vídeo), ajustada en ΔE2000 a spektrafilm |
| Tono | Contraste ±3 | Curva de 5 controles (gamma extendida) | **Curva de 1024 puntos** ajustada por look, por la misma vía de la gamma extendida |
| Balance / EV | Sí (K, AB/GM, EV) | Desplazamiento WB | No (lo hace la LUT dentro de su rango) |
| Textura | No | Grano, halation, bloom y viñeta por software tras la foto | No |

- **Aprovechado:**
  - la vía de la gamma extendida, que es el arreglo de la curva (§2);
  - la confirmación de que esa curva es nativa y aplicable en el ILCE‑6000.
- **Medido y descartado: la matriz RGB por look** («advMatrix»). Con mínimos cuadrados mejora solo los looks desaturados (Bleach Bypass 5,19→3,39 ΔE en colores uniformes; Classic Neg 2,38→1,70) y empeora sobre la foto real Portra 400 (0,73→1,99) y Vision3 500T (0,78→2,41). G90 ya había visto que buscarla en ΔE no mejora. Además, el ILCE‑6000 elige matrices de un catálogo por id (G27), sin una matriz libre que parchear.
- **No aplicado:**
  - Balance de blancos, EV y nitidez por receta: obligaría a reescribir los ajustes del usuario en el Backup (y a recargarlos como RecipeLab). La LUT ya lleva el color de cada película, y apilar una receta de RecipeLab encima duplicaría el look.
  - Grano, halation y bloom: solo existen por software sobre el JPEG (vía LUT-SW).
  - Ambos quedan como pendientes (FILM-3, FILM-4).
- **Nuevo hallazgo útil:** el blanco y negro (Acros, Ilford, Tri-X), que no cabe en la LUT (ΔC ±18 %, G96), sí sería posible como estilo B/N de Sony + nuestra curva 1D por la gamma extendida (FILM-5).

## 6. Uso recomendado
- Estilo Creativo **Estándar** con contraste, saturación y nitidez a 0, y **DRO Off**: el ajuste de la LUT parte del JPEG Estándar.
- El look se elige en Ajustes personalizados → Film. Manda la última fila cambiada.
- Si en la vista en vivo un look de cine se ve flojo, la foto ya sale con la curva. Para verla también en vivo, cambia de modo o de ajuste de imagen una vez.

## 7. Límites
- Todo lo de §2 está verificado en Unicorn, no en la cámara: que la rejilla de 96 nodos sea la curva que llega a la imagen sigue siendo lo inferido en G92. La cadena hasta la SRAM `+0x15300` está leída, no emulada de extremo a extremo.
- No se ha medido cada cuánto se ejecuta la máquina de la LUT (FN-LUT-6) ni cuándo se reconstruye el tono en la vista en vivo.
- `c68[8]` es la ranura de la gamma extendida: con un look de curva activo, una app PMCA que use `setExtendedGammaTable` la vería sustituida en la siguiente reconstrucción. Con Off se devuelve.
