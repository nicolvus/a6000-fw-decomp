# G114 — LUTs propios en la A6000: la mejor vía, qué se puede mejorar del 5×9×9 y especificación para subirlos a la cámara (26-11-2026)

Petición: continuar la integración de LUTs propios, decidir la mejor forma de implementarlos, si se puede mejorar la tabla
5×9×9 y qué debe cumplir un LUT para subirlo directo a la cámara. Sin cámara, sin CFW nuevo instalado: estático + Unicorn + PC.

Código nuevo: `scripts/lut/cube_spec.py` (validador, `tests/test_lut_spec.py`), paquete `.LUT` v2 y su integración en
`scripts/lut/lut_pkg.py`/`lutsd.c`/`lut_patch.py` según el estado que deje [G113](g113-lut-t1-curva-1d.md).
Medidas de las LUTs del usuario: `/home/nicolas/Documentos/a6000/lut-eval/informe.md` (fuera del repo, no se versionan las LUTs).

## 0. Resumen ejecutivo

1. **La mejor manera de implementarlo** es la que ya está montada, con una pieza que falta: **paquete `.LUT` precalculado en el PC
   (tabla 5×9×9 ajustada en ΔE + curva 1D T opcional) → SD → hilo `lutsd` → blob de Backup → ganchos de `av-cam`**.
   No cuesta nada por fotograma, funciona en foto, vídeo y vista en vivo, y no necesita que la cámara entienda un `.cube`.
   El `.cube` en la SD queda como comodidad (la cámara lo remuestrea peor, por nodo, y tarda); el `.cube` por software
   (`lutjpg`) queda como «foto exacta» opcional, porque solo afecta al JPEG y no a la vista en vivo.
   **Antes de instalar o probar nada en la cámara hay que cerrar ZONA-1**: la cueva y las tablas del ajuste LUT están hoy dentro
   de la tabla T1 de estabilización y de las BOKS del YC de captura (G107), y el CFW 3.86 instalado las lleva ahí (ver §1).
2. **La rejilla 5×9×9 no se puede ampliar**: no es una decisión del firmware, es el bloque de hardware (8 SRAM de 64/128 palabras;
   5×9×9 ya ocupa 75 en la más llena; 9³ pediría 100 y 17³ 729). El mismo bloque es idéntico en A7S y A6300.
   Se mejora **sin tocar la rejilla** con: curva 1D T tras la gamma (shaper, ganancia 2–4× en LUT con curva), elección T sí/no
   por LUT, ajuste en ΔE2000 en el PC, y —si la cámara lo confirma— el modelo de interpolación real. La matriz 3×3 M no aporta.
3. **Especificación para subir un LUT**: `.cube` Adobe 3D, rejilla 33³ recomendada (17³/65³ válidas; 2…129 aceptadas),
   dominio 0…1, valores dentro del dominio, **sin LUT 1D**, entrada **Rec.709/sRGB de pantalla (no V-Log/S-Log)**, salida 0…1.
   En la SD: `LUT/LUT1.LUT` … `LUT/LUT6.LUT` (paquete v2 de 3128 B con tabla + curva; v1 de 1080 B sin curva) o
   `LUT/LUT1.cube` … `LUT6.cube` como respaldo. Para la máxima calidad, el `.LUT` debe ser v2 (tabla ajustada en el PC + T).

## 1. Estado real (26-11-2026)

| Pieza | Qué hace | Estado |
|---|---|---|
| LUT 3D del ISP | 5×9×9 en YCbCr, deltas s7, 8 bancos SRAM, escritor `0x43b67a68` | VERIFICADO (bytes), geometría fija |
| `lut_patch.py` | ganchos `0x4381d2fe` (SA) y `0x4381d372` (MOV/MON/CAP) que entregan una tabla propia | hecho, Unicorn; **zona insegura (ZONA-1)**, LUT-C reabierto |
| `film_patch.py` | LUT + **curva 1D tras la gamma** (`bd5=1`, `be1=8`, `c68[8]`), máquina de cambio en caliente, blob «FILM» | hecho y en CFW (G98/G111) |
| `lutsd.c` (userland) | hilo en `viewUnified2.so`: lee `X:/LUT/LUT<n>.cube` o `LUT<n>.LUT`, remuestrea/valida y escribe el blob de Backup `0x150005` | hecho, Unicorn; **sin probar en cámara** (LUT-SD-2) |
| `lut_pkg.py` | `.cube` → tabla 5×9×9 ajustada en ΔE → paquete `.LUT` v1 (1080 B) o v2 (3128 B, con T elegida por LUT) | hecho (v2 en G113) |
| `lutjpg` | `.cube` completo (2…129³, tetraédrico) sobre el JPEG en la cámara | hecho, qemu; **sin probar en cámara** (LUT-SW-2) |
| `.cube` en la SD | respaldo si no hay `.LUT` | hecho, Unicorn; **sin probar en cámara** |

