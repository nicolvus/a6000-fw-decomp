# FILM-PB-1 · sub — ¿puede rechazarse MAH04198.MP4 por su propia estructura?

Fecha: 27-11-2026. Cámara no accesible: todo estático. Espacios **VA del ELF** en `libmpr.so` (REA = VA + `0x10000`) y
**VA directas** en `libObj.so`. Fichero `…/MAH04198.MP4`, 14 545 696 B, SHA-256 `148c204c…7dba6`. Instrumentos propios
(`reports/evidence/film-pb-1-sub-20261127/clip-*.py`); ffprobe solo contrasta.

**VEREDICTO: ACEPTABLE — el contenedor no ofrece a la guarda de «contenido no soportado» ningún defecto que
la haga disparar.** Reproduce valor por valor lo que escribe el grabador de la cámara para un clip `MSNV`
(minor, uuid propietarios, perfil/nivel, fps, resolución anamórfica, nombres de `hdlr`). No procede
reescribirlo (§4 explica qué haría un remux y por qué empeora). Límites en §5.

## 1. Inventario (48 cajas; la cobertura suma el tamaño del fichero; evidencia en `clip-boxdump.txt`, `clip-verify.txt`)

| off | tam | caja | datos |
|---|---:|---|---|
| 0 | 28 | `ftyp` | major `MSNV`, minor **22675568 = 0x015A0070**, compat `MSNV`,`mp42`,`isom` |
| 28 | 148 | `uuid` **PROF** | usertype `50524F46-21D24FCE-BB88695C-FAC9C740`; payload 8 B (00000000, 00000003) + `FPRF`(20) + `APRF`(44) + `VPRF`(52) |
| 176 | 14 540 866 | `mdat` | payload `[184, 14 541 042)`; última muestra acaba en 14 540 874 (+168 B de relleno) |
| 14 541 042 | 4 654 | `moov` | **al final**, tras `mdat` (como lo cierra el grabador) |
| 14 541 050 | 108 | `mvhd` v0 | timescale 90 000, duration 855 855 (9,5095 s), next_track 3 |
| 14 541 158 | 1 917 | `trak` vídeo | `tkhd` 14 541 166 (id 1, dur 855 855, display 1920×1080) · `edts/elst` 14 541 266 (855 855, media_time **1001**, rate 1,0) · `mdhd` 14 541 302 (30 000, 285 285) · `hdlr` `vide` «Video Media Handler» |
| ↳ 14 541 450 | 1 573 | `stbl` | `stsd`→`avc1` 14 541 474 (**1440×1080**, hres **0x00480000**, vres **0x00600000**, «\nAVC Coding», depth 24)→`avcC` 14 541 560 (79 B: Main **77**, compat 0x00, level **0x28=40**, lengthSize 4, 1 SPS de 55 B, 1 PPS) · `stts` 285×1001 · `ctts` v0 285×1001 · `stsc` 1×15 · `stsz` 285 (Σ 14 388 220 B) · `stco` 19 · `stss` 10 (1,31,…,271) |
| 14 543 023 | 52 | `uuid` **USMT** | usertype `55534D54-…-C740`; hijo `MTDT`(28) |
| 14 543 075 | 2 575 | `trak` audio | `tkhd` (dur 854 400) · `elst` (854 400, media_time 0) · `mdhd` (48 000, 455 680) · `hdlr` `soun` «Sound Media Handler» |
| ↳ 14 543 363 | 2 235 | `stbl` | `stsd`→`mp4a` (2 can., 16 bits, 48 000)→`esds` 14 543 423 (OTI 0x40, avg/max 128 000, ASC `11 90` = AAC‑LC 48 kHz est., SL 0x02) · `stts` 445×1024 · `stsc` 17 · `stsz` 445 (Σ 152 454 B) · `stco` 19 |
| 14 545 598 | 52 | `uuid` **USMT** | igual que @14 543 023, dentro del trak audio |
| 14 545 650 | 46 | `uuid` **USMT** | hijo `MTDT`(22) al final de `moov` |

Ausentes: `udta`, `meta`, `free`/`skip`, `iods`, `mvex`/`moof`, `wide`. **Ninguna caja no estándar**: las únicas
propietarias son las 4 `uuid` (1 PROF + 3 USMT/MTDT), las 4 con la cola canónica Sony `21D24FCE BB88695C FAC9C740`.
`moov` **después** de `mdat`, igual que en el escritor (`mp4FileLib_Rec::CloseRecFile`, cadenas ` Write Meta Box.
boxOffset=0x` @`0x912B21`). Integridad: 285 + 445 muestras dentro de `mdat`, tablas coherentes, sin truncamiento.

