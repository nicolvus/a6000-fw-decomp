# S125 — `[IMAGING_REL]` (31 trazas) y `[IMAGING]` (120 trazas): los dos módulos menores del gestor de captura

> Informe: [`analysis/s125_imaging_rel/imaging_rel.md`](../../analysis/s125_imaging_rel/imaging_rel.md) ·
> datos: [`imaging_rel.json`](../../analysis/s125_imaging_rel/imaging_rel.json) ·
> scripts: `scan_imaging_modules.py`, `build_diff.py`, `build_report_json.py`, `scan_callers.py` ·
> tests: [`tests/test_s125_imaging_rel.py`](../../tests/test_s125_imaging_rel.py)

## Qué es

- **`[IMAGING_REL]` = la clase `Camera::ReleaseLock`** (VERIFICADO por los nombres RTTI del
  firmware: `N6Camera11ReleaseLock9RelLockS1E` `0x43ca5483`, `…RelLockBaseE` `0x43ca54a4`,
  `…RelLockS2E` `0x43cb4b5f`, más `Queue`/`RingQueue`). **"REL" = RELease**, no es una sigla
  inventada. Su fichero fuente es **`Spinal.cpp`** (`0x43c9c54f`); el programa `av-cam.bin` es
  el **LIRO** (`EV SendSpinalON:LIROSeq` `0x43ca3c74`).
- **`[IMAGING]` = el subsistema de panorama/stitch** (`still_cnt_panoramaSweep.cpp`,
  `still_seq_panoramaStitch.cpp`, `still_cnt_panoramaStitch.cpp`,
  `src/stitch/ddl_stitch.cpp`, `src/srotate/ddl_srotate.cpp`, `still_dda_jpg/rc.cpp`,
  `still_seq_enc.cpp`…) **más el macro genérico `FATAL!`** de todo el subsistema de captura.

## Cifras (regla PIC estricta canónica)
| | `[IMAGING_REL]` | `[IMAGING]` |
|---|---|---|
| cadenas | **31** (`0x43c9c520`–`0x43cb4bc4`) | **120** (`0x43c9b47c`–`0x43cc6c99`) |
| con referencia | 30 (1 muerta) | 82 (**38 muertas**, también en la A7S) |
| sitios PIC / funciones | **34** / **26** | **608** / **346** |
| reparto | 31 específicos → 34 sitios, 26 funciones | 3 genéricos (`FATAL!`) → 473 sitios; 117 específicos → 135 sitios, 24 funciones, 11 ficheros |

## Hallazgos

- El despachador de **`REL_EVT`** está en `0x4379d83a`: `subs r2,r3,#1` + `cmp r2,#0x26` +
  `tbh` → **ids `0x01`–`0x27`**; el caso por defecto imprime `Unknown REL_EVT (%02X)`.
- La cadena del panorama coincide **exactamente** con la de S105 (`PanoramaSweepStart
  0x437e6b3c`, `UpdateSweepCanvas 0x437e751c`, `seq_panoramaClippingDecode 0x43780eb4`,
  `PanoramaStitch 0x438bcef8`). El motor de secciones de S114 **no** emite ningún mensaje
  específico de `[IMAGING]`: solo el `FATAL!` genérico.
- La **tabla de capture-ids** (`CapIdTblMgr`, `0x4381c30c`–`0x4381c6cc`) gestiona 6 campos
  (`irp`, `cidx`, `rp`, `wp`, `wpd`, `dm`); la **cola** (`RelQueue`, `0x4381c93c`–`0x4381cb7c`)
  avisa de cola vacía/llena en 4 variantes; `CapIdTblMgrIf` (`0x4381cc7c`) tiene 8 trazas y
  **0 llamadores `bl` directos** → se invoca por interfaz.
- La cadena `Spinal) osal_free_timer: err %x` (`0x43c9c520`) está **muerta** (ni PIC, ni
  puntero absoluto, ni `movw`/`movt`) **ya en la A7S**.

## Diferencial

| | A6000 fw3.21 | A7S fw3.20 | A6300 fw2.01 |
|---|---|---|---|
| trazas con el prefijo | 31 / 120 | **0 / 0** | **0 / 0** |
| mensajes equivalentes sin prefijo | — | **30 / 31** y **115 / 120** | **22 / 31** y **115 / 120** |
| nuevos de la fw3.21 / propios de la otra cámara | — | 1 (`(%d,%d,%d)`) y 5 (`[PanoramaSweepEnd]…`, `StitchProc ALL OK`) / 0 | idem / 2 (`CapIdTblMgr) SetMprInitEnd`, `CapIdTblMgrIf) Unknown massage`) |

→ la **etiqueta es nueva de la fw3.21 de la A6000** (igual que `[IDT_OPD]` en S120). El
`[IMAGING]: FATAL! %s:%d` (443 sitios) es el `FATAL! %s:%d` de la A7S (467 sitios) con la
etiqueta antepuesta; el A6300 **sí** tiene la clase `Camera::ReleaseLock`.

## Abierto

Significado de `irp/cidx/rp/wp/wpd/dm` e `InnerRP`; ids de `REL_EVT`; qué fuerza `S1` en
`IsNeedForceS1ON`; el "factor" de `RelLock`; quién invoca `CapIdTblMgrIf` por vtable; por qué
la fw3.21 etiqueta con `[IMAGING]:` el `FATAL!` de todo el subsistema de captura; los tres
valores de `[IMAGING_REL]: (%d,%d,%d)`.
Tests: `.venv/bin/python -m pytest tests/test_s125_imaging_rel.py -q` (38 tests)