# G16 — Picture Profile en el núcleo `av-cam.bin`: qué falta exactamente en la A6000 (REA + bytes, 08-11-2026)

**Alcance**: seguimiento de [G15](g15-picture-profile.md) §2 en el núcleo, con una sesión REA/Ghidra sobre `av-cam-a7s.bin` (A7S fw3.20,
misma generación y con Picture Profile) y comparación por bytes/Capstone con `av-cam.bin` de la A6000 fw3.21 (base `0x43541000` en los dos).
**Corrige G15 §2-§3**: la ausencia de `job_EC_CalcCaptureGamma`/`Camera::PP_*`/`Gamma/EC_Gamma.cpp` **no** significa que el
núcleo de la A6000 no sepa aplicar curvas PP; esas piezas son metadatos y una aserción (§3).

**Reproducción**: `scripts/gui/pp_core_audit.py analysis/gui/pp-core-audit.json` (autocomprobaciones sobre bytes).

## 1. Cadena completa de la gamma en el núcleo (igual en las dos cámaras)

| Paso | A6000 fw3.21 | A7S fw3.20 | Igual |
|---|---|---|---|
| Comando LIRO **0x4066** «ajustes de cámara» (42 campos del mensaje → bloque de configuración) | `0x43802a28` | `0x437a9404` | mismo formato y orden; solo cambian los desplazamientos de destino |
| Byte **`0x1a`** del mensaje = **selector de gamma PP** | → `cfg+0x153` | → `cfg+0x165` | sí |
| Selector → par (foto, vídeo) de **número de gamma** (tabla de bytes) | `0x43cb56e6`: índices 0–11 = todos `(0, 0x0a)` | `0x43cab54d`: 3 → `0x16`, 4 → `0x0a`, 5 → `0x00`, 6–9 → `0x18`–`0x1b`, 10 → `0x1c`, 11 → `0x1d` | **no**: la A6000 tiene la tabla en blanco |
| Copia de parámetros de tono al objeto YC (`+0xbd9` gamma, `+0xbd1…+0xbe1`, `+0xc7b`, `+0xc80…+0xc88`; límite gamma ≤ 0x1e) | `0x438546f8` | `0x437db578` | instrucción a instrucción |
| **Tabla de curvas** (puntero por `gamma·2 + modo`, modo 1 = vídeo; el código salta si es nulo) | `0x44001404` | `0x43ffa290` | **no**: 7 entradas de vídeo nulas en la A6000 |
| Curva: 0x101a B (2 048 puntos u16 + cola de 26 B con el número de gamma en `+0x1018`) | 26 curvas | 33 curvas | las curvas de vídeo comunes son **idénticas** salvo `+0x1012` (4 en A6000, 7 en A7S) |
| Rodilla/rango por número de gamma (`0x43867800`) | casos `0x0a`, `0x16`, `0x18`–`0x1b` | además `0x1c`, `0x1d` (`0x437ef210`) | casi |
| `switch` de parámetros por gamma (`cfg+0x3b2…+0x3bc`, escritos por un comando) | `cmp #0x1b` (`0x4384764c`) | `cmp #0x1d` (+ `cfg+0x4a8/0x4aa`) | casi |
| Clasificador de **gamma de captura** para metadatos RDD18/XAVC (`job_EC_CalcCaptureGamma`, `0x437db3c0`, 0x9e B) y su campo en el pin YC (`+0x104`) | **no existe** (el pin `0x43b09620` copia solo `+0xc62`/`+0xbd9`) | sí | no |

## 2. Qué falta en el núcleo de la A6000

| Pieza | Gammas | Tipo de cambio | Tamaño |
|---|---|---|---|
| 5 curvas de vídeo (`0x16`, `0x18`–`0x1b`) + sus 5 punteros | las que el código de la A6000 ya trata | **datos** | 5 × 4 122 B ≈ 20 KB |
| Entradas del selector → gamma (índices 3, 6–9; quizá 4/5 «Movie/Still» forzadas) | ídem | **datos** (bytes de una tabla) | ≈ 10 B |
| 2 curvas (`0x1c`, `0x1d`) + punteros + selector 10/11 | las dos restantes | datos ≈ 8 KB **y código**: ampliar `switch` (`cmp #0x1b` + tabla `tbb`), rango `0x18+3→+5`, rodilla, y campos `cfg+0x4a8/0x4aa` con su comando | código pequeño, pero en varias funciones |
| Clasificador de gamma de captura + campo del pin | metadatos del vídeo (RDD18) | código (≈ 0x9e B) + cambio del pin | opcional: sin él la imagen sale igual y solo falta la etiqueta |

