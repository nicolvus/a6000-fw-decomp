# G88 — LUTs propios desde `.cube` (17³, 32³, 33³, 64³) y por qué la cámara no los lee de la SD (20-11-2026)

> **Superado en la lectura de SD por [G89](g89-lut-sd-en-camara.md)** (20-11-2026): el userland (`Fsys_*` + Backup) sí permite leer los `.cube` en la cámara; §1 vale solo para `av-cam`.

Petición: `.cube` en la SD, nombre en la lista de «LUT» (G86) y cambio en vivo. Resultado: **ruta PC completa y verificada; lectura en cámara NO implementada** (§1). Código `scripts/lut/sd_lut.py`, `build_fn_lut.py --cubes CARPETA`; tests `tests/test_g88_sd_lut.py` (11). Sin CFW construido, sin cámara.

## 1. Lectura de la SD desde la cámara: descartada con evidencia
- `av-cam` no tiene API de ficheros: sin cadenas FAT/exFAT (S87), el sistema de archivos está en el userland. El único acceso a fichero de toda la imagen es `FUN_439005b8` (REA: un único llamador, `0x437edd44`): arma un mensaje IPC de `0x58` B (clase 2/3, código `0x11`, ruta de `0x40` B, asa u16) y espera la respuesta; devuelve 0 / 4 (envío) / 5 (respuesta ≠ 0). No devuelve datos: el contenido llega a un búfer que `0x437edd44` obtiene con `FUN_437873a4(ctx, 0x1df, 1, …)` (adquisición de un recurso con asa y búfer del tamaño de un ARW, liberado con `FUN_43787180`) y que parsea como TIFF (`DCIM/100MSDCF/DSC%05d.ARW`, g s20).
- Es el camino de «revelar un ARW» de la reproducción: recurso, asa y servicio del lado Linux acoplados a esa tarea. Llamarlo desde el gancho de la máquina `0x437a24fc` (tarea de imagen) exigiría adquirir el recurso `0x1df` (no medido su tamaño/contención), conocer el contrato del servicio del userland (no desensamblado) y no interferir con el revelado; nada de eso es verificable sin cámara y un fallo bloquearía la tarea de imagen.
- Alternativa en userland (`libInfraFsys.so`, `open/read`): es otro binario y otra tarea, sin gancho hacia `av-cam` ni hacia el Backup; no investigada (fuera de alcance y sin forma de probarla).
- Por eso: **los `.cube` se convierten en el PC** y el resultado va al `.dat` (`sd_lut.py`). El usuario copia sus `.cube` a una carpeta del PC, no a la SD.

## 2. Conversión (PC)
`cube_a6000.lee_cube` acepta cualquier `LUT_3D_SIZE ≥ 2` (probado 17, 32, 33, 64; trilineal; `DOMAIN_MIN/MAX`); 1D, filas incompletas → `ValueError`. `descompone(..., solo LUT)` ajusta por mínimos cuadrados la tabla del ISP (5×9×9 en Y/Cb/Cr, 7 bits, G71 §1) y `empaqueta_hw` genera el búfer de 0x654 B que las cuevas de G73 desempaquetan (21 bits). **El ISP admite solo 5×9×9 (405 nodos, deltas de 7 bits): una 32³ o 17³ no cabe**; se remuestrea. La aplicación exacta por software sobre el YC (LUT-B, gancho `0x438c6f68`) sigue sin dirección/pitch/formato del búfer YC y solo valdría para foto, no para el vídeo ni la vista en vivo: no implementada.

ΔE2000 del `.cube` exacto frente a lo que aplica el ISP (20 000 colores aleatorios, medio / p95; test `-s`): **32³ curva gamma 0,8 + tinte: 0,41 / 1,85; 17³ película: 0,66 / 1,78; 33³ teal & orange: 0,45 / 1,58**. Se pierde detalle fino de la LUT (nodos 5 en luminancia); imposible igualar el .cube exacto con el HW.

## 3. Lista y selección
- Tope **3 LUT** por `.dat` (3 tablas de 21 bits en la zona B verificada de G73, 3432 B); más exige otra zona. La fila nativa admite 7 (G36) → hasta 6 con nueva zona.
- Nombres: `Ajuste.opciones` se construye con el nombre de fichero (≤11 car., orden alfabético; faltantes = «Neutro») y entra como texto del nodo (`string_*.uxc`) en el build; los nombres no son dinámicos (cambian reconstruyendo).
- Selección 1…3 → tabla propia en ambos ganchos (SA y MOV), Off/fuera de rango = puntero de fábrica (Unicorn, `P.emular`); el gancho de cambio en caliente (FN-LUT-2) no cambia.

## 4. Qué exige cámara
Que el tamaño/tiempo de remuestreo no importe (offline), el aspecto real del remuestreo, FN-LUT-5/6 de G86, y toda lectura de SD (LUT-SD-1).
