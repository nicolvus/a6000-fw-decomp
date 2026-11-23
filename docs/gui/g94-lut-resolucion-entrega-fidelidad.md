# G94 — LUT: más resolución, entrega con el mínimo proceso en la cámara y vista en vivo fiel a la foto (23-11-2026)

Petición: auditar (1) cómo obtener LUT de más resolución, (2) cómo entregárselas a la cámara para que procese lo mínimo y (3) cómo lograr que la vista en vivo sea 100 % fiel a la foto ya tomada. Solo estático + Unicorn sobre `av-cam` (REA para descompilar); sin cámara ni CFW. Código: `scripts/lut/lut_modos.py`; tests `tests/test_g94_lut_modos.py` (2). Contexto: [g71](g71-lut3d-formato-y-cube.md), [g89](g89-lut-sd-en-camara.md), [g90](g90-lut-interpolacion-optimizacion-geometria.md), [g91](g91-lut-completa-por-software.md), [g92](g92-auditoria-cadena-color-lut-general.md), [g93](g93-ampliar-lut-3d-17.md).

## 1. Conclusión
- **Resolución y fidelidad están en conflicto si se usa software sobre la foto.** La única LUT de más de 5×9×9 es el `.cube` aplicado por software al JPEG (G91), y la vista en vivo nunca lo muestra. Para que la vista en vivo sea fiel, la foto tiene que salir de la misma cadena de hardware. La «resolución» se gana entonces ajustando mejor esa cadena, no añadiendo un paso posterior.
- **Hallazgo nuevo:** en vídeo y vista en vivo, el generador de la LUT añade una conversión de BT.709 a BT.601 (ConvSD) que en la foto no existe (§3). El ajuste «LUT» actual (G71/G89) entrega la misma tabla a todos los modos. Si ConvSD está activo, la vista en vivo se desvía de la foto unos 3 ΔE de media (hasta 9–12). Con una tabla precalculada por modo, la desviación baja a 0,09–0,43.
- **Pero en esta A6000 ConvSD no se activa (VERIFICADO en la RAM viva, §3 bis).** Todos los ids de color valen `00`, `01` o `ff` y el bit de capacidad está a 0. Con eso, entregar la misma tabla a todos los modos, como ya hace el ajuste «LUT», da una etapa LUT **idéntica** en vista en vivo y foto. La tabla por modo queda como herramienta por si la cámara mostrara otro estado (LV-FIEL-1); no hace falta cueva nueva.
- **Mínimo proceso:** todo se calcula en el PC (curva T, tabla para foto y tabla para ConvSD, ya en el formato del hardware). La cámara solo carga el bloque y elige un puntero; no hace ninguna cuenta por fotograma ni por cambio de ajuste (§4).

## 2. Más resolución (todas mantienen la vista en vivo igual que la foto)
| Vía | Ganancia medida | Estado |
|---|---|---|
| Ajustar la LUT 5×9×9 en ΔE en el PC, en vez de convertir el `.cube` en la cámara (`lutsd.c`) | G90 (métrica antigua, inflada → LUT-DE-1): película 0,60 en el PC frente a 1,09 del conversor de la cámara | hecho en el PC |
| Curva T tras la gamma + LUT (shaper) | G92: película 0,79 → 0,19, agresiva 2,81 → 1,23; empeora LUT sin curva, así que se elige por LUT | LUT-T-1 |
| Ajustar con el modelo de interpolación real (trilineal o tetraédrico) | G90: ajustar con el modelo equivocado reduce la ganancia | experimento A, en cámara |
| Rejilla mayor (17³, 9³) | imposible (G93) | descartado |
| `.cube` completo por software sobre el JPEG | error de la LUT 0 en la foto; la vista en vivo no lo muestra | G91, opcional («foto exacta») |

El rango de ±64 pasos de 7 bits recorta las LUT fuertes; T lo compensa (G90). La matriz de color no aporta (G90).

## 3. Fidelidad vista en vivo ↔ foto
**Tablas por modo (VERIFICADO en código).** `Create3DLUT` (`0x437a1d7c`) llena un búfer por modo (`+0x8c8 + n·0x654`), y la máquina `0x437a24fc` decide cuándo regenerarlo (`0x437a1a7c`, registro «LutMode Change SA/CAP/MOV-MON»). El generador aplica por modo:
- Level (`pkt+0x23` < 8, escala nivel/8);
- Color Depth;
- negros (`BlkOfs`, G93);
- **ConvSD** (`cfg+0xd9` = `FUN_437a1d14`): solo con `cfg+2` ∈ {0, 1} (MOV/MON; con 0 exige además `pkt+0x16` ∈ {2, 3}), bit 4 del id de color activo y bits 5–6 a cero. **Nunca en SA/CAP** (`cfg+2 = 2` sale con falso).

**ConvSD es 709 → 601 en la croma (VERIFICADO en Unicorn, test).** Con referencia nula, el generador real produce Cb' = 0,986·Cb − 0,111·Cr y Cr' = −0,074·Cb + 0,987·Cr. La conversión analítica de BT.709 a BT.601 es 0,990 / −0,111 / −0,072 / 0,983. La Y sale deformada por el recorte a 0…256 del propio generador. **Corrige la dirección de G71 §1(a)** («601→709»): ConvSD = convertir a SD (601). De ahí se **infiere** que en esos modos la entrada de la LUT es YCbCr 709 y la salida se lee como 601.

**Error de la vista en vivo frente a la foto cuando ConvSD está activo** (ΔE2000 medio / p95 / máx, 21³ colores; foto = CAP con la tabla `q`):