**Identificación de las curvas (INFERENCIA por la forma; no hay cadenas)**. `0x18`–`0x1b` son cuatro curvas de contraste suave
y techo bajo (máximo 957/878/958/958 frente a 1 023 de la estándar), compatibles con **Cine1–4**. `0x16` supera el rango
estándar (máximo 1 727), compatible con **ITU709(800%)** o S-Log2. `0x1c`/`0x1d` tienen el negro elevado (la primera muestra vale 20
frente a 5) y son las otras dos de **{ITU709, S-Log2}**. El orden exacto es NO_VERIFICADO; se puede confirmar en la A7S
cruzando el selector con el valor que envía su `libObj` para cada opción del menú.

**Espacio libre**: el CFW conserva el tamaño de `av-cam.bin`. Hay un hueco de 40 020 B a cero en `0x43faf28c` sin
referencias PC-relativas (cabrían 9 curvas) y otro de 2,4 MB en `0x43d620d9` (probablemente memoria de trabajo). Que ninguno
de los dos se escriba en ejecución está NO_VERIFICADO.

## 3. Correcciones a G15

- `Gamma/EC_Gamma.cpp` solo sale en la aserción de la propia selección de gamma (`0x437dad66` de la A7S). La A6000 tiene esa
  función, sin la cadena.
- `job_EC_CalcCaptureGamma(uchar, PP_COLOR_MODE, PP_MODE)` clasifica la gamma para los **metadatos** del vídeo; no calcula
  la curva. Su ausencia no impide la imagen.
- La conclusión de G15 («el núcleo de la A6000 no calcula curvas PP») queda **superada**. El núcleo sí aplica curvas
  arbitrarias por número de gamma. Le faltan los **datos** de 7 curvas y la tabla del selector, y código solo para las dos últimas.

## 4. Lo que sigue abierto

1. **Userland → byte `0x1a`**: `libObj.so` construye el 0x4066 en las dos cámaras (5 sitios, carga de 0x36 B). Falta ver si
   la `libObj` de la A6000 copia `PARAMID_PP_GAMMA_TYPE` a ese byte (si no, hay que parchearlo o enviarlo desde la UI).
2. **Resto de parámetros PP** (black gamma, black level, knee manual, color depth, detail, color mode): no tienen un comando
   LIRO propio en la A7S. Esta tiene solo tres comandos más que la A6000 (`0x40fb`→`cfg+0x4bc`, `0x40fc`→`+0x3e4`,
   `0x40fd`→`+0xac`), y sus 203 manejadores comunes son iguales salvo 5. NO_VERIFICADO dónde los aplica.
3. Si los parámetros por gamma `cfg+0x3b2…+0x3bc` (exposición por curva) llegan con valores correctos a la A6000. Los escribe
   un comando que existe en las dos cámaras.
4. El significado de `+0x1012` (4 frente a 7) antes de copiar curvas de la A7S.

## 5. Decisión que deja este hito

| Opción | Qué da | Coste | Riesgo |
|---|---|---|---|
| **A. «Cine» en el núcleo con datos** | 5 gammas (Cine1–4 + una de 709/S-Log), elegidas por el selector existente | ~20 KB de curvas + ~10 B de tabla en `av-cam.bin`; sin código en el núcleo | hueco libre NO_VERIFICADO; falta resolver el punto 1 para elegirlas desde la UI |
| B. Las 7 gammas | además las dos restantes | A + parche de código en 3–4 funciones del núcleo | más superficie; prueba en cámara |
| C. Picture Profile completo (UI de la A6300) | menú PP1–PP9 y todos los ajustes | B + UI de G15 (25 clases, vistas, ~30 ProcessIds, NVRAM) + puntos 2–3 | Muy alta |

Recomendación técnica: **A como prueba de concepto**. Primero se resuelve el punto 1 en offline. Después se prueba una curva,
con autorización expresa para la cámara.