**Riesgo de zona (ZONA-1), grave y previo a cualquier prueba nueva.** La cueva y las tablas del ajuste «LUT» están en
`ZONA_A` (`0x43be3b28…0x43be4330`) y `ZONA_B` (`0x43c1ff24…0x43c20c8c`), que **no son huecos**: G107 (`docs/gui/g107-causas-pp-ids-zonas.md`)
demuestra que son la tabla T1 de estabilización (1025 u16, leída por `0x43705a34` y usada en un modo EIS) y dos tablas `s16` 6×13×11
del YC de captura `BOKS` (descriptor `0x438f6fa4`). La cueva pisa T1[512…1024] y las tablas pisan la primera mitad de BOKS; el
**CFW 3.86 instalado** lleva exactamente eso. La función Film ya se mudó a `ZONA_G18`; el ajuste LUT no. Hasta cerrar `ZONA-1`
(reubicar y verificar con el criterio de G107/G74), **no se debe instalar ni probar el ajuste LUT en la cámara**: la fila `LUT-C`
figura como cerrada pero su premisa («fragmento libre verificado») es falsa.

Límite grande y honesto: **nada de esto se ha visto funcionando en la cámara**. El CFW 3.86 (con la lectura de SD y el paquete v1)
está instalado, pero LUT-SD-2 sigue abierto: falta un `.LUT`/`.cube` en la SD, insertar la tarjeta y comprobar el blob y el look.
Por eso este informe separa lo verificado offline de lo que solo la cámara puede cerrar (§9).

## 2. La tabla 5×9×9: qué se puede mejorar y qué no

### 2.1 Ampliarla: imposible (no es firmware)

- La escritura al hardware (`0x43b67918`, 8 casos) usa 8 SRAM con paso `0x200`/`0x100`: 128 palabras en el banco 0 y 64 en los demás.
  5×9×9 reparte 75/60/60/48/50/40/40/32. Cualquier eje +1 en esa geometría (6×9×9, 5×10×10) desborda un banco de 64; 9³ pediría 100
  y 17³ 729. **Matiz de la auditoría:** «5×9×9 es el máximo del mapa» es demasiado fuerte; con el modelo del test, 8×8×8 = 512 nodos
  cabría exacto (64 por banco) y `cabe(8,8)` nunca se probó. Pero eso no cambia la conclusión: la rejilla la fija el generador
  (`Create3DLUT` recorre 9×9×5 fijos, la copia es de `0x654` B y los 18 registros de control son de 1/6 bits), no la capacidad.
- El generador (`Create3DLUT` `0x437a1d7c`) recorre 9×9×5 fijos; la copia es de `0x654` B; los 18 registros de control son de 1/6 bits.
  No hay tamaño, stride ni eje parametrizable.
- El bloque es **idéntico byte a byte** en A7S (`0x43b61eba`) y A6300 (`0x43c2be20`): es el IP BIONZ X, no un recorte de la A6000.
- Prueba: `tests/test_g93_lut_geometria.py`. Informe: [G93](g93-ampliar-lut-3d-17.md).

Conclusión: 17³ en el ISP está descartado con evidencia; solo se consigue fuera del ISP (software sobre el JPEG) o en postproducción.

### 2.2 Curva 1D tras la gamma (shaper): la mejora real

La cadena de tono del firmware tiene una ranura de curva 1D (`c68[8]`, `0x440013ec`) que se aplica **después de la gamma** y
llega a vídeo, vista en vivo y foto. Es la descomposición estándar «shaper + LUT 3D»:

| LUT sintética de G90 (33³) | solo 5×9×9 | T + 5×9×9 |
|---|---|---|
| película | 0,79 / 1,81 / 6,0 | **0,19 / 0,50 / 1,3** (0,202 con la curva compacta de 33 nodos que guarda la cámara) |
| agresiva | 2,81 / 6,91 / 16,3 | **1,23 / 3,26 / 8,4** |
| teal & orange | **0,06 / 0,15 / 0,4** | 0,19 / 0,59 / 6,0 |
| suave | **0,09 / 0,24 / 1,0** | 0,16 / 0,52 / 3,5 |

ΔE2000 medio / p95 / máx, métrica corregida (G91 §5), modelo sRGB de `cube_a6000`; en cámara la gamma no es exactamente sRGB
(el adaptador de G97 mide 1,7 ΔE de mediana solo por eso). **T no siempre ayuda**: en LUT suaves o de solo color empeora; hay que
elegir por LUT (`cube_a6000.elige` ya lo hace). La implementación existe en `film_patch.py` (G98) para los looks Film; llevarla
al ajuste «LUT» genérico es [G113](g113-lut-t1-curva-1d.md)/LUT-T-1. **Matiz importante:** la T que vale en la cámara se construye
sobre el código de gamma real (`sosang_a6000.t_grises`/`_con_t`, 1024 u16), no sobre el modelo sRGB de `descompone`; las cifras de
T de esta tabla son del modelo sRGB y sirven para decidir sí/no, no como curva final.

Por qué funciona: la rejilla tiene solo 5 nodos de Y (0, 64, 128, 192, 256) y 9×9 de croma. La curva absorbe el contraste tonal
(que no necesita resolución espacial) y libera los nodos de Y para el color; además evita el recorte de ±64 del delta s7, que en
LUT fuertes satura cientos de nodos.

### 2.3 Otras mejoras, por orden de relación calidad/coste

1. **Ajuste en ΔE2000 en el PC** (ya es el método por defecto): 0,20–0,60 ΔE medio frente al 0,30–1,8 del ajuste por mínimos
   cuadrados; la cuantización s7 aporta +0,00–0,02. El error grande es el submuestreo a 405 nodos, no los bits.
2. **Modelo de interpolación**: ajustar con el modelo equivocado cuesta 0,6 → 1,48 ΔE en una LUT de película. El optimizador
   admite `tri`/`tetra`/`ambos`; por defecto `ambos`. Decidirlo exige el experimento de cámara LUT-INT-1 (G90 §A): no se puede
   deducir del binario.
3. **Paquete precalculado** en vez de que la cámara remuestree: teal&orange 0,40 → 0,07; película 1,05 → 0,79 (Unicorn, métrica
   antigua). Además quita parser, coma flotante y tiempo de arranque en la cámara.
4. **T sintética por look**: la T de G97 se elige por look (`T_grises`, `T_intervalos`, `sin_T`) y se guarda con la tabla. Es el
   mismo patrón que debe seguir el `.LUT` v2.
5. **Matriz 3×3 M: no**. El ajuste lineal por mínimos cuadrados empeora (película 0,28 → 1,03; agresiva 1,10 → 2,00) y una
   búsqueda Powell en ΔE no encontró mejora (M≈I). Descartado como etapa propia.
6. **Color Depth / LutMode / Level: no añaden geometría**. Color Depth se suma a la misma tabla (si se sustituye la tabla, deja de
   aplicarse); LutMode solo elige tabla y Level escala el nivel/8. Las «2D» son la misma tabla de `0x654` B.
7. **Segunda curva 1D** (`0x43bfaa86`, 512 puntos, de fábrica identidad): existe, pero su consumidor y su etapa no están
   localizados ([LUT-2C-1](g92-auditoria-cadena-color-lut-general.md)). Si resultara ser una curva **posterior** a la LUT 3D, sería
   una mejora adicional real; hoy no se puede afirmar.
8. **Vía software** (`lutjpg`): `.cube` exacto 2…129³, tetraédrico; el error de la LUT es 0 y solo queda la recompresión JPEG
   (q98: 0,57 ΔE medio). Solo foto y varios segundos por imagen; la vista en vivo no lo muestra.

## 3. Las cuatro formas de entregar un LUT

