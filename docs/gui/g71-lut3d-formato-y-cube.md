# G71 — LUT 3D del BIONZ X: formato resuelto, descomposición de `.cube` y ajuste «LUT» (15-11-2026)

Objetivo wiki 16 «Importación de LUTs» (ZV-E1), **fase A** (aproximación con el hardware; la fase B es la aplicación exacta por software en el JPEG). Solo ficheros del `.dat` (`av-cam`); sin CFW construido; sin tocar `scripts/gui/harness/`. Código: `scripts/lut/lut3d_emu.py` (Unicorn del generador), `scripts/lut/cube_a6000.py` (descomposición + medidas), `scripts/lut/lut_patch.py` (ajuste «LUT»), tests `tests/test_g71_lut.py` (10). Cierra **CCH-F3** (formato) con los límites de §1.

## 1. Formato de la LUT 3D (CCH-F3) — VERIFICADO en Unicorn salvo lo marcado
Generador `Create3DLUT` = `0x437a1d7e` (el que escribe el búfer; selector de tabla `0x437a24fc`).
- **(a) Ejes**: 5 en **Y** (nodos 0, 64, 128, 192, 256 sobre 0…256: tabla u16 en `0x43bef5d6`) × 9 en **Cb** × 9 en **Cr** (−128…+128 paso 32, tabla `0x43bef5e0`). Índice lógico `j·81 + a·9 + b` (j = Y, a = Cb, b = Cr). Prueba: la conversión SD→HD del generador (`ConvSD`) usa las matrices BT.601→709 (`0x6eb/0xd17` en Y, `0x3f45/−0x1d1e` en Cb, `−0x4b1/0x3ef2` en Cr) con `a` = Cb y `b` = Cr.
- **(b) 7 bits**: **delta con signo (−64…63) respecto al nodo**, no valor absoluto; 0 = sin cambio. Componentes (c0, c1, c2) = (ΔY, ΔCb, ΔCr). Unidades (del generador, `0x437a2204…0x437a226c`): ΔY en pasos de 1/256 de escala; ΔCb/ΔCr = 0,75/256 (el generador calcula `(nuevo − nodo)·0x1555 >> 12`, es decir ×4/3). Rango útil: ΔY ±24,6 %, Δcroma ±36,9 % del semirrango. Empaquetado `0x437a198c`: `dest[perm[j·81+a·9+b]] = (c0&0x7f)<<16 | (c1&0x7f)<<8 | (c2&0x7f)`; `perm` en `0x43bef2ac` (permutación de 0…404, test).
- **(c) Tabla de referencia `[cfg+0xd4]`**: tres planos s8 de 405 B (`+0`, `+0x195`, `+0x32a`, mismo índice). El selector `0x437a24fc` elige entre 4 tablas en BSS (`0x43f9943e`, `0x43f99cc2`, `0x43f98d19` y `0x43f98819 + 162·n`) según el id de modo de color (`cfg+0x7e`). **Todas están a cero en la imagen y ninguna instrucción de `av-cam` las escribe** (REA `xrefs`: solo los literales GOT y el propio selector): o se rellenan en ejecución (copia de un preset) o quedan a cero. **Con referencia a cero y `ConvSD = 0` el generador deja la LUT a cero = identidad** (test Unicorn); con `ConvSD = 1` un ref a cero NO da cero (398 de 405 nodos ≠ 0: es la conversión SD→HD). Si la A6000 real rellena esas tablas en ejecución no se ha podido ver (sin cámara): **NO_VERIFICADO** qué contienen de fábrica.
- Verificación del generador en Unicorn (`lut3d_emu.generar`): con `d8 = 1`, `d9 = 0` y 405×3 deltas aleatorios en ±60 la salida decodificada (con `perm`) = la referencia exacta; el nivel (`pkt+0x23` < 8) escala por nivel/8. `empaqueta_hw` (herramienta) = `generar` byte a byte.
- **Color Depth, Color Chrome (g69) y esta LUT son la misma tabla**: el generador suma los 6 Color Depth (`pkt+0x2a…0x2f`) en el mismo búfer. Con un ajuste «LUT» ≠ Off el búfer entero se sustituye: el Color Depth del usuario deja de aplicarse.
- **(d) Orden respecto a gamma y matriz**: la LUT trabaja en **YCbCr**, así que va después de la matriz de color y de la gamma (en la cadena del BIONZ la conversión a YC es posterior a ambas). **Inferido de la lógica del generador, no medido** (sin cámara). La herramienta lo asume.

## 2. Herramienta `scripts/lut/cube_a6000.py`
Lee `.cube` 3D Adobe (`LUT_3D_SIZE`, `DOMAIN_*`, 17³/33³/65³; interpolación trilineal). Cadena: x → lineal (sRGB) → **M** 3×3 (9 s16 Q10, G27) → **T** curva 1D compartida (2048 u16, escala `i·0,00271`, G25/G67) → YCbCr BT.601 → **LUT 3D** (mínimos cuadrados con trilineal inverso + Laplaciano, cuantizada a s7 con recorte, informa de los nodos recortados). Genera los bytes: M (18 B), T (2048 u16), LUT (`empaqueta_hw`, 0x654 B). Mide ΔE2000 en 30 000 colores aleatorios y en `DSC03799.ARW` revelado (480 px). **Límite**: la gamma de la cámara es una sola tabla (no por canal): lo que difiera por canal va al residuo de la LUT.

ΔE2000 (medio / p95), rejilla densa; entre paréntesis la foto. «nada» = cadena neutra (error de partida):

