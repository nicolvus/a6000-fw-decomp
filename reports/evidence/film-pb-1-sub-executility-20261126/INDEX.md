# Evidencia — film-pb-1-sub-executility-20261126

Todo generado desde bytes del binario (`libmpr.so` fw 3.21, y contraste a6300 fw2.01 / a7s fw3.20).
VA = dirección virtual del ELF (base 0). Desensamblado Thumb-2 propio (capstone); los nombres de
símbolo salen del `.dynsym` y los de PLT del orden de `.rel.plt` con los stubs ARM del `.plt`.

| Fichero | Qué prueba |
|---|---|
| `01-thunk-722bcc.txt` | `0x722BCC` = `MprIf::ExecMprUtility(UtilityCmdId,void*)` (40 B, exportado): traza `MprIfLog::AsyncApiCall<unsigned short>(0x40000005,0,id)` y `b.w 0x4500CC` |
| `02-impl-4500cc.txt` | implementación local: lock del api id, comprobación de sesión (`[this+4]->vt[0x18]`), petición de 9 B `{u32 id; u8 conDato; u8 dato[4]}`, entrega a `0x436408`, retorno 9 si la sesión no vive |
| `03-media-dispatch-436408.txt` | despacho: `[obj+0x1F0]==2`, `id ≤ 4`, máscaras `0x16` (ids 1,2,4 sin dato) y `0x9` (ids 0,3 con dato), 5 gestores (`cmp r4,#5`), `tbb` por id |
| `04-console-parser-72dd98.txt` | `MprIfMcmd::ExecMprUtility`: `quickFormat→0`, `fullFormat→3`, **`init→1`** (`0x72DDFE`), `check→4`; ayuda `ex) MPR FUNCRECOVERY ExecMprUtility [commandId` |
| `05-flashlib-init-2b696c.txt` | `FlashLib::Init`: `GetEepData(0x003C00BF)` → `tst #1` → **stores del flag en `0x2B6994`/`0x2B6998`** (literal `&m_enableFlag` en `0x2B6B64`), geometría en `0x2B0FFC` |
| `06-wbi-wrapper-2b4aac.txt` | envoltorio `FlashLib::WarmBootInit()` + `BackupMgr::WarmBootInit()` y `return 0` (pareja de recalentamiento) |
| `07-flashlib-warmbootinit-2b6788.txt` | `FlashLib::WarmBootInit` **no** escribe `m_enableFlag` |
| `08-scenario-run-MPR_SCN_FLASH_BACKUP_INIT.txt` | `scenario_run` del escenario: `puts`, `GetMprIfInstance`, `ExecMprUtility(1,NULL)` en `0x6DE`, salida con `"… End Err 0x%x"`; única guarda `buf_size ≥ 4` |
| `09-testcmd-scn-open-dlopen.txt` | `libtestcmd_scn.so`: `dlopen`, `dlsym("scenario_run")`, cadena `"/usr/scenario/"` |
| `10-barrido-llamantes-FlashLib.txt` | barrido de llamantes de `FlashLib::Init`/`WarmBootInit` en las 3 firmwares (directo, literal, PLT) — **incluye el falso negativo que motivó la corrección del informe del 26-11** |
| `11-arranque-cadena-MprIf-Create.txt` | cadena de arranque: `MprCtrl::Init` (`libmprctrl` `0x11B84`) → `MprIf::Create` (`0x71CC20`) → `0x712530` → **`FlashLib::Init` (`0x7126E2`)** → `BackupMgr::Init` (`0x7126E6`); equivalente a6300 en `0x7897D6` |
| `12-utilidad-1-quien-la-pide.txt` | los 3 escenarios que importan `ExecMprUtility` y sus puntos de llamada; mapa de ids del parser de consola; reglas de argumento |
| `13-correccion-escaneo-blx.txt` | bug de escaneo (`BLX` sin `&~3`) y tabla corregida de llamantes en a6000/a6300/a7s |

Reproducción: `python3 /tmp/subpx.py <lib> dis <va> <len>` y los scripts incrustados en `10-`, `12-`
y `13-` (usan `Elf` de `/tmp/subpx.py`; `callers()` enmascara los `BLX` a palabra).