| Vía | Alcance | Calidad (ΔE medio) | Coste en cámara | Estado |
|---|---|---|---|---|
| `.LUT` v2 en SD → blob → ganchos (tabla + T) | foto, vídeo, vista en vivo | la mejor del hardware (T+LUT: 0,19 película) | leer 3–5 KB y CRC al insertar tarjeta; 0 por fotograma | G113 (T) + LUT-SD-2 |
| `.cube` en SD → `lutsd.c` remuestrea | ídem | peor (muestreo por nodo: 1,05–1,43 en película) | parser + remuestreo una vez por tarjeta | hecho; LUT-SD-2 |
| `.cube` en SD → `lutjpg` sobre JPEG | solo foto | exacta (0 en la LUT; +0,57 por recompresión) | proceso aparte, segundos por foto | hecho; LUT-SW-2 |
| tablas en el `.dat` del CFW | ídem hardware | ídem | ninguna | hecho; requiere construir CFW |

**Recomendación:** `.LUT` v2 como vía principal; `.cube` en la SD solo como respaldo/comodidad; `lutjpg` como opción «foto exacta»
para LUT que el 5×9×9 no puede representar (B/N, curvas muy fuertes); el `.dat` solo para los looks que deban ir de fábrica en un CFW.

## 4. Especificación de entrada: el `.cube`

Formato: Adobe Cube LUT 1.0, texto, comentarios con `#`.

| Campo / requisito | Valor | Por qué |
|---|---|---|
| `LUT_3D_SIZE` | **33** recomendado; 17, 65 válidos; 2…129 aceptados | 33³ = 35 937 nodos es el equilibrio habitual; 65³ tarda en el ajuste y ocupa 1,6 MB en `lutjpg`; 129³ solo para software |
| Filas | exactamente `n³`, tres números por fila | si falta o sobra una, no se puede indexar |
| `DOMAIN_MIN` / `DOMAIN_MAX` | 0 0 0 / 1 1 1 (o dominio coherente) | el pipeline normaliza con ellos |
| Valores | finitos, dentro del dominio | fuera de rango se recorta en silencio |
| `LUT_1D_SIZE` / `LUT_1D_INPUT_RANGE` | **prohibido** | ni el ISP ni `lutjpg` aplican shaper 1D; el shaper va aparte (T) |
| `LUT_3D_INPUT_RANGE` | evitar (se interpreta como 0…1) | no está soportado |
| Espacio de entrada | **Rec.709/sRGB de pantalla** (lo que ve la cámara en JPEG Estándar) | la A6000 no graba V-Log/S-Log; un `.cube` V-Log sale lavado |
| Salida | 0…1, display-referred | el hardware aplica deltas s7 sobre YCbCr |
| Nombre | `LUT1.cube`…`LUT6.cube`, 8.3, en `LUT/` de la raíz | el hilo busca exactamente eso |
| Tamaño | 33³ ≈ 1,0 MB; 65³ ≈ 7,5 MB (solo `.LUT`/software) | se lee una vez por inserción |
| Líneas | ≤ 95 caracteres; `%0.6f` o menos decimales | el lector de la cámara (`lutsd.c`, `char line[96]`) trunca la línea y falla |
| Rejilla > 64³ | solo por `.LUT` (calculado en el PC) o `lutjpg` | el parser `.cube` de la cámara rechaza `n > 64` |

**Cómo lo hace Sony de serie (para comparar).** Los modelos con «Manage User LUTs» (FX3/FX30/A7S III fw≥4, A6700, ZV-E1,
A1 II…) importan `.cube` **3D de 17³ o 33³**, con entrada declarada **S-Gamut3.Cine/S-Log3**, en `/Private/Sony/PRO/LUT` de la
tarjeta, nombre ≤63 caracteres y **≈1 MB máximo** (lo que excede no se importa). No documentan dominio ni 1D, y la A6000 no está
en la lista: no tiene importación nativa. Este proyecto hace lo mismo pero con la ruta propia `LUT/`, entrada **Rec.709** (la
cámara no graba log) y un paquete de 1080 B que la cámara solo valida y copia.

Avisos que da el validador (`python3 scripts/lut/cube_spec.py A.cube`): rejilla no habitual, datos fuera de dominio, identidad
(no aporta), salida constante, LUT «uniforme» (1D disfrazada de 3D) y **entrada logarítmica** por `TITLE`/`#LUMIXPHOTOSTYLE`.

