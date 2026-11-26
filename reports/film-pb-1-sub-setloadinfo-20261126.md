# FILM-PB-1 · Auditoría del gate de carga del IFO MP4 (`MMgrMp4IfoAcsr::SetLoadInfo`) — 26-11-2026

**Resumen.** `SetLoadInfo` = **0x67B4B8–0x67B6AE** (`mmgrifoacsr/MMgrMp4IfoAcsr.cpp`, log final en **línea 523** =
`movw r3,#0x20B`); desensamblado completo en [01-setloadinfo](evidence/film-pb-1-sub-setloadinfo-20261126/01-setloadinfo-0x67B4B8.dis).
Sólo devuelve ≠0 por tres motivos: `0x018000FF` (no existe `[this+0x48]`), `0xB0100002` (mutex de `mp4Ifo_If` ocupado)
o **el código que le pasa `mp4Ifo_If::GetContentCount` (0x6E8C08) o `GetPlayThumbnailInfo` (0x6E8430)**.
`0xB0510007` tiene **una sola entrada** en la tabla del traductor mp4Ifo (`0x6DF7EC` y su gemelo `0x6E3860`):
**`0x32200001`**, que el mapper AVI `0x1DA818` nombra **`ER_AVI_FORMAT`**; `0xB0800001` es la **rama por defecto** de
esa tabla. El anillo real **no tiene la línea 523 para MP4** y sí `SetLoadInfo : TvSystem is NTSC, frameRate 3`
(anillo:106): en la cámara **SetLoadInfo pasa**; el fallo está en `mp4Ifo_General::Load` → `FlashLoadForMsv` →
`MsvMcmd::RcsBackupTblData` (`0x3AFA94`), que devuelve un código de grupo `0x10` sin traducción ⇒ `0xB0800001`
(normalizador `0x6F0D4C`). Las líneas **1749 y 1340 son el mismo fallo repetido**, no dos. **`mp4Ifo_General::Load`
(0x698FB8) no lee ni un campo** del registro de 0x80 B de `AVIN0001.INP`: sólo despacha por `device` y pone
`mb_load=1`. **No hay tabla de capacidades por modelo**: las máscaras de cadencia (`0x2A9`/`0x154`, y
`0x2A8`/`0x154`/`0x3` en `isSupportContent`) son inmediatas de compilación, y lo único "de modelo" es `TvSystem()`
(global en `0xAD28F8+0x28`). **Los dos llamadores de `SetLoadInfo` (0x627C6C, 0x628676 en `AviMMgrCmd`) tiran su
retorno.** Conclusión: con tarjeta recién formateada y un clip propio, lo único que puede hacer fallar el `Load` es
que **`RcsBackupTblData` (MSV/BKUP) no devuelva 0**, y el anillo muestra ese mismo `Err RcsBackupTblData` fallando
a la vez para **MSV, DCF y XAVC**: fallo de dispositivo/volumen compartido, no del MP4.
Evidencia: [evidence/film-pb-1-sub-setloadinfo-20261126/](evidence/film-pb-1-sub-setloadinfo-20261126/README.md).

> Espacio de direcciones: **VA del ELF con base 0 = offset de fichero** (`.text` 0x120228–0x7A3E84); es la
> convención ya usada en los informes previos de esta línea. Ninguna acción sobre la cámara: todo estático.

---

## 1. Localización y desensamblado