| LUT | misma tabla (gancho actual) | ConvSD de fábrica sobre `q` | **tabla precalculada en el PC** |
|---|---|---|---|
| identidad | 3,24 / 6,54 / 9,5 | 1,56 / 3,64 / 8,8 | **0,09 / 0,19 / 0,3** |
| teal & orange | 3,11 / 6,27 / 9,5 | 1,59 / 3,95 / 11,1 | **0,16 / 0,42 / 1,3** |
| película | 2,94 / 6,48 / 11,8 | 2,09 / 4,89 / 11,7 | **0,43 / 1,10 / 3,1** |

`lut_modos.tabla_convsd(q)` ajusta por mínimos cuadrados, sobre la rejilla 5×9×9 con entrada 709, la salida 601 que da CAP. Muestrear nodo a nodo deja la película en 0,88. La propia conversión de Sony también se desvía (1,56 con la identidad) porque recorta la Y. **Sin ConvSD** (CAP, SA y MOV/MON con la bandera a 0), entregar la misma tabla hace que la etapa LUT sea **idéntica** en la vista en vivo y en la foto.

**§3 bis — ¿Se activa ConvSD en esta cámara? (VERIFICADO en la RAM viva, test).** En el volcado del sistema en marcha (`analysis/camera-dumps/ram-servicio-20261020/ram_0x80000000.bin`, fw 3.21), los GOT de `FUN_437a4358` (`0x4402555c`) y de `FUN_437a1d14` (`0x44021084`) apuntan a `0x43f78dd2` y `0x43e964a4`, como en el fichero.
- Los 16 B de ids de color (`0x43f78dd2 + 0x2e8…0x2f7`), de donde salen todos los valores de `cfg+0x7e`, son `00 00 01 01 00 00 01 01 00 00 ff ff 00 00 ff ff`: ninguno tiene el bit 4.
- El byte de capacidades (`0x43e964a4 + 7`) vale `0x40`: el bit 1, que activaría ConvSD por la vía de Color Depth, está a 0.
- **Conclusión:** `FUN_437a1d14` devuelve 0 en todos los modos (`lut_modos.convsd_activable`). Límite: es un solo estado (modo de arranque tras restaurar la NVRAM); si esa tabla cambiara con el modo, lo vería LV-FIEL-1 leyendo esas dos direcciones por `/dev/mem`.

**Otras fuentes de diferencia (NO verificadas; las comprueba LV-FIEL-1):**
1. **Gamma por modo.** La tabla de curvas `0x44001404` tiene una curva para foto (modo 0) y otra para vídeo (modo 1); en las curvas estándar difieren entre 134 y 437 niveles de 1023 (medido en la imagen). `FUN_43854a28` toma el modo (`bd6`) de `param_1+0x51` y la gamma de `+0x52` (o de `+0x53` con `param_3+8 = 0x11`). Si la vista en vivo del modo foto usa la curva de vídeo, ninguna LUT la iguala a la foto. Además, `FUN_43854a28` recalcula la curva para salidas secundarias (hasta 13 papeles, `FUN_4381b26c`) con su propio índice de gamma. La curva T se aplica en todas, pero tiene que diseñarse para la gamma de cada una.
2. **Ajustes de la cámara.** «Visualización Live View: efecto de ajustes ON» (si está en OFF la vista en vivo ignora los ajustes); DRO/HDR automático (tono local, BDRO) y efectos de imagen apagados; el NR y la nitidez no cambian el color.
3. **Pantalla.** Brillo y temperatura de color del visor/LCD cambian lo que se ve, no la señal. Lo que se puede garantizar es la igualdad de la señal YCbCr, no la del panel.

## 4. Entrega con el mínimo proceso
**Hoy:**
- G89: la cámara lee el `.cube`, lo remuestrea y lo corrige (`lutsd.c`).
- G71/G73: las tablas van en el `.dat` y la cueva las desempaqueta.
- G91: interpolación por software, varios segundos por foto.

**Propuesta (LUT-PKG-1):** un bloque precalculado en el PC por LUT, en la SD (`LUT/LUTn.bin`) o en el `.dat`:

| Campo | Tamaño | Uso en la cámara |
|---|---|---|
| cabecera: firma, versión, índice de gamma de diseño, CRC32 | 16 B | validar; si falla, comportamiento de fábrica |
| curva T (1024 u16 sobre el código de gamma) | 2048 B | puntero en `c68[8]` (`0x440013cc + 32`), `bd5 = 1`, `be1 = 8` (LUT-T-1) |
| tabla CAP/SA (405 palabras u32 en el orden del HW, `empaqueta_hw`) | 0x654 B | puntero que devuelve el gancho |
| tabla ConvSD (`tabla_convsd`, mismo formato) | 0x654 B | puntero si ConvSD = 1 |

5304 B por LUT. **En la cámara:**
- se lee el fichero y se comprueba el CRC una sola vez;
- los ganchos de G71 (`0x4381d2fe`, `0x4381d372`) devuelven el puntero según la bandera ConvSD. La bandera está en `cfg+0xd9` y la máquina la copia a su bloque de salida `+0x55`. El escritor `FUN_4381d294` lee la tabla de `[ctx+0x1b4]+0xc4`, que es ese mismo bloque desplazado `0x80` (`+0x44` → `+0xc4`), así que **la bandera estaría en `+0xd5`** (INFERIDO por el desplazamiento; falta el test de Unicorn → LUT-MODO-1).

Sin parser de `.cube`, sin remuestreo y sin coma flotante en la cámara: la cueva se reduce a lectura, CRC y elección de puntero. Coste por fotograma: cero (la LUT la aplica el hardware). La copia a la SRAM (`0x43b67a68`) y el `memcpy` por modo son de fábrica y ya ocurren.

**Lo que sigue sin poder evitarse:** la tabla pasa por el búfer de parámetros y el escritor del ISP en cada regeneración, igual que con las tablas de Sony.
