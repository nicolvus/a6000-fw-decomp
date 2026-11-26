# Evidencia — `reports/grabacion-bd-fbm-20261126.md`

Binario: `analysis/camera-extract/usr/lib/libmpr.so` (fw 3.21). VA = offset ELF.
sha256 en `sha256.txt`. Desensamblador: `reports/evidence/fbm-sector31-consola-20261126/evidencia/mprdis.py`
(capstone Thumb; anota `.dynsym`, PLT y literales). Todo estático: no se ejecutó nada.

## Índice

| fichero | qué prueba |
|---|---|
| `dis/01-bkup-read-r4-0x37fb54.txt` | `0x37FB54`: lee `(0x22,8)` con `0x2B39B8`; con `0x10100001` llama `InitBackupData(9,8)` en `0x37FC06`, loguea y **devuelve 0** (`0x37FC4E`) |
| `dis/02-bkup-getbasediff-0x37fc80.txt` | `0x37FC80` (`GetBaseDifferenceDubbedInfo`): idéntico, `InitBackupData(9,8)` en `0x37FD4C`; devuelve 0 |
| `dis/03-dcf-initbackuptbl-0x38fe68.txt` | `[DCF MCMD] InitBackUpTbl`: `(7,mediaID)` por `tbb` → `0x38FEC4`; error logueado y **devuelve 1** |
| `dis/04-mmgr-0x61d930.txt` | gestor de medios: tipo 8→OM4, 0x10→**OM6**, 6→OM0xA, 1→OM7; `0x61D94C bl` y `0x61D984 movs r0,#0` (**no consulta el error**) |
| `dis/05-mmgr-mediaid-0x61d8d0.txt` | `mediaID` por tipo de medio: `3`/`4` en `0x61D8F8`, `2`,`5`,`6`,`7` |
| `dis/06-getindex-0x2b2f48.txt` | índice en `0xA3699C` por `fileType` (`0x2B2B18`); compara **sólo** `[entry+0]` (`0x2B2F96`): `fn` no interviene |
| `dis/07-readfirstpack-0x2b39b8.txt` | `ReadFirstPackData`: `0x2B39EC ldr r2,[entrada+4]` / **`0x2B39EE cbz r2,0x2B3A28`** → `0x10100001` |
| `dis/08-writepackbegin-0x2b3d24.txt` | `WritePackBegin`: handle de `0xA3699C` (`0x2B3D88`); 0 → **`0x2B3D90 ldr r5,=0x10100001`** |
| `dis/09-writebasedata-0x2b4030.txt` | `WriteBaseData`: `0x2B406A bl 0x2B3000`, `0x2B4072 bne 0x2B40FC` (`0x10800010`), `0x2B40C8 CreateSector32`, `0x2B4130 bl 0x2B3F7C` |
| `dis/10-changesector-0x2b41b4.txt` | `ChangeSector`: `0x2B41D8 bl 0x2B3094`; handle 0 → **`0x2B41F4 ldr r4,=0x10100006`** |
| `dis/11-m2psifo-registro-0x5c9aec.txt` | registro real de `(4,mediaID)` → `fn=0x5CA354` en `0x5C9B06`; `0x5C9B0A mov r0,r4` (**error descartado**) |
| `dis/12-m2psifo-write-0x5ca0b4.txt` | escritura del backup M2PS: `0x5CA10E bl 0x5C9F48`; si falla `0x5CA126 mov r0,r4`; si no, `WritePackBegin/WritePack/End` |
| `dis/13-m2psifo-writebasedata-0x5ca294.txt` | `fn` real: `"@@@ Flash Backup BaseData Write EXEC @@@"`; 4×`0xA0` memcpy del IFO vivo; IDs `0xE1`/`0xE2` |
| `dis/14-m2psifo-openrecfile-0x5e7a6c.txt` | `m2psIfo_rec::OpenRecFile`: `[I]` `0x8D2902`; `0x5E7B8C bl 0x5CA0B4`; `0x5E7B90` recarga `r0` (**resultado perdido**) |
| `dis/15-m2psifo-closerecfile-0x5e7d28.txt` | `CloseRecFile`: `[I]` `0x8D293F`; `0x5E7E50 bl 0x5CA0B4`; `0x5E7E54` recarga; `errorCode=` con 0; **`0x5E7E92 mov r0,r5` → devuelve 0** |
| `dis/16-m2psifo-cancelrec-0x5e7ec0.txt` | `CancelMovieRec`: `0x5E8002 bl 0x5CA0B4`, mismo trato |
| `dis/17-m2psifo-read-0x5ca5d4.txt` | lectura del backup M2PS: `0x5CA5FA movs r0,#4` + `ldr r1,[r4,#0xC]` → `0x2B39B8` |
| `dis/18-ltc01-0x2b5598.txt` | `LTC 1` = `[FBM]LocalTestCall::LTC_01`: registra `0x2B5724`/`0x2B5658` con `arg 0xA36C4C/0xA36C50`; textos «Dummy …» |
| `dis/19-m2psifo-changesector-0x5c9f48.txt` | `ChangeSector(4,mediaID)` en `0x5C9F7E`; `"Flash Backup SECTOR CHANGE ERROR!!"`; línea `0x3EA` |
| `dis/20-getsectorhandle-0x2b3000.txt` | `GetSectorHandleFromOperatioModeAndMediaID`: **`0x2B301A cbz r2`** sobre `fn`; sin fila → `0x10800010` |
| `dis/21-calluserfunc-0x2b3f7c.txt` | `CallUserFuncWriteBaseDataRequest`: recorre `0x9D23FC`, `cbz` de `fn` (`0x2B3FB4`), `blx r3` con `r0=[entry+0x14]` (`0x2B3FC6`) |
| `dis/22-entrywritebasedata-0x2b1dec.txt` | `EntryWriteBaseDataFunction`: empareja `(userID, mediaID)` y guarda `fn` en `+0x10`, `arg` en `+0x14` |
| `dis/23-m2psifo-read2-0x5ca5c0.txt` | variante de lectura (`0x5CA5C2`) usada por `0x5E7B98` tras `OpenRecFile` |
| `escritores-fn.txt` | los **11** llamantes de `0x2B1DEC` con `(userID, fn, arg, mediaID)` |
| `xrefs.txt` | llamantes `bl` de `0x2B1DEC 0x2B43F0 0x2B41B4 0x2B39B8 0x35EA1C 0x34E638 0x5CA0B4 0x5C9F48 0x61D930 0x2B3D24 0x2B3C64 0x2B3B94` |
| `tabla-0x9d23fc.txt` | volcado de la tabla estática `0x9D23FC` (37 filas de 0x18 B): `userID`, `mediaID`, `fileType`, `OM`, `fn`, `arg`; idx 13 = `(4,3)→0x31` con `fn=0` |
| `sha256.txt` | hash del binario analizado |