| LUT sintética (33³) | nada | solo LUT 5×9×9 | M+LUT | T+LUT | M+T+LUT | mejor |
|---|---|---|---|---|---|---|
| identidad | 0,23 / 1,60 (0,16) | 0,23 / 1,60 (0,16) | 0,23 | 0,25 | 0,25 | nada |
| teal & orange | 3,16 / 5,57 (6,43) | **0,44 / 1,59 (0,91)** | 0,46 (0,95) | **0,40 / 1,59 (1,44)** | 1,31 (2,10) | T+LUT en denso; solo LUT en foto |
| película (S + desat. + cruce) | 4,93 / 7,47 (4,61) | 0,67 / 1,80 (0,94) | 0,65 (0,89) | **0,33 / 1,60 (0,34)** | 1,15 (1,47) | T+LUT |

Aporte por etapa: **la LUT 5×9×9 sola ya baja el error 7–7,5×**; la curva compartida aporta mucho en la película (1,01 sola; con LUT 0,67 → 0,33) y nada en teal & orange en foto; **la matriz ajustada por mínimos cuadrados en luz lineal EMPEORA** (M+T+LUT 1,15–1,31): no es el ajuste adecuado (habría que optimizarla en ΔE junto a T; pendiente LUT-A). El ΔE de la identidad (0,23) es el suelo de la tabla de curva de 10 bits/2048 pasos. Panel visual (original | .cube exacto | solo LUT | mejor cadena, por fila teal & orange y película): `img/g71-lut-panel.png`.

## 3. Integración en el `.dat` (ajuste «LUT»)
- **Ids**: ya no quedaba ningún id de Backup libre (los 10 de `0x1070210…19` estaban usados). Se **reutiliza el del antiguo «CFW test»** (`0x1070211`, pid `0xEA`, inerte y sin consumidor): `Ajuste("lut", "LUT", …, Off/LUT1/LUT2/LUT3)` en `scripts/cfw_ajustes.py` (4 opciones, bajo el tope de 7 de G36); «Color Chrome» queda intacto.
- **Parche** (`lut_patch.py`): dos ganchos de 4 B (`ldr.w rX,[r5,#0xc4]` → `bl cueva`) en la escritura al hardware de `0x4381d2a0…0x4381d386`: SA `0x4381d2fe` (→ `0x43b67a68`) y MOV/MON/CAP `0x4381d372` (→ `memcpy`). La cueva lee el ajuste; Off o fuera de rango = puntero original (comportamiento de fábrica), LUT1…3 = `0x43FA4200 + 0x654·(n−1)`. Cueva y 3 tablas en `0x43FA4000` (2,3 MB a cero, como HLG; ver LUT-C).
- Por defecto LUT1 = teal & orange, LUT2 = película, LUT3 = identidad (ceros), generadas con «solo LUT» (matriz y curva **no** integradas: la matriz vive en el preset de Backup `0x30001` y la curva no tiene hueco → LUT-A). Para tablas propias: `descompone(...)` + `empaqueta_hw` y pasarlas a `apply_bytes(data, tablas)`.
- **Pruebas** (Unicorn sobre los bytes reales): bytes originales de ambos ganchos, zona a cero, Off y opción fuera de rango = puntero de fábrica en ambos ganchos, LUT1/2/3 = tabla correcta, tabla de la imagen = `empaqueta_hw`, el diff queda acotado a ganchos + zona.

## 4. Arnés
Overlay y perfil propios (`g71`, puerto 8771; `--no-avcam`; qemu parado y perfil borrado): Ajustes personalizados → «CFW» muestra «LUT: Off» (`img/g71-lut-off.png`), la lista ofrece Off/LUT1/LUT2/LUT3 (`img/g71-lut-lista.png`) y tras elegir LUT1 queda «LUT: LUT1» (`img/g71-lut1-guardado.png`) con `nvram.json` `"1070211": "01"`. **El ISP emulado (G23) no acepta la cadena**: modela Color Depth, no la LUT 3D ni el consumidor del búfer; el efecto visual se muestra con la simulación de Python (panel de §2), no con el arnés.

## 5. Notas para la fase B (aplicación exacta por software)
- Punto de enganche: `0x438c6f68` (`bl 0x438c6d30`, bytes `fff7e2fe`; g65): el revelado ha terminado, el handle u16 del YC está en `r6` y `ctx+0x4ecc` reservado; el YC aún no se ha liberado. Descriptor del YC construido por `FUN_437faf0c`→`FUN_437fae50`→`FUN_437fac18` (objeto de imagen vía `FUN_43561604`, método vtable `+0x308`). **Pendiente**: dirección base, pitch y formato de muestra del búfer (¿YC422 8/10 bit?) y que se pueda reescribir in situ (LIVEND-1).
- Coste estimado (NO medido): interpolación tetraédrica por píxel ≈ 25–30 instrucciones ARM (índice 3 ejes, 4 lecturas de nodo × 3 canales, 3 mul-acumulaciones) más conversión; 24 Mpíxel ≈ 0,6–0,7 G instrucciones ≈ 1 s por foto si el núcleo corre ≈ 700 MHz sin NEON, ≈ 3–4× menos con NEON. Una LUT 17³/33³ completa cabe en SRAM/DDR (33³×3×2 B ≈ 216 KB). Para vídeo/Live View no es viable por software: solo foto.

## 6. Pendientes
CCH-F3 (cerrado en formato), CCH-F5, LUT-A, LUT-B, LUT-C en [PENDIENTES](../PENDIENTES.md).
