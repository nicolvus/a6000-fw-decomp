# Evidencia — auditoría del gate de carga del IFO MP4 (26-11-2026)

`libmpr.so` 3.21 (`firmware/extracted/fw321/.../lib/libmpr.so`), **VA = offset de fichero, base 0**
(convención del repo; `.text` = 0x120228–0x7A3E84). Desensamblado con `capstone` (`.venv`) vía
`/tmp/elfhelper.py dis <va> <len>`; xrefs de literales con `17-repro-findlit.py`; xrefs de `bl`/`b.w`
con `18-repro-findbr.py`; límites de función desde `.ARM.exidx` (0x97E1C0).

| Fichero | Contenido |
|---|---|
| `01-setloadinfo-0x67B4B8.dis` | función completa (0x67B4B8–0x67B6AC) |
| `02-…-0x6DF7EC.dis`, `03-…-0x6E3860.dis` | las dos copias del traductor de códigos mp4Ifo |
| `04-normalizador-0x6F0D4C.dis` | normalizador de `mp4Ifo_General` (default 0xB0800001) |
| `05-avi-codigo-a-nombre-0x1DA818.dis` | `0x32200001 = ER_AVI_FORMAT`, etc. |
| `06/07` | `FlashLoadForMsv` 0x698EC8 y `DiscLoadForMsv` 0x698E78 |
| `08-checksalvagestatus-0x698F18.dis` | `CheckSalvageStatus` (logs 1334/1340/1351) |
| `09-mp4ifo-general-load-0x698FB8.dis` | `mp4Ifo_General::Load` |
| `10-rcsbackuptbldata-0x3AFA94.dis` | `MsvMcmd::RcsBackupTblData` (lectura real) |
| `11-issupportcontent-0x61A8F0.dis` | gate PAL/NTSC de `isSupportContent` |
| `12-getcontentcount-0x6E8C08.dis` | `mp4Ifo_If::GetContentCount` |
| `13-twin-setloadinfo-xavc-0x67E4F0.dis` | gemelo `MMgrXavcIfoAcsr::SetLoadInfo` (línea 501) |
| `14-logs.txt` | extractos del log del arnés y del anillo real de la cámara |
| `15-tabla-codigos.txt` | tablas de códigos derivadas |
| `16-callers-setloadinfo.txt` | los dos llamadores y por qué el retorno no se usa |
| `19-salidas-setloadinfo.txt` | pseudocódigo anotado con las 7 salidas |