| Dato | Valor | Cómo |
|---|---|---|
| Cadenas | `0x90D1C7` "SetLoadInfo : TvSystem is PAL, frameRate %d" · `0x90D1F4` "… is NTSC …" · `0x90D222` "… is %d, Unknown frameRate %d" · `0x90D257` "… is %d, Invalid frameRate %d" | `grep -abo` + mapa de PHDR |
| Quién las referencia | **sólo dos funciones**: los pools `0x67B6C4–0x67B6D0` y `0x67E710–0x67E718` | xref de literales PC-relativos ([17-repro-findlit.py](evidence/film-pb-1-sub-setloadinfo-20261126/17-repro-findlit.py)) |
| Función 1 | **0x67B4B8–0x67B6AE** (pool de literales 0x67B6B0–0x67B6DC; siguiente función 0x67B6E0), nombre `"SetLoadInfo"` (`0x90D180`), fichero `"mmgrifoacsr/MMgrMp4IfoAcsr.cpp"` (`0x90D18C`), **línea 523** (`0x67B69E: movw r3,#0x20b`) | dis |
| Función 2 (gemela) | **0x67E4F0–0x67E728**, `"mmgrifoacsr/MMgrXavcIfoAcsr.cpp"` (`0x90DC36`), **línea 501** | dis |
| Límites de función | `.ARM.exidx` (`0x97E1C0`, 31 233 funciones) — confirma que 0x67B4B8 es un inicio de función | parse exidx |
| Formato del log | `0x67B68E` → `0x677B8E` → `0x64E300`, que imprime `## ERROR(MMGR):0x%08X ## <fichero>(<línea>) <función>()` | dis de 0x677B8E y 0x64E300 |

`0x67B4B8` **no aparece como dato en ninguna parte del fichero** (ni `0x67B4B8` ni `0x67B4B9`): no está en vtable
estática. Sus únicos llamadores son dos `bl` directos, ambos en `AviMMgrCmd`:
**0x627C6C** (función 0x627BEC, camino "FlashLoadMp4") y **0x628676** (función 0x628594, "DiscLoadMp4"). Los dos
**sobrescriben `r0` inmediatamente** (`0x627C70 movs r1,#1` / `0x62867A movs r1,#6`), así que **el código de retorno
de `SetLoadInfo` se descarta** ([16-callers](evidence/film-pb-1-sub-setloadinfo-20261126/16-callers-setloadinfo.txt)).

## 2. Todas las salidas de `SetLoadInfo` (condición exacta)

Pseudocódigo anotado completo en
[19-salidas-setloadinfo.txt](evidence/film-pb-1-sub-setloadinfo-20261126/19-salidas-setloadinfo.txt).

| # | Dirección | Condición exacta | Código devuelto | Log |
|---|---|---|---|---|
| S1 | `0x67B4C2` | `[this+0x48] == 0` (no hay objeto `mp4Ifo_If`) | **`0x018000FF`** (literal en `0x67B6B8`) | `SetLoadInfo : MP4 No exist.` |
| S2 | `0x67B4D6` | `[this+0x0C]->vt[0x154]() == 0` ("no cargado") | **0** (`r5=r0`) | `SetLoadInfo : It is not loaded.` |
| S3 | `0x67B52E` | **`mp4Ifo_If::GetContentCount([this+0x48],1,0,1,&n)` ≠ 0** | **el código de esa llamada** | — (salta a `0x67B650`, sin log) |
| S4 | `0x67B53A` | `n == 0` (0 contenidos) | 0 | — |
| S5 | `0x67B598` | **`GetPlayThumbnailInfo(...)` ≠ 0** | **el código de esa llamada** | — (`0x67B650`) |
| S6 | `0x67B59C` | `[r7+0x000] == 0` (byte de validez de la info) | 0 | — |
| S7 | `0x67B5A4` | `fr = [r7+0x124] > 9` | 0 | `… Invalid frameRate %d` |
| S8 | `0x67B5AC` | `1<<fr & 0x2A9` ≠ 0 → **fr ∈ {0,3,5,7,9}** | 0 | `… TvSystem is NTSC, frameRate %d` + `vt[0x44](0)` |
| S9 | `0x67B5BE` | `1<<fr & 0x154` ≠ 0 → **fr ∈ {2,4,6,8}** | 0 | `… TvSystem is PAL, frameRate %d` + `vt[0x44](1)` |
| S10 | `0x67B5C4` | `1<<fr & 2` ≠ 0 → **fr == 1** | 0 | `… TvSystem is %d, Unknown frameRate %d` |
| S11 | `0x67B5CA` | cualquier otro fr ≤ 9 | 0 | `… TvSystem is %d, Invalid frameRate %d` |
| S12 | `0x67B660` | `0x6EB9D8([this+0x48],&b)` con `b != 0` (necesita *salvage*) | **no cambia `r5`** | `vt[0x88](1)` + `SetLoadInfo : Need salvage` |
| S13 | `0x67B68E` | siempre | `r5` | línea 523 |

