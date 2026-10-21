# S88 — GOLFSHOT (disparo de golf por análisis de sonido) y MOTIONSHOT

**Alcance:** línea de ingeniería inversa **general** de la cámara: el modo de disparo **GOLFSHOT**
(disparo sincronizado con el sonido del golpe de golf) y el **MOTIONSHOT**, en la A6000 fw3.21, con su
diferencial frente a la A7S fw3.20. No es la línea SilentShutter, ni la montura (S66), ni el AF, ni
el API del SA como eje (S84 —solo como contexto—), ni el visor (S85/S86), ni las caras (S71), ni el
wireless (S72), ni el almacenamiento (S87).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

> **Nota de revisión (21-10-2026).** El borrador del subagente citaba nombres **etiquetados por
> Ghidra** (`s__GOLFSHOT__…__43cb18bd`) en lugar de las cadenas reales, y afirmaba que el módulo
> `[GOLFSHOT]` era "independiente". La revisión lo corrige: en la A6000 la etiqueta `[GOLFSHOT]`
> aparece **anidada** dentro de los prefijos `[IMAGING_RSRC]:`, `[IMAGING_CAP]:`,
> `[CAMERA_MAIN_SYNC]:` y `[ADF]SAN …` (en la A7S sí es prefijo principal).

Artefactos: `tests/test_s88_shotmodes.py`.

---

## 1. Dónde vive el código del golf shot (VERIFICADO)

72 cadenas contienen `GOLFSHOT` en la A6000, **anidadas** en tres módulos:

| módulo contenedor | ejemplo | dirección |
|---|---|---|
| `[IMAGING_RSRC]:` | `[IMAGING_RSRC]: [GOLFSHOT]SA_LPF Exec[%02d] Err: sa_err[0x%x] intfct[0x%x] mbox1[%x]` | `0x43ca492f` |
| | `… SA_BGEST Exec Err: …` | `0x43ca4984` |
| | `… SA_SSP Exec[%03d] Err: …` | `0x43ca49d5` |
| | `… correctSndDetResult(WARNING): Corrected Value is Out of SoundDetBuff` | `0x43ca4a2a` |
| | `… vfc2indx: Shot Timing Transform Error` | `0x43ca4a8a` |
| `[IMAGING_CAP]:` | `[IMAGING_CAP]: [GOLFSHOT]FREE_ERR[%d]: SSP_IMAGE[%d]` | `0x43cacc82` |
| `[CAMERA_MAIN_SYNC]:` | `[CAMERA_MAIN_SYNC]: [GOLFSHOT] shot_time_vfc error!` | `0x43cb18a9` |
| | `… Seq._SndDetEE: FATAL ERR` | `0x43cb18de` |
| `[ADF]SAN …` | `[ADF]SAN START GOLFSHOT SendComp() Err : %x` | `0x43c327a6` |
| | `[ADF]SAN ANALYZE GOLFSHOT SendComp() OK err %x vfc %x vfcSub %x` | `0x43c36d0a` |

En la **A7S fw3.20** las mismas 72 trazas aparecen con `[GOLFSHOT]` como **prefijo principal**
(comprobado: 65 cadenas que *empiezan* por `[GOLFSHOT]` en A7S frente a **0** en A6000): la fw3.21
de A6000 **reorganizó el prefijo de traza**, no la función.

## 2. El módulo `[SAN]` — el análisis del sonido (VERIFICADO, 5 cadenas)

| cadena | dirección |
|---|---|
| `[SAN]StartGolfShot` | `0x43c2c72e` |
| `[SAN]StopGolfShot` | `0x43c2c77a` |
| `[SAN]AnalyzeGolfShot` | `0x43c2c792` |
| `[SAN]SetSoundAnalyze` | `0x43c2c7dd` |
| `[SAN] CLAP DETECT SCORE = %d (%d[deg])  DIFF = %d` | `0x43ce2f27` |

→ el golf shot **detecta el "clap" (el golpe) por el sonido**, con una **puntuación**, un **ángulo
en grados** y una **diferencia** entre lo detectado y lo esperado.

Los mismos comandos están expuestos como comandos de depuración del framework ADF (S81):
`[ADF][DBGCMD]SoundAnalyzer StartGolfShot` `0x43c2b143`, `StopGolfShot` `0x43c2b16c`,
`AnalyzeGolfShot` `0x43c2b194`, `SetSoundAnalyze` `0x43c2b1bf`.

## 3. Las tres fases en el motor de imagen (VERIFICADO)

El SA ejecuta **tres pasos** del golf shot, con traza propia:

1. `SA_LPF` (`0x43ca492f`) — filtrado paso bajo del audio/imagen de entrada.
2. `SA_BGEST` (`0x43ca4984`) — *background estimate*: hay trazas que lo confirman:
   `[CAMERA_MAIN_SYNC]: [GOLFSHOT]Seq._BgestPre: JPEG_DEC OPEN OFF(for debug)` (`0x43cb1ba1`) →
   la estimación de fondo **decodifica un JPEG** previo.