## 5. Especificación de salida: el paquete `.LUT`

Formato v1 (1080 B, little-endian), el que entiende `lutsd.c` y `lut_pkg.py`:

| Desplazamiento | Campo | Valor |
|---|---|---|
| 0 | firma u32 | `A6LT` (`0x544C3641`) |
| 4 | versión u8 | 1 |
| 5 | reservado u8 | 0 |
| 6 | longitud u16 | 1064 |
| 8 | CRC32 IEEE u32 | de la carga (bytes 16…1079) |
| 12 | reservado u32 | 0 |
| 16 | carga 1064 B | 405 nodos × 21 bits (7 bits por componente, orden lógico `j·81 + a·9 + b`) |

La carga es la tabla de `0x654` B del hardware compactada sin pérdida (3 componentes s7 → 21 bits); `av-cam` la desempaqueta con
la permutación `0x43bef2ac`. Si el CRC o la firma fallan, la ranura se ignora y se usa el `.cube`; si tampoco, la tabla de fábrica.

**v2 (con shaper T, [G113](g113-lut-t1-curva-1d.md)):** 3128 B. Misma cabecera con versión 2, byte 5 = `usa_T` (0/1), y CRC32 sobre
los 3112 B que siguen a la cabecera. Carga = tabla 1064 B (idéntica a v1) + curva T de 1024 u16 (2048 B) sobre el código de gamma.
`usa_T = 0` guarda la curva igualmente; la cámara solo la usa si vale 1. Un v1 en una cámara v2 y al revés se rechaza por longitud y
se cae al `.cube` sin romper nada. En el blob de Backup la curva se guarda compacta (33 nodos = 68 B) en `+0x1900 + (k−1)·68`; en el
`.dat`, 3 registros de 68 B. El `.cube` **no** lleva curva: la cámara no puede calcularla en punto fijo, así que una LUT que la necesite
tiene que llegar como `.LUT` v2 hecho en el PC.

