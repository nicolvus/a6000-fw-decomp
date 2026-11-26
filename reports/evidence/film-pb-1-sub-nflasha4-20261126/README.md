# Evidencia — auditoría de `nflasha4` (FILM-PB-1, 2026-11-26)

Todo se regenera con los scripts de este directorio. Nada se escribió en la cámara.

| fichero | qué es |
|---|---|
| `census.py` | censo por sectores de 1 KiB: cabecera FBS, trailer, regiones, entropía 4 KiB, cadenas, diferencias, mapa 80×32. Rutas de los tres volcados en `FILES` (`D1`=nand-20261020, `D2`=nand-20261105, `D3`=nand-20261105-total) |
| `census.txt` | su salida |
| `diff.txt` | diferencias por bloque de 1 KiB entre pares y contención D2⊂D3 |
| `libmpr-geometria.txt` | extracto de desensamblado de `libmpr.so` con la geometría del FBS |
| `dynsyms-flash.txt` | símbolos reales (`FlashLib::*`, `DvdFlashBackupLib::*`) de `.dynsym` |
| `geom_evidence.py` | regenera `libmpr-geometria.txt` |
| `recdesc.py`, `ann.py` | desensamblador Thumb-2 por descenso recursivo y anotador de literales (capstone) |

Reproducir:

```bash
python3 reports/evidence/film-pb-1-sub-nflasha4-20261126/census.py
python3 reports/evidence/film-pb-1-sub-nflasha4-20261126/geom_evidence.py
```

Los scripts `census.py` esperan ejecutarse desde la raíz del repo.
`ann.py`/`recdesc.py` cargan `analysis/camera-extract/usr/lib/libmpr.so`
(10 321 204 B, sha256 `9a74a3bb42836559…`), el mismo binario de `/usr/lib`
que corre en la cámara.

Aviso: `0x7DD572` en libmpr **es una dirección de cadena**
(`/sys/block/nflasha0/nflasha0p4/start`), no de código; `0x2B0FFC` sí es código
(thunk a `0x2A9AD8` = `DvdFlashBackupLib::Init`).
