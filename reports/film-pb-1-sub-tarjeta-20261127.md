# FILM-PB-1 — lado TARJETA: qué indexa los MP4 de `MP_ROOT` y cómo repararlo sin cámara

27-11-2026. Cámara **no accesible** (sin ping/USB/adb): análisis **estático** de `libmpr.so` de fw 3.21
(`firmware/extracted/fw321/firmware.tar_unpacked/0700_part_image/dev/nflasha15_unpacked_unpacked/lib/libmpr.so`,
SHA-256 `9a74a3bb42836559888509b6113d281b85ae53b03eb9cdf4a965eafb545e4c30`).
**Direcciones = VA del ELF (base 0); REA/Ghidra = ELF + 0x10000.** No se toca `M_SinglePbBase_Utils` ni la
guarda `vtable+0x58`. Evidencia cruda: [evidence/film-pb-1-sub-tarjeta-20261127/mapa-cadenas-y-tablas.txt](evidence/film-pb-1-sub-tarjeta-20261127/mapa-cadenas-y-tablas.txt).

## 1. Mapa de ficheros (VERIFICADO por bytes y xref)

| Fichero | Cadena (VA) | Código (VA) | Contenido |
|---|---|---|---|
| `AVF_INFO\` (raíz de `ms:`) | `AVF_INFO` 0x7A637F, `ms:` 0x8127EB | `IsExistAVIndexDirectory` 0x7A65F4 → 0x13C0E8; `MprFileIf::FindFirst` (PLT 0x11EA84) en **0x13E496**, dentro de la función 0x13E474 | directorio del **índice AV** = catálogo persistente de películas |
| `AVF_INFO\AVIN0001.INP` / `.BNP` / `.INT` | 0x7A912C / 0x7A9139 / 0x7A9160 | grupo `CS_AviAcsr`/`CS_FlashAcsr`; descriptor en `.data` **0x9D1270** `{name[16]; 0x80; 0x2710=10000; 0xFFFFFFFF; 1; 0x4B0; 0x86; id 16 B 817506FF 90E27BFA B0842745 AD10615E}` | índice **primario**, **respaldo** y tabla interna |
| `AVF_INFO\OTDISCBN.IND` / `MODELCFG.IND` / `PRV00001.BIN` | 0x7A91C0 / 0x7A91CD / *no está en libmpr* | xrefs 0x1447E4, 0x1449D8 / 0x144894, 0x144AB8; PRV medido en [g22 §5.51](../docs/gui/g22-avcam-puente.md):561 | disc-burn, config. de modelo y fichero «PRV» de propiedades (`FLUSH_FILE_ORIGINAL/PRV/THUMB/BACKUP` 0x7ADFC4) |
| `\PRIVATE\M4ROOT\{CLIP,SUB,THMBNL,GENERAL}` | 0x947C8A, 0x947C9A, 0x947CAF, 0x947CC3, 0x947CDA | **solo XAVC**: `xavcIfo_DbDirMngr`, constructor de rutas **0x779EAC** | estructura XAVC (`CLIP\C0001.MP4`, 0x94501F); `CLIP` vacío porque no hay XAVC |
| `\PRIVATE\M4ROOT\MEDIAPRO.XML` / `.BAK` | 0x947CF2 / 0x947D0F (y 0x94A26E / 0x94A276) | tablas 0x779FBC, 0x779FE4, 0x7825D0/0x7825E0 | **base de datos XAVC** (`xavcIfo_MediaProfile`); no es el índice de MP4 |
| `\PRIVATE\M4ROOT\CUEUP.XML`, `DISCMETA.XML`, `NRTMETA.xml`, `STATUS.BIN` | 0x947D2C, 0x947D46, 0x94A28B, 0x94E518 | ídem; `xavcIfo_StatusFileAcsr` (0x94E58C) | reanudación, metadatos de disco/no realtime y estado XAVC (`rsmInfo.bIsValid`, `Device Node ID`, `BasicUMID`) |
| `MP_ROOT\100ANV01\MAH0xxxx.MP4` | plantilla 0x7ACAEC; prefijos 0x7ABDB4 `MAH0`, `MAQ0`,`MAF0`,`MAS0`,`MAV0`,`M4H0`,`M4V0`; `*.MP4` 0x7ABDAE | módulo `mp4Ifo_*` | **los clips**. `mp4Ifo` no tiene **ninguna** cadena de ruta ni de fichero de índice: no posee catálogo propio en la tarjeta (VERIFICADO negativo) |

`xavcIfo_DbDirMngr` (0x779EAC) rellena campos de **0x1D B** en `+0x0C` (raíz), `+0x1C` CLIP, `+0x39` SUB, `+0x56`
THMBNL, `+0x73` GENERAL, `+0x90` MEDIAPRO.XML, `+0xAD` MEDIAPRO.BAK, `+0xCA` CUEUP.XML, `+0xE7` DISCMETA.XML (volcado
con nombres 0x947DAC–0x947EC3); secuenciador `xavcIfo_DbSequencer` 0x948066–0x9481E0 (`mp_mediaProfileFileAcsr`, `mb_isLoadedMediaProfile`, `mp_discMeta`).

## 2. ¿Escaneo de directorio o índice persistente? — **las dos cosas, en este orden**

1. **Índice persistente en el medio.** `FlashLoad [AVCHD/M2PS/DCF/**MP4_AVC**/MP4_MPEG4/WAV/XAVC]` (0x7AF307)
   frente a `DiskLoad [AVCHD/M2PS/DCF/XAVC]` (0x7AF2E3 = grabar a disco). «Flash» = tarjeta: `CS_HddAviSetDef`,
   `CS_MsAviSetDef`, `CS_FlashAviSetDef`, `CS_SsdAviSetDef`, `CS_UsbStorageAviSetDef` (0x7A5F47…0x7A5F88, tabla
   0x12C284–0x12C294). `avi_man_NewAviFileManager` (**0x14B660**) crea cinco gestores —raíz `+8`, de aplicación
   `+0xC`, propiedades original `+0x10`, respaldo `+0x14`, miniaturas `+0x18`— y concatena `AVF_INFO` (0x14B8D6, 0x14B9D0).
   Cargas por tipo: `GetMp4AvcLoadInfoCache` 0x7CCA87, `GetStillLoadInfoCache` 0x7CCBE5.
2. **Si falta o no cuadra: escanea y registra leyendo ficheros.** `AVIndex Accesser is not exist.` 0x7A7367,
   `Error CreateAVIndex`/`CreateAVIndex Success` 0x7A7BD4/0x7A7BE8, `CreateAVIndexFile`/`ReadAVIndexFile` 0x7A7E7C/0x7A7EA1,
   `BeginRepair <AVINDEX/AVCHD_NEW/AVCHD/M2PS/STILL/XAVC_RECONST/XAVC/WAV>` 0x9002BA,
   `[AVI][MON] BeginRealContentInfoLoad`/`RunRealContentInfoLoad` 0x7AD50B/0x7AD55E, `RunInconsistencyAvcMp4Register` 0x7ADB04.
3. **La duración sale del MP4, no del XML M4ROOT.** `mp4FileLib_Play::GetMovieDuration` 0x90FE84 y
   `mp4Ifo_General::GetMovieDuration` 0x914DE7 parsean el fichero (`GetMovieTimeInfo`, `GetSampleInfo`); el
   valor se persiste después en el índice (`nDuration` en ms y `Duration90kHz` en el volcado por fecha).

**Corrección a [g22:436](../docs/gui/g22-avcam-puente.md)**: la *cadena* `AVF_INFO` (0x7A637F) sí es solo una
etiqueta de volcado (9 xrefs, 0x12C6A4…0x14BCDC), pero el *directorio* `ms:/AVF_INFO` **sí** se sondea:
`Fsys_FindFirst("ms:/AVF_INFO")` → 0x2109 y `ms:/AVF_INFO/PRV00001.BIN` están en la traza medida
([g22:561](../docs/gui/g22-avcam-puente.md)); el import `MprFileIf::FindFirst` se llama en 0x13E496. Ambas cosas son ciertas.

## 3. Campos persistidos (duración, frames, validez, tipo)

| Campo | Dónde | Evidencia (VA) |
|---|---|---|
| duración **ms** | registro de contenido del índice AV | `[Avi][Mon]   nDuration           = [%d]` 0x7AFB45; `[AVI][MON] Duration(msec) = [%d]` 0x7AEAAC |
| duración **90 kHz** | atributos por fecha/grupo | `  Duration90kHz : ` 0x7A7D2C, junto a `ContentCount`/`ValidFlag`/`Width/Height`/`ContCreTime`/`ContModTime` (0x7A7C2E–0x7A7D1A) |
| **frames** | `frameCount` (atributo `<LtcChange>`) en `NRTMETA.xml` | 0x947958; en el índice AV **no localizado** → NO_VERIFICADO |
| **validez** | `ValidFlag` del contenido; huella del índice | 0x7A7CE9; `aviFileInfo.avindexFileId` 0x8F8283, `…ModificationTime` 0x8F82B5; `m_avIndexFileId12B[0..11]` 0x7A8E23–0x7A8F20 (`AVIndexFileID` 0x955DD8) |
| **tipo** | códec + perfil | `emVideoCodec` 0x7AFB6D, `[VIDEO_CODEC_AVC]` 0x7AFBD0, `emProfileIndication` 0x7AFC15, `AVI_CONF_PROF_DEF_SET_MP4_AVC` 0x7A8B34 |
| XAVC (referencia) | `MediaProfile`/`NRTMeta` XML | `<MediaProfile` 0x947364, `<Contents` 0x94737E, `xmlns …mediaprofile` 0x945E2B, `GetDuration` 0x944A58/0x94825E, `<Duration value=` 0x94791B/0x947925, `NRT_SETDURATION` 0x94C58F |

## 4. Receta de reparación, de menor a mayor riesgo

**R0 (0 riesgo, antes de nada).** Copia íntegra de `AVF_INFO\` y de `MP_ROOT\*\*.MP4` con tamaños y mtime.

**R1 (mínimo; no borra nada).** Menú → «Herramienta tarjeta memoria» → **«Recuperar BD imág.»** (id 0xE3D0 de
`string_spanish.uxc`, desplazamiento 0xB490; ayuda id 0xE43A en 0xC048: «Recupera el archivo de base de datos de
imágenes para películas y habilita la grabación y la reproducción.»). **INFERIDO**, no medido: dispara la API
por tipos (`BeginRepair <…AVINDEX…>` 0x9002BA → `RunInconsistencyAvcMp4Register`); reescribe `AVF_INFO\` y lista las 7 películas.
*Si falla:* cauciones 0xE40F «No se puede utilizar tarj. memoria.» (0xBA50), 0xE414 «Error en la tarjeta de memoria.» (0xBB14).

**R2 (bajo).** Renombrar el directorio: `AVF_INFO` → `AVF_INFO.old`. `IsExistAVIndexDirectory` falla →
`CreateAVIndexFile` reconstruye escaneando `MP_ROOT\*\*.MP4`. *Esperar:* `AVIN0001.INP/.BNP/.INT` nuevos y
duraciones leídas de los MP4. *Riesgo:* se pierden puntos de reanudación, contadores de fecha y la numeración
de EntryID (la presentación puede renumerarse por fecha).

**R3 (medio).** Renombrar solo el primario `AVF_INFO\AVIN0001.INP` → `.bak`, dejando `.BNP`/`.INT`: fuerza la
restauración desde el respaldo (`AVINDEX_FILE_RESTORE_*` 0x7C9D48, `AVINDEX_FILE_ORG_RESCUE_*` 0x7CAC41) y, si
tampoco sirve, la reconstrucción de R2.

**R4 (solo si hubo XAVC; nulo para MP_ROOT).** Renombrar `PRIVATE\M4ROOT\{MEDIAPRO.XML,MEDIAPRO.BAK,STATUS.BIN,
CUEUP.XML,DISCMETA.XML}`: reconstruye la base XAVC (`ExistMediaProfileFileByDirectory` 0x944B61, `CreateMediaProfileFile` 0x944B0B).

**R5 (no recomendado).** Formatear en la cámara: borra `DCIM` y `MP_ROOT`.

**Verificación sin flashear**, tras cada paso y con la tarjeta en el PC: (a) `AVF_INFO\AVIN0001.INP` existe, tamaño
≠ 0 y mtime nuevo; (b) `grep -a MAH04198 AVF_INFO/AVIN0001.INP` encuentra el nombre en ASCII (el registro guarda
`cFileName`); (c) el índice de la cámara muestra **0:09** para MAH04198 en vez de 0:02.
**Regla de decisión:** si tras R1+R2 sigue el 0:02 y el mismo «No se puede visualizar.», el catálogo queda
descartado (H2 muere) y solo queda H1 (arranque en frío/WBI), que discrimina E1/E3 del
[informe de auditoría](film-pb-1-auditoria-cfw-20261127.md).

## 5. Leer la duración registrada de MAH04198 en el PC

**(a) Referencia — del propio MP4 (VERIFICADO el 25-11).** `moov`→`mvhd` v0: `size(4)` `'mvhd'(4)` `version(1)`
`flags(3)` `creation(4)` `modification(4)` `timescale(4)` `duration(4)` (v1: `creation(8)` `modification(8)`
`timescale(4)` `duration(8)`); `s = duration/timescale`; por pista, `moov/trak/mdia/mdhd` igual. MAH04198:
**9,5095 s / 285 fotogramas** ([traspaso](film-pb-1-traspaso-20261125.md):36); es lo que debería mostrar la cámara.

**(b) Del índice (`AVF_INFO\AVIN0001.INP`).** El registro guarda `cFileName` y la duración:
1. `grep -aob "MAH04198.MP4" AVF_INFO/AVIN0001.INP` → desplazamiento del nombre en su registro.
2. Volcar ±256 B y buscar la duración en las dos unidades documentadas: **90 kHz** — 9,5095 s → 855 855 =
   `AF 0F 0D 00`, y 2 s → 180 000 = `20 BF 02 00`; **ms** — 9510 = `26 25 00 00`, y 2 s → 2000 = `D0 07 00 00`.
3. Contraste diferencial con los otros seis clips (5,005 / 24,5245 / 31,5315 / 34,5345 / 52,5525 / 72,5725 s):
   el campo que escale ×90 000 con ellos es la duración.

**NO_VERIFICADO:** offsets exactos del registro dentro de `AVIN0001.INP` (cabecera, tabla de fechas, entrada de
contenido); no se han invertido en esta sesión, de ahí que (b) sea diferencial. También **NO_VERIFICADO** que el
nombre vaya en ASCII plano en el `.INP`: no hay copia de una tarjeta de la A6000 en el repo ([g22:563](../docs/gui/g22-avcam-puente.md)).

## 6. Límites

Sin tarjeta ni cámara no se ha abierto un `AVF_INFO\` real ni medido una sola E/S. La correspondencia `ms:` →
tarjeta SD es **INFERIDA** (una ranura, `CS_FlashAviSetDef`); la sonda `ms:/AVF_INFO` sí está medida en G22.
La duración de MAH04198 está verificada en el *fichero* (9,5095 s), **NO** que el índice guarde 2 s. No se ha tocado `docs/`, `knowledge/`, `build/` ni el código.
