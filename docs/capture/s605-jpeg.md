# S605 — `[JPEG]`: módulo de traza JPEG exclusivo de la A6000 fw3.21

**17 trazas · ~19 sitios (regla PIC estricta) · ~6 funciones emisoras · 0 muertas.** Detalle + datos: `analysis/s605_jpeg/` (pendiente) / `.json` (pendiente).

## Qué es

`[JPEG]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 17 mensajes del **subsistema JPEG (DGI JPEG / dgi_jpeg_*)** que gestiona codificación/decodificación JPEG, colas de comandos, buffers, cuantificación, rotación, y variantes rápidas (fast dec/enc) y Tango (tanz). La sigla **SÍ tiene base textual**: `JPEG` → **J**oint **P**hotographic **E**xperts **G**roup; el prefijo `dgi_` → **D**river **G**eneric **I**nterface / **D**evice **G**raphics **I**nterface (NO VERIF.).

## Las 17 trazas (vaddr → texto corto)

```
0x43ce06ea [JPEG]: [cbJpegDebugClose] err : %d
0x43ce070e [JPEG]: [cbJpegDebugOpen] err : %d
0x43ce0731 [JPEG]: [cbJpegDebugOpen] uid : 0x%x
0x43ce075c [JPEG]: %s
0x43ce0767 [JPEG]: 0x%x
0x43ce0774 [JPEG]: [f_sa_dummy_send_msg] Start
0x43ce0798 [JPEG]: ERR. osal_try_valloc_msg. err=0x%x, L=%d
0x43ce07c9 [JPEG]: [f_sa_dummy_send_msg] error_status = %d, unique_id = %d
0x43ce0809 [JPEG]: ERR. osal_snd_msg. err=0x%x, L=%d
0x43ce0833 [JPEG]: ERR. osal_free_msg. err=0x%x, L=%d
0x43ce085e [JPEG]: [f_sa_dummy_send_msg] Comp
0x43ce0881 [JPEG]: [f_2open][NormalOpen] jpegErr : %d
0x43ce08ac [JPEG]: [f_2open][SortOpen] jpegErr : %d
0x43ce08d5 [JPEG]: [f_2open][TanzOpen] jpegErr : %d
0x43ce08fe [JPEG]: [f_2close] unique_id : 0x%x
0x43ce0922 [JPEG]: [f_2close][NormalClose] jpegErr : %d
0x43ce094f [JPEG]: [f_2close][SortClose] jpegErr : %d
```

## Hallazgos con dirección

- **Funciones de callback debug**: `cbJpegDebugOpen`, `cbJpegDebugClose` — puntos de entrada/salida del path debug JPEG; emiten 3 trazas vía logger de módulo.
- **Path SA dummy**: `f_sa_dummy_send_msg` — wrapper de envío de mensajes SA (Service Agent) con 3 trazas: `Start`, `error_status`, `Comp`. Validación de `osal_try_valloc_msg`, `osal_snd_msg`, `osal_free_msg`.
- **API de apertura dual**: `f_2open` con tres variantes — `NormalOpen`, `SortOpen`, `TanzOpen` (Tango encoding) — cada una emite `jpegErr : %d`.
- **API de cierre dual**: `f_2close` con dos variantes — `NormalClose`, `SortClose` — más traza de `unique_id : 0x%x`.
- **Logger dual (patrón S177/S179/S603/S604)**: la fw3.21 **duplica** la traza: nueva con prefijo `[JPEG]: ` (logger de módulo, dirección por determinar) + vieja sin prefijo vía logger global `0x43902718` (idéntico a S177/S179/S603/S604). Ejemplo: en `f_sa_dummy_send_msg` offset `+0x3c` carga string `0x43ce0774` (`[JPEG]: [f_sa_dummy_send_msg] Start`) y en `+0x42` llama `bl 0x43902718` con string original sin prefijo.
- **Estructura `dgi_jpeg_*`**: 35+ símbolos de cadena (`src/dgi_jpeg_*.c`, `dgi_jpeg_cmdbuff_*`, `dgi_jpeg_common_*`, `dgi_jpeg_decode/encode/estimate/extent_pointer/fast_dec/fast_enc/fill/open/qtable/queue/rotate/tanz_enc/tanz_ready/tanz_sort/close`) — capa DGI (Driver Generic Interface) para JPEG.
- **Sub-módulos DGI JPEG**: `cmdbuff` (cola de comandos), `common` (malloc/free/send_msg/wait_safin/check_bs_param/make_rsl_*), `decode`, `encode`, `estimate`, `extent_pointer`, `fast_dec`, `fast_enc`, `fill`, `open` (check_param, tskproc_sa_comp, tskproc, tskproc_sa_ack), `qtable` (conv_u4d82float, calc_qscale), `queue` (init/push/pop), `rotate`, `tanz_enc`, `tanz_ready`, `tanz_sort`, `close` (tskproc, tskproc_sa_ack).
- **Longitud del prefijo**: 7 B (`[JPEG]: `) → el más corto de la serie (S177: 16 B, S179: 14 B, S603: 21–24 B, S604: 10 B / 14 B).

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[JPEG]` | **17** | **0** | **0** |
| núcleo sin prefijo (`[cbJpegDebug...]`, `[f_sa_dummy_send_msg]`, `[f_2open]`, `[f_2close]`, `ERR. osal_*`) | 0/17 como literal autónomo | **0** | **0** |
| prefijos alternativos A7S (`[ddl_jpeg_open]`, `[ddl_jpeg_close]`, `[CDIAG][CTRLJPGDEC]`, `[CDIAG][CTRLJPGENC]`, `[CDIAG][CTRLJPGENCDEC]`) | 0 | **12+** | **12+** |
| símbolos `dgi_jpeg_*` / `src/dgi_jpeg_*.c` | **35+** | **0** | **0** |
| código equivalente (JPEG DGI) | `0x43cdfxxx`… | **sí, otro nombre** | **sí, otro nombre** |

→ **Módulo *nuevo* en traza, código preexistente renombrado.** El subsistema JPEG DGI **existe en los tres firmware** (misma funcionalidad: open/close, encode/decode, queue, fast/tanz, qtable, rotate), pero la fw3.21 de la A6000 **renombra la superficie de traza**: elimina los prefijos `[ddl_jpeg_*]`, `[CDIAG][CTRLJPG*]` de A7S/A6300 y **unifica bajo `[JPEG]: `**. La fw3.21 **duplica** la traza (nueva con logger de módulo + vieja intacta con logger global `0x43902718`), salvo en `f_2open`/`f_2close` donde solo usa logger propio (por confirmar).

**Longitud del prefijo fija:** 7 B (`[JPEG]: `) → no se ajusta al nivel/mensaje (a diferencia de S177/S179/S603/S604).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **codificación/decodificación JPEG y path SA dummy**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 17/17 cadenas `[JPEG]: ` confirmadas en `0x43ce06ea`–`0x43ce094f`.
- 35+ cadenas `dgi_jpeg_*` / `src/dgi_jpeg_*.c` en `0x43cdf178`–`0x43ce09af`.
- 0/0 en A7S y A6300 para token `[JPEG]`; 12+ prefijos alternativos en A7S/A6300.
- Scripts: `analysis/s605_jpeg/` (pendiente) · Tests: `tests/test_s605_jpeg.py` (pendiente).