## 2. Qué exige el parser (todo en `libmpr.so`; `libObj.so` no tiene parser)

`libObj.so` **no contiene parser de cajas**: sus apariciones de fourcc son subcadenas ajenas (`'ftyp'`
en `…iftype value…` @`0xCBA50A`; `'avcC'` en `xavcCanceled` @`0xCbfa29`; `'elst'` en
`pthread_setcancelstate` @`0x2E40F`; `'uuid:'` es un formateador @`0xC9BE1D`). Todo el demux está en
`libmpr`: `mp4FileLib_{Rec,Play,Common,If,LocalCache}` + `mp4Ifo_*` (cadenas `0x90F700–0x9175xx`) sobre un
núcleo tipo libavformat (`ff4ComIf/ff4RecIf/ff4PlayIf`, cadenas `0x915B48–0x916C8C`).

1. **Brand, guarda dura.** `Ff4PlayIf::CheckCompatibilityForMSNV` = **`0x6DE980`** (`---- Ff4PlayIf::CheckCompatibilityForMSNV() ---`
   @`0x91669F`): exige major `0x4D534E56` («MSNV», pool `0x6DEA28`), **low16 del minor ∈ {0x58,0x59,0x70}**
   (`0x6DE9A6–0x6DE9B2`) y que la lista de brands contenga `MSNV`(`0x6DE9BC`), `mp42`(`0x6DE9E4`) e
   `isom`(`0x6DEA02`); cualquier ausencia devuelve error (`ff4PlayIf.cpp:0x565/0x573/0x57b`). Lo que escribe el
   grabador (`IF/mp4FileLib_Rec.cpp`, `0x68E270–0x68E330`): MSNV ⇒ minor **`0x015A0070`** (pool `0x68E3A4`); XAVC ⇒
   `0x01001FFF` (`0x68E3A0`); brands = major, `mp42` (`0x68E3AC`) y `isom` (`0x68E3B4`) si MSNV / `iso2` si XAVC.
2. **`uuid` de Sony, obligatorio para tener perfil.** Lector **`0x6B8908`**: lee los 16 B del usertype, los
   normaliza a 4 palabras BE y compara las palabras 1–3 con `0x21D24FCE`/`0xBB88695C`/`0xFAC9C740` (pool
   `0x6B8AAC–0x6B8AB4`, `cmp` en `0x6B8A2E/0x6B8A34/0x6B8A3C`). **No compara el fourcc inicial**, solo la cola ⇒ PROF
   y USMT/MTDT entran por la misma puerta; deja el flag 0/1 en `0x6B8A8A`. Luego `Ff4PlayIf::GetMovieProfileInfo` =
   **`0x6DEAEC`** (@`0x9166FF`): `GetFtypInfo`(`0x69AC58`) → guardas de marca → **`0x69B210`**, que busca hijos
   `FPRF`(`0x46505246`, `0x69B2C4`), `VPRF`(`0x56505246`, `0x69B2C8`), `APRF`(`0x41505246`, `0x69B2CC`),
   `BPRF`(`0x42505246`, `0x69B2D0`) y `PPRF`(`0x50505246`, `0x69B2D4`), recorriendo hermanos por `[atom+0x38]`
   (`0x6BA182`); los dos últimos son opcionales.
3. **Valores admitidos** (cadenas del volcado `mp4FileLib`): `AVC_PROFILE_LEVEL_MAIN_21…HIGH_52` (`0x90F871–0x90FA73`);
   fps `FPS_100/119_88/200/239_76/UNKNOWN` (`0x90FB67`) y en grabación `23.976 / 29.97 / 100 / 119.88 / 200 / 239.76 Hz`
   (`0x912D54–0x912DB0`); audio `AAC_48KHz` (`0x912CF9`); hres «`0x00480000=HRE_VGA,HRE_HD,HRE_SQZ_HD`» (`0x912065`);
   vres «`0x00480000=VRE_VGA,VRE_HD, 0x00600000=VRE_SQZ_HD`» (`0x9120CD`); volcado `avcC` «`0x01`», «`77=AVC_MAIN_PROFILE`»,
   «`0x40=COMPATI_VGA,0x00=COMPATI_720P_1080I`», «`0x1E=LEVEL3.0,0x28=LEVEL4.0,0x2A=LEVEL4.2`» (`0x91210A–0x9121E1`).
4. **Huella del escritor**: `hdlr` «Video Media Handler» `0x915B1B`, «Sound Media Handler» `0x915B07`, «Timed
   Metadata Media Handler» `0x915A87`, «AVC Coding» `0x915A7C`.
