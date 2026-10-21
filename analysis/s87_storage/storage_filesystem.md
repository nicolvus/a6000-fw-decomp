# S87 — Almacenamiento, sistema de archivos y tarjeta de memoria (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: la capa de **almacenamiento** —
montaje de medios, estructura **DCIM**, nomenclatura de ficheros, el **índice** de la cámara y el
`/setting/psd.bin` — repartida entre el `av-cam.bin` y el userland (`libInfraFsys.so`,
`libObj.so`, `libmpr.so`). No es la línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD,
ni ZPD (S75), ni ZIT (S80), ni ADF, ni el visor, ni las caras (S71), ni el wireless (S72), ni los
modos de disparo (S88), ni el IDT (S89), ni AutoFraming (S82).

**Estado:** VERIFICADO = contra bytes/símbolos. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** El borrador del subagente daba **offsets de fichero**
> (`0x772148`…) en vez de direcciones del binario, afirmaba que el prefijo `CLIP_` estaba en
> `av-cam.bin` (está en el userland) y no localizaba la implementación de exFAT (está en
> `libInfraFsys.so`, con estructuras BPB y atributos FSYS).

Artefactos: `tests/test_s87_storage.py`.

---

## 1. En `av-cam.bin` (VERIFICADO)

| cadena | dirección A6000 | dirección A7S |
|---|---|---|
| `[CAMERA_MAIN_SYNC]: ##### ExternalStorageStart() Error` | `0x43cb3148` | `0x43cb4372` |
| `[CAMERA_MAIN_SYNC]: ##### ExternalStorageAcquire() Error` | `0x43cb317f` | — |
| `[CAMERA_MAIN_SYNC]: ##### ExternalStorageRelease() Error` | `0x43cb31b8` | — |
| `DCIM/100MSDCF/DSC%05d.ARW` | `0x43cac566` | `0x43cb022b` |
| `DCIM/100MSDCF/DSC00001.ARW` (ejemplo literal) | `0x4401ea7f` | `0x440241e5` |
| `/setting/psd.bin` | `0x43ccf2b6` | **0 (no existe)** |
| `[CAMERA_MAIN]: LiroSequencerMovieFileFormat : %d` | `0x43ca3b3a` | — |

**Conclusiones:**
- El **medio externo** se acquisitiona desde `CAMERA_MAIN_SYNC` (el `SyncResMgr` de S81): el
  almacenamiento es un **recurso sincronizado** como el resto de periféricos.
- La ruta de la foto RAW es **`DCIM/100MSDCF/DSC%05d.ARW`** (contador de 5 dígitos) → carpeta
  `100MSDCF` = "100 **M**edia **SD** **C**amera **F**older" (INFERENCIA por el nombre).
- **`/setting/psd.bin` es una novedad de la fw3.21 de A6000** (0 apariciones en la A7S) → coherente
  con S75 (origen "from body" de los datos ZPD) y con S72 (`CameraOnDemandSaver.so` escribe ahí).
- **No hay ninguna cadena `exFAT` ni `FAT` en `av-cam.bin`** (0 hits) → la implementación del
  sistema de archivos está **en el userland**, no en el firmware de la cámara.

## 2. El driver de sistema de archivos: `libInfraFsys.so` (VERIFICADO)

375 524 B en la A6000 (373 900 B en la A7S): **51 apariciones de "EXFAT"** y **8 de "FAT32"**, con
las estructuras del **BPB** (Block Parameter Block) de FAT y los atributos del sistema de archivos:

- `BPB_Media = 0x%02x`, `BPB_TotSec16/32 = 0x%08lx`, `block size (adj|org)`, `block start(adj|org)`
  → es el **BPB de FAT12/16/32** (número de sectores, tamaño y posición de los bloques).
- `FSYS_ATTRIB_ALL / ARCHIVE / DIRECTORY / HIDDEN / NONE / READONLY / SYSTEM / VOLUME` → el
  **conjunto de atributos** de la entrada de fichero.