**Consecuencia dura:** sólo **S1, S3, S5** pueden devolver ≠0, y S3/S5 sólo con el código de otra capa:
`0xB0100002` es el mutex de `mp4Ifo_If` (`0x5BAD00`; id `0x2f` en `0x6E8C08`, id `0x23` en `0x6E8430`) y cualquier
otro valor viene de `vt[0x54]` del dispositivo. **Ningún campo del IFO se comprueba en esta función**: lo único que
sale del contenido es `fr` (enum de cadencia) y el byte de validez de S6.

## 3. De dónde salen `0xB0510007` y `0xB0800001`

Tabla completa en [15-tabla-codigos.txt](evidence/film-pb-1-sub-setloadinfo-20261126/15-tabla-codigos.txt).

**(a) `0xB0510007` ⇐ `0x32200001`, y sólo ese.** El traductor mp4Ifo existe **dos veces** con el mismo *switch*:
`0x6DF7EC` (8 casos + default, loguea con `"mp4Ifo_AVISequence.cpp"`) y `0x6E3860` (idéntico, recibe
`r1=código, r2=fichero, r3=línea`). La rama `0x6E38C4`/`0x6DF850` carga `0xB0510007` y el único `cmp` que llega
allí es `r1 == 0x32200001`.

**(b) `0x32200001` = `ER_AVI_FORMAT`.** El mapper `0x1DA818` devuelve un `char*` por código; sus 16 ramas dan
`ER_OK, ER_BADARG, ER_INTERNAL, ER_ILLEGAL_SEQUENCE, ER_KERNEL_CALL, ER_CANCELED, **ER_AVI_FORMAT (0x32200001)**,
ER_AVI_MEDIUM_FULL, ER_AVI_TVSYSTEM_NONE, ER_FAILED, ER_DRIVE, ER_MEDIUM, ER_ACCESS, ER_UNRECOGNIZED,
ER_DISC_CORRUPT, ER_WRITE_VERIFY_ERROR, ER_NO_MEDIUM`. Es decir: **`0xB0510007` = "la capa AVI dice que el formato
del contenido no es válido"**.

**(c) `0xB0800001` = "no clasificado".** Es la rama por defecto del traductor (`0x6DF874`/`0x6E38E8`), y también el
`por_defecto` que `mp4Ifo_General` pasa al normalizador `0x6F0D4C`: éste sólo traduce los grupos
`0x80,0x20,0x40,0x50,0x81,0xF0,0xF2` y los exactos `0x1340000x/0x13810001`; **el grupo `0x10` (MSV) cae en
`0x6F0E96 → mov r4,ip`**, es decir, devuelve el `0xB0800001` del llamante. *(Refina, sin contradecir, el informe
[montaje/IFO](film-pb-1-sub-mount-ifo-20261126.md): allí se citaba `0x6F0EBC` como "default"; esa rama es la del
grupo `0xF0`, y el default real para grupos desconocidos es el que pasa el llamante, que en este camino es el
mismo `0xB0800001`.)*

**(d) Qué pasó en cada sitio.**