5. **La guarda en sí**: manejador `0x437BC0`; la llamada del camino «contenido no soportado» es `0x437C2C` →
   **`0x447F26`**, que delega en el método virtual `[vtable+0x58]` del objeto de medio obtenido por `0x66D0C8`; si
   devuelve 0: log ` Detect UnSupported Content ` (`0x85A7D8`) y `r3=0x1A` (`0x437C3C`). **El parser MP4 no decide ahí.**

## 3. Contraste fichero ↔ exigencias

| Requisito | Exigido (VA) | En el fichero | ¿Cumple? |
|---|---|---|---|
| major+minor+brands | `0x4D534E56`, low16∈{0x58,0x59,0x70}, MSNV+mp42+isom (`0x6DE9A0–0x6DEA02`) | `MSNV` /**0x0070**/`MSNV,mp42,isom` (off 0) | **sí**, idéntico a `0x68E3A4` |
| `uuid` cola Sony | `21D24FCE…C740` (`0x6B8AAC`) | PROF @28 + 3 USMT @14 543 023/14 545 598/14 545 650 | **sí** (4 de 4) |
| hijos `FPRF/VPRF/APRF` | `0x69B2C4–0x69B2CC` | FPRF(20)+APRF(44)+VPRF(52), cabecera 8 B con cuenta 3 | **sí** |
| perfil/nivel H.264 | MAIN_4 ∈ enum (`0x90F8D8`) | `avc1`+`avcC` 77/0x28 = Main@4.0, SPS 55 B | **sí** |
| fps | 29.97 | `stts` 1001 / `mdhd` 30 000 | **sí** |
| resolución + anamórfico | hres 0x00480000, vres 0x00600000 (SQZ_HD) | hres 72.0 / vres 96.0, `tkhd` 1920×1080, SAR 4:3 | **sí** |
| audio | `AAC_48KHz` | `esds` OTI 0x40, ASC `11 90` (LC 48 kHz estéreo) | **sí** |
| `hdlr` | nombres de `0x915B07/0x915B1B` | «Video/Sound Media Handler» literales | **sí** |
| posición de `moov` | tras `mdat` | 14 541 042 > 176 | **sí** |
| coherencia de datos | tablas dentro de `mdat` | 285+445 muestras dentro, sin truncar | **sí** |

Sin discrepancia explotable. Los bitrates reales coinciden con los declarados (vídeo 12 104 kbps ≈ `VPRF` 0x2EE0 =
12 000; audio 128,3 kbps = `esds` 128 000) y `ctts` constante 1001 con `elst` media_time 1001 es coherente con un
flujo IPPP de `num_ref_frames=1`. Ningún campo da ~2 s (confirma el informe del 25-11): el «0:02» no sale de ahí.

## 4. Receta de reescritura

**No aplica: no hay discrepancia.** Lo que *no* debe hacerse y el único camino neutro:

```bash
cp --preserve=all MAH04198.MP4 MAH04198_COPIA.MP4 && sha256sum MAH04198*.MP4   # NEUTRO: cajas intactas
ffmpeg -i MAH04198.MP4 -c copy -brand msnv out.mp4            # minor 0x015A0070 y uuid PROF no reproducibles
ffmpeg -i MAH04198.MP4 -c copy -movflags +faststart out.mp4   # movería moov al principio (no es lo que hace la cámara)
```

ffmpeg no escribe `uuid PROF` ni el minor `0x015A0070`: el resultado se parecería a un MP4 ajeno. Una copia
«normalizada» exigiría reinyectar las 4 `uuid` y el `ftyp` originales byte a byte y verificar el SHA-256; sin
cámara no se puede validar que siga aceptándose.

## 5. Límites (NO_VERIFICADO)
- **NO_VERIFICADO** qué implementa `[vtable+0x58]` (decisión final de «contenido soportado»): el objeto lo entrega
  `0x66D0C8` y su implementación no se ha localizado; podría estar fuera de `libmpr`. «Estructura correcta» es
  condición necesaria, no suficiente.
- **NO_VERIFICADO** si la tabla de perfiles del modelo (`AVI_CONF_PROF_DEF_SET_MP4_AVC`, contadores en
  `0x7A8B34`) incluye 1440×1080/29,97/12M: no se ha mapeado la tabla de descriptores.
- **NO_VERIFICADO** si el grabador escribe siempre `meta` (NRT XML): en `CloseRecFile` la llamada a `WriteMetaBox`
  (`0x691036`) está bajo un flag (`[this+0x2230]`, `0x691002–0x691008`); el fichero no tiene `meta` y no se ha
  hallado requisito de lectura que lo exija.
- No se ha ejecutado firmware ni abierto la cámara; nada depende de observación en caliente.
