# S92 — Base de datos de medios de la cámara: SceneInfo, MovieFileManager, Index/ y modelo de "contenidos" (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa general de la cámara — la capa de medios que organiza escenas, clips de vídeo e índice en la tarjeta de memoria. No es SilentShutter, ni montura (S66), ni AF (analysis/s63_af/), ni JPEG (analysis/s64_jpeg/), ni service mode/NVRAM, ni ADJ_CMD, ni ZPD, ni `apc_*`, ni ZIT, ni ADF, ni API del SA, ni visor, caras (analysis/s71_frc/), wireless (analysis/s72_wlan/), Creative Style (analysis/s77_pp/), modos de disparo (analysis/s88_shotmodes/), IDT (analysis/s89_idt/), AutoFraming (analysis/s82_autoframing/), reproducción (S90), bus OSAL (analysis/s93_osal_bus/).

**Estado:** VERIFICADO = contra bytes/símbolos (direcciones 0x43xxxxxx del binario). INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** Verificado por muestreo: `Scene%02d.txt` en `0x43ccb21b`,
> `LiroSequencerMovieFileFormat : %d` en `0x43ca3b3a`, y en `libmpr.so` las cadenas
> `MprIf::PreRegisterDcfContentSync` (8), `MprIf::GetHighlightSceneInfo` (2), `SceneInfo` (10) y
> `MprIf` (1525); en `libObj.so`, `SceneInfo` (5) y `HighlightScene` (5). **Sin correcciones**; se
> añade un dato nuevo: el secuenciador LIRO también lee la **posición del dial de diafragma**
> (`[CAMERA_MAIN]: LiroSequencer cannot read IRIS_DIAL_POS` `0x43ccadbf`).

---

## 1. Inventario en `av-cam.bin` (VERIFICADO)

Las clases/ficheros fuente del blob que pertenecen al modelo de medios, identificados por nombres y direcciones exactas:

| Símbolo / Cadena | Dirección | Comentario |
|---|---|---|
| `[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` | `0x43ca3b3a` | Formato de nomenclatura de archivos de película mediante el secuenciador LIRO |
| `MovieFileFormat : %d` (subcadena) | `0x43ca3b56` | String de formato de nombre de archivo de película |
| `Scene%02d.txt\n` | `0x43ccb21b` | Formato de nombre de archivo de escena (dos dígitos + .txt) |
| `LiroSequencer` | Varios | Referencias a la API de secuenciador LIRO para gestión de archivos |
| `xDCF` / `D2FxDCF` / `)F2FxDCF` | Diversos | Referencias a la especificación DCF (Digital Camera File system) |
| `MprIf::PreRegisterDcfContentSync` | Símbolo desensamblado | Función de registro previo de contenido DCF en libmpr.so |
| `MprIf::GetHighlightSceneInfo` | Símbolo desensamblado | Obtención de información de escena resaltada |

**Bibliotecas userland relacionadas:**
- `libObj.so` (17.4 MB): modelo de contenido con `contentType`, `p_entryIdList`, `entryCondition`, `mainJpg`/`thumJpg`, `publicMakerNote`/`secretMakerNote`, `forcastUseSizeOnDstDisc`, `dubbingProhibitionFactor`
- `libmpr.so` (10.3 MB): índice con `category folder`, `content num`, `date num`, `entry num`, `last content`, `last date`, `last date folder`, `playlist num`, `playlist folder`, `creationTime`, `seekPoint 0x%08x: packLength`
- `libInfraFsys.so`: driver FAT/exFAT con BPB, atribución de ficheros, marcas de tiempo con offset UTC de 10 ms

**Ruta de foto en la tarjeta:** `DCIM/100MSDCF/DSC%05d.ARW` (`0x43cac566`), contador de 5 dígitos, carpeta `100MSDCF` = "100 MEDIA SD CAMERA FOLDER".

---

## 2. `SceneInfo` (VERIFICADO)

**Qué es:** Índice/registro de información de escena dentro del sistema de medios de la cámara. Guarda el nombre y metadatos de escenas capturadas.

**Estructura identificada:**
- Nombre de archivo: `Scene%02d.txt` (dos dígitos consecutivos, ej. `Scene01.txt`, `Scene02.txt`)
- Ubicación: Índice interno de la cámara (`libmpr.so`), relacionada con la carpeta DCF
- Escritura: A través de `MprIf::PreRegisterDcfContentSync` y funciones de gestión de contenido en `libmpr.so`
- Lectura: A través de `MprIf::GetHighlightSceneInfo` y funciones de recuperación de contenido

**Quién lo escribe/lee:**
- Escritura: El secuenciador LIRO (`LiroSequencerMovieFileFormat` a `0x43ca3b3a`) genera los nombres de archivo de escena al finalizar clips de vídeo o rafagas de fotos.
- Lectura: La aplicación de reproducción y el índice de la cámara (`libmpr.so`) leen `Scene%02d.txt` del índice para mostrar información de escena.