## Scripts

| script | uso |
|---|---|
| `gen_evidencia.sh` | regenera `dis/`, `xrefs.txt`, `escritores-fn.txt` y `sha256.txt` |
| `tabla_escritores.py` | reconstruye `(r0..r3)` de los 11 llamantes de `0x2B1DEC` |
| `tabla_estatica.py` | vuelca la tabla `0x9D23FC` (37 filas de 0x18 B) |
| `xref_all.py` | llamantes `bl`/`blx` completos (sin truncar) |
| `funcstart.py` | inicio de la función que contiene una VA (prologos `push {..,lr}`) |
| `strref.py` | xref de código a una cadena/dato (pool de literales) |
| `strs.py` | cadenas referenciadas en un rango de código |
| `ptrs.py` | punteros Thumb a una VA en `.rodata`/`.data`/`.init_array`/`.got` |

## Cómo se ha generado

```sh
bash reports/evidence/grabacion-bd-fbm-20261126/gen_evidencia.sh
python3 reports/evidence/grabacion-bd-fbm-20261126/tabla_escritores.py > escritores-fn.txt
```

## Límites

- Sin ejecución (ni cámara ni QEMU): sólo bytes e instrucciones.
- Las etiquetas de módulo («BKUP», «DCF MCMD», «MMgr», `m2psIfo_Backup`) salen de las cadenas
  que cada función referencia, no de símbolos del ELF (el binario sólo trae `.dynsym` parcial).
