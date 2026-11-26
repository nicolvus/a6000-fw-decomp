# Evidencia — recreación de sectores FBM en `nflasha4` (2026-11-29)

Todo es análisis estático de `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21,
sha256 `9a74a3bb42836559…`) y de los volcados
`analysis/camera-dumps/nand-20261020/dev_nflasha4.bin` (D1) y
`analysis/camera-dumps/nand-20261105-total/dev_nflasha4.bin` (D3).
**No se ha tocado la cámara ni se ha escrito en NAND.**

## Ficheros

| fichero | qué es |
|---|---|
| `filetypes.txt` | lista `0x9D2380` (30 × u32) y `m_fileTypeSizeInfo` `0x9D2794` (39 × 16 B) con bytes y bloques de 128 KiB |
| `idnames.txt` | tabla `GetIdString` `0x7E95DC` (0x00–0x83): nombre por fileType |
| `ctrl-pages.txt` | las 64 páginas del anillo de control de D3 con seq, checksum y entradas |
| `verify-entries.txt` | comprobación `bloquesBase/Max` de las 5 entradas de la última página contra `0x9D2794` |
| `ctrl_seq381.bin` | página de control de 1 KiB con 0x90/0x91/0x92/0x60/0x61/0x68/0x6C/0x63 añadidos, seq 381, checksum |
| `make_ctrl.py` | genera `ctrl_seq381.bin` a partir de la última página de D3 y del `m_fileTypeSizeInfo` del ELF |
| `callgraph.py` | grafo inverso de llamadas Thumb-2 (BL/BLX) sobre `libmpr.so` |
| `dis/*.txt` | desensamblados anotados de las funciones citadas en el informe |

## Reproducir

```bash
cd /home/nicolas/Documents/a6000/sony-a6000-electronic-shutter
python3 reports/evidence/fbm-recreate-20261129/make_ctrl.py 0x90 0x91 0x92 0x60 0x61 0x68 0x6c 0x63
python3 reports/evidence/fbm-recreate-20261129/callgraph.py 0x2B1080 0x2B0E70 0x2A8750
```

## Direcciones clave

| VA | símbolo / función |
|---|---|
| `0x9D2380` | lista de 30 fileType + `0xFFFFFFFF` |
| `0x9D2794` | `FlashLib::m_fileTypeSizeInfo` (39 × 16 B) |
| `0xA3699C` | tabla FBM 30 × 0x14 `{fileType, handle, válido, OM}` |
| `0x7E7FAC` | tabla de comandos FBM (29 × 12 B `{name, handler, help}`) |
| `0x7DFF40` | tabla de comandos DFB (14 × 12 B `{help, name, func}`) |
| `0x2B4820` | `FBM::Init` |
| `0x2B208C` | `FlashLib::SetSectorManagerInfo` |
| `0x2B6F80` | `FlashLib::CreateSector_Body` |
| `0x2B7080` | `FlashLib::CreateSector32` |
| `0x2B708C` | `FlashLib::CreateSector` |
| `0x2B6688` | `FlashLib::OpenSector_Body` |
| `0x2B6764` | `FlashLib::OpenSector32` |
| `0x2B6E40` | `FlashLib::ForceDeleteSector` (no es CreateSector32) |
| `0x2B6EDC` | `FlashLib::DeleteSector` |
| `0x2B89C0` | `FlashLib::CheckAndRepairFlashBackup` |
| `0x2B8B7C` | `FlashLib::IsFlashAllCleared` |
| `0x2B8B48` | `FlashLib::CheckExistSector` |
| `0x2A8750` | `DvdFlashBackupLib::CreateSector` |
| `0x2A81E8` | `DvdFlashBackupLib::OpenSector` |
| `0x2A8DF8` | `DvdFlashBackupLib::AllDeleteFileType` |
| `0x2ABA28` | `pabe` — partition all block ERASE |
| `0x2A6880` | constructor de la página de control (`+4/+6` = total/libres) |
| `0x2B05B0` | checksum del FBS |
| `0x2B05DA` | builder de página (`+0=0`, `+0x3F8=seq`, `+0x3FC=cks`) |
| `0x2B061E` | test de página en blanco (`u32 @0 == 0xFFFFFFFF`) |
| `0x2B0E70` | allocator de fileType/bloques del FBS |
| `0x2B3F7C` | `BackupMgr::WriteBaseData` (crea con `CreateSector32` en `0x2B40C8`) |
| `0x722BCC` | `MprIf::ExecMprUtility(n)` (0/1/2/3/4 = quickFormat/init/flush/fullFormat/check) |