| Fuente | `0xB0510007` | `0xB0800001` |
|---|---|---|
| Arnés (`analysis/film-pb1-arnes/log-e2e17b.txt`:19-22) | `AviSeqPlay.cpp ER_AVI_FORMAT` → `mp4Ifo_AVISequence.cpp(3646)` y `(0889)` → **`MMgrMp4IfoAcsr.cpp(523)`** | arnés 12-13: `Err RcsBackupTblData` → `mp4Ifo_General.cpp(1749)` → `0xB0800001` |
| Cámara real (`…/log-real-20261126/anillo-mpr-20261020.txt`:20-27, 39-46) | — | `[MSV]Err RcsBackupTblData` → `(1749)` → `(1340)`; **y a la vez** `[DCF]Err RcsBackupTblData` y `xavcIfo_File.cpp(0874) 0xB0520001` / `xavcIfo_General.cpp(1508) 0xB0800005` |
| Cámara real, MP4 `SetLoadInfo` | **no aparece** (no hay línea 523 de `MMgrMp4IfoAcsr`) | — (sí `XavcIfoAcsr.cpp(501) 0xB0810001`, que es la traducción de "1") |

El anillo no está truncado justo ahí: la línea 106 (`SetLoadInfo : TvSystem is NTSC, frameRate 3`) va seguida de 24
líneas más (reproducción de foto, `StillCache`, `PlayStillSingle`…) y en **el mismo volcado** hay dos logs de
`mmgrifoacsr/MMgrMp4IfoAcsr.cpp` (2319 `LoadSub` y 246 `CreateAndLoad`). Es decir: si el MP4 `SetLoadInfo` hubiera
fallado, su línea 523 estaría en el buffer; no está.

En el arnés **no hay ninguna línea `SetLoadInfo : TvSystem …`**: encaja con que el fallo entró por **S3**
(`GetContentCount` ≠ 0), que salta a `0x67B650` **sin** log de cadencia. En la cámara, en cambio, sí está la línea
NTSC ⇒ entró por **S8** y devolvió 0.

## 4. Qué necesita `mp4Ifo_General::Load` para tener éxito

`mp4Ifo_General::Load` `0x698FB8` (38 instrucciones, [09-…dis](evidence/film-pb-1-sub-setloadinfo-20261126/09-mp4ifo-general-load-0x698FB8.dis)):

```
log " mp4Ifo_General::Load IN (device=" ; log(device == 0 ? "FLASH" : "DISC")
if (device == 1) r = DiscLoadForMsv(this)      ; 0x698E78, log en la linea 1713
else             r = FlashLoadForMsv(this)     ; 0x698EC8, log en la linea 1749
if (r == 0) this->[0x23] = 1                   ; mb_load = 1
log " mp4Ifo_General::Load OUT()" ; return r
```

* **No lee ningún byte del registro de 0x80 B de `AVIN0001.INP`.** Tampoco `FlashLoadForMsv` (`0x698EC8`), que
  sólo hace `0x3AFA94( [this]->[8] )` — resolver el objeto MSV con el *getter* `0x6964E2` (`return this->[8]`) y
  llamar a `MsvMcmd::RcsBackupTblData`. En este nivel lo único obligatorio es `device == 0` (FLASH) y `[this]`
  válido; el flag `mb_load` (`[this+0x23]`) **no** lo mira `Load`: sólo lo consulta `CheckSalvageStatus`.
* **El único dato que sí es obligatorio** es la respuesta de la capa MSV/BKUP: `MsvMcmd::RcsBackupTblData`
  `0x3AFA94` ([10-…dis](evidence/film-pb-1-sub-setloadinfo-20261126/10-rcsbackuptbldata-0x3AFA94.dis)) llama al
  lector real `0x35EA1C` (que se identifica con su propio log `"RcsBackupTblData Start"`, `0x81DFA7`) y:
  * si `r != 0` y `(r & 0xFF000000) == 0x10000000` → log **`"Err RcsBackupTblData"`** (clase E/S) y **devuelve `r`**;
  * si `r != 0` y otro grupo → log `" Need Salvage"`, `[this+0x44]=1` y devuelve `r`;
  * si `r == 0` → `0x34E5D4` (`"BKUP GetBaseOverFlag"`), y si el flag `[r7+0x6C] != 0` → `[this+0x44]=1` y **0**
    (no es error); luego `vt[0x78](this, &[r7+0x5C])` y `vt[0x60](this, u16 [r7+0x64])`.
  Ese `r` es el que `0x6F0D4C` convierte en **`0xB0800001`** (grupo `0x10`, sin traducción) y con el que
  `FlashLoadForMsv` llama a `Unload` (`0x697D70`) y retorna el error.
