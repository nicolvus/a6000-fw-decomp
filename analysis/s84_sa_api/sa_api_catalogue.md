# S84 — El API del motor de imagen (SA): catálogo de `sa_func_*` con sus firmas C++ (A6000 fw3.21)

**Alcance:** línea de ingeniería inversa **general** de la cámara: **la superficie completa del
driver del motor de imagen** (`Camera::SaFuncDrv`), es decir, la lista de funciones `sa_func_*` que
el firmware usa para programar el acelerador Scalar, con sus **firmas C++ embebidas** (tipos de
parámetros) y el diferencial A6000 fw3.21 vs A7S fw3.20. No es la línea SilentShutter, ni la
montura (S66), ni el AF, ni ADJ_CMD, ni ZPD, ni ZIT (S80), ni ADF (S81), ni las caras (S71).

**Estado:** VERIFICADO = contra bytes. INFERENCIA = lectura razonada. NO_VERIFICADO = pendiente.

Artefactos: `tests/test_s84_sa_api.py`.

---

## 1. La forma de la API (VERIFICADO)

Todas las funciones del driver tienen la misma forma (firma embebida, p. ej.
`0x43cec7f5`):

```c
Camera::SaFuncDrv::SA_FUNCDRV_ERR Camera::SaFuncDrv::sa_func_<X>_<op>(
        __uint8_t, __uint16_t, Camera::SaFuncDrv::<X>_START_PARAM*);
```

Es decir: **número de unidad** (`__uint8_t`), **código de función** (`__uint16_t`) y **puntero a la
estructura de parámetros** específica del algoritmo. Las que además gestionan memoria llevan un
contexto `Camera::SaFuncDrv::SaFuncDrvCmn*` como primer argumento (p. ej. `sa_func_BFNR_init` y
`sa_func_KKNR_exit`).

Códigos de error del driver (VERIFICADO): `SA_FUNCDRV_E_OSAL`, `SA_FUNCDRV_E_RSLTCODE`,
`SA_FUNCDRV_E_ERRCODE`.

## 2. Las 19 familias de funciones (VERIFICADO)

