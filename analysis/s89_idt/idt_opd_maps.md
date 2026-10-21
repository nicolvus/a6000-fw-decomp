# S89 — El módulo `IDT`/`IDT_OPD`: mapas de parámetros del imager, FOPD e IDTSA

**Alcance:** línea de ingeniería inversa **general** de la cámara: el módulo **`IDT`** (298 trazas) y su
gemelo **`IDT_OPD`** (274) del `av-cam.bin`, que **calcula y entrega al imager los mapas de
parámetros** (sombreado, histograma, mapas de color, miniRAW) y gestiona el modo de **captura
partida** (`Split`/`IDTSA`) y el **kick FOPD**. No es la línea SilentShutter, ni la montura (S66), ni
el AF, ni ADJ_CMD, ni ZIT (S80), ni el visor, ni las caras (S71 —aunque se enlazan, ver §5), ni el
wireless (S72).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s89_idt.py`.

---

## 1. Hallazgo principal: `[IDT]` y `[IDT_OPD]` son **el mismo código con dos prefijos** (VERIFICADO)

Casi **cada** mensaje del módulo aparece **dos veces**, con prefijo `[IDT_OPD]` y con prefijo
`[IDT]`, y las dos copias están **contiguas** (separadas por la longitud del propio mensaje). Ejemplos:

| mensaje | dirección `[IDT_OPD]` | dirección `[IDT]` |
|---|---|---|
| `4cmap.adrs Err:%X` | `0x43cf2c2e` | `0x43cf2c4b` |
| `histmap.adrs Err:%X` | `0x43cf2c64` | `0x43cf2c83` |
| `summap.adrs Err:%X` | `0x43cf2c9e` | `0x43cf2cbc` |
| `shade_map.adrs Err:%X` | `0x43cf2bf0` | `0x43cf2c11` |
| `imgmap.adrs Err:%X` | `0x43cf1e45` | `0x43cf1e63` |
| `refmap.adrs Err:%X` | `0x43cf1eb5` | `0x43cf1ed3` |
| `backImgData.adrs Err:%X` | `0x43cf1e03` | `0x43cf1e26` |
| `miniRAW Addr : %08x` | `0x43cf40e0` | `0x43cf4100` |
| `4cmap:%X` | `0x43cf4545` | `0x43cf4559` |
| `msain0:%X` | `0x43cf463d` | `0x43cf4652` |
| `msain1:%X` | `0x43cf4663` | `0x43cf4678` |
| `msaout:%X` | `0x43cf4689` | `0x43cf469e` |
| `p_backImgData:%X` | `0x43cf46ff` | `0x43cf471b` |
| `refmap:%X` | `0x43cf47cb` | `0x43cf47e0` |

INFERENCIA: `OPD` es una **variante/instanciación** del mismo cálculo (posiblemente la ruta
"optical pixel data" o la variante para otro subsistema), y el firmware emite los dos mensajes
deliberadamente. NO_VERIFICADO: qué distingue a las dos variantes.

## 2. Los mapas que el IDT entrega al imager (VERIFICADO)

Direcciones de la pareja `[IDT_OPD]` / `[IDT]`:

| mapa / memoria | dirección OPD | dirección IDT | traza |
|---|---|---|---|
| `backImgData` | `0x43cf1e03` | `0x43cf1e26` | `backImgData.adrs Err:%X` |
| `imgmap` | `0x43cf1e45` | `0x43cf1e63` | `imgmap.adrs Err:%X` |
| `refmap` | `0x43cf1eb5` | `0x43cf1ed3` | `refmap.adrs Err:%X` |
| `shade_map` | `0x43cf2bf0` | `0x43cf2c11` | `shade_map.adrs Err:%X` |
| `4cmap` | `0x43cf2c2e` | `0x43cf2c4b` | `4cmap.adrs Err:%X` |
| `histmap` | `0x43cf2c64` | `0x43cf2c83` | `histmap.adrs Err:%X` |
| `summap` | `0x43cf2c9e` | `0x43cf2cbc` | `summap.adrs Err:%X` |
| `miniRAW` | `0x43cf40e0` | `0x43cf4100` | `miniRAW Addr : %08x` |
| `msain0` | `0x43cf463d` | `0x43cf4652` | `msain0:%X` |
| `msain1` | `0x43cf4663` | `0x43cf4678` | `msain1:%X` |
| `msaout` | `0x43cf4689` | `0x43cf469e` | `msaout:%X` |
| `p_backImgData` | `0x43cf46ff` | `0x43cf471b` | `p_backImgData:%X` |
| `refmap` (valor) | `0x43cf47cb` | `0x43cf47e0` | `refmap:%X` |

El volcado completo de direcciones del cálculo (VERIFICADO, en `[IDT]`):
`4cmap:%X` `0x43cf4559`, `hmap:%X`, `smap:%X`, `ccout:%X`, `ecout:%X`, `shade:%X`, `input:%X`,
`msain0/1` `0x43cf4652`/`0x43cf4678`, `msaout` `0x43cf469e`, `ieout:%X`, `p_img_map:%X`,
`p_backImgData:%X` `0x43cf471b`, `ie_in:%X`, `mapRC_in:%X`, `lc_out:%X`, `lc_in:%X`, `refmap:%X`
`0x43cf47e0`.

**`miniRAW` (VERIFICADO):** el mini-RAW es la imagen de baja resolución que el IDT entrega para
detectar caras/AF; el subsistema de calibración de lente lo usa directamente:
`[CAMERA_MAIN_LC]: [LC] Movie DM AF cannot get miniRAW Stored memhandle` (`0x43c9c8ba`) →
**enlace directo entre el IDT y el AF híbrido/LC** (S75/S71).

## 3. `FOPD` — el "kick" de lectura del imager (VERIFICADO, 42 trazas)

- Errores por canal: `FOPD_AIF_R0_ERROR:%x` (`0x43c91547`), `FOPD_AIF_W0_ERROR` (`0x43c91567`),
  `FOPD_AIF_W1_ERROR` (`0x43c91587`), `FOPD_AIF_W2_ERROR` (`0x43c915a7`) → **cuatro canales**
  (R0, W0, W1, W2).
- Desde el gestor de captura: `[IMAGING_CAP]: StartRdraw_Prelight: KickFOPD error` (`0x43cadd2d`),
  `StartRdraw_Read: KickFOPD error` (`0x43cadd60`).
- Consistencia de tasa: `[IDT]: FOPD rate is not correct! %d`, `FOPD_mode error`,
  `FOPD_rate Convert NG %d`, `Illegal cap FOPD Call when 1pass %d`,
  `IDT Async FOPD Sem Get error` / `Sem Rel error` (semáforos de sincronización).
- Sincronización con el gestor de recursos: `[CAMERA_MAIN_SYNC]: [IDT]r0:%02X r1:%02X r2:%02X
  w0:%02X [FOPD]r0:%02X w0:%02X w1:%02X w2:%02X [PRC]r0…` (`0x43ca2939`) → el **SyncResMgr**
  (S81) reparte los recursos de lectura entre IDT, FOPD y PRC.

## 4. `Split`/`IDTSA` — la captura partida (VERIFICADO, 52 trazas con "Split")

- `GetIDTSA Unknown aspect:%d` (`0x43cf3306` OPD / `0x43cf332c` IDT), `calc SplitIDTSA error %d %d %d
  %d %d %d.` (`0x43cf34d4`/`0x43cf3508`), `IDTSA Invalid Ch select. %d %d` (`0x43cf3538`/`0x43cf3562`),
  `Illegal FRM mode for IDTSA %d` (`0x43cf5147`).
- `[IDT]: Split Coordinate: Async invalid.`, `calc SplitIDTSA error`, `IDT Async FOPD Sem Get error`,
  `Illegal Split cap FOPD Call %d`, `Fatal Not Copiled for Split Cap`, `Illegal Split EE FOPD Call %d`,
  `Fatal Not Copiled for Split`, `Split Movie Cannot use AIF! %d`, `Split Movie Cannot use Insel! %d`,
  `Split Movie Cannot use AIF!!! %d`, `Split Movie Cannot use Insel!!! %d`, `PBL SET_FUNC_ERROR R0 only`,
  `PBL START_ERROR R0 only`.
- En el gestor de núcleo: `[CAMCORE]: SplitEEController: Memory Close Error!(VATR)` (`0x43c90982`).

INFERENCIA: la **captura partida** ("Split") es el modo de **dos曝光/2 frames** que usa el AF híbrido
por desplazamiento de sensor (DM AF) y el ZPD (S75): de ahí los "Can't use AIF" en modo Split y el
`zpd_mario_afa` de S71.

## 5. Los umbrales de detección que el IDT calcula (VERIFICADO) — enlace con las caras

| parámetro | traza | dirección OPD / IDT |
|---|---|---|
| `kido_th[%d].up/.dn` | `[IDT]: kido_th[%d].up Err:%d` | `0x43cf2962` / `0x43cf2983` |
| `ratio_wak[%d].up/.dn/.rgt/.lft` | `[IDT]: ratio_wak[%d].up Err:%d` | `0x43cf29de`–`0x43cf2aa6` |
| `sel_hist` / `sel_sum` / `sel_wak` / `sel_waku[%d]` | `[IDT]: sel_hist Err:%d` | `0x43cf2b54`/`0x43cf2b6f` |
| `lc_waku[%d].x_end/.y_end` | `[IDT]: lc_waku[%d].x_end Err:%d` | (misma familia) |
| `idealWidth`/`idealHeight`, `mask.x_end/.y_end` | `[IDT]: idealWidth Err:%d` | |

Estas son las **regiones de detección** (`wak`/`waku` = 枠, "marco/región") que el IDT entrega al
subsistema de caras: el módulo `[TRK]: [STK]` de S71 usa `box af_island_*`, `p_saliency`,
`p_similarity` y `maps p_hsv_xyz` — mismo tipo de estructura (umbrales por región).

## 6. `VATR` y `NSX_OPD` (VERIFICADO)

- `VATR` (36 trazas): `[IDT_OPD]: VATR Error det:%x gle:%x` (`0x43cf3ec8`),
  `[NSX_OPD]: VATR released when moving` (`0x43c91609`), `VATR Mem OK %x` / `Mem NG %d` /
  `Mem Release OK` / `Release NG`, `Can't Get VATR Mem`, `VATR Mem Get: FW param is NULL!`,
  y en el gestor de recursos `[CAMERA_MAIN_SYNC]: SyncResMgr::Free: MODE_EE(01),
  IDT_STOP_ERR(VATR):0x%02x` (`0x43c9b5ab`) → **VATR es un detector con dos resultados (`det`, `gle`)**.
- `NSX_OPD` (28 trazas): `FRM set SGC unknown %d` (`0x43c915c7`), `FRM start unknown %d`
  (`0x43c915e9`), `IDT AIF illegal address. <%x> --> <%x>`, `mask error. total_num: %d`,
  `deno=0!`, `Unknown FRM mode in calc %d`, `FRM out_size calc is wrong`.
  INFERENCIA: `NSX` es la variante de sensor nueva ("new sensor eXperimental"?) para la que el
  firmware tiene un camino de cálculo propio.

## 7. Abierto (NO_VERIFICADO)

- Qué distingue exactamente las variantes `[IDT]` y `[IDT_OPD]` (mismo código, dos prefijos).
- Significado de `kido_th`, `ratio_wak`, `waku`, `sel_hist`, `sel_sum`, `sel_wak`, `gle`.
- Formato y tamaño de cada mapa entregado al imager.
- Qué es exactamente `FOPD` (y su relación con AIF: ¿"all in frame"?) y con `PRL`/`PBL`.
- Cómo se calculan las coordenadas del modo `Split` y su vínculo con el DM AF y el ZPD.
- Significado de `NSX` y de `SGC`.
- Si el bloque de A7S fw3.20 es igual (no comprobado).

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s89_idt.py -q
```
