# G03 — Pila de dibujo y presentación en pantalla (avance)

**Fecha**: 28-10-2026
**Estado**: PARCIAL. Capa de dibujo identificada y presentación localizada en una rutina concreta; el
invocador de esa rutina y la relación con `WindowServer`/`ViewSystem` siguen **NO_VERIFICADO**.
**Evidencia reproducible**: `scripts/gui/elf_scan.py` (`plt`, `resolve`, `callers`, `dis`),
`tests/test_gui_elf_scan.py`.

---

## 1. Hallazgo que cambia el método

Las cadenas `WindowServer_DI.cpp`, `WindowServerEGL.cpp`, `ViewSystem::updateFrame`, `drawFramebuffer`,
`EGL_KHR_image`, `DMP2D_*`, `OSD Gain Filter`, `/dev/fb0`… **no tienen ni una sola referencia** en todo el
fichero:

| Búsqueda | Resultado |
|---|---|
| Literal de 32 bits con la dirección de la cadena, en todo el binario | 0 resultados (`/dev/fb0` @ `0xd5f904`, `WindowServer::ViewSystem::ViewSystem` @ `0xd88482`, etc.) |
| `add rD, pc, #imm` (Thumb, 0xA0xx) que caiga en los bloques `0xd5c000–0xd60000`, `0xd77000–0xd79000`, `0xd88000–0xd89000` | 0 resultados |
| Puntero en tablas (`.data.rel.ro`, `.got`, `.data`) | 0 resultados |

Conclusión: son **cadenas muertas** (etiquetas de log/traza con ID, o restos de compilación), no una vía para
localizar el compositor. Cualquier intento de seguir la GUI por `xrefs` de cadena está condenado; hay que ir por
símbolos, llamadas y estructuras.

## 2. La capa de dibujo está **dentro** de `libObj.so` (VERIFICADO)

Al resolver la PLT (ver [G01 §8](g01-arquitectura.md)) aparece un detalle importante: muchas entradas de
`.rel.plt` apuntan a símbolos **definidos en el propio** `libObj.so`. Es el efecto de la *interposición*: las
funciones exportadas con visibilidad por defecto se llaman a sí mismas a través de la PLT.

Así, el motor de dibujo no es una biblioteca externa: son funciones exportadas de `libObj.so`, llamadas por su
propia PLT. Las relevantes:

| Símbolo | Dirección | Tamaño | Papel |
|---|---|---|---|
| `GRM_fbrmSetScreenPreference` | `0x614831` | 88 | preferencias de pantalla |
| `GRM_fbrmInitializeYUV` | `0x614925` | 8 | inicializa la superficie YUV |
| `GRM_fbrmPrepareUpdateYUV` | `0x61494d` | 8 | prepara actualización |
| `GRM_fbrmUpdateYUV` | `0x61495d` | 8 | **presenta** (actualiza la superficie) |
| `GRM_fbrmFillrectYUV` | `0x614965` | 8 | relleno de rectángulo |
| `GRM_fbrmRectblitYUV` | `0x61496d` | 8 | copia de rectángulo |
| `GRM_gpermFillrect` | `0x615249` | 348 | relleno genérico |
| `GRM_gpermRectblit` | `0x6153a5` | 896 | copia/mezcla genérica |
| `GRM_bitmapCreate` | `0x615fef` | 120 | crea mapa de bits |
| `GRM_bitmapGetPhysicalAddress` | `0x616245` | 16 | dirección física del búfer |
| `TsDrawGlyphParams_init` | `0x53e8b9` | 22 | parámetros de dibujo de glifo (texto) |

`GRM` = gestor de recursos gráficos; `fbrm` = gestión del *framebuffer*; `YUV` indica que la superficie de salida
es YUV, no RGB. `Ts*` es el motor de texto (glifos, *layout*, OpenType/Thai/Bidi), coherente con
`ux::core::TextLayout` y `ux::gfxeng::TextSprite`.

## 3. Rutina de presentación (VERIFICADO; invocador NO_VERIFICADO)

Todas las llamadas a `GRM_fbrmPrepareUpdateYUV`/`FillrectYUV`/`RectblitYUV`/`UpdateYUV` caen en un único bloque
`0x12e6d0–0x12e7de` (2, 3, 1 y 2 llamadas respectivamente). La rutina trabaja sobre un objeto `this` con este
mapa de campos, leído directamente de las instrucciones:

| Campo | Uso observado |
|---|---|
| `+0x88` | superficie principal: fuente de `RectblitYUV` y primer argumento de `bitmapGetPhysicalAddress` |
| `+0x8c` | bandera: si es 0, se sale sin presentar |
| `+0x92` | selector: decide si se rellena (`FillrectYUV`) o se copia con compensación |
| `+0x94`, `+0x98` | origen (x, y) y tamaño de la copia |
| `+0x9c`, `+0xa4` | rectángulo de relleno (destino y color/valor) |
| `+0xa8`, `+0xac` | segunda superficie y su origen (relleno alternativo) |
| `+0x3c` (indirecto) | vía `[r5]`: bandera «actualización en curso» que evita reentrada |

Secuencia (resumida del desensamblado):

```asm
0x12e6f2  blx  GRM_fbrmPrepareUpdateYUV
0x12e724  blx  GRM_fbrmFillrectYUV        ; si +0x92 == 0
0x12e748  blx  GRM_fbrmFillrectYUV        ; si +0x88 != 0 (segunda pasada)
0x12e76a  blx  GRM_fbrmRectblitYUV        ; copia con origen +0x94/+0x98
0x12e782  blx  GRM_fbrmUpdateYUV          ; presentación final
0x12e6c4  bl   0x12e6c4                   ; normaliza el código de retorno (0/1)
```

**Lo que no está verificado**: quién llama a `0x12e6d0`. No tiene ninguna llamada `bl`/`blx` directa ni puntero
literal: o se invoca por puntero de estructura/vtable construida en ejecución, o por tabla de salto. Es el
siguiente objetivo de G3.

## 4. Quién usa la copia genérica (VERIFICADO)

`GRM_gpermRectblit` (`0x6153a5`, 896 B) tiene 7 llamadas directas, entre ellas:

| Sitio | Contenedor | Lectura |
|---|---|---|
| `0x5ed8d6` | `ux::core::GraphicsImage::clear(void*, CColor, short, short, short, short)` | limpiar una imagen pasa por la copia genérica |
| `0x615802`, `0x615916` | dentro del propio `GRM_gpermRectblit` | ruta interna (máscara/mezcla) |
| `0xea6a4`, `0x109672`, `0x201388`, `0x3ece7a` | funciones sin símbolo exportado | usos fuera del motor (`GEN_Cache*`, `CameraBackground*`, escalar) |

Y `GRM_bitmapCreate` sólo se llama desde `0x6343d0`, cerca de `DDSUserInit/Res/Sus` (`0x634315–0x634335`),
es decir, la creación de mapas de bits de imagen está en la ruta de recursos/DDS, no en el bucle de dibujo.

`TsDrawGlyphParams_init` se llama desde `0x516ee6` y `0x54944e`, ambos en la zona del motor de texto
(`0x53e8b9` es su propia definición; `0x551915`–`0x5532xx` son `Ts*_init` de OpenType). El texto se rasteriza
en el mismo proceso, sin biblioteca externa de fuentes.

## 5. Consecuencias para la modificación

1. El dibujo es **software propio** sobre superficies YUV (`GRM_fbrm*`), con un *blitter* 2D (`DMP2D_*`) por
   debajo. No hay `libGLES`/`libEGL` en `DT_NEEDED`: si hay aceleración, entra por `DMP_*`/`GRM_*`.
2. Un cambio de interfaz puede hacerse **sin tocar el motor**: basta alterar los datos que alimentan
   `FillrectYUV`/`RectblitYUV` (rectángulos, colores, superficies) o los recursos que decodifica el motor.
3. La presentación es un punto único (`0x12e782`, `GRM_fbrmUpdateYUV`): un *hook* ahí afecta a todo lo visible,
   lo que sirve para *overlays* globales, pero es también el punto de mayor riesgo de parpadeo o bloqueo.

## 6. Siguiente paso exacto

Localizar el invocador de `0x12e6d0`:

- buscar tablas de salto Thumb (`tbb`/`tbh`) cuyos destinos caigan en `0x12e6d0`;
- revisar si el puntero se escribe en `.data`/`.bss` en tiempo de ejecución (constructor que guarda
  `&func` en un objeto) buscando el valor `0x12e6d1` en escrituras `str`;
- si no aparece, pasar a la estructura del objeto (campos `+0x88…+0xac`) y a quién la rellena, que es
  probablemente el verdadero `WindowServer`.

Criterio de cierre de G3: cadena verificada desde un bucle de la aplicación hasta `0x12e782`, con el punto de
enganche estable identificado.

## 7. Reproducibilidad

```bash
L=firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libObj.so
.venv/bin/python scripts/gui/elf_scan.py plt $L | grep -E 'GRM_|TsDraw'
.venv/bin/python scripts/gui/elf_scan.py callers $L 0xe2374 0xdf6dc 0x12e6d1
.venv/bin/python scripts/gui/elf_scan.py dis $L 0x12e6d0 48
.venv/bin/python scripts/gui/elf_scan.py sym $L '^GRM_|^TsDraw'
```
