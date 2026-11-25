# Informe de análisis — MAH04198.MP4

Análisis de solo lectura. El archivo MP4 no fue modificado.
Parser propio en Python (sin librerías externas); ffprobe usado solo para contrastar.

## 1. SHA-256

```
148c204cdea843ebafee0ffc9123b1614a493c083a931e5e499489ce27b7dba6  MAH04198.MP4
```

Coincide con el valor esperado. Tamaño: 14 545 696 bytes.

## 2. Árbol completo de atoms (44 boxes)

Offsets absolutos en el archivo. `moov` está al final (offset 14 541 042), tras `mdat`.

| Offset | Tamaño | Box | Campos relevantes |
|---|---|---|---|
| 0 | 28 | `ftyp` | major_brand=`MSNV`, minor_version=22675568, compatible=`MSNV`,`mp42`,`isom` |
| 28 | 148 | `uuid` (Sony PROF: `50524f46...c740`) | contiene sub-boxes `FPRF`, `APRF` (perfil `mp4a`, 48000 Hz), `VPRF` (perfil `avc1`) |
| 176 | 14 540 866 | `mdat` | datos multimedia (14 540 858 bytes de payload) |
| 14 541 042 | 4 654 | `moov` | |
| 14 541 050 | 108 | `mvhd` v0 | timescale=**90000**, duration=**855855** → **9,5095 s**, rate=1.0, next_track_id=3, creación/modificación=3471397321 (2014-01-01T05:02:01Z) |
| 14 541 158 | 1 917 | `trak` (vídeo) | |
| 14 541 166 | 92 | `tkhd` v0 flags=7 | track_id=1, duration=**855855** (ts movie 90000 → 9,5095 s), width=1920, height=1080 (display) |
| 14 541 258 | 36 | `edts` | |
| 14 541 266 | 28 | `elst` v0 | 1 entrada: segment_duration=**855855**, media_time=**1001**, rate=1.0 |
| 14 541 294 | 1 729 | `mdia` | |
| 14 541 302 | 32 | `mdhd` v0 | timescale=**30000**, duration=**285285** → **9,5095 s**, lang=0x55c4 (`und`) |
| 14 541 334 | 52 | `hdlr` | handler=`vide`, "Video Media Handler" |
| 14 541 386 | 1 637 | `minf` | |
| 14 541 394 | 20 | `vmhd` | |
| 14 541 414 | 36 | `dinf`/`dref` | 1 referencia `url ` (self-contained) |
| 14 541 450 | 1 573 | `stbl` | |
| 14 541 458 | 181 | `stsd` | 1 entry: `avc1` 1440x1080 (depth 0 en muestra; 24 en avcC), con `avcC` (SPS 25 bytes, PPS) |
| 14 541 639 | 24 | `stts` | 1 entrada: count=**285**, delta=**1001** → total 285 285 ticks = 9,5095 s |
| 14 541 663 | 24 | `ctts` v0 | 1 entrada: count=285, offset=**+1001** (B-frames: PTS = DTS + 1 cuadro) |
| 14 541 687 | 28 | `stsc` | 19 grupos de chunks |
| 14 541 715 | 1 160 | `stsz` | sample_size=0, **285 muestras**, tamaños variables (357 745, 33 660, 62 666, …) |
| 14 541 875→14 542 875 | 92 | `stco` | **19 chunks**, offsets 184 … 13 765 773 |
| 14 542 967 | 56 | `stss` | **10 keyframes**: samples [1, 31, 61, 91, 121, 151, 181, 211, 241, 271] |
| 14 543 023 | 52 | `uuid` (Sony USMT: `55534d54...c740`) | sub-box `MTDT` (28 bytes): flags 0x010012, valores 10, 0x55c40000, 1, 0 — sin campo de ~2 s |
| 14 543 075 | 2 575 | `trak` (audio) | |
| 14 543 083 | 92 | `tkhd` v0 flags=7 | track_id=2, duration=**854400** (ts movie 90000 → 9,4933 s) |
| 14 543 175 | 36 | `edts` | |
| 14 543 183 | 28 | `elst` v0 | 1 entrada: segment_duration=**854400**, media_time=**0**, rate=1.0 |
| 14 543 211 | 2 387 | `mdia` | |
| 14 543 219 | 32 | `mdhd` v0 | timescale=**48000**, duration=**455680** → **9,4933 s**, lang=`und` |
| 14 543 251 | 52 | `hdlr` | handler=`soun`, "Sound Media Handler" |
| 14 543 303 | 2 295 | `minf` | `smhd`, `dinf`/`dref` |
| 14 543 363 | 2 235 | `stbl` | |
| 14 543 371 | 91 | `stsd` | 1 entry: `mp4a` AAC-LC, 2 canales, 16 bits, **48000 Hz**, con `esds` |
| 14 543 462 | 24 | `stts` | 1 entrada: count=**445**, delta=**1024** → total 455 680 ticks = 9,4933 s |
| 14 543 486 | 220 | `stsc` | 17 grupos de chunks |
| 14 543 706 | 1 800 | `stsz` | **445 muestras** (369, 332, 312, 335, … bytes) |
| 14 545 506 | 92 | `stco` | 19 chunks, offsets 943 357 … 14 533 022 |
| 14 545 598 | 52 | `uuid` (Sony USMT) | `MTDT` idéntico al de la pista de vídeo |
| 14 545 650 | 46 | `uuid` (Sony USMT, en moov) | `MTDT` (22 bytes): flags 0x01000c, valores 11, 0xd5c40000, 0xfed4 — sin campo de ~2 s |

