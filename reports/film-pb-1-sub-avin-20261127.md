# FILM-PB-1 — Formato de `AVF_INFO\AVIN0001.INP` (+ `.BNP`/`.INT`/`PRV00001.BIN`) y lector para PC

27-11-2026. Cámara **no accesible**: todo **estático** sobre `libmpr.so` de fw 3.21
(`.../nflasha15_unpacked_unpacked/lib/libmpr.so`, SHA-256 `9a74a3bb…5e4c30`).
**Direcciones = VA del ELF**; en `libmpr` REA/Ghidra = VA + 0x10000. No se abrió ningún binario en g22/REA.
Etiquetas: **V** = verificado en bytes/instrucciones · **D** = deducido (coherente, sin fichero real) ·
**NV** = no verificado.

## 1. Los cuatro ficheros

| Fichero | Nombre en el binario | Descriptor (V) |
|---|---|---|
| `AVIN0001.INP` (índice primario) | 0x7A912C | tabla `.data` **0x9D1270**: `name[16]`, `0x80`, `0x2710`, `0xFFFFFFFF`, `1`, `0x4B0`, `0x86`, **file-ID de 16 B** |
| `AVIN0001.BNP` (respaldo) | 0x7A9139 | misma tabla, entrada contigua |
| `AVIN0001.INT` (tabla interna) | 0x7A9160 | descriptor propio en 0x9D12C0 (`0xA0`, `0x78`, `0x300000`, tabla de punteros 0x9D1324+) |
| `PRV00001.BIN` (propiedades) | *no está en `libmpr`* | `FLUSH_FILE_ORIGINAL/PRV/THUMB/BACKUP` 0x7ADFC4; medido en g22 §5.51 |

Volcado de 0x9D1270 (V): `AVIN0001.INP\0\0\0\0`·`80 00 00 00`·`10 27 00 00`·`ff ff ff ff`·`01 00 00 00`·`b0 04 00 00`·`86 00 00 00`·`ff 06 75 81 fa 7b e2 90 45 27 84 b0 5e 61 10 ad`.
Ciclo de vida: `IsExistAVIndexDirectory` 0x7A65F4 → `CreateAVIndexFile` 0x7A7E7C / `ReadAVIndexFile` 0x7A7EA1 →
`FlushAVIndexFile`/`BackupAVIndexFile` 0x7A7821 → `BeginRepair <AVINDEX>` 0x9002BA →
`RunInconsistencyAvcMp4Register` 0x7ADB04 (V: cadenas con xref; las de `Flush/Read/Create` caen en código 0x140A..–0x1430..).

## 2. Cabecera del fichero

- **V**: el descriptor guarda un **file-ID de 16 B** (`0x817506FF 0x90E27BFA 0xB0842745 0xAD10615E`) y el API lo
  expone como `aviFileInfo.avindexFileId` + `aviFileInfo.avindexFileModificationTime` (cadenas 0x8F8283/0x8F82B5,
  consumidas en 0x6535B0); hay un `m_avIndexFileId12B[0..11]` (0x7A8E23). ⇒ **D**: la cabecera lleva ese ID (16 B,
  forma LE o BE) y un sello de modificación; es lo único que identifica el fichero como “de este formato”.
- **D**: `0x80 = 128 B` = tamaño de registro (`contentInfoSize`, 0x8F8200/0x8F821A del API) y `0x2710 = 10000`
  = nº máximo de contenidos ⇒ imagen de hasta 1 280 000 B. El valor `0xFFFFFFFF` es el centinela de “vacío”.
- **CRC: no aparece ninguno ligado a este fichero (NV negativo)**. Lo único de *checksum* es
  `CS_FlashDataAcsr::CheckSumCalc/DataCheckSumJudge` (0x7D80C1 / 0x7D9B32) sobre **flash interna**, y
  `aviFileInfo.avindexFileId` como huella lógica (0x955DD8 `AVIndexFileID`). Si el `.INP` real tuviera CRC al
  final, el lector lo verá como cola no cero tras el último registro (ver §5).
- **NV**: tamaño exacto de la cabecera (en el sintético se usan 0x100 B por comodidad) y el orden/versión.

## 3. Registro por clip (base = inicio del registro)

| Off | Tipo | Campo | Evidencia |
|---|---|---|---|
| +0x00 | `char[0x12]` | `cDirPath` (p.ej. `MP_ROOT/100ANV01`) | **V** 0x1DE066 y 0x1DE4CE: `cDirPath` en `r7+0xB8` / `r5+0x08`, `cFileName` en `r7+0xCA` / `r5+0x1A` ⇒ Δ=0x12 |
| +0x12 | `char[0x0E]` | `cFileName` (`MAH04198.MP4`) | **V** Δ siguiente campo = 0x0E (0xCA→0xD8 y 0x1A→0x28) |
| +0x20 | `u32` | `nFileSize` | **V** 0x1DE09C `ldr [r7,#0xD8]` |
| +0x24 | `u8` | **validez/inconsistencia** (candidato) | **D** hueco 0xDC–0xDF del volcado; el flag real es `ValidFlag` 0x7A7CE9 |
| +0x28 | `u32` | `nWidth` | **V** 0x1DE0B6 `[r7,#0xE0]` |
| +0x2C | `u32` | `nHeight` | **V** 0x1DE0D0 `[r7,#0xE4]` |
| +0x30 | `u32` | **`nDuration` en ms** | **V** 0x1DE0E4 `[r7,#0xE8]` + cadena 0x7AFB45 |
| +0x34 | `u32` | **`Duration90kHz`** (2.º candidato de duración) | **D** cadena 0x7A7D2C en el volcado de fecha/grupo |
| +0x38 | `u32` | `emVideoCodec` (4 = AVC) | **V** 0x1DE104 `[r7,#0xF0]`; 0x7AFB6D/0x7AFBD0 |
| +0x3C | `u32` | `emProfileIndication` | **V** 0x7AFC15 (mismo bloque) |

