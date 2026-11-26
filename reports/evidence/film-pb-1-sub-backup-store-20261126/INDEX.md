# Evidencia — film-pb-1-sub-backup-store-20261126

Todo generado con `/tmp/tools/elftool.py` (capstone Thumb-2 + resolución de PLT por `.rel.plt`/`.rel.dyn`)
sobre `libmpr.so` de fw 3.21. Direcciones = VA del ELF. Nada ejecutado.

| fichero | qué demuestra |
|---|---|
| `01-msvmcmd-RcsBackupTblData-3afa94.txt` | `MsvMcmd::RcsBackupTblData` (`0x3AFA94`): sólo llama a `0x35EA1C`; el `Err RcsBackupTblData` sale con `(ret & 0xFF000000)==0x10000000` |
| `02-ReadFirstPackData-2b39b8.txt` | el corte `cbz r2` -> `0x10100001` en `0x2B39EE`, antes de leer nada |
| `03-table-A3699C-dump.txt` | geometría 30x0x14, campos y escritores; la tabla está en `.bss` (ceros al cargar); array de fileTypes `0x9D2380` |
| `04-xrefs-A3699C.txt` | 24 punteros literales a la tabla, todos en `0x2B2xxx-0x2B4xxx` |
| `05-sector-mgr-region-2b2000-2b4c00.txt` | desensamblado completo de la unidad gestora de sectores |
| `06-callers-SetSectorManagerInfo.txt` | `SetSectorManagerInfo` tiene **1** llamante: `0x2B5A3A` (consola `SetSMI`) |
| `07-register-loop-2b5900.txt` | el handler de consola que parsea `SetSMI [index] [SectorName] ...` |
| `08-table-registration-2b4400.txt` | `SetSectorManagerTable` (`0x2B45A8`): escribe `+0x00/+0x04/+0x08/+0x0C/+0x10` |
| `09-WarmBootInit-2b4624.txt` | bucle de registro en `BackupMgr::WarmBootInit` y su rama `else` (`0x2B4718`, reader=0) |
| `10-array-9D2380.txt` | los 30 fileTypes que se intentan registrar |
| `11-BKUP-worker-35e04c.txt` | `BkRead(userId=[this+0x4088], backupId=[this+0x408C])` en `0x35E0EC` |
| `12-RcsBackupTblData-35ea1c.txt` | el envoltorio: no fija `+0x4088/+0x408C`, delega |
| `13-writers-4088.txt` | barrido de escrituras candidatas a `+0x88/+0x8c` de objeto grande (negativo: son otras estructuras) |
| `14-GetSMI-Index-2b2f48.txt` | `GetSectorManagerInfoTableIndexFromUserID`: compara `entry[+0]` con el fileType; si no, `0x10800010` |
| `15-readfirstpack-real-2b3948.txt` | `ReadNextPackData`: bucle sobre `0x2B267C` |
| `16-ReadPack-2b267c.txt` | `ReadPack` usa `FlashLib::ChangeSeekPoint` / `ReadSector` / `AppointSectorEnd` |
| `17-FlashLib-ReadSector-2b62e4.txt` | `FlashLib::ReadSector` completo |
| `18-fbs-name-table.txt` / `19-sector-names.txt` | tabla `userID -> nombre` (`FLH AVCHD`, `FLH DCF`, `FLASH MP4`, `FSYS`, `AVI1 (CSVC1)`...) |
| `20-init-2b47e0.txt` | `BackupMgr::Event` (`0x2B47E0`) y `BackupMgr::Init` (`0x2B4820`) con el bucle y `SetBackupMgrCallback` |
| `21-callers-init.txt` | llamantes y ausencia de llamantes (Init -> `0x7126E6`; `FlashLib::Init` sin llamante interno) |
| `22-enableflag-xrefs.txt` | `m_enableFlag` (`0xA36C78`): **una** escritura (`0x2B6B64`), 34 lecturas |
| `23-FlashLib-Init-2b696c.txt` | `FlashLib::Init(SystemType)`: habilita/deshabilita y pide geometría a la capa DFB |
| `24-scenario-flash-backup-init.txt` | `MPR_SCN_FLASH_BACKUP_INIT.so` (de fábrica) -> `MprIf::ExecMprUtility(1,NULL)` |
| `25-FlashBackupCheckAndDestroy.txt` | `0x61DB54`: `AVCHD/M2PS/MP4/DCF BackupClear!!` y destrucción de los cuatro sectores |
| `26-DFB-CheckExistFile-2a6690.txt` | `0x45` = existe, `0x4F` = "not initialized yet" |
| `27-dependencias-negativas.txt` | libmpr **no** contiene `/setting` ni `nflasha2`; sí `/dev/nflasha4`, `/dev/cnflasha4`, `nflasha0p4` |