* **`CheckSalvageStatus` `0x698F18`** explica el doble mensaje del anillo: si `[this+0x23] != 0` devuelve
  `0xB0100006` (línea **1334**); si no, `r = FlashLoadForMsv(this)`, **log en la línea 1340 con ese mismo `r`**,
  y si `r != 0` sale. Por eso `(1749)` y `(1340)` son **un solo fallo, impreso dos veces** con el mismo código.
* El registro de 0x80 B **sí existe** y está declarado en `.rodata`: junto a los nombres `PLAYLIST`,
  `AVIN0001.INP`, `AVIN0001.BNP`, `AVIN0001.INT` (≈`0x7A90C0`–`0x7A9170`) y la tabla de límites con
  `0x2710 = 10000` y `0x80` (≈`0x7A9120`/`0x7A9180`). Pero lo consume el lector AVIN/AVI, **no** esta ruta.
  *(La semántica exacta campo a campo del registro se tomó de [sub-avin](film-pb-1-sub-avin-20261127.md) §3 y
  aquí sólo se corrobora que la tabla existe; ver NO_VERIFICADO.)*

## 5. ¿Hay comprobación dependiente del modelo o del firmware?

* **En `SetLoadInfo`: no.** Las dos clasificaciones de cadencia son **inmediatas compiladas**:
  `movw r2,#0x2A9` (`0x67B5B0`) y `tst.w r3,#0x154` (`0x67B5BE`) + `tst.w r3,#2`. No hay ninguna carga indexada
  por modelo ni identificador de modelo en toda la función. Lo único "de modelo" es el valor de `TvSystem()`
  (`0x1EEFDC`: `return *(u32*)(0xAD28F8 + 0x28)`), un **global de ejecución**, no una tabla.
* **En el gate vecino `isSupportContent` `0x61A8F0`: tampoco hay tabla.** También con inmediatas:
  `TvSystem()==1` (PAL) acepta `{2,4,6,8}` ∪ `{0,1}` y rechaza `{3,5,7,9}` (`0x2A8` → "Invalid TvSystem detected",
  `movs r0,#0`); `TvSystem()!=1` (NTSC) acepta `{3,5,7,9}` ∪ `{0,1}` y rechaza `{2,4,6,8}`; `fr > 9` →
  "Unknown frameRate" y **devuelve 1 (acepta)**. Su otra entrada viene por parámetro: `0x3F9C7C([core+0x768], …)`
  "Can't get condition" y `0x61A764(this,0xC4,4,…)`, es decir **configuración por instancia**, no una tabla de
  capacidades embebida. **Nota:** `SetLoadInfo` usa `0x2A9` (mete 24p/23,976 en el grupo NTSC) mientras
  `isSupportContent` usa `0x2A8` + `0x3` (24p aceptado por ambos); no es la misma máscara.
* Lo que sí varía por firmware es el **código compilado**: las tablas de traducción de códigos están replicadas
  cuatro veces (`0x6DF7EC`, `0x6E3860`, `0x787508`, `0x78B864`) y son parte de `libmpr.so`, no datos de tarjeta.
  Con `TvSystem` NTSC y `fr=3` el resultado es "COINCIDE" en las dos versiones de la máscara.

## 6. Conclusión

Con **tarjeta recién formateada en la cámara** y un **clip grabado por la propia cámara**:

1. **`SetLoadInfo` no puede ser la causa.** Con `fr=3` cae en S8 (NTSC), devuelve 0 y su valor se descarta en los
   dos llamadores. Su único camino de fallo realista (S5/S3) exige que `vt[0x54]` del dispositivo falle — y en el
   anillo de la cámara no hay ninguna línea 523 de MP4.
