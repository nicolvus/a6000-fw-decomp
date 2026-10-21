# S66 (subtarea E) — Sombreado dependiente de la lente (SHD / "LensMountSHD")

**Alcance:** línea de ingeniería inversa **general** de la cámara: el subsistema `SHD` de
`av-cam.bin` que corrige el **sombreado** (iluminación no uniforme, viñeteado) **dependiente de
la lente**. Sin relación con SilentShutter.

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `analysis/s66/shd_modes.py`, `analysis/s66/out/shd_modes_a6000.txt`,
`tests/test_s66_lens_mount.py` (tests SHD incluidos).

---

## 1. Por qué importa

El sombreado de una lente depende del modelo: la A6000 guarda **11 valores** y **32 ganancias**
por lente (`ss_LensMountShdValue[0..10]`, `us_LensMountShdGain[0..31]`) más el mínimo de ganancia
(`us_ShdGainMin`) y el factor de efecto (`us_LensMountShdEffect`). Es el punto donde el firmware
**personaliza el procesado de imagen según la lente montada**.

## 2. Inventario del subsistema SHD (VERIFICADO por strings y referencias)

| Función (nombre interno) | Dirección (A6000) | Logs asociados |
|---|---|---|
| `SHD::GetShdMode` | `0x438ef40e` | `SHD::GetShdMode: unknown drive_mode = 0x%x` (`0x43ccca56`) |
| `SHD::GetLensShdGain` | `0x438eee3c` | `SHD::GetLensShdGain: uc_Color = 0x%x` (`0x43ccca1f`) |
| `SHD::job_LensMountSHD_GainCalc` | `0x438f0804` | `...: ShdMode = 0x%x` (`0x43ccce0c`) |
| `SHD::CalcLensShdGainToy` | `0x438f10e2` | `...: ShdMode = 0x%x` (`0x43ccce4d`) |
| `SHD::IsTrackBonoboOn` | `0x438f1f5e` | `SHD:IsTrackBonoboOn: LensShdMode = 0x%x` (`0x43cccf6b`) |
| `SHD::CalcLensShdGainAdj` / `SHD::CalcLensShdGain` | `0x438f3278` | `...: ShdMode/ShdSync/lens_shd_mode` (`0x43ccd31f`, `0x43ccd359`, `0x43ccd393`) |

Otros logs del mismo bloque: `SHD::JudgeShdOn` (combina `LensShdOn` y `PzShdOn` — sombreado de
lente y de zoom), `SHD::GetWviSize`, `SHD::GetShdTblData: id = 0x%x`, `SHD::IsModulateOn`
(`uc_modulate_bit`), `SHD::CalcRateBase`, `SHD::CalcCenterBase` (centros R/G1/G2/B y `hshift`),
`SHD::GetShiftPixel`, `SHD::CalcSensShdCoefAdj`.

Helper de traza común: `0x438ee938` (usado por todas las funciones SHD con el prefijo
`[CAMERA_MAIN_YC]:`).

## 3. Modo de sombreado en función del modo de captura (VERIFICADO)

`SHD::GetShdMode` (`0x438ef40e`) recibe el `drive_mode` y usa una **tabla de saltos `tbb`**:

```
cmp  r3, #0x44          ; drive_mode 0..0x44 (69 modos)
bhi  -> "unknown drive_mode"
tbb  [pc, r3]           ; tabla de 69 bytes en 0x438ef418
```

Cada entrada salta a un bloque que devuelve un `ShdMode` inmediato. Extracción completa en
`analysis/s66/out/shd_modes_a6000.txt`:

- 69 modos de captura → **14 valores de ShdMode** distintos: `0x00,0x01,0x02,0x03,0x04,0x05,0x06,
  0x07,0x08,0x09,0x0A,0x0B,0x0C,0x0D,0x0F` (falta `0x0E`).
- Reparto: `0x02` → 20 modos, `0x00` → 10, `0x01` → 8, `0x0A` → 7, `0x08` → 4, `0x03` → 4, resto 1–3.
- El ShdMode 0x0F solo se usa en `drive_mode` 16.