- Metadatos con marca de tiempo: `create time/date`, `access time/date`, `create UTC Offset`,
  `create time_10ms` → la fecha se guarda con precisión de 10 ms y con **desplazamiento UTC** (el
  índice de la cámara es horaware).

## 3. El modelo de contenido: `libObj.so` (VERIFICADO, 17.4 MB)

Es la **capa de objetos** de la cámara (la misma familia que `libObj` ya documentada en el proyecto
para el lado Linux/SDF). Cadenas relevantes para el almacenamiento:

- **Nomenclatura**: 13 × `CLIP_` (los clips de vídeo), y en el volcado de una entrada:
  `contentType`, `p_entryIdList`, `entryCondition`, `p_listInfo`, `mediaSizeOnDstDisc`,
  `remainSizeOnDstDisc`, **`forcastUseSizeOnDstDisc`** (sic), `isExistUnsupportedContent`,
  `dubbingProhibitionFactor`, `mainJpg`, `thumJpg`, `screenNail`, `exifSrcArea`, `lensModel`,
  `model`, `pimInfo`, `publicMakerNote`, `secretMakerNote`, `software`, `mpfSrcArea`.
  → INFERENCIA: `forcastUseSizeOnDstDisc` es la **estimación del espacio que ocupará** la siguiente
  captura (el mecanismo de "reducir/divide" cuando la tarjeta se llena) y `remainSizeOnDstDisc` el
  espacio libre; `dubbingProhibitionFactor` impide duplicar (copiar) contenido.
- Los **MakerNote público y secreto** (S71) viajan como áreas del objeto, junto con la miniatura
  (`thumJpg`) y el JPEG principal (`mainJpg`).

## 4. El índice de la cámara: `libmpr.so` (VERIFICADO, 10.3 MB)

El "MPR" mantiene la base de datos de lo grabado, con el modelo de **carpetas por fecha y
contenido**:

- `category folder`, `content num`, `date num`, `entry num`, `last content`, `last date`,
  `last date folder` (`%ld/%ld/%ld`), `last folder date`, `playlist num`, `playlist folder`,
  `playlist category folder`, `playlist content num`, `total mark num`.
- Tiempos: `creationTime :%04d.%02d.%02d %02d:%02d:%02d(%d)`,
  `->bckPropFileModTime`, `->orgPropFileModTime`, `->thumbPictFileModTime`, `aviFileModTime`,
  `m_firstContentCreationTime`.
- `seekPoint 0x%08x: packLength 0x%08x PH %d PF%d` → el índice también apunta a **puntos de lectura
  dentro de los packs** (formato de contenedor con "packs").

## 5. Comparación A6000 fw3.21 vs A7S fw3.20 (VERIFICADO)

- `libInfraFsys.so`, `libObj.so` y `libmpr.so` **existen en ambas** (375 524/373 900 B;
  17 436 172/16 184 848 B; 10 321 204/10 321 412 B) → el almacenamiento es el mismo en las dos
  cámaras.
- Las rutas DCIM son idénticas (`DCIM/100MSDCF/DSC%05d.ARW`).
- **`/setting/psd.bin` no existe en la A7S** → es **novedad fw3.21** (S75/S72).

## 6. Abierto (NO_VERIFICADO)

- El **formato MBR / tabla de particiones** y el modo de formateo: no hay cadenas en el firmware
  analizado; están en `libInfraFsys.so` (51 × "EXFAT") sin haber sido desensambladas aquí.
- El **número máximo de imágenes por carpeta** y la regla exacta de "reducir/divide".
- La codificación de los prefijos de nombre (`DSC`, `CLIP_`, `MVI`…) más allá del `DSC%05d.ARW`
  verificado.
- La estructura binaria del índice (`Index/`, `SceneInfo`, `DCF`) y su relación con `libmpr.so`.
- Los contenedores de vídeo en tarjeta (XAVCS/AVCHD/MP4) y su relación con `[VIDENCSTAT]` /
  `[ENCOUCSTAT]` (S83).

## 7. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s87_storage.py -q
```