| familia | operaciones | firma de referencia (dirección) |
|---|---|---|
| `BFNR` | init, acquire, start, release | `sa_func_BFNR_init(SaFuncDrvCmn*, BFNR_START_PARAM*, BFNR_PARAM*, __uint16_t)` (`0x43cec98b`), `sa_func_BFNR_release(__uint8_t, __uint16_t, BFNR_START_PARAM*)` (`0x43cec7f5`) |
| `BOKS` | init, init_CONTROL, GetAddr, start, release, exit | `sa_func_BOKS_init_CONTROL` (traza `0x43cecf8d`) |
| `CONTP` | acquire, start, release | `sa_func_CONTP_release(__uint8_t, __uint16_t, CONTP_START_PARAM*)` (`0x43ced65e`) |
| `DECOMP` | acquire, start, release | `sa_func_DECOMP_release(__uint8_t, __uint16_t, DECOMP_START_PARAM*)` (`0x43ced8ac`) |
| `DUALREC_BAYER` / `DUALREC_CLEARVID` | acquire, start, release, exit | sin firma completa; llamadas desde `IMAGING_CAP` (`0x43cac9c1`–`0x43caca0a`, `0x43cac6cf`–`0x43cac867`) |
| `GOLFSHOT` | start (**dos sobrecargas**), release | `sa_func_GOLFSHOT_start(__uint8_t, __uint16_t, SSP_START_PARAM*, SSP_START_MBX*, __uint8_t*)` (`0x43cedc91`) y `sa_func_GOLFSHOT_start(__uint8_t, __uint16_t, BGEST_START_PARAM*, SA_MBX_0123*, __uint8_t*)` (`0x43cedff6`); `sa_func_GOLFSHOT_release(__uint8_t, __uint16_t, GOLFSHOT_START_PARAM*)` (`0x43cedf67`) |
| `KKNR` | acquire, start, release, exit | `sa_func_KKNR_release(__uint8_t, __uint16_t, KKNR_START_PARAM*)` (`0x43cee1f4`), `sa_func_KKNR_exit(SaFuncDrvCmn*, KKNR_START_PARAM*)` (`0x43cee27b`) |
| `LFNR` | init, acquire, start, release, exit | llamadas desde `IMAGING_CAP` (`0x43cc9355`, `0x43cc94fb`) |
| `MOTIONSHOT` | init, acquire, start, release, exit | `sa_func_MOTIONSHOT_release(__uint8_t, __uint16_t, MSHOT_START_PARAM*)` (solo A7S: `0x43ce3448`) |
| `NFLASH` | acquire, start, release | `sa_func_NFLASH_release(__uint8_t, __uint16_t, NFLASH_START_PARAM*)` (`0x43cee4ca`) — **flash**: sus parámetros son `flash_add`, `amb_add`, `int_add`, `rc_line_ofs` |
| `NLAP` | init, acquire, start, release, exit | `sa_func_NLAP_init` / `sa_func_NLAP_release` (solo A7S: `0x43ce39d4`) |
| `PreDCV` | start, release | `sa_func_PreDCV_release(__uint8_t, __uint16_t, PRE_DCV_START_PARAM*)` (`0x43cee7ec`) |
| `SFTFCS` | preinit, release | `sa_func_SFTFCS_preinit(__uint16_t)` (`0x43ceeaa0`), `sa_func_SFTFCS_release(__uint8_t, __uint16_t, SFTFCS_START_PARAM*)` (`0x43cee878`) |
| `SPICA` | acquire, start, release, exit + fases **PRE/MAPPING/POST** | `sa_func_SPICA_PRE_release` / `_MAPPING_release` / `_POST_release` (llamadas desde `IMAGING_CAP`, `0x43cc9b3a`–`0x43cc9c19`) |
| `STAR` | acquire, start, release, exit | llamadas desde `IMAGING_CAP` (`0x43cc9c54`–`0x43cc9da7`) |
| `TBOX` | acquire, start, release | `sa_func_TBOX_release(__uint8_t, __uint16_t, TBOX_START_PARAM*)` (`0x43ceeea8`) |
| `YKNR` | acquire, start, release, exit | llamadas desde `IMAGING_CAP` (`0x43cca388`–`0x43cca4a4`) |
| `BDEX` | release, exit | `sa_func_BDEX_exit` (traza `0x43cec6ff`) |

**92 cadenas** contienen `sa_func_` en la A6000 (109 en la A7S).

Detalle de nombres: la A6000 invoca `sa_func_sftfcs_start` / `_release` / `_acquire` **en minúsculas**
(`[IMAGING_CAP]: %s: sa_func_sftfcs_start error (%d)`, `0x43cc93c2`), mientras que la firma del driver
es `sa_func_SFTFCS_preinit` / `_release` en mayúsculas (`0x43ceeaa0`, `0x43cee878`); y el arranque de
SFTFCS fija tres mailbox (`sftfcs_start_mbx.cha_mbx0/1/2 = 0x%x`, `0x43cc9df0`–`0x43cc9e58`).

## 3. Quién llama al SA (VERIFICADO)

El módulo `IMAGING_CAP` (697 trazas) es el que **invoca** el motor de imagen durante la captura, con
trazas de error por cada operación:

`sa_func_NFLASH_start error` (`0x43c9ef73`), `sa_func_NFLASH_release error` (`0x43c9f1df`),
`sa_func_NFLASH_acquire error` (`0x43c9f20f`), `sa_func_DUALREC_CLEARVID_acquire` (`0x43cac6cf`),
`sa_func_DUALREC_BAYER_start` (`0x43caca0a`), `sa_func_BFNR_acquire()` (`0x43cc7390`),
`sa_func_BOKS_acquire err` (`0x43cc75a5`), `sa_func_CONTP_acquire error` (`0x43cc7bfa`),
`sa_func_DECOMP_acquire()` (`0x43cc7e09`), `sa_func_PreDCV_start error` (`0x43cc8085`),
`sa_func_KKNR_acquire error` (`0x43cc8e85`), `sa_func_LFNR_acquire error` (`0x43cc9355`),
`sa_func_SPICA_acquire error` (`0x43cc99d4`), `sa_func_STAR_acquire error` (`0x43cc9c54`),
`sa_func_TBOX_start error` (`0x43cca213`), `sa_func_YKNR_acquire error` (`0x43cca388`).

El otro usuario es el propio driver, con el prefijo `[CAMERA_SA]` (231 trazas), p. ej.
`[CAMERA_SA]: %s: \`sa_func_BDEX_exit' error` (`0x43cec6ff`).

## 4. Diferencial A6000 fw3.21 vs A7S fw3.20 (VERIFICADO)

La fw3.21 de A6000 **elimina por completo** dos familias del driver del motor de imagen:

- **`NLAP`**: la A7S tiene 13 cadenas (`[YC][NLAP]isNLAP:true, iso_cont=0x%04x` `0x43cbbf71`,
  `[YC][NLAP]Param:%x,%x,%x,%x,%x,%x,%x,%x` `0x43cbc008`, `sa_func_NLAP_acquire error` `0x43cc4197`,
  `sa_func_NLAP_start error (%d)` `0x43cc41d8`, `sa_func_NLAP_release error` `0x43cc4252`); en la
  A6000 hay **0 ocurrencias de "NLAP"** (ni módulo ni driver).
- **`sa_func_MOTIONSHOT_*`**: la A7S los invoca desde `IMAGING_CAP` (`sa_func_MOTIONSHOT_acquire error`
  `0x43cc403e`, `sa_func_MOTIONSHOT_start error (%d)` `0x43cc4063`) y tiene la firma
  `sa_func_MOTIONSHOT_release(__uint8_t, __uint16_t, MSHOT_START_PARAM*)` (`0x43ce3448`); en la A6000
  hay **0 ocurrencias de "sa_func_MOTIONSHOT"**. Ojo: lo que sí queda en la A6000 es
  **`MOTIONSHOTVIDEO`** (24 cadenas, p. ej. `[SFRS][ERR] ***FUNC_CMD_SET_MOTIONSHOTVIDEO_PARAM_PARAMETER_ERROR`
  `0x43ce99ab`), que pertenece al módulo **SFRS** (vídeo de movimiento) y **no** es lo mismo.

Otros diferenciales menores: la A7S registra los errores de `LFNR` con más detalle
(`sa_func_LFNR_start_sendStartMsg error[%d]` `0x43ce33be`, `sa_func_LFNR_start_rcvDoneMsg error[%d]`
`0x43ce33ec`) y no usa el prefijo `[IMAGING_CAP]:` en esas trazas.

## 5. Abierto (NO_VERIFICADO)

- Significado de cada sigla: BFNR, BOKS, CONTP, DDCV/PreDCV, GOLFSHOT (SSP/BGEST), KKNR, LFNR,
  MOTIONSHOT, NFLASH, NLAP, SFTFCS, STAR, TBOX, YKNR, BDEX, SPICA.
- Estructura de cada `<X>_START_PARAM` (campos y tamaños).
- Qué algorithms del SA corresponden a cada familia (código dentro del acelerador, fuera del blob).
- Las fases `PRE`/`MAPPING`/`POST` de SPICA en detalle.
- Por qué la A6000 conserva el driver de MOTIONSHOT/NLAP sin llamarlo.

## 6. Reproducción

```bash
cd /home/nicolas/Documentos/a6000/sony-a6000-electronic-shutter
.venv/bin/python -m pytest tests/test_s84_sa_api.py -q
```