2. **El registro de 0x80 B del `AVIN0001.INP` no interviene en el `Load`.** Ni `mp4Ifo_General::Load`, ni
   `FlashLoadForMsv`, ni `DiscLoadForMsv` leen campo alguno: no hay comprobación de duración, tamaño, cadencia,
   `EntryId` ni flags en esta ruta.
3. **Lo único que puede hacer fallar el `Load` es que `MsvMcmd::RcsBackupTblData` (`0x3AFA94`) no devuelva 0**, es
   decir, que la **lectura de la tabla de respaldo de la capa MSV/BKUP** falle o pida *salvage*. Y el anillo real
   demuestra que ese fallo **no es del MP4**: en las líneas 20-27 y 39-46 el mismo `[MSV][MS1]Err RcsBackupTblData`
   precede al `[DCF][MS1]Err RcsBackupTblData` y a los fallos de XAVC (`0xB0520001`, `0xB0800005`). Un solo fallo
   de dispositivo/volumen explica los cuatro consumidores; el MP4 sólo lo refleja con el código **genérico**
   `0xB0800001`.
4. **`0xB0510007` del arnés no es el fallo de la cámara.** Es `ER_AVI_FORMAT` de la capa AVI entrando por
   `GetContentCount` (sin línea de TvSystem en el log del arnés). Reproduce el mecanismo del traductor, no la causa
   física. Y como el retorno de `SetLoadInfo` se descarta, ese valor **no es una guarda** que el firmware consulte.

## 7. NO_VERIFICADO

* **Qué código `0x10xxxxxx` concreto** devolvió `RcsBackupTblData` en la cámara: el anillo sólo conserva el código
  ya normalizado (`0xB0800001`); `libmpr` no tiene tabla de nombres para el grupo `0x10`.
* **Destino de los virtuales** `vt[0x154]`, `vt[0x44]`, `vt[0x88]`, `vt[0x78]`, `vt[0x60]`: no resueltos (el
  objeto se construye en ejecución; `0x67B4B8` no aparece en ninguna vtable estática). Los nombres
  "está cargado"/"fija TvSystem" son **inferencia** por uso, no símbolo.
* **Si `0x35EA1C` o `vt[0x78]`/`vt[0x60]` del objeto MSV leen algún byte del registro de 0x80 B**: no trazado hasta
  campo. Lo **verificado** es lo negativo: `mp4Ifo_General::Load` y `FlashLoadForMsv` no lo hacen.
* **Semántica de `0x018000FF`** (S1): no aparece en ninguna tabla de nombres de `libmpr` (0 apariciones fuera del
  pool `0x67B6B8`).
* **Identidad de `0x6EB9D8`** (consulta de *salvage* de S12) más allá de su uso.
* **`0x80` como "tamaño de registro"**: se corrobora que la constante está junto al descriptor de `AVIN0001.INP` y
  que existe `0x2710` en la tabla de límites, pero la asignación campo-a-campo se apoya en
  [sub-avin](film-pb-1-sub-avin-20261127.md) §3 y **no** se ha re-verificado aquí.

## Referencias

* Evidencia e índice: [`reports/evidence/film-pb-1-sub-setloadinfo-20261126/`](evidence/film-pb-1-sub-setloadinfo-20261126/README.md)
  (13 desensamblados, tablas de códigos, llamadores, pseudocódigo, extractos de log, scripts de reproducción).
* Log del arnés: `analysis/film-pb1-arnes/log-e2e17b.txt` (líneas 12-13, 19-22).
* Anillo real: `reports/evidence/film-pb-1-log-real-20261126/anillo-mpr-20261020.txt` (líneas 20-27, 39-46, 95-106).
* Informes previos usados como contraste: [montaje/IFO](film-pb-1-sub-mount-ifo-20261126.md),
  [RcsBackup](film-pb-1-sub-rcsbackup-20261126.md), [AVIN](film-pb-1-sub-avin-20261127.md),
  [log real](film-pb-1-log-real-20261126.md), [arnés](film-pb-1-sub-arnes-20261127.md).
