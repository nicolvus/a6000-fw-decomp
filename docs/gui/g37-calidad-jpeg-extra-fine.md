# G37 — Calidad JPEG Extra Fine: ya existe de fábrica en la A6000 (15-11-2026)

**Resultado: DESCARTADO por no aplicable.** La A6000 (fw 3.21) ya trae la calidad «Extra fine» en el firmware de serie: textos, cadena de calidad y tablas de tamaño del codificador. No hay nada que añadir; el objetivo del wiki partía de una suposición («origen α6300») que el firmware desmiente. No se construye CFW.

## 1. Evidencia (todo sobre el fw 3.21 original, `firmware/extracted/fw321/.../nflasha15_unpacked_unpacked`)

| # | Hecho | Dónde | Estado |
|---|---|---|---|
| 1 | Texto `0xe001 'Extra fine'` en `string_english.uxc`, junto a `0xe123 RAW`, `0xe124 RAW & JPEG`, `0xe125 Fine`, `0xe126/7 Standard`, y la ayuda `0xe8ff 'Records JPEG images of maximum quality. Records beautiful images with little compression.'` | `share/app/string_english.uxc` (volcado con `scripts/gui/uxc_strings.py dump`) | VERIFICADO |
| 2 | Misma cadena `0xe001`/`0xe8ff` en la α6300 fw 2.01; la vista `viewStillImageQuality.uxc` es **byte a byte idéntica** en ambas (sha256 `11be5edf…`, 1004 B): la α6300 no aporta una pantalla distinta | `firmware/extracted/a6300-fw201/...` | VERIFICADO |
| 3 | `WrapperImageQuality::convertProcessValueIdToValue` (`wrapperImageQuality.so+0x16ae`) acepta ids de proceso 0–4 (`cmp r1,#4; bhi`) y los traduce por `tbb` a `WRAPPER_IMAGE_QUALITY`: cinco valores = RAW, RAW+JPEG, Extra fine, Fine, Standard | `lib/wrapperImageQuality.so` (Capstone Thumb) | VERIFICADO el límite 0–4; el reparto exacto id→etiqueta no se tabuló |
| 4 | `libObj.so` contiene `DefStruct::JPG_QUALITY_EXFINE`, ` EXFINE [%x]` y `[InfStillEncoder]encodeQuality` (el codificador recibe la calidad) | `lib/libObj.so` (strings) | VERIFICADO |
| 5 | `libmprctrl.so` (sha256 `514e1411…`, idéntica a la usada en S37): `[Quality]:0(STD)/1(FINE)/2(EXFINE)` en los registros de `GetStillRec`/`GetStillDataInfo`, y 20 tamaños × 3 calidades × {TGT, MAX} = 120 claves `BKID_IMAGING_DATSZ_APSC_DRJPG_{L,M,S}_{3_2,4_3,16_9,17_9,1_1}_{STD,FINE,EXFINE}_{TGT,MAX}` (tamaño objetivo y máximo de fichero del JPEG) | `analysis/rea-independent/input/libmprctrl.so` | VERIFICADO (nombres y enumeración; los valores numéricos de los BKID no se extrajeron) |
| 6 | Referencia: `UtilStillSize::GetStillTargetFileSize(int, StillSize, StillAspect, JpgQuality, CropType, bool)` suma los tres tamaños de `MprCtrl::GetStillDataInfo` (`analysis/ghidra/s37-library.json`) | libmprctrl | VERIFICADO |

Por tanto el valor de calidad (0 STD, 1 FINE, 2 EXFINE) ya llega al núcleo y a la tabla de tamaño objetivo/máximo del codificador; no hay factor de cuantización que tocar y la opción del menú ya existe (la A6000 real la muestra como «Extra fine»).

## 2. Qué NO se hizo / límites

- No se renderizó el menú «Quality» en el arnés: el arnés lo modifica otra sesión y la conclusión no depende de él; la cadena completa se ha comprobado estáticamente (1–5).
- No se extrajeron los valores numéricos de los BKID `EXFINE_TGT/MAX` (tamaños objetivo) ni se midió un JPEG real (no hay JPEG de la A6000 en el repo, solo `.ARW`). Si en el futuro se quisiera un Extra fine *más* alto que el de Sony, sería otro objetivo (subir los `TGT/MAX`), no este.
- `README.md` conserva la fila «Calidad JPEG Extra Fine | En curso» (el README no se toca por sesión); la verdad vigente es `wiki/16-Objetivos.md` (movida a Descartadas).