Alineación 4 B en todos los `u32`; sin `pack`. El volcado `[Avi][Mon] stAviMovieProf` (0x7AFA61) imprime estos
campos en orden y el de fecha/grupo (0x7A7C2E–0x7A7D40) imprime `AVITime`, `ContentCount`, `DurationTime`,
`AccessPath`, `FileSize`, `ValidFlag`, `Width/Height`, `ContCreTime`, `ContModTime`, `Duration90kHz` ⇒ **D**:
registro por clip = 0x80 B (0x00–0x3F usados) más un registro de atributos por fecha.
**NV**: que el fichero sea copia literal de esa estructura; es la hipótesis que valida el §6.

**Punto de reanudación**: *no* es un campo de este registro. Vive en el modelo de reproducción:
`pbTimeInContent` (cadena 0x85A919, dump en 0x4385F0) dentro de un bloque de 0x18 B
`{framePerSecX100 u32, pbTimeInTotal u32, pbTimeInContent u32, durationOfTotal u32, durationOfContent u32,
bInfoValid u8}` (V, 0x43858E–0x4385A4), con `Get/SetContentResumePoint` (0x8CAE60/0x8CB4B2 según camino-final).
**NV**: si ese valor se persiste en `.INP`, en `.INT` o en `PRIVATE/M4ROOT/CUEUP.XML` (0x947D2C).

## 4. Lector y prueba

`reports/evidence/film-pb-1-sub-avin-20261127/leer_avin.py` (172 líneas, solo stdlib): imprime tamaño, busca el
file-ID de 16 B (LE/BE/sufijo de 12 B), **escanea los nombres ASCII** `[A-Z0-9]{4}[0-9]{4}\.XXX` (no depende de la
rejilla) y para cada uno toma `base = offset_nombre − 0x12` y lista tamaño, WxH, **duración en ms** (+0x30),
**duración 90 kHz** (+0x34) y byte de validez (+0x24); `--raw NOMBRE` vuelca el registro de 0x80 B, `--header`
comprueba la rejilla.
Prueba: `sintetico_avin.py` construye `AVIN0001_sintetico.INP` (1408 B = cabecera 0x100 + 9×0x80) con los 7 clips
del 25-11 más un control `MAH04199.MP4` con 2000 ms; transcripción en `…/transcripcion-prueba.txt` (65 líneas).
Demuestra que el lector saca `9510=9.510s`/`855900=9.510s` de `MAH04198` y `2000=2.000s` del control **sin conocer la
cabecera**; **NO** demuestra que el `.INP` real use esta rejilla: eso lo decide el §5 sobre el fichero de la tarjeta.

## 5. Criterio de confirmación: ¿el índice dice 2 s de MAH04198?

Con la tarjeta en el PC, en `AVF_INFO\`:
1. `grep -aob "MAH04198.MP4" AVIN0001.INP` → offset `O`. `python3 leer_avin.py AVIN0001.INP --raw MAH04198`.
2. **Comprobación de la rejilla**: en `base = O−0x12` debe leerse `cDirPath` (`MP_ROOT\100ANV01` o `…/100ANV01`) y
   en `base+0x38` un `04 00 00 00` (AVC). Si sí, la estructura del §3 es la del fichero; si no, el registro es otro
   y se usa `--raw` para localizar los campos por la vía diferencial del punto 4.
3. **Duración en el registro**: u32 LE en `base+0x30` (ms) y `base+0x34` (90 kHz):
   - `26 25 00 00` (9510 ms) o `AF 0F 0D 00` (855855 @90 kHz, 9,5095 s) ⇒ el índice guarda la duración **correcta**:
     el `0:02` de la cámara **no** viene del catálogo persistido (H-B cae; queda H-A/H-C y el punto de reanudación).
   - `D0 07 00 00` (2000 ms) o `20 BF 02 00` (180000 @90 kHz) ⇒ **el índice dice 2 s**: H-B confirmada, el
     `0:02` es un valor persistido, no una lectura del `mvhd` (9,5095 s, ya verificado en el MP4).
4. **Contraste diferencial** (sin conocer la rejilla): con los 7 clips (5,005 / 9,5095 / 24,5245 / 31,5315 /
   34,5345 / 52,5525 / 72,5725 s) el `u32` que dividido por 90 000 da esas cifras es la duración 90 kHz; el que las
   da dividiendo por 1 000 es la de ms. El que solo cuadre para MAH04198 con 2 s es el campo averiado.
5. **Respaldo**: `cmp -l AVIN0001.INP AVIN0001.BNP | head` — si `.BNP` coincide, el primario no está corrupto
   (misma cifra) y el `0:02` no es artefacto de reparación; si difieren, el `.BNP` es la referencia buena.
6. Guardar `sha256sum AVIN0001.INP AVIN0001.BNP AVIN0001.INT` y los offsets `O` en el informe de la sesión física.

## 6. Límites

Sin tarjeta no hay ni un byte real: el tamaño y contenido de la cabecera, el CRC (o su ausencia), el offset exacto
de `Duration90kHz` y de la marca de validez, y la persistencia del punto de reanudación son **NV**. El descriptor
`0x80/0x2710` se interpreta como registro/máximo (D) y el lector **no** depende de ello: ancla en los nombres.
Nada tocado en `docs/`, `knowledge/`, `build/`, `scripts/`; solo este informe y `reports/evidence/film-pb-1-sub-avin-20261127/`.