Nombres y ubicación: `LUT/LUT1.LUT` … `LUT/LUT6.LUT`. El hilo prueba `.LUT` antes que `.cube`, y `/` antes que `\`.
Insertar o reinsertar la tarjeta dispara el barrido; no hay que reiniciar.

## 6. Flujo recomendado para hacer tus LUTs

1. **Diseña el look sobre una imagen Rec.709/sRGB** (el JPEG Estándar de la cámara), no sobre log. Si partes de un `.cube` V-Log,
   conviértelo antes a Rec.709 con el shaper de ese log; si no, el resultado en la A6000 sale plano y lavado.
2. **Exporta `.cube` 33³**, dominio 0…1, sin 1D, con la transformación completa (contraste, color, virado). Para B/N o curvas
   extremas, asume que el 5×9×9 no llega: usa `lutjpg` o sube el contraste con la receta de la cámara.
3. **Valida**: `python3 scripts/lut/cube_spec.py mi.cube` (debe decir HARDWARE; si dice SOLO SOFTWARE, es 1D disfrazada).
4. **Convierte y mide**: `python3 scripts/lut/lut_pkg.py mi.cube LUT1.LUT` (G113: elige T sí/no por ΔE y escribe v2 con la curva;
   `--sin-t` fuerza v1). Elige la variante con menor ΔE, no la que «parezca» mejor.
5. **Copia** `LUT1.LUT`…`LUT6.LUT` a `LUT/` en la raíz de la SD (FAT32/exFAT), inserta la tarjeta y elige la ranura en el menú.
6. **Comprueba en la cámara** (pendiente LUT-SD-2): que el look cambia en vista en vivo y en la foto, y que el blob `0x150005`
   tiene las ranuras válidas. Si una ranura no carga, el diagnóstico del CFW 3.84+ deja los códigos en `0x2000` del blob.

### 6.1 Cómo diseñarlo para que el 5×9×9 lo pueda seguir

- **Trabaja en pantalla, no en log.** El LUT se aplica después de la gamma: la entrada es la señal YCbCr de la cámara
  (JPEG Estándar). Si lo diseñas en S-Log/V-Log necesitas primero la transformación de salida de ese log; si no, el resultado
  sale lavado (medido: blanco 81–87 % en vez de 97–99 %).
- **No salgas del rango de la tabla.** El delta es de ±64 en 7 bits: ±24,6 % de luma y ±36,9 % de croma por nodo. Los looks que
  piden más (B/N total, cruces de canal muy fuertes) saturan cientos de nodos: 203/405 en `classic_neg`, 384/405 en
  `eterna_bleach_bypass`, 565 en Tri-X. Para eso está `lutjpg`, no el ISP.
- **Deja el contraste para la curva T y el color para la LUT.** Si la LUT mueve mucho la luminancia, T la absorbe mejor; si solo
  mueve el color, T suele empeorarla (medido en las 6 películas: ayuda en Kodachrome/Ektachrome, estorba en Portra/Pro 400H).
- **Comprueba la rampa de grises y la carta de color** antes de subir: un look que en el PC mide 0,2 ΔE puede recortar 0 nodos o
  200; el informe del conversor lo dice (`rec`).
- **Una LUT por ranura, sin duplicados.** El menú tiene 6 ranuras fijas («LUT 1»…«LUT 6»), sin nombres dinámicos; el nombre del
  fichero es la ranura.
- **No metas 1D.** El shaper va aparte (T). Un `.cube` «1D disfrazado de 3D» (salida independiente de un eje) se detecta y se
  rechaza para el hardware.

## 7. Medidas de las LUTs que ya tienes

**75 `.cube` validados** (todos 33³, 0 valores fuera de [0,1], sin 1D ni NaN) y **21 medidos**. Solo las 6 de `luts/peliculas/`
están hechas para la A6000; las 69 de `luts/sosang/` son de una Panasonic S1II (`TITLE "S1II Standard - NNNNVLOG"`,
`catalog.json: defaultCamera: S1II`) y esperan el Estándar de esa cámara: **salen planas en la Sony** (rampa de gris 78–87 % frente a
97–99 % de las de películas) y saturan la tabla (31–384 de 405 nodos recortados). Las 29 de `sosang/vlog` esperan V-Log y no son
aplicables (la A6000 no graba log). `luts/Ektar100CA.cube` es un render `GH7 Standard` de otra cámara.

ΔE2000 medio / p95 / máx sobre 20 000 colores aleatorios; «foto» = 20 000 píxeles reales de 4 JPEG de la A6000; `rec` = nodos que
el hardware no puede representar (±64). Medido con `descompone(usa_M=False, metodo="de", modelo="ambos")`.

| `.cube` | solo 5×9×9 (denso) | foto | rec | T + 5×9×9 (denso) | foto | rec | mejor para la cámara |
|---|---|---|---|---|---|---|---|
| portra400 | 0,225 / 0,59 / 1,4 | 0,218 / 0,41 | 0 | 0,248 / 0,64 / 1,5 | 0,249 / 0,48 | 0 | **solo LUT** |
| pro400h | 0,272 / 0,85 / 2,3 | 0,276 / 0,53 | 0 | 0,299 / 0,90 / 1,9 | 0,312 / 0,63 | 0 | **solo LUT** |
| gold200 | 0,303 / 0,79 / 2,4 | 0,365 / 0,68 | 0 | 0,280 / 0,72 / 2,1 | 0,362 / 0,72 | 0 | T (leve) |
| ektachrome_e100 | 0,376 / 0,86 / 2,9 | 0,558 / 1,03 | 0 | 0,284 / 0,85 / 3,8 | 0,400 / 0,84 | 0 | **T** |
| kodachrome64 | 0,638 / 1,78 / 4,8 | 0,855 / 1,61 | 0 | 0,420 / 1,27 / 4,0 | 0,548 / 1,21 | 0 | **T** |
| velvia50 | 0,667 / 1,73 / 5,9 | 0,843 / 1,66 | 28 | 0,636 / 1,83 / 6,5 | 0,888 / 2,04 | 11 | solo LUT (T empeora la foto) |

La T de esta tabla es la del modelo sRGB (`descompone`), no la curva de 1024 u16 sobre la gamma real de la cámara: sirve para
elegir T sí/no; la curva final se construye con `sosang_a6000.t_grises`/`_con_t` (G97). La ganancia de T medida en cámara con la
gamma real puede diferir (el adaptador de G97 tiene 1,7 ΔE de mediana).

Pack recomendado para las 6 ranuras, por calidad medida: **LUT1 portra400 · LUT2 pro400h · LUT3 gold200 · LUT4 ektachrome_e100 ·
LUT5 kodachrome64 · LUT6 velvia50**. Los paquetes de referencia están en `lut-eval/pack/LUT1…6.LUT` (v1, sin T). Con G113 se regeneran con `lut_pkg.py` (v2, T automática
por LUT); recuerda que la T de la tabla es la del modelo sRGB y la definitiva se construye sobre la gamma real. El resto de `sosang/std`
solo es fiel con el `.cube` completo por software (`lutjpg`).

## 8. Qué se puede mejorar todavía (y qué no)

| Idea | Veredicto |
|---|---|
| Rejilla 17³/9³ en el ISP | **imposible**: SRAM y generador fijos (G93) |
| Curva T tras la gamma | **hecha en Film**; falta en el ajuste LUT genérico (G113) |
| Elegir T por LUT | **necesario** (medido: ayuda 2–4× o empeora 0,1–0,4) |
| Ajuste en ΔE2000 + modelo real | hecho el ajuste; el modelo exige cámara (LUT-INT-1) |
| Matriz M | **no** (empeora) |
| Paquete precalculado | **hecho** (v1); v2 con T en G113 |
| `.cube` completo por software | **hecho** para foto (LUT-SW-2) |
| Segunda curva 1D post-LUT | abierta (LUT-2C-1); sin consumidor localizado |
| Reubicar cueva/tablas (ZONA-1) | **obligatorio antes de cámara**: ZONA_A/B están ocupadas (G107) |
| Subir el LUT por USB/red | **no existe** en la A6000: solo SD (la app no tiene API de LUT) |

## 9. Lo que solo la cámara puede cerrar

1. **LUT-SD-2**: `.LUT` y `.cube` en la SD, blob `0x150005`, look en vista en vivo y foto. Es el bloqueo real de todo lo demás.
2. **LUT-T-2**: que la curva T compuesta llegue al procesador en los tres modos y que el look coincida con `cube_a6000`.
3. **LUT-INT-1**: trilineal o tetraédrica; cambia el ajuste óptimo y el modelo del PC.
4. **LUT-SW-2**: que `lutjpg` corra en la cámara (Cortex-A5, 204 MB) y cuánto tarda por foto.
5. Orden real gamma/matriz/LUT y la gamma por modo (inferidos, no medidos).
6. **ZONA-1**: reubicar cueva y tablas fuera de T1/BOKS y verificar la zona nueva. Es requisito previo para LUT-SD-2/LUT-T-2. Si no
   se reubica, el ajuste LUT puede corromper la estabilización en un modo EIS y el YC de captura (G107).

## 10. Referencias

[G71](g71-lut3d-formato-y-cube.md) formato · [G89](g89-lut-sd-en-camara.md) SD · [G90](g90-lut-interpolacion-optimizacion-geometria.md)
interpolación/optimización · [G91](g91-lut-completa-por-software.md) software · [G92](g92-auditoria-cadena-color-lut-general.md) cadena y T ·
[G93](g93-ampliar-lut-3d-17.md) geometría · [G94](g94-lut-resolucion-entrega-fidelidad.md) entrega/modos ·
[G95](g95-lut-paquete-precalculado.md) paquete · [G96](g96-peliculas-iconicas.md)/[G97](g97-cfw-film-sosang.md) películas ·
[G113](g113-lut-t1-curva-1d.md) T en el ajuste LUT · [PENDIENTES](../PENDIENTES.md) filas LUT-*.
Evidencias completas (auditoría, medidas de los 75 `.cube` y especificaciones de otros fabricantes):
[reports/lut-20261126](../../reports/lut-20261126/README.md).

Especificación Adobe Cube LUT 1.0: <https://github.com/ImageEngine/gaffer/wiki/File-Formats#cube-lut>
Sony, LUTs de usuario: <https://helpguide.sony.net/ilc/2210/v1/en/contents/TP1000888940.html> ·
<https://www.sony.com/electronics/support/articles/00283315> · <https://www.sony.com/electronics/support/articles/00253964>