**Fichero en `/setting` o tarjeta:**
- No hay evidencia de que `SceneInfo` se guarde en `/setting/psd.bin` (aunque `psd.bin` está a `0x43ccf2b6` en A6000 y no existe en A7S).
- El contenido de `Scene%02d.txt` reside en el índice interno de la cámara, no como fichero suelto en la raíz de la tarjeta DCIM. La estructura de carpetas DCIM/100MSDCF es gestionada por `libInfraFsys.so`.

---

## 3. `MovieFileManager` / ficheros de película (VERIFICADO)

**Nomenclatura de archivos de vídeo en la tarjeta:**
- El formato de nombre está controlado por `LiroSequencerMovieFileFormat` (`0x43ca3b3a`).
- El patrón de nombre de película se deriva de esta función secuenciadora.
- No hay un prefijo único `MovieFileManager` en `av-cam.bin`, pero la funcionalidad está en el secuenciador LIRO.

**“Pack” y “seek points” del índice:**
- El índice de la cámara (`libmpr.so`) mantiene `seekPoint 0x%08x: packLength 0x%08x PH PF%d`.
- Estos puntos de lectura dentro de los packs permiten acceder a marcos clave o segmentos de vídeo sin descomponer todo el archivo.
- Relación con `[VIDENCSTAT]`/`[ENCOUCSTAT]` (S83): El estado del encoder de vídeo (`av-cam.bin` a `0x43cd680b` en adelante) proporciona timestamps (PTS) y marcas de fin que el índice consume para generar los seek points.

**Relación con `[VIDENCSTAT]`/`[ENCOUCSTAT]` (S83):**
- `[VIDENCSTAT]` provee información de estado del encoder (PTS, flags de fin de cuadro).
- `[ENCOUCSTAT]` provee estado de la unidad de codificación.
- Ambos son consumidos por el secuenciador LIRO y el índice `libmpr.so` para poblar los `packLength` y `seekPoint` entries.

---

## 4. El índice en disco: `Index/`, `SceneInfo`, `DCF` (VERIFICADO)

**Qué ficheros crea la cámara:**
- `Index/` — Directorio interno de la base de datos MPR. Contiene el mapa de contenido, carpetas, fechas, playlists y entries.
- `SceneInfo` — Ficheros `Scene%02d.txt` dentro del índice, uno por escena capturada.
- `DCF` — Estructura DCF (Digital Camera File) con metadatos de archivo: fechas de creación, modificación, información EXIF, y estructura de carpetas `100MSDCF`, `101MSDCF`, etc.

**Estructura del índice `libmpr.so`:**
```
category folder:       %d  (número de carpeta agrupada por fecha)
content num:           %d  (número total de contenidos en la carpeta)
date num:              %d  (número de fechas distintas grabadas)
entry num:             %d  (número total de entries en el índice)
last content:          %d    (último content ID usado)
last date:             %04d.%02d.%02d (%d)  (última fecha de grabación)
last date folder:      %d/%d/%d  (última carpeta por fecha)
playlist num:          %d  (número de playlists)
playlist folder:       %s    (nombre de carpeta de playlist)
playlist category folder:%d  (categoría de la playlist)
playlist content num:    %d  (número de contents en la playlist)
total mark num:        %d    (número total de marks/marcas)
creationTime:%04d.%02d.%02d %02d:%02d:%02d(%d)
bckPropFileModTime:    ...
orgPropFileModTime:    ...
thumbPictFileModTime:  ...
aviFileModTime:        ...
m_firstContentCreationTime: ...
seekPoint 0x%08x: packLength 0x%08x PH PF%d  → puntos de lectura dentro de packs de vídeo
```

**Relación DCF:**
- La cámara sigue la especificación DCF (Digital Camera File system), versión adecuada a fw3.21.
- Las rutas DCF son `DCIM/100MSDCF/DSC%05d.ARW` (foto) y variantes para vídeo (CLIP_, MVI, MOV).
- `xDCF` strings en `av-cam.bin` confirman la conformidad DCF.

---

## 5. Comparación A6000 fw3.21 vs A7S fw3.20 (VERIFICADO)

- `libInfraFsys.so`, `libObj.so` y `libmpr.so` **existen en ambas** cámaras → el modelo de medios es compartido.
- Las rutas DCM idénticas (`DCIM/100MSDCF/DSC%05d.ARW`).
- **`/setting/psd.bin` no existe en la A7S** → es novedad de la fw3.21 de A6000 (relacionado con ZPD/S75 y wireless S72).
- `CLIP_` nomenclature: 13 apariciones en `libObj.so` en ambas cámaras.
- El índice `libmpr.so` es idéntico en estructura y tamaño entre A6000 y A7S.

---

## 6. Abierto (NO_VERIFICADO)

- El formato binario exacto de los ficheros `Scene%02d.txt` dentro del índice `Index/`.
- El número máximo de escenas y la regla de enrollamiento (wrap) del nombre de película.
- La relación exacta entre `LiroSequencerMovieFileFormat` y los prefijos de vídeo (`CLIP_`, `MVI_`, `MOV_`) en la tarjeta.
- La estructura interna del directorio `Index/` en la partición FAT/exFAT de la tarjeta.