ffprobe concuerda: 2 streams (H.264 Main@L4.0 1440x1080 30000/1001, 285 frames, duración 9,5095 s; AAC-LC 48000 Hz estéreo, 445 frames, 9,4933 s), format duration=9,5095 s, major_brand=MSNV.

## 3. Todos los valores temporales medidos

| Campo | Valor crudo | Timescale | Segundos |
|---|---|---|---|
| mvhd duration | 855 855 | 90 000 | 9,5095 |
| tkhd vídeo duration | 855 855 | 90 000 (movie) | 9,5095 |
| tkhd audio duration | 854 400 | 90 000 (movie) | 9,4933 |
| mdhd vídeo duration | 285 285 | 30 000 | 9,5095 |
| mdhd audio duration | 455 680 | 48 000 | 9,4933 |
| elst vídeo segment_duration | 855 855 | 90 000 | 9,5095 |
| elst vídeo media_time | 1 001 | 30 000 (media) | 0,0334 (1 cuadro de offset inicial) |
| elst audio segment_duration | 854 400 | 90 000 | 9,4933 |
| elst audio media_time | 0 | — | 0 |
| stts vídeo (suma) | 285 × 1 001 = 285 285 | 30 000 | 9,5095 |
| stts audio (suma) | 445 × 1 024 = 455 680 | 48 000 | 9,4933 |
| ctts vídeo offset | +1 001 | 30 000 | 0,0334 |
| Número de muestras vídeo | 285 (stts/stsz) | 30 000/1001 fps | 9,5095 |
| Número de muestras audio | 445 (stts/stsz) | 48 000 | 9,4933 |
| Primer PTS vídeo | 0 ticks | 30 000 | 0,0000 s |
| Último PTS vídeo | 284 × 1 001 = 284 284 ticks | 30 000 | 9,4761 s |
| Duración total vídeo (último PTS + delta) | 285 285 ticks | 30 000 | 9,5095 s |
| Primer PTS audio | 0 | 48 000 | 0,0000 s |
| Último PTS audio | 444 × 1 024 = 454 656 | 48 000 | 9,4720 s |
| Duración audio vs vídeo | 9,4933 s vs 9,5095 s | — | el audio es 0,0162 s más corto |

**Keyframes (stss) en segundos** (PTS = (sample−1) × 1001 / 30000):

