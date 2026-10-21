# S78 — El espacio de parámetros `apc_*` del motor de imagen YC (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: el **conjunto de parámetros de
procesado de imagen** que calcula el motor `Camera::YC` (el que entrega los parámetros al motor
SA/DFE) y los registra con el espacio de nombres jerárquico `apc_<módulo>.<parámetro>`. No es la
línea SilentShutter, ni la montura (S66), ni el AF, ni ADJ_CMD (`analysis/s73_adj/`), ni ZPD
(`analysis/s75_zpd/`), ni el grafo de etapas (`analysis/s76_stages/`).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s78_apc.py`.

---

## 1. Qué es (VERIFICADO)

El motor de imagen de la cámara (`Camera::YC`, logs con prefijo `[CAMERA_MAIN_YC]: YAP:`) calcula sus
parámetros de imagen y los registra con nombres de la forma `apc_<módulo>.<parámetro>`. Hay
**50 parámetros distintos** repartidos en **7 módulos**, todos entre `0x43cc44cb` y `0x43cc4fe4`:

| módulo | n | parámetros (dirección de la cadena) |
|---|---|---|
| `apc_lpf` | 2 | `vaplpf` (`0x43cc44cb`), `haplpf` (`0x43cc44f6`) |
| `apc_mask` | 6 | `vmaskgain` (`0x43cc4521`), `vmaskoffset` (`0x43cc4557`), `hmaskgain` (`0x43cc458d`), `hmaskoffset` (`0x43cc45c3`), `hmasksel_l` (`0x43cc45f9`), `hmasksel_h` (`0x43cc462f`) |
| `apc_yld` | 9 | `yld_vlpf` (`0x43cc4665`), `yld_hlpf` (`0x43cc469d`), `yld_base_gain` (`0x43cc46d5`), `yld_slope_l` (`0x43cc470d`), `yld_slope_h` (`0x43cc4745`), `yld_sofst_l` (`0x43cc477d`), `yld_ofst_l` (`0x43cc47b5`), `yld_ofst_h` (`0x43cc47ed`), `yld_sofst_h` (`0x43cc4825`) |
| `apc_acm` | 4 | `acmpm_th_en` (`0x43cc485d`), `acmpm_th` (`0x43cc488d`), `acmpm` (`0x43cc48ba`), `acmpp` (`0x43cc48e8`) |
| `apc_zoukou` | 18 | `size_adj` (`0x43cc4916`), `dist_ofst_start` (`0x43cc4952`), `dist_ofst_end` (`0x43cc498e`), `pgainy` (`0x43cc49ca`), `cgain_vh/vm/vs` (`0x43cc4a06`/`0x43cc4a42`/`0x43cc4a7e`), `cgain_hh/hm/hl/hs` (`0x43cc4aba`/`0x43cc4af6`/`0x43cc4b32`/`0x43cc4b6e`), `egain_slope_vh/vm/vs` (`0x43cc4baa`/`0x43cc4be6`/`0x43cc4c22`), `egain_slope_hh/hm/hl/hs` (`0x43cc4c5e`/`0x43cc4c9a`/`0x43cc4cd6`/`0x43cc4d12`) |
| `apc_coring` | 8 | `vcoring_p0/p1/p2/aplk` (`0x43cc4dcc`–`0x43cc4e74`), `hcoring_p0/p1/p2/aplk` (`0x43cc4eac`–`0x43cc4f54`) |
| `apc_gain` | 3 | `apgain` (`0x43cc4f8c`), `vapgain` (`0x43cc4fb8`), `hapgain` (`0x43cc4fe4`) |

**El nombre del parámetro va embebido en la propia cadena de formato del log** (VERIFICADO), p. ej.
`'[CAMERA_MAIN_YC]: YAP:\tapc_lpf.vaplpf\t=%x'` (`0x43cc44b4`),
`'[CAMERA_MAIN_YC]: YAP:\t    apc_mask.vmaskgain   \t=%x'` (`0x43cc450a`),
`'[CAMERA_MAIN_YC]: YAP:\t    apc_yld.yld_vlpf       \t=%x'` (`0x43cc464e`),
`'[CAMERA_MAIN_YC]: YAP:\tapc_acm.acmpm_th_en\t=%x'` (`0x43cc4846`),
`'[CAMERA_MAIN_YC]: YAP:\t    apc_zoukou.size_adj        \t=%x'` (`0x43cc48ff`),
`'[CAMERA_MAIN_YC]: YAP:\t    apc_coring.vcoring_p0   \t=%x'` (`0x43cc4db5`),
`'[CAMERA_MAIN_YC]: YAP:\tapc_gain.apgain\t\t=%x'` (`0x43cc4f75`): no hay tabla de nombres
aparte, el nombre *es* la cadena.

Convenciones de nomenclatura observadas (VERIFICADO en los nombres):
- Prefijo `v`/`h` = **vertical/horizontal** (`vaplpf`/`haplpf`, `vcoring_*`/`hcoring_*`,
  `vapgain`/`hapgain`, `cgain_v*`/`cgain_h*`).
- Sufijo `_l`/`_h` dentro de `yld_*` y `mask` =区域内 **low/high** (p. ej. `yld_slope_l/h`,
  `hmasksel_l/h`).
- `*_vh/vm/vs` y `*_hh/hm/hl/hs` = combinaciones **vertical/horizontal × high/middle/low** (3 bandas
  por eje: `vh`=very-high, `vm`=very-mid, `vs`=very-short; `hh/hm/hl/hs` simétricos).
- `acm` = matriz de color; `coring` = corrección de color en zonas oscuras; `lpf` = filtro paso bajo;
  `mask` = máscara de zonas; `gain` = ganancia; `yld` = "yield"?; `zoukou` = 左右
  (japonés, "izquierda-derecha") → compensación **deBalance horizontal** (INFERENCIA por el nombre;
  no hay evidencia textual en el firmware).

## 2. Los jobs que calculan cada módulo (VERIFICADO por los prefijos de log)

El log `[CAMERA_MAIN_YC]: YAP:` que precede a cada familia de parámetros está referenciado por una
función distinta; esa función es la que **calcula y registra** ese módulo:

| Función | Módulo registrado | Evidencia |
|---|---|---|
| `0x438b0f80` | `apc_lpf` | `'[CAMERA_MAIN_YC]: YAP:'` en `0x43cc44b4`/`0x43cc44df` |
| `0x438b1058` | `apc_mask` | `0x43cc450a`, `0x43cc4540`, `0x43cc4576`, `0x43cc45ac`, `0x43cc45e2`, `0x43cc4618` |
| `0x438b11f0` | `apc_yld` | `0x43cc464e`–`0x43cc4825` (9 refs) |
| `0x438b177c` | `apc_acm` | `0x43cc4846`, `0x43cc4876`, `0x43cc48a3`, `0x43cc48d1` |
| `0x438b2070` | `apc_zoukou` | `0x43cc48ff`–`0x43cc4d12` (18 refs) |
| `0x438b2ac4` | `apc_coring` | `0x43cc4db5`–`0x43cc4f54` (8 refs) |
| `0x438b3570` | `apc_gain` | `0x43cc4f75`, `0x43cc4fa1`, `0x43cc4fcd` |
| `0x438b3ea8` | job global de foto fija | `job_apc_main_stl main_digitalZoomRatioDenom=%x` (`0x43cc4ff9`) |
| `0x438b5810` | job global de vídeo | `job_apc_main_mov digitalZoomRatioDenom=%x` (`0x43cc50fb`) |

**Firmas de función embebidas (VERIFICADO):**
- `void Camera::YC::job_apc_gain_stl(short unsigned int, short unsigned int, short unsigned int,
  unsigned char, unsigned ch…` → `0x43cc40df` (ref `0x438b3570`).
- `void Camera::YC::job_apc_coring_stl(short unsigned int, …` → `0x43cc513d` (ref `0x438b2ac4`).

## 3. Contexto de la captura (VERIFICADO)

- El job de coring además registra: `[CAMERA_MAIN_YC]: %s: bdro_sequence error = 0x%x`
  (`0x43cc4d37`), `YAP:aus_X_ISO =%x` (`0x43cc4d68`) y `YAP:picture_effect =%x` (`0x43cc4d8c`):
  el cálculo de coring depende de la **secuencia BDRO**, del **ISO** y del **efecto de imagen**.
- El job global de foto fija (`0x438b3ea8`) registra además `ISO:`, `IRIS:`, `OPT_ZOOM:`, `RC_ZOOM:`
  y `MOV_HS  =%x` (`0x43cc50dc`, ref `0x438b4080`).
- `YAP::job_YC_CalcParam (SYNC): AgcContStdBase = 0x%x` (`0x43cc4428`, ref `0x438b079a`) y
  `AgcContBlend` (`0x43cc446e`): el cálculo de parámetros de ganancia es **sincronizado** entre
 拍照 y preview (AG = auto gain / "agc control").

## 4. Abierto (NO_VERIFICADO)

- Qué significan exactamente `acmpm` vs `acmpp` (¿matriz de color de la foto fija vs la de preview?).
- Dónde se materializan estos 50 parámetros (¿struct en RAM, `T_AdjRam`? ¿paso al SA por
  `sa_func_*`?) — el proyecto ya conoce `Camera::YC::sjob_GetDetectArea(Camera::YC::T_AdjRam*, …)`
  (`0x43cbd92c` → `0x438ea230`): `T_AdjRam` es el bloque de parámetros de ajuste.
- La tabla de valores por modo de captura (los modos 69→14 de S66) para cada parámetro `apc_*`.
- Si la A7S (fw3.20) tiene el mismo conjunto (no comprobado).

## 5. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s78_apc.py -q
```
