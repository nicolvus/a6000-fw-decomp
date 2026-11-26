# Evidencia · `InitB` / `WriteBaseData` (2026-11-30)

Binario: `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21).
Herramienta: `python3 /tmp/elfhelper.py <lib> dis <va> <len>` (`.dynsym`; los símbolos Thumb llevan el bit 0).
Volcados: `analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` (D1),
`analysis/camera-dumps/nand-20261105-total/dev_nflasha4.bin` (D3), 10 MiB cada uno.

## Ficheros

| fichero | qué contiene |
|---|---|
| `console_table.txt` | las 29 entradas de la consola FBM en `0x7E7FAC` (nombre, handler con bit 0 limpio, ayuda) |
| `user-table.txt` | tabla `0x9D23FC` (37 × 0x18 B: userID, mediaID, fileType, OM, fn, arg) y `0x9D2794` (tamaños) |
| `dis/initb_handler.txt` | `InitB` `0x2B5B34`–`0x2B5B60` (argc, parsers `0x5FFE6E`, llamada a `0x2B43F0`) |
| `dis/initbackupdata.txt` | `BackupMgr::InitBackupData` `0x2B43F0` |
| `dis/writebasedata.txt` | `BackupMgr::WriteBaseData` `0x2B4030` |
| `dis/base_sub.txt` | `CallUserFuncWriteBaseDataRequest` `0x2B3F7C` (tabla `0x9D23FC`, fn/arg) |
| `dis/lookup.txt` | `GetSectorHandleFromOperatioModeAndMediaID` `0x2B3000` |
| `dis/userid.txt` | `GetUserIDFromOperationModeAndMediaID` `0x2B385C` |
| `dis/getft.txt` | `GetFileType` `0x2B2B18` (userID+mediaID → `+8`) |
| `dis/getom.txt` | `GetOperationModeFromUserFuncTable` `0x2B2BCC` |
| `dis/index1.txt` / `dis/index2.txt` | `0x2B2E54` / `0x2B2F48` (índice en `0xA3699C`, 0x1E entradas) |
| `dis/isdvd.txt` / `dis/getmodekind.txt` | `0x2B1DCC` (OM 7/8) y `0x2B1DBC` (`[0xA36C64]`) |
| `dis/setom.txt` / `dis/setom_impl.txt` | consola `SetOM` `0x2B5A60` y `SetOperationMode` `0x2B1EE8` |
| `dis/chgsec.txt` / `dis/changesector.txt` | consola `ChgSec` `0x2B5AF4` (hex) y `ChangeSector` `0x2B41B4` |
| `dis/fbs_create.txt` | `0x2B1080` (lock) → `0x2A8750`; `OpenSector` `0x2B10BA` → `0x2A81E8` |
| `dis/setsmtable.txt` | `SetSectorManagerTable` `0x2B45A8` (rellena `0xA3699C`) |
| `dis/dcf_initbackuptbl.txt` | `[DCF MCMD] InitBackUpTbl` `0x38FE68` (tbb → `InitBackupData(7,mediaID)`) |
| `dis/initb_tail.txt` | cola de `InitBackupData` (eventos `0x2010`/`0x2011`) |
| `dis/wbd_variants.txt` | `ChangeSector` (OM/media) y `ChangeSector(void)` con los OM guardados |

## Direcciones clave

- consola FBM `0x7E7FAC`; `InitB` = entrada 7 (`0x7E8000`), handler `0x2B5B34`.
- tabla maestra `0x9D23FC` (userID/mediaID/fileType/OM) y lista de fileTypes `0x9D2380`.
- `0xA3699C`: 30 × `0x14` `{+0 fileType, +4 handle, +8 válido, +0xC OM, +0x10 extra}`.
- `0x9E452C`: tabla de fileID del FBS (48 × 16 B); `0x9E5588` = unidad de sector (`0x20000`).
- `0x9E598C` = "repair needed"; si ≠0 `DvdFlashBackupLib::CreateSector` `0x2A8750` no crea.
- Errores de `WriteBaseData`: `0x10800010` y líneas `0xF47`, `0xF4F`, `0xF56`, `0xF5D`, `0xF6D`, `0xF79`.
- Duplicado en el FBS: `0x4B` (`0x2A8A86`).

## Reproducir

```
python3 /tmp/elfhelper.py analysis/camera-extract/usr/lib/libmpr.so dis 0x2B4030 0x160
python3 /tmp/elfhelper.py analysis/camera-extract/usr/lib/libmpr.so dis 0x2B5B34 0x30
python3 make_table.py    # regenera user-table.txt
```