| # | sample | PTS (ticks) | segundos | truncado |
|---|---|---|---|---|
| 1 | 1 | 0 | 0,0000 | 0:00 |
| 2 | 31 | 30 030 | 1,0010 | 0:01 |
| 3 | **61** | **60 060** | **2,0020** | **0:02** |
| 4 | 91 | 90 090 | 3,0030 | 0:03 |
| 5 | 121 | 120 120 | 4,0040 | 0:04 |
| 6 | 151 | 150 150 | 5,0050 | 0:05 |
| 7 | 181 | 180 180 | 6,0060 | 0:06 |
| 8 | 211 | 210 210 | 7,0070 | 0:07 |
| 9 | 241 | 240 240 | 8,0080 | 0:08 |
| 10 | 271 | 270 270 | 9,0090 | 0:09 |

**Tamaño de GOP**: 30 cuadros = 30 × 1001/30000 = **1,001 s** (cada keyframe, salvo el último tramo).

## 4. ¿Qué valores dan ~2 s (rango 1,5–2,5 s)?

### Hechos medidos

1. **PTS del 3.er keyframe de vídeo (stss[2] = muestra 61) = 60 060 ticks = 2,0020 s.**
   Al truncar a segundos enteros: `int(2,0020) = 2` → se muestra como **"0:02"**.
   Es exactamente el final de los **2 primeros GOPs completos** (2 × 30 cuadros × 1001/30000 = 2,002 s).
   Es el único valor temporal del archivo (calculado a partir de stts+stss) que cae en el rango 1,5–2,5 s y trunca a 2.

2. **Muestra AAC nº 95**: PTS = 94 × 1024 = 96 256 ticks @ 48 000 = **2,0053 s** → trunca a 2.
   (El audio no tiene stss; todas las muestras AAC son "sync" por definición, así que este valor es menos candidato que el del keyframe de vídeo.)

3. **Valor literal 60 000 (= 2,0000 s a timescale 30 000)** existe en el archivo en el offset 14 541 599 (`00 00 EA 60`), pero está **dentro de los bytes del SPS** del `avcC` (SPS ocupa 14 541 576–14 541 600): es un falso positivo del bitstream H.264, no un campo de tiempo.

4. **Ninguna duración almacenada da ~2 s bajo ninguna combinación de timescale.**
   Comprobado cruzando todos los campos de duración con todos los timescales presentes (90 000, 30 000, 48 000):

   | Campo | /90 000 | /30 000 | /48 000 |
   |---|---|---|---|
   | mvhd/tkhd_v 855 855 | 9,5095 | 28,5285 | 17,8303 |
   | mdhd_v/stts_v 285 285 | 3,1698 | 9,5095 | 5,9434 |
   | tkhd_a 854 400 | 9,4933 | 28,4800 | 17,8000 |
   | mdhd_a/stts_a 455 680 | 5,0631 | 15,1893 | 9,4933 |
   | elst_v media_time 1 001 | 0,0111 | 0,0334 | 0,0209 |
   | ctts offset 1 001 | 0,0111 | 0,0334 | 0,0209 |

   Ninguna cae en 1,5–2,5 s. Tampoco los boxes propietarios Sony (`uuid` PROF/USMT/MTDT) contienen ningún valor de 2 s: sus campos son perfiles de codec (48000 Hz, avc1) y contadores (10, 11, 1, 0, 0x55c4, 0xfed4).

### Hipótesis (no hechos)

- La lectura más directa: la cámara muestra **"0:02" porque trunca a segundos enteros el valor 2,002 s**, que es el PTS del **3.er keyframe (muestra 61)** — equivalente al cierre del **2º GOP**. Un contador que arranca en el keyframe anterior (1,001 s → "0:01") y avanza un GOP daría "0:02"; o un seek que aterrice en el keyframe 61 mostraría directamente 2,002 s truncado a "0:02".
- Alternativa menor: la muestra de audio nº 95 (2,0053 s) también trunca a 2, pero al no haber stss en audio es menos probable que sea la fuente.
- No se ha encontrado ningún campo de duración almacenado que valga 2 s en ninguna escala, así que la explicación no pasa por un `duration` mal interpretado, sino por un **PTS de keyframe (2,002 s) truncado a entero**.

## 5. Nota metodológica

No si hicieron suposiciones sobre el firmware de la cámara. Todo lo anterior son medidas del archivo (parser propio) contrastadas con ffprobe; la única conjetura es que "0:02" proviene de truncar 2,002 s, el único valor temporal medido en el rango 1,5–2,5 s.