INFERENCIA: el ShdMode selecciona el **perfil de corrección de sombreado** en función del modo de
captura (no solo de la lente): es decir, el firmware cruza *modo de captura* × *modelo de lente*.

## 4. Datos por lente (VERIFICADO en nombres; valores NO_VERIFICADO en su origen)

Nombres de campo presentes en el blob (A6000 `0x43cbe9cb`–`0x43cbee11`):

- `ss_LensMountShdValue[0]` … `[10]` (11 valores)
- `us_LensMountShdGain[0]` … `[31]` (32 ganancias, `u16`)
- `us_ShdGainMin`, `us_LensMountShdEffect`, `uc_SyncLensShdOn`

Hipótesis de enlace (INFERENCIA fuerte, pendiente de la subtarea B): los valores por lente viven en
el fichero `/lens/VX91xx_lensfile.bin`. En `VX9101_lensfile.bin` hay una tirada contigua de u16
(≈36 valores en el rango 0x026C–0x03DC a partir del offset 0x38) compatible con las 32 ganancias
`us_LensMountShdGain[]`; el recuento y el orden exactos los confirma la subtarea B.

## 5. A6000 (fw3.21) vs A7S (fw3.20): bloque SHD **idéntico** (VERIFICADO)

Comparación de los logs SHD de ambos blobs:

- A6000: **217** cadenas `SHD::…`, **todas** con el prefijo `[CAMERA_MAIN_YC]: `.
- A7S: **217** cadenas `SHD::…`, **ninguna** con prefijo.
- Los **conjuntos son idénticos** byte a byte tras quitar el prefijo (`assertEqual` en
  `tests/test_s66_lens_mount.py::LensShading::test_shd_logs_identical_between_models`).

| Aspecto | A6000 | A7S |
|---|---|---|
| Nº de logs SHD | 217 | 217 |
| Formato del log | `[CAMERA_MAIN_YC]: SHD::…` | `SHD::…` (sin prefijo) |
| Variantes `SHD::Std::` / `SHD::Regulus::` | sí | sí |
| Fases SYNC / PRELIGHT / CAP (`job_YC_SetParam`) | sí | sí |
| `uc_lshd_gain_idx_num`, `uc_iris_idx_num`, `uc_fc_idx_num`, `uc_shut_idx_num`, `uc_zm_idx_num` | sí | sí |
| `SHD::GetShdTblData: id = 0x%x`, `SHD::GetWviSize`, `SHD::CalcSensShdCoefAdj` | sí | sí |
| `us_LensMountShdGain[0..31]` | sí | sí |

**Conclusión (VERIFICADO):** el subsistema de corrección de sombreado es **el mismo** en la A6000
(fw3.21) y en la A7S (fw3.20); la única diferencia es el esquema de traza (el prefijo
`[CAMERA_MAIN_YC]:` se añadió en la fw3.21). Es decir, la línea de firmware de la A6000 **no
tocó** la corrección de sombreado respecto de la A7S.

## 6. Abierto (NO_VERIFICADO)

1. Origen físico de `ss_LensMountShdValue[]` / `us_LensMountShdGain[]` (fichero de lente vs. tabla
   interna) — depende de la subtarea B.
2. Semántica numérica de las ganancias (¿miles? ¿log2? ¿enteros con escala?) y de `us_ShdGainMin`.
3. Relación entre `ShdMode`, `lens_shd_mode` y `sens_shd_mode` (sensor IMX210) y el coeficiente
   final aplicado al YC.
4. Qué es exactamente "Bonobo" en `SHD::IsTrackBonoboOn` (el "BonoboDSP" de la subtarea C).

## 7. Reproducción

```bash
.venv/bin/python analysis/s66/shd_modes.py A6000        # tabla drive_mode -> ShdMode
.venv/bin/python analysis/s66/func_strings.py A6000 0x438ef40e 0x438ef4c0 --calls
```
