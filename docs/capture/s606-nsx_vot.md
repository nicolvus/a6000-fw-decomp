# S606 — `[NSX_VOT]`: módulo de traza timer/alarma exclusivo de la A6000 fw3.21

**Auditoría 23-10-2026:** direcciones de las cadenas corregidas contra coincidencias únicas en `av-cam.bin` (base `0x43541000`). Las longitudes canónicas están en el JSON corregido. La duplicación del logger, los límites de funciones y la equivalencia entre modelos no quedan demostrados por presencia de cadenas; esas afirmaciones históricas siguen NO_VERIFICADO.

**7 trazas · 14 sitios (regla PIC estricta: 7 pares gemelos) · ~2 funciones emisoras · 0 muertas.** Detalle + datos: [JSON](../../analysis/s606_nsx_vot/nsx_vot.json).

## Qué es

`[NSX_VOT]` es la etiqueta de traza que la fw3.21 de la A6000 antepone a 7 mensajes del **gestor de timers/alarmas (almhdl = alarm handler, VOT = ?)** que gestiona asignación/liberación/configuración/cancelación de timers OSAL. La sigla **SÍ tiene base textual**: `NSX` → probable nombre de submódulo Sony; `VOT` → **V**irtual **O**perating **T**imer / **V**oice **O**ver **T**imer / **V**ideo **O**utput **T**imer (NO VERIF.).

## Las 7 trazas (vaddr → texto corto; gemelo `[TRK]: ` en `vaddr+Δ`)

```
0x43cfdb1e [NSX_VOT]: almhdl : bt stop error: %d          → gemelo 0x43cfdb9c (+0x26)
0x43cfdb66 [NSX_VOT]: osal_alloc_timer(): %d               → gemelo 0x43cfdbe0 (+0x22)
0x43cfdba6 [NSX_VOT]: osal_alloc_timer(): handle alloc again!! → gemelo 0x43cfdc32 (+0x34)
0x43cfdc0a [NSX_VOT]: osal_free_timer(): handle NULL!!     → gemelo 0x43cfdc8e (+0x2c)
0x43cfdc5e [NSX_VOT]: osal_free_timer(): %d                → gemelo 0x43cfdcd7 (+0x21)
0x43cfdc9c [NSX_VOT]: osal_set_timer(): %d                 → gemelo 0x43cfdd14 (+0x20)
0x43cfdcd8 [NSX_VOT]: osal_can_timer(): %d                 → gemelo 0x43cfdd50 (+0x20)
```

## Hallazgos con dirección

- **Pares gemelos exactos**: cada traza `[NSX_VOT]: ` tiene su gemelo `[TRK]: ` a distancia fija (20–52 bytes), confirmando **duplicación de traza** (logger de módulo nuevo + logger global viejo), patrón idéntico a S177/S179/S603/S604/S605.
- **Función `almhdl`**: manejador de alarma/bluetooth (`bt stop error`) + API timer OSAL (`alloc/free/set/can`).
- **Logger dual**: la fw3.21 emite **ambas** trazas (nueva con prefijo `[NSX_VOT]: ` + vieja con prefijo `[TRK]: `). El logger global `[TRK]: ` ya existe en A7S/A6300 (ver diferencial).
- **Longitud del prefijo**: 11 B (`[NSX_VOT]: `) → fija, no se ajusta al nivel/mensaje.
- **Estructura**: capa fina sobre `osal_*_timer()`; `almhdl` sugiere manejador de alarma con Bluetooth.

## Diferencial A6000 fw3.21 vs A7S fw3.20 vs A6300 fw2.01

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| token `[NSX_VOT]` | **7** | **0** | **0** |
| token `[TRK]` (mismo núcleo) | **7** (gemelos) | **7** | **7** |
| prefijo alternativo A7S (`[CapMgr]` para alloc/set/free) | 0 | **3** | **3** |
| núcleo sin prefijo (`almhdl...`, `osal_*_timer...`) | 0/7 como literal autónomo | **7/7** (con `[TRK]: `) | **7/7** (con `[TRK]: `) |
| código equivalente (`osal_*_timer`, `almhdl`) | `0x43cfdxxx`… | **sí** | **sí** |

→ **Cambio de *logging*, no de código.** El gestor de timers/alarmas **existe igual** en los tres firmware (mismas 7 cadenas núcleo, mismas funciones `osal_*_timer`, mismo `almhdl`). Lo propio de la fw3.21 de la A6000 son **las 7 trazas con prefijo `[NSX_VOT]: `** y la **duplicación** con logger global `[TRK]: ` (que ya es el prefijo usado en A7S/A6300). A7S/A6300 usan `[TRK]: ` como prefijo principal y `[CapMgr]` para variantes.

**Longitud del prefijo fija:** 11 B (`[NSX_VOT]: `) → no variable (igual que S605).

## Línea del obturador: NEGATIVO ACOTADO

0 coincidencias de `shutter`/`silent`/`curtain`/`electro`/`mech`/`obtur`/`sensor`/`readout`/`imager`/`iso`/`apert`/`expos`/`brack`/`drive`/`release`/`flash`/`sync`/`vsync`/`capture`/`shot`/`still`/`movie`/`focus`/`svd`/`shd`/`spl`/`frame`. El módulo gestiona **timers OSAL y alarmas**, no el obturador. → **S51 (A/B/C = NO) se mantiene.**

## Verificación

- 7/7 cadenas `[NSX_VOT]: ` confirmadas en `0x43cfdb1e`–`0x43cfdcd8`.
- 7/7 gemelos `[TRK]: ` confirmados en `0x43cfdb9c`–`0x43cfdd50` (distancias +20 a +52 bytes).
- 0/0 en A7S y A6300 para token `[NSX_VOT]`; 7/7 para `[TRK]` (mismo núcleo).
- Scripts: `analysis/s606_nsx_vot/` (pendiente) · Tests: `tests/test_s606_nsx_vot.py`.