3. `SA_SSP` (`0x43ca49d5`) — *sound snapshot*: búfer `SSP_IMAGE`
   (`FREE_ERR[%d]: SSP_IMAGE[%d]` `0x43cacc82`).

## 4. El "ALOCK" (alpha lock) y sus búferes (VERIFICADO)

`[CAMERA_MAIN_SYNC]: [GOLFSHOT]ALOCK_ERR: BG_INPUT_IMAGE[%2d]` (`0x43cb1915`) y la serie completa:

| búfer | traza | dirección |
|---|---|---|
| `BG_INPUT_IMAGE` | `ALOCK_ERR: BG_INPUT_IMAGE[%2d]` | `0x43cb1915` |
| `BG_IMAGE` | `ALOCK_ERR[%d]: BG_IMAGE` | `0x43cb1952` |
| `BG_MASK_IMAGE` | `ALOCK_ERR[%d]: BG_MASK_IMAGE` | `0x43cb1988` |
| `INPUT_IMAGE` | `ALOCK_ERR[%d]: INPUT_IMAGE[%d]` | `0x43cb19c3` |
| `INPUT_LPF_IMAGE` | `ALOCK_ERR[%d]: INPUT_LPF_IMAGE` | `0x43cb1a00` |
| `ALPHA_IMAGE` | `ALOCK_ERR[%d]: ALPHA_IMAGE` | `0x43cb1a3d` |
| `KEY_ALPHA_LPF_IMAGE[%d]` | `ALOCK_ERR[%d]: KEY_ALPHA_LPF_IMAGE[%d]` | `0x43cb1a76` |
| `SSP_IMAGE[%d]` | `ALOCK_ERR[%d]: SSP_IMAGE[%d]` | `0x43cb1abb` |
| `PRE_KEY_SSP_IMAGE` | `ALOCK_ERR[%d]: PRE_KEY_SSP_IMAGE` | `0x43cb1af6` |

INFERENCIA: el "ALOCK" es el **cálculo de la imagen alfa** (la foto se toma en el instante en que la
bola/raqueta entra en el encuadre y el fondo se sustituye por un JPEG de fondo), y `KEY_ALPHA_LPF_IMAGE`
es la imagen alfa ya filtrada.

## 5. La temporización por VFC (VERIFICADO)

`[IMAGING_RSRC]: [GOLFSHOT]vfc2indx: Shot Timing Transform Error` (`0x43ca4a8a`),
`[CAMERA_MAIN_SYNC]: [GOLFSHOT] shot_time_vfc error!` (`0x43cb18a9`),
`[ADF]SAN ANALYZE GOLFSHOT SendComp() OK err %x vfc %x vfcSub %x` (`0x43c36d0a`) → el instante del
disparo se calcula en **unidades de VFC** (vertical frequency counter) y con **VFC de subcanal**
(→ conecta con S85: `CLK_CTRL` lleva dos VFC, `m_vfc.main` y `m_vfc.sub`).

## 6. `MOTIONSHOT` — eliminado en la fw3.21 de A6000 (VERIFICADO)

- A7S fw3.20: 5 apariciones de `sa_func_MOTIONSHOT` (llamadas desde `IMAGING_CAP` y la firma
  `sa_func_MOTIONSHOT_release(__uint8_t, __uint16_t, MSHOT_START_PARAM*)` en `0x43ce3448`).
- **A6000 fw3.21: 0 apariciones de `sa_func_MOTIONSHOT`** → el driver sigue compilado en la A7S y
  **desaparece por completo** en la A6000.
- Lo que **sí** queda en la A6000 es `MOTIONSHOTVIDEO` (24 cadenas), que pertenece al módulo **SFRS**
  (vídeo en movimiento) y **no es lo mismo**: p. ej.
  `[SFRS][ERR] ***FUNC_CMD_SET_MOTIONSHOTVIDEO_PARAM_PARAMETER_ERROR` (`0x43ce99ab`).

## 7. Abierto (NO_VERIFICADO)

- Qué significa exactamente "ALOCK" (¿*alpha lock*?) y cómo se combinan `BG_*`/`INPUT_*`/`SSP_*` para
  componer la foto final.
- La unidad de medida de `vfc2indx` y la relación con el shutter (el instante de disparo en VFC).
- El significado de `deg` en `CLAP DETECT SCORE = %d (%d[deg]) DIFF = %d` (ángulo del golpe).
- Si el "JPEG_DEC" de BGEST reutiliza el decodificador JPEG del proyecto (S19/S30).
- Por qué la fw3.21 de A6000 elimina MOTIONSHOT (¿reemplazado por otro modo?).

## 8. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s88_shotmodes.py -q
```
